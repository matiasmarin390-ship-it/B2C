import re


def normalizar_texto(txt):
    if not txt:
        return ""

    txt = str(txt).lower()
    txt = txt.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    txt = txt.replace(".", " ").replace(",", " ").replace(";", " ").replace(":", " ").replace("-", " ")
    txt = " ".join(txt.split())
    return txt.strip()


def link_google_maps_coords(lat, lon):
    return f"https://www.google.com/maps?q={lat},{lon}"


def extraer_numero(direccion):
    match = re.search(r"\b(\d{1,6})\b", direccion or "")
    return match.group(1) if match else ""


def extraer_calle_base(direccion):
    texto = normalizar_texto(direccion)

    remover = {"calle", "avenida", "av", "pasaje", "pje", "sn", "s/n"}
    tokens = [t for t in texto.split() if t not in remover and not t.isdigit()]

    return " ".join(tokens[:4]).strip()


def score_match(parada, evento):
    direccion = parada.get("direccion", "")
    localidad = parada.get("localidad", "")

    calle = extraer_calle_base(direccion)
    numero = extraer_numero(direccion)
    localidad_norm = normalizar_texto(localidad)

    texto_evento = " ".join([
        normalizar_texto(evento.get("ubicacion", "")),
        normalizar_texto(evento.get("punto_cercano", "")),
        normalizar_texto(evento.get("direccion_inferida", "")),
        normalizar_texto(evento.get("evento", "")),
    ]).strip()

    if not texto_evento:
        return 0

    score = 0

    if calle:
        partes_calle = calle.split()
        coincidencias = sum(1 for p in partes_calle if p in texto_evento)
        score += coincidencias * 3

        if calle in texto_evento:
            score += 4

    if numero and numero in texto_evento:
        score += 4

    if localidad_norm and localidad_norm in texto_evento:
        score += 3

    return score


def buscar_evento_mas_relevante(parada, eventos):
    mejor = None
    mejor_score = 0

    for evento in eventos:
        score = score_match(parada, evento)
        if score > mejor_score:
            mejor_score = score
            mejor = evento

    return mejor, mejor_score


def procesar_cruce_completo(hoja_ruta_nro, paradas, eventos):
    eventos_procesados = []

    for ev in eventos:
        lat, lon = ev["coordenadas"]
        item = dict(ev)
        item["link_mapa"] = link_google_maps_coords(lat, lon)
        eventos_procesados.append(item)

    paradas_procesadas = []
    cumplidos = 0
    no_cumplidos = 0

    for idx, parada in enumerate(paradas, start=1):
        item = dict(parada)
        item["orden"] = idx

        evento, score = buscar_evento_mas_relevante(item, eventos_procesados)

        item["evento_mas_cercano"] = evento
        item["score"] = score

        if evento and score >= 4:
            item["estado"] = "Cumplido"
            cumplidos += 1
        else:
            item["estado"] = "No cumplido"
            no_cumplidos += 1

        paradas_procesadas.append(item)

    resumen = {
        "hoja_ruta_nro": hoja_ruta_nro,
        "total_paradas": len(paradas_procesadas),
        "total_eventos": len(eventos_procesados),
        "cumplidos": cumplidos,
        "no_cumplidos": no_cumplidos,
    }

    return resumen, paradas_procesadas, eventos_procesados
