import openai
import streamlit as st
import os

# Access OpenAI API key from secrets
if hasattr(st, "secrets") and "GITHUB_ACTIONS" not in os.environ:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure the API key is available
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OPENAI_API_KEY is missing! Set it in Streamlit Secrets or GitHub Actions.")

openai.api_key = OPENAI_API_KEY

def generate_ai_commentary(stock, financials, scores):
    """
    Generate a concise, actionable AI-powered stock commentary.

    Args:
        stock (str): Stock symbol
        financials (dict): Financial metrics for the stock
        scores (tuple): Performance scores

    Returns:
        str: AI-generated stock analysis
    """
    # Prepare a more structured, nuanced prompt
    prompt = (f"Provide a crisp, professional stock analysis for {stock}:\n"
              f"Financial Context:\n"
              f"• Sector: {financials['sector']}\n"
              f"• Market Cap: ${financials['market_cap']:,}\n"
              f"• P/E Ratio: {financials['pe_ratio']:.2f}\n"
              f"• Debt/Equity: {financials['debt_equity']:.2f}\n"
              f"• ROE: {financials['return_on_equity']:.2f}%\n"
              f"• Profit Margin: {financials['profit_margin']:.2f}%\n\n"
              f"Performance Scores (0-10):\n"
              f"• Momentum: {scores[0]}/10\n"
              f"• P/E Valuation: {scores[1]}/10\n"
              f"• Debt Health: {scores[2]}/10\n"
              f"• Return Efficiency: {scores[3]}/10\n\n"
              "Analyze investment potential. Provide:\n"
              "1. Quick investment thesis\n"
              "2. Key risk factors\n"
              "3. Short-term outlook")

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise, data-driven financial analyst. "
                               "Provide clear, actionable stock insights. "
                               "Use professional language. Avoid jargon."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,  # Slightly increased for more detail
            temperature=0.2,  # More conservative, factual tone
        )
        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"🤖 AI Analysis Unavailable: {str(e)}"

# Optional: Add caching to reduce API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_ai_commentary(stock, financials, scores):
    return generate_ai_commentary(stock, financials, scores)
