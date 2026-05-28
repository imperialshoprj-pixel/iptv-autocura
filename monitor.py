import json, time, threading, logging, gzip, os
from io import BytesIO
from flask import Flask, Response, request
import urllib3

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Cache global
state = {"canais": {}, "m3u": b"", "last": "Aguardando..."}
lock = threading.Lock()
JSON_PATH = 'canais.json'

# Cliente HTTP sem pool persistente (mais lento, mas impossível de dar erro de pool)
http = urllib3.PoolManager(maxsize=1, block=True)

def validar_canal(cid, url):
    try:
        # Request único e isolado
        r = http.request('GET', url, timeout=3.0)
        if r.status == 200:
            return cid, url
    except: pass
    return None

def atualizar():
    if not os.path.exists(JSON_PATH): return
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    validos = {}
    # Processamento estritamente um por um (respeitoso com o servidor de origem)
    for cid, url in data.items():
        res = validar_canal(cid, url)
        if res:
            validos[res[0]] = res[1]
            time.sleep(0.5) # Pausa estratégica para não ser bloqueado por Flood
    
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
    return f"Status: OK | Canais: {len(state['canais'])} | Última: {state['last']}"

@app.route('/lista.m3u')
def m3u():
    if request.args.get('senha') != "admin": return "Erro 403", 403
    with lock:
        if not state["m3u"]: return "Processando...", 503
        return Response(state["m3u"], mimetype="application/x-mpegurl", headers={"Content-Encoding": "gzip"})

def loop():
    while True:
        atualizar()
        time.sleep(1800) # Atualiza a cada 30 minutos (mais estável)

if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
