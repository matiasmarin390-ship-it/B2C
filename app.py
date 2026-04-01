import os
from flask import Flask, render_template, request

from utils.parser_pdf import extraer_paradas_pdf
from utils.parser_xlsx import extraer_datos_xlsx
from utils.matcher import procesar_cruce_completo

app = Flask(__name__)


@app.route("/health")
def health():
    return "OK", 200


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "index.html",
            resumen=None,
            paradas=None,
            eventos=None,
            error=None
        )

    try:
        pdf_file = request.files.get("pdf_file")
        xlsx_file = request.files.get("xlsx_file")

        if not pdf_file or pdf_file.filename == "":
            return render_template(
                "index.html",
                resumen=None,
                paradas=None,
                eventos=None,
                error="Falta adjuntar la hoja de ruta en PDF."
            ), 400

        if not xlsx_file or xlsx_file.filename == "":
            return render_template(
                "index.html",
                resumen=None,
                paradas=None,
                eventos=None,
                error="Falta adjuntar el histórico en Excel."
            ), 400

        hoja_ruta_nro, paradas = extraer_paradas_pdf(pdf_file)
        eventos = extraer_datos_xlsx(xlsx_file)

        if not paradas:
            return render_template(
                "index.html",
                resumen=None,
                paradas=None,
                eventos=None,
                error="No se pudieron detectar paradas en la hoja de ruta."
            ), 400

        if not eventos:
            return render_template(
                "index.html",
                resumen=None,
                paradas=None,
                eventos=None,
                error="No se detectaron eventos distintos de 'Posición' en la solapa Resultados."
            ), 400

        resumen, paradas_procesadas, eventos_procesados = procesar_cruce_completo(
            hoja_ruta_nro=hoja_ruta_nro,
            paradas=paradas,
            eventos=eventos
        )

        return render_template(
            "index.html",
            resumen=resumen,
            paradas=paradas_procesadas,
            eventos=eventos_procesados,
            error=None
        )

    except Exception as e:
        return render_template(
            "index.html",
            resumen=None,
            paradas=None,
            eventos=None,
            error=f"Error interno: {str(e)}"
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
