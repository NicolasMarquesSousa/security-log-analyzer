from datetime import datetime
from pathlib import Path


LIMITE_FALHAS = 3
JANELA_SEGUNDOS = 60


def interpretar_linha(linha):
    """Converte uma linha de log em um registro estruturado."""
    linha = linha.strip()
    if not linha:
        return None

    dados = [dado.strip() for dado in linha.split("|")]
    if len(dados) != 4:
        raise ValueError(f"linha inválida ignorada: {linha}")

    data_hora, endereco_ip, evento, usuario = dados
    try:
        momento = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
    except ValueError as erro:
        raise ValueError(f"data inválida ignorada: {data_hora}") from erro

    return {
        "data_hora": data_hora,
        "endereco_ip": endereco_ip,
        "evento": evento,
        "usuario": usuario,
        "momento": momento,
    }


def analisar_linhas(linhas, limite_falhas=LIMITE_FALHAS, janela_segundos=JANELA_SEGUNDOS):
    """Analisa linhas de log e devolve contagens, alertas e avisos."""
    resultado = {
        "total_sucessos": 0,
        "total_falhas": 0,
        "falhas_por_ip": {},
        "alertas": [],
        "avisos": [],
        "registros": [],
    }
    horarios_falhas_por_ip = {}

    for linha in linhas:
        try:
            registro = interpretar_linha(linha)
        except ValueError as erro:
            resultado["avisos"].append(str(erro))
            continue

        if registro is None:
            continue

        resultado["registros"].append(registro)
        evento = registro["evento"]
        endereco_ip = registro["endereco_ip"]

        if evento == "LOGIN_SUCESSO":
            resultado["total_sucessos"] += 1
        elif evento == "LOGIN_FALHA":
            resultado["total_falhas"] += 1
            resultado["falhas_por_ip"][endereco_ip] = (
                resultado["falhas_por_ip"].get(endereco_ip, 0) + 1
            )
            horarios_falhas_por_ip.setdefault(endereco_ip, []).append(
                registro["momento"]
            )

    for ip, horarios in horarios_falhas_por_ip.items():
        quantidade_grupos = len(horarios) - limite_falhas + 1
        for indice in range(max(0, quantidade_grupos)):
            primeira_falha = horarios[indice]
            ultima_falha = horarios[indice + limite_falhas - 1]
            intervalo = (ultima_falha - primeira_falha).total_seconds()

            if intervalo <= janela_segundos:
                resultado["alertas"].append(
                    {
                        "ip": ip,
                        "quantidade": limite_falhas,
                        "intervalo_segundos": intervalo,
                    }
                )
                break

    return resultado


def analisar_arquivo(caminho_log):
    """Lê um arquivo e envia suas linhas para a análise."""
    with open(caminho_log, "r", encoding="utf-8") as arquivo:
        return analisar_linhas(arquivo.readlines())


def exibir_resultado(resultado):
    """Apresenta os registros e o resumo da análise no terminal."""
    for aviso in resultado["avisos"]:
        print(f"AVISO: {aviso}")

    for registro in resultado["registros"]:
        print(f"Data: {registro['data_hora']}")
        print(f"IP: {registro['endereco_ip']}")
        print(f"Evento: {registro['evento']}")
        print(f"Usuário: {registro['usuario']}")
        print("-" * 40)

    print("\nRESUMO DA ANÁLISE")
    print(f"Logins com sucesso: {resultado['total_sucessos']}")
    print(f"Logins com falha: {resultado['total_falhas']}")

    print("\nFALHAS POR IP")
    for ip, quantidade in resultado["falhas_por_ip"].items():
        print(f"{ip}: {quantidade} falhas")

    print("\nANÁLISE POR TEMPO")
    for alerta in resultado["alertas"]:
        print(f"IP: {alerta['ip']}")
        print(
            f"ALERTA: {alerta['quantidade']} falhas em "
            f"{alerta['intervalo_segundos']} segundos"
        )


def main():
    pasta_projeto = Path(__file__).parent
    caminho_log = pasta_projeto / "logs" / "exemplo.log"
    resultado = analisar_arquivo(caminho_log)
    exibir_resultado(resultado)


if __name__ == "__main__":
    main()

