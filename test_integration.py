import requests
import os
import random

BASE_URL = "http://127.0.0.1:5000/api"

def test_full_integration():
    print("--- Shield System Integration Test ---")
    
    # 1. Register Device (SHIELD-TEST)
    print("1. Registering Device...")
    reg_res = requests.post(f"{BASE_URL}/device/register", json={
        "email": "admin@safety.com", # Matches run.py seed
        "device_uid": "SHIELD-TEST-001"
    })
    print(reg_res.json())

    # 2. Find a 'Stressed' audio file from data/raw
    raw_dir = "data/raw"
    stressed_audio = None
    # RAVDESS: 05=angry, 06=fearful
    for root, dirs, files in os.walk(raw_dir):
        for f in files:
            if f.endswith(".wav") and ("-05-" in f or "-06-" in f):
                stressed_audio = os.path.join(root, f)
                break
        if stressed_audio: break

    if not stressed_audio:
        print("No stressed audio found in data/raw. Using generic .wav")
        # Try any wav
        for root, dirs, files in os.walk(raw_dir):
            for f in files:
                if f.endswith(".wav"):
                    stressed_audio = os.path.join(root, f)
                    break
            if stressed_audio: break

    # 3. Send Event with Vitals + Audio
    print(f"2. Sending Emergency Event (HR=115, Audio={os.path.basename(stressed_audio)})...")
    with open(stressed_audio, "rb") as audio_file:
        files = {"audio": ("stressed.wav", audio_file, "audio/wav")}
        data = {
            "device_uid": "SHIELD-TEST-001",
            "heart_rate": 115.0,
            "temperature": 38.8,
            "lat": 28.6139,
            "lng": 77.2090,
            "battery": 82
        }
        event_res = requests.post(f"{BASE_URL}/device/event", data=data, files=files)
    
    print("Response:", event_res.json())
    
    if event_res.status_code == 200 and event_res.json().get('alert_triggered'):
        print("SUCCESS: Emergency Alert Triggered via Sensor Fusion!")
    else:
        print("FAILURE: Alert not triggered.")

if __name__ == "__main__":
    test_full_integration()
