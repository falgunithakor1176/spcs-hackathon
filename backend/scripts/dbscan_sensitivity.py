import os
import sys
import pandas as pd
import numpy as np
import psycopg2
from sklearn.cluster import DBSCAN
import warnings
warnings.filterwarnings('ignore')

DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

EARTH_RADIUS_KM = 6371.0
SCORE_MAX_RAW = 50
severity_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}

def haversine_m(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * np.arcsin(np.sqrt(a)) * 6371000

# Load data once
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
    df_base = pd.read_sql(query, conn)
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
    sys.exit(1)

def run_config(df, eps_m, min_samp):
    coords = np.radians(df[['latitude', 'longitude']].values)
    eps_rad = (eps_m / 1000.0) / EARTH_RADIUS_KM
    
    dbscan = DBSCAN(eps=eps_rad, min_samples=min_samp, algorithm='ball_tree', metric='haversine')
    labels = dbscan.fit_predict(coords)
    df = df.copy()
    df['cluster'] = labels
    
    n_noise = (labels == -1).sum()
    n_clustered = (labels != -1).sum()
    df_cl = df[df['cluster'] != -1]
    
    hotspots = []
    alerts = []
    patrols = []
    total_risk = 0
    
    for cid, grp in df_cl.groupby('cluster'):
        crime_count = len(grp)
        raw_score = sum(grp['severity'].map(severity_weights).fillna(1))
        score = min(100, int((raw_score / SCORE_MAX_RAW) * 100))
        
        if score >= 80:   risk = 'Critical'
        elif score >= 50: risk = 'High'
        elif score >= 25: risk = 'Medium'
        else:             risk = 'Low'
        
        lat_c = round(grp['latitude'].mean(), 4)
        lng_c = round(grp['longitude'].mean(), 4)
        
        dists = grp.apply(lambda r: haversine_m(lat_c, lng_c, r['latitude'], r['longitude']), axis=1)
        radius = int(dists.max()) + 100
        
        primary_area = grp['area'].mode()[0]
        primary_crime = grp['crime_type'].mode()[0]
        
        hs = {
            'id': f'HS-{cid+1:03d}',
            'name': f'{primary_area} Zone',
            'lat': lat_c, 'lng': lng_c,
            'radius': radius,
            'risk': risk, 'score': score,
            'crimes': crime_count,
            'primary_type': primary_crime
        }
        hotspots.append(hs)
        total_risk += score
        
        if risk in ['High', 'Critical']:
            alerts.append({'hotspot': hs['name'], 'risk': risk, 'score': score})
        
        if risk == 'Critical':
            patrols.append({'target': hs['name'], 'action': 'Immediate Dispatch (2 Units)', 'priority': 'P1'})
        elif risk == 'High':
            patrols.append({'target': hs['name'], 'action': 'Enhanced Patrol (1 Unit)', 'priority': 'P2'})
        elif risk == 'Medium':
            patrols.append({'target': hs['name'], 'action': 'Routine Surveillance', 'priority': 'P3'})
    
    risk_index = min(100, int((total_risk / 300) * 100))
    
    return {
        'hotspots': hotspots,
        'alerts': alerts,
        'patrols': patrols,
        'risk_index': risk_index,
        'noise': n_noise,
        'clustered': n_clustered
    }

# ============================================================
# Run all 3 configurations
# ============================================================
configs = [
    {'eps': 250, 'min_samples': 5, 'label': 'Config A: eps=250m, min_samples=5 (APPROVED)'},
    {'eps': 250, 'min_samples': 4, 'label': 'Config B: eps=250m, min_samples=4 (RELAXED)'},
    {'eps': 300, 'min_samples': 5, 'label': 'Config C: eps=300m, min_samples=5 (WIDER)'},
]

print("="*80)
print(" DBSCAN SENSITIVITY ANALYSIS ON 30-DAY WINDOW")
print(f" Dataset: {len(df_base)} crimes (Feb 26 - Mar 28, 2025)")
print("="*80)

results = []

for cfg in configs:
    r = run_config(df_base, cfg['eps'], cfg['min_samples'])
    r['label'] = cfg['label']
    r['eps'] = cfg['eps']
    r['min_samples'] = cfg['min_samples']
    results.append(r)

# ============================================================
# Print detailed results for each config
# ============================================================
for r in results:
    print("\n" + "-"*80)
    print(f" {r['label']}")
    print("-"*80)
    print(f"  Clustered Crimes: {r['clustered']} | Noise: {r['noise']}")
    print(f"  Hotspots Found:   {len(r['hotspots'])}")
    print(f"  Alerts Generated: {len(r['alerts'])}")
    print(f"  Patrol Recs:      {len(r['patrols'])}")
    print(f"  Risk Index:       {r['risk_index']} / 100")
    
    if r['hotspots']:
        print(f"\n  {'ID':<10} {'Name':<20} {'Score':<8} {'Risk':<10} {'Crimes':<8} {'Radius':<8} {'Primary Type'}")
        print(f"  {'---':<10} {'---':<20} {'---':<8} {'---':<10} {'---':<8} {'---':<8} {'---'}")
        for hs in r['hotspots']:
            print(f"  {hs['id']:<10} {hs['name']:<20} {hs['score']:<8} {hs['risk']:<10} {hs['crimes']:<8} {hs['radius']:<8} {hs['primary_type']}")
    
    if r['alerts']:
        print(f"\n  Alerts:")
        for al in r['alerts']:
            print(f"    -> {al['risk']} alert for {al['hotspot']} (score: {al['score']})")
    
    if r['patrols']:
        print(f"\n  Patrol Deployments:")
        for p in r['patrols']:
            print(f"    -> {p['priority']}: {p['action']} -> {p['target']}")

# ============================================================
# Side-by-side comparison table
# ============================================================
print("\n" + "="*80)
print(" SIDE-BY-SIDE COMPARISON")
print("="*80)
print(f"\n  {'Metric':<30} {'Config A':<15} {'Config B':<15} {'Config C':<15}")
print(f"  {'(eps/min_samples)':<30} {'250m / 5':<15} {'250m / 4':<15} {'300m / 5':<15}")
print(f"  {'-'*30} {'-'*15} {'-'*15} {'-'*15}")

metrics = [
    ('Hotspots Found', lambda r: len(r['hotspots'])),
    ('Crimes Clustered', lambda r: r['clustered']),
    ('Noise Points', lambda r: r['noise']),
    ('Cluster Ratio', lambda r: f"{r['clustered']/len(df_base)*100:.1f}%"),
    ('Alerts Generated', lambda r: len(r['alerts'])),
    ('Patrol Deployments', lambda r: len(r['patrols'])),
    ('Risk Index', lambda r: f"{r['risk_index']}/100"),
    ('Avg Score/Hotspot', lambda r: f"{sum(h['score'] for h in r['hotspots'])/max(1,len(r['hotspots'])):.0f}" if r['hotspots'] else "N/A"),
    ('Max Hotspot Score', lambda r: max((h['score'] for h in r['hotspots']), default=0)),
    ('Critical Hotspots', lambda r: sum(1 for h in r['hotspots'] if h['risk'] == 'Critical')),
    ('High Hotspots', lambda r: sum(1 for h in r['hotspots'] if h['risk'] == 'High')),
    ('Medium Hotspots', lambda r: sum(1 for h in r['hotspots'] if h['risk'] == 'Medium')),
    ('Low Hotspots', lambda r: sum(1 for h in r['hotspots'] if h['risk'] == 'Low')),
]

for name, fn in metrics:
    vals = [str(fn(r)) for r in results]
    print(f"  {name:<30} {vals[0]:<15} {vals[1]:<15} {vals[2]:<15}")

print("\n" + "="*80)
print(" ANALYSIS COMPLETE")
print("="*80)
