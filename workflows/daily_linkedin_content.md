# Daily LinkedIn Content Workflow

## Objective
Every day at 8am AEST, research a trending AI in marketing or customer service topic, write a LinkedIn post in Bec Bennett's voice, generate 3 branded carousel slides, and deliver everything to Bec's inbox + Google Drive.

## Inputs Required
- Reddit API credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`) in `.env`
- Anthropic API key (`ANTHROPIC_API_KEY`) in `.env`
- Google OAuth token (`token.json`) — run `tools/auth_google.py` once to generate
- Optional: `GOOGLE_DRIVE_OUTPUT_FOLDER_ID` in `.env` to organise Drive output into a parent folder

## Tools Used
- `tools/fetch_trending_topics.py` — Scrapes Reddit (r/artificial, r/ChatGPT, r/marketing, r/customerservice) + RSS feeds for trending AI topics
- `tools/write_linkedin_post.py` — Sends topics to Claude Sonnet to select the best one and write post copy + 3-slide carousel copy
- `tools/generate_infographic.py` — Renders 3 branded PNG slides (1080x1080) using Pillow + Space Grotesk font + Growth Lab Co brand colours
- `tools/deliver_content.py` — Creates a dated Google Drive folder, uploads slides, sends HTML email to becbennett90@gmail.com
- `tools/run_daily_linkedin.py` — Master orchestrator that runs all 4 steps in sequence

## Steps
1. Run `tools/fetch_trending_topics.py` → outputs JSON list of trending topics → saved to `.tmp/topics.json`
2. Run `tools/write_linkedin_post.py .tmp/topics.json` → Claude selects best topic, writes post + slide copy → saved to `.tmp/linkedin_content.json`
3. Run `tools/generate_infographic.py` → generates `.tmp/slide_1.png`, `slide_2.png`, `slide_3.png`
4. Run `tools/deliver_content.py` → uploads to Drive, sends email with slides attached

Or run everything at once: `python3 tools/run_daily_linkedin.py`

## Scheduled Execution
GitHub Actions runs this daily at 8am AEST (22:00 UTC previous day).
See `.github/workflows/daily_linkedin.yml` for the full config.

GitHub Secrets required (Settings → Secrets → Actions):
- `ANTHROPIC_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_TOKEN_JSON` (paste the full contents of your local `token.json`)
- `GOOGLE_DRIVE_OUTPUT_FOLDER_ID` (optional)

## Expected Output
- Email to becbennett90@gmail.com with subject "🎯 Your LinkedIn Content is Ready — YYYY-MM-DD"
- Email contains: full post copy, slide-by-slide copy breakdown, Drive link, slide images attached
- Google Drive: dated folder with 3 PNG slides

## Brand Spec (for infographic generation)
- Background: `#181840` (Midnight Base)
- Primary accent: `#A070F8` (Electric Violet)
- Secondary accent: `#9878F0` (Soft Violet)
- Text: `#F8F8F8` (Clean White)
- Font: Space Grotesk (auto-downloaded to `.tmp/fonts/` on first run)
- Slide size: 1080 x 1080px (LinkedIn square carousel)

## Tone & Positioning
- Voice: Bec Bennett — fun, engaging, direct, confident. Not corporate.
- Audience: Australian SMB business owners, marketing managers, customer service leads
- Goal: Position Bec as the authority on AI for marketing and CS teams in Australian SMBs

## Edge Cases & Known Constraints
- Reddit API: Free tier, no rate limit issues for this use case (~50 posts fetched daily)
- RSS feeds: feedparser handles malformed feeds gracefully — won't crash if a feed is down
- Font download: Space Grotesk is fetched from GitHub on first run, cached in `.tmp/fonts/`
- token.json: Google OAuth tokens auto-refresh. If refresh fails (token revoked), re-run `tools/auth_google.py`
- Python 3.9 warning: Google libraries warn about Python 3.9 EOL but still work. Upgrade to 3.11+ recommended.
