##################################################

#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3

##################################################
#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
from smbus2 import SMBus
import time
from pi_endpoints import send_reading, get_switch_decision, confirm_switch

BASE_URL = "http://3.19.232.240:8000/api/pi"
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

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

print("Setup The Relay Module is [success]")

try:
	with SMBus(1) as bus:
		# Run QuickStart once at the beginning
		quick_start(bus)
		time.sleep(0.5) # Give the chip a moment to stabilize
		pwr_source = "grid"
		print("entering pwr source loop")
		while True:
			voltage, level = read_battery_data(bus)
			battery_info = {
				"battery_level": int(level), 
				"power_source": str(pwr_source), 
				"voltage": voltage,
				"current": None,
				"temperature": None
				}
			print("sending first API")
			print(battery_info)
			send_reading(BASE_URL, battery_info)
			print("API 1 sent")
			switch = get_switch_decision(BASE_URL)
			print("API 2 sent")
			if switch["command"] == "switch_to_grid":
				GPIO.output(Relay_Ch3,GPIO.HIGH)
				GPIO.output(Relay_Ch1,GPIO.LOW)
				GPIO.output(Relay_Ch2,GPIO.LOW)
				confirm_switch(BASE_URL, switch)
				print("API 3 sent")
				pwr_source = "grid"
				
			elif switch["command"] == "switch_to_battery":
				GPIO.output(Relay_Ch1,GPIO.HIGH)
				GPIO.output(Relay_Ch2,GPIO.HIGH)
				GPIO.output(Relay_Ch3,GPIO.LOW)
				confirm_switch(BASE_URL, switch)
				print("API 4 sent")
				pwr_source = "battery"
			print("sleeping 10 secs")
			time.sleep(10)
except KeyboardInterrupt:
    print("\nStopping monitor...")
    GPIO.output(Relay_Ch1,GPIO.HIGH)
    GPIO.output(Relay_Ch2,GPIO.HIGH)
    GPIO.output(Relay_Ch3,GPIO.HIGH)
except Exception as e:
	print(e)
	GPIO.cleanup()


#Control the Channel 1
		# GPIO.output(Relay_Ch1,GPIO.LOW)
		# print("Channel 1:The Common Contact is access to the Normal Open Contact!")
		# time.sleep(5)
	
		# GPIO.output(Relay_Ch1,GPIO.HIGH)
		# print("Channel 1:The Common Contact is access to the Normal Closed Contact!\n")
		# time.sleep(0.5)

		#Control the Channel 2
		# GPIO.output(Relay_Ch2,GPIO.LOW)
		# print("Channel 2:The Common Contact is access to the Normal Open Contact!")
		# time.sleep(5)
		
		# GPIO.output(Relay_Ch2,GPIO.HIGH)
		# print("Channel 2:The Common Contact is access to the Normal Closed Contact!\n")
		# time.sleep(0.5)

		#Control the Channel 3
		#GPIO.output(Relay_Ch3,GPIO.LOW)
		#print("Channel 3:The Common Contact is access to the Normal Open Contact!")
		#time.sleep(0.5)
		
		#GPIO.output(Relay_Ch3,GPIO.HIGH)
		#print("Channel 3:The Common Contact is access to the Normal Closed Contact!\n")
		#time.sleep(0.5)
		
