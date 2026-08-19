"""
DBSCAN Hotspot Detection Engine - Production ML Service
Config C: eps=300m, min_samples=5
Runs against the densest 30-day window (Feb 26 - Mar 28, 2025)
"""

import numpy as np
from datetime import datetime
from sklearn.cluster import DBSCAN
from db import db
from models import Crime, Hotspot, Alert, Prediction, PatrolUnit

# Approved Config C parameters
EPS_METERS = 300
MIN_SAMPLES = 5
EARTH_RADIUS_KM = 6371.0
SCORE_MAX_RAW = 50  # Raw severity sum of 50 maps to score 100

SEVERITY_WEIGHTS = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

# Area-to-Zone mapping for the hotspot table
AREA_ZONES = {
    'Naroda': 'East', 'Bapunagar': 'East', 'Asarwa': 'East',
    'Gomtipur': 'East', 'Nikol': 'East', 'Vastral': 'East',
    'Maninagar': 'South', 'Isanpur': 'South', 'Narol': 'South',
    'Vatva': 'South', 'Paldi': 'South', 'Vejalpur': 'South', 'Sarkhej': 'South',
    'Dariapur': 'Central', 'Ellis Bridge': 'Central', 'Navrangpura': 'Central',
    'Ranip': 'North', 'Shahibaug': 'North', 'Chandkheda': 'North', 'Gota': 'North',
    'Ambavadi': 'West', 'Vastrapur': 'West', 'Satellite': 'West',
    'Thaltej': 'West', 'Prahlad Nagar': 'West', 'Bodakdev': 'West', 'Bopal': 'West',
}


def _haversine_m(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two GPS points using Haversine formula."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * np.arcsin(np.sqrt(a)) * 6371000


# Analysis window constants (used for both clustering and trend comparison)
ANALYSIS_WINDOW_START = '2025-02-26'
ANALYSIS_WINDOW_END   = '2025-03-28'
PREV_WINDOW_START     = '2025-01-27'
PREV_WINDOW_END       = '2025-02-25'


def _get_area_prev_count(primary_area):
    """
    Query the crime count for a given area in the preceding 30-day window
    (2025-01-27 to 2025-02-25) to compute a real trend percentage.
    Returns 0 if no data is found for that area in the prior window.
    """
    result = db.session.execute(db.text("""
        SELECT COUNT(*) FROM crimes
        WHERE area = :area
          AND TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') >= :start
          AND TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') <  :end
    """), {'area': primary_area, 'start': PREV_WINDOW_START, 'end': PREV_WINDOW_END}).scalar()
    return int(result or 0)


def _compute_trend(current_count, prev_count):
    """
    Compute a percentage change string between two windows.
    Returns 'New' if no prior data exists, otherwise '+X%' or '-X%'.
    """
    if prev_count == 0:
        return 'New'
    pct = ((current_count - prev_count) / prev_count) * 100
    return f'+{pct:.0f}%' if pct >= 0 else f'{pct:.0f}%'


def run_dbscan_engine():
    """
    Execute the full DBSCAN pipeline:
    1. Fetch crimes from the dense 30-day analysis window
    2. Run DBSCAN clustering
    3. TRUNCATE & INSERT new hotspots (with real trend vs preceding window)
    4. Generate alerts for High/Critical hotspots
    5. Return summary metrics
    """

    # Step 1: Fetch crimes from the dense 30-day analysis window
    crimes = db.session.execute(db.text("""
        SELECT crime_id, crime_type, severity, latitude, longitude, area
        FROM crimes
        WHERE TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') >= :start
          AND TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') <= :end
    """), {'start': ANALYSIS_WINDOW_START, 'end': ANALYSIS_WINDOW_END}).fetchall()

    if not crimes:
        return {'status': 'error', 'message': 'No crimes found in the analysis window.'}

    # Convert to numpy arrays
    lats = np.array([c.latitude for c in crimes])
    lngs = np.array([c.longitude for c in crimes])
    severities = [c.severity for c in crimes]
    areas = [c.area for c in crimes]
    crime_types = [c.crime_type for c in crimes]

    coords = np.radians(np.column_stack([lats, lngs]))

    # Step 2: Run DBSCAN
    eps_rad = (EPS_METERS / 1000.0) / EARTH_RADIUS_KM
    dbscan = DBSCAN(eps=eps_rad, min_samples=MIN_SAMPLES, algorithm='ball_tree', metric='haversine')
    labels = dbscan.fit_predict(coords)

    # Step 3: TRUNCATE existing hotspots, predictions and clean up old ML alerts
    db.session.execute(db.text("TRUNCATE TABLE hotspots"))
    db.session.execute(db.text("TRUNCATE TABLE predictions"))
    db.session.execute(db.text("DELETE FROM alerts WHERE id LIKE 'ALT-ML-%'"))

    # Build cluster data
    hotspot_records = []
    alert_records = []
    predictions_by_area = {}
    total_risk_score = 0
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    unique_clusters = set(labels)
    unique_clusters.discard(-1)  # Remove noise; compute max cluster size for density normalisation
    max_cluster_size = max(
        [int((labels == cid).sum()) for cid in unique_clusters], default=1
    )

    for cluster_id in sorted(unique_clusters):
        mask = labels == cluster_id
        cluster_lats = lats[mask]
        cluster_lngs = lngs[mask]
        cluster_sevs = [severities[i] for i in range(len(labels)) if labels[i] == cluster_id]
        cluster_areas = [areas[i] for i in range(len(labels)) if labels[i] == cluster_id]
        cluster_crimes = [crime_types[i] for i in range(len(labels)) if labels[i] == cluster_id]

        crime_count = int(mask.sum())

        # Weighted severity score
        raw_score = sum(SEVERITY_WEIGHTS.get(s, 1) for s in cluster_sevs)
        score = min(100, int((raw_score / SCORE_MAX_RAW) * 100))

        # Risk classification
        if score >= 80:
            risk = 'Critical'
        elif score >= 50:
            risk = 'High'
        elif score >= 25:
            risk = 'Medium'
        else:
            risk = 'Low'

        # Centroid
        lat_center = float(np.mean(cluster_lats))
        lng_center = float(np.mean(cluster_lngs))

        # Radius (max distance from centroid + 100m buffer)
        distances = [_haversine_m(lat_center, lng_center, lat, lng)
                     for lat, lng in zip(cluster_lats, cluster_lngs)]
        radius = int(max(distances)) + 100

        # Most common area and crime type
        from collections import Counter
        primary_area = Counter(cluster_areas).most_common(1)[0][0]
        primary_crime = Counter(cluster_crimes).most_common(1)[0][0]
        zone = AREA_ZONES.get(primary_area, 'Unknown')

        # --- Real trend: compare current window vs preceding 30-day window for this area ---
        prev_count = _get_area_prev_count(primary_area)
        trend = _compute_trend(crime_count, prev_count)

        # --- Cluster Density Score: normalized 0-100 based on largest cluster this run ---
        density_score = min(100, int((crime_count / max(max_cluster_size, 1)) * 100))

        hs_id = f'HS-ML-{cluster_id + 1:03d}'

        hotspot = Hotspot(
            id=hs_id,
            name=f'{primary_area} Zone',
            lat=round(lat_center, 4),
            lng=round(lng_center, 4),
            radius=radius,
            risk=risk,
            score=score,
            crimes=crime_count,
            primary_type=primary_crime,
            trend=trend,
            emerged=now_str,
            zone=zone
        )
        db.session.add(hotspot)
        hotspot_records.append(hotspot.to_dict())
        total_risk_score += score

        # Fetch active patrols (not inactive) to assign to High/Critical alerts
        active_patrols = PatrolUnit.query.filter(PatrolUnit.status != 'Inactive').all()
        available_patrols = [p for p in active_patrols if p.status != 'Responding']

        # Step 4: Generate alerts for High/Critical
        if risk in ['High', 'Critical']:
            assigned_vehicle = None
            if available_patrols:
                closest_patrol = None
                min_dist = float('inf')
                for patrol in available_patrols:
                    try:
                        import ast
                        loc = ast.literal_eval(patrol.current_location) if isinstance(patrol.current_location, str) else patrol.current_location
                        p_lat, p_lng = loc['lat'], loc['lng']
                        dist = _haversine_m(lat_center, lng_center, p_lat, p_lng)
                        if dist < min_dist:
                            min_dist = dist
                            closest_patrol = patrol
                    except Exception as e:
                        pass
                
                if closest_patrol:
                    assigned_vehicle = closest_patrol.vehicle_id
                    closest_patrol.status = 'Responding'
                    available_patrols.remove(closest_patrol)

            alert_id = f'ALT-ML-{cluster_id + 1:03d}'
            alert = Alert(
                id=alert_id,
                type=risk.upper(),
                title=f'DBSCAN: {risk} Risk Hotspot Detected',
                message=f'ML Engine detected a {risk} risk cluster in {primary_area}. '
                        f'{crime_count} crimes within {radius}m radius. '
                        f'Primary offense: {primary_crime}. Score: {score}/100.',
                area=primary_area,
                timestamp=now_str,
                acknowledged=False,
                assigned_to=assigned_vehicle
            )
            db.session.add(alert)
            alert_records.append(alert.to_dict())

        # Step 4.5: Generate Patrol Predictions for the AI Intelligence Panel
        # Aggregate by area to avoid Primary Key violations
        if primary_area not in predictions_by_area:
            predictions_by_area[primary_area] = {
                'area': primary_area,
                'risk_level': risk,
                'score': score,
                'total_crimes': crime_count,
                'top_crime': primary_crime,
                'lat': round(lat_center, 4),
                'lng': round(lng_center, 4)
            }
        else:
            prev = predictions_by_area[primary_area]
            prev['total_crimes'] += crime_count
            if score > prev['score']:
                prev['score'] = score
                prev['risk_level'] = risk
                prev['top_crime'] = primary_crime
                prev['lat'] = round(lat_center, 4)
                prev['lng'] = round(lng_center, 4)

    # Insert final aggregated predictions
    for area, data in predictions_by_area.items():
        deployment_strategy = (
            f"Deploy {min(4, max(1, data['total_crimes'] // 3))} units + PCR van"
            if data['risk_level'] in ['High', 'Critical']
            else "Routine patrol + Community outreach"
        )
        # density_score: normalized cluster size vs largest cluster this run (0–100)
        area_density_score = min(100, int((data['total_crimes'] / max(max_cluster_size, 1)) * 100))
        prediction = Prediction(
            area=data['area'],
            risk_level=data['risk_level'],
            score=data['score'],
            predicted_crimes=int(data['total_crimes']),   # Actual clustered count — no multiplier
            top_crime=data['top_crime'],
            confidence=str(area_density_score),           # Renamed semantically to Density Score
            deployment=deployment_strategy,
            lat=data['lat'],
            lng=data['lng']
        )
        db.session.add(prediction)

    db.session.commit()

    # Step 5: Calculate city risk index
    n_hotspots = len(hotspot_records)
    city_risk_index = min(100, int((total_risk_score / 300) * 100)) if n_hotspots > 0 else 0

    noise_count = int((labels == -1).sum())

    return {
        'status': 'success',
        'algorithm': 'DBSCAN',
        'config': {
            'eps_meters': EPS_METERS,
            'min_samples': MIN_SAMPLES,
            'time_window': '2025-02-26 to 2025-03-28'
        },
        'summary': {
            'total_crimes_analyzed': len(crimes),
            'crimes_clustered': len(crimes) - noise_count,
            'noise_points': noise_count,
            'hotspots_generated': n_hotspots,
            'alerts_generated': len(alert_records),
            'city_risk_index': city_risk_index
        },
        'hotspots': hotspot_records,
        'alerts': alert_records
    }
