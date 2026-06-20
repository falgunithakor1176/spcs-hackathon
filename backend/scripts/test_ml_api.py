"""Test the ML Engine API endpoint end-to-end."""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

# Step 1: Login to get JWT token
print("="*60)
print(" PHASE 4 INTEGRATION TEST: DBSCAN ML ENGINE")
print("="*60)

print("\n[1] Authenticating...")
login_resp = requests.post(f'{BASE_URL}/auth/login', json={
    'username': 'commissioner',
    'password': 'admin123'
})
token = login_resp.json().get('access_token')
if not token:
    print("  FAILED: Could not authenticate.")
    exit(1)
print("  OK: JWT token received.")

headers = {'Authorization': f'Bearer {token}'}

# Step 2: Check ML status
print("\n[2] Checking ML Engine Status...")
status_resp = requests.get(f'{BASE_URL}/ml/status', headers=headers)
print(f"  Status: {status_resp.json().get('status')}")
print(f"  Engine: {status_resp.json().get('engine')}")

# Step 3: Count hotspots BEFORE ML run
print("\n[3] Current hotspots in database (BEFORE ML run)...")
hotspots_before = requests.get(f'{BASE_URL}/hotspots', headers=headers)
print(f"  Hotspots count: {len(hotspots_before.json())}")

# Step 4: Trigger the ML Engine
print("\n[4] Triggering DBSCAN ML Engine (POST /api/ml/run)...")
ml_resp = requests.post(f'{BASE_URL}/ml/run', headers=headers)
result = ml_resp.json()

if result.get('status') == 'success':
    summary = result['summary']
    print(f"  Status: SUCCESS")
    print(f"  Crimes Analyzed: {summary['total_crimes_analyzed']}")
    print(f"  Crimes Clustered: {summary['crimes_clustered']}")
    print(f"  Noise Points: {summary['noise_points']}")
    print(f"  Hotspots Generated: {summary['hotspots_generated']}")
    print(f"  Alerts Generated: {summary['alerts_generated']}")
    print(f"  City Risk Index: {summary['city_risk_index']} / 100")
    
    print(f"\n  Hotspot Details:")
    for hs in result['hotspots']:
        print(f"    {hs['id']:<12} {hs['name']:<20} Score={hs['score']:<4} Risk={hs['risk']:<10} Crimes={hs['crimes']}")
    
    if result['alerts']:
        print(f"\n  Alert Details:")
        for al in result['alerts']:
            print(f"    {al['id']:<12} {al['type']:<10} {al['area']}")
    else:
        print(f"\n  No alerts generated (all hotspots below High threshold).")
else:
    print(f"  FAILED: {result.get('message')}")

# Step 5: Verify hotspots were written to database
print("\n[5] Verifying hotspots in database (AFTER ML run)...")
hotspots_after = requests.get(f'{BASE_URL}/hotspots', headers=headers)
print(f"  Hotspots count: {len(hotspots_after.json())}")
for hs in hotspots_after.json():
    print(f"    {hs['id']:<12} {hs['name']:<20} Score={hs['score']:<4} Zone={hs.get('zone', 'N/A')}")

# Step 6: Run ML Engine AGAIN to prove no duplicates
print("\n[6] Running ML Engine a SECOND time (duplicate test)...")
ml_resp2 = requests.post(f'{BASE_URL}/ml/run', headers=headers)
hotspots_after2 = requests.get(f'{BASE_URL}/hotspots', headers=headers)
print(f"  Hotspots after 2nd run: {len(hotspots_after2.json())}")
if len(hotspots_after2.json()) == len(hotspots_after.json()):
    print("  PASS: No duplicates created. TRUNCATE+INSERT working correctly.")
else:
    print("  FAIL: Duplicate hotspots detected!")

print("\n" + "="*60)
print(" ALL TESTS COMPLETE")
print("="*60)
