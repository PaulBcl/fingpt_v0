import yfinance as yf
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from textblob import TextBlob
import datetime
import time

# Expand Streamlit to full width
st.set_page_config(layout="wide")

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
            data = yf.Ticker(stock).history(period='1mo')
            stock_data[stock] = data
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
    return stock_data

# Fetch market trends and alerts
def get_trend_alerts(stock_data):
    alerts = []
    for stock, data in stock_data.items():
        if len(data) < 10:
            continue

        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-5]
        price_change = (last_close - prev_close) / prev_close * 100

        if price_change > 5:
            alerts.append(f"📈 {stock} is on an uptrend: {price_change:.2f}% in the last 5 days")
        elif price_change < -5:
            alerts.append(f"📉 {stock} is on a downtrend: {price_change:.2f}% in the last 5 days")
    return alerts

# Fetch stock data
stock_data = fetch_stock_data(ALL_STOCKS)
trend_alerts = get_trend_alerts(stock_data)

# Display trend alerts
if trend_alerts:
    st.sidebar.subheader("🚨 Trend Alerts")
    for alert in trend_alerts:
        st.sidebar.write(alert)
else:
    st.sidebar.write("No significant trends detected.")

# Add refresh button
def refresh_data():
    st.experimental_rerun()

if st.sidebar.button("🔄 Refresh Data"):
    refresh_data()

st.write("### AI Stock Picker - Live Updates Enabled")
st.write("Stock picks based on momentum, volume, sentiment, and trend alerts.")

st.write(f"⏳ Data refreshes every {refresh_interval} minutes automatically. You can also refresh manually using the button.")
