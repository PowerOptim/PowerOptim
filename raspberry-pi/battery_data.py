import time
from smbus2 import SMBus

ADDR = 0x36

# Command Register
COMMAND_REG = 0x06
QUICKSTART_COMMAND = 0x4000  # 0x40 in MSB, 0x00 in LSB

def quick_start(bus):
    """Resets the ModelGauge algorithm to improve initial accuracy."""
    # We send 2 bytes (0x40 and 0x00) to the command register (0x06)
    bus.write_word_data(ADDR, COMMAND_REG, QUICKSTART_COMMAND)
    print("Sent QuickStart command to MAX17043...")

def read_battery_data(bus):
    # Read Voltage (Register 0x02 and 0x03)
    v_data = bus.read_i2c_block_data(ADDR, 0x02, 2)
    voltage = ((v_data[0] << 4) | (v_data[1] >> 4)) * 1.25 / 1000.0

    # Read State of Charge (Register 0x04 and 0x05)
    soc_data = bus.read_i2c_block_data(ADDR, 0x04, 2)
    soc = soc_data[0] + (soc_data[1] / 256.0)

    return voltage, soc

print("--- MAX17043 Battery Monitor ---")

try:
    with SMBus(1) as bus:
        # Run QuickStart once at the beginning
        quick_start(bus)
        time.sleep(0.5) # Give the chip a moment to stabilize

        while True:
            v, p = read_battery_data(bus)
            print(f"Voltage: {v:.2f}V | Charge: {p:.2f}%")
            time.sleep(0.5)
except KeyboardInterrupt:
    print("\nStopping monitor...")
except Exception as e:
    print(f"Error: {e}")
