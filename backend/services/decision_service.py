"""
Decision service - determines whether the Pi should switch power sources.
Currently a placeholder - will use real battery data + pricing API in the future.
"""


def get_pending_command() -> dict:
    """
    Decides what command to send to the Raspberry Pi.

    Returns a dict with:
        command: "none" | "switch_to_battery" | "switch_to_grid"
        reason:  plain english reason for the command, or None

    TODO: Replace hardcoded return with real logic:
        1. Fetch latest battery level from sensor_readings table
        2. Fetch current electricity price from pricing_service
        3. If price is high AND battery is charged enough → switch to battery
        4. If battery is low → switch back to grid
    """
    return {"command": "none", "reason": None}