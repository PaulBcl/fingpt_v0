import requests
import base64
import streamlit as st

# Load GitHub credentials from Streamlit secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]

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

    # Encode content in base64
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

# Streamlit UI for requesting code changes
st.title("🛠 Automated Code Updates from Chat")

file_path = st.text_input("Enter file path (e.g., ui_components.py)")
update_content = st.text_area("Describe what you want changed:")

if st.button("Apply Change and Push to GitHub"):
    if file_path and update_content:
        old_content, _ = get_file_content(file_path)
        if old_content:
            new_content = old_content.replace("# TODO: Implement", update_content)  # Modify based on chat request
            response = update_file(file_path, new_content)
            if "commit" in response:
                st.success(f"✅ Successfully updated {file_path} in GitHub!")
            else:
                st.error(f"❌ Failed to update {file_path}: {response}")
        else:
            st.error("⚠️ File not found in GitHub!")
    else:
        st.warning("⚠️ Please enter both the file path and the change description.")
