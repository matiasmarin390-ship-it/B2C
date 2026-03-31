import math

def distancia(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def optimizar_ruta(origen, puntos):
    ruta = []
    actual = origen
    total_dist = 0

    puntos_copy = puntos.copy()

    while puntos_copy:
        siguiente = min(puntos_copy, key=lambda x: distancia(actual, x["coords"]))
        ruta.append(siguiente)
        total_dist += distancia(actual, siguiente["coords"])
        actual = siguiente["coords"]
        puntos_copy.remove(siguiente)

    tiempo_estimado = total_dist * 2  # simplificado

    return ruta, round(total_dist,2), round(tiempo_estimado,2)

def generar_link_maps(origen, ruta):
    base = "https://www.google.com/maps/dir/?api=1"

    waypoints = "|".join([r["direccion"] for r in ruta])

    link = f"{base}&origin={origen[0]},{origen[1]}&destination={ruta[-1]['direccion']}&waypoints={waypoints}"

    return link
