import json

# Caminho do arquivo de persistência JSON
ARQUIVO_DADOS = "usuarios.json"


# =============================================================================
#   FUNÇÕES AUXILIARES — MANIPULAÇÃO DO ARQUIVO JSON
#   (Peso: 20% da avaliação — Manipulação de Arquivos)
# =============================================================================

def ler_dados() -> dict:
    """
    Lê e retorna o conteúdo do arquivo usuarios.json como dicionário Python.

    Returns:
        dict: Dados completos do sistema (usuários, receitas, etc.)

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        json.JSONDecodeError: Se o arquivo estiver corrompido.
    """
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_dados(dados: dict) -> None:
    """
    Salva o dicionário Python de volta no arquivo usuarios.json.

    O parâmetro `indent=2` garante formatação legível.
    O parâmetro `ensure_ascii=False` preserva caracteres especiais (ç, ã, etc.).

    Args:
        dados (dict): Dicionário completo a ser persistido.
    """
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
