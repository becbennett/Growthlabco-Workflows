"""
Lists files in a Google Drive folder by folder ID.
Usage: python3 tools/list_drive_folder.py <folder_id>
"""

import sys
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://mail.google.com/",
]

folder_id = sys.argv[1] if len(sys.argv) > 1 else None
if not folder_id:
    print("Usage: python3 tools/list_drive_folder.py <folder_id>")
    sys.exit(1)

token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
creds = Credentials.from_authorized_user_file(token_path, SCOPES)
service = build("drive", "v3", credentials=creds)

results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name, mimeType)"
).execute()

files = results.get("files", [])
if not files:
    print("No files found.")
else:
    for f in files:
        print(f"{f['name']}  |  {f['mimeType']}  |  {f['id']}")
