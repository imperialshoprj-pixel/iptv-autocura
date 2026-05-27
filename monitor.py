import requests
import json
import schedule
import time
import threading
from flask import Flask, jsonify

# Configuração dos Canais
canais_config = {
    "universal_hd": [
        "http://aguasdecoco.cdnxjp.space:80/03985093485/903482930834/90",
        "http://link-backup-exemplo.com/stream"
    ],
    "warner_hd": [
        "http://aguasdecoco.cdnxjp.space:80/03985093485/903482930834/93",
        "http://link-backup-exemplo-2.com/stream"
    ]
}

app = Flask(__name__)

def testar_link(url):
    try:
        # Timeout reduzido para ser mais rápido
        res = requests.get(url, timeout=3, stream=True)
        return res.status_code == 200
    except:
        return False

def atualizar_links():
    print(f"[{time.strftime('%H:%M:%S')}] Iniciando checagem de links...")
    melhores_links = {}
    
    for canal, fontes in canais_config.items():
        for fonte in fontes:
            if testar_link(fonte):
                melhores_links[canal] = fonte
                break
    
    with open('canais_ativos.json', 'w') as f:
        json.dump(melhores_links, f, indent=4)
    print("Check-up concluído e JSON atualizado.")

# --- API ROTAS ---
@app.route('/')
def health_check():
    return "Status: Online e Operacional", 200

@app.route('/canal/<canal_id>')
def get_canal(canal_id):
    try:
        with open('canais_ativos.json', 'r') as f:
            canais = json.load(f)
            if canal_id in canais:
                return jsonify({"status": "ok", "url": canais[canal_id]})
            return jsonify({"status": "error", "message": "Canal offline"}), 404
    except:
        return jsonify({"status": "error", "message": "Aguardando processamento"}), 503

# --- FLUXO DE EXECUÇÃO ---
def rodar_api():
    # Roda o servidor Flask na porta que o Render espera (10000)
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    print("Iniciando sistema unificado...")
    
    # 1. Execução inicial forçada
    atualizar_links()
    
    # 2. Agenda o loop de monitoramento
    schedule.every(5).minutes.do(atualizar_links)
    
    # 3. Inicia a API em Thread separada (não bloqueia o monitor)
    threading.Thread(target=rodar_api, daemon=True).start()
    
    # 4. Loop principal do monitor (mantém o processo vivo)
    while True:
        schedule.run_pending()
        time.sleep(1)
