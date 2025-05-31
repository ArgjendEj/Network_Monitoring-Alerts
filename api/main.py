from fastapi import FastAPI, HTTPException
import sqlite3
from datetime import datetime
import os
import logging
from tabulate import tabulate

app = FastAPI()

DB_PATH = "api_alerts.db"

# Konfiguro logimin në file dhe console
logging.basicConfig(
    filename="api_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Print në console gjithashtu
def log_console(message):
    print(message)
    logging.info(message)

# Krijo databazën nëse nuk ekziston
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
        log_console("✅ Databaza dhe tabela 'alerts' u krijuan.")

# Printo të gjitha alarmet e ruajtura
def display_all_alerts():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts")
            rows = cursor.fetchall()
            if rows:
                headers = ["ID", "IP", "Port", "Status", "Timestamp"]
                table = tabulate(rows, headers=headers, tablefmt="grid")
                log_console("\n📋 Lista e alarmeve në databazë:\n" + table)
            else:
                log_console("📭 Nuk ka alarme të regjistruara.")
    except Exception as e:
        log_console(f"❌ Gabim gjatë leximit të databazës: {e}")

# Shto disa alarme testuese
def insert_test_alarm():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        test_data = [
            ("1.1.1.1", 80, "Test alarm 1.1.1.1"),
            ("8.8.8.8", 53, "Test alarm 8.8.8.8"),
            ("192.168.1.1", 8080, "Test alarm 192.168.1.1")
        ]
        for ip, port, status in test_data:
            cursor.execute("""
                INSERT INTO alerts (ip, port, status, timestamp)
                VALUES (?, ?, ?, ?)
            """, (ip, port, status, datetime.now().isoformat()))
        conn.commit()
        log_console("✅ U shtuan 3 alarme testuese.")

# Endpoint për marrjen e alarmave
@app.get("/alerts")
def get_alerts():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts")
            rows = cursor.fetchall()
            if rows:
                return {
                    "alerts": [
                        {
                            "ID": row[0],
                            "IP": row[1],
                            "Port": row[2],
                            "Status": row[3],
                            "Timestamp": row[4]
                        } for row in rows
                    ]
                }
            else:
                return {"message": "Nuk ka alarme të regjistruara në databazë."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gabim me databazën: {e}")

# Endpoint për regjistrimin e një alarmi të ri
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
            message = f"🔔 Alarm për {ip}:{port} u regjistrua me sukses."
            log_console(message)
            return {"message": message}
    except Exception as e:
        log_console(f"❌ Gabim gjatë regjistrimit të alarmit: {e}")
        raise HTTPException(status_code=500, detail=f"Gabim gjatë regjistrimit: {e}")

# Ekzekutohet kur API startohet
@app.on_event("startup")
def startup_event():
    log_console("🚀 API po starton...")
    create_database()
    insert_test_alarm()
    display_all_alerts()
###################### uvicorn api.main:app --reload