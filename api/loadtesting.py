import requests
import random
import time
from datetime import datetime

# Parametrat e testit
URL = "http://127.0.0.1:8000/monitor"
NUM_REQUESTS = 50  # Sa kërkesa dëshiron të dërgosh
DELAY = 0.1  # Sa sekonda pauzë mes çdo kërkese
# Lista e IP-ve testuese
ip_list = ["1.1.1.1", "8.8.8.8", "192.168.1.1", "10.0.0.1"]

print(f"🚀 Filloi testimi i ngarkesës në {URL}\n")

# Funksioni për të gjeneruar status të rastësishëm
def generate_status(ip, port):
    return f"Test alarm nga load test për {ip}:{port} në {datetime.now().isoformat()}"

# Dërgo kërkesat
for i in range(NUM_REQUESTS):
    ip = random.choice(ip_list)
    port = random.randint(1, 65535)
    status = generate_status(ip, port)

    try:
        response = requests.post(URL, params={"ip": ip, "port": port, "status": status})
        if response.status_code == 200:
            print(f"[{i+1}] ✅ Kërkesa e dërguar: {ip}:{port}")
        else:
            print(f"[{i+1}] ❌ Gabim: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{i+1}] ❌ Gabim në dërgim: {e}")

    time.sleep(DELAY)

print("\n✅ Testimi i ngarkesës përfundoi.")
