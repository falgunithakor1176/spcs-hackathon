"""
prediction_engine.py — Phase 6C: Engine 2 (Future Crime Risk Prediction)
=========================================================================

Purpose:
    Generate next-month crime forecasts for every area using the frozen
    Random Forest models trained in Phase 6B.

    Physical Crime  → RF Regressor  → predicted count → physical_risk label
    Cybercrime      → RF Classifier → cyber_risk label directly

    Results are UPSERTED into:
        crime_forecasts    (physical predictions)
        cyber_forecasts    (cyber predictions)

Constraints:
    - DOES NOT touch DBSCAN / Engine 1 / hotspots table
    - DOES NOT touch any other existing table
    - No confidence_score fields (not mathematically justified)
    - Risk thresholds derived from training-set quantiles (documented in frozen config)
    - Weights are configurable heuristics, not "AI formulas"

Risk Thresholds (physical, from Phase 6B training distribution):
    Low      : predicted_count <= 6
    Medium   : 7 <= predicted_count <= 10
    High     : 11 <= predicted_count <= 16
    Critical : predicted_count > 16
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, date
import joblib

from db import db
from models import CrimeForecast, CyberForecast

logger = logging.getLogger(__name__)

# ─── PATHS ────────────────────────────────────────────────────────────────────

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_DIR   = os.path.join(_BACKEND_DIR, 'ml_models')

# ─── PHYSICAL RISK THRESHOLDS (from training data quantiles, Phase 6B) ────────
# Q25=6, Q50=10, Q75=16 on the training set target distribution
PHYSICAL_RISK_THRESHOLDS = {
    'Low':      (None, 6),
    'Medium':   (7,   10),
    'High':     (11,  16),
    'Critical': (17, None),
}

def _count_to_physical_risk(predicted_count: float) -> str:
    c = float(predicted_count)
    if c <= 6:   return 'Low'
    if c <= 10:  return 'Medium'
    if c <= 16:  return 'High'
    return 'Critical'


# ─── LAZY MODEL LOADING ───────────────────────────────────────────────────────

_physical_model        = None
_physical_feature_names = None
_cyber_model           = None
_cyber_feature_names   = None
_frozen_config         = None


def _load_models():
    global _physical_model, _physical_feature_names
    global _cyber_model, _cyber_feature_names, _frozen_config

    if _physical_model is None:
        phys_path = os.path.join(_MODEL_DIR, 'physical_rf_model.joblib')
        phys_feat = os.path.join(_MODEL_DIR, 'physical_feature_names.joblib')
        if not os.path.exists(phys_path):
            raise FileNotFoundError(f"Physical model not found: {phys_path}")
        _physical_model         = joblib.load(phys_path)
        _physical_feature_names = joblib.load(phys_feat)
        logger.info("[Engine 2] Physical RF model loaded.")

    if _cyber_model is None:
        cyber_path = os.path.join(_MODEL_DIR, 'cyber_rf_classifier.joblib')
        cyber_feat = os.path.join(_MODEL_DIR, 'cyber_feature_names.joblib')
        if not os.path.exists(cyber_path):
            raise FileNotFoundError(f"Cyber model not found: {cyber_path}")
        _cyber_model          = joblib.load(cyber_path)
        _cyber_feature_names  = joblib.load(cyber_feat)
        logger.info("[Engine 2] Cyber RF classifier loaded.")

    if _frozen_config is None:
        cfg_path = os.path.join(_MODEL_DIR, 'frozen_model_config.json')
        with open(cfg_path, 'r') as f:
            _frozen_config = json.load(f)


# ─── FEATURE BUILDING FOR INFERENCE ──────────────────────────────────────────

def _build_inference_features(forecast_year: int, forecast_month: int):
    """
    Build one inference feature row per area for the given target month.
    Uses the last known data from the database as look-back context.
    Returns two DataFrames: phys_df and cyber_df (one row per area).
    """
    from services.feature_engine import (
        build_physical_training_matrix,
        build_cyber_training_matrix,
    )

    # Rebuild the full cleaned matrices
    _, _, _, phys_clean = build_physical_training_matrix()
    _, _, _, cyber_clean = build_cyber_training_matrix()

    # For inference, we take the most recent row per area and adjust temporal features
    # for the target month — this simulates asking "what will next month look like
    # given everything we know up to the current month?"

    # Physical — use most recent area row and re-encode temporal features
    phys_latest = (
        phys_clean
        .sort_values(['area', 'year', 'month'])
        .groupby('area')
        .last()
        .reset_index()
    )

    # Update temporal features for the forecast period
    phys_latest['month_sin'] = np.sin(2 * np.pi * forecast_month / 12)
    phys_latest['month_cos'] = np.cos(2 * np.pi * forecast_month / 12)
    phys_latest['quarter']   = (forecast_month - 1) // 3 + 1

    # Festival months: Jan(1), Mar(3), Aug(8), Oct(10), Nov(11)
    festival_months = {1, 3, 8, 10, 11}
    phys_latest['is_festival_month'] = int(forecast_month in festival_months)

    # Cyber — same approach
    cyber_latest = (
        cyber_clean
        .sort_values(['area', 'year', 'month'])
        .groupby('area')
        .last()
        .reset_index()
    )

    cyber_latest['month_sin'] = np.sin(2 * np.pi * forecast_month / 12)
    cyber_latest['month_cos'] = np.cos(2 * np.pi * forecast_month / 12)
    cyber_latest['quarter']   = (forecast_month - 1) // 3 + 1
    cyber_latest['is_festival_month'] = int(forecast_month in festival_months)

    return phys_latest, cyber_latest


# ─── MAIN PREDICTION FUNCTION ─────────────────────────────────────────────────

def run_prediction_engine(
    forecast_year: int  = None,
    forecast_month: int = None,
) -> dict:
    """
    Generate Engine 2 predictions for the given year/month.
    Defaults to next calendar month from today.

    Returns a summary dict with counts and status.
    Upserts results into crime_forecasts and cyber_forecasts tables.
    """
    _load_models()

    # Default to next month
    if forecast_year is None or forecast_month is None:
        today = date.today()
        if today.month == 12:
            forecast_year  = today.year + 1
            forecast_month = 1
        else:
            forecast_year  = today.year
            forecast_month = today.month + 1

    logger.info(f"[Engine 2] Generating forecasts for {forecast_year}-{forecast_month:02d}")
    now = datetime.utcnow()

    # ── Build features ────────────────────────────────────────────────────────
    phys_df, cyber_df = _build_inference_features(forecast_year, forecast_month)

    # ── Physical predictions ──────────────────────────────────────────────────
    phys_feat_cols = _physical_feature_names
    # Ensure all expected columns are present; fill any missing with 0
    for col in phys_feat_cols:
        if col not in phys_df.columns:
            phys_df[col] = 0

    X_phys   = phys_df[phys_feat_cols].fillna(0).values
    y_phys   = _physical_model.predict(X_phys)
    # Clip to non-negative (regression can occasionally go negative)
    y_phys   = np.clip(y_phys, 0, None)

    phys_rows = []
    for i, row in phys_df.iterrows():
        area  = row['area']
        zone  = row.get('zone', '')
        pred  = float(y_phys[i - phys_df.index[0]] if phys_df.index[0] != 0 else y_phys[phys_df.index.get_loc(i)])
        risk  = _count_to_physical_risk(pred)
        phys_rows.append({
            'area': area, 'zone': zone,
            'predicted_count': round(pred, 2),
            'physical_risk': risk,
        })

    # ── Cyber predictions ─────────────────────────────────────────────────────
    cyber_feat_cols = _cyber_feature_names
    for col in cyber_feat_cols:
        if col not in cyber_df.columns:
            cyber_df[col] = 0

    X_cyber  = cyber_df[cyber_feat_cols].fillna(0).values
    y_cyber  = _cyber_model.predict(X_cyber)

    cyber_rows = []
    for i, row in cyber_df.iterrows():
        area  = row['area']
        zone  = row.get('zone', '')
        risk  = str(y_cyber[cyber_df.index.get_loc(i)])
        cyber_rows.append({'area': area, 'zone': zone, 'cyber_risk': risk})

    # ── Upsert to DB ──────────────────────────────────────────────────────────
    # Delete existing rows for this forecast period before inserting
    CrimeForecast.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).delete()
    CyberForecast.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).delete()

    for r in phys_rows:
        db.session.add(CrimeForecast(
            area           = r['area'],
            zone           = r['zone'],
            forecast_year  = forecast_year,
            forecast_month = forecast_month,
            predicted_count = r['predicted_count'],
            physical_risk  = r['physical_risk'],
            generated_at   = now,
        ))

    for r in cyber_rows:
        db.session.add(CyberForecast(
            area           = r['area'],
            zone           = r['zone'],
            forecast_year  = forecast_year,
            forecast_month = forecast_month,
            cyber_risk     = r['cyber_risk'],
            generated_at   = now,
        ))

    db.session.commit()
    logger.info(
        f"[Engine 2] Done. {len(phys_rows)} physical forecasts, "
        f"{len(cyber_rows)} cyber forecasts written."
    )

    # Risk distribution summary
    phys_dist = {}
    for r in phys_rows:
        phys_dist[r['physical_risk']] = phys_dist.get(r['physical_risk'], 0) + 1
    cyber_dist = {}
    for r in cyber_rows:
        cyber_dist[r['cyber_risk']] = cyber_dist.get(r['cyber_risk'], 0) + 1

    return {
        'status':          'success',
        'forecast_period': f"{forecast_year}-{forecast_month:02d}",
        'physical': {
            'areas_forecast': len(phys_rows),
            'risk_distribution': phys_dist,
        },
        'cyber': {
            'areas_forecast': len(cyber_rows),
            'risk_distribution': cyber_dist,
        },
    }


def get_latest_forecasts(forecast_year: int = None, forecast_month: int = None) -> dict:
    """
    Fetch the most recent Engine 2 forecast rows from the DB.
    Returns dicts keyed by area.
    """
    if forecast_year is None or forecast_month is None:
        today = date.today()
        if today.month == 12:
            forecast_year  = today.year + 1
            forecast_month = 1
        else:
            forecast_year  = today.year
            forecast_month = today.month + 1

    phys_rows  = CrimeForecast.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).all()
    cyber_rows = CyberForecast.query.filter_by(
        forecast_year=forecast_year, forecast_month=forecast_month
    ).all()

    phys_by_area  = {r.area: r.to_dict() for r in phys_rows}
    cyber_by_area = {r.area: r.to_dict() for r in cyber_rows}

    return {
        'forecast_period':  f"{forecast_year}-{forecast_month:02d}",
        'physical_by_area': phys_by_area,
        'cyber_by_area':    cyber_by_area,
    }
