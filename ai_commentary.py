import openai
import streamlit as st

# Access OpenAI API key from secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]  # Correct way to access the key based on your secret name

# Use this key for the OpenAI API
openai.api_key = OPENAI_API_KEY

# Function to generate AI-powered stock commentary (GPT-4 Chat Model)
import hashlib

def generate_ai_commentary(stock, momentum, rsi, volume, overall):
    prompt = (f"Analyze {stock}:\n"
              f"- Momentum: {momentum}%\n"
              f"- RSI: {rsi}\n"
              f"- Volume: {volume}\n"
              f"Give a short investment recommendation.")

    # Create a hash key for this specific request
    request_key = hashlib.md5(prompt.encode()).hexdigest()

    # Check if response is already cached
    if request_key in st.session_state:
        return st.session_state[request_key]

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model
            messages=[
                {"role": "system", "content": "Give concise stock insights in bullet points."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,  # Reduce max tokens
            temperature=0.5,
        )

        ai_comment = response.choices[0].message.content.strip()

        # Store result in session cache
        st.session_state[request_key] = ai_comment

        return ai_comment

    except openai.OpenAIError as e:
        return f"AI analysis unavailable: {str(e)}"
