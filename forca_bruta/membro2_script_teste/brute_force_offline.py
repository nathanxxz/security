def executar_brute_force_offline():
    print("=" * 60)
    print(" ALGORITMO BRUTEFORCE - SIMULAÇÃO DIDÁTICA (PSEUDOCÓDIGO)")
    print("=" * 60)

    senha_correta = 583
    tentativa = 0
    encontrada = False

    print(f"[*] Alvo definido (PIN correto em segredo): {senha_correta}")
    print("[*] Iniciando varredura sequencial no espaço de busca [000 - 999]...\n")

    while tentativa <= 999 and not encontrada:
        pin_formatado = f"{tentativa:03d}"

        if tentativa % 100 == 0 or tentativa >= 580:
            print(f"[-] Testando senha: {pin_formatado}")

        if tentativa == senha_correta:
            encontrada = True
            print(f"\n[+] SUCESSO: Senha encontrada: {pin_formatado}!")
            print(f"[+] Total de tentativas realizadas: {tentativa + 1}")
        else:
            tentativa += 1

    if not encontrada:
        print("\n[-] Senha não encontrada no intervalo testado.")

    print("=" * 60)


if __name__ == "__main__":
    executar_brute_force_offline()
