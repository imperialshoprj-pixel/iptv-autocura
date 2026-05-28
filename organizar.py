import json

def organizar_catalogo():
    with open('canais.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Defina aqui quais IDs pertencem a quais categorias
    # Exemplo: IDs de 1 a 100 são Séries, 101 a 200 são Filmes...
    for cid, info in data.items():
        cid_int = int(cid)
        
        if cid_int < 100:
            info['genero'] = 'Séries'
        elif cid_int < 500:
            info['genero'] = 'Filmes'
        else:
            info['genero'] = 'Animes'
            
    with open('canais.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Sucesso! Seu JSON foi atualizado com categorias baseadas nos IDs.")

if __name__ == "__main__":
    organizar_catalogo()
