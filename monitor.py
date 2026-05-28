import json, time, threading, logging, gzip, os
from io import BytesIO
from flask import Flask, Response, request
import urllib3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

# Cache global
state = {"canais": {}, "m3u": b"", "last": "Aguardando..."}
lock = threading.Lock()
JSON_PATH = 'canais.json'

# Cliente HTTP configurado para seguir redirecionamentos
http = urllib3.PoolManager(maxsize=1, block=True)

def validar_canal(cid, url):
    """
    Versão otimizada: simula uma SmartTV e segue redirecionamentos
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (SmartHub; SMART-TV; U; smt740; BR) AppleWebKit/537.36 (KHTML, like Gecko) SmartTV Safari/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        # redirect=True segue o caminho do servidor final
        r = http.request('GET', url, timeout=10.0, headers=headers, redirect=True)
        
        # Aceita status 200 (OK) ou 206 (Conteúdo parcial de vídeo)
        if r.status in [200, 206]:
            return cid, url
    except Exception as e:
        logging.warning(f"Erro ao validar canal {cid}: {e}")
    return None

def atualizar():
    if not os.path.exists(JSON_PATH): 
        logging.error("Arquivo canais.json não encontrado!")
        return
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logging.info(f"Iniciando validação de {len(data)} canais...")
    
    validos = {}
    # Processamento um por um respeitando o servidor de origem
    for cid, url in data.items():
        res = validar_canal(cid, url)
        if res:
            validos[res[0]] = res[1]
            logging.info(f"Canal {cid} validado com sucesso!")
        else:
            logging.warning(f"Canal {cid} falhou na validação.")
        time.sleep(0.5) # Pausa estratégica
    
    logging.info(f"Validação finalizada. Total: {len(validos)} ativos.")
    
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
        time.sleep(1800) # Atualiza a cada 30 minutos

if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
