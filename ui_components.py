import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_stock_recommendation_table(data):
    """
    Create and display a stock recommendation table.

    Parameters:
    data (list): A list of stock recommendation tuples.
    """
    df = pd.DataFrame(data, columns=["Stock", "Momentum Score", "RSI Score", "Volume Score", "Overall Score"])
    df = df.round(2)
    st.dataframe(df)

import streamlit as st
import pandas as pd
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

        # ✅ Move Market Sentiment, Momentum, and Market Cap into the Expander
        with st.expander(f"📊 {stock} - Financial Overview", expanded=False):
            stock_df = pd.DataFrame({
                "Metric": ["Market Cap", "Momentum %", "P/E Ratio", "Debt/Equity", "Return on Equity", "Market Sentiment"],
                "Value": [
                    f"${financials['market_cap']:,}" if financials.get("market_cap") else "N/A",
                    f"{momentum:.2f}%" if momentum else "N/A",
                    round(financials["pe_ratio"], 2) if financials.get("pe_ratio") else "N/A",
                    round(financials["debt_equity"], 2) if financials.get("debt_equity") else "N/A",
                    round(financials["return_on_equity"], 2) if financials.get("return_on_equity") else "N/A",
                    financials.get("market_sentiment", "N/A")  # ✅ Ensure this key exists in financials
                ]
            })
            st.table(stock_df)

        # ✅ Plot stock price with volume (dual-axis)
        data = stock_data[stock]["price_data"]
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index, y=data["Close"], mode="lines",
            name="Stock Price", yaxis="y1"
        ))

        fig.add_trace(go.Bar(
            x=data.index, y=data["Volume"],
            name="Volume", marker_color="lightgray", yaxis="y2"
        ))

        fig.update_layout(
            title=f"{stock} - Price & Volume",
            xaxis_title="Date",
            yaxis=dict(title="Stock Price", side="left"),
            yaxis2=dict(title="Volume", side="right", overlaying="y", showgrid=False)
        )

        st.plotly_chart(fig)

        st.write(f"💬 **AI Analysis:** {ai_comment}")
