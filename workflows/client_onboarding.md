# Client Onboarding Workflow

## Objective
Spin up a new client's automation stack on GitHub, generate their client brief, and send a welcome email — all from a single JSON config file.

## Inputs Required
Fill in `client_configs/{client-slug}.json` with:
- `client_slug` — URL-safe name, e.g. `acme-widgets` (used for repo name)
- `business_name` — Full business name
- `contact_name` / `contact_email` — Primary contact
- `industry`, `location`, `employee_count`
- `tone_of_voice` — How they communicate
- `target_audience` — Who they're talking to
- `goals` — List of what they want to achieve
- `workflows_requested` — Which workflows to activate (must match names in `workflows/`)
- `api_keys` — Their credentials (ANTHROPIC, GHL, GOOGLE)
- `notes` — Anything else relevant

## Tools Used
- `tools/onboard_client.py` — Master onboarding script (runs all 5 steps)

## Steps
1. Duplicate `client_configs/example-client.json` → `client_configs/{slug}.json`
2. Fill in all fields
3. Run: `python3 tools/onboard_client.py client_configs/{slug}.json`
4. Script will:
   - Create `Growth-Lab-Co/client-{slug}-automations` private GitHub repo
   - Push base template files (CLAUDE.md, .gitignore, folder structure)
   - Set GitHub Secrets from `api_keys` in the config
   - Generate a client brief HTML doc with Claude and upload to Google Drive
   - Send a welcome email to the client (BCC: becbennett90@gmail.com)
5. Copy the relevant workflow files from this repo into the client's repo and push

## Expected Output
- New private repo: `https://github.com/Growth-Lab-Co/client-{slug}-automations`
- Google Doc: "Client Brief — {Business Name}" in your Drive
- Welcome email sent to client, BCC'd to you
- All API keys stored as GitHub Secrets (never in any file)

## After Onboarding
- Copy the relevant workflow `.md` files from `workflows/` into the client repo
- Copy the relevant tool `.py` files from `tools/` into the client repo
- Set up GitHub Actions schedules in the client repo (`.github/workflows/`)
- Run `auth_google.py` in the client's context if they have their own Google account

## Pricing Notes (Internal)
- Setup fee covers onboarding + first workflow build
- Monthly retainer = per-workflow hosting + maintenance fee
- Each workflow run costs ~$0.01–0.05 in API credits (Claude) — factor into pricing

## Known Constraints
- Client must have their own Anthropic account for heavy AI usage (or use Growth Lab Co account and charge on)
- Google OAuth token is per-Google-account — each client with their own Google needs their own token.json
- GitHub Secrets are encrypted and never visible after being set
