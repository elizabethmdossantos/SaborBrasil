import json
import os
from flask import Flask, render_template, request, jsonify, session

# O módulo bcrypt fornece funções de hash seguro para senhas.
import bcrypt

app = Flask(__name__)

# Chave secreta necessária para o uso de sessões no Flask.
app.secret_key = "sabor_do_brasil_chave_secreta_2024"

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


# =============================================================================
#   ROTAS DA APLICAÇÃO
# =============================================================================

@app.route("/")
def index():
    """Rota principal — renderiza a página inicial com as receitas."""
    dados = ler_dados()
    usuario_logado = session.get("usuario")
    return render_template("index.html", receitas=dados["receitas"], usuario=usuario_logado)


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    """
    Rota de cadastro de novo usuário.

    Recebe via JSON: { "nickname": "...", "senha": "..." }
    Retorna JSON com sucesso ou mensagem de erro.

    IMPORTANTE: A senha NUNCA deve ser salva em texto puro!
    Use a função hash_senha() que você implementou.
    """
    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()

    # Validação básica dos campos
    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()

    # Verifica se o nickname já existe
    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            return jsonify({"erro": "Nickname já está em uso"}), 409

    # Use hash_senha(senha) para gerar o hash da sen
    senha_hasheada = hash_senha(senha)
    # Crie um dicionário novo_usuario
    novo_usuario = {
        "id": dados["proximo_usuario_id"],
        "nickname": nickname,
        "senha": senha_hasheada,
        "perfil": "comum"
    }
    # Adicione novo_usuario em dados["usuarios"]
    dados["usuarios"].append(novo_usuario)
    # Incremente dados["proximo_usuario_id"] em 1
    dados["proximo_usuario_id"] += 1
    # Chame salvar_dados(dados) para persistir
    salvar_dados(dados)
    # Retorne jsonify({"mensagem": "Cadastro realizado com sucesso!"})
    return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201


@app.route("/login", methods=["POST"])
def login():
    """
    Rota de autenticação.

    Recebe via JSON: { "nickname": "...", "senha": "..." }
    Em caso de sucesso, salva o usuário na sessão Flask.

    (Peso: 30% — Linguagem de Programação / estruturas condicionais)
    """
    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()

    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()
    usuario_encontrado = None

    # Busca o usuário pelo nickname (case-insensitive)
    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            usuario_encontrado = usuario
            break

    # verificar usuario e senha, se for None retorna erro 401
    if usuario_encontrado is None or not verificar_senha(senha, usuario_encontrado["senha"]):
        return jsonify({"erro": "Usuário ou senha incorreto"}), 401

    session["usuario"]  = {
         "id": usuario_encontrado["id"],
         "nickname": usuario_encontrado["nickname"],
         "perfil": usuario_encontrado["perfil"]
    }

    return jsonify({"mensagem": "Login realizado!", "usuario": session["usuario"]})


@app.route("/logout", methods=["POST"])
def logout():
    """Remove o usuário da sessão (logout)."""
    session.pop("usuario", None)
    return jsonify({"mensagem": "Logout realizado com sucesso!"})


@app.route("/curtir/<int:receita_id>", methods=["POST"])
def curtir(receita_id: int):
    """
    Adiciona ou remove a curtida do usuário logado em uma receita (toggle).
    Se o usuário não estiver logado, retorna erro 401.
    """
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"erro": "Você precisa estar logado para curtir"}), 401

    dados = ler_dados()

    for receita in dados["receitas"]:
        if receita["id"] == receita_id:
            nickname = usuario["nickname"]
            if nickname in receita["curtidas"]:
                receita["curtidas"].remove(nickname)
                acao = "removida"
            else:
                receita["curtidas"].append(nickname)
                acao = "adicionada"
            salvar_dados(dados)
            return jsonify({
                "mensagem": f"Curtida {acao}!",
                "total_curtidas": len(receita["curtidas"]),
                "curtiu": nickname in receita["curtidas"]
            })

    return jsonify({"erro": "Receita não encontrada"}), 404


@app.route("/comentar/<int:receita_id>", methods=["POST"])
def comentar(receita_id: int):
    """
    Adiciona um comentário à receita.
    Requer usuário logado.
    """
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"erro": "Você precisa estar logado para comentar"}), 401

    corpo = request.get_json()
    texto = corpo.get("texto", "").strip()

    if not texto:
        return jsonify({"erro": "O comentário não pode estar vazio"}), 400

    dados = ler_dados()

    for receita in dados["receitas"]:
        if receita["id"] == receita_id:
            novo_comentario = {
                "id": dados["proximo_comentario_id"],
                "autor_id": usuario["id"],
                "autor_nickname": usuario["nickname"],
                "texto": texto
            }
            receita["comentarios"].append(novo_comentario)
            dados["proximo_comentario_id"] += 1
            salvar_dados(dados)
            return jsonify({
                "mensagem": "Comentário adicionado!",
                "comentario": novo_comentario
            })

    return jsonify({"erro": "Receita não encontrada"}), 404


@app.route("/comentario/<int:comentario_id>", methods=["DELETE"])
def excluir_comentario(comentario_id: int):
    """
    Exclui um comentário pelo ID.

    Regras:
        - Admin pode excluir qualquer comentário.
        - Usuário comum só pode excluir seu próprio comentário.

    (Utiliza a função usuario_pode_editar() que você implementou.)
    """
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"erro": "Você precisa estar logado"}), 401

    dados = ler_dados()

    for receita in dados["receitas"]:
        for comentario in receita["comentarios"]:
            if comentario["id"] == comentario_id:

                if usuario_pode_editar(usuario["id"], comentario["autor_id"]):
                    receita["comentarios"].remove(comentario)
                    salvar_dados(dados)
                    return jsonify({"mensagem": "Comentário excluído com sucesso!"})
                else:
                    return jsonify({"erro": "Sem permissão para excluir este comentário"}), 403

    return jsonify({"erro": "Comentário não encontrado"}), 404


@app.route("/status")
def status():
    """Rota utilitária — retorna o usuário da sessão atual (útil para debug)."""
    return jsonify({"usuario_logado": session.get("usuario")})


# =============================================================================
#   INICIALIZAÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    if not os.path.exists(ARQUIVO_DADOS):
        print(f"[ERRO] Arquivo '{ARQUIVO_DADOS}' não encontrado!")
        print("Certifique-se de que o arquivo usuarios.json está na mesma pasta que app.py.")
    else:
        print("=" * 50)
        print("  Sabor do Brasil — Servidor iniciado!")
        print("  Acesse: http://127.0.0.1:5000")
        print("=" * 50)
        app.run(debug=True)