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
            
# ====== FUNKSIONET E MONITORIMIT ======
def check_host_connection(host, port=80):
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False

def send_sms_alert(host, issue_description):
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    from_phone = 'your_twilio_phone'
    to_phone = 'your_phone_number'

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = f"NETWORK ALERT\nHost: {host}\nTime: {timestamp}\nIssue: {issue_description}\nPlease check the node immediately!"

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=body,
            from_=from_phone,
            to=to_phone
        )
        print(f"[{timestamp}] SMS alert sent to {to_phone} for {host}\n")
    except Exception as e:
        print(f"[{timestamp}] Error sending SMS: {e}\n")

def send_email_alert(host, issue_description):
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_email_password"

    subject = "URGENT: Network Alert"
    body = f"ALERT! {host} is having an issue: {issue_description}. Please check immediately!"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"Email alert sent for {host}\n")
    except Exception as e:
        print(f"Error sending email: {e}\n")

def log_alert(host, issue_description):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - ALERT: {host} - {issue_description}\n"
    with open("smsalerts_log.txt", "a") as log_file:
        log_file.write(log_message)
    print(f"Log saved: {log_message}")

def monitor_hosts():
    hosts = [
        {"host": "8.8.8.8", "port": 53, "name": "Google DNS"},
        {"host": "1.1.1.1", "port": 53, "name": "Cloudflare DNS"},
        {"host": "192.168.1.1", "port": 80, "name": "Router Local"},
        {"host": "192.168.1.1", "port": 443, "name": "Router HTTPS"},
    ]

    while True:
        for host_info in hosts:
            host = host_info["host"]
            port = host_info["port"]
            host_name = host_info["name"]

            if not check_host_connection(host, port):
                issue_description = f"Port {port} is closed or host is unreachable: {host_name}"
                print(f"ALERT! {host_name} ({host}:{port}) is unreachable.")
                send_sms_alert(host, issue_description)
                send_email_alert(host, issue_description)
                log_alert(host, issue_description)
                save_alert_to_db(host, port, issue_description)
            else:
                print(f"{host_name} ({host}:{port}) is reachable.")
        
        print("Waiting 30 seconds before next check...\n")
        time.sleep(30)

# ====== MAIN ======
if __name__ == "__main__":
    create_database()
    display_all_alerts()
    print("\nMonitoring network and sending SMS & Email alerts")
    monitor_hosts()


