"""
BatteryStatus model for tracking battery health and metrics
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base


class BatteryStatus(Base):
    """
    Battery status snapshots
    More detailed than EnergyReading - focuses on battery health and metrics
    """
    __tablename__ = "battery_status"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key - links to User table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamp - when this snapshot was taken
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Battery charge level
    level = Column(Integer, nullable=False)
    # Percentage (0-100)
    
    # Electrical measurements
    voltage = Column(Float, nullable=False)
    # Measured in volts (e.g., 48.2V)
    
    current = Column(Float, nullable=False)
    # Measured in amps
    # Negative = discharging, Positive = charging
    # e.g., -2.5A (discharging), +3.0A (charging)
    
    temperature = Column(Float, nullable=False)
    # Measured in Celsius
    
    # Battery health and lifecycle
    health = Column(Integer, nullable=False)
    # Percentage (0-100), degrades over time
    # 100% = brand new, 80% = needs replacement soon
    
    status = Column(String, nullable=False)
    # Values: "charging", "discharging", "idle", "full"
    
    cycles = Column(Integer, nullable=False)
    # Total number of full charge cycles
    # Increments each time battery goes from 0% → 100%
    # Used to predict battery lifespan
    
    # Relationship back to User
    user = relationship("User", back_populates="battery_statuses")
    
    def __repr__(self):
        return f"<BatteryStatus(time={self.timestamp}, level={self.level}%, status={self.status})>"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

"""
Creating a battery status snapshot:
------------------------------------
from models.battery_status import BatteryStatus

status = BatteryStatus(
    user_id=1,
    level=78,
    voltage=48.2,
    current=-2.5,        # Negative = discharging
    temperature=25.3,
    health=98,
    status="discharging",
    cycles=47
)
db.add(status)
db.commit()


Get current battery status:
---------------------------
current_status = db.query(BatteryStatus).filter(
    BatteryStatus.user_id == user_id
).order_by(BatteryStatus.timestamp.desc()).first()


Get battery history (last 24 hours):
------------------------------------
from datetime import timedelta

yesterday = datetime.now(timezone.utc) - timedelta(days=1)
history = db.query(BatteryStatus).filter(
    BatteryStatus.user_id == user_id,
    BatteryStatus.timestamp >= yesterday
).order_by(BatteryStatus.timestamp).all()


Check if battery is low:
------------------------
latest = db.query(BatteryStatus).filter(
    BatteryStatus.user_id == user_id
).order_by(BatteryStatus.timestamp.desc()).first()

if latest and latest.level < 20:
    send_low_battery_alert(user_id)


Track battery degradation over time:
------------------------------------
from sqlalchemy import func

avg_health = db.query(
    func.date(BatteryStatus.timestamp).label('date'),
    func.avg(BatteryStatus.health).label('avg_health')
).filter(
    BatteryStatus.user_id == user_id
).group_by('date').all()
"""