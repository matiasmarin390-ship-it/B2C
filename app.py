import os
from flask import Flask, render_template, request

from utils.parser import extraer_paradas_y_hoja
from utils.optimizer import optimizar_ruta_basica, generar_link_maps

app = Flask(__name__)

DEPOSITOS = {
    "monte_chingolo": {
        "nombre": "Monte Chingolo, Buenos Aires, Argentina",
        "coords": (-34.7174, -58.3732),
    },
    "roque_perez": {
        "nombre": "ROQUE PEREZ 3650, Saavedra, Buenos Aires, Argentina",
        "coords": (-34.5520, -58.4872),
    }
}


def construir_respuesta(deposito_key, nro_hoja, paradas, error=None):
    deposito = DEPOSITOS[deposito_key]

    ruta, distancia_total_km, tiempo_total_min = optimizar_ruta_basica(
        deposito["coords"],
        paradas
    )

    link_maps = generar_link_maps(deposito["nombre"], ruta)

    return render_template(
        "index.html",
        deposito_key=deposito_key,
        deposito=deposito["nombre"],
        nro_hoja=nro_hoja,
        ruta=ruta,
        paradas_editables=paradas,
        distancia=distancia_total_km,
        tiempo=tiempo_total_min,
        link=link_maps,
        error=error
    )


@app.route("/health")
def health():
    return "OK", 200


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "index.html",
            deposito_key=None,
            deposito=None,
            nro_hoja=None,
            ruta=None,
            paradas_editables=None,
            distancia=None,
            tiempo=None,
            link=None,
            error=None
        )

    try:
        accion = request.form.get("accion", "subir")

        if accion == "subir":
            deposito_key = request.form.get("deposito")
            archivo = request.files.get("file")

            if not deposito_key or deposito_key not in DEPOSITOS:
                return render_template(
                    "index.html",
                    error="Depósito inválido.",
                    deposito_key=None, deposito=None, nro_hoja=None,
                    ruta=None, paradas_editables=None, distancia=None,
                    tiempo=None, link=None
                ), 400

            if not archivo or archivo.filename == "":
                return render_template(
                    "index.html",
                    error="No adjuntaste ningún archivo PDF.",
                    deposito_key=None, deposito=None, nro_hoja=None,
                    ruta=None, paradas_editables=None, distancia=None,
                    tiempo=None, link=None
                ), 400

            nro_hoja, paradas = extraer_paradas_y_hoja(archivo)

            if not paradas:
                return render_template(
                    "index.html",
                    error="No se pudieron detectar direcciones en la hoja de ruta.",
                    deposito_key=None, deposito=None, nro_hoja=None,
                    ruta=None, paradas_editables=None, distancia=None,
                    tiempo=None, link=None
                ), 400

            return construir_respuesta(deposito_key, nro_hoja, paradas)

        elif accion == "recalcular":
            deposito_key = request.form.get("deposito_key")
            nro_hoja = request.form.get("nro_hoja")

            if not deposito_key or deposito_key not in DEPOSITOS:
                return render_template(
                    "index.html",
                    error="Depósito inválido al recalcular.",
                    deposito_key=None, deposito=None, nro_hoja=None,
                    ruta=None, paradas_editables=None, distancia=None,
                    tiempo=None, link=None
                ), 400

            clientes = request.form.getlist("cliente[]")
            direcciones = request.form.getlist("direccion[]")
            localidades = request.form.getlist("localidad[]")

            paradas = []
            for cliente, direccion, localidad in zip(clientes, direcciones, localidades):
                cliente = (cliente or "").strip()
                direccion = (direccion or "").strip()
                localidad = (localidad or "").strip()

                if not direccion:
                    continue

                if not cliente:
                    cliente = "Cliente"

                if not localidad:
                    localidad = "Sin localidad"

                paradas.append({
                    "cliente": cliente,
                    "direccion": direccion,
                    "localidad": localidad,
                    "direccion_mapa": f"{direccion}, {localidad}, Buenos Aires, Argentina"
                })

            if not paradas:
                return render_template(
                    "index.html",
                    error="No quedaron paradas válidas para recalcular.",
                    deposito_key=None, deposito=None, nro_hoja=None,
                    ruta=None, paradas_editables=None, distancia=None,
                    tiempo=None, link=None
                ), 400

            return construir_respuesta(deposito_key, nro_hoja, paradas)

        return render_template(
            "index.html",
            error="Acción no válida.",
            deposito_key=None, deposito=None, nro_hoja=None,
            ruta=None, paradas_editables=None, distancia=None,
            tiempo=None, link=None
        ), 400

    except Exception as e:
        return render_template(
            "index.html",
            error=f"Error interno: {str(e)}",
            deposito_key=None, deposito=None, nro_hoja=None,
            ruta=None, paradas_editables=None, distancia=None,
            tiempo=None, link=None
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
