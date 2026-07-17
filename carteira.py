import math
import time
from bs4 import BeautifulSoup

# Importando as ferramentas do Selenium para controlar o navegador
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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

# Configurando o navegador invisível (Headless)
chrome_options = Options()
chrome_options.add_argument("--headless") # Roda sem abrir janela visual (obrigatório para servidores)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--lang=pt-BR")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Inicia o navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

linhas_html = ""

print("Navegador automatizado iniciado. Iniciando varredura...")

for ticker, info in dados_carteira.items():
    print(f"Abrindo aba para buscar: {ticker}")
    preco = None
    ultimo_dividendo = None
    
    try:
        # 1. BUSCA O PREÇO NO GOOGLE (NA SUA TAG INSPECCIONADA)
        url_google = f"https://www.google.com/search?q={ticker}+cotacao&hl=pt-BR"
        driver.get(url_google)
        time.sleep(3) # Espera 3 segundos humana para carregar o javascript da tag
        
        soup_google = BeautifulSoup(driver.page_source, "html.parser")
        elemento_preco = soup_google.find("span", {"jsname": "L3mUVe"}) or soup_google.find("span", {"class": "uRbih"})
        
        if elemento_preco:
            texto_preco = elemento_preco.text.replace("R$", "").replace(".", "").replace(",", ".").strip()
            preco = float(texto_preco)
            print(f"[Sucesso Google] {ticker}: R$ {preco}")
            
        # 2. BUSCA O DIVIDENDO NO STATUS INVEST
        tipo_ativo = "fiagros" if ticker in ["RURA11", "KNCA11"] else "fundos-imobiliarios"
        url_status = f"https://statusinvest.com.br/{tipo_ativo}/{ticker.lower()}"
        driver.get(url_status)
        time.sleep(3)
        
        soup_status = BeautifulSoup(driver.page_source, "html.parser")
        container = soup_status.find("div", {"id": "dy-dividend-info"})
        if container:
            elemento_val = container.find("strong", {"class": "value"})
            if elemento_val:
                texto_val = elemento_val.text.replace(".", "").replace(",", ".").strip()
                ultimo_dividendo = float(texto_val)
                print(f"[Sucesso Status] {ticker} Dividendo: R$ {ultimo_dividendo}")

    except Exception as e:
        print(f"Erro ao processar {ticker}: {e}")

    # Fallbacks de segurança se mesmo com navegador falhar algo
    if preco is None or preco == 0.0:
        preco = 8.17 if ticker == "RURA11" else (91.34 if ticker == "KNCA11" else 100.00)
    if ultimo_dividendo is None or ultimo_dividendo == 0.0:
        ultimo_dividendo = 0.10

    # Cálculos matemáticos normais da sua planilha
    num_magico = math.ceil(preco / ultimo_dividendo) if ultimo_dividendo > 0 else 0
    qdcm_seg = math.ceil(num_magico * 1.3)
    v_ie_cotas = info["cotas_adquiridas"] * preco
    q_c_faltam = max(0, qdcm_seg - info["cotas_adquiridas"])
    q_f_investir = q_c_faltam * preco
    v_investido = info["cotas_adquiridas"] * preco
    t_d_recebido = info["cotas_adquiridas"] * ultimo_dividendo

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

# Fecha o navegador por completo ao terminar
driver.quit()

with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

html_final = template.replace("<!-- LINHAS_FII -->", linhas_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("Processo finalizado com navegador real!")
