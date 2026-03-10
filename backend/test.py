"""Quick script to add test data"""
from sqlalchemy.orm import Session
from database.database import SessionLocal, init_db
from models import User, EnergyReading, BatteryStatus
from datetime import datetime, timezone

# Make sure tables exist
init_db()

# Create a session
db = SessionLocal()

try:
    # Add a user
    user = User(
        email="john@test.com",
        hashed_password="fakehash123",
        full_name="John Doe",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # Get the ID
    
    # Add energy reading
    reading = EnergyReading(
        user_id=user.id,
        timestamp=datetime.now(timezone.utc),
        power_source="battery",
        energy_consumption=1.5,
        electricity_price=0.28,
        cost=0.42,
        battery_level=78
    )
    db.add(reading)
    
    # Add battery status
    battery = BatteryStatus(
        user_id=user.id,
        timestamp=datetime.now(timezone.utc),
        level=78,
        voltage=48.2,
        current=-2.5,
        temperature=25.3,
        health=98,
        status="discharging",
        cycles=47
    )
    db.add(battery)
    
    db.commit()
    print("✅ Test data added!")
    print(f"User ID: {user.id}")
    
finally:
    db.close()