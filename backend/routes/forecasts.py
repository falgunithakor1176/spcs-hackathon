"""
forecasts.py — Phase 6C: Engine 2 & Engine 3 REST API Endpoints
================================================================

Endpoints:
    POST  /api/engine2/run                 — Run Engine 2 (RF predictions) for next month
    GET   /api/engine2/forecasts           — Fetch latest Engine 2 forecast rows
    POST  /api/engine3/run                 — Run Engine 3 (Correlation Engine)
    GET   /api/engine3/area-intelligence   — Fetch combined risk per area (sorted by priority)
    GET   /api/engine3/config              — Return current heuristic weights + model config
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from services.prediction_engine import (
    run_prediction_engine,
    get_latest_forecasts,
)
from services.correlation_engine import (
    run_correlation_engine,
    get_area_intelligence,
    WEIGHTS,
)
from services.audit_service import log_action

import json, os


forecasts_bp = Blueprint('forecasts', __name__)

_BACKEND_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FROZEN_CONFIG = None


def _load_frozen_config():
    global _FROZEN_CONFIG
    if _FROZEN_CONFIG is None:
        cfg_path = os.path.join(_BACKEND_DIR, 'ml_models', 'frozen_model_config.json')
        with open(cfg_path, 'r') as f:
            _FROZEN_CONFIG = json.load(f)
    return _FROZEN_CONFIG


# ─── ENGINE 2 ─────────────────────────────────────────────────────────────────

@forecasts_bp.route('/engine2/run', methods=['POST'])
@jwt_required()
def run_engine2():
    body           = request.get_json(silent=True) or {}
    forecast_year  = body.get('forecast_year')
    forecast_month = body.get('forecast_month')
    try:
        claims = get_jwt()
        result = run_prediction_engine(forecast_year=forecast_year, forecast_month=forecast_month)
        log_action(get_jwt_identity() if False else claims.get('sub', 'unknown'),
                   claims.get('role',''), 'ENGINE_RUN', 'Engine 2',
                   f"period={result.get('forecast_period')}")
        return jsonify(result), 200
    except FileNotFoundError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Engine 2 failed: {str(e)}'}), 500


@forecasts_bp.route('/engine2/forecasts', methods=['GET'])
@jwt_required()
def get_engine2_forecasts():
    """
    GET /api/engine2/forecasts?year=2026&month=8
    Returns latest Engine 2 forecasts (physical + cyber) per area.
    """
    year  = request.args.get('year',  type=int)
    month = request.args.get('month', type=int)

    try:
        data = get_latest_forecasts(forecast_year=year, forecast_month=month)
        return jsonify({'status': 'success', 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ─── ENGINE 3 ─────────────────────────────────────────────────────────────────

@forecasts_bp.route('/engine3/run', methods=['POST'])
@jwt_required()
def run_engine3():
    """
    POST /api/engine3/run
    Triggers Engine 3: Correlates Engine 1 + Engine 2 into combined risk.
    Optional JSON body:
    {
        "forecast_year": 2026,
        "forecast_month": 9,
        "weights": { "physical": 0.45, "cyber": 0.25, "spatial": 0.30 }
    }
    If weights are omitted, defaults are used.
    """
    body           = request.get_json(silent=True) or {}
    forecast_year  = body.get('forecast_year')
    forecast_month = body.get('forecast_month')
    weights        = body.get('weights')

    try:
        result = run_correlation_engine(
            forecast_year=forecast_year,
            forecast_month=forecast_month,
            weights=weights,
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Engine 3 failed: {str(e)}'}), 500


@forecasts_bp.route('/engine3/area-intelligence', methods=['GET'])
@jwt_required()
def get_engine3_intelligence():
    """
    GET /api/engine3/area-intelligence?year=2026&month=8
    Returns combined risk per area sorted by patrol_priority (1 = highest risk).
    """
    year  = request.args.get('year',  type=int)
    month = request.args.get('month', type=int)

    try:
        rows = get_area_intelligence(forecast_year=year, forecast_month=month)
        return jsonify({
            'status': 'success',
            'count': len(rows),
            'data': rows,
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forecasts_bp.route('/engine3/config', methods=['GET'])
@jwt_required()
def get_engine3_config():
    """
    GET /api/engine3/config
    Returns the current heuristic weights, model metadata, and performance metrics.
    This ensures full transparency: weights are NOT hidden inside the algorithm.
    """
    try:
        frozen = _load_frozen_config()
        return jsonify({
            'status': 'success',
            'engine3_weights': {
                'description': (
                    'Domain-informed heuristic weights for combining Engine 1, 2 outputs. '
                    'These are configurable parameters, not fixed AI formulas.'
                ),
                'weights': WEIGHTS,
                'risk_score_mapping': {
                    'Low': 0.25, 'Medium': 0.50, 'High': 0.75, 'Critical': 1.00
                },
                'risk_threshold_from_score': {
                    'Low': '< 0.35',
                    'Medium': '0.35 – 0.54',
                    'High': '0.55 – 0.74',
                    'Critical': '>= 0.75',
                },
            },
            'engine2_physical_model': {
                'type': frozen['physical']['model_type'],
                'hyperparameters': {
                    'n_estimators':      frozen['physical']['n_estimators'],
                    'max_depth':         frozen['physical']['max_depth'],
                    'min_samples_leaf':  frozen['physical']['min_samples_leaf'],
                    'min_samples_split': frozen['physical']['min_samples_split'],
                },
                'validation_metrics': frozen['physical']['metrics'],
                'n_features': len(frozen['physical']['feature_names']),
            },
            'engine2_cyber_model': {
                'type': frozen['cyber']['model_type'],
                'hyperparameters': {
                    'n_estimators':      frozen['cyber']['n_estimators'],
                    'max_depth':         frozen['cyber']['max_depth'],
                    'min_samples_leaf':  frozen['cyber']['min_samples_leaf'],
                    'min_samples_split': frozen['cyber']['min_samples_split'],
                    'class_weight':      frozen['cyber']['class_weight'],
                },
                'validation_metrics': frozen['cyber']['metrics'],
                'risk_thresholds': frozen['cyber']['risk_thresholds'],
                'n_features': len(frozen['cyber']['feature_names']),
            },
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
