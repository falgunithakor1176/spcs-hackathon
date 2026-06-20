import os
import sys
import pandas as pd
import numpy as np
import psycopg2
from sklearn.cluster import DBSCAN

# Configuration
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

EPS_METERS = 250
MIN_SAMPLES = 5
EARTH_RADIUS_KM = 6371.0

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    # The densest 30-day window found in our previous analysis
    query = """
        SELECT crime_id as id, crime_type, severity, TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') as dt, latitude, longitude, area
        FROM crimes
        WHERE TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') >= '2025-02-26' 
          AND TO_TIMESTAMP(timestamp, 'DD-MM-YYYY HH24:MI') <= '2025-03-28'
    """
    df = pd.read_sql(query, conn)
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
    sys.exit(1)

print("="*80)
print(" DBSCAN ML ENGINE: DRY RUN & TABLE GENERATION")
print("="*80)

if df.empty:
    print("No data found in window.")
    sys.exit(0)

# 1. Run DBSCAN
coords = np.radians(df[['latitude', 'longitude']].values)
eps_rad = (EPS_METERS / 1000.0) / EARTH_RADIUS_KM

dbscan = DBSCAN(eps=eps_rad, min_samples=MIN_SAMPLES, algorithm='ball_tree', metric='haversine')
df['cluster'] = dbscan.fit_predict(coords)

# Remove noise
df_hotspots = df[df['cluster'] != -1]

# 2 & 3. Generate Hotspots & Calculate Scores
hotspots = []
alerts = []
patrols = []
total_risk_score = 0

severity_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

for cluster_id, group in df_hotspots.groupby('cluster'):
    crime_count = len(group)
    
    # Calculate weighted score
    raw_score = sum(group['severity'].map(severity_weights).fillna(1))
    
    # Normalize score (0-100). Assume a raw score of 50 is 100% for this window
    score = min(100, int((raw_score / 50.0) * 100))
    
    # Assign Risk Level
    if score >= 80: risk = 'Critical'
    elif score >= 50: risk = 'High'
    elif score >= 25: risk = 'Medium'
    else: risk = 'Low'
    
    # Calculate Centroid and Radius
    lat_center = group['latitude'].mean()
    lng_center = group['longitude'].mean()
    
    # Calculate max distance from center in meters using Haversine
    def haversine_m(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        return 2 * np.arcsin(np.sqrt(a)) * 6371000
    
    distances = group.apply(lambda r: haversine_m(lat_center, lng_center, r['latitude'], r['longitude']), axis=1)
    radius = int(distances.max()) + 100 # Add 100m buffer
    
    # Get most common area name and crime type
    primary_area = group['area'].mode()[0]
    primary_crime = group['crime_type'].mode()[0]
    
    hs_record = {
        'id': f'HS-2025-{cluster_id+1:03d}',
        'name': f"{primary_area} Zone",
        'lat': round(lat_center, 4),
        'lng': round(lng_center, 4),
        'radius': radius,
        'risk': risk,
        'score': score,
        'crimes': crime_count,
        'primary_type': primary_crime,
        'trend': '+12%' # Mock trend
    }
    hotspots.append(hs_record)
    total_risk_score += score
    
    # 4. Generate Alerts
    if risk in ['High', 'Critical']:
        alerts.append({
            'id': f'ALT-HS-{cluster_id+1}',
            'type': risk.upper(),
            'message': f"DBSCAN detected {risk} risk hotspot in {primary_area}. {crime_count} crimes clustered.",
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Active'
        })
    
    # 6. Patrol Deployment
    if risk == 'Critical':
        patrols.append({'unit': f'Unit-{cluster_id+10}', 'target_hotspot': hs_record['name'], 'action': 'Immediate Dispatch (2 Units)'})
    elif risk == 'High':
        patrols.append({'unit': f'Unit-{cluster_id+20}', 'target_hotspot': hs_record['name'], 'action': 'Routine Patrol (1 Unit)'})

# 5. Calculate Global Risk Index
city_risk_index = min(100, int((total_risk_score / 300) * 100)) # Base max 300

# ---------------------------------------------------------
# PRINT RESULTS (To be integrated into Flask APIs)
# ---------------------------------------------------------
print(f"\n[1] DBSCAN Complete. Found {len(hotspots)} distinct hotspots.\n")

print("-" * 80)
print(" TABLE 1: hotspots (To be INSERTED via Flask /api/ml/run)")
print("-" * 80)
hotspots_df = pd.DataFrame(hotspots)
print(hotspots_df.to_string(index=False))

print("\n" + "-" * 80)
print(" TABLE 2: alerts (Auto-generated from DBSCAN engine)")
print("-" * 80)
alerts_df = pd.DataFrame(alerts)
if not alerts_df.empty:
    print(alerts_df[['id', 'type', 'message']].to_string(index=False))
else:
    print("No alerts generated.")

print("\n" + "-" * 80)
print(" TABLE 3: patrol_deployments (Recommendations)")
print("-" * 80)
patrols_df = pd.DataFrame(patrols)
if not patrols_df.empty:
    print(patrols_df.to_string(index=False))
else:
    print("No patrols recommended.")

print("\n" + "-" * 80)
print(" METRIC: City Risk Index")
print("-" * 80)
print(f"  Current Index: {city_risk_index} / 100")
if city_risk_index >= 75: print("  Status: CRITICAL THREAT LEVEL")
elif city_risk_index >= 50: print("  Status: HIGH THREAT LEVEL")
else: print("  Status: NORMAL")

print("\n" + "="*80)
