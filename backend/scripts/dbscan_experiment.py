import os
import sys
import time
import pandas as pd
import numpy as np
import psycopg2
from sklearn.cluster import DBSCAN

# Connect to DB
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'falguni')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'spcs_db')

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    query = "SELECT latitude, longitude FROM crimes"
    df = pd.read_sql(query, conn)
    conn.close()
except Exception as e:
    print(f"Database error: {e}")
    sys.exit(1)

print("="*60)
print(" DBSCAN FEASIBILITY STUDY: HYPERPARAMETER TUNING")
print("="*60)
print(f"Total Crimes Loaded: {len(df)}")

# Convert lat/lng to radians for Haversine distance
coords = np.radians(df[['latitude', 'longitude']].values)
EARTH_RADIUS_KM = 6371.0

# 3. Compare eps values
eps_test_cases_m = [250, 500, 750, 1000]
min_samples = 5

results = []

print(f"\nRunning DBSCAN with min_samples = {min_samples}...")
print("-" * 60)
print(f"{'eps (m)':<10} | {'Clusters':<10} | {'Noise Points':<15} | {'Noise %':<10} | {'Time (s)':<10}")
print("-" * 60)

for eps_m in eps_test_cases_m:
    # Convert meters to km, then to radians
    eps_rad = (eps_m / 1000.0) / EARTH_RADIUS_KM
    
    start_time = time.time()
    dbscan = DBSCAN(eps=eps_rad, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
    labels = dbscan.fit_predict(coords)
    runtime = time.time() - start_time
    
    # 1. Estimate Hotspots (clusters)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    
    # 2. Estimate Noise
    n_noise = list(labels).count(-1)
    noise_pct = (n_noise / len(df)) * 100
    
    print(f"{eps_m:<10} | {n_clusters:<10} | {n_noise:<15} | {noise_pct:>5.1f}%     | {runtime:.4f}")
    
    results.append({
        'eps_m': eps_m,
        'clusters': n_clusters,
        'noise': n_noise,
        'noise_pct': noise_pct,
        'time': runtime
    })

print("-" * 60)
print("\nExperiment Complete.")
