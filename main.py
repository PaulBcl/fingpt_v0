import yfinance as yf
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import openai
from textblob import TextBlob
import datetime
import time
import os
import streamlit as st
import openai

# Expand Streamlit to full width
st.set_page_config(layout="wide")

# OpenAI API Key (Replace with your own key)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# Expander to show example recommendation
with st.expander("📌 Example Stock Recommendation", expanded=False):
    st.write("Here is an example of what a stock recommendation might look like based on our strategy:")
    example_df = pd.DataFrame({
        "Stock": ["NVDA"],
        "Momentum %": [7.85],
        "RSI": [45.6],
        "SMA20": [320.45],
        "MACD": [2.45],
        "Bollinger High": [330.0],
        "Bollinger Low": [310.0],
        "Volume Surge": [True],
        "Trend Alert": ["📈 Uptrend detected"]
    })
    st.dataframe(example_df)

# Define stock pools with more tickers
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA', 'RNO.PA', 'ACA.PA', 'BN.PA', 'AI.PA', 'STM.PA', 'CAP.PA']  # Expanded mid-cap list
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS', 'BABA', 'TCEHY', 'JD', 'NTES', 'SE', 'SONY']  # Expanded Asia stocks
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI', 'COIN', 'AMD', 'RBLX', 'UPST', 'CRWD', 'FSLY', 'NET']  # Growth & small-cap stocks
ALL_STOCKS = FRANCE_STOCKS + ASIA_STOCKS + US_STOCKS

# API Limit Configuration
NEWSAPI_LIMIT = 1000  # Adjust based on your NewsAPI plan
NEWSAPI_KEY = "c45a33e5851c470ea9d6bdbab7dab14c"

# Enable auto-refresh
refresh_interval = st.sidebar.slider("Auto-refresh interval (minutes)", 1, 30, 5)

@st.cache_data(ttl=refresh_interval * 60)
def fetch_stock_data(stock_list):
    stock_data = {}
    for stock in stock_list:
        try:
            data = yf.Ticker(stock).history(period='3mo')
            stock_data[stock] = data
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
    return stock_data

# Fetch stock data
stock_data = fetch_stock_data(ALL_STOCKS)

# Compute stock scores
def compute_stock_scores(stock_data):
    scores = []
    for stock, data in stock_data.items():
        if len(data) < 20:
            continue

        # Ensure 'Volume' column exists and fill NaNs
        if 'Volume' not in data.columns or data['Volume'].isna().all():
            data['Volume'] = 0  # Default volume if missing
        else:
            data['Volume'].fillna(0, inplace=True)  # Fill NaNs with 0

        momentum_score = min(max((data['Close'].pct_change().iloc[-1] * 200), 0), 10)
        rsi = data['Close'].rolling(window=14).mean().iloc[-1]
        rsi_score = 10 if rsi < 30 else 4 if rsi < 50 else 0
        volume_score = 10 if data['Volume'].iloc[-1] > data['Volume'].rolling(window=20).mean() * 1.5 else 4 if data['Volume'].iloc[-1] > data['Volume'].rolling(window=20).mean() else 0

        overall_score = (momentum_score + rsi_score + volume_score) / 3
        scores.append((stock, momentum_score, rsi_score, volume_score, overall_score))

    scores = sorted(scores, key=lambda x: x[4], reverse=True)
    return scores[:5]

# Fetch top 5 stocks
top_stocks = compute_stock_scores(stock_data)

# Generate AI-based commentary
def generate_ai_commentary(stock, momentum, rsi, volume, overall):
    prompt = (f"Analyze the stock {stock} based on the following indicators: \n"
              f"- Momentum Score: {momentum}/10 \n"
              f"- RSI Score: {rsi}/10 \n"
              f"- Volume Score: {volume}/10 \n"
              f"- Overall Score: {overall}/10 \n"
              f"Provide a short investment recommendation, stating whether it's a good buy, hold, or avoid.")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a financial analyst providing stock investment insights."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Display top 5 stocks with AI commentary
st.subheader("🏆 Top 5 Stock Picks Overall")
df_top_stocks = pd.DataFrame(top_stocks, columns=["Stock", "Momentum Score", "RSI Score", "Volume Score", "Overall Score"])
st.dataframe(df_top_stocks)

st.subheader("💡 AI-Powered Investment Insights")
for stock, momentum, rsi, volume, overall in top_stocks:
    ai_comment = generate_ai_commentary(stock, momentum, rsi, volume, overall)
    st.write(f"**{stock} Analysis:** {ai_comment}")

# Add refresh button
def refresh_data():
    st.experimental_rerun()

if st.sidebar.button("🔄 Refresh Data"):
    refresh_data()

st.write("### AI Stock Picker - Live Updates Enabled")
st.write("Stock picks based on momentum, volume, sentiment, and trend alerts.")

st.write(f"⏳ Data refreshes every {refresh_interval} minutes automatically. You can also refresh manually using the button.")
