import requests
import json
import time
import threading
import logging
import gzip
import os
from io import BytesIO
from flask import Flask, jsonify, Response, request, abort
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configurações ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Cache de estado
canais_ativos = {}
m3u_cache = b""
lock = threading.Lock()
SENHA_PROTECAO = "minha_senha_secreta" 

# Caminho absoluto para o arquivo JSON (Garante que funcione no Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'canais.json')

# Sessão otimizada
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
        logging.info(f"Tentando ler JSON em: {JSON_PATH}")
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"ERRO CRÍTICO ao ler canais.json: {e}")
        return {}

def testar_link(canal_info):
    """
    Testa o link usando HEAD primeiro. Se falhar, tenta um GET rápido
    para contornar servidores que bloqueiam apenas requisições HEAD.
    """
    canal_id, url = canal_info
    try:
        # Tentativa 1: HEAD (Rápido)
        res = session.head(url, timeout=(3, 7), allow_redirects=True)
        if res.status_code == 200:
            return canal_id, url
        
        # Tentativa 2: GET (Fallback para servidores bloqueadores)
        res = session.get(url, timeout=(3, 7), stream=True, allow_redirects=True)
        if res.status_code == 200:
            res.close()
            return canal_id, url
            
        return canal_id, None
    except Exception:
        return canal_id, None

def gerar_m3u_comprimido(canais):
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
    if not config: 
        logging.error("Configuração vazia. Verifique se canais.json existe na raiz.")
        return
    
    logging.info(f"Monitoramento: Verificando {len(config)} canais...")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        resultados = executor.map(testar_link, config.items())
    
    novos_canais = {cid: url for cid, url in resultados if url}
    
    with lock:
        if novos_canais:
            canais_ativos = novos_canais
            m3u_cache = gerar_m3u_comprimido(novos_canais)
            logging.info(f"Monitoramento: Sucesso. {len(canais_ativos)} canais ativos.")
        else:
            logging.error("Monitoramento falhou: Nenhum canal pôde ser validado.")

@app.route('/lista.m3u')
def gerar_m3u():
    if request.args.get('senha') != SENHA_PROTECAO:
        abort(403)
        
    with lock:
        if not m3u_cache:
            return "Aguardando processamento inicial dos canais...", 503
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
        "ultima_atualizacao": time.strftime('%H:%M:%S')
    })

def loop_monitoramento():
    # Primeira execução imediata ao iniciar
    atualizar_links()
    while True:
        time.sleep(300) # Intervalo de 5 minutos
        atualizar_links()

if __name__ == "__main__":
    threading.Thread(target=loop_monitoramento, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
