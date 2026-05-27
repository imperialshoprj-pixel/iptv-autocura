import requests
import json
import schedule
import time

# PREENCHA AQUI COM OS SEUS LINKS REAIS
# Você pode copiar os links do seu arquivo .m3u e colocar aqui
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

def testar_link(url):
    try:
        # Usamos stream=True para não baixar o arquivo todo, apenas o cabeçalho
        res = requests.get(url, timeout=5, stream=True)
        return res.status_code == 200
    except Exception as e:
        return False

def atualizar_links():
    print(f"[{time.strftime('%H:%M:%S')}] Testando links...")
    melhores_links = {}
    
    for canal, fontes in canais_config.items():
        canal_encontrado = False
        for fonte in fontes:
            if testar_link(fonte):
                melhores_links[canal] = fonte
                canal_encontrado = True
                break 
        
        if not canal_encontrado:
            print(f"ALERTA: Todos os links para {canal} estão offline!")
    
    with open('canais_ativos.json', 'w') as f:
        json.dump(melhores_links, f, indent=4)
    print("Arquivo 'canais_ativos.json' atualizado com sucesso.")

# Agenda para rodar a cada 5 minutos
schedule.every(5).minutes.do(atualizar_links)

if __name__ == "__main__":
    print("Sistema de Autocura Iniciado...")
    atualizar_links()
    while True:
        schedule.run_pending()
        time.sleep(1)
