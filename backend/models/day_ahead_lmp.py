"""
DayAheadLMP model for storing day-ahead hourly LMP data from PJM Data Miner 2
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime, timezone, timedelta
from database.database import Base


class DayAheadLMP(Base):
    """
    Day-ahead hourly LMP data from PJM.
    Populated by the pricing service hourly.
    """
    __tablename__ = "day_ahead_lmp"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Datetime fields from PJM
    datetime_beginning_utc = Column(DateTime, nullable=False, index=True)
    datetime_beginning_ept = Column(DateTime, nullable=False)

    # Node identification
    pricing_node_id = Column(Integer, nullable=False)
    pricing_node_name = Column(String, nullable=False)
    pricing_node_type = Column(String, nullable=False)

    # Equipment and location info
    voltage = Column(String, nullable=False)
    equipment = Column(String, nullable=False)
    transmission_zone = Column(String, nullable=False)

    # Price components (USD/MWh)
    system_energy_price_da = Column(Float, nullable=False)
    total_lmp_da = Column(Float, nullable=False)
    congestion_price_da = Column(Float, nullable=False)
    marginal_loss_price_da = Column(Float, nullable=False)

    # Versioning
    latest_version = Column(Boolean, nullable=False)
    version_number = Column(Integer, nullable=False)

    # Cache control - set to 1 hour after insert since day-ahead updates hourly
    valid_until = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(hours=1))

    def __repr__(self):
        return f"<DayAheadLMP(datetime={self.datetime_beginning_utc}, node={self.pricing_node_name}, lmp={self.total_lmp_da})>"