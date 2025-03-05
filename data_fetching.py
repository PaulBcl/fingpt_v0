import yfinance as yf
import requests
import textblob
import streamlit as st
import os

# Check if running in Streamlit (st.secrets exists)
if hasattr(st, "secrets") and "GITHUB_ACTIONS" not in os.environ:
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", None)
else:
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Ensure the API key is available
if not NEWS_API_KEY:
    raise ValueError("❌ ERROR: NEWS_API_KEY is missing! Set it in Streamlit Secrets or GitHub Actions.")

def fetch_stock_data(stock_list):
    """
    Fetch stock data for a list of stock tickers.

    Parameters:
    stock_list (list): A list of stock tickers.

    Returns:
    dict: A dictionary containing stock data for each ticker.
    """
    stock_data = {}  # ✅ Initialize stock_data at the beginning

    for stock in stock_list:
        try:
            ticker = yf.Ticker(stock)
            data = ticker.history(period="6mo")
            info = ticker.info

            financial_data = {
                "market_cap": info.get("marketCap"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "pe_ratio": info.get("trailingPE"),
                "debt_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
                "profit_margin": info.get("profitMargins"),
                "rsi": None,  # Placeholder for RSI (to be calculated)
            }

            news_sentiment = fetch_news_sentiment(stock)  # ✅ Fetch news sentiment

            stock_data[stock] = {
                "price_data": data,
                "financials": financial_data,
                "news_sentiment": news_sentiment  # ✅ Store in stock_data
            }

        except Exception as e:
            print(f"Error fetching {stock}: {e}")
            stock_data[stock] = None


    return stock_data

def fetch_news_sentiment(stock):
    """
    Fetch financial news for a stock and analyze sentiment.

    Parameters:
    - stock (str): Stock ticker.

    Returns:
    - float: Sentiment score (-1 to 1), where:
        - Positive = Bullish sentiment
        - Negative = Bearish sentiment
        - 0 = Neutral sentiment
    """
    url = f"https://newsapi.org/v2/everything?q={stock}&language=en&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])

        sentiment_scores = []
        for article in articles[:5]:  # Only analyze top 5 articles
            text = article.get("title", "") + " " + article.get("description", "")
            sentiment = textblob.TextBlob(text).sentiment.polarity
            sentiment_scores.append(sentiment)

        if sentiment_scores:
            return sum(sentiment_scores) / len(sentiment_scores)  # Average sentiment score
        else:
            return 0  # Neutral sentiment if no news found

    except Exception as e:
        print(f"Error fetching news sentiment for {stock}: {e}")
        return 0  # Default to neutral if error occurs
