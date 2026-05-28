import json
import time
import threading
import logging
import gzip
import os
import urllib3
from io import BytesIO
from flask import Flask, Response, request
from concurrent.futures import ThreadPoolExecutor

# Configuração de Log Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cache de estado com proteção de thread
state = {"canais": {}, "m3u": b"", "last": "Aguardando..."}
lock = threading.Lock()
JSON_PATH = 'canais.json'

# Configuração de Pool HTTP de Alta Performance
http = urllib3.PoolManager(
    maxsize=20, 
    block=True, 
    timeout=urllib3.Timeout(connect=5.0, read=10.0)
)

def validar_canal(cid, url):
    """Validação robusta com headers de navegador e tratamento de exceção."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Range': 'bytes=0-1024',
        'Referer': 'http://aguasdecoco.cdnxjp.space/',
        'X-Forwarded-For': '190.150.10.25' # IP mascarado
    }
    try:
        r = http.request('GET', url, headers=headers, redirect=True)
        # Status 200, 206 (Conteúdo parcial) e até 301/302 (Redirecionamento) são aceitos
        if r.status in [200, 206, 301, 302]:
            return cid, url
    except Exception as e:
        logger.debug(f"Canal {cid} indisponível: {e}")
    return None

def atualizar():
    """Lógica principal de atualização com tratamento de erros de arquivo."""
    if not os.path.exists(JSON_PATH):
        logger.error(f"Arquivo {JSON_PATH} não encontrado!")
        return
    
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler JSON: {e}")
        return

    logger.info(f"Iniciando ciclo de validação para {len(data)} canais.")
    
    validos = {}
    # Processamento paralelo eficiente
    with ThreadPoolExecutor(max_workers=10) as executor:
        resultados = executor.map(lambda item: validar_canal(item[0], item[1]), data.items())
        
    for res in resultados:
        if res:
            validos[res[0]] = res[1]
    
    # Atualização atômica do cache
    if validos:
        m3u = ["#EXTM3U"]
        for c, u in validos.items():
            m3u.append(f'#EXTINF:-1, {c}\n{u}')
        
        buf = BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb') as f:
            f.write("\n".join(m3u).encode('utf-8'))
        
        with lock:
            state["canais"] = validos
            state["m3u"] = buf.getvalue()
            state["last"] = time.strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Ciclo concluído. {len(validos)} canais ativos.")
    else:
        logger.warning("Nenhum canal validado com sucesso nesta rodada.")

@app.route('/')
def home():
    return f"Sistema Online | Ativos: {len(state['canais'])} | Última att: {state['last']}"

@app.route('/lista.m3u')
def m3u():
    senha = request.args.get('senha')
    if senha != "admin": return "Acesso Negado", 403
    with lock:
        if not state["m3u"]: return "Aguardando processamento inicial...", 503
        return Response(state["m3u"], mimetype="application/x-mpegurl", headers={"Content-Encoding": "gzip"})

def loop_background():
    """Loop infinito com espera inicial."""
    while True:
        atualizar()
        time.sleep(3600) # Atualiza a cada hora para poupar recursos

if __name__ == "__main__":
    # Inicia o worker em segundo plano
    threading.Thread(target=loop_background, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
