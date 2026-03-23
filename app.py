import os
from flask import Flask
from controllers.auth_controller import main_bp

app = Flask(__name__)

# Chave secreta necessária para o uso de sessões no Flask.
app.secret_key = "sabor_do_brasil_chave_secreta_2024"

app.register_blueprint(main_bp)


if __name__ == "__main__":
    if not os.path.exists("usuarios.json"):
        print("[ERRO] Arquivo 'usuario.json' não encontrado!")
        print("Certifique-se de que o arquivo usuarios.json está na mesma pasta que app.py.")
    else:
        print("=" * 50)
        print("  Sabor do Brasil — Servidor iniciado!")
        print("  Acesse: http://127.0.0.1:5000")
        print("=" * 50)
        app.run(debug=True)