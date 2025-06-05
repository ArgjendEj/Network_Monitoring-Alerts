import requests
import random
import time
import threading
from datetime import datetime

URL = "http://127.0.0.1:8000/monitor"
TOTAL_REQUESTS = 300  # 🔄 Ndryshuar nga 200 në 300 kërkesa
CONCURRENT_THREADS = 20

ip_list = ["1.1.1.1", "8.8.8.8", "192.168.1.1", "10.0.0.1"]

# Funksioni që dërgon një kërkesë POST
def send_request(request_id):
    ip = random.choice(ip_list)
    port = random.randint(1, 65535)
    status = f"Stress test alarm për {ip}:{port} ({datetime.now().isoformat()})"
    
    try:
        response = requests.post(URL, params={"ip": ip, "port": port, "status": status})
        if response.status_code == 200:
            print(f"[{request_id}] ✅ Sukses - {ip}:{port}")
        else:
            print(f"[{request_id}] ❌ Gabim {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{request_id}] ❌ Exception: {e}")

# Menaxhon dërgimin e kërkesave me fije paralele
def run_stress_test():
    threads = []
    for i in range(TOTAL_REQUESTS):
        t = threading.Thread(target=send_request, args=(i+1,))
        threads.append(t)
        t.start()

        if len(threads) >= CONCURRENT_THREADS:
            for t in threads:
                t.join()
            threads = []

        if (i + 1) % 10 == 0:
            print(f"📊 Derguar {i+1}/{TOTAL_REQUESTS} kërkesa...")

    for t in threads:
        t.join()

    print("\n🚨 Stress test përfundoi.")

# Ekzekutimi kryesor
if __name__ == "__main__":
    print(f"🚀 Filloi stress testi me {TOTAL_REQUESTS} kërkesa...")
    start = time.time()
    run_stress_test()
    end = time.time()
    print(f"\n⏱️ Koha totale: {end - start:.2f} sekonda.")
