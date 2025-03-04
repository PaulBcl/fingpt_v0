import yfinance as yf
import requests
import pandas as pd
import streamlit as st
from textblob import TextBlob
import datetime

# Define stock pools
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA']  # Replace with mid-cap tickers
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS']  # Japan, HK, Korea, India
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI']  # Growth & small-cap stocks
ALL_STOCKS = FRANCE_STOCKS + ASIA_STOCKS + US_STOCKS

# Define sentiment analysis function
def get_sentiment(text):
    sentiment = TextBlob(text).sentiment.polarity
    return sentiment

# Fetch stock data
def fetch_stock_data(stock_list):
    stock_data = {}
    for stock in stock_list:
        try:
            data = yf.Ticker(stock).history(period='1mo')
            stock_data[stock] = data
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
    return stock_data

# Fetch market news sentiment
def fetch_market_news(stock):
    url = f'https://newsapi.org/v2/everything?q={stock}&apiKey=c45a33e5851c470ea9d6bdbab7dab14c'
    response = requests.get(url).json()
    if 'articles' in response:
        headlines = [article['title'] for article in response['articles'][:5]]
        sentiment_scores = [get_sentiment(headline) for headline in headlines]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        return avg_sentiment
    return 0

# Screen stocks based on criteria
def screen_stocks(stock_data):
    selected_stocks = []
    for stock, data in stock_data.items():
        if len(data) < 10:
            continue

        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-5]
        price_change = (last_close - prev_close) / prev_close * 100

        volume_spike = data['Volume'].iloc[-1] > data['Volume'].mean() * 1.5

        if price_change > 5 and volume_spike:
            sentiment = fetch_market_news(stock)
            if sentiment > 0.1:
                selected_stocks.append((stock, price_change, sentiment))
    return selected_stocks

# Streamlit UI
st.title("AI Stock Picker")
st.write("Stock picks based on momentum, volume, and sentiment analysis.")

# Execute screening
stock_data = fetch_stock_data(ALL_STOCKS)
selected_stocks = screen_stocks(stock_data)

# Display recommendations
if selected_stocks:
    df = pd.DataFrame(selected_stocks, columns=["Stock", "Price Change (%)", "Sentiment Score"])
    df["Action"] = "BUY"
    st.dataframe(df)
else:
    st.write("No stocks meet the criteria today.")
