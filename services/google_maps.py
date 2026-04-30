import requests
from config import GOOGLE_MAPS_API_KEY

def validate_address(state):
    if not GOOGLE_MAPS_API_KEY:
        return True  # fallback for dev

    address = f"{state['street']}, {state['city']}, {state['state']} {state['zip_code']}"

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}

    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        return data["status"] == "OK"
    except:
        return False