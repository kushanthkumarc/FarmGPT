import requests
import time

BASE_URL = "http://localhost:8000"

from db import pest_reports_collection

def test_pest_outbreak():
    print("🧹 Cleaning up old reports...")
    pest_reports_collection.delete_many({})
    
    print("🚀 Starting Community Pest Outbreak Test...")
    
    # Coordinates in Bangalore (approx 50-100m apart)
    reports = [
        {"lat": 12.9716, "lon": 77.5946, "disease_id": "rice_blast", "user_id": "farmer_A"},
        {"lat": 12.9718, "lon": 77.5948, "disease_id": "rice_blast", "user_id": "farmer_B"},
        {"lat": 12.9720, "lon": 77.5950, "disease_id": "rice_blast", "user_id": "farmer_C"}
    ]
    
    for i, data in enumerate(reports):
        print(f"\n📢 Farmer {i+1} reporting Rice Blast...")
        try:
            res = requests.post(f"{BASE_URL}/api/report_pest", json=data)
            result = res.json()
            print(f"Status: {res.status_code}")
            print(f"Response: {result}")
            
            if result.get("outbreak_detected"):
                print("🚨 ALERT TRIGGERED: The 3rd report successfully triggered a community alert!")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    test_pest_outbreak()
