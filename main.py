import streamlit as st
import os
import requests
import openai  # Add this import
from data_fetching import fetch_stock_data
from stock_scoring import compute_stock_scores
from ai_commentary import generate_ai_commentary
from ui_components import create_stock_recommendation_table, display_top_stocks
import yfinance as yf

# Expand Streamlit to full width
st.set_page_config(layout="wide")

# Load secrets from GitHub Actions or Streamlit environment variables
if hasattr(st, "secrets") and "GITHUB_ACTIONS" not in os.environ:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", None)
else:
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure the API key is available
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OPENAI_API_KEY is missing! Set it in Streamlit Secrets or GitHub Actions.")

openai.api_key = OPENAI_API_KEY
NEWSAPI_LIMIT = 1000  # Adjust based on your NewsAPI plan

# Define stock pools with more tickers
FRANCE_STOCKS = ['ML.PA', 'ALSTOM.PA', 'DG.PA', 'PUB.PA', 'RNO.PA', 'ACA.PA', 'BN.PA', 'AI.PA', 'STM.PA', 'CAP.PA']
ASIA_STOCKS = ['9984.T', '700.HK', '005930.KQ', 'RELIANCE.NS', 'BABA', 'TCEHY', 'JD', 'NTES', 'SE', 'SONY']
US_STOCKS = ['NVDA', 'TSLA', 'PLTR', 'SOFI', 'COIN', 'AMD', 'RBLX', 'UPST', 'CRWD', 'FSLY', 'NET']
ALL_STOCKS = FRANCE_STOCKS + ASIA_STOCKS + US_STOCKS

# Enable auto-refresh
refresh_interval = st.sidebar.slider("Auto-refresh interval (minutes)", 1, 30, 30)

@st.cache_data(ttl=refresh_interval * 60)
def fetch_stock_data_cached(stock_list):
    return fetch_stock_data(stock_list)

# Fetch stock data
stock_data = fetch_stock_data_cached(ALL_STOCKS)

# Compute stock scores
computed_scores, valid_stock_count = compute_stock_scores(stock_data)
top_stocks = computed_scores

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
if top_stocks:
    display_top_stocks(top_stocks, stock_data, generate_ai_commentary)
else:
    st.write("🚨 No valid stocks available for ranking. Check data sources.")

# Test APIs
def test_apis():
    api_results = {}

    # Test OpenAI API
    try:
        if not OPENAI_API_KEY:
            api_results['OpenAI'] = "Error: API Key missing"
        else:
            openai.api_key = OPENAI_API_KEY
            openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Test API functionality."},
                    {"role": "user", "content": "Test OpenAI API"}
                ],
                max_tokens=5
            )
            api_results['OpenAI'] = "Working"
    except Exception as e:
        api_results['OpenAI'] = f"Error: {str(e)}"

    # Test Yahoo Finance API
    try:
        yf.Ticker('AAPL').history(period='1d')
        api_results['Yahoo Finance'] = "Working"
    except Exception as e:
        api_results['Yahoo Finance'] = f"Error: {str(e)}"

    # Test NewsAPI
    try:
        news_response = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}')
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

if st.sidebar.button("🚀 Apply Code Update from Chat"):
    st.switch_page("github_updater.py")

st.write("### AI Stock Picker - Live Updates Enabled")
st.write("Stock picks based on momentum, volume, sentiment, and trend alerts.")
st.write(f"⏳ Data refreshes every {refresh_interval} minutes automatically. You can also refresh manually using the button.")
