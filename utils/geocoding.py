import requests

API_KEY = "TU_API_KEY"

def geocodificar(direccion):
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": direccion,
        "key": API_KEY
    }

    res = requests.get(url, params=params).json()

    if res["status"] == "OK":
        loc = res["results"][0]["geometry"]["location"]
        return (loc["lat"], loc["lng"])

    return None
