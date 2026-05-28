import json
import os
from flask import Flask, render_template, abort

app = Flask(__name__)

# Caminho para o seu catálogo
JSON_PATH = 'canais.json'

def carregar_catalogo():
    """Lê o arquivo canais.json com tratamento de erro."""
    if not os.path.exists(JSON_PATH):
        print(f"Aviso: {JSON_PATH} não encontrado!")
        return {}
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        return {}

# --- Rotas do Site ---

@app.route('/')
def index():
    """Rota principal: exibe a grade do catálogo."""
    catalogo = carregar_catalogo()
    return render_template('index.html', catalogo=catalogo)

@app.route('/filme/<filme_id>')
def detalhe(filme_id):
    """Rota de player: exibe o vídeo do filme/canal clicado."""
    catalogo = carregar_catalogo()
    filme = catalogo.get(filme_id)
    
    if not filme:
        abort(404) # Retorna erro caso o ID não exista no JSON
        
    return render_template('player.html', filme=filme)

# --- Tratamento de Erros ---

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return "Filme ou página não encontrado! <a href='/'>Voltar para o início</a>", 404

# --- Inicialização ---

if __name__ == "__main__":
    # O Render atribui a porta via variável de ambiente PORT. 
    # Isso é usado apenas para testes locais.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
