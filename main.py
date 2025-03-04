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
from concurrent.futures import ThreadPoolExecutor
import ta  # For technical indicators like RSI

# Expand Streamlit to full width
st.set_page_config(layout="wide")

# OpenAI API Key (Replace with your own key)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

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
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA', 'RNO.PA', 'ACA.PA', 'BN.PA', 'AI.PA', 'STM.PA', 'CAP.PA']
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS', 'BABA', 'TCEHY', 'JD', 'NTES', 'SE', 'SONY']
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI', 'COIN', 'AMD', 'RBLX', 'UPST', 'CRWD', 'FSLY', 'NET']
ALL_STOCKS = FRANCE_STOCKS + ASIA_STOCKS + US_STOCKS

# API Limit Configuration
NEWSAPI_LIMIT = 1000
NEWSAPI_KEY = "c45a33e5851c470ea9d6bdbab7dab14c"

# Enable auto-refresh
refresh_interval = st.sidebar.slider("Auto-refresh interval (minutes)", 1, 30, 30)

# Batch fetch stock data for multiple tickers at once
@st.experimental_memo(ttl=refresh_interval * 60)
def fetch_stock_data(stock_list):
    try:
        data = yf.download(stock_list, period='3mo', group_by='ticker')
        return data
    except Exception as e:
        st.warning(f"Error fetching data: {e}")
        return {}

# Compute stock scores (using efficient calculations for RSI and volume)
@st.experimental_memo(ttl=refresh_interval * 60)
def compute_stock_scores(stock_data):
    scores = []
    for stock, data in stock_data.items():
        if data is None or len(data) < 20:
            continue

        if 'Volume' not in data.columns or data['Volume'].isna().all():
            data['Volume'] = 0
        else:
            data['Volume'].fillna(0, inplace=True)

        # Calculate momentum using percentage change
        momentum_score = min(max((data['Close'].pct_change().iloc[-1] * 200), 0), 10)

        # Use 'ta' library to compute RSI
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi().iloc[-1]
        rsi_score = 10 if rsi < 30 else 4 if rsi < 50 else 0

        rolling_avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1] if len(data) >= 20 else data['Volume'].mean()
        last_volume = data['Volume'].iloc[-1]

        if last_volume > rolling_avg_volume * 1.5:
            volume_score = 10
        elif last_volume > rolling_avg_volume:
            volume_score = 4
        else:
            volume_score = 0

        overall_score = (momentum_score + rsi_score + volume_score) / 3
        scores.append((stock, momentum_score, rsi_score, volume_score, overall_score))

    scores = sorted(scores, key=lambda x: x[4], reverse=True)
    return scores[:3]

# Generate AI commentary with improved error handling and caching
@st.experimental_memo(ttl=refresh_interval * 60)
def generate_ai_commentary(stock, momentum, rsi, volume, overall):
    prompt = (f"Analyze the stock {stock} based on the following indicators:\n"
              f"- Momentum: {momentum}%\n"
              f"- RSI: {rsi}\n"
              f"- Volume: {volume}\n"
              f"Provide a concise investment recommendation without extensive explanations.")

    try:
        if not OPENAI_API_KEY:
            return "AI analysis unavailable: OpenAI API key is missing."
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing stock investment insights."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        return f"AI analysis unavailable: {str(e)}"
    except openai.AuthenticationError:
        return "AI analysis unavailable: Invalid OpenAI API key."
    except openai.RateLimitError:
        return "AI analysis unavailable: Rate limit exceeded. Try again later."
    except Exception as e:
        return f"AI analysis unavailable due to an unexpected error: {str(e)}"

# Fetch top stocks (asynchronously, if necessary, using ThreadPoolExecutor)
with ThreadPoolExecutor() as executor:
    stock_data = fetch_stock_data(ALL_STOCKS)
    top_stocks = compute_stock_scores(stock_data)

# Display top stocks and generate AI commentary
st.subheader("🏆 Top 3 Stock Picks Overall")
df_top_stocks = pd.DataFrame(top_stocks, columns=["Stock", "Momentum Score", "RSI Score", "Volume Score", "Overall Score"])
df_top_stocks = df_top_stocks.round(2)
st.dataframe(df_top_stocks)

st.subheader("💡 AI-Powered Investment Insights")
for stock, momentum, rsi, volume, overall in top_stocks:
    ai_comment = generate_ai_commentary(stock, momentum, rsi, volume, overall)
    st.write(f"📊 **{stock} Analysis:**")
    stock_df = pd.DataFrame({
        "Indicator": ["Momentum %", "RSI", "Volume"],
        "Value": [momentum, rsi, volume]
    })
    st.table(stock_df)
    st.write(f"💬 **AI Insight:** {ai_comment}")

    # Plot only the last 30 days of data
    fig = px.line(stock_data[stock].tail(30), x=stock_data[stock].tail(30).index, y=["Close", "Volume"], title=f"{stock} Price & Volume (Last 30 Days)")
    st.plotly_chart(fig)

# Add refresh button
def refresh_data():
    if 'refresh_triggered' not in st.session_state or not st.session_state.refresh_triggered:
        st.session_state.refresh_triggered = True
        st.experimental_rerun()
    st.session_state.refresh_triggered = True
    st.experimental_rerun()

if st.sidebar.button("🔄 Refresh Data"):
    refresh_data()

st.write("### AI Stock Picker - Live Updates Enabled")
st.write("Stock picks based on momentum, volume, sentiment, and trend alerts.")
st.write(f"⏳ Data refreshes every {refresh_interval} minutes automatically. You can also refresh manually using the button.")
