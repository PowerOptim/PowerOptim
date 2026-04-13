import os
import requests
from datetime import datetime, timezone, timedelta
from database.database import SessionLocal
from models.realtime_lmp import RealtimeLMP
from models.itsced_lmp import ItscedLMP
from utils import get_logger

logger = get_logger(__name__)

PJM_API_KEY = os.getenv("PJM_API_KEY")
PNODE_ID    = os.getenv("PNODE_ID")

if not PJM_API_KEY or not PNODE_ID:
    raise RuntimeError("PJM_API_KEY and PNODE_ID must be configured")

HEADERS = {"Ocp-Apim-Subscription-Key": PJM_API_KEY}


def fetch_and_store_realtime_lmp():
    """Fetches current real-time 5-min LMP from PJM and saves to DB"""
    db = SessionLocal()
    try:
        response = requests.get(
            "https://api.pjm.com/api/v1/rt_unverified_fivemin_lmps",
            params={"pnode_id": PNODE_ID, "format": "json"},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("items") or []
        if not items:
            raise ValueError("PJM returned no realtime LMP items")
        data = items[0]

        interval_start_utc = datetime.fromisoformat(data["datetime_beginning_utc"])
        reading = RealtimeLMP(
            datetime_beginning_utc      = interval_start_utc,
            datetime_beginning_ept      = datetime.fromisoformat(data["datetime_beginning_ept"]),
            pricing_node_id             = data["pnode_id"],
            pricing_node_name           = data["pnode_name"],
            pricing_node_type           = data["pnode_type"],
            voltage                     = data["voltage"],
            equipment                   = data["equipment"],
            transmission_zone           = data["transmission_zone"],
            system_energy_price_rt      = data["system_energy_price_rt"],
            total_lmp_rt                = data["total_lmp_rt"],
            congestion_price_rt         = data["congestion_price_rt"],
            marginal_loss_price_rt      = data["marginal_loss_price_rt"],
            latest_version              = data["latest_version"],
            version_number              = data["version_nbr"],
            valid_until                 = interval_start_utc + timedelta(minutes=5)
        )
        db.add(reading)
        db.commit()
        logger.info(f"Stored real-time LMP: ${reading.total_lmp_rt}/MWh")
    except Exception:
        db.rollback()
        logger.exception("Failed to fetch real-time LMP")
    finally:
        db.close()


def fetch_and_store_itsced_lmp():
    """Fetches future ITSCED LMP from PJM and saves to DB"""
    db = SessionLocal()
    try:
        response = requests.get(
            "https://api.pjm.com/api/v1/itsced_lmps",
            params={"pnode_id": PNODE_ID, "format": "json"},
            headers=HEADERS
        )
        data = response.json()["items"][0]

        interval_start_utc = datetime.fromisoformat(data["datetime_beginning_utc"])
        reading = ItscedLMP(
            case_approval_datetime_utc  = datetime.fromisoformat(data["case_approval_datetime_utc"]),
            case_approval_datetime_ept  = datetime.fromisoformat(data["case_approval_datetime_ept"]),
            datetime_beginning_utc      = interval_start_utc,
            datetime_beginning_ept      = datetime.fromisoformat(data["datetime_beginning_ept"]),
            pnode_id                    = data["pnode_id"],
            pnode_name                  = data["pnode_name"],
            itsced_lmp                  = data["itsced_lmp"],
            marginal_congestion_component = data["marginal_congestion_component"],
            marginal_loss_component     = data["marginal_loss_component"],
            valid_until                 = interval_start_utc + timedelta(minutes=5)
        )
        db.add(reading)
        db.commit()
        logger.info(f"Stored ITSCED LMP: ${reading.itsced_lmp}/MWh")
    except Exception:
        db.rollback()
        logger.exception("Failed to fetch ITSCED LMP")
    finally:
        db.close()