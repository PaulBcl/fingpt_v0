import pandas as pd

def compute_stock_scores(stock_data):
    """
    Compute stock scores based on momentum, RSI, and volume.

    Parameters:
    stock_data (dict): A dictionary containing stock data.

    Returns:
    tuple: A tuple containing the top 3 stocks and the count of valid stocks.
    """
    scores = []
    for stock, data in stock_data.items():
        if data is None or len(data["price_data"]) < 20:
            continue

        price_data = data["price_data"]
        financials = data["financials"]

        # Ensure data integrity
        volume = price_data['Volume'].fillna(0).iloc[-1] if "Volume" in price_data else 0
        momentum = price_data["Close"].pct_change().iloc[-1] * 100  # % change
        pe_ratio = financials["pe_ratio"] if financials["pe_ratio"] else 15  # Default to avg P/E
        debt_equity = financials["debt_equity"] if financials["debt_equity"] else 1  # Default ratio
        roe = financials["return_on_equity"] if financials["return_on_equity"] else 0  # Default 0

        # Scoring logic (higher is better)
        momentum_score = min(max(momentum, 0), 10)
        pe_score = 10 if pe_ratio < 15 else 4 if pe_ratio < 30 else 0  # Low P/E is better
        debt_score = 10 if debt_equity < 1 else 4 if debt_equity < 2 else 0
        roe_score = 10 if roe > 0.15 else 4 if roe > 0.05 else 0

        overall_score = (momentum_score + pe_score + debt_score + roe_score) / 4

        scores.append((stock, momentum_score, pe_score, debt_score, roe_score, overall_score))

    scores = sorted(scores, key=lambda x: x[-1], reverse=True)
    return scores[:3]
