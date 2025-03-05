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
            data = yf.Ticker(stock).history(period='3mo')
            if data.empty:
                print(f"No data available for {stock}")
                stock_data[stock] = None
            else:
                stock_data[stock] = data
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
            stock_data[stock] = None
    return stock_data
