"""
Decision service - determines whether the Pi should switch power sources.
Currently a placeholder - will use real battery data + pricing API in the future.
"""


def get_pending_command(g_now: float, g_future: float, b_charge: float) -> dict:
    """
    Decides what command to send to the Raspberry Pi.

    Returns a dict with:
        command: "switch_to_battery" | "switch_to_grid"
        reason:  plain english reason for the command
    """
    battery = {"command": "switch_to_battery", "reason": "Using battery while price is relatively high"}
    grid    = {"command": "switch_to_grid", "reason": "Charging battery for upcoming higher price"}
    grid_no_battery = {"command": "switch_to_grid", "reason": "Battery empty, falling back to grid"}
    
    # the future is more expensive, so use the grid now and charge battery
    if g_future > g_now:
        return grid
    
    # the future is cheaper. discharge now if possible
    return battery if b_charge > 0 else grid_no_battery