import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import openai
import requests
import ta

# Expand Streamlit to full width
st.set_page_config(layout="wide")

# OpenAI API Key (Replace with your own key)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Example Stock Recommendation (unchanged)
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
refresh_interval = st.sidebar.slider("Auto-refresh interval (minutes)", 1, 30, 30)

# Use @st.cache_data instead of @st.experimental_memo
@st.cache_data(ttl=refresh_interval * 60)
def fetch_stock_data(stock_list):
    stock_data = {}
    for stock in stock_list:
        try:
            data = yf.Ticker(stock).history(period='3mo')
            if data.empty:
                stock_data[stock] = None  # If data is empty, store None for that stock
            else:
                stock_data[stock] = data
        except Exception as e:
            st.warning(f"Error fetching data for {stock}: {e}")
            stock_data[stock] = None  # Handle errors and set data as None
    return stock_data

# Fetch stock data
stock_data = fetch_stock_data(ALL_STOCKS)

# Compute percentage of valid tickers
def calculate_valid_data_percentage(stock_data):
    valid_data_count = sum(1 for data in stock_data.values() if data is not None and not data.empty)
    total_tickers = len(stock_data)
    return (valid_data_count / total_tickers) * 100 if total_tickers > 0 else 0

# Use @st.cache_data instead of @st.experimental_memo
@st.cache_data(ttl=refresh_interval * 60)
def compute_stock_scores(stock_data):
    scores = []
    for stock, data in stock_data.items():
        if data is None or len(data) < 20:
            st.warning(f"No sufficient data for {stock} or data is empty.")
            continue

        # Check that 'data' is a DataFrame and contains required columns
        if 'Close' not in data or 'Volume' not in data:
            st.warning(f"Missing necessary columns for {stock}. Skipping...")
            continue

        # Ensure 'Volume' exists and fill NaNs
        data['Volume'].fillna(0, inplace=True)

        # Calculate Momentum (percentage change in closing price)
        momentum_score = min(max((data['Close'].pct_change().iloc[-1] * 200), 0), 10)

        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(data['Close'], window=14).rsi().iloc[-1]
        rsi_score = 10 if rsi < 30 else 4 if rsi < 50 else 0

        # Calculate Volume Score
        rolling_avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1] if len(data) >= 20 else data['Volume'].mean()
        last_volume = data['Volume'].iloc[-1]

        if last_volume > rolling_avg_volume * 1.5:
            volume_score = 10
        elif last_volume > rolling_avg_volume:
            volume_score = 4
        else:
            volume_score = 0

        # Overall score
        overall_score = (momentum_score + rsi_score + volume_score) / 3
        scores.append((stock, momentum_score, rsi_score, volume_score, overall_score))

    scores = sorted(scores, key=lambda x: x[4], reverse=True)
    return scores[:3]

# Use @st.cache_data instead of @st.experimental_memo
@st.cache_data(ttl=refresh_interval * 60)
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

# API Test Function (unchanged)
def test_apis():
    api_results = {}
    # Test OpenAI API
    try:
        if not OPENAI_API_KEY:
            api_results['OpenAI'] = "Error: API Key missing"
        else:
            openai.api_key = OPENAI_API_KEY
            openai.Model.list()  # A simple API call to check connectivity
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

# Display top 5 stocks with AI commentary
st.subheader("🏆 Top 3 Stock Picks Overall")
top_stocks = compute_stock_scores(stock_data)
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
    fig = px.line(stock_data[stock], x=stock_data[stock].index, y=["Close", "Volume"], title=f"{stock} Price & Volume (Last 10 Weeks)")
    st.plotly_chart(fig)

# Show valid data percentage in the sidebar
valid_data_percentage = calculate_valid_data_percentage(stock_data)
st.sidebar.write(f"✅ **Valid Data Found**: {valid_data_percentage:.2f}% of the tickers have data available for analysis.")

# Test APIs Button (unchanged)
if st.sidebar.button("🔍 Test APIs"):
    st.sidebar.write("Testing APIs...")
    results = test_apis()

    for api, status in results.items():
        st.sidebar.write(f"{api}: {status}")

# Add refresh button (unchanged)
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
