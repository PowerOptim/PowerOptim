"""
IтscedLMP model for storing five minute ITSCED LMP data from PJM Data Miner 2
"""
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone, timedelta
from database.database import Base


class ItscedLMP(Base):
    """
    Five minute ITSCED (Intermediate Term Security Constrained Economic Dispatch)
    LMP data from PJM. Populated by the pricing service every 5 minutes.
    """
    __tablename__ = "itsced_lmp"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Case approval timestamps
    case_approval_datetime_utc = Column(DateTime, nullable=False)
    case_approval_datetime_ept = Column(DateTime, nullable=False)

    # Solution interval start timestamps
    datetime_beginning_utc = Column(DateTime, nullable=False, index=True)
    datetime_beginning_ept = Column(DateTime, nullable=False)

    # Node identification
    pnode_id = Column(Integer, nullable=False)
    pnode_name = Column(String, nullable=False)

    # Price components (USD/MWh)
    itsced_lmp = Column(Float, nullable=False)
    marginal_congestion_component = Column(Float, nullable=False)
    marginal_loss_component = Column(Float, nullable=False)

    # Cache control - set to datetime_beginning_utc + 5 minutes on insert
    valid_until = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))

    def __repr__(self):
        return f"<ItscedLMP(datetime={self.datetime_beginning_utc}, pnode={self.pnode_name}, lmp={self.itsced_lmp})>"
