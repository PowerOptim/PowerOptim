"""
Battery status routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from utils import get_logger
from models import SensorReading, SwitchEvent


logger = get_logger(__name__)

router = APIRouter(prefix="/battery", tags=["Battery"])


def get_battery_level(db: Session) -> int | None:
    count = db.query(func.count(SensorReading.id)).scalar()
    if not count:
        return None

    latest = (
        db.query(SensorReading)
        .filter(SensorReading.user_id == 1)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    return latest.battery_level if latest else None


def get_battery_status(db: Session) -> str:
    latest = (
        db.query(SensorReading)
        .filter(SensorReading.user_id == 1)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not latest:
        return "Unknown"
    if latest.battery_level == 100:
        return "Full"
    if latest.current is None:
        return "Unknown"
    if latest.current > 0:
        return "Charging"
    if latest.current < 0:
        return "Discharging"
    return "Idle"


def get_recent_activity(db: Session, limit: int = 10) -> list:
    events = (
        db.query(SwitchEvent)
        .filter(SwitchEvent.user_id == 1)
        .order_by(SwitchEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "action": "SWITCHED TO BATTERY POWER" if e.switched_to == "battery" else "SWITCHED TO GRID POWER",
            "details": e.reason or "No reason provided",
            "timestamp": e.timestamp.isoformat(),
            "icon": "🔋" if e.switched_to == "battery" else "🔌"
        }
        for e in events
    ]


@router.get("/")
async def get_battery_data(db: Session = Depends(get_db), history_limit: int = 10):
    """
    Get battery status and recent activity
    Returns current battery metrics and switching history for battery page
    """
    logger.info("Battery data requested")
    
    battery_data = {
        "status": {
            "level": get_battery_level(db),                    # percentage
            "status": get_battery_status(db),        # "Charging", "Discharging", "Idle", "Full"
            "capacity": 10.0,               # kWh
            "health": 98                    # percentage
        },
        "recentActivity": get_recent_activity(db, history_limit)
    }
    
    logger.debug(f"Returning battery data: level={battery_data['status']['level']}%, status={battery_data['status']['status']}")
    
    return battery_data