import json, time, threading, logging, gzip, os
from io import BytesIO
from flask import Flask, Response, request
import urllib3
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Configurações
state = {"canais": {}, "m3u": b"", "last": "Aguardando..."}
lock = threading.Lock()
JSON_PATH = 'canais.json'
# Pool de conexões controlado para não saturar a rede
http = urllib3.PoolManager(maxsize=10, block=True)

def validar_canal(cid, url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Range': 'bytes=0-1024',
            'Referer': 'http://aguasdecoco.cdnxjp.space/'
            'X-Forwarded-For': '192.168.1.1'
        }
        r = http.request('GET', url, timeout=7.0, headers=headers, redirect=True)
        if r.status in [200, 206]:
            return cid, url
    except Exception as e:
        logging.debug(f"Canal {cid} falhou: {e}")
    return None

def atualizar():
    if not os.path.exists(JSON_PATH): return
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logging.info(f"Iniciando varredura paralela de {len(data)} canais...")
    
    validos = {}
    # ThreadPoolExecutor permite validar vários canais simultaneamente sem travar o app
    with ThreadPoolExecutor(max_workers=5) as executor:
        resultados = executor.map(lambda item: validar_canal(item[0], item[1]), data.items())
        
    for res in resultados:
        if res:
            validos[res[0]] = res[1]
    
    logging.info(f"Validação concluída: {len(validos)} ativos.")
    
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
            state["last"] = time.strftime('%H:%M:%S')

@app.route('/')
def home():
    return f"Status: OK | Ativos: {len(state['canais'])} | Última att: {state['last']}"

@app.route('/lista.m3u')
def m3u():
    if request.args.get('senha') != "admin": return "Erro 403", 403
    with lock:
        if not state["m3u"]: return "Processando...", 503
        return Response(state["m3u"], mimetype="application/x-mpegurl", headers={"Content-Encoding": "gzip"})

def loop():
    while True:
        atualizar()
        time.sleep(3600) # Intervalo aumentado para 1 hora (evita bloqueio)

if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
