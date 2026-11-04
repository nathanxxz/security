from flask import Flask, render_template, request, jsonify
import time
import logging
from collections import defaultdict
import re

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AUDIT] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

USUARIO_TESTE = "aluno"
SENHA_CORRETA = "583"

config_defesa = {
    "rate_limit_ativo": False,
    "throttling_ativo": False,
    "max_tentativas": 5,
    "janela_bloqueio_segundos": 30,
    "atraso_throttling_segundos": 1.5
}

historico_tentativas = defaultdict(list)
bloqueios_ips = {}


def verificar_rate_limit(ip_cliente):
    agora = time.time()

    if ip_cliente in bloqueios_ips:
        tempo_restante = int(bloqueios_ips[ip_cliente] - agora)
        if tempo_restante > 0:
            logging.warning(f"Acesso NEGADO (Rate Limit Ativo) para IP {ip_cliente}. Restam {tempo_restante}s.")
            return False, tempo_restante
        else:
            del bloqueios_ips[ip_cliente]
            historico_tentativas[ip_cliente] = []

    historico_tentativas[ip_cliente] = [
        t for t in historico_tentativas[ip_cliente] if agora - t < 60
    ]

    if len(historico_tentativas[ip_cliente]) >= config_defesa["max_tentativas"]:
        bloqueios_ips[ip_cliente] = agora + config_defesa["janela_bloqueio_segundos"]
        logging.critical(
            f"ALERTA DE SEGURANÇA: IP {ip_cliente} atingiu o limite de {config_defesa['max_tentativas']} "
            f"tentativas falhas. Bloqueado por {config_defesa['janela_bloqueio_segundos']}s."
        )
        return False, config_defesa["janela_bloqueio_segundos"]

    return True, 0


def validar_politica_senha_forte(senha):
    padrao = r"^(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\S+$).{8,}$"
    return bool(re.match(padrao, senha))


@app.route("/")
def index():
    return render_template(
        "login.html",
        usuario_padrao=USUARIO_TESTE,
        config=config_defesa,
        bloqueios=bloqueios_ips
    )


@app.route("/api/config-defesa", methods=["POST"])
def alterar_config_defesa():
    dados = request.get_json() or {}
    if "rate_limit_ativo" in dados:
        config_defesa["rate_limit_ativo"] = bool(dados["rate_limit_ativo"])
    if "throttling_ativo" in dados:
        config_defesa["throttling_ativo"] = bool(dados["throttling_ativo"])

    historico_tentativas.clear()
    bloqueios_ips.clear()

    logging.info(
        f"Configurações atualizadas: Rate Limit={config_defesa['rate_limit_ativo']}, "
        f"Throttling={config_defesa['throttling_ativo']}"
    )
    return jsonify({
        "status": "sucesso",
        "mensagem": "Configurações de defesa atualizadas.",
        "config": config_defesa
    })


@app.route("/api/login", methods=["POST"])
def api_login():
    ip_cliente = request.remote_addr or "127.0.0.1"

    if config_defesa["rate_limit_ativo"]:
        permitido, tempo_restante = verificar_rate_limit(ip_cliente)
        if not permitido:
            return jsonify({
                "status": "bloqueado",
                "mensagem": f"Muitas tentativas falhas. Rate Limit ativado! Tente novamente em {tempo_restante} segundos.",
                "tempo_restante": tempo_restante
            }), 429

    dados = request.get_json() if request.is_json else request.form
    usuario = dados.get("usuario", "").strip()
    senha = str(dados.get("senha", "")).strip()

    logging.info(f"Tentativa de login recebida - Usuário: '{usuario}' | Senha testada: '{senha}' | Origem: {ip_cliente}")

    if config_defesa["throttling_ativo"]:
        time.sleep(config_defesa["atraso_throttling_segundos"])

    if usuario == USUARIO_TESTE and senha == SENHA_CORRETA:
        historico_tentativas.pop(ip_cliente, None)
        bloqueios_ips.pop(ip_cliente, None)
        logging.info(f"LOGIN BEM-SUCEDIDO: Usuário '{usuario}' autenticado com sucesso.")
        return jsonify({
            "status": "sucesso",
            "mensagem": f"Login efetuado com sucesso! Bem-vindo, {usuario}.",
            "codigo": 200
        }), 200
    else:
        historico_tentativas[ip_cliente].append(time.time())
        falhas_atuais = len(historico_tentativas[ip_cliente])
        logging.warning(f"FALHA NO LOGIN: Credenciais inválidas para '{usuario}'. Tentativas acumuladas: {falhas_atuais}.")
        return jsonify({
            "status": "falha",
            "mensagem": "Credenciais incorretas.",
            "tentativas_atuais": falhas_atuais,
            "max_tentativas": config_defesa["max_tentativas"] if config_defesa["rate_limit_ativo"] else "ilimitado"
        }), 401


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" SERVIÇO DE AUTENTICAÇÃO DIDÁTICO (MEMBRO 1)")
    print(" Porta: 5000 | URL: http://127.0.0.1:5000")
    print(f" Credenciais Padrão: Usuário='{USUARIO_TESTE}' | PIN/Senha='{SENHA_CORRETA}'")
    print("="*70 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
