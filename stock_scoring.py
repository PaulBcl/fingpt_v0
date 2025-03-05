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
    valid_stock_count = 0
    for stock, data in stock_data.items():
        if data is None or len(data) < 20:
            continue

        data.loc[:, 'Volume'] = data['Volume'].fillna(0)
        momentum_score = min(max((data['Close'].pct_change().iloc[-1] * 200), 0), 10)
        rsi = data['Close'].rolling(window=14).mean().iloc[-1]
        rsi_score = 10 if rsi < 30 else 4 if rsi < 50 else 0
        rolling_avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
        last_volume = data['Volume'].iloc[-1]
        volume_score = 10 if last_volume > rolling_avg_volume * 1.5 else 4 if last_volume > rolling_avg_volume else 0
        overall_score = (momentum_score + rsi_score + volume_score) / 3
        scores.append((stock, momentum_score, rsi_score, volume_score, overall_score))
        valid_stock_count += 1

    scores = sorted(scores, key=lambda x: x[4], reverse=True)
    return scores[:3], valid_stock_count
