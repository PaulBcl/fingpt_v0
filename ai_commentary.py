import openai
import streamlit as st
import hashlib
import os

# Access OpenAI API key from secrets

# Check if running in Streamlit (st.secrets exists)
if hasattr(st, "secrets"):
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Raise an error if the API key is missing
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OPENAI_API_KEY is missing! Set it in Streamlit Secrets or GitHub Actions.")

openai.api_key = OPENAI_API_KEY

# Function to generate AI-powered stock commentary (GPT-4 Chat Model)
def generate_ai_commentary(stock, financials, scores):
    prompt = (f"Stock: {stock}\n"
              f"- Sector: {financials['sector']}, Industry: {financials['industry']}\n"
              f"- Market Cap: {financials['market_cap']}\n"
              f"- P/E Ratio: {financials['pe_ratio']}\n"
              f"- Debt/Equity: {financials['debt_equity']}\n"
              f"- Return on Equity: {financials['return_on_equity']}\n"
              f"- Profit Margin: {financials['profit_margin']}\n"
              f"Scoring:\n"
              f"- Momentum: {scores[0]}/10\n"
              f"- P/E Ratio Score: {scores[1]}/10\n"
              f"- Debt Score: {scores[2]}/10\n"
              f"- ROE Score: {scores[3]}/10\n"
              f"Provide a **detailed investment analysis**.")

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing detailed stock recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"AI analysis unavailable: {str(e)}"
