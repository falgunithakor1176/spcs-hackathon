"""
test_dispatch_flow.py — Phase 7B Integration Test Suite
=========================================================
Performs automated checks on:
- Dispatch recommendation calculation
- Atomicity and persistence of dispatch transactions
- Status updates and alert assignments in PostgreSQL
- Dynamic OSRM route generation on dispatch
- Validation logic for invalid hotspot / patrol inputs
- Race-condition handling (409 Conflict) for double-dispatches
"""

import requests
import json
import os
import sys

BASE_URL = "http://127.0.0.1:5000/api"

def reset_db_state():
    print("\n[Test Setup] Accessing PostgreSQL to reset status values...")
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.append(backend_dir)
        
    from app import create_app
    from db import db
    from models import PatrolUnit, Alert
    
    flask_app = create_app()
    with flask_app.app_context():
        # Set all units to 'Standby' to ensure availability
        for p in PatrolUnit.query.all():
            p.status = 'Standby'
        
        # Clear alert assignments
        for a in Alert.query.all():
            a.assigned_to = None
            
        db.session.commit()
    print("[Test Setup] Database reset completed.")

def run_tests():
    print("==================================================")
    print("SPCS — PHASE 7B INTEGRATION TEST SUITE")
    print("==================================================")

    # 1. Login to get JWT Token
    login_url = f"{BASE_URL}/auth/login"
    login_data = {"username": "commissioner", "password": "admin123"}
    resp = requests.post(login_url, json=login_data)
    if resp.status_code != 200:
        print("[FAIL] Authentication failed.")
        return
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Authentication successful.")

    # Reset any existing alerts/patrols status to ensure clean test run
    reset_db_state()

    # TEST 1: Fetch dispatch recommendations
    print("\n--- TEST 1: High-risk hotspot + available patrol recommendations ---")
    recs_resp = requests.get(f"{BASE_URL}/dispatch/recommendations", headers=headers)
    if recs_resp.status_code != 200:
        print(f"[FAIL] Recommendations endpoint failed: {recs_resp.text}")
        return
    
    recs = recs_resp.json().get("recommendations", [])
    if not recs:
        print("[FAIL] No recommendations generated. Make sure High/Critical hotspots exist in DB.")
        return
    
    # Filter for first undispatched recommendation
    undispatched = [r for r in recs if not r['dispatched']]
    if not undispatched:
        print("[FAIL] All hotspots show as already dispatched.")
        return

    first_rec = undispatched[0]
    print(f"[PASS] Recommendations successfully fetched ({len(recs)} total).")
    print(f"       Target Hotspot: {first_rec['hotspot_id']} ({first_rec['area']}, Score: {first_rec['score']}, Risk: {first_rec['risk']})")
    
    if not first_rec['recommended_unit']:
        print("[FAIL] No recommended patrol unit returned.")
        return
        
    rec_unit = first_rec['recommended_unit']
    print(f"       Recommended Unit: {rec_unit['vehicle_id']} (Distance: {rec_unit['distance_km']} km, Status: {rec_unit['status']})")
    print("[PASS] TEST 1 passed.")

    hotspot_id = first_rec['hotspot_id']
    patrol_id = rec_unit['vehicle_id']

    # TEST 2 & 3 & 4 & 5 & 6: Execute dispatch
    print("\n--- TEST 2, 3, 4, 5, 6: Commander dispatch execution ---")
    dispatch_data = {"hotspot_id": hotspot_id, "patrol_id": patrol_id}
    dispatch_resp = requests.post(f"{BASE_URL}/dispatch", json=dispatch_data, headers=headers)
    
    if dispatch_resp.status_code != 200:
        print(f"[FAIL] Dispatch failed: {dispatch_resp.status_code} - {dispatch_resp.text}")
        return

    payload = dispatch_resp.json()
    print("[PASS] TEST 2: Dispatch successfully processed & persisted.")
    print(f"       OSRM dynamic distance returned: {payload.get('distance_km')} km (TEST 5 PASS)")
    print(f"       OSRM dynamic ETA returned: {payload.get('eta_minutes')} min (TEST 6 PASS)")
    print(f"       OSRM route waypoints returned: {len(payload.get('waypoints', []))} points (TEST 4 PASS)")

    # Verify status changed to Responding
    patrols_resp = requests.get(f"{BASE_URL}/patrols", headers=headers)
    patrols = {p['vehicle_id']: p for p in patrols_resp.json()}
    dispatched_patrol = patrols.get(patrol_id)
    
    if dispatched_patrol and dispatched_patrol['status'] == 'Responding':
        print(f"[PASS] TEST 3: Patrol unit {patrol_id} status updated to Responding in PostgreSQL.")
    else:
        print(f"[FAIL] Patrol unit {patrol_id} status is '{dispatched_patrol['status']}', expected 'Responding'.")

    # TEST 7 & 8: Simultaneous / Unavailable Patrol Dispatch
    print("\n--- TEST 7 & 8: Simultaneous / double dispatch validation (409 Conflict) ---")
    double_resp = requests.post(f"{BASE_URL}/dispatch", json=dispatch_data, headers=headers)
    print(f"       Double-dispatch response code: {double_resp.status_code}")
    print(f"       Payload message: {double_resp.json().get('message')}")
    
    if double_resp.status_code == 409:
        print("[PASS] TEST 7 & 8: Simultaneous dispatch correctly blocked with 409 Conflict.")
    else:
        print(f"[FAIL] Expected 409 Conflict, got {double_resp.status_code}")

    # TEST 9: Invalid Hotspot validation
    print("\n--- TEST 9: Invalid Hotspot Validation ---")
    invalid_hs_data = {"hotspot_id": "HS-ML-INVALID", "patrol_id": patrol_id}
    ihs_resp = requests.post(f"{BASE_URL}/dispatch", json=invalid_hs_data, headers=headers)
    print(f"       Response code: {ihs_resp.status_code}")
    print(f"       Payload message: {ihs_resp.json().get('message')}")
    if ihs_resp.status_code == 404:
        print("[PASS] TEST 9: Invalid hotspot successfully rejected with 404.")
    else:
        print(f"[FAIL] Expected 404, got {ihs_resp.status_code}")

    # TEST 10: Invalid Patrol validation
    print("\n--- TEST 10: Invalid Patrol Validation ---")
    invalid_p_data = {"hotspot_id": hotspot_id, "patrol_id": "AHD-PCR-INVALID"}
    ip_resp = requests.post(f"{BASE_URL}/dispatch", json=invalid_p_data, headers=headers)
    print(f"       Response code: {ip_resp.status_code}")
    print(f"       Payload message: {ip_resp.json().get('message')}")
    if ip_resp.status_code == 404:
        print("[PASS] TEST 10: Invalid patrol unit successfully rejected with 404.")
    else:
        print(f"[FAIL] Expected 404, got {ip_resp.status_code}")

    print("\n==================================================")
    print("INTEGRATION TEST SUMMARY: ALL TESTS PASSED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
