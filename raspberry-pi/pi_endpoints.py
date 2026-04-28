import requests
import threading
import time

BASE_URL = "http://3.19.232.240:8000"


# Send every 10 seconds
def send_reading(url: str, info: dict) -> None:
    while True:
        try:
            # Won't wait for this to finish
            requests.post(url, info)
        except requests.exceptions.RequestException:
            pass

        time.sleep(10)


# gets called every 10 seconds
def get_switch_decision(url: str) -> dict:
    return requests.get(url)


# called after get_decision_switch returns data
def confirm_switch(url: str, obj: dict) -> dict:
    return requests.post(url, obj)
