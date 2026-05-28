import json
import os
from flask import Flask, render_template, abort

app = Flask(__name__)

# O arquivo JSON que geramos com o script de conversão
JSON_PATH = 'canais.json'

def carregar_catalogo():
    """Lê o seu novo arquivo canais.json estruturado."""
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    # Envia o catálogo inteiro para a página HTML
    catalogo = carregar_catalogo()
    return render_template('index.html', catalogo=catalogo)

@app.route('/filme/<filme_id>')
def detalhe(filme_id):
    """Exibe o player para o filme/canal clicado."""
    catalogo = carregar_catalogo()
    filme = catalogo.get(filme_id)
    if not filme:
        abort(404) # Se não existir, mostra erro 404
    return render_template('player.html', filme=filme)

if __name__ == "__main__":
    # O Render ignora a porta 10000 e usa a dele, mas manter assim é seguro
    app.run(host='0.0.0.0', port=10000)
