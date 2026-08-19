"""
routing.py — Dynamic Road Route Generation & Dispatch Blueprint
================================================================
Queries OSRM to generate road-following routes between patrol units and hotspots,
and manages commander-approved patrol dispatches.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import requests
import ast
import logging
import math
import json
from datetime import datetime
from db import db
from models import PatrolUnit, Hotspot, Alert, ActiveDispatch
from services.audit_service import log_action

logger = logging.getLogger(__name__)
routing_bp = Blueprint('routing', __name__)

OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/{coords}"

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def _haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance in kilometers between two GPS coordinates using Haversine."""
    degrees_to_radians = math.pi / 180.0
    phi1 = lat1 * degrees_to_radians
    phi2 = lat2 * degrees_to_radians
    
    dphi = (lat2 - lat1) * degrees_to_radians
    dlambda = (lon2 - lon1) * degrees_to_radians
    
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return 6371.0 * c


def calculate_route(start_lat, start_lng, end_lat, end_lng):
    """
    Query the public OSRM server to calculate road-following route.
    OSRM expects coordinates as lng,lat.
    """
    coords_param = f"{start_lng},{start_lat};{end_lng},{end_lat}"
    url = OSRM_ROUTE_URL.format(coords=coords_param) + "?overview=full&geometries=geojson"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                geometry = route['geometry']['coordinates'] # list of [lng, lat]
                waypoints = [[coords[1], coords[0]] for coords in geometry]
                distance_km = round(route['distance'] / 1000.0, 2)
                duration_mins = int(round(route['duration'] / 60.0))
                return {
                    'waypoints': waypoints,
                    'distance_km': distance_km,
                    'eta_minutes': duration_mins
                }
    except Exception as e:
        logger.error(f"[OSRM Engine] Routing failed: {e}")
    return None

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@routing_bp.route('/routes/generate', methods=['POST'])
@jwt_required()
def generate_dynamic_route():
    """
    POST /api/routes/generate
    Manual trigger endpoint from Phase 7A.
    """
    body = request.get_json(silent=True) or {}
    patrol_id = body.get('patrol_id')
    hotspot_id = body.get('hotspot_id')

    if not patrol_id or not hotspot_id:
        return jsonify({'status': 'error', 'message': 'Missing patrol_id or hotspot_id'}), 400

    patrol = PatrolUnit.query.get(patrol_id)
    if not patrol:
        return jsonify({'status': 'error', 'message': f'Patrol unit {patrol_id} not found'}), 404

    try:
        loc = patrol.current_location
        if isinstance(loc, str):
            loc = ast.literal_eval(loc)
        start_lat = float(loc['lat'])
        start_lng = float(loc['lng'])
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Patrol unit coordinates invalid: {e}'}), 400

    hotspot = Hotspot.query.get(hotspot_id)
    if not hotspot:
        return jsonify({'status': 'error', 'message': f'Hotspot {hotspot_id} not found'}), 404

    route_res = calculate_route(start_lat, start_lng, hotspot.lat, hotspot.lng)
    if not route_res:
        return jsonify({'status': 'error', 'message': 'OSRM routing engine failed.'}), 502

    # Log route query
    claims = get_jwt()
    username = get_jwt_identity() or claims.get('sub', 'unknown')
    log_action(
        username=username, role=claims.get('role', ''),
        action='ROUTE_GENERATION', resource='OSRM Routing Engine',
        detail=f"Unit: {patrol_id} -> Hotspot: {hotspot_id} ({route_res['distance_km']}km)"
    )

    return jsonify({
        'status': 'success',
        'patrol_id': patrol_id,
        'hotspot_id': hotspot_id,
        'origin': {'lat': start_lat, 'lng': start_lng},
        'destination': {'lat': hotspot.lat, 'lng': hotspot.lng},
        'distance_km': route_res['distance_km'],
        'eta_minutes': route_res['eta_minutes'],
        'waypoints': route_res['waypoints'],
        'mode': 'Dynamic Road Route'
    }), 200


@routing_bp.route('/dispatch/recommendations', methods=['GET'])
@jwt_required()
def get_dispatch_recommendations():
    """
    GET /api/dispatch/recommendations
    Identifies nearest available patrol unit for every High/Critical hotspot.
    """
    # 1. Fetch High/Critical hotspots
    hotspots = Hotspot.query.filter(Hotspot.risk.in_(['High', 'Critical'])).order_by(Hotspot.score.desc()).all()
    
    # 2. Fetch available units (not inactive, not responding)
    available_units = PatrolUnit.query.filter(
        PatrolUnit.status.notin_(['Responding', 'Inactive'])
    ).all()

    # 3. Fetch active alerts to map already assigned dispatches
    active_alerts = Alert.query.filter(
        Alert.acknowledged == False,
        Alert.assigned_to.isnot(None)
    ).all()

    assigned_map = {a.area: a.assigned_to for a in active_alerts}

    results = []
    for hs in hotspots:
        area_name = hs.name.replace(' Zone', '')
        assigned_patrol = assigned_map.get(area_name)

        if assigned_patrol:
            # Already dispatched
            results.append({
                'hotspot_id': hs.id,
                'area': area_name,
                'risk': hs.risk,
                'score': hs.score,
                'crimes': hs.crimes,
                'dispatched': True,
                'assigned_patrol_id': assigned_patrol,
                'recommended_unit': None
            })
            continue

        # Find closest available unit
        best_unit = None
        min_dist = float('inf')

        for unit in available_units:
            try:
                loc = unit.current_location
                if isinstance(loc, str):
                    loc = ast.literal_eval(loc)
                u_lat, u_lng = float(loc['lat']), float(loc['lng'])
                dist = _haversine_km(hs.lat, hs.lng, u_lat, u_lng)
                if dist < min_dist:
                    min_dist = dist
                    best_unit = unit
            except Exception:
                continue

        rec_unit = None
        if best_unit:
            rec_unit = {
                'vehicle_id': best_unit.vehicle_id,
                'officer_name': best_unit.officer_name,
                'vehicle_type': best_unit.vehicle_type,
                'status': best_unit.status,
                'distance_km': round(min_dist, 2)
            }

        results.append({
            'hotspot_id': hs.id,
            'area': area_name,
            'risk': hs.risk,
            'score': hs.score,
            'crimes': hs.crimes,
            'dispatched': False,
            'recommended_unit': rec_unit
        })

    return jsonify({
        'status': 'success',
        'recommendations': results
    }), 200


@routing_bp.route('/dispatch', methods=['POST'])
@jwt_required()
def execute_dispatch():
    """
    POST /api/dispatch
    Transactional dynamic dispatch assignment.
    Body: { "hotspot_id": "HS-ML-001", "patrol_id": "AHD-PCR-004" }
    """
    claims = get_jwt()
    body = request.get_json(silent=True) or {}
    hotspot_id = body.get('hotspot_id')
    patrol_id = body.get('patrol_id')

    if not hotspot_id or not patrol_id:
        return jsonify({'status': 'error', 'message': 'Missing hotspot_id or patrol_id'}), 400

    # Execute inside transaction with row locks to prevent race conditions
    try:
        # Lock the patrol unit row
        patrol = PatrolUnit.query.with_for_update().get(patrol_id)
        if not patrol:
            return jsonify({'status': 'error', 'message': f'Patrol unit {patrol_id} not found'}), 404

        # Validate Hotspot
        hotspot = Hotspot.query.get(hotspot_id)
        if not hotspot:
            return jsonify({'status': 'error', 'message': f'Hotspot {hotspot_id} not found'}), 404

        # Race-condition safeguard check
        if patrol.status in ('Responding', 'Inactive'):
            return jsonify({
                'status': 'conflict',
                'message': f'Patrol unit {patrol_id} is no longer available.'
            }), 409

        if hotspot.risk not in ('High', 'Critical'):
            return jsonify({
                'status': 'error',
                'message': f'Dispatch restricted to High/Critical hotspots. Hotspot {hotspot_id} is {hotspot.risk}.'
            }), 400

        # Parse coordinates
        try:
            loc = patrol.current_location
            if isinstance(loc, str):
                loc = ast.literal_eval(loc)
            start_lat = float(loc['lat'])
            start_lng = float(loc['lng'])
        except Exception:
            return jsonify({'status': 'error', 'message': 'Patrol coordinates invalid.'}), 400

        # 3. Call OSRM *before* committing the status change to handle failures safely
        route_res = calculate_route(start_lat, start_lng, hotspot.lat, hotspot.lng)
        if not route_res:
            db.session.rollback()  # Abort transaction
            return jsonify({
                'status': 'error',
                'message': 'OSRM route generation failed. Dispatch aborted to preserve patrol availability.'
            }), 502

        # 4. Atomically persist changes
        # Find or create corresponding alert
        area_name = hotspot.name.replace(' Zone', '')
        alert = Alert.query.filter_by(area=area_name, acknowledged=False).with_for_update().first()
        
        if not alert:
            # Create alert matching existing schema
            alert_id = f"ALT-ML-D-{hotspot.id}"
            alert = Alert(
                id=alert_id,
                type=hotspot.risk.upper(),
                title=f"DBSCAN: {hotspot.risk} Risk Hotspot Detected",
                message=f"ML Engine detected a {hotspot.risk} risk cluster in {area_name}. Score: {hotspot.score}/100.",
                area=area_name,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
                acknowledged=False,
                assigned_to=patrol.vehicle_id
            )
            db.session.add(alert)
        else:
            alert.assigned_to = patrol.vehicle_id

        # Update patrol status in DB
        patrol.status = 'Responding'
        db.session.commit()

        # ── Phase 7C: Persist active dispatch with route geometry ──
        import json as _json
        # Remove any stale dispatch for this patrol (shouldn't exist, but defensive)
        ActiveDispatch.query.filter_by(patrol_id=patrol_id).delete()
        active_dispatch = ActiveDispatch(
            patrol_id=patrol_id,
            hotspot_id=hotspot_id,
            alert_id=alert.id,
            route_geometry=_json.dumps(route_res['waypoints']),
            total_points=len(route_res['waypoints']),
            current_index=0,
            distance_km=route_res['distance_km'],
            eta_minutes=route_res['eta_minutes'],
            status='Responding',
            dispatched_at=datetime.now()
        )
        db.session.add(active_dispatch)
        db.session.commit()

        # Log to Audit Log for security/compliance
        username = get_jwt_identity() or claims.get('sub', 'unknown')
        log_action(
            username=username, role=claims.get('role', ''),
            action='DISPATCH', resource='Patrol Dispatch System',
            detail=f"Unit {patrol_id} assigned to hotspot {hotspot_id} ({route_res['distance_km']}km)"
        )

        return jsonify({
            'status': 'success',
            'message': 'Dispatch successfully confirmed.',
            'patrol_id': patrol_id,
            'hotspot_id': hotspot_id,
            'officer_name': patrol.officer_name,
            'distance_km': route_res['distance_km'],
            'eta_minutes': route_res['eta_minutes'],
            'waypoints': route_res['waypoints'],
            'mode': 'Dynamic Road Route'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception("Transactional dispatch aborted due to backend error")
        return jsonify({'status': 'error', 'message': f'Backend error during transaction: {str(e)}'}), 500


@routing_bp.route('/dispatch/active', methods=['GET'])
@jwt_required()
def get_active_dispatches():
    """
    GET /api/dispatch/active
    Returns all currently active (non-arrived) dispatches with their route geometry.
    Used by frontend to resume simulations after browser refresh.
    """
    dispatches = ActiveDispatch.query.filter(
        ActiveDispatch.status != 'Arrived'
    ).all()
    return jsonify({
        'status': 'success',
        'dispatches': [d.to_dict() for d in dispatches]
    }), 200


@routing_bp.route('/dispatch/update-position', methods=['POST'])
@jwt_required()
def update_patrol_position():
    """
    POST /api/dispatch/update-position
    Updates simulated patrol position along the OSRM route.
    Body: { "patrol_id": "AHD-PCR-002", "step_index": 5 }
    The backend reads the actual coordinate from stored route geometry.
    """
    import json as _json
    body = request.get_json(silent=True) or {}
    patrol_id = body.get('patrol_id')
    step_index = body.get('step_index')

    if not patrol_id or step_index is None:
        return jsonify({'status': 'error', 'message': 'Missing patrol_id or step_index'}), 400

    try:
        step_index = int(step_index)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'step_index must be an integer'}), 400

    # Find active dispatch
    dispatch = ActiveDispatch.query.filter_by(patrol_id=patrol_id, status='Responding').first()
    if not dispatch:
        return jsonify({'status': 'error', 'message': f'No active dispatch found for patrol {patrol_id}'}), 404

    # Validate step_index range
    if step_index < 0 or step_index >= dispatch.total_points:
        return jsonify({'status': 'error', 'message': f'step_index {step_index} out of range (0-{dispatch.total_points - 1})'}), 400

    # Parse stored route geometry
    try:
        geometry = _json.loads(dispatch.route_geometry)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Stored route geometry is corrupt'}), 500

    # Get coordinate at step_index
    coord = geometry[step_index]  # [lat, lng]
    new_lat, new_lng = coord[0], coord[1]

    # Update patrol unit location in DB
    patrol = PatrolUnit.query.get(patrol_id)
    if not patrol:
        return jsonify({'status': 'error', 'message': f'Patrol unit {patrol_id} not found'}), 404

    patrol.current_location = str({'lat': new_lat, 'lng': new_lng})
    patrol.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dispatch.current_index = step_index
    db.session.commit()

    # Calculate progress
    progress_pct = round((step_index / (dispatch.total_points - 1)) * 100) if dispatch.total_points > 1 else 100

    # Calculate simulated remaining ETA
    remaining_fraction = 1.0 - (step_index / max(dispatch.total_points - 1, 1))
    simulated_eta = max(0, int(round(dispatch.eta_minutes * remaining_fraction)))

    return jsonify({
        'status': 'success',
        'patrol_id': patrol_id,
        'step_index': step_index,
        'position': {'lat': new_lat, 'lng': new_lng},
        'progress_pct': progress_pct,
        'simulated_eta_minutes': simulated_eta,
        'total_points': dispatch.total_points,
        'is_final': step_index >= dispatch.total_points - 1
    }), 200


@routing_bp.route('/dispatch/arrive', methods=['POST'])
@jwt_required()
def patrol_arrival():
    """
    POST /api/dispatch/arrive
    Called when simulated patrol reaches final OSRM waypoint.
    Resolves alert, resets patrol to Standby, logs audit event.
    Body: { "patrol_id": "AHD-PCR-002" }
    """
    claims = get_jwt()
    body = request.get_json(silent=True) or {}
    patrol_id = body.get('patrol_id')

    if not patrol_id:
        return jsonify({'status': 'error', 'message': 'Missing patrol_id'}), 400

    # Find active dispatch
    dispatch = ActiveDispatch.query.filter_by(patrol_id=patrol_id, status='Responding').first()
    if not dispatch:
        return jsonify({'status': 'error', 'message': f'No active dispatch found for patrol {patrol_id}'}), 404

    try:
        # 1. Mark dispatch as arrived
        dispatch.status = 'Arrived'
        dispatch.arrived_at = datetime.now()
        dispatch.current_index = dispatch.total_points - 1

        # 2. Reset patrol to Standby
        patrol = PatrolUnit.query.get(patrol_id)
        if patrol:
            patrol.status = 'Standby'
            patrol.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Increment incidents handled
            patrol.incidents_handled = (patrol.incidents_handled or 0) + 1

        # 3. Acknowledge the associated alert
        if dispatch.alert_id:
            alert = Alert.query.get(dispatch.alert_id)
            if alert:
                alert.acknowledged = True

        db.session.commit()

        # 4. Log audit event
        username = get_jwt_identity() or claims.get('sub', 'unknown')
        log_action(
            username=username, role=claims.get('role', ''),
            action='PATROL_ARRIVAL', resource='Simulated GPS Tracking',
            detail=f"Unit {patrol_id} arrived at hotspot {dispatch.hotspot_id}. "
                   f"Route: {dispatch.distance_km}km, dispatch duration: "
                   f"{dispatch.dispatched_at.strftime('%H:%M')} → {dispatch.arrived_at.strftime('%H:%M')}"
        )

        return jsonify({
            'status': 'success',
            'message': f'Patrol {patrol_id} has arrived at hotspot {dispatch.hotspot_id}.',
            'patrol_id': patrol_id,
            'hotspot_id': dispatch.hotspot_id,
            'patrol_status': 'Standby',
            'alert_acknowledged': True
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Arrival processing failed')
        return jsonify({'status': 'error', 'message': f'Arrival processing error: {str(e)}'}), 500
