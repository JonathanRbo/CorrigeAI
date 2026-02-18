"""
CorrigeAI - Servidor Flask
API de correção de textos em português.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from analyzer import analyze
import os

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)


@app.route("/")
def index():
    """Serve a landing page."""
    return send_from_directory(".", "index.html")


@app.route("/api/analisar", methods=["POST"])
def analisar():
    """
    Endpoint principal de análise de texto.
    Recebe JSON: { "texto": "..." }
    Retorna: { errors, grade, grade_label, grade_class, stats }
    """
    data = request.get_json()

    if not data or "texto" not in data:
        return jsonify({"error": "Campo 'texto' é obrigatório."}), 400

    texto = data["texto"].strip()

    if not texto:
        return jsonify({"error": "O texto não pode estar vazio."}), 400

    if len(texto) > 10000:
        return jsonify({"error": "Texto muito longo. Máximo: 10.000 caracteres."}), 400

    resultado = analyze(texto)
    return jsonify(resultado)


@app.route("/api/status", methods=["GET"])
def status():
    """Health check do servidor."""
    from analyzer import HAS_LANGUAGE_TOOL
    return jsonify({
        "status": "online",
        "language_tool": HAS_LANGUAGE_TOOL,
        "message": "CorrigeAI API funcionando.",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"""
    ╔══════════════════════════════════════════╗
    ║         CorrigeAI - Servidor             ║
    ║                                          ║
    ║   http://localhost:{port}                  ║
    ║   API: http://localhost:{port}/api/analisar ║
    ╚══════════════════════════════════════════╝
    """)
    app.run(debug=True, port=port)
