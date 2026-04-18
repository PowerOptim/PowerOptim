"""
Heartbeat model for storing periodic system stats reported by the Raspberry Pi
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base


class PiStatus(Base):
    """
    A periodic system status report sent by the Raspberry Pi.
    The Pi POSTs one of these every few minutes with its current stats.
    """
    __tablename__ = "pi_status"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key - links to User table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamp - when this heartbeat was received
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Device identification
    device_id = Column(String, nullable=True)
    # e.g. "RPi-4B-A7F2"

    firmware = Column(String, nullable=True)
    # e.g. "v1.2.4"

    ip_address = Column(String, nullable=True)
    # e.g. "192.168.1.142"

    # System stats
    cpu_percent = Column(Float, nullable=True)
    # CPU usage percentage (0-100)

    memory_used_gb = Column(Float, nullable=True)
    # RAM used in GB (e.g. 1.2)

    memory_total_gb = Column(Float, nullable=True)
    # Total RAM in GB (e.g. 4.0)

    # Relationship back to User
    user = relationship("User", back_populates="pi_status")

    def __repr__(self):
        return f"<PiStatus(time={self.timestamp}, device={self.device_id}, cpu={self.cpu_percent}%)>"