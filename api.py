from flask import Flask, redirect, jsonify
import json
import os

app = Flask(__name__)

@app.route('/canal/<nome_canal>')
def canal(nome_canal):
    if not os.path.exists('canais_ativos.json'):
        return "Sistema em inicialização", 503
        
    with open('canais_ativos.json', 'r') as f:
        dados = json.load(f)
        link = dados.get(nome_canal)
        
        if link:
            return redirect(link)
    
    return "Canal Indisponível", 404

if __name__ == '__main__':
    # Roda na porta 5000
    app.run(host='0.0.0.0', port=5000)