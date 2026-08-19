"""
simulation.py — Scenario Simulation API
=========================================
POST /api/simulate
    Applies domain-informed risk multipliers to current Engine 3 outputs
    and returns adjusted per-area risk — READ ONLY, no DB writes.

Scenarios & Multipliers:
    festival    : ×1.40  (Navratri, Diwali, Uttarayan)
    large_event : ×1.25  (IPL, rallies, concerts)
    curfew      : ×0.55  (curfew / heavy deployment reduces risk)
    night_ops   : ×1.20  (night shift — violent crime spike)
    normal      : ×1.00  (baseline)

Area modifiers (zone-based):
    Festival areas (Navrangpura, Vastrapur, Paldi, Ellis Bridge): +15% extra during festival
    Industrial zones (Naroda, Vatva, Narol): extra curfew reduction

Output: list of {area, zone, original_risk, simulated_risk, original_score,
                 simulated_score, change_pct, patrol_priority}
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import AreaIntelligence
from datetime import date

simulation_bp = Blueprint('simulation', __name__)

# ─── SCENARIO CONFIG ──────────────────────────────────────────────────────────

SCENARIO_MULTIPLIERS = {
    'festival':    1.40,
    'large_event': 1.25,
    'curfew':      0.55,
    'night_ops':   1.20,
    'normal':      1.00,
}

SCENARIO_LABELS = {
    'festival':    'Festival Mode (Navratri / Diwali / Uttarayan)',
    'large_event': 'Large Public Event (IPL / Rally / Concert)',
    'curfew':      'Curfew / Heavy Deployment',
    'night_ops':   'Night Operations',
    'normal':      'Normal Operations (Baseline)',
}

# Areas that get extra multiplier during festivals
FESTIVAL_HOTSPOT_AREAS = {'Navrangpura', 'Vastrapur', 'Paldi', 'Ellis Bridge', 'Maninagar', 'Naroda'}

# Risk score → label
def _score_to_risk(score: float) -> str:
    if score < 0.35: return 'Low'
    if score < 0.55: return 'Medium'
    if score < 0.75: return 'High'
    return 'Critical'


@simulation_bp.route('/simulate', methods=['POST'])
@jwt_required()
def run_simulation():
    """
    POST /api/simulate
    Body: { "scenario": "festival", "area": "all" | "<AreaName>" }
    Returns adjusted risk for all areas (or one area), sorted by simulated patrol priority.
    """
    claims  = get_jwt()
    body    = request.get_json(silent=True) or {}
    scenario = body.get('scenario', 'normal').lower()
    area_filter = body.get('area', 'all')

    if scenario not in SCENARIO_MULTIPLIERS:
        return jsonify({
            'status': 'error',
            'message': f"Unknown scenario '{scenario}'. Valid: {list(SCENARIO_MULTIPLIERS.keys())}"
        }), 400

    # Fetch latest Engine 3 data
    today = date.today()
    forecast_month = today.month + 1 if today.month < 12 else 1
    forecast_year  = today.year if today.month < 12 else today.year + 1

    rows = AreaIntelligence.query.filter_by(
        forecast_year=forecast_year,
        forecast_month=forecast_month,
    ).all()

    if not rows:
        # Fall back to any available data
        rows = AreaIntelligence.query.order_by(
            AreaIntelligence.forecast_year.desc(),
            AreaIntelligence.forecast_month.desc()
        ).limit(27).all()

    if not rows:
        return jsonify({'status': 'error', 'message': 'No Engine 3 data available. Run Engine 3 first.'}), 404

    base_mult = SCENARIO_MULTIPLIERS[scenario]
    results = []

    for r in rows:
        if area_filter != 'all' and r.area != area_filter:
            continue

        orig_score = r.combined_risk_score or 0.0

        # Area-specific extra modifier for festival scenario
        area_mult = base_mult
        if scenario == 'festival' and r.area in FESTIVAL_HOTSPOT_AREAS:
            area_mult = min(1.0, base_mult * 1.10)  # extra 10% for hotspot areas

        sim_score = min(1.0, orig_score * area_mult)
        change_pct = round(((sim_score - orig_score) / max(orig_score, 0.01)) * 100, 1)

        results.append({
            'area':             r.area,
            'zone':             r.zone,
            'original_risk':    r.combined_risk,
            'simulated_risk':   _score_to_risk(sim_score),
            'original_score':   round(orig_score, 4),
            'simulated_score':  round(sim_score, 4),
            'change_pct':       change_pct,
            'physical_risk':    r.physical_risk,
            'cyber_risk':       r.cyber_risk,
            'hotspot_risk':     r.hotspot_risk,
        })

    # Sort by simulated score descending → assign simulated patrol priority
    results.sort(key=lambda x: x['simulated_score'], reverse=True)
    for i, r in enumerate(results, start=1):
        r['simulated_patrol_priority'] = i

    # Summary
    orig_dist = {}
    sim_dist  = {}
    for r in results:
        orig_dist[r['original_risk']]  = orig_dist.get(r['original_risk'],  0) + 1
        sim_dist[r['simulated_risk']]  = sim_dist.get(r['simulated_risk'],  0) + 1

    areas_escalated = sum(1 for r in results if
        ['Low','Medium','High','Critical'].index(r['simulated_risk']) >
        ['Low','Medium','High','Critical'].index(r['original_risk']))
    areas_reduced = sum(1 for r in results if
        ['Low','Medium','High','Critical'].index(r['simulated_risk']) <
        ['Low','Medium','High','Critical'].index(r['original_risk']))

    return jsonify({
        'status':           'success',
        'scenario':         scenario,
        'scenario_label':   SCENARIO_LABELS[scenario],
        'multiplier':       base_mult,
        'area_filter':      area_filter,
        'forecast_period':  f"{forecast_year}-{forecast_month:02d}",
        'areas_escalated':  areas_escalated,
        'areas_reduced':    areas_reduced,
        'original_distribution':  orig_dist,
        'simulated_distribution': sim_dist,
        'areas':            results,
    }), 200


@simulation_bp.route('/simulate/scenarios', methods=['GET'])
@jwt_required()
def list_scenarios():
    """GET /api/simulate/scenarios — returns available scenario configs"""
    return jsonify({
        'status': 'success',
        'scenarios': [
            {'key': k, 'label': SCENARIO_LABELS[k], 'multiplier': v}
            for k, v in SCENARIO_MULTIPLIERS.items()
        ]
    }), 200
