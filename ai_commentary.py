import openai

def generate_ai_commentary(stock, momentum, rsi, volume, overall):
    """
    Generate AI commentary for a stock based on its indicators.

    Parameters:
    stock (str): The stock ticker.
    momentum (float): The momentum score.
    rsi (float): The RSI score.
    volume (float): The volume score.
    overall (float): The overall score.

    Returns:
    str: The AI-generated commentary.
    """
    prompt = (f"Analyze the stock {stock} based on the following indicators:\n"
              f"- Momentum: {momentum}%\n"
              f"- RSI: {rsi}\n"
              f"- Volume: {volume}\n"
              f"Provide a concise investment recommendation without extensive explanations.")

    try:
        if not openai.api_key:
            return "AI analysis unavailable: OpenAI API key is missing."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing stock investment insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5,
        )

        return response['choices'][0]['message']['content'].strip()

    except openai.OpenAIError as e:
        return f"AI analysis unavailable: {str(e)}"
