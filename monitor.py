import json
import os
from flask import Flask, render_template, abort

app = Flask(__name__)

# O arquivo canais.json agora deve conter a estrutura de filmes/series
JSON_PATH = 'canais.json'

def carregar_catalogo():
    """Carrega o catálogo visual a partir do JSON."""
    if not os.path.exists(JSON_PATH):
        return {}
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return {}

@app.route('/')
def index():
    """Exibe o catálogo estilo Netflix."""
    catalogo = carregar_catalogo()
    return render_template('index.html', catalogo=catalogo)

@app.route('/assistir/<item_id>')
def assistir(item_id):
    """Página de player para um item específico."""
    catalogo = carregar_catalogo()
    item = catalogo.get(item_id)
    if not item:
        abort(404)
    return render_template('player.html', item=item)

if __name__ == "__main__":
    # O Render usa a porta 10000 por padrão
    app.run(host='0.0.0.0', port=10000)
