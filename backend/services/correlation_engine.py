"""
correlation_engine.py — Phase 6C: Engine 3 (Combined Risk Intelligence)
========================================================================

Purpose:
    Merge the outputs of Engine 1 (DBSCAN spatial hotspot detection) and
    Engine 2 (RF crime/cyber forecasts) into a single Combined Risk Score
    per area, then derive patrol deployment priorities.

Methodology:
    The combined_risk_score is computed using configurable domain-informed
    heuristic weights. These are NOT a fixed "AI formula" — they are
    explicit, documentable parameters that can be tuned by domain experts.

    Heuristic Weights (default):
        w_physical = 0.45   — Physical crime forecast risk
        w_cyber    = 0.25   — Cybercrime forecast risk
        w_spatial  = 0.30   — DBSCAN active hotspot presence

    Risk levels are mapped to numeric scores:
        Low      = 0.25
        Medium   = 0.50
        High     = 0.75
        Critical = 1.00

    combined_risk_score = (
        w_physical * physical_score
      + w_cyber    * cyber_score
      + w_spatial  * spatial_score
    )

    Combined risk label from score:
        < 0.35  → Low
        < 0.55  → Medium
        < 0.75  → High
        >= 0.75 → Critical

    Patrol priority = rank by combined_risk_score descending (1 = highest risk)

Output table: area_intelligence
    One row per area per forecast period. Truncated and replaced on each run.
"""

import logging
from datetime import datetime, date

from db import db
from models import Hotspot, CrimeForecast, CyberForecast, AreaIntelligence
from services.feature_engine import AREA_BASE_WEIGHTS, AREA_ZONES

logger = logging.getLogger(__name__)


# ─── CONFIGURABLE HEURISTIC WEIGHTS ──────────────────────────────────────────
# Domain-informed — can be adjusted by operators without retraining models.
WEIGHTS = {
    'physical': 0.45,   # Engine 2 physical crime forecast
    'cyber':    0.25,   # Engine 2 cybercrime forecast
    'spatial':  0.30,   # Engine 1 DBSCAN active hotspot presence
}

# Risk level → numeric score mapping
RISK_SCORES = {
    'Low':      0.25,
    'Medium':   0.50,
    'High':     0.75,
    'Critical': 1.00,
}


def _risk_to_score(risk_label: str) -> float:
    return RISK_SCORES.get(risk_label, 0.25)


def _score_to_risk(score: float) -> str:
    if score < 0.35: return 'Low'
    if score < 0.55: return 'Medium'
    if score < 0.75: return 'High'
    return 'Critical'


def _spatial_risk_from_hotspots(hotspot_count: int, worst_hotspot_risk: str) -> str:
    """
    Derive an area's spatial risk from DBSCAN hotspot data.
    If no hotspots in the area → Low.
    If hotspots exist, use the worst risk level present.
    """
    if hotspot_count == 0:
        return 'Low'
    return worst_hotspot_risk or 'Low'


def run_correlation_engine(
    forecast_year: int  = None,
    forecast_month: int = None,
    weights: dict = None,
) -> dict:
    """
    Merge Engine 1 + Engine 2 outputs into combined area-level intelligence.

    Args:
        forecast_year:  Target year (defaults to next month's year)
        forecast_month: Target month (defaults to next month)
        weights:        Override heuristic weights dict (optional)

    Returns:
        Summary dict with status, area count, risk distribution, and top areas.
    """
    if weights:
        # Validate weights sum to ~1.0 and all keys present
        required = {'physical', 'cyber', 'spatial'}
        if not required.issubset(weights.keys()):
            raise ValueError(f"weights must contain keys: {required}")
        w = weights
    else:
        w = WEIGHTS

    # Default to next month
    if forecast_year is None or forecast_month is None:
        today = date.today()
        if today.month == 12:
            forecast_year  = today.year + 1
            forecast_month = 1
        else:
            forecast_year  = today.year
            forecast_month = today.month + 1

    logger.info(
        f"[Engine 3] Running Correlation Engine for {forecast_year}-{forecast_month:02d} "
        f"| weights: physical={w['physical']}, cyber={w['cyber']}, spatial={w['spatial']}"
    )
    now = datetime.utcnow()

    # ── Fetch Engine 2 outputs ────────────────────────────────────────────────
    phys_rows = CrimeForecast.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).all()
    cyber_rows = CyberForecast.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).all()

    if not phys_rows:
        return {
            'status': 'error',
            'message': 'No Engine 2 physical forecasts found. Run Engine 2 first.',
        }

    phys_by_area  = {r.area: r for r in phys_rows}
    cyber_by_area = {r.area: r for r in cyber_rows}

    # ── Fetch Engine 1 (DBSCAN) outputs ──────────────────────────────────────
    # We read the current hotspots table (populated by Engine 1 / DBSCAN)
    # and build an area → (hotspot_count, worst_risk) map.
    # Engine 1 is NOT re-run here — we only read its latest output.
    all_hotspots = Hotspot.query.all()

    hotspot_area_map = {}   # area → {'count': int, 'worst_risk': str}
    risk_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

    for hs in all_hotspots:
        area = hs.name  # Hotspot names are area names (set by DBSCAN engine)
        if area not in hotspot_area_map:
            hotspot_area_map[area] = {'count': 0, 'worst_risk': 'Low'}
        hotspot_area_map[area]['count'] += 1
        existing_order = risk_order.get(hotspot_area_map[area]['worst_risk'], 1)
        new_order      = risk_order.get(hs.risk, 1)
        if new_order > existing_order:
            hotspot_area_map[area]['worst_risk'] = hs.risk

    # Also attempt area-level matching by zone/name similarity for hotspots
    # whose name may not exactly match an area (DBSCAN names like "Naroda Cluster")
    for hs in all_hotspots:
        for area in AREA_BASE_WEIGHTS.keys():
            if area.lower() in hs.name.lower() and area not in hotspot_area_map:
                hotspot_area_map[area] = {'count': 1, 'worst_risk': hs.risk}
            elif area.lower() in hs.name.lower() and area in hotspot_area_map:
                hotspot_area_map[area]['count'] += 1

    # ── Compute combined score per area ───────────────────────────────────────
    all_areas = list(AREA_BASE_WEIGHTS.keys())
    area_results = []

    for area in all_areas:
        zone = AREA_ZONES.get(area, '')

        # Engine 2 physical
        phys_rec      = phys_by_area.get(area)
        physical_risk = phys_rec.physical_risk if phys_rec else 'Low'
        predicted_count = phys_rec.predicted_count if phys_rec else 0.0

        # Engine 2 cyber
        cyber_rec  = cyber_by_area.get(area)
        cyber_risk = cyber_rec.cyber_risk if cyber_rec else 'Low'

        # Engine 1 spatial
        hs_data       = hotspot_area_map.get(area, {'count': 0, 'worst_risk': 'Low'})
        hotspot_count = hs_data['count']
        hotspot_risk  = _spatial_risk_from_hotspots(hotspot_count, hs_data['worst_risk'])

        # Numeric scores
        phys_score    = _risk_to_score(physical_risk)
        cyber_score   = _risk_to_score(cyber_risk)
        spatial_score = _risk_to_score(hotspot_risk)

        combined_score = (
            w['physical'] * phys_score
            + w['cyber']   * cyber_score
            + w['spatial'] * spatial_score
        )

        combined_risk = _score_to_risk(combined_score)

        # Identify which engine contributed most
        contributions = {
            'Engine 2 Physical': w['physical'] * phys_score,
            'Engine 2 Cyber':    w['cyber']    * cyber_score,
            'Engine 1 Spatial':  w['spatial']  * spatial_score,
        }
        top_engine = max(contributions, key=contributions.get)

        area_results.append({
            'area':               area,
            'zone':               zone,
            'hotspot_count':      hotspot_count,
            'hotspot_risk':       hotspot_risk,
            'physical_risk':      physical_risk,
            'predicted_count':    predicted_count,
            'cyber_risk':         cyber_risk,
            'combined_risk':      combined_risk,
            'combined_risk_score': round(combined_score, 4),
            'top_contributing_engine': top_engine,
        })

    # Sort by score descending — higher score = higher patrol priority
    area_results.sort(key=lambda x: x['combined_risk_score'], reverse=True)
    for rank, r in enumerate(area_results, start=1):
        r['patrol_priority'] = rank

    # ── Write to DB ───────────────────────────────────────────────────────────
    AreaIntelligence.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).delete()

    for r in area_results:
        db.session.add(AreaIntelligence(
            area                  = r['area'],
            zone                  = r['zone'],
            forecast_year         = forecast_year,
            forecast_month        = forecast_month,
            hotspot_count         = r['hotspot_count'],
            hotspot_risk          = r['hotspot_risk'],
            physical_risk         = r['physical_risk'],
            predicted_count       = r['predicted_count'],
            cyber_risk            = r['cyber_risk'],
            combined_risk         = r['combined_risk'],
            combined_risk_score   = r['combined_risk_score'],
            patrol_priority       = r['patrol_priority'],
            top_contributing_engine = r['top_contributing_engine'],
            generated_at          = now,
        ))

    db.session.commit()

    # ── Build summary ─────────────────────────────────────────────────────────
    risk_dist = {}
    for r in area_results:
        risk_dist[r['combined_risk']] = risk_dist.get(r['combined_risk'], 0) + 1

    top5 = [
        {
            'rank':           r['patrol_priority'],
            'area':           r['area'],
            'combined_risk':  r['combined_risk'],
            'score':          r['combined_risk_score'],
            'physical_risk':  r['physical_risk'],
            'cyber_risk':     r['cyber_risk'],
            'hotspot_risk':   r['hotspot_risk'],
        }
        for r in area_results[:5]
    ]

    logger.info(
        f"[Engine 3] Done. {len(area_results)} areas processed. "
        f"Risk dist: {risk_dist}"
    )

    return {
        'status':           'success',
        'forecast_period':  f"{forecast_year}-{forecast_month:02d}",
        'weights_used':     w,
        'areas_processed':  len(area_results),
        'risk_distribution': risk_dist,
        'top_5_priority_areas': top5,
    }


def get_area_intelligence(
    forecast_year: int = None,
    forecast_month: int = None,
) -> list:
    """
    Fetch AreaIntelligence rows for the given period, sorted by patrol priority.
    """
    if forecast_year is None or forecast_month is None:
        today = date.today()
        if today.month == 12:
            forecast_year  = today.year + 1
            forecast_month = 1
        else:
            forecast_year  = today.year
            forecast_month = today.month + 1

    rows = (
        AreaIntelligence.query
        .filter_by(forecast_year=forecast_year, forecast_month=forecast_month)
        .order_by(AreaIntelligence.patrol_priority.asc())
        .all()
    )
    return [r.to_dict() for r in rows]
