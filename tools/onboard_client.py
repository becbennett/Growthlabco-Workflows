"""
Client onboarding tool for Growth Lab Co.
Creates a GitHub repo, sets secrets, generates a client brief, and sends a welcome email.

Usage: python3 tools/onboard_client.py client_configs/your-client.json
"""

import os
import sys
import json
import base64
import subprocess
import shutil
import tempfile
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import anthropic
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

load_dotenv()

GITHUB_ORG = "Growth-Lab-Co"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "client-repo")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://mail.google.com/",
]


# ── Step 1: Create GitHub repo ──────────────────────────────────────────────

def create_github_repo(slug, business_name):
    repo_name = f"client-{slug}-automations"
    description = f"Growth Lab Co automation stack for {business_name}"

    print(f"  Creating repo: {GITHUB_ORG}/{repo_name}")
    result = subprocess.run(
        ["gh", "repo", "create", f"{GITHUB_ORG}/{repo_name}",
         "--private", "--description", description],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"GitHub repo creation failed:\n{result.stderr}")

    print(f"  ✓ Repo created: https://github.com/{GITHUB_ORG}/{repo_name}")
    return repo_name


# ── Step 2: Push template files ─────────────────────────────────────────────

def push_template_files(repo_name, client):
    tmp_dir = tempfile.mkdtemp(prefix="glc-onboard-")
    try:
        clone_url = f"https://github.com/{GITHUB_ORG}/{repo_name}.git"
        subprocess.run(["git", "clone", clone_url, tmp_dir], check=True,
                       capture_output=True)

        # Copy template files
        for item in os.listdir(TEMPLATE_DIR):
            src = os.path.join(TEMPLATE_DIR, item)
            dst = os.path.join(tmp_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        # Write a client-specific README
        readme = f"""# {client['business_name']} — Automation Stack

Managed by [Growth Lab Co](https://growthlabco.com.au)

## Active Workflows
{chr(10).join(f"- {w}" for w in client.get('workflows_requested', []))}

## Setup
1. Copy `.env.example` to `.env` and fill in API keys
2. Run `python3 tools/auth_google.py` once to set up Google OAuth
3. Workflows run automatically via GitHub Actions

Questions? Contact hello@growthlabco.com.au
"""
        with open(os.path.join(tmp_dir, "README.md"), "w") as f:
            f.write(readme)

        # Git commit and push
        subprocess.run(["git", "config", "user.email", "hello@growthlabco.com.au"],
                       cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Growth Lab Co"],
                       cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmp_dir, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Growth Lab Co setup"],
                       cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=tmp_dir, check=True,
                       capture_output=True)

        print(f"  ✓ Template files pushed")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Step 3: Set GitHub Secrets ───────────────────────────────────────────────

def set_github_secrets(repo_name, api_keys):
    full_repo = f"{GITHUB_ORG}/{repo_name}"
    for key, value in api_keys.items():
        if not value:
            print(f"  ⚠ Skipping {key} — no value provided")
            continue
        result = subprocess.run(
            ["gh", "secret", "set", key, "--body", value, "-R", full_repo],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ✓ Secret set: {key}")
        else:
            print(f"  ⚠ Failed to set {key}: {result.stderr.strip()}")


# ── Step 4: Generate client brief with Claude ────────────────────────────────

def generate_client_brief(client):
    ai_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Write a professional client brief document for Growth Lab Co's records.

Client details:
- Business: {client['business_name']}
- Contact: {client['contact_name']} ({client['contact_email']})
- Industry: {client['industry']}
- Location: {client['location']}
- Team size: {client.get('employee_count', 'Unknown')}
- Tone of voice: {client['tone_of_voice']}
- Target audience: {client['target_audience']}
- Goals: {', '.join(client['goals'])}
- Workflows active: {', '.join(client.get('workflows_requested', []))}
- Notes: {client.get('notes', 'None')}
- Onboarded: {datetime.date.today().strftime('%d %B %Y')}

Write this as a clean HTML document with:
1. Client Overview section
2. Goals & Objectives
3. Active Automations
4. Tone & Audience Guide
5. Notes & Special Instructions

Use professional but warm language. Growth Lab Co brand style."""

    message = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ── Step 5: Upload brief to Google Drive ────────────────────────────────────

def upload_brief_to_drive(html_content, client):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, GOOGLE_SCOPES)
    drive = build("drive", "v3", credentials=creds)

    file_name = f"Client Brief — {client['business_name']}"
    media = MediaInMemoryUpload(
        html_content.encode("utf-8"),
        mimetype="text/html",
        resumable=False
    )
    file_meta = {
        "name": file_name,
        "mimeType": "application/vnd.google-apps.document",
    }
    doc = drive.files().create(
        body=file_meta,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    print(f"  ✓ Client brief uploaded: {doc['webViewLink']}")
    return doc["webViewLink"]


# ── Step 6: Send welcome email ───────────────────────────────────────────────

def send_welcome_email(client, repo_name, brief_link):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, GOOGLE_SCOPES)
    gmail = build("gmail", "v1", credentials=creds)

    repo_url = f"https://github.com/{GITHUB_ORG}/{repo_name}"
    html_body = f"""
<p>Hi {client['contact_name'].split()[0]},</p>

<p>Welcome to Growth Lab Co! 🎉 Your automation stack is set up and ready to go.</p>

<h3>What's been set up</h3>
<ul>
{''.join(f"<li>{w.replace('_', ' ').title()}</li>" for w in client.get('workflows_requested', []))}
</ul>

<h3>Your active automations will</h3>
<ul>
  <li>Run automatically on schedule — no action needed from you</li>
  <li>Deliver outputs directly to your inbox or Google Drive</li>
  <li>Improve over time as we learn what works best for {client['business_name']}</li>
</ul>

<p>If you have questions or want to add new workflows, just reply to this email.</p>

<p>Talk soon,<br>
<strong>Bec Bennett</strong><br>
Growth Lab Co<br>
hello@growthlabco.com.au</p>
"""

    msg = MIMEMultipart("alternative")
    msg["To"] = client["contact_email"]
    msg["From"] = "becbennett90@gmail.com"
    msg["Subject"] = f"Welcome to Growth Lab Co — Your automations are live, {client['contact_name'].split()[0]}!"
    msg["Bcc"] = "becbennett90@gmail.com"
    msg.attach(MIMEText(html_body, "html"))

    import base64 as b64
    raw = b64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"  ✓ Welcome email sent to {client['contact_email']}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/onboard_client.py client_configs/your-client.json")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path) as f:
        client = json.load(f)

    slug = client["client_slug"]
    print(f"\n{'='*50}")
    print(f"Onboarding: {client['business_name']}")
    print(f"{'='*50}\n")

    print("[1/5] Creating GitHub repo...")
    repo_name = create_github_repo(slug, client["business_name"])

    print("\n[2/5] Pushing template files...")
    push_template_files(repo_name, client)

    print("\n[3/5] Setting GitHub Secrets...")
    set_github_secrets(repo_name, client.get("api_keys", {}))

    print("\n[4/5] Generating client brief...")
    brief_html = generate_client_brief(client)
    brief_link = upload_brief_to_drive(brief_html, client)

    print("\n[5/5] Sending welcome email...")
    send_welcome_email(client, repo_name, brief_link)

    print(f"\n{'='*50}")
    print(f"✓ {client['business_name']} is onboarded!")
    print(f"  Repo: https://github.com/{GITHUB_ORG}/{repo_name}")
    print(f"  Brief: {brief_link}")
    print(f"{'='*50}\n")
