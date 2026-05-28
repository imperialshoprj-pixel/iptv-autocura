def carregar_catalogo():
    if not os.path.exists(JSON_PATH):
        return {}
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verifica se o JSON ainda está no formato antigo (apenas URL)
    # Se for, ele transforma em tempo real para o formato novo
    primeiro_item = list(data.values())[0]
    if isinstance(primeiro_item, str):
        novo_catalogo = {}
        for cid, url in data.items():
            novo_catalogo[cid] = {
                "titulo": f"Canal {cid}",
                "capa": "https://via.placeholder.com/200x300",
                "url": url,
                "genero": "Diversos"
            }
        return novo_catalogo
        
    return data # Já está no formato novo
