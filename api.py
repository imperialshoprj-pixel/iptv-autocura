from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "API Online", 200

@app.route('/canal/<canal_name>')
def canal(canal_name):
    if os.path.exists('canais_ativos.json'):
        with open('canais_ativos.json', 'r') as f:
            canais = json.load(f)
            link = canais.get(canal_name)
            if link:
                return jsonify({"canal": canal_name, "link": link})
    return jsonify({"error": "Indisponivel"}), 404

if __name__ == '__main__':
    app.run()
