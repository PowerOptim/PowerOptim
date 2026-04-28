import requests
import threading
import time

BASE_URL = "http://3.19.232.240:8000"


# Send every 10 seconds
def send_reading():
    while True:
        try:
            # Won't wait for this to finish
            requests.post("https://example.com", json={"key": "value"})
        except requests.exceptions.RequestException:
            pass

        time.sleep(10)


def get_switch_decision():
    return None


def confirm_switch():
    return None


if __name__ == "__main__":
    thread = threading.Thread(
        target=send_reading, kwargs={
            "url": str(BASE_URL), 
            "battery_level": battery_level, 
            "power_source": power_source, 
            "voltage": voltage, 
            "current": current, 
            "temperature": temperature
        }
    )  
    thread.start()


  
