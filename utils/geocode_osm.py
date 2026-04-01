import time
from functools import lru_cache
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="rt_auditoria_hojas_ruta")


def variantes_direccion(direccion: str, localidad: str):
    base = (direccion or "").strip()
    loc = (localidad or "").strip()

    variantes = []

    # original
    variantes.append(f"{base}, {loc}, Buenos Aires, Argentina")

    # sin localidad exacta, con provincia
    variantes.append(f"{base}, Buenos Aires, Argentina")

    # reemplazos comunes
    reemplazos = [
        ("Pasaje ", "Pje. "),
        ("Pje. ", "Pasaje "),
        ("Avenida ", "Av. "),
        ("Av. ", "Avenida "),
        ("Calle ", ""),
    ]

    for viejo, nuevo in reemplazos:
        if viejo in base:
            variantes.append(f"{base.replace(viejo, nuevo)}, {loc}, Buenos Aires, Argentina")
            variantes.append(f"{base.replace(viejo, nuevo)}, Buenos Aires, Argentina")

    # si no empieza con calle/avenida/pasaje, intentar con Calle
    lower = base.lower()
    if not lower.startswith(("calle ", "avenida ", "av. ", "pasaje ", "pje. ", "pje ")):
        variantes.append(f"Calle {base}, {loc}, Buenos Aires, Argentina")

    # deduplicar
    unicas = []
    vistos = set()
    for v in variantes:
        k = v.lower().strip()
        if k not in vistos:
            vistos.add(k)
            unicas.append(v)
    return unicas


@lru_cache(maxsize=1000)
def geocodificar_texto(q: str):
    try:
        time.sleep(1)  # respetar Nominatim
        loc = geolocator.geocode(q, exactly_one=True, timeout=15, country_codes="ar")
        if not loc:
            return None
        return (loc.latitude, loc.longitude, loc.address)
    except Exception:
        return None


def geocodificar_direccion(direccion: str, localidad: str):
    for consulta in variantes_direccion(direccion, localidad):
        res = geocodificar_texto(consulta)
        if res:
            lat, lon, address = res
            return {
                "lat": lat,
                "lon": lon,
                "address": address,
                "consulta_usada": consulta
            }
    return None
