"""
EnergyReading model for tracking energy consumption data
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base


class EnergyReading(Base):
    """
    Energy consumption readings from Raspberry Pi
    Stores historical energy usage data over time
    """
    __tablename__ = "energy_readings"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key - links to User table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # ForeignKey("users.id") means this must match an id in the users table
    
    # Timestamp - when this reading was taken
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    # index=True makes time-based queries faster (we'll query by date a lot)
    
    # Power source at this time
    power_source = Column(String, nullable=False)
    # Values: "grid" or "battery"
    
    # Energy consumed during this reading
    energy_consumption = Column(Float, nullable=False)
    # Measured in kWh (kilowatt-hours)
    
    # Electricity price at this time
    electricity_price = Column(Float, nullable=False)
    # Price per kWh (e.g., 0.28 = $0.28/kWh)
    
    # Total cost for this reading
    cost = Column(Float, nullable=False)
    # Calculated as: energy_consumption * electricity_price
    
    # Battery level at this time (snapshot)
    battery_level = Column(Integer)
    # Percentage (0-100)
    
    # Relationship back to User
    user = relationship("User", back_populates="energy_readings")
    # This allows: reading.user to get the User object
    # And: user.energy_readings to get all readings for that user
    
    def __repr__(self):
        return f"<EnergyReading(time={self.timestamp}, consumption={self.energy_consumption}kWh, source={self.power_source})>"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

"""
Creating a reading:
-------------------
from models.energy_reading import EnergyReading

reading = EnergyReading(
    user_id=1,
    power_source="battery",
    energy_consumption=1.5,      # 1.5 kWh used
    electricity_price=0.28,      # $0.28 per kWh
    cost=0.42,                   # 1.5 * 0.28 = $0.42
    battery_level=75
)
db.add(reading)
db.commit()


Get last 24 hours of readings:
-------------------------------
from datetime import timedelta

yesterday = datetime.now(timezone.utc) - timedelta(days=1)
readings = db.query(EnergyReading).filter(
    EnergyReading.user_id == user_id,
    EnergyReading.timestamp >= yesterday
).all()


Get total consumption for today:
---------------------------------
from sqlalchemy import func

today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
total = db.query(func.sum(EnergyReading.energy_consumption)).filter(
    EnergyReading.user_id == user_id,
    EnergyReading.timestamp >= today_start
).scalar()


Get hourly consumption (for charts):
------------------------------------
from sqlalchemy import func, extract

hourly_data = db.query(
    extract('hour', EnergyReading.timestamp).label('hour'),
    func.sum(EnergyReading.energy_consumption).label('total_kwh')
).filter(
    EnergyReading.user_id == user_id,
    EnergyReading.timestamp >= yesterday
).group_by('hour').all()
"""