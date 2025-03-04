import yfinance as yf
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from textblob import TextBlob
import datetime

# Expand Streamlit to full width
st.set_page_config(layout="wide")

# Define stock pools with more tickers
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA', 'RNO.PA', 'ACA.PA', 'BN.PA', 'AI.PA', 'STM.PA', 'CAP.PA']  # Expanded mid-cap list
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS', 'BABA', 'TCEHY', 'JD', 'NTES', 'SE', 'SONY']  # Expanded Asia stocks
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI', 'COIN', 'AMD', 'RBLX', 'UPST', 'CRWD', 'FSLY', 'NET']  # Growth & small-cap stocks
ALL_STOCKS = FRANCE_STOCKS + ASIA_STOCKS + US_STOCKS

# API Limit Configuration
NEWSAPI_LIMIT = 1000  # Adjust based on your NewsAPI plan
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"  # Make sure to replace with actual API Key

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

# Fetch market news sentiment and track API usage
def fetch_market_news(stock):
    query = stock.replace(".PA", "").replace(".T", "").replace(".KQ", "")  # Simplify stock names for better search
    url = f'https://newsapi.org/v2/everything?q={query}&language=en&apiKey={c45a33e5851c470ea9d6bdbab7dab14c}'

    try:
        response = requests.get(url).json()

        # Debug: Print API response
        print(f"NewsAPI Response for {stock}: {response}")

        if 'articles' not in response or 'totalResults' not in response:
            print(f"Warning: No articles found for {stock}")
            return 0, 0

        api_usage = response.get('totalResults', 0)  # Track API usage percentage
        api_usage_percent = min((api_usage / NEWSAPI_LIMIT) * 100, 100)  # Ensure max is 100%

        headlines = [article['title'] for article in response['articles'][:5]]
        sentiment_scores = [get_sentiment(headline) for headline in headlines]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        return avg_sentiment, api_usage_percent

    except Exception as e:
        print(f"Error fetching news for {stock}: {e}")
        return 0, 0

# Screen stocks based on criteria
def screen_stocks(stock_data):
    selected_stocks = []
    momentum_top3 = []
    volume_top3 = []
    sentiment_top3 = []
    total_api_usage_percent = 0

    for stock, data in stock_data.items():
        if len(data) < 10:
            continue

        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-5]
        price_change = (last_close - prev_close) / prev_close * 100

        volume_spike = data['Volume'].iloc[-1] > data['Volume'].mean() * 1.5
        sentiment, api_usage_percent = fetch_market_news(stock)
        total_api_usage_percent += api_usage_percent

        if price_change > 5 and volume_spike and sentiment > 0.1:
            selected_stocks.append((stock, price_change, sentiment))

        momentum_top3.append((stock, price_change))
        volume_top3.append((stock, data['Volume'].iloc[-1]))
        sentiment_top3.append((stock, sentiment))

    momentum_top3.sort(key=lambda x: x[1], reverse=True)
    volume_top3.sort(key=lambda x: x[1], reverse=True)
    sentiment_top3.sort(key=lambda x: x[1], reverse=True)

    return selected_stocks, momentum_top3[:3], volume_top3[:3], sentiment_top3[:3], total_api_usage_percent

# Streamlit UI
st.title("AI Stock Picker")
st.write("Stock picks based on momentum, volume, and sentiment analysis.")

# Execute screening
stock_data = fetch_stock_data(ALL_STOCKS)
selected_stocks, top_momentum, top_volume, top_sentiment, api_usage_percent = screen_stocks(stock_data)

# Display API usage information
st.sidebar.subheader("📊 API Usage")
st.sidebar.progress(api_usage_percent / 100)
st.sidebar.write(f"NewsAPI Usage: {api_usage_percent:.2f}% of limit")

# Display recommendations in columns for a better layout
if selected_stocks:
    df = pd.DataFrame(selected_stocks, columns=["Stock", "Price Change (%)", "Sentiment Score"])
    df["Action"] = "BUY"
    st.dataframe(df)
else:
    st.write("No stocks meet all criteria today. Here are the top picks by category:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📈 Top 3 Momentum Stocks")
        df_momentum = pd.DataFrame(top_momentum, columns=["Stock", "Price Change (%)"])
        st.dataframe(df_momentum)

    with col2:
        st.subheader("📊 Top 3 Volume Surge Stocks")
        df_volume = pd.DataFrame(top_volume, columns=["Stock", "Volume"])
        st.dataframe(df_volume)

    with col3:
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
