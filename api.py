from flask import Flask, jsonify
import threading
import time
import monitor
import json
import os
import fcntl # Biblioteca para garantir que apenas um monitor rode

app = Flask(__name__)

# Bloqueio simples para garantir que o monitor rode apenas uma vez
def run_monitor():
    lock_file = "/tmp/monitor.lock"
    with open(lock_file, "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            return # Já existe um monitor rodando, este processo sai

    while True:
        try:
            print("Monitoring channels...")
            monitor.atualizar_links()
        except Exception as e:
            print(f"Error in monitor: {e}")
        time.sleep(300)

# Inicia o monitor em thread separada
threading.Thread(target=run_monitor, daemon=True).start()

@app.route('/')
def home():
    return "API de Autocura IPTV Online", 200

@app.route('/canal/<canal_name>')
def canal(canal_name):
    json_path = 'canais_ativos.json'
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                canais = json.load(f)
                link = canais.get(canal_name)
                if link:
                    return jsonify({"canal": canal_name, "link": link})
                return jsonify({"error": "Canal não encontrado"}), 404
        except Exception as e:
            return jsonify({"error": f"Erro ao ler JSON: {str(e)}"}), 500
    return jsonify({"error": "Aguardando primeira verificação..."}), 503

if __name__ == '__main__':
    app.run()
