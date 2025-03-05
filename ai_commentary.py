import openai
import streamlit as st

# Access OpenAI API key from secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Correct way to access the key based on your secret name

# Use this key for the OpenAI API
openai.api_key = OPENAI_API_KEY

# Function to generate AI-powered stock commentary (GPT-4)
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
        response = openai.completions.create(  # Updated method for v1.0.0+
            model="gpt-4",  # Use GPT-4 for the analysis
            prompt=prompt,
            max_tokens=150,  # You can adjust the token length as necessary
            temperature=0.5,  # Adjust temperature (creativity) from 0.0 to 1.0
        )

        # Extract and return the content of the AI response
        return response['choices'][0]['text'].strip()

    except openai.OpenAIError as e:
        return f"AI analysis unavailable: {str(e)}"
