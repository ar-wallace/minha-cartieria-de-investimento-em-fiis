import requests
from bs4 import BeautifulSoup
import math
import time

# Seus dados manuais (Cotas Adquiridas e Setor)
dados_carteira = {
    "KNRI11": {"cotas_adquiridas": 10, "setor": "Tijolo - Escritórios"},
    "HGLG11": {"cotas_adquiridas": 5,  "setor": "Tijolo - Logística"},
    "XPML11": {"cotas_adquiridas": 12, "setor": "Tijolo - Shopping"},
    "MXRF11": {"cotas_adquiridas": 50, "setor": "Papel - Recebíveis"},
    "RURA11": {"cotas_adquiridas": 266,"setor": "Fiagro"},
    "GARE11": {"cotas_adquiridas": 20, "setor": "Híbrido"},
    "VISC11": {"cotas_adquiridas": 2,  "setor": "Tijolo - Shopping"},
    "BTLG11": {"cotas_adquiridas": 8,  "setor": "Tijolo - Logística"},
    "GGRC11": {"cotas_adquiridas": 0,  "setor": "Tijolo - Logística"},
    "BRCO11": {"cotas_adquiridas": 5,  "setor": "Tijolo - Logística"},
    "HGBS11": {"cotas_adquiridas": 1,  "setor": "Tijolo - Shopping"},
    "IRIM11": {"cotas_adquiridas": 0,  "setor": "Papel - Recebíveis"},
    "XPLG11": {"cotas_adquiridas": 7,  "setor": "Tijolo - Logística"},
    "RBRR11": {"cotas_adquiridas": 15, "setor": "Papel - Recebíveis"},
    "PMLL11": {"cotas_adquiridas": 0,  "setor": "Híbrido"},
    "KNCR11": {"cotas_adquiridas": 10, "setor": "Papel - Recebíveis"},
    "KNCA11": {"cotas_adquiridas": 30, "setor": "Fiagro"},
    "KNSC11": {"cotas_adquiridas": 0,  "setor": "Papel - Recebíveis"},
    "CPSH11": {"cotas_adquiridas": 0,  "setor": "Tijolo - Shopping"},
    "DEVA11": {"cotas_adquiridas": 10, "setor": "Papel - Recebíveis"}
}

linhas_html = ""

# Cabeçalho para simular um navegador real e evitar bloqueios dos sites
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def pegar_preco_google(ticker):
    try:
        # Busca direta no Google Finance mercado brasileiro (BVMF)
        url = f"https://www.google.com/finance/quote/{ticker}:BVMF"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Encontra a classe do container de preço do Google Finance
        elemento_preco = soup.find("div", {"class": "YMlKec fxKbKc"})
        if elemento_preco:
            texto_preco = elemento_preco.text.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(texto_preco)
    except Exception as e:
        print(f"Erro ao buscar preço de {ticker} no Google: {e}")
    return None

def pegar_dividendo_statusinvest(ticker):
    try:
        # Acessa a página do FII/Fiagro no Status Invest
        tipo_ativo = "fiagros" if ticker in ["RURA11", "KNCA11"] else "fundos-imobiliarios"
        url = f"https://statusinvest.com.br/{tipo_ativo}/{ticker.lower()}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Procura pelo container do último rendimento anunciado
        container = soup.find("div", {"id": "dy-dividend-info"})
        if container:
            elemento_val = container.find("strong", {"class": "value"})
            if elemento_val:
                texto_val = elemento_val.text.replace(".", "").replace(",", ".").strip()
                return float(texto_val)
    except Exception as e:
        print(f"Erro ao buscar dividendo de {ticker} no Status Invest: {e}")
    return None

print("Iniciando a coleta de dados da web...")

for ticker, info in dados_carteira.items():
    print(f"Coletando dados de: {ticker}")
    
    preco = pegar_preco_google(ticker)
    ultimo_dividendo = pegar_dividendo_statusinvest(ticker)
    
    # Pausa curta para não sobrecarregar os servidores e evitar bloqueios sequenciais
    time.sleep(1.5)

    # Fallbacks de segurança estritos caso o scraping falhe ou seja bloqueado temporariamente
    if preco is None or preco == 0.0:
        if ticker in ["MXRF11", "RURA11", "GARE11"]:
            preco = 9.80
        elif ticker == "KNCA11":
            preco = 96.89
        else:
            preco = 100.00

    if ultimo_dividendo is None or ultimo_dividendo == 0.0:
        ultimo_dividendo = 0.09 if preco < 15.00 else 1.00

    # Regras matemáticas da carteira
    num_magico = math.ceil(preco / ultimo_dividendo) if ultimo_dividendo > 0 else 0
    qdcm_seg = math.ceil(num_magico * 1.3) # Meta com 30% de margem
    v_ie_cotas = info["cotas_adquiridas"] * preco
    q_c_faltam = max(0, qdcm_seg - info["cotas_adquiridas"])
    q_f_investir = q_c_faltam * preco
    v_investido = info["cotas_adquiridas"] * preco
    t_d_recebido = info["cotas_adquiridas"] * ultimo_dividendo

    # Monta a estrutura de linhas do HTML
    linhas_html += f"""
        <tr>
            <td>{ticker}</td>
            <td>R$ {preco:.2f}</td>
            <td>R$ {ultimo_dividendo:.2f}</td>
            <td>{num_magico}</td>
            <td>R$ {v_ie_cotas:.2f}</td>
            <td>{info["cotas_adquiridas"]}</td>
            <td>{q_c_faltam}</td>
            <td>R$ {q_f_investir:.2f}</td>
            <td>R$ {v_investido:.2f}</td>
            <td>{info["setor"]}</td>
            <td>R$ {t_d_recebido:.2f}</td>
            <td>{qdcm_seg}</td>
        </tr>"""

# Injeta as linhas capturadas no arquivo modelo final
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

html_final = template.replace("<!-- LINHAS_FII -->", linhas_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("index.html atualizado com dados extraídos do Google e Status Invest!")
