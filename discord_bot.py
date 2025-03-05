import discord
import openai
import requests
import os
import streamlit as st
import base64
import traceback
import json
import ast  # Safer than eval()
import difflib

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

# Raise an error if critical API keys are missing
if not DISCORD_BOT_TOKEN or not OPENAI_API_KEY or not REPO_NAME or not TOKEN_REPO:
    raise ValueError("❌ ERROR: One or more API keys are missing! Ensure they are set in Streamlit Secrets or GitHub Actions.")

print("✅ All secrets loaded successfully. Starting bot...")

# Initialize OpenAI API
client_openai = openai.OpenAI(api_key=OPENAI_API_KEY)

# GitHub API URL for modifying files
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents/"

# ✅ Use explicit privileged intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # ✅ Required for reading messages

# Define Discord client
client = discord.Client(intents=intents)

def smart_merge_content(original_content, new_content):
    """
    Intelligently merge new content with existing content.
    Tries to add or modify specific parts without completely replacing the file.
    """
    # If the file is completely empty or very short, just return new content
    if not original_content or len(original_content.split('\n')) < 5:
        return new_content

    # Use difflib to find the best merge strategy
    differ = difflib.Differ()
    diff = list(differ.compare(original_content.splitlines(), new_content.splitlines()))

    # Try to identify meaningful changes
    added_lines = [line[2:] for line in diff if line.startswith('+ ')]
    removed_lines = [line[2:] for line in diff if line.startswith('- ')]

    # If changes are minimal, append or insert strategically
    if len(added_lines) < 5:
        # Append new lines at the end or insert before a specific section
        if 'if __name__ == "__main__":' in original_content:
            split_content = original_content.split('if __name__ == "__main__":')
            return split_content[0] + '\n'.join(added_lines) + '\n\nif __name__ == "__main__":' + split_content[1]
        else:
            return original_content + '\n\n# New additions from Discord\n' + '\n'.join(added_lines)

    return new_content

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"📩 Received message: {message.content}")  # ✅ Debugging

    if message.author == client.user:
        return

    prompt = message.content.strip()

    instruction = f"""
    You are an AI assistant responsible for modifying a Python-based Streamlit application.
    The user asked: '{prompt}'.

    - Identify all necessary files that require changes.
    - Return the full modified content of each file that needs updating.
    - The response must be in **JSON format** with:
      - "files": A dictionary where keys are filenames and values are their new content.

    Example of expected output:
    {{
      "files": {{
        "main.py": "import streamlit as st\nst.title('Hello from Discord')",
        "ui_components.py": "..."
      }}
    }}

    Do **not** return explanations, only the raw JSON.
    """

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": instruction}]
        )

        response_content = response.choices[0].message.content.strip()

        try:
            # Ensure OpenAI response is correctly formatted
            if not response_content.startswith("{") or not response_content.endswith("}"):
                raise ValueError("❌ ERROR: OpenAI response is not properly formatted as JSON.")

            updated_files = ast.literal_eval(response_content)  # Safe alternative to eval()

            if "files" not in updated_files:
                raise ValueError("❌ ERROR: The response does not contain 'files' key.")

        except Exception as e:
            await message.channel.send(f"❌ Error processing request: {e}")
            print(f"Unexpected Error: {e}")
            return

        headers = {"Authorization": f"token {TOKEN_REPO}"}

        for file_path, new_content in updated_files["files"].items():
            # Fetch the current file's content and SHA
            try:
                file_info = requests.get(GITHUB_API_URL + file_path, headers=headers).json()
                current_content = base64.b64decode(file_info.get('content', '')).decode('utf-8')
                file_sha = file_info.get("sha", None)
            except Exception as e:
                current_content = ""
                file_sha = None

            # Smart merge of content
            merged_content = smart_merge_content(current_content, new_content)

            # Encode content to Base64
            encoded_content = base64.b64encode(merged_content.encode("utf-8")).decode("utf-8")

            # Prepare the update payload
            update_data = {
                "message": f"Auto-update based on Discord command: {prompt}",
                "content": encoded_content,
                "sha": file_sha
            }

            response = requests.put(GITHUB_API_URL + file_path, json=update_data, headers=headers)

            if response.status_code in [200, 201]:
                await message.channel.send(f"✅ {file_path} updated successfully in GitHub!")
                # Optional: Show diff or changes
                diff = '\n'.join(difflib.unified_diff(
                    current_content.splitlines(),
                    merged_content.splitlines(),
                    fromfile='original',
                    tofile='updated'
                ))
                if diff:
                    await message.channel.send(f"Changes:\n```diff\n{diff[:1900]}{'...' if len(diff) > 1900 else ''}```")
            else:
                await message.channel.send(f"❌ Failed to update {file_path}. Check logs.")
                print(f"GitHub API Response: {response.text}")

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error occurred:\n{error_trace}")
        await message.channel.send(f"❌ Error processing request:\n```{e}```")

# Run the bot
print("🚀 Starting Discord bot...")
client.run(DISCORD_BOT_TOKEN)
