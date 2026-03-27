from flask import Blueprint, render_template, request, jsonify, session
from models.usuario import ler_dados, salvar_dados
from utils.validacoes import hash_senha, verificar_senha

main_bp = Blueprint('main', __name__)

# Chave secreta para criar contas de administrador
CHAVE_MESTRA_ADMIN = "receita123"

# =============================================================================
#   ROTAS DA APLICAÇÃO
# =============================================================================

@main_bp.route("/")
def index():
    """Rota principal — renderiza a página inicial com as receitas."""
    dados = ler_dados()
    usuario_logado = session.get("usuario")
    return render_template("index.html", receitas=dados["receitas"], usuario=usuario_logado)


@main_bp.route("/cadastrar", methods=["POST"])
def cadastrar():

    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()
    chave_enviada = corpo.get("chave_admin", "").strip()

    # Validação básica dos campos
    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()

    perfil_final = "admin" if chave_enviada == CHAVE_MESTRA_ADMIN else "comum"

    # Verifica se o nickname já existe
    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            return jsonify({"erro": "Nickname já está em uso"}), 409

    # Crie um dicionário novo_usuario
    novo_usuario = {
        "id": dados["proximo_usuario_id"],
        "nickname": nickname,
        "senha": hash_senha(senha),
        "perfil": perfil_final
    }
    # Adicione novo_usuario em dados["usuarios"]
    dados["usuarios"].append(novo_usuario)
    # Incremente dados["proximo_usuario_id"] em 1
    dados["proximo_usuario_id"] += 1
    # Chame salvar_dados(dados) para persistir
    salvar_dados(dados)
    # Retorne jsonify({"mensagem": "Cadastro realizado com sucesso!"})
    return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201


@main_bp.route("/login", methods=["POST"])
def login():

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


@main_bp.route("/logout", methods=["POST"])
def logout():
    """Remove o usuário da sessão (logout)."""
    session.pop("usuario", None)
    return jsonify({"mensagem": "Logout realizado com sucesso!"})


@main_bp.route("/status")
def status():
    """Rota utilitária — retorna o usuário da sessão atual (útil para debug)."""
    return jsonify({"usuario_logado": session.get("usuario")})