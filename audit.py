import sys
import json
import requests
import sqlite3
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup
BASE_URL = "http://127.0.0.1:5000/api"
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "instance", "spcs.db")

# 1. Login and get token
print("--- AUDIT START ---")
login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "commissioner", "password": "admin123"})
if login_res.status_code != 200:
    print("FAILED TO LOGIN:", login_res.text)
    sys.exit(1)
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Run POST /api/ml/run
print("\n--- 1. POST /api/ml/run RESPONSE ---")
ml_res = requests.post(f"{BASE_URL}/ml/run", headers=headers)
print(f"HTTP Status Code: {ml_res.status_code}")
try:
    print("Full JSON Response:")
    print(json.dumps(ml_res.json(), indent=2))
except Exception as e:
    print("Response Text:", ml_res.text)

# 3. Database Check
print("\n--- 2. DATABASE ROW COUNTS ---")
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM hotspots;")
    hs_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictions;")
    pred_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM alerts;")
    alerts_count = cursor.fetchone()[0]
    
    print(f"hotspots count: {hs_count}")
    print(f"predictions count: {pred_count}")
    print(f"alerts count: {alerts_count}")

    print("\n--- 3. ACTUAL RECORDS IN HOTSPOTS ---")
    cursor.execute("SELECT * FROM hotspots;")
    hotspots = cursor.fetchall()
    for h in hotspots:
        print(h)

    print("\n--- 4. ACTUAL RECORDS IN PREDICTIONS ---")
    cursor.execute("SELECT * FROM predictions;")
    predictions = cursor.fetchall()
    for p in predictions:
        print(p)

    conn.close()
    
except Exception as e:
    print("Database Error:", str(e))
