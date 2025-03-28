import pandas as pd

def compute_stock_scores(stock_data):
    """
    Compute stock scores based on momentum, RSI, and volume.

    Parameters:
    stock_data (dict): A dictionary containing stock data.

    Returns:
    tuple: A tuple containing a list of tuples with stock data and the count of valid stocks.
    """
    scores = []
    for stock, data in stock_data.items():
        if data is None or "price_data" not in data or len(data["price_data"]) < 20:
            continue

        price_data = data["price_data"]
        financials = data.get("financials", {})  # Ensure financials exist

        # Ensure data integrity with null checks
        volume = price_data.get('Volume', pd.Series([0])).fillna(0).iloc[-1] if "Volume" in price_data else 0
        momentum = price_data["Close"].pct_change().iloc[-1] * 100 if "Close" in price_data else 0
        
        # Add null checks for financial metrics
        pe_ratio = financials.get("pe_ratio")
        if pe_ratio is None:
            pe_ratio = 15  # Default to average P/E if missing
        debt_equity = financials.get("debt_equity")
        if debt_equity is None:
            debt_equity = 1  # Default to 1 if missing
        roe = financials.get("return_on_equity")
        if roe is None:
            roe = 0  # Default to 0 if missing

        # Scoring logic (higher is better)
        momentum_score = min(max(momentum, 0), 10)
        pe_score = 10 if pe_ratio < 15 else 4 if pe_ratio < 30 else 0  # Low P/E is better
        debt_score = 10 if debt_equity < 1 else 4 if debt_equity < 2 else 0
        roe_score = 10 if roe > 0.15 else 4 if roe > 0.05 else 0

        overall_score = (momentum_score + pe_score + debt_score + roe_score) / 4

        scores.append((stock, momentum_score, pe_score, debt_score, roe_score, overall_score))

    scores = sorted(scores, key=lambda x: x[-1], reverse=True)
    return scores[:3], len(scores)  # Ensure only top 3 are returned and valid stock count is included
