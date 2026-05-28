import json

def converter():
    # Carrega seu JSON atual
    with open('canais.json', 'r', encoding='utf-8') as f:
        dados_antigos = json.load(f)

    dados_novos = {}
    
    # Transforma cada item no novo formato
    for cid, url in dados_antigos.items():
        dados_novos[cid] = {
            "titulo": f"Canal ou Filme {cid}", # Você edita o nome depois
            "capa": "https://via.placeholder.com/200x300", # Placeholder padrão
            "url": url,
            "genero": "Geral"
        }

    # Salva o novo arquivo
    with open('canais_novo.json', 'w', encoding='utf-8') as f:
        json.dump(dados_novos, f, indent=4, ensure_ascii=False)
    
    print("Conversão concluída! O arquivo 'canais_novo.json' foi criado.")

if __name__ == "__main__":
    converter()
