import socket
import time
import datetime
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Funksioni qe krijon databazen dhe tabelen nese nuk ekziston
def create_database():
    conn = sqlite3.connect("network_monitor.db", timeout=10)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            host TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Funksioni qe shkruan log ne databaze
def log_to_database(host, status):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attempt = 0
    max_attempts = 5

    while attempt < max_attempts:
        try:
            conn = sqlite3.connect("network_monitor.db", timeout=10)
            c = conn.cursor()
            c.execute('INSERT INTO logs (timestamp, host, status) VALUES (?, ?, ?)', (timestamp, host, status))
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError:
            attempt += 1
            print(f"Database is locked. Retrying {attempt}/{max_attempts}...")
            time.sleep(2)
        except Exception as e:
            print(f"Error logging to database: {e}")
            break

# Funksioni qe kontrollon nese porti eshte i hapur per hostin
def check_host_port(host, port):
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        return f"{host}:{port} is open"
    except (socket.timeout, socket.error):
        return f"{host}:{port} is unreachable or closed"

# Funksioni per te shkruar te dhenat ne nje skedar log dhe databaze
def log_to_file(host, status):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("networkmonitor_log.txt", "a") as f:
        f.write(f"{timestamp} - {host}: {status}\n")
    log_to_database(host, status)

# Funksioni per te derguar alarme me email
def send_email_alert(host, status):
    sender_email = "your_email@example.com"
    receiver_email = "receiver_email@example.com"
    password = "your_email_password"

    subject = "Network Port Alert!"
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
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"Email alert sent for {host}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Funksioni per te derguar alarme
def send_alert(host, status):
    print(f"ALERT! {host} - {status}")
    send_email_alert(host, status)

# Funksioni per te shfaqur te dhenat nga databaza ne forme tabele
def show_logs():
    conn = sqlite3.connect("network_monitor.db", timeout=10)
    c = conn.cursor()
    c.execute('SELECT * FROM logs')
    rows = c.fetchall()
    print("\n--- Logs ---")
    print("ID    | Timestamp            | Host            | Status")
    print("------------------------------------------------------------")
    for row in rows:
        print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<15} | {row[3]}")
    conn.close()

# Funksioni qe monitoron hostet dhe portet dhe shfaq log-et ne intervale te caktuara
def monitor_and_show_logs(hosts_ports, interval=15):
    while True:
        for host, port in hosts_ports:
            status = check_host_port(host, port)
            print(status)
            log_to_file(host, status)
            if "unreachable" in status:
                send_alert(f"{host}:{port}", status)

        # Shfaq log-et pas çdo kontrolli
        print("\nDisplaying logs:\n")
        show_logs()

        print(f"\nWaiting {interval} seconds before next check...\n")
        time.sleep(interval)

# Lista e hosteve dhe porteve per monitorim
if __name__ == "__main__":
    create_database()
    hosts_ports = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("192.168.1.1", 80),
        ("192.168.1.1", 443),
        ("10.0.0.1", 80),
        ("8.8.4.4", 53),
        ("8.8.8.8", 443)
    ]
    monitor_and_show_logs(hosts_ports, interval=15)

