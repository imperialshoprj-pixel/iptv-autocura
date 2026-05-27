import requests
import json
import time
import threading
import logging
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
canais_ativos = {} 
# Session otimiza as conexões HTTP
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

def carregar_config():
    try:
        with open('canais.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao carregar canais.json: {e}")
        return {}

def testar_link(canal_id, url):
    """Testa apenas a URL fornecida com sessão persistente."""
    try:
        # head solicita apenas o cabeçalho, muito mais rápido que baixar o stream
        res = session.head(url, timeout=(3, 5), allow_redirects=True)
        if res.status_code == 200:
            return canal_id, url
    except:
        pass
    return canal_id, None

def atualizar_links():
    global canais_ativos
    config = carregar_config()
    logging.info(f"Iniciando check-up de {len(config)} canais...")
    
    novos_ativos = {}
    # Aumentei para 20 threads para agilizar o scan em listas grandes
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Ajustado para aceitar dict direto: {id: url}
        resultados = list(executor.map(lambda item: testar_link(item[0], item[1]), config.items()))
    
    for canal_id, link in resultados:
        if link:
            novos_ativos[canal_id] = link
            
    canais_ativos = novos_ativos
    logging.info(f"Check-up concluído. {len(canais_ativos)} canais ativos.")

@app.route('/canal/<canal_id>')
def get_canal(canal_id):
    if canal_id in canais_ativos:
        return jsonify({"status": "ok", "url": canais_ativos[canal_id]})
    return jsonify({"status": "error", "message": "Canal offline"}), 404

@app.route('/')
def home():
    return jsonify({"status": "online", "canais_monitorados": len(canais_ativos)})

def loop_monitoramento():
    """Loop infinito que roda a cada 5 minutos."""
    while True:
        atualizar_links()
        time.sleep(300) # 5 minutos

if __name__ == "__main__":
    # Inicia o monitoramento em uma thread separada para não travar a API
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    
    # Inicia Web Server (Gunicorn seria melhor em produção)
    app.run(host='0.0.0.0', port=10000)
