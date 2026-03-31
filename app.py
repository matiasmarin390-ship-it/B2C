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
        "nombre": "Roque Pérez, Buenos Aires, Argentina",
        "coords": (-35.4237, -59.3323),
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            deposito_key = request.form.get("deposito")
            archivo = request.files.get("file")

            if not deposito_key or deposito_key not in DEPOSITOS:
                return "Error: depósito inválido", 400

            if not archivo or archivo.filename == "":
                return "Error: no se adjuntó archivo", 400

            nro_hoja, paradas = extraer_paradas_y_hoja(archivo)

            if not paradas:
                return "Error: no se detectaron paradas en la hoja de ruta", 400

            deposito = DEPOSITOS[deposito_key]

            ruta, distancia_total_km, tiempo_total_min = optimizar_ruta_basica(
                deposito["coords"],
                paradas
            )

            link_maps = generar_link_maps(deposito["nombre"], ruta)

            return render_template(
                "index.html",
                deposito=deposito["nombre"],
                nro_hoja=nro_hoja,
                ruta=ruta,
                distancia=distancia_total_km,
                tiempo=tiempo_total_min,
                link=link_maps
            )

        except Exception as e:
            return f"Error interno: {str(e)}", 500

    return render_template(
        "index.html",
        deposito=None,
        nro_hoja=None,
        ruta=None,
        distancia=None,
        tiempo=None,
        link=None
    )

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
