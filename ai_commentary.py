import openai
import streamlit as st

# Access OpenAI API key from secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Correct way to access the key based on your secret name

# Use this key for the OpenAI API
openai.api_key = OPENAI_API_KEY

# Function to generate AI-powered stock commentary (GPT-4 Chat Model)
def generate_ai_commentary(stock, momentum, rsi, volume, overall):
    prompt = (f"Analyze the stock {stock} based on the following indicators:\n"
              f"- Momentum: {momentum}%\n"
              f"- RSI: {rsi}\n"
              f"- Volume: {volume}\n"
              f"Provide a concise investment recommendation without extensive explanations.")

    try:
        if not OPENAI_API_KEY:
            return "AI analysis unavailable: OpenAI API key is missing."

        # Set the OpenAI API key
        openai.api_key = OPENAI_API_KEY

        # Use the correct method for GPT-4 with the new OpenAI library
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(

            model="gpt-4",  # Use GPT-4 for the analysis
            messages=[
                {"role": "system", "content": "You are a financial analyst providing stock investment insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # Adjust token length as necessary
            temperature=0.5,  # Adjust temperature (creativity) from 0.0 to 1.0
        )

        # Extract and return the content of the AI response
        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"AI analysis unavailable: {str(e)}"
