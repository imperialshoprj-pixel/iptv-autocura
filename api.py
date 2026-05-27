from flask import Flask, jsonify
import threading
import time
import monitor

app = Flask(__name__)

def run_monitor():
    while True:
        try:
            print("Monitoring channels...")
            monitor.atualizar_links() 
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)

threading.Thread(target=run_monitor, daemon=True).start()

@app.route('/canal/<canal_name>')
def canal(canal_name):
    return jsonify({"status": "API is running", "channel": canal_name})

if __name__ == '__main__':
    app.run()
