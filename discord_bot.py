import discord
import openai
import requests
import os
import streamlit as st
import base64

# Detect if running in GitHub Actions
RUNNING_IN_GITHUB = "GITHUB_ACTIONS" in os.environ

# Load secrets from GitHub Actions or Streamlit
if not RUNNING_IN_GITHUB and hasattr(st, "secrets"):
    print("✅ Running in Streamlit, using st.secrets")
    BOT_TOKEN = st.secrets.get("DISCORD_BOT_TOKEN", None)
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
    REPO_NAME = st.secrets.get("REPO_NAME", None)
    TOKEN_REPO = st.secrets.get("TOKEN_REPO", None)
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", None)
else:
    print("✅ Running in GitHub Actions, using os.environ")
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPO_NAME = os.getenv("REPO_NAME")
    TOKEN_REPO = os.getenv("TOKEN_REPO")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Raise an error if critical API keys are missing
if not BOT_TOKEN or not OPENAI_API_KEY or not REPO_NAME or not TOKEN_REPO:
    raise ValueError("❌ ERROR: One or more API keys are missing! Ensure they are set in Streamlit Secrets or GitHub Actions.")

# GitHub API URL for modifying files
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/"

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Set up Discord bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    prompt = message.content.strip()
    print(f"📩 Received message: {prompt}")

    # Use GPT-4 to interpret the instruction
    instruction = f"""
    You are an AI assistant modifying a Streamlit Python app.
    The user asked: '{prompt}'.
    Identify all necessary files that require changes and provide their updated contents.
    The output should be a JSON containing:
    - "files": A dictionary where keys are filenames and values are their new content.
    Ensure all modifications keep the application functional and error-free.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": instruction}]
        )
        updated_files = eval(response["choices"][0]["message"]["content"])  # Convert JSON response

        headers = {"Authorization": f"token {TOKEN_REPO}"}

        for file_path, new_content in updated_files["files"].items():
            # Fetch the current file's SHA (GitHub requires this for updates)
            file_info = requests.get(GITHUB_API_URL + file_path, headers=headers).json()
            file_sha = file_info.get("sha", None)

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
print("🚀 Starting Discord bot...")
client.run(BOT_TOKEN)
