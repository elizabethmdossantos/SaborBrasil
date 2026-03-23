from flask import Blueprint, render_template, request, jsonify, session
from models.usuario import ler_dados, salvar_dados
from utils.validacoes import hash_senha, verificar_senha, usuario_pode_editar

main_bp = Blueprint('main', __name__)

# Chave secreta para criar contas de administrador
CHAVE_MESTRA_ADMIN = "receita_secreta_2024"

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
    chave_enviada = corpo.get("cahve_admin", "").strip()

    # Validação básica dos campos
    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()

    if chave_enviada:
        if chave_enviada == CHAVE_MESTRA_ADMIN:
            perfil_final = "admin"
        else:
            perfil_final = "comum"

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


@main_bp.route("/logout", methods=["POST"])
def logout():
    """Remove o usuário da sessão (logout)."""
    session.pop("usuario", None)
    return jsonify({"mensagem": "Logout realizado com sucesso!"})


@main_bp.route("/curtir/<int:receita_id>", methods=["POST"])
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


@main_bp.route("/comentar/<int:receita_id>", methods=["POST"])
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


@main_bp.route("/comentario/<int:comentario_id>", methods=["DELETE"])
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


@main_bp.route("/status")
def status():
    """Rota utilitária — retorna o usuário da sessão atual (útil para debug)."""
    return jsonify({"usuario_logado": session.get("usuario")})