"""
Cost and savings routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from utils import get_logger
from models import SwitchEvent, SensorReading, RealtimeLMP, DayAheadLMP
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

logger = get_logger(__name__)

router = APIRouter(prefix="/cost", tags=["Cost"])

BATTERY_CAPACITY_KWH = 0.004  # EEMB 3.7V 1100mAh LiPo

# Time-of-day zones in EPT (Eastern Prevailing Time)
# Frontend converts to local display time
PEAK_HOURS_EPT    = range(17, 21)  # 17:00 - 21:00
OFF_PEAK_HOURS_EPT = range(0, 6)   # 00:00 - 06:00
# Standard = everything else

EPT = ZoneInfo("America/New_York")


def get_hour_zone(dt: datetime) -> str:
    """
    Returns the tariff zone for a given datetime in EPT.
    """
    ept_dt = dt.astimezone(EPT)
    hour = ept_dt.hour
    if hour in PEAK_HOURS_EPT:
        return "peak"
    if hour in OFF_PEAK_HOURS_EPT:
        return "off_peak"
    return "standard"


def get_switch_windows(db: Session, days: int = 30) -> list[dict]:
    """
    Returns a list of charge/discharge windows from SwitchEvents.
    Each window has a start, end, and type (grid=charging, battery=discharging).
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    # Get the last event before the window — seeds the first window's type
    seed_event = (
        db.query(SwitchEvent)
        .filter(SwitchEvent.user_id == 1)
        .filter(SwitchEvent.timestamp < since)
        .order_by(SwitchEvent.timestamp.desc())
        .first()
    )

    events = (
        db.query(SwitchEvent)
        .filter(SwitchEvent.user_id == 1)
        .filter(SwitchEvent.timestamp >= since)
        .order_by(SwitchEvent.timestamp.asc())
        .all()
    )

    windows = []

    # If there's a seed event, start a window from `since` with its type
    if seed_event:
        first_end = events[0].timestamp if events else datetime.now(timezone.utc)
        windows.append({
            "type": seed_event.switched_to,
            "start": since,
            "end": first_end
        })

    for i in range(len(events)):
        start = events[i].timestamp
        end = events[i + 1].timestamp if i + 1 < len(events) else datetime.now(timezone.utc)
        windows.append({
            "type": events[i].switched_to,
            "start": start,
            "end": end
        })

    return windows


def get_battery_level_at(db: Session, timestamp: datetime) -> float | None:
    """
    Returns the closest battery level reading to a given timestamp.
    """
    max_gap = timedelta(minutes=15)
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.user_id == 1)
        .filter(SensorReading.timestamp >= timestamp - max_gap)
        .filter(SensorReading.timestamp <= timestamp + max_gap)
        .order_by(func.abs(func.extract('epoch', SensorReading.timestamp - timestamp)))
        .first()
    )
    return reading.battery_level if reading else None


def get_avg_lmp(db: Session, start: datetime, end: datetime) -> float | None:
    """
    Returns average real-time LMP over a window in USD/MWh.
    """
    result = (
        db.query(func.avg(RealtimeLMP.total_lmp_rt))
        .filter(RealtimeLMP.latest_version == True)
        .filter(RealtimeLMP.datetime_beginning_utc >= start)
        .filter(RealtimeLMP.datetime_beginning_utc < end)
        .scalar()
    )
    return result


def get_pricing_zones(db: Session) -> list[dict]:
    """
    Returns 24 hours of pricing data for the chart.
    Past hours use RealtimeLMP, future hours use DayAheadLMP.
    Timestamps are in EPT for frontend display.
    """
    now_ept = datetime.now(EPT)
    now = now_ept.astimezone(timezone.utc)
    start_of_day_ept = now_ept.replace(hour=0, minute=0, second=0, microsecond=0)

    pricing_zones = []

    for hour in range(24):
        hour_start_ept = start_of_day_ept + timedelta(hours=hour)
        hour_end_ept = hour_start_ept + timedelta(hours=1)
        hour_start = hour_start_ept.astimezone(timezone.utc)
        hour_end = hour_end_ept.astimezone(timezone.utc)
        is_past = hour_start <= now

        if is_past:
            price = (
                db.query(func.avg(RealtimeLMP.total_lmp_rt))
                .filter(RealtimeLMP.latest_version == True)
                .filter(RealtimeLMP.datetime_beginning_utc >= hour_start)
                .filter(RealtimeLMP.datetime_beginning_utc < hour_end)
                .scalar()
            )
        else:
            price = (
                db.query(func.avg(DayAheadLMP.total_lmp_da))
                .filter(DayAheadLMP.latest_version == True)
                .filter(DayAheadLMP.datetime_beginning_utc >= hour_start)
                .filter(DayAheadLMP.datetime_beginning_utc < hour_end)
                .scalar()
            )

        pricing_zones.append({
            "hour": hour_start_ept.isoformat(),
            "price": round(price / 1000, 4) if price is not None else None,  # USD/MWh → USD/kWh
            "is_forecast": not is_past
        })

    return pricing_zones


def calculate_cost_savings(db: Session, days: int = 30) -> dict:
    """
    Calculates actual cost paid vs estimated cost without the system,
    broken down by tariff zone (peak, off-peak, standard).
    """
    windows = get_switch_windows(db, days)

    # Guard against no switch events
    if not windows:
        return {
            "monthlyCost": {
                "actual":            0.0,
                "withoutSystem":     0.0,
                "savings":           0.0,
                "savingsPercentage": 0.0
            },
            "breakdown": []
        }

    # Totals
    total_actual = 0.0
    total_without_system = 0.0

    # Zone breakdown
    zones = {
        "peak":     {"actual": 0.0, "without_system": 0.0},
        "off_peak": {"actual": 0.0, "without_system": 0.0},
        "standard": {"actual": 0.0, "without_system": 0.0},
    }

    for window in windows:
        level_start = get_battery_level_at(db, window["start"])
        level_end   = get_battery_level_at(db, window["end"])
        avg_lmp     = get_avg_lmp(db, window["start"], window["end"])

        if level_start is None or level_end is None or avg_lmp is None:
            continue

        energy_kwh = abs(level_end - level_start) / 100 * BATTERY_CAPACITY_KWH
        cost = energy_kwh * avg_lmp / 1000  # USD/MWh → USD/kWh

        # Determine tariff zone from window start time (EPT)
        # Note: crude UTC→EPT approximation (-4h), DST edge cases possible
        ept_start = window["start"].astimezone(EPT)
        zone = get_hour_zone(ept_start)

        if window["type"] == "grid":
            # Charging — this is what we actually paid
            total_actual += cost
            zones[zone]["actual"] += cost
        elif window["type"] == "battery":
            # Discharging — this is what we avoided
            total_without_system += cost
            zones[zone]["without_system"] += cost

    savings = total_without_system - total_actual
    savings_pct = (savings / total_without_system * 100) if total_without_system > 0 else 0

    breakdown = []
    zone_labels = {
        "peak":     {"label": "Peak Hours",     "description": "17:00 - 21:00 EPT"},
        "off_peak": {"label": "Off-Peak Hours", "description": "00:00 - 06:00 EPT"},
        "standard": {"label": "Standard Hours", "description": "06:00 - 17:00, 21:00 - 24:00 EPT"},
    }

    for zone_key, zone_data in zones.items():
        zone_savings = zone_data["without_system"] - zone_data["actual"]
        breakdown.append({
            "category":     zone_labels[zone_key]["label"],
            "description":  zone_labels[zone_key]["description"],
            "actual":       round(zone_data["actual"], 2),
            "withoutSystem": round(zone_data["without_system"], 2),
            "savings":      round(zone_savings, 2),
        })

    return {
        "monthlyCost": {
            "actual":           round(total_actual, 2),
            "withoutSystem":    round(total_without_system, 2),
            "savings":          round(savings, 2),
            "savingsPercentage": round(savings_pct, 1)
        },
        "breakdown": breakdown
    }


@router.get("/")
async def get_cost_data(db: Session = Depends(get_db)):
    """
    Get cost analysis and savings data for the cost tab.
    Returns monthly cost comparison, pricing zones, and cost breakdown.
    """
    logger.info("Cost data requested")

    costs = calculate_cost_savings(db, days=30)

    cost_data = {
        "monthlyCost":  costs["monthlyCost"],
        "pricingZones": get_pricing_zones(db),
        "breakdown":    costs["breakdown"]
    }

    logger.debug(f"Returning cost data: savings=${cost_data['monthlyCost']['savings']}")

    return cost_data