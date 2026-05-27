from flask import Flask, jsonify
import threading
import time
import monitor  # Certifique-se de que o arquivo monitor.py está na mesma pasta

app = Flask(__name__)

# Função que o thread vai executar
def rodar_monitor():
    while True:
        try:
            print("Monitorando canais...")
            monitor.main_loop() # Chame a função principal do seu monitor.py
        except Exception as e:
            print(f"Erro no monitor: {e}")
        time.sleep(300)  # Aguarda 5 minutos antes de rodar de novo

# Inicia o monitor em segundo plano ao ligar a API
threading.Thread(target=rodar_monitor, daemon=True).start()

@app.route('/canal/<canal_id>')
def canal(canal_id):
    # Aqui você coloca a lógica para ler o canais_ativos.json
    # e retornar o link correspondente ao canal_id
    return jsonify({"status": "API rodando", "canal": canal_id})

if __name__ == '__main__':
    app.run()
