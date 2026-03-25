from flask import Blueprint, request, jsonify, session
from models.usuario import ler_dados, salvar_dados
from utils.validacoes import usuario_pode_editar
import json

receitas_bp = Blueprint('receitas', __name__)

ARQUIVO_DADOS = "usuarios.json"

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


@receitas_bp.route("/receitas/adicionar", methods=["POST"])
def adicionar_receita():
    usuario = session.get("usuario")
    
    # 1. Validação de Segurança: Só admin entra
    if not usuario or usuario.get("perfil") != "admin":
        return jsonify({"erro": "Acesso negado. Apenas administradores podem adicionar receitas."}), 403

    corpo = request.get_json()
    titulo = corpo.get("titulo", "").strip()
    descricao = corpo.get("descricao", "").strip()
    imagem = corpo.get("imagem", "🍳") # Emoji padrão se não enviar

    if not titulo or not descricao:
        return jsonify({"erro": "Título e descrição são obrigatórios"}), 400

    dados = ler_dados()

    # 2. Criar o novo objeto de receita
    nova_receita = {
        "id": len(dados["receitas"]) + 1, # Lógica simples de ID
        "titulo": titulo,
        "descricao": descricao,
        "imagem": imagem,
        "curtidas": [],
        "comentarios": []
    }

    # 3. Persistência
    dados["receitas"].append(nova_receita)
    salvar_dados(dados)

    return jsonify({"mensagem": "Receita adicionada com sucesso!", "receita": nova_receita}), 201

@receitas_bp.route('/receitas/excluir/<int:id>', methods=['DELETE'])
def excluir_receita(id): # <--- Mude de 'receita_id' para 'id'
    usuario = session.get('usuario')
    if not usuario or usuario.get('perfil') != 'admin':
        return jsonify({"erro": "Acesso negado"}), 403
    
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        receitas_originais = dados.get('receitas', [])
        
        # Aqui também usamos 'id' para filtrar
        nova_lista = [r for r in receitas_originais if r['id'] != id]

        if len(receitas_originais) == len(nova_lista):
            return jsonify({"erro": "Receita não encontrada"}), 404
        
        dados['receitas'] = nova_lista
    
        with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        return jsonify({"mensagem": "Receita excluída com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao deletar: {e}")
        return jsonify({"erro": "Erro interno ao processar o arquivo"}), 500