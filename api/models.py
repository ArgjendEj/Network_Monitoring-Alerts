from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ✅ Modeli për kërkesën e monitorimit
class MonitorRequest(BaseModel):
    host: str
    port: Optional[int] = None
    email: EmailStr
    interval: Optional[int] = 60  # në sekonda

    class Config:
        json_schema_extra = {
            "example": {
                "host": "192.168.1.100",
                "port": 80,
                "email": "admin@example.com",
                "interval": 30
            }
        }

# ✅ Modeli për përgjigje të standardizuara
class APIResponse(BaseModel):
    success: bool
    detail: str
    data: Optional[dict] = None

# ✅ Model për log të alarmeve
class AlertLog(BaseModel):
    host: str
    status: str
    alert_sent: bool
    timestamp: str

# ✅ Krijimi i Bazës së të Dhënave
Base = declarative_base()

class AlertLogDB(Base):
    __tablename__ = 'alert_logs'

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, index=True)
    status = Column(String)
    alert_sent = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ✅ Krijoni engine për SQLite dhe një seancë të bazës së të dhënave
DATABASE_URL = "sqlite:///./models_alerts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Krijoni tabelën e databazës (nëse nuk ekziston)
Base.metadata.create_all(bind=engine)

# ✅ Funksioni për të shkruar log në skedarin .txt
try:
    message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ models.py u ekzekutua me sukses!\n"
    with open("models_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message)
    print("📦 [INFO] Modelet u ngarkuan dhe janë gati për përdorim në API.")
except Exception as e:
    print(f"[ERROR] Nuk u shkrua log: {e}")

# ✅ Funksioni për të ruajtur një alarm në bazën e të dhënave
def save_alert_log(db_session, alert: AlertLog):
    db_alert = AlertLogDB(
        host=alert.host,
        status=alert.status,
        alert_sent=alert.alert_sent,
        timestamp=datetime.fromisoformat(alert.timestamp)
    )
    db_session.add(db_alert)
    db_session.commit()
    db_session.refresh(db_alert)
    return db_alert

# ✅ Funksioni për të printuar të gjitha alarmet në formë tabele
def print_all_alert_logs(db_session):
    alert_logs = db_session.query(AlertLogDB).all()
    if not alert_logs:
        print("⚠️ Nuk ka alarme të ruajtura në databazë.")
        return

    print("\n📋 Tabela e Alarmeve:")
    print("-" * 90)
    print(f"{'ID':<5} {'HOST':<20} {'STATUS':<10} {'ALERT_SENT':<12} {'TIMESTAMP'}")
    print("-" * 90)
    for log in alert_logs:
        print(f"{log.id:<5} {log.host:<20} {log.status:<10} {str(log.alert_sent):<12} {log.timestamp}")
    print("-" * 90)

# ✅ Funksioni kryesor për testim
if __name__ == "__main__":
    db = SessionLocal()

    # Lista me IP për testim
    ip_list = ["192.168.1.100", "8.8.8.8", "1.1.1.1", "192.168.1.1"]

    for ip in ip_list:
        alert_data = AlertLog(
            host=ip,
            status="OK",  # ose "FAIL" nëse doni të simuloni problem
            alert_sent=True,
            timestamp=datetime.now().isoformat()
        )
        saved_alert = save_alert_log(db, alert_data)
        print(f"📝 Alarmi i ruajtur: ID={saved_alert.id} HOST={saved_alert.host}")

    # ✅ Printo të gjitha alarmet në formë tabele
    print_all_alert_logs(db)

    db.close()


