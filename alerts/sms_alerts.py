from twilio.rest import Client
import datetime
import time
import socket
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3

# ====== KONFIGURIMET E DATABASE ======
DB_PATH = "sms_alerts.db"

def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                issue_description TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
    print("Databaza 'sms_alerts.db' dhe tabela 'alerts' janë krijuar.")

def save_alert_to_db(host, port, issue_description):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (host, port, issue_description, timestamp)
            VALUES (?, ?, ?, ?)
        """, (host, port, issue_description, timestamp))
        conn.commit()
    print(f"Alarmi u ruajt në databazë për {host}:{port}")

def display_all_alerts():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts")
        rows = cursor.fetchall()
        if rows:
            print("\nLista e alarmeve ekzistuese në databazë:")
            for row in rows:
                print(f"ID: {row[0]} | Host: {row[1]} | Port: {row[2]} | Issue: {row[3]} | Time: {row[4]}")
        else:
            print("\nNuk ka alarme të regjistruara në databazë.")
