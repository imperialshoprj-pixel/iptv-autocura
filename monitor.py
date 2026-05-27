import requests
import json
import schedule
import time
import threading
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
canais_ativos = {} # Cache em memória

def carregar_config():
    try:
        with open('canais.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def testar_link(canal_id, fontes):
    for fonte in fontes:
        try:
            # timeout agressivo para manter o sistema rápido
            res = requests.get(fonte, timeout=2, stream=True)
            if res.status_code == 200:
                return canal_id, fonte
        except:
            continue
    return canal_id, None

def atualizar_links():
    global canais_ativos
    config = carregar_config()
    print(f"[{time.strftime('%H:%M:%S')}] Checando {len(config)} canais...")
    
    novos_ativos = {}
    # Testa 10 canais ao mesmo tempo para velocidade máxima
    with ThreadPoolExecutor(max_workers=10) as executor:
        resultados = executor.map(lambda p: testar_link(p[0], p[1]), config.items())
    
    for canal_id, link in resultados:
        if link:
            novos_ativos[canal_id] = link
            
    canais_ativos = novos_ativos # Atualiza o cache em memória
    print("Check-up concluído. Canais ativos atualizados.")

@app.route('/canal/<canal_id>')
def get_canal(canal_id):
    if canal_id in canais_ativos:
        return jsonify({"status": "ok", "url": canais_ativos[canal_id]})
    return jsonify({"status": "error", "message": "Canal offline ou inexistente"}), 404

def rodar_api():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # Inicializa
    atualizar_links()
    schedule.every(5).minutes.do(atualizar_links)
    
    # Inicia Web Server
    threading.Thread(target=rodar_api, daemon=True).start()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
