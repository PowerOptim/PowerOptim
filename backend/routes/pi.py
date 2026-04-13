"""
Pi routes - all communication between Raspberry Pi and backend lives here
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from utils import get_logger
from services.decision_service import get_pending_command
from models.itsced_lmp import ItscedLMP
from models.realtime_lmp import RealtimeLMP
from models.sensor_reading import SensorReading
from models.switch_event import SwitchEvent
from schemas.sensor_reading import SensorReadingCreate
from schemas.switch_event import SwitchEventCreate


logger = get_logger(__name__)

router = APIRouter(prefix="/pi", tags=["Pi"])


@router.post("/readings")
async def receive_reading(
    payload: SensorReadingCreate, 
    db: Session = Depends(get_db)
):
    """
    Receives a sensor snapshot from the Raspberry Pi and saves it to the database.
    Pi should call this every 10-30 seconds.
    """
    logger.info(
        f"Received reading from Pi: battery={payload.battery_level}%, "
        f"source={payload.power_source}"
    )

    reading = SensorReading(
        user_id=1,  # Hardcoded until auth is built
        battery_level=payload.battery_level,
        power_source=payload.power_source,
        voltage=payload.voltage,
        current=payload.current,
        temperature=payload.temperature
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    logger.debug(f"Saved reading id={reading.id} at {reading.timestamp}")

    return {
        "success": True,
        "id": reading.id,
        "timestamp": reading.timestamp
    }
    

def get_grid_now(db: Session) -> float | None:
    now = datetime.now(timezone.utc)
    latest = (
        db.query(RealtimeLMP)
        .filter(RealtimeLMP.valid_until > now)
        .order_by(RealtimeLMP.datetime_beginning_utc.desc())
        .first()
    )
    return latest.total_lmp_rt if latest else None

def get_grid_future(db: Session) -> float | None:
    now = datetime.now(timezone.utc)
    latest = (
        db.query(ItscedLMP)
        .filter(ItscedLMP.valid_until > now)
        .order_by(ItscedLMP.datetime_beginning_utc.desc()).
        first()
    )
    return latest.itsced_lmp if latest else None


def get_battery_level(db: Session) -> int | None:
    latest = (
        db.query(SensorReading)
        .filter(SensorReading.user_id == 1)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    return latest.battery_level if latest else None
    

@router.get("/pending-command")
async def pending_command(db: Session = Depends(get_db)):
    """
    Pi polls this endpoint to check if it should switch power sources.
    Pi should call this every 10-30 seconds.
    """
    logger.info("Pi requesting pending command")

    g_now = get_grid_now(db)
    g_future = get_grid_future(db)
    b_charge = get_battery_level(db)

    if g_now is None or g_future is None:
        raise HTTPException(status_code=503, detail="Grid pricing unavailable")
    result = get_pending_command(g_now, g_future, b_charge)

    logger.debug(
        f"Returning command: {result['command']}, reason: {result['reason']}"
    )

    return result


@router.post("/confirm-switch")
async def confirm_switch(payload: SwitchEventCreate, db: Session = Depends(get_db)):
    """
    Pi calls this after physically switching power sources.
    Logs the switch event to the database.
    """
    logger.info(
        f"Pi confirmed switch to {payload.switched_to}, "
        f"reason: {payload.reason}"
    )

    event = SwitchEvent(
        user_id=1,  # Hardcoded until auth is built
        switched_to=payload.switched_to,
        reason=payload.reason
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    logger.debug(f"Saved switch event id={event.id} at {event.timestamp}")

    return {
        "success": True,
        "id": event.id,
        "timestamp": event.timestamp
    }
