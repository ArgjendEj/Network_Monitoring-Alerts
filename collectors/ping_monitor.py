from ping3 import ping
import datetime
import time
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_database():
    conn = sqlite3.connect('ping_monitor.db')  # Ndryshuar emrin e bazës së të dhënave
    c = conn.cursor()
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            host TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def reset_database():
    conn = sqlite3.connect('ping_monitor.db')  # Ndryshuar emrin e bazës së të dhënave
    c = conn.cursor()
    # Fshij të dhënat nga tabela
    c.execute('DELETE FROM alerts')
    # Përdor commit për të mbyllur transaksionin aktual
    conn.commit()
    
    # Kthe ID-në e tabelës në 1
    c.execute('''DELETE FROM sqlite_sequence WHERE name='alerts' ''')
    conn.commit()
    
    conn.close()

def check_host(host):
    latency = ping(host)
    if latency is None:
        return f"{host} is unreachable"
    return f"{host} responded in {latency*1000:.2f} ms"

def log_to_database(host, status):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('ping_monitor.db')  # Ndryshuar emrin e bazës së të dhënave
    c = conn.cursor()
    c.execute(''' 
        INSERT INTO alerts (timestamp, host, status)
        VALUES (?, ?, ?)
    ''', (timestamp, host, status))
    conn.commit()
    conn.close()

def log_to_file_and_db(host, status):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("pingmonitor_log.txt", "a") as f:
        f.write(f"{timestamp} - {host}: {status}\n")
    log_to_database(host, status)

def send_email_alert(host, status):
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_email_password"

    subject = "Network Alert!"
    body = f"ALERT! {host} - {status}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"Email alert sent for {host}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_alert(host, status):
    if "unreachable" in status:
        print(f"ALERT! {host} - {status}")
        send_email_alert(host, status)

def show_database_logs():
    conn = sqlite3.connect('ping_monitor.db')  # Ndryshuar emri i bazës së të dhënave
    c = conn.cursor()
    c.execute("SELECT timestamp, host, status FROM alerts ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()

    print("\n=== DATABASE LOGS (LAST 10) ===")
    print(f"{'No':<4} {'Timestamp':<20} {'Host':<15} {'Status'}")
    print("-" * 70)
    for i, row in enumerate(reversed(rows), 1):
        print(f"{i:<4} {row[0]:<20} {row[1]:<15} {row[2]}")
    print("=" * 70 + "\n")

def monitor_hosts_at_intervals(interval=60):
    hosts = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]
    create_database()
    reset_database()  # Fshij të dhënat dhe rifillo nga ID 1

    while True:
        for h in hosts:
            status = check_host(h)
            print(status)
            log_to_file_and_db(h, status)
            send_alert(h, status)

        show_database_logs()
        print(f"Waiting {interval} seconds before next check...")
        time.sleep(interval)

if __name__ == "__main__":
    monitor_hosts_at_intervals(15)


