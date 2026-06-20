import requests
import sys

BASE_URL = 'http://localhost:5000/api'
USERNAME = 'commissioner'
PASSWORD = 'admin123'

print("="*50)
print("  SPCS BACKEND API FULL TEST SUITE")
print("="*50)

# 1. Test Login
print("\n[1] Testing Authentication...")
try:
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": USERNAME, "password": PASSWORD})
    if login_res.status_code == 200:
        token = login_res.json().get('access_token')
        print("  âœ… Login successful! Received JWT token.")
    else:
        print(f"  âŒ Login failed. Status: {login_res.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"  âŒ Connection error: {e}")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 2. Test Endpoints
endpoints = [
    ("/crimes", 10000),
    ("/cybercrime", 1200),
    ("/patrols", 24),
    ("/patrol-routes", 3),
    ("/hotspots", 15),
    ("/alerts", 50),
    ("/predictions", 7),
]

print("\n[2] Testing Secured Data Endpoints...")
all_passed = True
for endpoint, expected_count in endpoints:
    url = f"{BASE_URL}{endpoint}"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            actual_count = len(data)
            if actual_count == expected_count:
                print(f"  âœ… GET {endpoint:<15} - Passed ({actual_count} records)")
            else:
                print(f"  âš ï¸ GET {endpoint:<15} - Warning: Expected {expected_count}, got {actual_count}")
                all_passed = False
        else:
            print(f"  âŒ GET {endpoint:<15} - Failed (Status: {res.status_code})")
            all_passed = False
    except Exception as e:
        print(f"  âŒ GET {endpoint:<15} - Error: {e}")
        all_passed = False

# 3. Test Stats Endpoint
print("\n[3] Testing /stats Endpoint...")
try:
    res = requests.get(f"{BASE_URL}/stats", headers=headers)
    if res.status_code == 200:
        data = res.json()
        print(f"  âœ… GET /stats          - Passed")
        print(f"     Total Crimes: {data.get('total_crimes')}")
        print(f"     Cyber Total:  {data.get('cyber_total')}")
    else:
        print(f"  âŒ GET /stats          - Failed (Status: {res.status_code})")
        all_passed = False
except Exception as e:
    print(f"  âŒ GET /stats          - Error: {e}")
    all_passed = False

print("\n" + "="*50)
if all_passed:
    print("  ðŸŽ‰ ALL TESTS PASSED! BACKEND IS 100% OPERATIONAL.")
else:
    print("  âš ï¸ SOME TESTS FAILED. CHECK LOGS ABOVE.")
print("="*50 + "\n")
