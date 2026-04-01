import os
import requests

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

def geocodificar(direccion: str):
    if not API_KEY:
        raise ValueError("Falta la variable de entorno GOOGLE_MAPS_API_KEY")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": direccion,
        "key": API_KEY,
        "region": "ar",
        "language": "es"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    if data.get("status") == "OK" and data.get("results"):
        loc = data["results"][0]["geometry"]["location"]
        return (loc["lat"], loc["lng"])

    return None
