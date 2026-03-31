from urllib.parse import quote

def optimizar_ruta(origen, direcciones):
    # No optimizamos, dejamos el orden como viene del PDF
    ruta = []

    for i, d in enumerate(direcciones, start=1):
        ruta.append({
            "orden": i,
            "direccion": d,
            "link_individual": f"https://www.google.com/maps/search/?api=1&query={quote(d)}"
        })

    distancia_total = "N/A"
    tiempo_total = "N/A"

    return ruta, distancia_total, tiempo_total


def generar_link_maps(origen, direcciones):
    if not direcciones:
        return None

    origin = quote(origen)
    destination = quote(direcciones[-1])

    waypoints = "|".join([quote(d) for d in direcciones[:-1]])

    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"

    if waypoints:
        url += f"&waypoints={waypoints}"

    return url
