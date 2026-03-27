"""
Schema for switch event data validation.
Defines what the Pi sends when confirming a power source switch.
"""
from pydantic import BaseModel
from typing import Optional


class SwitchEventCreate(BaseModel):
    """
    Data the Raspberry Pi sends when confirming it switched power sources.
    switched_to is required, reason is echoed back from the pending-command response.
    """
    switched_to: str
    # Values: "battery" or "grid"

    reason: Optional[str] = None
    # Echoed back from GET /api/pi/pending-command/ response