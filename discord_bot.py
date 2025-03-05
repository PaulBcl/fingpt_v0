import discord
import openai
import requests
import os
import streamlit as st
import base64
import traceback

# Detect if running in GitHub Actions
RUNNING_IN_GITHUB = "GITHUB_ACTIONS" in os.environ

# Load secrets from GitHub Actions or Streamlit
if not RUNNING_IN_GITHUB and hasattr(st, "secrets"):
    print("✅ Running in Streamlit, using st.secrets")
    DISCORD_BOT_TOKEN = st.secrets.get("DISCORD_BOT_TOKEN", None)
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
    REPO_NAME = st.secrets.get("REPO_NAME", None)
    TOKEN_REPO = st.secrets.get("TOKEN_REPO", None)
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", None)
else:
    print("✅ Running in GitHub Actions, using os.environ")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPO_NAME = os.getenv("REPO_NAME")
    TOKEN_REPO = os.getenv("TOKEN_REPO")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Debugging: Print secrets before raising an error
print(f"🔍 Debugging Secrets in Python:")
print(f"DISCORD_BOT_TOKEN: {'✅ Loaded' if DISCORD_BOT_TOKEN else '❌ MISSING'}")
print(f"OPENAI_API_KEY: {'✅ Loaded' if OPENAI_API_KEY else '❌ MISSING'}")
print(f"REPO_NAME: {'✅ Loaded' if REPO_NAME else '❌ MISSING'}")
print(f"TOKEN_REPO: {'✅ Loaded' if TOKEN_REPO else '❌ MISSING'}")
print(f"NEWS_API_KEY: {'✅ Loaded' if NEWS_API_KEY else '❌ MISSING'}")

# Raise an error if critical API keys are missing
if not DISCORD_BOT_TOKEN or not OPENAI_API_KEY or not REPO_NAME or not TOKEN_REPO:
    raise ValueError("❌ ERROR: One or more API keys are missing! Ensure they are set in Streamlit Secrets or GitHub Actions.")

print("✅ All secrets loaded successfully. Starting bot...")

# Initialize OpenAI API
client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Use explicit privileged intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # ✅ Required for reading messages

# Define Discord client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"📩 Received message: {message.content}")  # ✅ Debugging: Print all messages

    if message.author == client.user:
        return

    prompt = message.content.strip()

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content

        await message.channel.send(reply)
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error occurred:\n{error_trace}")
        await message.channel.send(f"❌ Error processing request:\n```{e}```")

# Run the bot
print("🚀 Starting Discord bot...")
client.run(DISCORD_BOT_TOKEN)
