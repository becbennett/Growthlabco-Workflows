"""
One-time Google OAuth setup. Run this to generate token.json.
Grants access to Gmail and Google Drive.
"""

import os
import json
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://mail.google.com/",
]

client_config = {
    "installed": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=8080)

token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
with open(token_path, "w") as f:
    f.write(creds.to_json())

print(f"✓ token.json saved. Google Drive and Gmail access granted.")
