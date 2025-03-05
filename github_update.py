import requests
import base64
import json

# GitHub credentials (stored in Streamlit Secrets)
GITHUB_TOKEN = "your_github_token_here"
GITHUB_REPO = "PaulBcl/fingpt_v0"

def get_file_content(file_path):
    """Retrieve the latest content of a file from GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        return base64.b64decode(content).decode("utf-8"), response.json()["sha"]
    return None, None

def update_file(file_path, new_content, commit_message="Auto-update code"):
    """Push updated file content to GitHub."""
    content, sha = get_file_content(file_path)
    if content is None:
        return "File not found or access error."

    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    return response.json()
