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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Configurações de segurança e estado
canais_ativos = {}
lock = threading.Lock() # Garante thread-safety na atualização da lista
SENHA_PROTECAO = "minha_senha_secreta" 

# Sessão otimizada para alta concorrência
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=50, 
    pool_maxsize=100,
    max_retries=Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({'User-Agent': 'Mozilla/5.0 (SmartTV; Tizen) AppleWebKit/537.36'})

def carregar_config():
    try:
        with open('canais.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Erro crítico ao ler canais.json: {e}")
        return {}

def testar_link(canal_info):
    canal_id, url = canal_info
    try:
        # HEAD é ideal. Timeout reduzido para evitar gargalos em canais mortos
        res = session.head(url, timeout=(2, 5), allow_redirects=True)
        return canal_id, url if res.status_code == 200 else None
    except:
        return canal_id, None

def atualizar_links():
    global canais_ativos
    config = carregar_config()
    if not config: return
    
    logging.info(f"Monitoramento: Iniciando verificação de {len(config)} canais...")
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        resultados = executor.map(testar_link, config.items())
    
    novos_canais = {cid: url for cid, url in resultados if url}
    
    # Atualização segura usando Lock
    with lock:
        canais_ativos = novos_canais
    
    logging.info(f"Monitoramento: Concluído. {len(canais_ativos)} canais ativos.")

# --- Rotas ---

@app.route('/lista.m3u')
def gerar_m3u():
    if request.args.get('senha') != SENHA_PROTECAO:
        abort(403)
        
    with lock: # Bloqueia leitura durante atualização para evitar dados incompletos
        m3u = ["#EXTM3U"]
        for cid, url in canais_ativos.items():
            m3u.append(f'#EXTINF:-1, Canal {cid}')
            m3u.append(url)
            
    return Response(
        "\n".join(m3u), 
        mimetype="application/x-mpegurl",
        headers={"Content-Disposition": "attachment; filename=lista.m3u"}
    )

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "canais_ativos": len(canais_ativos),
        "ultima_atualizacao": time.strftime('%H:%M:%S'),
        "proxima_atualizacao": "5 minutos"
    })

def loop_monitoramento():
    while True:
        atualizar_links()
        time.sleep(300) 

if __name__ == "__main__":
    # Inicia a thread de monitoramento em background
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    # Roda com Flask (para produção, utilize gunicorn monitor:app)
    app.run(host='0.0.0.0', port=10000)
