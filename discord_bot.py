import discord
import openai
import requests
import streamlit as st
import base64

# Load secrets from Streamlit Dashboard
BOT_TOKEN = st.secrets["discord"]["bot_token"]
OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]
GITHUB_REPO = st.secrets["github"]["GITHUB_REPO"]
GITHUB_TOKEN = st.secrets["github"]["GITHUB_TOKEN"]

# GitHub API URL for modifying files
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Set up Discord bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    prompt = message.content.strip()

    # GPT-4 analyzes and determines necessary modifications
    instruction = f"""
    You are an AI assistant modifying a Streamlit Python app.
    The user asked: '{prompt}'.
    Identify all necessary files that require changes and provide their updated contents.
    The output should be a JSON containing:
    - "files": A dictionary where keys are filenames and values are their new content.
    Ensure all modifications keep the application functional and error-free.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": instruction}]
    )

    try:
        updated_files = eval(response["choices"][0]["message"]["content"])  # Convert JSON response

        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        for file_path, new_content in updated_files["files"].items():
            # Fetch the current file's SHA (GitHub requires this for updates)
            file_info = requests.get(GITHUB_API_URL + file_path, headers=headers).json()
            file_sha = file_info.get("sha")

            # Encode content to Base64
            encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

            # Prepare the update payload
            update_data = {
                "message": f"Auto-update based on Discord command: {prompt}",
                "content": encoded_content,
                "sha": file_sha
            }

            response = requests.put(GITHUB_API_URL + file_path, json=update_data, headers=headers)

            if response.status_code == 200:
                await message.channel.send(f"✅ {file_path} updated successfully!")
            else:
                await message.channel.send(f"❌ Failed to update {file_path}.")

    except Exception as e:
        await message.channel.send("❌ An error occurred while processing the request.")
        print(f"Error: {e}")

# Run the bot
client.run(BOT_TOKEN)
