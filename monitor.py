import requests
import json
import time
import threading
import logging
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configurações ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Configuração robusta de sessão para evitar "Connection pool is full"
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=50, 
    pool_maxsize=50,
    max_retries=Retry(total=2, backoff_factor=0.5)
)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

canais_ativos = {}

def carregar_config():
    try:
        with open('canais.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao ler canais.json: {e}")
        return {}

def testar_link(canal_info):
    """Testa o link e retorna ID e URL se estiver vivo."""
    canal_id, url = canal_info
    try:
        # HEAD é suficiente e muito mais leve que GET
        res = session.head(url, timeout=(3, 5), allow_redirects=True)
        if res.status_code == 200:
            return canal_id, url
    except Exception as e:
        logging.debug(f"Canal {canal_id} falhou: {e}")
    return canal_id, None

def atualizar_links():
    global canais_ativos
    config = carregar_config()
    if not config: return
    
    logging.info(f"Iniciando check-up de {len(config)} canais...")
    
    # Processamento paralelo otimizado
    with ThreadPoolExecutor(max_workers=25) as executor:
        resultados = executor.map(testar_link, config.items())
    
    # Filtra apenas os que retornaram URL válida
    novos_ativos = {cid: url for cid, url in resultados if url}
            
    canais_ativos = novos_ativos
    logging.info(f"Check-up concluído. {len(canais_ativos)} canais ativos.")

@app.route('/canal/<canal_id>')
def get_canal(canal_id):
    if canal_id in canais_ativos:
        return jsonify({"status": "ok", "url": canais_ativos[canal_id]})
    return jsonify({"status": "error", "message": "Canal offline ou inexistente"}), 404

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "monitor_ativo": True,
        "canais_ativos": len(canais_ativos),
        "ultima_atualizacao": time.strftime('%H:%M:%S')
    })

def loop_monitoramento():
    # Primeira execução imediata
    atualizar_links()
    # Loop de repetição
    while True:
        time.sleep(300) # 5 minutos
        atualizar_links()

if __name__ == "__main__":
    # Inicia o worker de monitoramento
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    
    # Inicia o servidor Flask
    # Dica: Em produção no Render, use 'gunicorn monitor:app' no comando de start
    app.run(host='0.0.0.0', port=10000)
