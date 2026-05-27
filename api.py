from flask import Flask, jsonify
import threading
import time
import monitor
import json
import os

app = Flask(__name__)

# Função do monitor que roda em paralelo
def run_monitor():
    while True:
        try:
            print("Monitoring channels...")
            monitor.atualizar_links() 
        except Exception as e:
            print(f"Error in monitor: {e}")
        time.sleep(300) # Espera 5 minutos

# Inicia o monitor apenas UMA vez
threading.Thread(target=run_monitor, daemon=True).start()

# ROTA RAIZ: Isso evita que o Render reinicie o seu servidor!
@app.route('/')
def home():
    return "API de Autocura IPTV Online", 200

@app.route('/canal/<canal_name>')
def canal(canal_name):
    if os.path.exists('canais_ativos.json'):
        with open('canais_ativos.json', 'r') as f:
            try:
                canais = json.load(f)
                link = canais.get(canal_name)
                if link:
                    return jsonify({"canal": canal_name, "link": link})
                else:
                    return jsonify({"error": "Canal não encontrado"}), 404
            except:
                return jsonify({"error": "Erro no arquivo JSON"}), 500
    return jsonify({"error": "Aguardando primeira verificação..."}), 503

if __name__ == '__main__':
    app.run()
