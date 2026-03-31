import math
from urllib.parse import quote

# Coordenadas aproximadas por barrio/localidad
ZONAS = {
    "La Boca": (-34.6347, -58.3648),
    "Capital Federal": (-34.6037, -58.3816),
    "San Cristóbal": (-34.6220, -58.4008),
    "San Cristobal": (-34.6220, -58.4008),
    "Almagro": (-34.6098, -58.4219),
    "Villa Santa Rit": (-34.6200, -58.4900),
    "Villa Santa Rita": (-34.6200, -58.4900),
    "Villa Crespo": (-34.5990, -58.4370),
    "Parque Chas": (-34.5878, -58.4846),
    "Belgrano": (-34.5621, -58.4563),
    "Flores": (-34.6283, -58.4630),
    "Velez Sarsfield": (-34.6328, -58.4928),
    "Vélez Sarsfield": (-34.6328, -58.4928),
    "Caballito": (-34.6186, -58.4424),
    "Devoto": (-34.6026, -58.5107),
    "Ciudad Autónoma": (-34.6037, -58.3816),
    "Ciudad Autonoma": (-34.6037, -58.3816),
    "Palermo": (-34.5733, -58.4300),
    "CABA": (-34.6037, -58.3816),
}

def haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    y = 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))
    return r * y

def coords_de_parada(parada):
    return ZONAS.get(parada.get("localidad"), ZONAS["CABA"])

def generar_link_individual(texto):
    return f"https://www.google.com/maps/search/?api=1&query={quote(texto)}"

def optimizar_ruta_basica(origen_coords, paradas):
    pendientes = []
    for p in paradas:
        item = dict(p)
        item["coords"] = coords_de_parada(item)
        pendientes.append(item)

    ruta = []
    actual = origen_coords
    distancia_total = 0.0

    while pendientes:
        siguiente = min(pendientes, key=lambda x: haversine_km(actual, x["coords"]))
        tramo = haversine_km(actual, siguiente["coords"])
        distancia_total += tramo

        siguiente["distancia_desde_anterior_km"] = round(tramo, 2)
        siguiente["link_individual"] = generar_link_individual(siguiente["direccion_mapa"])
        ruta.append(siguiente)

        actual = siguiente["coords"]
        pendientes.remove(siguiente)

    for i, p in enumerate(ruta, start=1):
        p["orden"] = i

    # velocidad urbana básica de camión
    tiempo_total_min = round((distancia_total / 25) * 60) if distancia_total > 0 else 0

    return ruta, round(distancia_total, 2), tiempo_total_min

def generar_link_maps(origen_texto, ruta):
    if not ruta:
        return None

    destino = ruta[-1]["direccion_mapa"]
    intermedios = [r["direccion_mapa"] for r in ruta[:-1]]

    url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={quote(origen_texto)}"
        f"&destination={quote(destino)}"
        f"&travelmode=driving"
    )

    if intermedios:
        url += f"&waypoints={quote('|'.join(intermedios))}"

    return url
