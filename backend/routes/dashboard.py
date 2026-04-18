"""
Dashboard routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from utils import get_logger
from models import User, SensorReading, RealtimeLMP
from routes.battery import get_battery_level, get_battery_status
from routes.cost import calculate_cost_savings, get_hour_zone
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


logger = get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_current_user(db: Session) -> dict:
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        return {"firstName": None, "fullName": None}

    full_name  = user.full_name.strip() if user.full_name else None
    first_name = full_name.split()[0] if full_name else None

    return {"firstName": first_name, "fullName": full_name}


def get_current_price(db: Session) -> float | None:
    latest = (
        db.query(RealtimeLMP)
        .filter(RealtimeLMP.latest_version == True)
        .order_by(RealtimeLMP.datetime_beginning_utc.desc())
        .first()
    )
    return round(latest.total_lmp_rt / 1000, 4) if latest else None


def get_current_source(db: Session) -> str | None:
    latest = (
        db.query(SensorReading)
        .filter(SensorReading.user_id == 1)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    return latest.power_source.capitalize() if latest else None


def get_uptime(db: Session, days: int = 30) -> float | None:
    """
    Estimates uptime as % of 10-second intervals in the last N days
    that have at least one sensor reading.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    total_expected = (days * 24 * 60 * 60) / 10  # expected readings at 10s interval

    bucket = func.floor(func.extract("epoch", SensorReading.timestamp) / 10)
    actual = (
        db.query(func.count(func.distinct(bucket)))
        .filter(SensorReading.user_id == 1)
        .filter(SensorReading.timestamp >= since)
        .scalar()
    )

    if not actual:
        return None

    return round(min(actual / total_expected * 100, 100.0), 1)


@router.get("/")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Get all dashboard overview data.
    Returns everything needed to display the dashboard page.
    """
    logger.info("Dashboard data requested")

    user           = get_current_user(db)
    current_price  = get_current_price(db)
    now_ept        = datetime.now(ZoneInfo("America/New_York"))
    monthly_costs  = calculate_cost_savings(db, days=30)
    daily_costs    = calculate_cost_savings(db, days=1)

    dashboard_data = {
        "user": user,
        "battery": {
            "level":  get_battery_level(db),
            "status": get_battery_status(db)
        },
        "power": {
            "source":       get_current_source(db),
            "currentPrice": current_price,
            "priceTier":    get_hour_zone(now_ept).replace("_", "-").title()  # "Off-Peak", "Standard", "Peak"
        },
        "savings": {
            "today": daily_costs["monthlyCost"]["savings"],
            "month": monthly_costs["monthlyCost"]["savings"]
        },
        "energy": {
            "usedToday": None,   # requires current sensor (INA219)
            "usedWeek":  None,
            "usedMonth": None
        },
        "system": {
            "batteryCycles": None,   # not tracked yet
            "uptime":        get_uptime(db, days=30)
        }
    }

    logger.debug(f"Returning dashboard data for user={dashboard_data['user']['fullName']}, battery={dashboard_data['battery']['level']}%")

    return dashboard_data