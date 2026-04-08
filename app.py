import os
from flask import Flask, render_template, request

from utils.parser_ruta_excel import extraer_paradas_ruta_excel
from utils.parser_xlsx import extraer_datos_xlsx
from utils.matcher import procesar_cruce_completo

app = Flask(__name__)


@app.route("/health")
def health():
    return "OK", 200


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", resumen=None, paradas=None, eventos=None, error=None)

    try:
        ruta_file = request.files.get("ruta_file")
        historico_file = request.files.get("historico_file")

        hoja_ruta_nro, paradas = extraer_paradas_ruta_excel(ruta_file)
        datos = extraer_datos_xlsx(historico_file)

        eventos = datos["eventos"]
        track_points = datos["track_points"]

        resumen, paradas_procesadas, eventos_procesados = procesar_cruce_completo(
            hoja_ruta_nro,
            paradas,
            eventos,
            track_points
        )

        return render_template(
            "index.html",
            resumen=resumen,
            paradas=paradas_procesadas,
            eventos=eventos_procesados,
            error=None
        )

    except Exception as e:
        return render_template("index.html", resumen=None, paradas=None, eventos=None, error=str(e)), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
