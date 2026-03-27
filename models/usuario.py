import json

# Caminho do arquivo de persistência JSON
ARQUIVO_DADOS = "usuarios.json"

def ler_dados() -> dict:

    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados(dados: dict) -> None:

    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
