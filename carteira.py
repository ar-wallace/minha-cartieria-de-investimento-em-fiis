import requests
import math

# Seus dados manuais (Cotas Adquiridas e Setor)
# Quando comprar mais cotas, altere apenas os números aqui!
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

# Usando a API pública da UseBolsaI com a sua chave para buscar os dados reais
minha_chave = "sk_9ebd2ddf7587f98147ea61cfaaed6ad400fed15fb2ec1ca2"

for ticker, info in dados_carteira.items():
    try:
        url = f"https://api.usebolsai.com/api/v1/dividends/{ticker}?years=1"
        headers = {"X-API-Key": minha_chave, "Accept": "application/json"}
        response = requests.get(url, headers=headers).json()
        
        # Pega o preço atual (verifica os dois campos possíveis da API)
        preco = float(response.get('current_price') or response.get('close_price') or 100.00)
        
        # Pega o último dividendo pago
        ultimo_dividendo = float(response.get('last_dividend') or 0.10)
    except Exception:
        # Fallback de segurança para o script não travar se a API falhar
        preco = 10.00 if ticker in ["MXRF11", "RURA11"] else 100.00
        ultimo_dividendo = 0.09 if preco == 10.00 else 1.00

    # Executando as suas regras matemáticas:
    num_magico = math.ceil(preco / ultimo_dividendo) if ultimo_dividendo > 0 else 0
    qdcm_seg = math.ceil(num_magico * 1.3) # Número Mágico + 30% de margem
    v_ie_cotas = info["cotas_adquiridas"] * preco
    q_c_faltam = max(0, qdcm_seg - info["cotas_adquiridas"])
    q_f_investir = q_c_faltam * preco
    v_investido = info["cotas_adquiridas"] * preco
    t_d_recebido = info["cotas_adquiridas"] * ultimo_dividendo

    # Monta a linha da tabela
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

# Abre o arquivo modelo e injeta as linhas gerando o index.html finalizado
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

html_final = template.replace("<!-- LINHAS_FII -->", linhas_html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("index.html atualizado!")
