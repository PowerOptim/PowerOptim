"""
System status routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from utils import get_logger
from models import PiStatus
from routes.dashboard import get_uptime
from datetime import datetime, timezone

logger = get_logger(__name__)

router = APIRouter(prefix="/system", tags=["System"])


def get_latest_pi_status(db: Session):
    return (
        db.query(PiStatus)
        .filter(PiStatus.user_id == 1)
        .order_by(PiStatus.timestamp.desc())
        .first()
    )


@router.get("/")
async def get_system_data(db: Session = Depends(get_db)):
    """
    Get system status and device information for the system tab.
    Returns system health metrics and Raspberry Pi device info.
    """
    logger.info("System data requested")

    pi = get_latest_pi_status(db)
    pi_active = pi and (datetime.now(timezone.utc) - pi.timestamp.replace(tzinfo=timezone.utc)).seconds < 300

    system_data = {
        "health": {
            "system":        "Online",
            "apiConnection": "Connected",
            "raspberryPi":   "Active" if pi_active else "Inactive",
            "lastUpdate":    pi.timestamp.isoformat() if pi else None,
            "uptime":        get_uptime(db, days=30)
        },
        "device": {
            "deviceId":  pi.device_id if pi else None,
            "firmware":  pi.firmware if pi else None,
            "ipAddress": pi.ip_address if pi else None,
            "cpu":       pi.cpu_percent if pi else None,
            "memory": {
                "used":  pi.memory_used_gb if pi else None,
                "total": pi.memory_total_gb if pi else None
            }
        }
    }

    logger.debug(f"Returning system data: raspberryPi={system_data['health']['raspberryPi']}")

    return system_data