import requests
import json
import time
import threading
import logging
import gzip
from io import BytesIO
from flask import Flask, jsonify, Response, request, abort
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configurações ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Cache de estado e compressão
canais_ativos = {}
m3u_cache = b"" # Armazena a lista já comprimida (GZIP) para entrega instantânea
lock = threading.Lock()
SENHA_PROTECAO = "minha_senha_secreta" 

# Sessão otimizada para alta concorrência
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=100, 
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
    except Exception as e:
        logging.error(f"Erro ao ler canais.json: {e}")
        return {}

def testar_link(canal_info):
    canal_id, url = canal_info
    try:
        res = session.head(url, timeout=(2, 5), allow_redirects=True)
        return canal_id, url if res.status_code == 200 else None
    except:
        return canal_id, None

def gerar_m3u_comprimido(canais):
    """Cria a lista M3U e a comprime para reduzir banda e evitar travamentos"""
    m3u = ["#EXTM3U"]
    for cid, url in canais.items():
        m3u.append(f'#EXTINF:-1, Canal {cid}')
        m3u.append(url)
    
    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as f:
        f.write("\n".join(m3u).encode('utf-8'))
    return buf.getvalue()

def atualizar_links():
    global canais_ativos, m3u_cache
    config = carregar_config()
    if not config: return
    
    logging.info(f"Monitoramento: Verificando {len(config)} canais...")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        resultados = executor.map(testar_link, config.items())
    
    novos_canais = {cid: url for cid, url in resultados if url}
    
    # Atualiza Cache e prepara o GZIP em memória
    with lock:
        canais_ativos = novos_canais
        m3u_cache = gerar_m3u_comprimido(novos_canais)
        
    logging.info(f"Monitoramento: Concluído. {len(canais_ativos)} canais ativos.")

# --- Rotas ---

@app.route('/lista.m3u')
def gerar_m3u():
    if request.args.get('senha') != SENHA_PROTECAO:
        abort(403)
        
    return Response(
        m3u_cache, 
        mimetype="application/x-mpegurl",
        headers={
            "Content-Encoding": "gzip",
            "Content-Disposition": "attachment; filename=lista.m3u"
        }
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
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
