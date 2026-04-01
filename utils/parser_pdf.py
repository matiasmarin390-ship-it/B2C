import pdfplumber
import re
from collections import defaultdict


def limpiar(texto: str) -> str:
    texto = (texto or "").replace("\xa0", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def extraer_nro_hoja(texto: str):
    m = re.search(r"Impresi[oó]n de Hoja de Ruta Nro\.\s*:\s*(\d+)", texto, re.IGNORECASE)
    return m.group(1) if m else None


def agrupar_por_linea(words, tolerancia=3):
    lineas = defaultdict(list)
    for w in words:
        top_key = round(w["top"] / tolerancia) * tolerancia
        lineas[top_key].append(w)

    resultado = []
    for _, items in sorted(lineas.items(), key=lambda x: x[0]):
        resultado.append(sorted(items, key=lambda x: x["x0"]))
    return resultado


def texto_en_rango(words, x_min, x_max):
    partes = [w["text"] for w in words if w["x0"] >= x_min and w["x0"] < x_max]
    return limpiar(" ".join(partes))


def normalizar_localidad(localidad: str) -> str:
    loc = limpiar(localidad)

    reemplazos = {
        "CAPITAL FEDERAL": "Capital Federal",
        "Ciudad Autónoma": "Ciudad Autónoma",
        "Velez Sarsfield": "Vélez Sarsfield",
        "San Cristobal": "San Cristóbal",
        "Villa Santa Rit": "Villa Santa Rita",
        "Jose Clemente P": "José C. Paz",
        "Jose C. Paz": "José C. Paz",
    }
    return reemplazos.get(loc, loc)


def normalizar_domicilio(domicilio: str) -> str:
    d = limpiar(domicilio)

    reemplazos = [
        (r"(?i)^pje[\.\s]+", "Pasaje "),
        (r"(?i)^av[\.\s]+", "Avenida "),
        (r"(?i)^av\.", "Avenida "),
    ]
    for patron, nuevo in reemplazos:
        d = re.sub(patron, nuevo, d)

    return limpiar(d)


def es_fila_datos(cliente, domicilio, localidad):
    if not domicilio:
        return False

    bloqueados = [
        "Cliente/Expreso", "Domicilio", "Localidad", "Documentos", "COT",
        "Cant.", "Remito", "Novedades", "m3 Total Viaje", "Total Documentos",
        "CHOFER", "Firma:", "Aclaración:", "SALIDA", "ARRIBO",
        "CONTROLADOR", "OBSERVACIONES", "IMPORTANTE"
    ]

    todo = f"{cliente} {domicilio} {localidad}".lower()
    for b in bloqueados:
        if b.lower() in todo:
            return False

    return bool(re.search(r"\d", domicilio))


def extraer_paradas_pdf(file_storage):
    nro_hoja = None
    paradas = []
    vistos = set()

    with pdfplumber.open(file_storage) as pdf:
        texto_total = []
        for page in pdf.pages:
            texto_total.append(page.extract_text() or "")
        nro_hoja = extraer_nro_hoja("\n".join(texto_total))

        for page in pdf.pages:
            words = page.extract_words(
                x_tolerance=2,
                y_tolerance=2,
                keep_blank_chars=False,
                use_text_flow=True
            )
            if not words:
                continue

            ancho = page.width

            x_cliente_min = 0
            x_cliente_max = ancho * 0.28

            x_domicilio_min = ancho * 0.28
            x_domicilio_max = ancho * 0.56

            x_localidad_min = ancho * 0.56
            x_localidad_max = ancho * 0.72

            lineas = agrupar_por_linea(words, tolerancia=3)

            dentro_tabla = False

            for linea_words in lineas:
                texto_linea = limpiar(" ".join(w["text"] for w in linea_words))

                if "Cliente/Expreso" in texto_linea and "Domicilio" in texto_linea and "Localidad" in texto_linea:
                    dentro_tabla = True
                    continue

                if not dentro_tabla:
                    continue

                if "m3 Total Viaje" in texto_linea or "Total Documentos" in texto_linea:
                    break

                cliente = texto_en_rango(linea_words, x_cliente_min, x_cliente_max)
                domicilio = texto_en_rango(linea_words, x_domicilio_min, x_domicilio_max)
                localidad = texto_en_rango(linea_words, x_localidad_min, x_localidad_max)

                domicilio = normalizar_domicilio(domicilio)
                localidad = normalizar_localidad(localidad)

                if not es_fila_datos(cliente, domicilio, localidad):
                    continue

                direccion_mapa = f"{domicilio}, {localidad}, Buenos Aires, Argentina"
                key = direccion_mapa.lower()

                if key in vistos:
                    continue
                vistos.add(key)

                paradas.append({
                    "cliente": cliente or "Cliente",
                    "direccion": domicilio,
                    "localidad": localidad,
                    "direccion_mapa": direccion_mapa
                })

    return nro_hoja, paradas
