"""
Uses Claude to write a LinkedIn post + 3-slide infographic copy from a list of trending topics.
Inputs: JSON file of topics (from fetch_trending_topics.py)
Outputs: JSON with post copy and slide content written to .tmp/linkedin_content.json
Usage: python3 tools/write_linkedin_post.py .tmp/topics.json
"""

import os
import sys
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a LinkedIn content strategist for Bec Bennett, founder of Growth Lab Co.

About Bec:
- Positions herself as the go-to authority on AI for marketing and customer service teams in Australian SMB businesses
- Tone: fun, engaging, direct, confident — not corporate, but still professional
- Audience: Australian SMB business owners, marketing managers, and customer service leads
- Goal: Every post should make her audience think "I need to pay attention to this" and "Bec gets it"

Your job: Take a trending AI topic and turn it into a high-performing LinkedIn post + carousel content.

LinkedIn post rules:
- Open with a punchy hook (1-2 lines max) — no "I" as the first word
- Use short paragraphs (1-3 lines)
- Include a real, practical insight for SMB marketers or CS teams
- End with a question or strong CTA to drive comments
- Relevant emojis sparingly (2-4 max)
- No hashtags in the post body (add 3-5 at the very end on their own line)
- Max 1,300 characters for the post body

Carousel slide rules (3 slides):
- Slide 1 (Hook): Bold headline (max 8 words) + 1 subheading line
- Slide 2 (Insight): Headline + 3 bullet points (each max 12 words)
- Slide 3 (CTA): Bold closing statement + "Follow Bec Bennett for more AI insights"
"""

def write_content(topics: list) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    topics_text = "\n".join([
        f"- [{t['source']}] {t['title']} (score: {t['score']})"
        for t in topics[:10]
    ])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Here are today's trending AI topics. Pick the ONE most relevant and interesting for Australian SMB marketing/customer service teams and write:

1. A full LinkedIn post
2. Copy for a 3-slide LinkedIn carousel infographic

Topics:
{topics_text}

Return your response as valid JSON in exactly this format:
{{
  "chosen_topic": "the topic title you chose",
  "source": "where it came from",
  "post": "the full linkedin post text including hashtags at end",
  "slides": {{
    "slide_1": {{
      "headline": "Bold hook headline",
      "subheading": "Supporting line"
    }},
    "slide_2": {{
      "headline": "The insight headline",
      "bullets": ["bullet 1", "bullet 2", "bullet 3"]
    }},
    "slide_3": {{
      "statement": "Closing bold statement",
      "cta": "Follow Bec Bennett for more AI insights"
    }}
  }}
}}"""
        }]
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


if __name__ == "__main__":
    topics_file = sys.argv[1] if len(sys.argv) > 1 else ".tmp/topics.json"

    with open(topics_file) as f:
        topics = json.load(f)

    content = write_content(topics)

    output_path = ".tmp/linkedin_content.json"
    with open(output_path, "w") as f:
        json.dump(content, f, indent=2)

    print(f"✓ LinkedIn content written to {output_path}")
    print(f"  Topic: {content['chosen_topic']}")
