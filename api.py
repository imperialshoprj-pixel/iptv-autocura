from flask import Flask, jsonify
import threading
import time
import monitor
import json
import os

app = Flask(__name__)

# Função que o thread vai executar
def run_monitor():
    while True:
        try:
            print("Monitoring channels...")
            monitor.atualizar_links() # Agora chamamos o nome correto!
        except Exception as e:
            print(f"Error in monitor: {e}")
        time.sleep(300) # Espera 5 minutos

# Inicia o monitor em segundo plano
threading.Thread(target=run_monitor, daemon=True).start()

@app.route('/')
def home():
    return "Sistema de Autocura IPTV Online!"

@app.route('/canal/<canal_name>')
def canal(canal_name):
    # Lê o arquivo que o monitor criou
    if os.path.exists('canais_ativos.json'):
        with open('canais_ativos.json', 'r') as f:
            canais = json.load(f)
            # Retorna o link se o canal existir, ou uma mensagem de erro
            link = canais.get(canal_name)
            if link:
                return jsonify({"canal": canal_name, "link": link})
            else:
                return jsonify({"error": "Canal indisponível no momento"}), 404
    return jsonify({"error": "Monitor ainda não processou os links"}), 500

if __name__ == '__main__':
    app.run()
