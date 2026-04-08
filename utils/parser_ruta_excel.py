import pandas as pd
import math
import re


def limpiar(texto):
    if texto is None or (isinstance(texto, float) and math.isnan(texto)):
        return ""
    texto = str(texto).strip()
    return texto


def normalizar_domicilio(domicilio: str) -> str:
    d = limpiar(domicilio)

    reemplazos = [
        (r"(?i)^pje[\.\s]+", "Pasaje "),
        (r"(?i)^av[\.\s]+", "Avenida "),
    ]

    for patron, nuevo in reemplazos:
        d = re.sub(patron, nuevo, d)

    return d


def normalizar_localidad(localidad: str) -> str:
    return limpiar(localidad)


def extraer_paradas_ruta_excel(file_storage):
    df = pd.read_excel(file_storage, sheet_name=0)

    columnas = {str(c).strip().upper(): c for c in df.columns}

    col_hoja = columnas.get("HOJA_RUTA_NRO")
    col_cliente = columnas.get("CLIENTE_EXPRESO")
    col_domicilio = columnas.get("DROP_DOMICILIO")
    col_ciudad = columnas.get("DROP_CIUDAD")

    if not col_domicilio or not col_ciudad:
        raise ValueError("Faltan columnas DROP_DOMICILIO o DROP_CIUDAD")

    hoja_ruta_nro = None
    paradas = []
    vistos = set()

    for _, row in df.iterrows():

        direccion = normalizar_domicilio(row.get(col_domicilio))
        localidad = normalizar_localidad(row.get(col_ciudad))
        cliente = limpiar(row.get(col_cliente)) if col_cliente else "Cliente"

        if not direccion:
            continue

        if hoja_ruta_nro is None and col_hoja:
            hoja_ruta_nro = limpiar(row.get(col_hoja))

        key = f"{direccion}|{localidad}|{cliente}".lower()
        if key in vistos:
            continue
        vistos.add(key)

        paradas.append({
            "cliente": cliente,
            "direccion": direccion,
            "localidad": localidad,
            "remito": ""  # ← no existe en este formato
        })

    return hoja_ruta_nro, paradas
