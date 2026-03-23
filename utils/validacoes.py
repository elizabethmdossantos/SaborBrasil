import bcrypt
from models.usuario import ler_dados
# =============================================================================
#   FUNÇÕES DE SEGURANÇA — HASH DE SENHAS
#   (Peso: 30% da avaliação — Segurança da Informação)
# =============================================================================

def hash_senha(senha_texto_puro: str) -> str:
    """
    Recebe uma senha em texto puro e retorna sua versão em hash (bcrypt).

    O bcrypt adiciona automaticamente um "salt" aleatório ao hash, tornando
    dois hashes da mesma senha diferentes entre si — isso é proposital e seguro!

    Exemplo de uso:
        senha_hash = hash_senha("minha_senha_123")
        # Resultado: "$2b$12$..." (string longa e ilegível)

    Args:
        senha_texto_puro (str): Senha digitada pelo usuário no cadastro.

    Returns:
        str: Hash da senha, pronto para ser salvo no JSON.

    Dica:
        1. Converta a senha para bytes com: senha_texto_puro.encode("utf-8")
        2. Use bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        3. Decodifique o resultado para string com: .decode("utf-8")
    """
    # converter para bytes
    senha_bytes = senha_texto_puro.encode("utf-8")
    # gerar o hash com bcrypt.hashpw()
    hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    # retornar hash como string
    return hash_bytes.decode("utf-8")

def verificar_senha(senha_texto_puro: str, senha_hash: str) -> bool:
    """
    Compara uma senha digitada com o hash armazenado no JSON.

    O bcrypt.checkpw() faz a comparação de forma segura, sem nunca
    "descriptografar" o hash (pois hash é uma função de mão única).

    Exemplo de uso:
        eh_valida = verificar_senha("minha_senha_123", hash_do_banco)
        # Resultado: True ou False

    Args:
        senha_texto_puro (str): Senha digitada pelo usuário no login.
        senha_hash (str): Hash armazenado no arquivo JSON.

    Returns:
        bool: True se a senha confere, False caso contrário.

    Dica:
        1. Converta senha_texto_puro para bytes com: .encode("utf-8")
        2. Converta senha_hash para bytes com: .encode("utf-8")
        3. Use bcrypt.checkpw(senha_bytes, hash_bytes) — retorna bool
    """
    # converter ambas variáveis para bytes
    senha_bytes = senha_texto_puro.encode("utf-8")
    # uso do bcrypt.checkpw() para comparar
    hash_bytes = senha_hash.encode("utf-8")
    # retorna o resultado com booleano
    return bcrypt.checkpw(senha_bytes, hash_bytes)

# =============================================================================
#   FUNÇÕES AUXILIARES — GESTÃO DE PERFIS
#   (Parte da lógica de Linguagem de Programação — 30%)
# =============================================================================

def usuario_pode_editar(id_usuario_acao: int, id_autor_comentario: int) -> bool:
    """
    Verifica se um usuário tem permissão para editar ou excluir um comentário.

    Regras de negócio:
        - O ADMIN pode editar/excluir qualquer comentário.
        - Um usuário COMUM só pode editar/excluir seus próprios comentários.

    Args:
        id_usuario_acao (int): ID do usuário que está tentando agir.
        id_autor_comentario (int): ID do autor original do comentário.

    Returns:
        bool: True se tem permissão, False caso contrário.

    Dica:
        1. Busque o usuário pelo id_usuario_acao dentro de dados["usuarios"]
        2. Verifique se usuario["perfil"] == "admin"
        3. OU verifique se id_usuario_acao == id_autor_comentario
    """
    # Chame ler_dados() para obter os dados
    dados = ler_dados()
    # Encontre o usuário pelo id_usuario_acao
    usuario = next((u for u in dados["usuarios"] if u["id"] == id_usuario_acao), None)
    
    if not usuario:
        return False
    # Retorne True se for admin OU se for o próprio autor
    if usuario["perfil"] == "admin" or id_usuario_acao == id_autor_comentario:
        return True
    # Retorne False em todos os outros casos
    return False