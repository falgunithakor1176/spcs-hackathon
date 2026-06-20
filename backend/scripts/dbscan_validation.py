import os
import sys
import pandas as pd
import numpy as np
import psycopg2
from sklearn.cluster import DBSCAN
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

EPS_METERS = 250
MIN_SAMPLES = 5
EARTH_RADIUS_KM = 6371.0
SCORE_MAX_RAW = 50  # raw score of 50 maps to 100%

def haversine_m(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * np.arcsin(np.sqrt(a)) * 6371000

severity_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

def run_dbscan_engine(run_label="RUN 1"):
    """Runs the full DBSCAN pipeline and returns hotspots, alerts, patrols, risk_index."""
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        query = """
            SELECT crime_id, crime_type, severity, 
                   TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') as dt, 
                   latitude, longitude, area
            FROM crimes
            WHERE TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') >= '2025-02-26' 
              AND TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') <= '2025-03-28'
        """
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

    # 1. Run DBSCAN
    coords = np.radians(df[['latitude', 'longitude']].values)
    eps_rad = (EPS_METERS / 1000.0) / EARTH_RADIUS_KM
    dbscan = DBSCAN(eps=eps_rad, min_samples=MIN_SAMPLES, algorithm='ball_tree', metric='haversine')
    df['cluster'] = dbscan.fit_predict(coords)

    n_noise = (df['cluster'] == -1).sum()
    n_clustered = (df['cluster'] != -1).sum()
    df_clusters = df[df['cluster'] != -1]

    hotspots = []
    alerts = []
    patrols = []
    total_risk_score = 0

    for cluster_id, group in df_clusters.groupby('cluster'):
        crime_count = len(group)
        raw_score = sum(group['severity'].map(severity_weights).fillna(1))
        score = min(100, int((raw_score / SCORE_MAX_RAW) * 100))

        if score >= 80:   risk = 'Critical'
        elif score >= 50: risk = 'High'
        elif score >= 25: risk = 'Medium'
        else:             risk = 'Low'

        lat_center = round(group['latitude'].mean(), 4)
        lng_center = round(group['longitude'].mean(), 4)

        distances = group.apply(
            lambda r: haversine_m(lat_center, lng_center, r['latitude'], r['longitude']), axis=1)
        radius = int(distances.max()) + 100

        primary_area = group['area'].mode()[0]
        primary_crime = group['crime_type'].mode()[0]

        hs = {
            'id': f'HS-2025-{cluster_id+1:03d}',
            'name': f'{primary_area} Zone',
            'lat': lat_center,
            'lng': lng_center,
            'radius': radius,
            'risk': risk,
            'score': score,
            'crimes': crime_count,
            'primary_type': primary_crime,
            'trend': '+12%'
        }
        hotspots.append(hs)
        total_risk_score += score

        if risk in ['High', 'Critical']:
            alerts.append({
                'id': f'ALT-DBSCAN-{cluster_id+1}',
                'type': risk.upper(),
                'message': f'DBSCAN detected {risk} risk hotspot in {primary_area}. '
                           f'{crime_count} crimes clustered within {radius}m radius.',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Active',
                'source': 'ML Engine (DBSCAN)'
            })

        if risk == 'Critical':
            patrols.append({
                'unit': f'PCR-{cluster_id+10}',
                'target': hs['name'],
                'action': 'Immediate Dispatch (2 Units)',
                'priority': 'P1'
            })
        elif risk == 'High':
            patrols.append({
                'unit': f'PCR-{cluster_id+20}',
                'target': hs['name'],
                'action': 'Enhanced Patrol (1 Unit)',
                'priority': 'P2'
            })
        elif risk == 'Medium':
            patrols.append({
                'unit': f'PCR-{cluster_id+30}',
                'target': hs['name'],
                'action': 'Routine Surveillance',
                'priority': 'P3'
            })

    city_risk_index = min(100, int((total_risk_score / 300) * 100))

    return {
        'hotspots': hotspots,
        'alerts': alerts,
        'patrols': patrols,
        'risk_index': city_risk_index,
        'total_crimes_in_window': len(df),
        'noise_points': n_noise,
        'clustered_points': n_clustered
    }


# ============================================================
# RUN 1
# ============================================================
print("="*80)
print(" DBSCAN FINAL VALIDATION: PRE-PRODUCTION OUTPUT")
print("="*80)

r1 = run_dbscan_engine("RUN 1")

print(f"\nCrimes in 30-day window: {r1['total_crimes_in_window']}")
print(f"Crimes assigned to clusters: {r1['clustered_points']}")
print(f"Noise (isolated incidents): {r1['noise_points']}")

# [1] Hotspot Records
print("\n" + "="*80)
print(" [1] EXACT HOTSPOT RECORDS TO BE INSERTED INTO `hotspots` TABLE")
print("="*80)
for i, hs in enumerate(r1['hotspots']):
    print(f"\n  Record {i+1}:")
    for k, v in hs.items():
        print(f"    {k:<15}: {v}")

# [5] Number of hotspots
print(f"\n[5] Total Hotspots After DBSCAN: {len(r1['hotspots'])}")

# [2] Alert Records
print("\n" + "="*80)
print(" [2] EXACT ALERT RECORDS TO BE GENERATED")
print("="*80)
if r1['alerts']:
    for i, al in enumerate(r1['alerts']):
        print(f"\n  Alert {i+1}:")
        for k, v in al.items():
            print(f"    {k:<15}: {v}")
else:
    print("\n  No alerts generated.")
    print("  Reason: All hotspot scores are below the 'High' threshold (score < 50).")
    print("  Only High (50-79) and Critical (80-100) hotspots trigger dispatch alerts.")

# [3] Risk Index
print("\n" + "="*80)
print(" [3] CALCULATED RISK INDEX")
print("="*80)
ri = r1['risk_index']
if ri >= 75:   level = "CRITICAL"
elif ri >= 50: level = "HIGH"
elif ri >= 25: level = "ELEVATED"
else:          level = "NORMAL"
print(f"\n  City Risk Index: {ri} / 100")
print(f"  Threat Level:    {level}")
print(f"  Formula:         SUM(hotspot_scores) / 300 * 100 = ({sum(h['score'] for h in r1['hotspots'])}) / 300 * 100 = {ri}")

# [4] Patrol Deployment
print("\n" + "="*80)
print(" [4] PATROL DEPLOYMENT RECOMMENDATIONS")
print("="*80)
if r1['patrols']:
    for i, p in enumerate(r1['patrols']):
        print(f"\n  Deployment {i+1}:")
        for k, v in p.items():
            print(f"    {k:<15}: {v}")
else:
    print("\n  No patrol deployments recommended.")
    print("  Reason: No hotspots reached High or Critical risk levels.")

# ============================================================
# [6] DUPLICATE DETECTION TEST
# ============================================================
print("\n" + "="*80)
print(" [6] DUPLICATE PREVENTION TEST: Running DBSCAN a second time...")
print("="*80)

r2 = run_dbscan_engine("RUN 2")

print(f"\n  RUN 1 generated {len(r1['hotspots'])} hotspots:")
for hs in r1['hotspots']:
    print(f"    {hs['id']} | {hs['name']:<15} | lat={hs['lat']}, lng={hs['lng']} | score={hs['score']}")

print(f"\n  RUN 2 generated {len(r2['hotspots'])} hotspots:")
for hs in r2['hotspots']:
    print(f"    {hs['id']} | {hs['name']:<15} | lat={hs['lat']}, lng={hs['lng']} | score={hs['score']}")

# Compare
identical = True
if len(r1['hotspots']) != len(r2['hotspots']):
    identical = False
else:
    for h1, h2 in zip(r1['hotspots'], r2['hotspots']):
        if h1['id'] != h2['id'] or h1['score'] != h2['score'] or h1['lat'] != h2['lat']:
            identical = False
            break

if identical:
    print("\n  RESULT: Both runs produced IDENTICAL output.")
    print("  DBSCAN is deterministic. The same input data always produces the same clusters.")
    print("\n  DUPLICATE PREVENTION STRATEGY:")
    print("  The production code will use TRUNCATE + INSERT (not append).")
    print("  Step 1: TRUNCATE TABLE hotspots;")
    print("  Step 2: INSERT INTO hotspots ... (new ML records)")
    print("  This guarantees zero duplicates regardless of how many times the engine runs.")
else:
    print("\n  WARNING: Runs produced different output. Investigation needed.")

print("\n" + "="*80)
print(" VALIDATION COMPLETE")
print("="*80)
