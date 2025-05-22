import sqlite3
from datetime import datetime
import os
import logging
from fastapi import FastAPI, HTTPException
from tabulate import tabulate  # Lib për printimin e tabelave në console

app = FastAPI()

DB_PATH = "api_alerts.db"

# Konfigurimi i logging
logging.basicConfig(
    filename="api_log.txt",  # Ndryshimi i skedarit të log-imit në api_log.txt
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Funksioni për të krijuar databazën dhe tabelën
def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        logging.info("✅ Databaza 'api_alerts.db' dhe tabela 'alerts' janë krijuar.")

# Funksioni për të marrë të gjitha alarmet nga databaza dhe për t'i shfaqur si tabelë
def display_all_alerts():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts")
            rows = cursor.fetchall()
            if rows:
                headers = ["ID", "IP", "Port", "Status", "Timestamp"]
                print("\n📋 Lista e alarmeve të regjistruara:\n")
                print(tabulate(rows, headers=headers, tablefmt="grid"))
                logging.info("📋 Lista e alarmeve u printua në console.")
            else:
                print("📭 Nuk ka alarme të regjistruara në databazë.")
                logging.info("📭 Nuk ka alarme të regjistruara në databazë.")
    except Exception as e:
        logging.error(f"❌ Gabim gjatë leximit të databazës: {e}")
        print(f"❌ Gabim gjatë leximit të databazës: {e}")

# Funksioni për të shtuar alarm testues me IP-të 1.1.1.1, 8.8.8.8 dhe 192.168.1.1
def insert_test_alarm():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Alarm për IP 1.1.1.1
        cursor.execute(""" 
            INSERT INTO alerts (ip, port, status, timestamp) 
            VALUES (?, ?, ?, ?)
        """, ("1.1.1.1", 80, "Test insert alarm 1.1.1.1", datetime.now().isoformat()))
        
        # Alarm për IP 8.8.8.8
        cursor.execute(""" 
            INSERT INTO alerts (ip, port, status, timestamp) 
            VALUES (?, ?, ?, ?)
        """, ("8.8.8.8", 53, "Test insert alarm 8.8.8.8", datetime.now().isoformat()))
        
        # Alarm për IP 192.168.1.1
        cursor.execute(""" 
            INSERT INTO alerts (ip, port, status, timestamp) 
            VALUES (?, ?, ?, ?)
        """, ("192.168.1.1", 8080, "Test insert alarm 192.168.1.1", datetime.now().isoformat()))
        
        conn.commit()
        logging.info("✅ Alarme testues u shtuan në databazë për 1.1.1.1, 8.8.8.8 dhe 192.168.1.1.")

# Funksioni për të marrë të gjitha alarmet
@app.get("/alerts")
def get_alerts():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts")
            rows = cursor.fetchall()
            if rows:
                alerts = [{
                    "ID": row[0],
                    "IP": row[1],
                    "Port": row[2],
                    "Status": row[3],
                    "Timestamp": row[4]
                } for row in rows]
                return {"alerts": alerts}
            else:
                return {"message": "Nuk ka alarme të regjistruara në databazë."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gabim gjatë lidhjes me databazën: {e}")

# Funksioni për të shtuar alarm
@app.post("/monitor")
def monitor_host(ip: str, port: int, status: str):
    timestamp = datetime.now().isoformat()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(""" 
                INSERT INTO alerts (ip, port, status, timestamp) 
                VALUES (?, ?, ?, ?)
            """, (ip, port, status, timestamp))
            conn.commit()
            logging.info(f"🔔 Alarm për {ip}:{port} u regjistrua me sukses.")
            return {"message": f"Alarmi për {ip}:{port} u regjistrua me sukses!"}
    except Exception as e:
        logging.error(f"❌ Gabim gjatë regjistrimit të alarmeve: {e}")
        raise HTTPException(status_code=500, detail=f"Gabim gjatë regjistrimit të alarmeve: {e}")

# Ekzekutohet kur API startohet
@app.on_event("startup")
def startup_event():
    create_database()
    insert_test_alarm()  # Shto alarm testues
    display_all_alerts()  # Shfaq alarme në console

# Krijo databazën dhe shto test alarm nëse është bosh
if not os.path.exists(DB_PATH):
    create_database()

insert_test_alarm()  # Shto alarm testues në çdo ekzekutim

# Ekzekuto API-në në mënyrë lokale
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
