"""
SwitchEvent model for logging every power source switch confirmed by the Pi
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base


class SwitchEvent(Base):
    """
    A log entry for every time the Pi confirms it switched power sources.
    Powers the recent activity feed on the dashboard.
    """
    __tablename__ = "switch_events"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key - links to User table 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamp - when the switch was confirmed
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # What the Pi switched to
    switched_to = Column(String, nullable=False)
    # Values: "battery" or "grid"

    # Why the switch happened - echoed back from the pending-command response
    reason = Column(String, nullable=True)
    # e.g. "high price", "low battery", or None if not yet implemented

    # Relationship back to User
    user = relationship("User", back_populates="switch_events")

    def __repr__(self):
        return f"<SwitchEvent(time={self.timestamp}, switched_to={self.switched_to}, reason={self.reason})>"