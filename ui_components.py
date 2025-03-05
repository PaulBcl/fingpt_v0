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


def display_top_stocks(top_stocks, stock_data, generate_ai_commentary):
    """
    Display only the top 3 stocks with AI commentary.

    Parameters:
    top_stocks (list): A list of top stock tuples.
    stock_data (dict): A dictionary containing stock data.
    generate_ai_commentary (function): A function to generate AI commentary.
    """

    ### ✅ **Step 1: Show a High-Level Overview of ONLY the Top 3**
    st.subheader("🏆 Top 3 Stock Picks Overview")

    for i, (stock, momentum, pe_score, debt_score, roe_score, overall) in enumerate(top_stocks[:3]):  # ✅ Ensuring only Top 3
        financials = stock_data[stock]["financials"]
        sector = financials.get("sector", "Unknown Sector")
        industry = financials.get("industry", "Unknown Industry")
        market_cap = f"${financials['market_cap']:,}" if financials.get("market_cap") else "N/A"

        # Sentiment (Mock Example – Can be improved with real sentiment analysis)
        def calculate_sentiment(momentum, rsi, news_sentiment):
            """
            Determine market sentiment based on multiple factors.

            Parameters:
            - momentum (float): Stock's momentum score.
            - rsi (float or None): Relative Strength Index (if None, assume neutral 50).
            - news_sentiment (float or None): Sentiment score from financial news (if None, assume 0).

            Returns:
            - str: Emoji + Sentiment description.
            """
            if news_sentiment is None:
                news_sentiment = 0  # Default to neutral if no data available

            if rsi is None:
                rsi = 50  # Default to neutral RSI if missing

            # Weight factors (adjust as needed)
            momentum_weight = 0.4
            rsi_weight = 0.3
            news_weight = 0.3

            # Normalize sentiment score between -1 and 1
            total_sentiment_score = (momentum * momentum_weight) + ((50 - rsi) * rsi_weight / 50) + (news_sentiment * news_weight)

            if total_sentiment_score > 0.2:
                return "📈 Positive"
            elif total_sentiment_score < -0.2:
                return "📉 Negative"
            else:
                return "⚖️ Neutral"

        news_sentiment = stock_data[stock].get("news_sentiment", 0)
        sentiment = calculate_sentiment(momentum, financials["rsi"], news_sentiment)


        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"### {stock}")
            st.write(f"**Sector:** {sector}")
            st.write(f"**Industry:** {industry}")

        with col2:
            st.write(f"**Market Sentiment:** {sentiment}")
            st.write(f"**Market Cap:** {market_cap}")

        with col3:
            st.write(f"**Momentum:** {'📈' if momentum > 0 else '📉'} {round(momentum, 2)}%")

    ### ✅ **Step 2: Show Detailed Analysis for ONLY the Top 3**
    st.subheader("🏆 Top 3 Stock Picks - Detailed Analysis")

    for i, (stock, momentum, pe_score, debt_score, roe_score, overall) in enumerate(top_stocks[:3]):  # ✅ Again, Only Top 3
        financials = stock_data[stock]["financials"]
        ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))

        # Financial Overview Expander
        with st.expander(f"📊 {stock} - Financial Overview", expanded=False):
            stock_df = pd.DataFrame({
                "Metric": ["Market Cap", "P/E Ratio", "Debt/Equity", "Return on Equity", "Profit Margin"],
                "Value": [
                    f"${financials['market_cap']:,}" if financials.get("market_cap") else "N/A",
                    round(financials["pe_ratio"], 2) if financials.get("pe_ratio") else "N/A",
                    round(financials["debt_equity"], 2) if financials.get("debt_equity") else "N/A",
                    round(financials["return_on_equity"], 2) if financials.get("return_on_equity") else "N/A",
                    f"{round(financials['profit_margin'] * 100, 2)}%" if financials.get("profit_margin") else "N/A"
                ]
            })
            st.table(stock_df)

        # Plot stock price with volume (dual-axis)
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
