"""
ML API Endpoints - Exposes the DBSCAN Hotspot Engine via REST API
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from services.ml_service import run_dbscan_engine

ml_bp = Blueprint('ml', __name__)


@ml_bp.route('/ml/run', methods=['POST'])
@jwt_required()
def trigger_ml_engine():
    """
    POST /api/ml/run
    Triggers the DBSCAN Hotspot Detection Engine.
    - Fetches crimes from the dense 30-day window
    - Runs DBSCAN clustering (Config C: eps=300m, min_samples=5)
    - TRUNCATES old hotspots and INSERTS new ML-generated ones
    - Generates alerts for High/Critical hotspots
    - Returns full summary with metrics
    """
    try:
        result = run_dbscan_engine()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ML Engine failed: {str(e)}'
        }), 500


@ml_bp.route('/ml/status', methods=['GET'])
@jwt_required()
def ml_status():
    """
    GET /api/ml/status
    Returns the current ML engine configuration and readiness.
    """
    return jsonify({
        'engine': 'DBSCAN Hotspot Detection',
        'version': '1.0',
        'config': {
            'eps_meters': 300,
            'min_samples': 5,
            'time_window': '2025-02-26 to 2025-03-28',
            'scoring': 'Severity-weighted (Critical=4, High=3, Medium=2, Low=1)',
            'duplicate_prevention': 'TRUNCATE + INSERT'
        },
        'status': 'ready'
    }), 200
