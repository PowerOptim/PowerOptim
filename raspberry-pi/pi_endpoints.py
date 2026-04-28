import requests
import threading
import time

# BASE_URL = "http://3.19.232.240:8000"


# Send every 10 seconds
def send_reading(url: str, info: dict) -> None:
    endpoint = url + "/readings"
    while True:
        try:
            requests.post(endpoint, json=info, timeout=5)
        except requests.exceptions.RequestException:
            pass

        time.sleep(10)


# gets called every 10 seconds
def get_switch_decision(url: str) -> dict | None:
    endpoint = url + "/pending-command"
    try:
        response = requests.get(endpoint, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


# called after get_decision_switch returns data
def confirm_switch(url: str, obj: dict) -> dict | None:
    endpoint = url + "/confirm-switch"
    try:
        response = requests.post(endpoint, json=obj, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None
