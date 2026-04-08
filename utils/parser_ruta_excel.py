import pandas as pd
import math


def limpiar(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return str(x).strip()


def extraer_paradas_ruta_excel(file):
    df = pd.read_excel(file)

    hoja = limpiar(df.iloc[0].get("HOJA_RUTA_NRO", ""))

    paradas = []
    vistos = set()

    for _, row in df.iterrows():
        direccion = limpiar(row.get("DROP_DOMICILIO"))
        ciudad = limpiar(row.get("DROP_CIUDAD"))
        cliente = limpiar(row.get("CLIENTE_EXPRESO"))

        if not direccion:
            continue

        key = f"{direccion}|{ciudad}|{cliente}"
        if key in vistos:
            continue
        vistos.add(key)

        paradas.append({
            "cliente": cliente,
            "direccion": direccion,
            "localidad": ciudad,
            "remito": ""
        })

    return hoja, paradas
