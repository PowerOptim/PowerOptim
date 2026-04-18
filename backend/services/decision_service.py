"""
Decision service - determines whether the Pi should switch power sources.
Currently a placeholder - will use real battery data + pricing API in the future.
"""


def get_pending_command(g_now: float | None, g_future: float | None, b_charge: float | None) -> dict:
    """
    Decides what command to send to the Raspberry Pi.

    Returns a dict with:
        command: "switch_to_battery" | "switch_to_grid"
        reason:  plain english reason for the command
    """
    battery = {"command": "switch_to_battery", "reason": "Using battery while price is relatively high"}
    grid    = {"command": "switch_to_grid", "reason": "Charging battery for upcoming higher price"}
    grid_no_battery  = {"command": "switch_to_grid", "reason": "Battery empty, falling back to grid"}
    grid_with_gerror  = {"command": "switch_to_grid", "reason": "ERROR (grid): Price data unavailable, defaulting to grid"}
    grid_with_berror = {"command": "switch_to_grid", "reason": "ERROR (battery): Battery charge unknown, defaulting to grid"}

    if g_now is None or g_future is None:
        return grid_with_gerror

    if b_charge is None:
        return grid_with_berror

    # the future is more expensive, so use the grid now and charge battery
    if g_future >= g_now:
        return grid
    
    # the future is cheaper, so discharge now if possible
    return battery if b_charge > 0 else grid_no_battery