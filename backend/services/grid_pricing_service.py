import os
import requests
from datetime import datetime, timezone, timedelta
from database.database import SessionLocal
from models.realtime_lmp import RealtimeLMP
from models.day_ahead_lmp import DayAheadLMP
from utils import get_logger

logger = get_logger(__name__)

PJM_API_KEY = os.getenv("PJM_API_KEY")
PNODE_ID    = int(os.getenv("PNODE_ID", "116013753"))  # ATSI Hub

if not PJM_API_KEY:
    raise RuntimeError("PJM_API_KEY is missing! Set it in your .env file.")

HEADERS = {"Ocp-Apim-Subscription-Key": PJM_API_KEY}
BASE_URL = "https://api.pjm.com/api/v1"


def _pjm_get(endpoint: str, params: dict) -> list:
    """Shared GET helper with the now-discovered mandatory fields."""
    params["format"] = "json"
    params["startRow"] = 1  # Mandatory per error log
    
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        headers=HEADERS,
        timeout=15,
    )
    
    if response.status_code == 400:
        logger.error(f"PJM 400 Error Detail: {response.text}")
        
    response.raise_for_status()
    return response.json().get("items") or []


def fetch_and_store_realtime_lmp():
    """
    Fetches the most recent real-time 5-min LMP for ATSI hub.
    Uses rt_unverified_fivemin_lmps — best available low-latency feed.
    Typically ~10-15 min behind real time, but most current available.
    """
    db = SessionLocal()
    try:
        items = _pjm_get("rt_unverified_fivemin_lmps", {
            "pnode_id": str(PNODE_ID),
            "datetime_beginning_ept": "5minutesago", 
            "rowCount": 10
        })

        if not items:
            # If 5 minutes is too tight, try 1 hour ago
            items = _pjm_get("rt_unverified_fivemin_lmps", {
                "pnode_id": str(PNODE_ID),
                "datetime_beginning_ept": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "rowCount": 10
            })

        if not items:
            logger.warning("No RT LMP items returned from PJM")
            return

        # Sort descending and take the most recent interval and version
        items.sort(
            key=lambda x: (x["datetime_beginning_utc"], x.get("version_nbr", 0)),
            reverse=True
        )
        data = items[0]

        interval_start_utc = datetime.fromisoformat(data["datetime_beginning_utc"]).replace(tzinfo=timezone.utc)

        # Skip if we already have this interval stored
        existing = db.query(RealtimeLMP).filter(
            RealtimeLMP.datetime_beginning_utc == interval_start_utc,
            RealtimeLMP.pricing_node_id == PNODE_ID
        ).first()
        if existing:
            logger.debug(f"RT LMP for {interval_start_utc} already stored, skipping")
            return

        reading = RealtimeLMP(
            datetime_beginning_utc      = interval_start_utc,
            datetime_beginning_ept      = datetime.fromisoformat(data["datetime_beginning_ept"]),
            pricing_node_id             = int(data["pnode_id"]),
            pricing_node_name           = data.get("pnode_name") or "Unknown",
            pricing_node_type           = data.get("type") or "Unknown",
            voltage                     = data.get("voltage") or "N/A",
            equipment                   = data.get("equipment") or "N/A",
            transmission_zone           = data.get("transmission_zone") or "N/A",
            system_energy_price_rt      = data.get("mw_weighted_energy_price", data.get("system_energy_price_rt", 0)),
            total_lmp_rt                = data.get("total_lmp_rt", 0),
            congestion_price_rt         = data.get("congestion_price_rt", 0),
            marginal_loss_price_rt      = data.get("marginal_loss_price_rt", 0),
            # FIX: Provide defaults for mandatory DB fields that PJM left empty
            latest_version              = data.get("latest_version", True), 
            version_number              = data.get("version_nbr") or 1,
            valid_until                 = interval_start_utc + timedelta(minutes=5),
        )
        db.add(reading)
        db.commit()
        logger.info(f"Stored RT LMP: ${reading.total_lmp_rt:.2f}/MWh at {interval_start_utc}")

    except Exception:
        db.rollback()
        logger.exception("Failed to fetch real-time LMP")
    finally:
        db.close()


def fetch_and_store_da_lmp():
    """
    Fetches Day-Ahead hourly LMPs for the current + next 2 hours.
    This is your FUTURE PRICE signal — stable, published by 1pm day prior.
    Used to anticipate upcoming price spikes before they happen in RT.
    """
    db = SessionLocal()
    try:
        # PJM is extremely specific: Use EPT for BOTH filter and sort
        today_ept = datetime.now().strftime("%m/%d/%Y")
        
        items = _pjm_get("da_hrl_lmps", {
            "pnode_id": str(PNODE_ID),
            "datetime_beginning_ept": today_ept, 
            "sort": "datetime_beginning_ept", # UTC is not sortable here
            "order": "desc",
            "rowCount": 50
        })

        if not items:
            logger.warning("No DA LMP items returned from PJM")
            return

        stored_count = 0
        for data in items:
            interval_start_utc = datetime.fromisoformat(data["datetime_beginning_utc"]).replace(tzinfo=timezone.utc)

            existing = db.query(DayAheadLMP).filter(
                DayAheadLMP.datetime_beginning_utc == interval_start_utc,
                DayAheadLMP.pricing_node_id == PNODE_ID
            ).first()
            if existing:
                continue

            reading = DayAheadLMP(
                datetime_beginning_utc  = interval_start_utc,
                datetime_beginning_ept  = datetime.fromisoformat(data["datetime_beginning_ept"]),
                pricing_node_id         = int(data["pnode_id"]),
                pricing_node_name       = data.get("pnode_name") or "ATSI",
                # Provide defaults for mandatory DB columns not in DA feed:
                pricing_node_type       = data.get("type") or "HUB",
                voltage                 = data.get("voltage") or "N/A",
                equipment               = data.get("equipment") or "N/A",
                transmission_zone       = data.get("zone") or "N/A",
                total_lmp_da            = data.get("total_lmp_da", 0.0),
                system_energy_price_da  = data.get("system_energy_price_da", 0.0),
                congestion_price_da     = data.get("congestion_price_da", 0.0),
                marginal_loss_price_da  = data.get("marginal_loss_price_da", 0.0),
                latest_version          = True,
                version_number          = 1,
                valid_until             = interval_start_utc + timedelta(hours=1),
            )
            db.add(reading)
            stored_count += 1

        db.commit()
        logger.info(f"Stored {stored_count} DA LMP intervals")

    except Exception:
        db.rollback()
        logger.exception("Failed to fetch Day-Ahead LMP")
    finally:
        db.close()


def get_current_and_future_prices() -> dict:
    """
    Returns a clean price snapshot for the decision engine:
      - current_lmp:  latest RT price ($/MWh)
      - future_lmp:   DA price for next hour ($/MWh)
      - trend:        'rising', 'falling', or 'flat' based on last 3 RT readings
      - as_of_utc:    timestamp of the current RT reading
    """
    db = SessionLocal()

    result = {
        "current_lmp": None,
        "future_lmp":  None,
        "trend":       "unknown",
        "as_of_utc":   None,
    }

    try:
        # Current: most recent RT reading
        recent_rt = (
            db.query(RealtimeLMP)
            .filter(RealtimeLMP.pricing_node_id == PNODE_ID)
            .order_by(RealtimeLMP.datetime_beginning_utc.desc())
            .limit(3)
            .all()
        )
        if not recent_rt:
            logger.warning("No RT LMP data available in DB")
            return result

        result["current_lmp"] = recent_rt[0].total_lmp_rt
        result["as_of_utc"]   = recent_rt[0].datetime_beginning_utc

        # Trend: compare oldest to newest of last 3
        if len(recent_rt) >= 3:
            delta = recent_rt[0].total_lmp_rt - recent_rt[-1].total_lmp_rt
            if delta > 2:
                result["trend"] = "rising"
            elif delta < -2:
                result["trend"] = "falling"
            else:
                result["trend"] = "flat"
        else:
            result["trend"] = "unknown"

        # Future: DA LMP for the next full hour
        now_utc = datetime.now(timezone.utc)
        next_hour = now_utc.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        da_reading = (
            db.query(DayAheadLMP)
            .filter(
                DayAheadLMP.pricing_node_id == PNODE_ID,
                DayAheadLMP.datetime_beginning_utc == next_hour,
            )
            .first()
        )
        result["future_lmp"] = da_reading.total_lmp_da if da_reading else None

        # DEBUG
        print(f"current_lmp: {result['current_lmp']}")
        print(f"future_lmp: {result['future_lmp']}")
        print(f"trend: {result['trend']}")
        print(f"as_of_utc: {result['as_of_utc']}")

        return {
            "current_lmp": result["current_lmp"],
            "future_lmp":  result["future_lmp"],
            "trend":       result["trend"],
            "as_of_utc":   result["as_of_utc"],
        }

    finally:
        db.close()