import yfinance as yf

def fetch_stock_data(stock_list):
    """
    Fetch stock data for a list of stock tickers.

    Parameters:
    stock_list (list): A list of stock tickers.

    Returns:
    dict: A dictionary containing stock data for each ticker.
    """
    stock_data = {}
    for stock in stock_list:
        try:
            ticker = yf.Ticker(stock)
            data = ticker.history(period='6mo')

            # Fetch additional company information
            info = ticker.info
            financial_data = {
                "market_cap": info.get("marketCap"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "pe_ratio": info.get("trailingPE"),
                "debt_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
                "profit_margin": info.get("profitMargins"),
            }

            stock_data[stock] = {"price_data": data, "financials": financial_data}

        except Exception as e:
            print(f"Error fetching {stock}: {e}")
            stock_data[stock] = None

    return stock_data
