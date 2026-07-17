import pandas as pd
import math

# Dados da sua carteira (Você altera a quantidade de cotas direto aqui!)
# Formato: "TICKER": [Preço Atual, Média de Dividendos, Cotas Adquiridas]
dados_carteira = {
    "KNRI11": [165.20, 1.00, 10], "HGLG11": [168.50, 1.10, 5],
    "XPML11": [112.10, 0.92, 12], "MXRF11": [10.15, 0.09, 50],
    "RURA11": [10.20, 0.10, 0],  "GARE11": [9.10, 0.08, 20],
    "VISC11": [120.00, 0.85, 2],  "BTLG11": [104.50, 0.76, 8],
    "GGRC11": [11.30, 0.09, 0],  "BRCO11": [118.00, 0.87, 5],
    "HGBS11": [220.00, 1.45, 1],  "IRIM11": [78.00, 0.65, 0],
    "XPLG11": [106.00, 0.78, 7],  "RBRR11": [92.50, 0.82, 15],
    "PMLL11": [98.00, 0.70, 0],  "KNCR11": [102.30, 1.05, 10],
    "KNCA11": [104.10, 1.10, 30], "KNSC11": [91.20, 0.80, 0],
    "CPSH11": [110.00, 0.85, 0],  "DEVA11": [42.00, 0.45, 10]
}

df = pd.DataFrame.from_dict(
    dados_carteira, orient='index', 
    columns=['Preço', 'Dividendo_Medio', 'Cotas_Adquiridas']
)
df.index.name = 'Ativo'

# Cálculos Financeiros Automatizados
df['Valor_Investido'] = df['Cotas_Adquiridas'] * df['Preço']
df['Num_Magico'] = (df['Preço'] / df['Dividendo_Medio']).apply(math.ceil)
df['Qtd_Cotas_Faltam'] = (df['Num_Magico'] - df['Cotas_Adquiridas']).clip(lower=0)
df['Valor_Falta_Investir'] = df['Qtd_Cotas_Faltam'] * df['Preço']

# Gerando a página de relatório em HTML
html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de FIIs</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f4f6f9; color: #333; }}
        h2 {{ color: #111; }}
        table {{ border-collapse: collapse; width: 100%; background: white; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #24292e; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .resumo {{ margin-top: 30px; padding: 20px; background: #e1e4e8; border-left: 6px solid #24292e; border-radius: 4px; }}
    </style>
</head>
<body>
    <h2>📊 Minha Carteira de FIIs</h2>
    <p>Relatório gerado automaticamente através do Python.</p>
    
    {{df.to_html(classes='tabela-fiis')}}

    <div class="resumo">
        <h3>💰 Resumo Patrimonial Geral</h3>
        <p><strong>Total Investido Atual:</strong> R$ {{df['Valor_Investido'].sum():,.2f}}</p>
        <p><strong>Falta Aportar para o Número Mágico global:</strong> R$ {{df['Valor_Falta_Investir'].sum():,.2f}}</p>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Tabela index.html atualizada com sucesso!")
