# =============================================================================
# IMPORTS — carregando as ferramentas que vamos usar
# =============================================================================

from flask import Flask, request, jsonify, send_file
# Flask   → o framework que transforma nosso script Python em um servidor web
# request → objeto que representa a requisição HTTP recebida (body, headers, etc.)
# jsonify → converte dicionários Python em respostas JSON válidas

from flask_cors import CORS
# CORS (Cross-Origin Resource Sharing) → permite que outros domínios acessem
# nossa API. Sem isso, um site em "meusite.com" não conseguiria chamar nossa
# API em "localhost:5000" por restrições de segurança do browser.

from datetime import datetime, UTC
# Usado para gerar o timestamp (data/hora) nas respostas


# =============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =============================================================================

app = Flask(__name__)
# Cria a aplicação Flask. __name__ indica o módulo atual, necessário para o
# Flask localizar arquivos e configurações corretamente.

CORS(app)
# Aplica o CORS em todas as rotas da aplicação.


# =============================================================================
# DICIONÁRIOS DE DADOS — configuração das operações
# =============================================================================

OPERATIONS = {
    "soma":          lambda a, b: a + b,
    "subtracao":     lambda a, b: a - b,
    "multiplicacao": lambda a, b: a * b,
    "divisao":       lambda a, b: a / b if b != 0 else None,
}
# Um dicionário onde cada chave é o nome da operação e o valor é uma função.
# "lambda a, b: a + b" é uma função anônima (sem nome) que recebe dois
# parâmetros e retorna a soma. É equivalente a escrever:
#
#   def soma(a, b):
#       return a + b
#
# Na divisão usamos um operador ternário: "X if CONDIÇÃO else Y"
# Se b != 0 → divide normalmente. Se b == 0 → retorna None (evita erro).

SYMBOLS = {
    "soma":          "+",
    "subtracao":     "-",
    "multiplicacao": "×",
    "divisao":       "÷",
}
# Apenas os símbolos para montar a expressão legível na resposta.
# Ex: "10 + 3 = 13"


# =============================================================================
# ROTA 1 — POST /calcular
# =============================================================================

@app.route("/calcular", methods=["POST"])
# @app.route é um "decorator": ele registra a função abaixo como responsável
# por responder às requisições que chegarem na URL "/calcular" via método POST.
# methods=["POST"] restringe para aceitar apenas requisições POST.

def calcular():
    data = request.get_json()
    # Lê o corpo (body) da requisição e interpreta como JSON.
    # Se o body não for JSON válido, retorna None.

    if not data:
        return jsonify({"erro": "Body JSON é obrigatório"}), 400
    # Se data for None ou vazio, retorna erro.
    # jsonify() cria a resposta JSON. O segundo valor (400) é o HTTP status code:
    #   200 → sucesso
    #   400 → erro do cliente (Bad Request)
    #   422 → erro de lógica (Unprocessable Entity)

    num1 = data.get("num1")
    num2 = data.get("num2")
    operacao = data.get("operacao", "").lower().strip()
    # data.get("chave") extrai o valor do JSON recebido.
    # .get("operacao", "") usa "" como valor padrão se a chave não existir.
    # .lower() → converte para minúsculas ("SOMA" vira "soma")
    # .strip()  → remove espaços extras no início/fim ("soma " vira "soma")


    # --- VALIDAÇÕES ---
    # Validamos antes de calcular para garantir que os dados são válidos.

    if num1 is None or num2 is None:
        return jsonify({"erro": "Os campos 'num1' e 'num2' são obrigatórios"}), 400
    # Verifica se os campos existem no JSON enviado.

    if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
        return jsonify({"erro": "'num1' e 'num2' devem ser números"}), 400
    # isinstance(valor, tipo) verifica se o valor é de um determinado tipo.
    # Aqui aceitamos tanto int (10) quanto float (10.5).
    # Isso evita que alguém envie strings como "dez".

    if operacao not in OPERATIONS:
        return jsonify({
            "erro": f"Operação '{operacao}' inválida",
            "operacoes_validas": list(OPERATIONS.keys())
        }), 400
    # "x not in dicionario" verifica se a chave não existe no dicionário.
    # list(OPERATIONS.keys()) retorna ["soma", "subtracao", ...] para ajudar
    # o usuário a saber quais valores são aceitos.

    if operacao == "divisao" and num2 == 0:
        return jsonify({"erro": "Divisão por zero não é permitida"}), 422
    # Checagem extra especificamente para divisão por zero.
    # Embora o lambda já trate isso retornando None, aqui retornamos um erro
    # claro antes mesmo de tentar calcular.


    # --- CÁLCULO ---

    resultado = OPERATIONS[operacao](num1, num2)
    # OPERATIONS[operacao] → busca a função lambda pelo nome da operação.
    # (num1, num2)          → chama essa função passando os dois números.
    # É equivalente a: resultado = lambda_encontrada(num1, num2)

    simbolo = SYMBOLS[operacao]
    # Busca o símbolo correspondente para montar a expressão legível.

    return jsonify({
        "sucesso": True,
        "operacao": operacao,
        "expressao": f"{num1} {simbolo} {num2} = {resultado}",
        # f"..." é uma f-string: permite inserir variáveis dentro de strings
        # usando chaves {}. Resultado: "10 ÷ 2 = 5.0"
        "num1": num1,
        "num2": num2,
        "resultado": resultado,
        "timestamp": datetime.utcnow().isoformat() + "Z"
        # datetime.utcnow() → data/hora atual em UTC (fuso horário universal)
        # .isoformat()       → formata como "2026-03-07T14:00:00"
        # + "Z"              → adiciona o "Z" indicando que é UTC
    })


# =============================================================================
# ROTA 2 — GET /operacoes
# =============================================================================

@app.route("/operacoes", methods=["GET"])
def listar_operacoes():
    # Rota informativa: retorna a lista de operações disponíveis.
    # Útil para quem está integrando com a API e quer saber o que aceita.
    return jsonify({
        "operacoes_disponiveis": [
            {"nome": "soma",          "simbolo": "+", "descricao": "Adição de dois números"},
            {"nome": "subtracao",     "simbolo": "-", "descricao": "Subtração de dois números"},
            {"nome": "multiplicacao", "simbolo": "×", "descricao": "Multiplicação de dois números"},
            {"nome": "divisao",       "simbolo": "÷", "descricao": "Divisão de dois números (num2 ≠ 0)"},
        ]
    })


# =============================================================================
# ROTA 3 — GET /health
# =============================================================================

@app.route("/health", methods=["GET"])
def health():
    # Rota de "heartbeat": serve para monitoramento.
    # Ferramentas de DevOps (ex: AWS, Docker) batem nessa rota periodicamente
    # para saber se o serviço está vivo e respondendo.
    return jsonify({"status": "ok", "timestamp": datetime.now(UTC).isoformat()})

# =============================================================================
# ROTA 4 — GET /docs
# =============================================================================

@app.route("/docs", methods=["GET"])
@app.route("/", methods=["GET"])
def docs():
    return send_file("docs.html")


# =============================================================================
# TRATAMENTO GLOBAL DE ERROS
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    # Intercepta erros 404 (rota não encontrada) em toda a aplicação.
    # Sem isso, o Flask retornaria uma página HTML de erro — aqui garantimos
    # que a resposta seja sempre JSON, mantendo o padrão da API.
    return jsonify({"erro": "Rota não encontrada"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    # Intercepta erros 405 (método HTTP não permitido).
    # Ex: tentar um GET em /calcular, que só aceita POST.
    return jsonify({"erro": "Método HTTP não permitido"}), 405


# =============================================================================
# PONTO DE ENTRADA — inicialização do servidor
# =============================================================================

if __name__ == "__main__":
    # Esta condição é True apenas quando executamos o arquivo diretamente
    # com "python api.py". Se o arquivo for importado por outro módulo,
    # este bloco NÃO é executado — o que evita iniciar o servidor por acidente.

    app.run(debug=True, port=5000)
    # debug=True → ativa o modo de desenvolvimento:
    #   - reinicia o servidor automaticamente ao salvar o arquivo
    #   - mostra erros detalhados no terminal
    #   ⚠️ Nunca use debug=True em produção!
    # port=5000  → porta onde o servidor vai escutar (padrão do Flask)