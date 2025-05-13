import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os
import subprocess  # Përdoret për të kontrolluar lidhjen me ping

# Funksioni për të krijuar lidhjen me databazën SQLite
def connect_db():
    return sqlite3.connect("email_alerts.db")  # Emri i ri i databazës

# Funksioni për të krijuar tabelën e alarmeve në databazë
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            issue_description TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Funksioni për të futur alarmet në databazë
def insert_alert_to_db(host, issue_description, status):
    conn = connect_db()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO alerts (host, issue_description, status, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (host, issue_description, status, timestamp))
    conn.commit()
    conn.close()

# Funksioni për të shfaqur të dhënat nga databaza
def display_all_alerts():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alerts')
    rows = cursor.fetchall()
    print("\n| id | host       | issue_description  | status      | timestamp           |")
    print("|----|------------|--------------------|-------------|---------------------|")
    for row in rows:
        print(f"| {row[0]:<2} | {row[1]:<10} | {row[2]:<18} | {row[3]:<11} | {row[4]:<19} |")
    conn.close()

# Funksioni për të ruajtur alarmet në një skedar log
def log_alert_to_file(host, issue_description):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {host} - {issue_description}\n"

    log_file = os.path.join(os.path.dirname(__file__), "emailalert_logs.txt")  # Emri i ri i fajllit log
    with open(log_file, "a") as log:
        log.write(log_message)

# Funksioni për të kontrolluar lidhjen me ping
def is_host_reachable(host):
    try:
        # Përdor ping për të kontrolluar lidhjen (unë përdora 'ping' që është në sistemet Linux/Windows)
        response = subprocess.run(['ping', '-c', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error pinging host: {e}")
        return False

# Funksioni për të dërguar një alarm me email dhe për ta loguar
def send_network_email_alert(host, issue_description, is_reachable):
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_email_password"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if is_reachable:
        subject = f"Network Status: {host} is reachable"
        body = f"""
        ✅ NETWORK STATUS ✅

        Host: {host}
        Time: {timestamp}
        Status: Host is reachable

        Everything is functioning properly.
        """
    else:
        subject = f"Network Alert: {host} unreachable"
        body = f"""
        🚨 NETWORK ALERT 🚨

        Host: {host}
        Time: {timestamp}
        Issue: {issue_description}

        Please check the node immediately!
        """

    # Shfaq në terminal përmbajtjen e alarmit
    print("\n--- Email Alert Details ---")
    print(f"To: {receiver_email}")
    print(f"Subject: {subject}")
    print("Message Body:")
    print(body)
    print("---------------------------\n")

    # Ndërto email-in
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Dërgo email-in
    try:
        server = smtplib.SMTP('smtp.example.com', 587)  # NDRYSHO SMTP
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"[{timestamp}] ✅ Email alert sent for {host}\n")
    except Exception as e:
        print(f"[{timestamp}] ❌ Error sending email: {e}\n")

    # Ruaj alarmin në fajll log
    log_alert_to_file(host, issue_description)

    # Ruaj alarmin në databazë
    insert_alert_to_db(host, issue_description, "reachable" if is_reachable else "unreachable")

    # Shfaq të dhënat nga databaza
    display_all_alerts()

# Testim i drejtpërdrejtë kur ekzekutohet ky file
if __name__ == "__main__":
    create_table()  # Krijo tabelën kur ekzekutohet për herë të parë
    print("🔧 Testim i alarmit për rrjetin")
    test_host = input("Shkruaj IP ose hostname për test: ")
    
    if is_host_reachable(test_host):
        send_network_email_alert(test_host, "No issues detected", True)  # Përdor statusin "arritje pozitive"
    else:
        issue = input("Shkruaj përshkrimin e problemit: ")
        send_network_email_alert(test_host, issue, False)  # Përdor statusin "problemi"



