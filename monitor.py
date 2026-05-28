from flask import Flask, render_template, abort
import json
import os

app = Flask(__name__)

# Função para carregar o catálogo de filmes
def carregar_catalogo():
    if os.path.exists('canais.json'):
        with open('canais.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/')
def index():
    catalogo = carregar_catalogo()
    return render_template('index.html', catalogo=catalogo)

@app.route('/filme/<filme_id>')
def filme(filme_id):
    catalogo = carregar_catalogo()
    filme_data = catalogo.get(filme_id)
    
    if not filme_data:
        abort(404)  # Filme não encontrado
        
    return render_template('player.html', filme=filme_data)

if __name__ == '__main__':
    # O Render usa a porta definida pelo sistema
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
