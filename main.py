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

# Expand Streamlit to full width
st.set_page_config(layout="wide")

# OpenAI API Key (Replace with your own key)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

# Function to create and display a stock recommendation table
def create_stock_recommendation_table(data):
    """
    This function creates a consistent table for displaying stock recommendations
    :param data: a list of stock recommendation tuples (stock, momentum_score, rsi_score, volume_score, overall_score)
    """
    df = pd.DataFrame(data, columns=["Stock", "Momentum Score", "RSI Score", "Volume Score", "Overall Score"])
    df = df.round(2)
    st.dataframe(df)

# Expander to show example recommendation using the new function
with st.expander("📌 Example Stock Recommendation", expanded=False):
    st.write("Here is an example of what a stock recommendation might look like based on our strategy:")

    # Creating the example stock recommendation data
    example_data = [
        ("NVDA", 7.85, 45.6, 320.45, 2.45)  # Example data for NVDA
    ]

    # Call the function to display the example stock recommendation table
    create_stock_recommendation_table(example_data)

# Define stock pools with more tickers
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA', 'RNO.PA', 'ACA.PA', 'BN.PA', 'AI.PA', 'STM.PA', 'CAP.PA']
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS', 'BABA', 'TCEHY', 'JD', 'NTES', 'SE', 'SONY']
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI', 'COIN', 'AMD', 'RBLX', 'UPST', 'CRWD', 'FSLY', 'NET']
ALL_STOCKS = FRANCE_STOCKS + ASIA_STOCKS + US_STOCKS

# API Limit Configuration
NEWSAPI_LIMIT = 1000  # Adjust based on your NewsAPI plan
NEWSAPI_KEY = "c45a33e5851c470ea9d6bdbab7dab14c"

# Enable auto-refresh
refresh_interval = st.sidebar.slider("Auto-refresh interval (minutes)", 1, 30, 30)

@st.cache_data(ttl=refresh_interval * 60)
def fetch_stock_data(stock_list):
    stock_data = {}
    for stock in stock_list:
        try:
            data = yf.Ticker(stock).history(period='3mo')
            stock_data[stock] = data if not data.empty else None
        except Exception as e:
            print(f"Error fetching {stock}: {e}")
            stock_data[stock] = None
    return stock_data

# Fetch stock data
stock_data = fetch_stock_data(ALL_STOCKS)

# Compute stock scores
def compute_stock_scores(stock_data):
    scores = []
    valid_stock_count = 0  # Track the number of stocks with data
    for stock, data in stock_data.items():
        if data is None or len(data) < 20:
            continue

        # Ensure 'Volume' column exists and fill NaNs
        if 'Volume' not in data.columns or data['Volume'].isna().all():
            data['Volume'] = 0  # Default volume if missing
        else:
            data['Volume'].fillna(0, inplace=True)  # Fill NaNs with 0

        momentum_score = min(max((data['Close'].pct_change().iloc[-1] * 200), 0), 10)
        rsi = data['Close'].rolling(window=14).mean().iloc[-1]
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

        if data is not None and len(data) >= 20:  # Valid data
            valid_stock_count += 1

    scores = sorted(scores, key=lambda x: x[4], reverse=True)
    return scores[:3], valid_stock_count

# Generate AI-based commentary
import openai

def generate_ai_commentary(stock, momentum, rsi, volume, overall):
    prompt = (f"Analyze the stock {stock} based on the following indicators:\n"
              f"- Momentum: {momentum}%\n"
              f"- RSI: {rsi}\n"
              f"- Volume: {volume}\n"
              f"Provide a concise investment recommendation without extensive explanations.")

    try:
        if not OPENAI_API_KEY:
            return "AI analysis unavailable: OpenAI API key is missing."

        openai.api_key = OPENAI_API_KEY  # Ensure correct API key

        # Using the new API Completion to generate responses
        response = openai.Completion.create(
            model="gpt-4",  # You can also use "gpt-3.5-turbo" if needed
            prompt=prompt,
            max_tokens=100,  # You can adjust the number of tokens for the response
            temperature=0.5,  # Adjust the temperature for randomness of responses
            n=1  # Return 1 response
        )

        # Extracting the content of the AI response
        return response['choices'][0]['text'].strip()

    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"


# Display top 3 stocks and their AI commentary
top_stocks, valid_stock_count = compute_stock_scores(stock_data)

# Calculate percentage of valid data
valid_data_percentage = (valid_stock_count / len(ALL_STOCKS)) * 100 if len(ALL_STOCKS) > 0 else 0

# Sidebar: Display warnings and valid data percentage
with st.sidebar.expander("⚠️ Data Warnings & Stats", expanded=False):
    st.write(f"🔹 **Percentage of tickers with valid data:** {valid_data_percentage:.2f}%")
    if valid_data_percentage < 100:
        st.write("⚠️ Some tickers don't have sufficient data for analysis.")
    else:
        st.write("✅ All tickers have sufficient data for analysis.")

# Display top 3 stocks with AI commentary
st.subheader("🏆 Top 3 Stock Picks Overall")
create_stock_recommendation_table(top_stocks)

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
    fig = px.line(stock_data[stock], x=stock_data[stock].index, y=["Close", "Volume"], title=f"{stock} Price & Volume (Last 10 Weeks)")
    st.plotly_chart(fig)

# Test APIs
def test_apis():
    api_results = {}

    # Test OpenAI API (updated method)
    try:
        if not OPENAI_API_KEY:
            api_results['OpenAI'] = "Error: API Key missing"
        else:
            openai.api_key = OPENAI_API_KEY
            # Make a simple API call to check if the key works
            openai.Completion.create(
                model="text-davinci-003",  # or any other model you want to use
                prompt="Hello, world!",
                max_tokens=5
            )
            api_results['OpenAI'] = "Working"
    except Exception as e:
        api_results['OpenAI'] = f"Error: {str(e)}"

    # Test Yahoo Finance API (unchanged)
    try:
        yf.Ticker('AAPL').history(period='1d')  # A simple call to check Yahoo Finance
        api_results['Yahoo Finance'] = "Working"
    except Exception as e:
        api_results['Yahoo Finance'] = f"Error: {str(e)}"

    # Test NewsAPI (unchanged)
    try:
        news_response = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWSAPI_KEY}')
        if news_response.status_code == 200:
            api_results['NewsAPI'] = "Working"
        else:
            api_results['NewsAPI'] = f"Error: Status code {news_response.status_code}"
    except Exception as e:
        api_results['NewsAPI'] = f"Error: {str(e)}"

    return api_results

# Sidebar: API Test Button
if st.sidebar.button("🔍 Test APIs"):
    st.sidebar.write("Testing APIs...")
    results = test_apis()

    for api, status in results.items():
        st.sidebar.write(f"{api}: {status}")

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
