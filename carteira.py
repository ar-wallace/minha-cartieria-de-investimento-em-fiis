def pegar_preco_alternativo(ticker):
    try:
        # Usando o Fundamentus, que entrega o HTML puríssimo e direto, ideal para o GitHub Actions
        url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # No Fundamentus, os valores ficam em tabelas com a classe 'data'
        # Procuramos o texto que vem logo após a etiqueta "Cotação"
        for td in soup.find_all("td", {"class": "label"}):
            if "Cotação" in td.text:
                elemento_preco = td.find_next_sibling("td", {"class": "value"})
                if elemento_preco:
                    texto_preco = elemento_preco.text.replace(".", "").replace(",", ".").strip()
                    return float(texto_preco)
    except Exception as e:
        print(f"Erro ao buscar preço de {ticker} na fonte alternativa: {e}")
    return None
