from pathlib import Path

from datetime import datetime


pasta_projeto = Path(__file__).parent
caminho_log = pasta_projeto / "logs" / "exemplo.log"

with open(caminho_log, "r", encoding="utf-8") as arquivo:
    linhas = arquivo.readlines()

total_sucessos = 0
total_falhas = 0
falhas_por_ip = {}
horarios_falhas_por_ip = {}
LIMITE_FALHAS = 3
JANELA_SEGUNDOS = 60

for linha in linhas:
    linha = linha.strip()
    if not linha:
        continue

    dados = linha.split("|")

    if len(dados) != 4:
        print(f"AVISO: linha inválida ignorada: {linha}")
        continue

    data_hora = dados[0].strip()
    endereco_ip = dados[1].strip()
    evento = dados[2].strip()
    usuario = dados[3].strip()

    try:
        momento = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"AVISO: data inválida ignorada: {data_hora}")
        continue
    

    if evento == "LOGIN_SUCESSO":
        total_sucessos += 1
    elif evento == "LOGIN_FALHA":
        total_falhas += 1

        if endereco_ip not in falhas_por_ip:
            falhas_por_ip[endereco_ip] = 0

        falhas_por_ip[endereco_ip] += 1 

        if endereco_ip not in horarios_falhas_por_ip:
            horarios_falhas_por_ip[endereco_ip] = []

        horarios_falhas_por_ip[endereco_ip].append(momento)

    print(f"Data: {data_hora}")
    print(f"IP: {endereco_ip}")
    print(f"Evento: {evento}")
    print(f"Usuário: {usuario}")
    print("-" * 40)

print("\nRESUMO DA ANÁLISE")
print(f"Logins com sucesso: {total_sucessos}")
print(f"Logins com falha: {total_falhas}")

print("\nFalhas Por IP")

for ip, quantidade in falhas_por_ip.items():
    print(f"{ip}: {quantidade} falhas")

   
print("\nANÁLISE POR TEMPO")

for ip, horarios in horarios_falhas_por_ip.items():
    if len(horarios) >= LIMITE_FALHAS:
        quantidade_grupos = len(horarios) - LIMITE_FALHAS + 1

        for indice in range(quantidade_grupos):
            primeira_falha = horarios[indice]
            terceira_falha = horarios[indice + LIMITE_FALHAS - 1]

            intervalo = (terceira_falha - primeira_falha).total_seconds()

            if intervalo <= JANELA_SEGUNDOS:
                print(f"IP: {ip}")
                print(
                    f"ALERTA: {LIMITE_FALHAS} falhas em "
                    f"{intervalo} segundos"
                )
                break
