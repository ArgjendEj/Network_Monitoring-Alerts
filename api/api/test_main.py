import sys
import os
from fastapi.testclient import TestClient

# Shto rrugën e projektit në sistem që të mund të importohet main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.main import app

client = TestClient(app)

def test_get_alerts():
    response = client.get("/alerts")
    print("📥 /alerts status_code:", response.status_code)
    print("📋 Përgjigja:", response.json())
    assert response.status_code == 200

def test_monitor_host():
    response = client.post("/monitor", params={
        "ip": "127.0.0.1",
        "port": 8000,
        "status": "Testing from unit test"
    })
    print("🚨 /monitor status_code:", response.status_code)
    print("✅ Përgjigja:", response.json())
    assert response.status_code == 200

# Thirr funksionet që të ekzekutohen kur lëshohet skripti
if __name__ == "__main__":
    test_get_alerts()
    test_monitor_host()
