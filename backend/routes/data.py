from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from db import db
from models import Crime, Cybercrime, PatrolUnit, Hotspot, Alert, Prediction, PatrolRoute

data_bp = Blueprint('data', __name__)


@data_bp.route('/crimes', methods=['GET'])
@jwt_required()
def get_crimes():
    # Support optional filters
    area     = request.args.get('area')
    severity = request.args.get('severity')
    year     = request.args.get('year', type=int)
    crime_type = request.args.get('type')

    q = Crime.query
    if area:        q = q.filter(Crime.area == area)
    if severity:    q = q.filter(Crime.severity == severity)
    if year:        q = q.filter(Crime.year == year)
    if crime_type:  q = q.filter(Crime.crime_type == crime_type)

    crimes = q.all()
    return jsonify([c.to_dict() for c in crimes]), 200


@data_bp.route('/cybercrime', methods=['GET'])
@jwt_required()
def get_cybercrime():
    year = request.args.get('year', type=int)
    q = Cybercrime.query
    if year: q = q.filter(Cybercrime.year == year)
    return jsonify([c.to_dict() for c in q.all()]), 200


@data_bp.route('/patrols', methods=['GET'])
@jwt_required()
def get_patrols():
    return jsonify([p.to_dict() for p in PatrolUnit.query.all()]), 200


@data_bp.route('/patrol-routes', methods=['GET'])
@jwt_required()
def get_routes():
    return jsonify([r.to_dict() for r in PatrolRoute.query.all()]), 200


@data_bp.route('/hotspots', methods=['GET'])
@jwt_required()
def get_hotspots_data():
    return jsonify([h.to_dict() for h in Hotspot.query.all()]), 200


@data_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts_data():
    return jsonify([a.to_dict() for a in Alert.query.order_by(Alert.timestamp.desc()).all()]), 200


@data_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_ai_predictions():
    return jsonify([p.to_dict() for p in Prediction.query.all()]), 200


@data_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Quick stats endpoint for the top header."""
    total_crimes  = Crime.query.count()
    active_patrol = PatrolUnit.query.filter(PatrolUnit.status == 'On Patrol').count()
    open_alerts   = Alert.query.filter(Alert.acknowledged == False).count()
    cyber_total   = Cybercrime.query.count()
    return jsonify({
        'total_crimes': total_crimes,
        'active_patrols': active_patrol,
        'open_alerts': open_alerts,
        'cyber_total': cyber_total,
    }), 200
