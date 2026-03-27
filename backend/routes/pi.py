"""
Pi routes - all communication between Raspberry Pi and backend lives here
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.sensor_reading import SensorReading
from schemas.sensor_reading import SensorReadingCreate
from models.switch_event import SwitchEvent
from schemas.switch_event import SwitchEventCreate
from utils import get_logger
from services.decision_service import get_pending_command

logger = get_logger(__name__)

router = APIRouter(prefix="/pi", tags=["Pi"])


@router.post("/readings")
async def receive_reading(payload: SensorReadingCreate, db: Session = Depends(get_db)):
    """
    Receives a sensor snapshot from the Raspberry Pi and saves it to the database.
    Pi should call this every 10-30 seconds.
    """
    logger.info(f"Received reading from Pi: battery={payload.battery_level}%, source={payload.power_source}")

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
    
    
@router.get("/pending-command")
async def pending_command():
    """
    Pi polls this endpoint to check if it should switch power sources.
    Pi should call this every 10-30 seconds.
    """
    logger.info("Pi requesting pending command")

    result = get_pending_command()

    logger.debug(f"Returning command: {result['command']}, reason: {result['reason']}")

    return result

@router.post("/confirm-switch")
async def confirm_switch(payload: SwitchEventCreate, db: Session = Depends(get_db)):
    """
    Pi calls this after physically switching power sources.
    Logs the switch event to the database.
    """
    logger.info(f"Pi confirmed switch to {payload.switched_to}, reason: {payload.reason}")

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