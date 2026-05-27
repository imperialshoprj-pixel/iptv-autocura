# converter_lista.py
# Este script lê sua lista original e aponta os links para a sua API

# O IP que apareceu no seu CMD
IP_API = "10.165.132.109" 

with open('lista.m3u8', 'r', encoding='utf-8') as f:
    linhas = f.readlines()

with open('lista_autocura.m3u', 'w', encoding='utf-8') as novo:
    for linha in linhas:
        if linha.startswith('http'):
            # Esta lógica assume que o ID do canal na API é baseado no final do link original
            # Se precisar de um mapeamento mais preciso, teremos que ajustar
            canal_id = linha.strip().split('/')[-1]
            novo.write(f"http://{IP_API}:5000/canal/{canal_id}\n")
        else:
            novo.write(linha)

print("Arquivo 'lista_autocura.m3u' criado com sucesso!")