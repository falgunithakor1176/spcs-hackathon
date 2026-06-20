import requests
import json

base_url = 'http://127.0.0.1:5000/api'

# Login
res = requests.post(f"{base_url}/auth/login", json={"username": "commissioner", "password": "password123"})
if res.status_code != 200:
    res = requests.post(f"{base_url}/auth/login", json={"username": "commissioner", "password": "admin123"})

token = res.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# Run ML Engine
res = requests.post(f"{base_url}/ml/run", headers=headers)
print("ML Engine Run Status:", res.status_code)
if res.status_code != 200:
    print(res.text)

# Fetch Predictions
res = requests.get(f"{base_url}/predictions", headers=headers)
predictions = res.json()

print(f"Total Prediction Rows: {len(predictions)}")
print(json.dumps(predictions, indent=2))
