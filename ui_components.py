import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

@st.cache_data(ttl=300)  # Cache for 5 minutes
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
        financials = stock_data.get(stock, {}).get("financials", {})
        if not financials:
            continue

        ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))
        
        table_data.append({
            "Stock": stock,
            "Momentum": f"{momentum:.2f}%",
            "P/E Score": f"{pe_score}/10",
            "Debt Score": f"{debt_score}/10",
            "ROE Score": f"{roe_score}/10",
            "Overall": f"{overall:.2f}/10",
            "AI Analysis": ai_comment
        })

    if not table_data:
        st.warning("No valid stock data available for the table.")
        return

    df = pd.DataFrame(table_data)

    # Apply custom styling to the DataFrame
    def highlight_scores(val):
        try:
            score = float(val.split('/')[0])
            if score >= 8:
                return 'background-color: #dcfce7'  # Light green
            elif score >= 5:
                return 'background-color: #fef9c3'  # Light yellow
            else:
                return 'background-color: #fee2e2'  # Light red
        except:
            return ''

    # Apply styling to score columns
    score_columns = ['Momentum', 'P/E Score', 'Debt Score', 'ROE Score', 'Overall']
    styled_df = df.style.applymap(highlight_scores, subset=score_columns)

    # Display the styled DataFrame
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=400  # Fixed height for better scrolling
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def format_stock_metrics(momentum, pe_score, debt_score, roe_score, overall):
    """Format stock metrics for display with consistent styling."""
    return {
        "Momentum": f"{momentum:.2f}%",
        "P/E Score": f"{pe_score}/10",
        "Debt Score": f"{debt_score}/10",
        "ROE Score": f"{roe_score}/10",
        "Overall Score": f"{overall:.2f}/10"
    }

def display_top_stocks(top_stocks, stock_data, generate_ai_commentary):
    """
    Display the top selected stocks with AI commentary.
    
    Args:
        top_stocks (list): List of tuples containing stock data
        stock_data (dict): Dictionary containing detailed stock information
        generate_ai_commentary (callable): Function to generate AI analysis
    """
    if not top_stocks:
        st.warning("No top stocks available.")
        return

    # Create columns for better layout
    cols = st.columns(len(top_stocks))
    
    for idx, stock_data_entry in enumerate(top_stocks):
        if not isinstance(stock_data_entry, tuple) or len(stock_data_entry) != 6:
            st.error(f"❌ Unexpected data format: {stock_data_entry} (expected tuple with 6 elements)")
            continue

        stock, momentum, pe_score, debt_score, roe_score, overall = stock_data_entry
        financials = stock_data.get(stock, {}).get("financials", {})

        # Skip if no financial data
        if not financials:
            st.warning(f"⚠️ No financial data found for {stock}. Skipping AI commentary.")
            continue

        # Format metrics
        metrics = format_stock_metrics(momentum, pe_score, debt_score, roe_score, overall)
        
        with cols[idx]:
            # Create a card-like container for each stock
            st.markdown(f"""
            <div style="
                background-color: #f8fafc;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h3 style="color: #1e40af; margin-bottom: 15px;">{stock}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    {''.join(f'''
                    <div style="background-color: white; padding: 10px; border-radius: 5px;">
                        <small style="color: #64748b;">{metric}</small>
                        <p style="margin: 0; font-weight: bold; color: #1e40af;">{value}</p>
                    </div>
                    ''' for metric, value in metrics.items())}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Generate and display AI commentary
            ai_comment = generate_ai_commentary(stock, financials, (momentum, pe_score, debt_score, roe_score))
            st.markdown(f"""
            <div style="
                background-color: #e0e7ff;
                border-radius: 10px;
                padding: 15px;
                margin-top: 10px;
            ">
                <h4 style="color: #3730a3; margin-bottom: 10px;">AI Analysis</h4>
                <p style="font-size: 0.9em; color: #1e40af;">{ai_comment}</p>
            </div>
            """, unsafe_allow_html=True)

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
