"""
Downloads a file from Google Drive by file ID.
Usage: python3 tools/download_drive_file.py <file_id> <output_path>
"""

import sys
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://mail.google.com/",
]

file_id = sys.argv[1]
output_path = sys.argv[2]

token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
creds = Credentials.from_authorized_user_file(token_path, SCOPES)
service = build("drive", "v3", credentials=creds)

request = service.files().get_media(fileId=file_id)
with open(output_path, "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

print(f"✓ Downloaded to {output_path}")
