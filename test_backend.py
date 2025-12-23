import requests
import json
import os
import sys
import time

# Base URL
BASE_URL = 'http://127.0.0.1:5000/api'

def test_backend_flow():
    print("=== Testing Backend Flow ===")
    
    # 1. Register User (Guardian)
    print("\n[1] Registering User...")
    user_payload = {
        'name': 'John Doe',
        'email': f'john_{int(time.time())}@example.com',
        'password': 'password123',
        'role': 'GUARDIAN'
    }
    res = requests.post(f"{BASE_URL}/auth/register", json=user_payload)
    print(f"Status: {res.status_code}, Resp: {res.json()}")
    if res.status_code != 201: return

    # 2. Login
    print("\n[2] Logging in...")
    login_payload = {'email': user_payload['email'], 'password': 'password123'}
    res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    data = res.json()
    token = data.get('access_token')
    print(f"Login Success. Token: {token[:10]}...")
    
    headers = {'Authorization': f"Bearer {token}"}

    # 3. Register Device
    print("\n[3] Registering Device...")
    device_payload = {'email': user_payload['email']}
    res = requests.post(f"{BASE_URL}/device/register", json=device_payload, headers=headers)
    print(f"Status: {res.status_code}, Resp: {res.json()}")
    device_uid = res.json().get('device_uid')
    
    # 4. Send Heartbeat (Event without audio)
    print("\n[4] Sending Heartbeat Event...")
    event_payload = {
        'device_uid': device_uid,
        'heart_rate': 75,
        'lat': 12.9716,
        'lng': 77.5946
    }
    res = requests.post(f"{BASE_URL}/device/event", data=event_payload)
    print(f"Status: {res.status_code}, Resp: {res.json()}")

    # 5. Send Stress Event (with dummy audio)
    print("\n[5] Sending Stress Event (Audio)...")
    # Generate a dummy wav file if not exists
    dummy_wav = 'test_audio.wav'
    if not os.path.exists(dummy_wav):
        import numpy as np
        import soundfile as sf
        sr = 16000
        # High freq for "stress" simulation (880Hz)
        t = np.linspace(0, 3, sr*3)
        y = 0.5 * np.sin(2 * np.pi * 880 * t)
        sf.write(dummy_wav, y, sr)
    
    files = {'audio': open(dummy_wav, 'rb')}
    res = requests.post(f"{BASE_URL}/device/event", data=event_payload, files=files)
    print(f"Status: {res.status_code}, Resp: {res.json()}")
    
    # 6. List Alerts
    print("\n[6] Listing Alerts...")
    res = requests.get(f"{BASE_URL}/alerts/", headers=headers)
    print(f"Status: {res.status_code}, Resp: {res.json()}")

if __name__ == "__main__":
    # Ensure server is running!
    try:
        test_backend_flow()
    except Exception as e:
        print(f"Test failed. Is the server running? Error: {e}")
