import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

def create_stock_recommendation_table(top_stocks, stock_data, generate_ai_commentary):
    """
    Create a compact and visual stock recommendation table.

    Parameters:
    top_stocks (list): A list of top stock tuples.
    stock_data (dict): A dictionary containing stock data.
    generate_ai_commentary (function): A function to generate AI commentary.
    """
    st.subheader("📈 Stock Recommendations")

    if not top_stocks:
        st.warning("No stocks available for recommendation.")
        return

    # Creating DataFrame for better visualization
    table_data = []
    for stock, momentum, pe_score, debt_score, roe_score, overall in top_stocks:
        table_data.append({
            "Stock": stock,
            "Momentum Score": f"{momentum:.2f}%" if momentum else "N/A",
            "P/E Score": round(pe_score, 2),
            "Debt Score": round(debt_score, 2),
            "ROE Score": f"{roe_score:.2f}%" if roe_score else "N/A",
            "Overall Score": round(overall, 2),
            "AI Commentary": generate_ai_commentary(stock, stock_data[stock]["financials"],
                                                    (momentum, pe_score, debt_score, roe_score))
        })

    df = pd.DataFrame(table_data)

    # Use Streamlit's table display for better formatting
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_top_stocks(top_stocks, stock_data, generate_ai_commentary):
    """
    Display the top selected stocks with AI commentary.
    """
    if not top_stocks:
        st.warning("No top stocks available.")
        return

    # Debugging: Check if `top_stocks` structure is as expected
    st.write("🔍 Debugging: top_stocks structure:", top_stocks)

    for stock_data_entry in top_stocks:
        if len(stock_data_entry) != 6:
            st.error(f"❌ Unexpected data format: {stock_data_entry} (expected 6 elements)")
            continue  # Skip incorrect entries

        stock, momentum, pe_score, debt_score, roe_score, overall = stock_data_entry
        financials = stock_data.get(stock, {}).get("financials", {})

        # Ensure financials are valid before using them in AI commentary
        if not financials:
            st.warning(f"⚠️ No financial data found for {stock}. Skipping AI commentary.")
            continue

        ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))

        st.write(f"**{stock}**")
        st.write(f"📊 Momentum: {momentum}, P/E: {pe_score}, Debt: {debt_score}, ROE: {roe_score}, Overall: {overall}")
        st.write(f"🧠 AI Commentary: {ai_comment}")


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
