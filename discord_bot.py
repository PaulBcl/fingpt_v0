import discord
import openai
import requests
import streamlit as st

# Load secrets from Streamlit Dashboard
BOT_TOKEN = st.secrets["discord"]["bot_token"]
OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]
GITHUB_REPO = st.secrets["github"]["GITHUB_REPO"]
GITHUB_TOKEN = st.secrets["github"]["GITHUB_TOKEN"]

# GitHub API URL for direct file modifications
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

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    generated_code = response["choices"][0]["message"]["content"]

    # File to modify (example: main.py)
    file_path = "main.py"

    # Fetch the current file's SHA (required by GitHub API)
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    file_info = requests.get(GITHUB_API_URL + file_path, headers=headers).json()
    file_sha = file_info["sha"]

    # Update the file content
    commit_message = f"Auto-update based on Discord command: {prompt}"
    update_data = {
        "message": commit_message,
        "content": generated_code.encode("utf-8").decode("latin1"),  # Encode to Base64
        "sha": file_sha
    }

    response = requests.put(GITHUB_API_URL + file_path, json=update_data, headers=headers)

    if response.status_code == 200:
        await message.channel.send("✅ Code updated and pushed to GitHub!")
    else:
        await message.channel.send("❌ Failed to update GitHub.")

# Run the bot
client.run(BOT_TOKEN)
