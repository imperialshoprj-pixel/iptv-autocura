import requests, json, time, threading, logging, gzip, os
from io import BytesIO
from flask import Flask, jsonify, Response, request, abort
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configurações Otimizadas ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Cache de estado com acesso thread-safe
state = {"canais": {}, "m3u": b"", "last_update": "N/A"}
lock = threading.Lock()
SENHA_PROTECAO = os.getenv("SENHA_PROTECAO", "minha_senha_secreta")
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canais.json')

# Session com Pool de Conexões de Alta Performance
session = requests.Session()
retries = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=retries)
session.mount("https://", adapter)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': '*/*'
})

def testar_link(item):
    canal_id, url = item
    try:
        # Timeout curto para não prender a thread
        res = session.get(url, timeout=(2, 5), stream=True)
        is_ok = 200 <= res.status_code < 400
        res.close()
        return (canal_id, url) if is_ok else None
    except:
        return None

def atualizar_links():
    try:
        if not os.path.exists(JSON_PATH): return
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Pool de threads para validação massiva
        with ThreadPoolExecutor(max_workers=60) as executor:
            resultados = list(filter(None, executor.map(testar_link, config.items())))
        
        # Gerar M3U eficientemente
        m3u = ["#EXTM3U"]
        for cid, url in resultados:
            m3u.append(f'#EXTINF:-1, {cid}')
            m3u.append(url)
        
        # Compressão Gzip em memória
        buf = BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb') as f:
            f.write("\n".join(m3u).encode('utf-8'))
        
        with lock:
            state["canais"] = dict(resultados)
            state["m3u"] = buf.getvalue()
            state["last_update"] = time.strftime('%H:%M:%S')
            
    except Exception as e:
        logging.error(f"Erro no ciclo de atualização: {e}")

@app.route('/lista.m3u')
def gerar_m3u():
    if request.args.get('senha') != SENHA_PROTECAO: abort(403)
    with lock:
        if not state["m3u"]: return "Processando...", 503
        return Response(state["m3u"], mimetype="application/x-mpegurl", headers={
            "Content-Encoding": "gzip",
            "Content-Disposition": "attachment; filename=lista.m3u"
        })

@app.route('/')
def home():
    with lock:
        return jsonify({
            "status": "online",
            "total_canais": len(state["canais"]),
            "ultima_atualizacao": state["last_update"]
        })

def daemon_worker():
    # Primeira execução imediata
    atualizar_links()
    while True:
        time.sleep(300) # Intervalo de 5 min
        atualizar_links()

if __name__ == "__main__":
    # Inicia o worker em background
    threading.Thread(target=daemon_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=10000, threaded=True)
