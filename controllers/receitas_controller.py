from flask import Blueprint, request, jsonify, session
from models.usuario import ler_dados, salvar_dados
from utils.validacoes import usuario_pode_editar

receitas_bp = Blueprint('receitas', __name__)

@receitas_bp.route("/curtir/<int:receita_id>", methods=["POST"])
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


@receitas_bp.route("/comentar/<int:receita_id>", methods=["POST"])
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


@receitas_bp.route("/comentario/<int:comentario_id>", methods=["DELETE"])
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