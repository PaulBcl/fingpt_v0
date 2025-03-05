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

import plotly.graph_objects as go

def display_top_stocks(top_stocks, stock_data, generate_ai_commentary):
    """
    Display the top stocks with AI commentary.

    Parameters:
    top_stocks (list): A list of top stock tuples.
    stock_data (dict): A dictionary containing stock data.
    generate_ai_commentary (function): A function to generate AI commentary.
    """
    st.subheader("🏆 Top 3 Stock Picks - Detailed Analysis")

    for stock, momentum, pe_score, debt_score, roe_score, overall in top_stocks:
        financials = stock_data[stock]["financials"]
        ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))

        # Display stock table
        stock_df = pd.DataFrame({
            "Metric": ["Momentum %", "P/E Ratio", "Debt/Equity", "Return on Equity", "Overall Score"],
            "Value": [momentum, financials["pe_ratio"], financials["debt_equity"], financials["return_on_equity"], overall]
        })
        st.table(stock_df)

        # Plot stock price
        data = stock_data[stock]["price_data"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Stock Price"))
        fig.add_trace(go.Bar(x=data.index, y=data["Volume"], name="Volume", marker_color="lightgray"))
        fig.update_layout(title=f"{stock} - Price & Volume", xaxis_title="Date", yaxis_title="Value")
        st.plotly_chart(fig)

        st.write(f"💬 **AI Analysis:** {ai_comment}")
