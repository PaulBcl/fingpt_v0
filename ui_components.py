import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

def create_comprehensive_stock_view(top_stocks, stock_data, generate_ai_commentary):
    """
    Create a comprehensive, compact view of top stock picks with multiple visualizations.

    Parameters:
    top_stocks (list): A list of top stock tuples.
    stock_data (dict): A dictionary containing stock data.
    generate_ai_commentary (function): A function to generate AI commentary.
    """
    # Slice to top 3 stocks
    top_3_stocks = top_stocks[:3]

    st.subheader("🏆 Top 3 Stock Picks - Comprehensive Analysis")

    # Create columns for side-by-side stock selection
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]

    for idx, (stock, momentum, pe_score, debt_score, roe_score, overall) in enumerate(top_3_stocks):
        with columns[idx]:
            # Financial Highlight Card
            financials = stock_data[stock]["financials"]
            ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))

            # Stylized stock card with key metrics
            st.markdown(f"""
            <div style="background-color:#f0f2f6; border-radius:10px; padding:15px; margin-bottom:10px;">
            <h3 style="color:#1e3a8a; margin-bottom:10px;">{stock} Overview</h3>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div>
                    <small>Market Cap</small>
                    <p style="font-weight:bold; color:#2563eb;">
                        ${financials.get('market_cap', 'N/A'):,}
                    </p>
                </div>
                <div>
                    <small>Momentum</small>
                    <p style="font-weight:bold; color:#16a34a;">
                        {f"{momentum:.2f}%" if momentum else "N/A"}
                    </p>
                </div>
                <div>
                    <small>P/E Ratio</small>
                    <p style="font-weight:bold; color:#dc2626;">
                        {round(financials.get('pe_ratio', 0), 2)}
                    </p>
                </div>
                <div>
                    <small>ROE</small>
                    <p style="font-weight:bold; color:#ca8a04;">
                        {f"{financials.get('return_on_equity', 'N/A'):.2f}%" if financials.get('return_on_equity') else "N/A"}
                    </p>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

    # Create a multi-plot figure for all three stocks
    fig = sp.make_subplots(
        rows=2, cols=3,
        subplot_titles=[f"{stock} Price" for stock in [s[0] for s in top_3_stocks]] +
                       [f"{stock} Volume" for stock in [s[0] for s in top_3_stocks]],
        vertical_spacing=0.1,
        horizontal_spacing=0.05
    )

    # Add price and volume plots for each stock
    for idx, stock in enumerate([s[0] for s in top_3_stocks], 1):
        data = stock_data[stock]["price_data"]

        # Price plot (first row)
        fig.add_trace(
            go.Scatter(x=data.index, y=data["Close"], mode="lines", name=f"{stock} Price"),
            row=1, col=idx
        )

        # Volume plot (second row)
        fig.add_trace(
            go.Bar(x=data.index, y=data["Volume"], name=f"{stock} Volume", marker_color="lightgray"),
            row=2, col=idx
        )

    # Update layout for compact, informative view
    fig.update_layout(
        height=600,
        width=1200,
        title_text="Stock Prices and Trading Volumes",
        showlegend=False
    )

    # Render the multi-plot figure
    st.plotly_chart(fig, use_container_width=True)

    # AI Analysis Section
    st.subheader("🤖 AI Investment Insights")
    analysis_cols = st.columns(3)

    for idx, (stock, momentum, pe_score, debt_score, roe_score, overall) in enumerate(top_3_stocks):
        financials = stock_data[stock]["financials"]
        ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))

        with analysis_cols[idx]:
            st.markdown(f"""
            <div style="background-color:#e0e7ff; border-radius:10px; padding:15px; margin-bottom:10px;">
            <h4 style="color:#3730a3;">{stock} Analysis</h4>
            <p style="font-size:0.9em;">{ai_comment}</p>
            </div>
            """, unsafe_allow_html=True)

    return top_3_stocks
