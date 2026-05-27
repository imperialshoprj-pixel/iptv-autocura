import requests
import json
import time
import threading
import logging
from flask import Flask, jsonify, Response, request, abort
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configurações ---
# Filtra logs para evitar poluição no console do Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Configuração robusta de sessão
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=100, 
    pool_maxsize=100,
    max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({'User-Agent': 'Mozilla/5.0 (SmartTV; Tizen) AppleWebKit/537.36'})

canais_ativos = {}
SENHA_PROTECAO = "minha_senha_secreta" # <--- ALTERE AQUI A SUA SENHA

def carregar_config():
    try:
        with open('canais.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao ler canais.json: {e}")
        return {}

def testar_link(canal_info):
    canal_id, url = canal_info
    try:
        res = session.head(url, timeout=(3, 7), allow_redirects=True)
        if res.status_code == 200:
            return canal_id, url
    except:
        pass
    return canal_id, None

def atualizar_links():
    global canais_ativos
    config = carregar_config()
    if not config: return
    
    logging.info(f"Monitoramento: Testando {len(config)} canais...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = executor.map(testar_link, config.items())
    
    canais_ativos = {cid: url for cid, url in resultados if url}
    logging.info(f"Monitoramento: Concluído. {len(canais_ativos)} canais estão online.")

# --- ROTAS ---

@app.route('/lista.m3u')
def gerar_m3u():
    # Proteção de acesso
    if request.args.get('senha') != SENHA_PROTECAO:
        abort(403)
        
    m3u = ["#EXTM3U"]
    for cid, url in canais_ativos.items():
        m3u.append(f'#EXTINF:-1, Canal {cid}')
        m3u.append(url)
    return Response("\n".join(m3u), mimetype="application/x-mpegurl")

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "monitor_ativo": True,
        "canais_ativos": len(canais_ativos),
        "ultima_verificacao": time.strftime('%H:%M:%S')
    })

def loop_monitoramento():
    while True:
        atualizar_links()
        time.sleep(300) # Intervalo de 5 min

if __name__ == "__main__":
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
