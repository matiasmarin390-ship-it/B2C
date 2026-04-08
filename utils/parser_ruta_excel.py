import pandas as pd
import math
import re


def limpiar(texto):
    if texto is None or (isinstance(texto, float) and math.isnan(texto)):
        return ""
    return str(texto).strip()


def normalizar_domicilio(domicilio: str) -> str:
    d = limpiar(domicilio)

    reemplazos = [
        (r"(?i)^pje[\.\s]+", "Pasaje "),
        (r"(?i)^av[\.\s]+", "Avenida "),
        (r"(?i)^av\.", "Avenida "),
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
    col_documentos = columnas.get("DOCUMENTOS")

    if not col_domicilio or not col_ciudad:
        raise ValueError("El Excel de hoja de ruta debe tener las columnas DROP_DOMICILIO y DROP_CIUDAD.")

    hoja_ruta_nro = None
    paradas = []
    vistos = set()

    for _, row in df.iterrows():
        cliente = limpiar(row.get(col_cliente)) if col_cliente else "Cliente"
        direccion = normalizar_domicilio(row.get(col_domicilio))
        localidad = normalizar_localidad(row.get(col_ciudad))
        remito = limpiar(row.get(col_documentos)) if col_documentos else ""

        if not direccion:
            continue

        if not localidad:
            localidad = "Sin localidad"

        if hoja_ruta_nro is None and col_hoja:
            hoja_ruta_nro = limpiar(row.get(col_hoja))

        key = f"{direccion}|{localidad}|{cliente}|{remito}".lower()
        if key in vistos:
            continue
        vistos.add(key)

        paradas.append({
            "cliente": cliente or "Cliente",
            "direccion": direccion,
            "localidad": localidad,
            "remito": remito
        })

    return hoja_ruta_nro, paradas
