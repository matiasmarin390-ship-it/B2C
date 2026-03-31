import math
from urllib.parse import quote

def haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b

    r = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    x = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    y = 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))

    return r * y

def optimizar_ruta(origen, puntos):
    if not origen or not puntos:
        return [], 0, 0

    pendientes = puntos.copy()
    ruta = []
    actual = origen
    distancia_total = 0.0

    while pendientes:
        siguiente = min(pendientes, key=lambda p: haversine_km(actual, p["coords"]))
        tramo = haversine_km(actual, siguiente["coords"])
        distancia_total += tramo

        siguiente["distancia_desde_anterior_km"] = round(tramo, 2)
        ruta.append(siguiente)

        actual = siguiente["coords"]
        pendientes.remove(siguiente)

    # estimación simple de tiempo de camión urbano
    # promedio conservador 25 km/h
    tiempo_total_horas = distancia_total / 25 if distancia_total > 0 else 0
    tiempo_total_min = round(tiempo_total_horas * 60)

    return ruta, round(distancia_total, 2), tiempo_total_min

def generar_link_maps(origen, ruta):
    if not origen or not ruta:
        return None

    origin = f"{origen[0]},{origen[1]}"
    destination = f"{ruta[-1]['coords'][0]},{ruta[-1]['coords'][1]}"

    intermedios = ruta[:-1]
    waypoints = "|".join([f"{p['coords'][0]},{p['coords'][1]}" for p in intermedios])

    base = "https://www.google.com/maps/dir/?api=1"
    url = f"{base}&origin={quote(origin)}&destination={quote(destination)}&travelmode=driving"

    if waypoints:
        url += f"&waypoints={quote(waypoints)}"

    return url

def generar_link_individual(direccion: str):
    if not direccion:
        return None
    return f"https://www.google.com/maps/search/?api=1&query={quote(direccion)}"

def enriquecer_ruta_con_links(ruta):
    for i, punto in enumerate(ruta, start=1):
        punto["orden"] = i
        punto["link_individual"] = generar_link_individual(punto["direccion"])
    return ruta
