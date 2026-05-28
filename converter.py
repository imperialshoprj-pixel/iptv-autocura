import json
import re

def converter_m3u_para_json():
    # Cole o conteúdo da sua lista M3U entre aspas triplas abaixo:
    lista_m3u = """
    #EXTINF:-1 tvg-id="" tvg-name="#ComVocê: Volume: 1 (2021)" tvg-logo="" group-title="Filmes | Comedia",#ComVocê: Volume: 1 (2021)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/129833.mp4
#EXTINF:-1 tvg-id="" tvg-name="#PartiuFama: Cancelado no Amor (2022)" tvg-logo="" group-title="Filmes | Comedia",#PartiuFama: Cancelado no Amor (2022)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/91070.mp4
#EXTINF:-1 tvg-id="" tvg-name="#SalveRosa (2025)" tvg-logo="" group-title="Filmes | Suspense",#SalveRosa (2025)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/965506.mp4
#EXTINF:-1 tvg-id="" tvg-name="#SeAcabó: Diário das Campeãs (2024)" tvg-logo="" group-title="Filmes | Documentarios",#SeAcabó: Diário das Campeãs (2024)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/222959.mp4
#EXTINF:-1 tvg-id="" tvg-name="(500) Dias com Ela (2009)" tvg-logo="" group-title="Filmes | Comedia",(500) Dias com Ela (2009)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/166538.mp4
#EXTINF:-1 tvg-id="" tvg-name="(Des)controle (2026)" tvg-logo="" group-title="Filmes | Lancamentos 2026",(Des)controle (2026)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/1006027.mp4
#EXTINF:-1 tvg-id="" tvg-name="(Re)Nascer (2023)" tvg-logo="" group-title="Filmes | Drama",(Re)Nascer (2023)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/189826.mp4
#EXTINF:-1 tvg-id="" tvg-name="+ Velozes + Furiosos (2003)" tvg-logo="" group-title="Filmes | Acao",+ Velozes + Furiosos (2003)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/88164.mp4
#EXTINF:-1 tvg-id="" tvg-name="...E o Vento Levou (1939)" tvg-logo="" group-title="Filmes | Drama",...E o Vento Levou (1939)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/81610.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 - Permissão para Matar (1989)" tvg-logo="" group-title="Filmes | Aventura",007 - Permissão para Matar (1989)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135577.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 A Serviço Secreto de Sua Majestade (1969)" tvg-logo="" group-title="Filmes | Aventura",007 A Serviço Secreto de Sua Majestade (1969)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135557.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Cassino Royale (2006)" tvg-logo="" group-title="Filmes | Aventura",007 Cassino Royale (2006)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/74801.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Contra GoldenEye (1995)" tvg-logo="" group-title="Filmes | Aventura",007 Contra GoldenEye (1995)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/941147.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Contra Goldfinger (1964)" tvg-logo="" group-title="Filmes | Aventura",007 Contra Goldfinger (1964)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135552.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Contra Octopussy (1983)" tvg-logo="" group-title="Filmes | Aventura",007 Contra Octopussy (1983)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135574.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Contra Spectre (2015)" tvg-logo="" group-title="Filmes | Acao",007 Contra Spectre (2015)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/73050.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Contra o Foguete da Morte (1979)" tvg-logo="" group-title="Filmes | Acao",007 Contra o Foguete da Morte (1979)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135572.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Contra o Homem com a Pistola de Ouro (1974)" tvg-logo="" group-title="Filmes | Aventura",007 Contra o Homem com a Pistola de Ouro (1974)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135570.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Na Mira dos Assassinos (1985)" tvg-logo="" group-title="Filmes | Aventura",007 Na Mira dos Assassinos (1985)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/948904.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Operação Skyfall (2012)" tvg-logo="" group-title="Filmes | Acao",007 Operação Skyfall (2012)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/48343.mp4
#EXTINF:-1 tvg-id="" tvg-name="007 Quantum of Solace (2008)" tvg-logo="" group-title="Filmes | Aventura",007 Quantum of Solace (2008)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/74802.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Contra a Chantagem Atômica (1965)" tvg-logo="" group-title="Filmes | Aventura",007: Contra a Chantagem Atômica (1965)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135555.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Contra o Satânico Dr. No (1962)" tvg-logo="" group-title="Filmes | Aventura",007: Contra o Satânico Dr. No (1962)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135553.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Marcado para a Morte (1987)" tvg-logo="" group-title="Filmes | Aventura",007: Marcado para a Morte (1987)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135576.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Nunca Mais Outra Vez (1983)" tvg-logo="" group-title="Filmes | Aventura",007: Nunca Mais Outra Vez (1983)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/969093.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: O Amanhã Nunca Morre (1997)" tvg-logo="" group-title="Filmes | Aventura",007: O Amanhã Nunca Morre (1997)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135578.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: O Espião Que Me Amava (1977)" tvg-logo="" group-title="Filmes | Aventura",007: O Espião Que Me Amava (1977)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135571.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: O Mundo Não é o Bastante (1999)" tvg-logo="" group-title="Filmes | Acao",007: O Mundo Não é o Bastante (1999)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135579.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Operação Skyfall (2012)" tvg-logo="" group-title="Filmes | Acao",007: Operação Skyfall (2012)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/131081.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Os Diamantes São Eternos (1971)" tvg-logo="" group-title="Filmes | Aventura",007: Os Diamantes São Eternos (1971)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135558.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Sem Tempo para Morrer (2021)" tvg-logo="" group-title="Filmes | Acao",007: Sem Tempo para Morrer (2021)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/83017.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Somente para Seus Olhos (1981)" tvg-logo="" group-title="Filmes | Aventura",007: Somente para Seus Olhos (1981)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135573.mp4
#EXTINF:-1 tvg-id="" tvg-name="007: Um Novo Dia para Morrer (2002)" tvg-logo="" group-title="Filmes | Aventura",007: Um Novo Dia para Morrer (2002)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/135580.mp4
#EXTINF:-1 tvg-id="" tvg-name="1 Dia, 2 Pais (1997) [L]" tvg-logo="" group-title="Filmes | Legendados",1 Dia, 2 Pais (1997) [L]
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/986993.mp4
#EXTINF:-1 tvg-id="" tvg-name="1 Milhão de Seguidores (2024)" tvg-logo="" group-title="Filmes | Suspense",1 Milhão de Seguidores (2024)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/1006780.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Anos de Pura Amizade (2012)" tvg-logo="" group-title="Filmes | Comedia",10 Anos de Pura Amizade (2012)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/166531.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Coisas Que Deveríamos Fazer Antes de Nos Separar (2020)" tvg-logo="" group-title="Filmes | Drama",10 Coisas Que Deveríamos Fazer Antes de Nos Separar (2020)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/71261.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Coisas Que Eu Odeio em Você (1999)" tvg-logo="" group-title="Filmes | Comedia",10 Coisas Que Eu Odeio em Você (1999)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/48378.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Dias de um Homem Bom (2023)" tvg-logo="" group-title="Filmes | Misterio",10 Dias de um Homem Bom (2023)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/107643.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Dias de um Homem Curioso (2024)" tvg-logo="" group-title="Filmes | Crime",10 Dias de um Homem Curioso (2024)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/223811.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Dias de um Homem Mau (2023)" tvg-logo="" group-title="Filmes | Crime",10 Dias de um Homem Mau (2023)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/133530.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Horas para o Natal (2020)" tvg-logo="" group-title="Filmes | Especial de Natal",10 Horas para o Natal (2020)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/166533.mp4
#EXTINF:-1 tvg-id="" tvg-name="10 Regras Para Salvar um Casamento (2023)" tvg-logo="" group-title="Filmes | Romance",10 Regras Para Salvar um Casamento (2023)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/1006212.mp4
#EXTINF:-1 tvg-id="" tvg-name="10.000 A.C. (2008)" tvg-logo="" group-title="Filmes | Aventura",10.000 A.C. (2008)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/112031.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Coisas (2018)" tvg-logo="" group-title="Filmes | Comedia",100 Coisas (2018)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/87214.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Coisas para Fazer Antes de Virar Zumbi (2023)" tvg-logo="" group-title="Filmes | Comedia",100 Coisas para Fazer Antes de Virar Zumbi (2023)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/132860.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Dias de Resistência (2019)" tvg-logo="" group-title="Filmes | Guerra",100 Dias de Resistência (2019)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/152449.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Escovadas Antes de Dormir (2005)" tvg-logo="" group-title="Filmes | Drama",100 Escovadas Antes de Dormir (2005)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/222571.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Garotas (2000)" tvg-logo="" group-title="Filmes | Comedia",100 Garotas (2000)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/166534.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Medos - 2022" tvg-logo="" group-title="Filmes | Comedia",100 Medos - 2022
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/91351.mp4
#EXTINF:-1 tvg-id="" tvg-name="100 Metros (2016)" tvg-logo="" group-title="Filmes | Comedia",100 Metros (2016)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/184012.mp4
#EXTINF:-1 tvg-id="" tvg-name="100% Lobo (2020)" tvg-logo="" group-title="Filmes | Infantil",100% Lobo (2020)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/217815.mp4
#EXTINF:-1 tvg-id="" tvg-name="100% Lobo (2020) [L]" tvg-logo="" group-title="Filmes | Legendados",100% Lobo (2020) [L]
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/971338.mp4
#EXTINF:-1 tvg-id="" tvg-name="101 Dálmatas (1996)" tvg-logo="" group-title="Filmes | Infantil",101 Dálmatas (1996)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/81538.mp4
#EXTINF:-1 tvg-id="" tvg-name="101 Dálmatas II: A Aventura de Patch em Londres (2003)" tvg-logo="" group-title="Filmes | Familia",101 Dálmatas II: A Aventura de Patch em Londres (2003)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/49697.mp4
#EXTINF:-1 tvg-id="" tvg-name="10DANCE (2025)" tvg-logo="" group-title="Filmes | Romance",10DANCE (2025)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/964839.mp4
#EXTINF:-1 tvg-id="" tvg-name="10x10 (2019)" tvg-logo="" group-title="Filmes | Drama",10x10 (2019)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/64499.mp4
#EXTINF:-1 tvg-id="" tvg-name="10x10: O Cativeiro (2018)" tvg-logo="" group-title="Filmes | Drama",10x10: O Cativeiro (2018)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/203649.mp4
#EXTINF:-1 tvg-id="" tvg-name="11/09: Os Quatro Voos Fatais (2021)" tvg-logo="" group-title="Filmes | Documentarios",11/09: Os Quatro Voos Fatais (2021)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/217183.mp4
#EXTINF:-1 tvg-id="" tvg-name="11/9: A Vida Sob Ataque (2021)" tvg-logo="" group-title="Filmes | Documentarios",11/9: A Vida Sob Ataque (2021)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/969025.mp4
#EXTINF:-1 tvg-id="" tvg-name="12 Anos de Escravidão (2013)" tvg-logo="" group-title="Filmes | Drama",12 Anos de Escravidão (2013)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/222503.mp4
#EXTINF:-1 tvg-id="" tvg-name="12 Heróis (2018)" tvg-logo="" group-title="Filmes | Guerra",12 Heróis (2018)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/49720.mp4
#EXTINF:-1 tvg-id="" tvg-name="12 Horas (2012)" tvg-logo="" group-title="Filmes | Suspense",12 Horas (2012)
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/54551.mp4
#EXTINF:-1 tvg-id="" tvg-name="12 Horas Para Sobreviver O Ano da Eleição" tvg-logo="" group-title="Filmes | Acao",12 Horas Para Sobreviver O Ano da Eleição
http://play.dnsrot.vip/movie/huhenz/fa7kum6q4bm/60957.mp4
    """
    
    catalogo = {}
    # Regex para pegar o título e o link
    padrao = r'group-title="Filmes \| (.*?)",(.*)\n(http.*)'
    matches = re.findall(padrao, lista_m3u)
    
    for i, (genero, titulo, url) in enumerate(matches):
        catalogo[str(i)] = {
            "titulo": titulo.strip(),
            "capa": "https://via.placeholder.com/200x300", # Placeholder
            "url": url.strip(),
            "genero": genero.strip()
        }

    with open('canais.json', 'w', encoding='utf-8') as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)
    print("Conversão concluída! O canais.json foi gerado com sucesso.")

if __name__ == "__main__":
    converter_m3u_para_json()
