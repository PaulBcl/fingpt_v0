import yfinance as yf
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from textblob import TextBlob
import datetime

# Define stock pools with more tickers
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA', 'RNO.PA', 'ACA.PA', 'BN.PA']  # Expanded mid-cap list
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS', 'BABA', 'TCEHY', 'JD', 'NTES']  # Expanded Asia stocks
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI', 'COIN', 'AMD', 'RBLX', 'UPST']  # Growth & small-cap stocks
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
    url = f'https://newsapi.org/v2/everything?q={stock}&apiKey=YOUR_NEWSAPI_KEY'
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
    momentum_top3 = []
    volume_top3 = []
    sentiment_top3 = []

    for stock, data in stock_data.items():
        if len(data) < 10:
            continue

        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-5]
        price_change = (last_close - prev_close) / prev_close * 100

        volume_spike = data['Volume'].iloc[-1] > data['Volume'].mean() * 1.5
        sentiment = fetch_market_news(stock)

        if price_change > 5 and volume_spike and sentiment > 0.1:
            selected_stocks.append((stock, price_change, sentiment))

        momentum_top3.append((stock, price_change))
        volume_top3.append((stock, data['Volume'].iloc[-1]))
        sentiment_top3.append((stock, sentiment))

    momentum_top3.sort(key=lambda x: x[1], reverse=True)
    volume_top3.sort(key=lambda x: x[1], reverse=True)
    sentiment_top3.sort(key=lambda x: x[1], reverse=True)

    return selected_stocks, momentum_top3[:3], volume_top3[:3], sentiment_top3[:3]

# Streamlit UI
st.title("AI Stock Picker")
st.write("Stock picks based on momentum, volume, and sentiment analysis.")

# Execute screening
stock_data = fetch_stock_data(ALL_STOCKS)
selected_stocks, top_momentum, top_volume, top_sentiment = screen_stocks(stock_data)

# Display recommendations
if selected_stocks:
    df = pd.DataFrame(selected_stocks, columns=["Stock", "Price Change (%)", "Sentiment Score"])
    df["Action"] = "BUY"
    st.dataframe(df)
else:
    st.write("No stocks meet all criteria today. Here are the top picks by category:")

    st.subheader("📈 Top 3 Momentum Stocks")
    df_momentum = pd.DataFrame(top_momentum, columns=["Stock", "Price Change (%)"])
    st.dataframe(df_momentum)

    st.subheader("📊 Top 3 Volume Surge Stocks")
    df_volume = pd.DataFrame(top_volume, columns=["Stock", "Volume"])
    st.dataframe(df_volume)

    st.subheader("📰 Top 3 Sentiment-Driven Stocks")
    df_sentiment = pd.DataFrame(top_sentiment, columns=["Stock", "Sentiment Score"])
    st.dataframe(df_sentiment)

# Plot price trends for selected stocks
if selected_stocks:
    st.subheader("📉 Stock Price Trends")
    for stock, _, _ in selected_stocks:
        data = stock_data[stock]
        fig = px.line(data, x=data.index, y='Close', title=f"{stock} Price Movement")
        st.plotly_chart(fig)
