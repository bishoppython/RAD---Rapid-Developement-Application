from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

OPERATIONS = {
    "soma": lambda a, b: a + b,
    "subtracao": lambda a, b: a - b,
    "multiplicacao": lambda a, b: a * b,
    "divisao": lambda a, b: a / b if b != 0 else None,
}

SYMBOLS = {
    "soma": "+",
    "subtracao": "-",
    "multiplicacao": "×",
    "divisao": "÷",
}


@app.route("/calcular", methods=["POST"])
def calcular():
    data = request.get_json()

    if not data:
        return jsonify({"erro": "Body JSON é obrigatório"}), 400

    num1 = data.get("num1")
    num2 = data.get("num2")
    operacao = data.get("operacao", "").lower().strip()

    # Validações
    if num1 is None or num2 is None:
        return jsonify({"erro": "Os campos 'num1' e 'num2' são obrigatórios"}), 400

    if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
        return jsonify({"erro": "'num1' e 'num2' devem ser números"}), 400

    if operacao not in OPERATIONS:
        return jsonify({
            "erro": f"Operação '{operacao}' inválida",
            "operacoes_validas": list(OPERATIONS.keys())
        }), 400

    if operacao == "divisao" and num2 == 0:
        return jsonify({"erro": "Divisão por zero não é permitida"}), 422

    resultado = OPERATIONS[operacao](num1, num2)
    simbolo = SYMBOLS[operacao]

    return jsonify({
        "sucesso": True,
        "operacao": operacao,
        "expressao": f"{num1} {simbolo} {num2} = {resultado}",
        "num1": num1,
        "num2": num2,
        "resultado": resultado,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@app.route("/operacoes", methods=["GET"])
def listar_operacoes():
    return jsonify({
        "operacoes_disponiveis": [
            {"nome": "soma", "simbolo": "+", "descricao": "Adição de dois números"},
            {"nome": "subtracao", "simbolo": "-", "descricao": "Subtração de dois números"},
            {"nome": "multiplicacao", "simbolo": "×", "descricao": "Multiplicação de dois números"},
            {"nome": "divisao", "simbolo": "÷", "descricao": "Divisão de dois números (num2 ≠ 0)"},
        ]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"erro": "Rota não encontrada"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"erro": "Método HTTP não permitido"}), 405


if __name__ == "__main__":
    app.run(debug=True, port=5000)
