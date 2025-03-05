import streamlit as st
import pandas as pd
import plotly.express as px

def create_stock_recommendation_table(data):
    """
    Create and display a stock recommendation table.

    Parameters:
    data (list): A list of stock recommendation tuples.
    """
    df = pd.DataFrame(data, columns=["Stock", "Momentum Score", "RSI Score", "Volume Score", "Overall Score"])
    df = df.round(2)
    st.dataframe(df)

def display_top_stocks(top_stocks, stock_data, generate_ai_commentary):
    """
    Display the top stocks with AI commentary.

    Parameters:
    top_stocks (list): A list of top stock tuples.
    stock_data (dict): A dictionary containing stock data.
    generate_ai_commentary (function): A function to generate AI commentary.
    """
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
