"""
Fetches trending AI in marketing/customer service topics from Reddit (no API key needed)
and RSS feeds. Outputs a JSON list of top topics to stdout.
Usage: python3 tools/fetch_trending_topics.py
"""

import json
import sys
import time
import requests
import feedparser

REDDIT_SUBS = ["artificial", "ChatGPT", "marketing", "customerservice", "smallbusiness"]

RSS_FEEDS = [
    "https://feeds.feedburner.com/venturebeat/SZYF",
    "https://www.marketingaiinstitute.com/blog/rss.xml",
    "https://feeds.feedburner.com/TechCrunch/",
]

KEYWORDS = [
    "AI", "artificial intelligence", "automation", "chatbot", "LLM",
    "customer service", "marketing", "GPT", "Claude", "CRM", "agent"
]

HEADERS = {"User-Agent": "GrowthLabContent/1.0 (content research bot)"}


def is_relevant(text):
    return any(k.lower() in text.lower() for k in KEYWORDS)


def fetch_reddit():
    topics = []
    for sub in REDDIT_SUBS:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            posts = response.json()["data"]["children"]
            for post in posts:
                d = post["data"]
                if is_relevant(d["title"]):
                    topics.append({
                        "source": f"r/{sub}",
                        "title": d["title"],
                        "url": f"https://reddit.com{d['permalink']}",
                        "score": d["score"],
                        "comments": d["num_comments"],
                    })
            time.sleep(1)  # polite delay between subreddit requests
        except Exception as e:
            print(f"Reddit fetch warning (r/{sub}): {e}", file=sys.stderr, flush=True)
    return topics


def fetch_rss():
    topics = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                if is_relevant(title):
                    topics.append({
                        "source": feed.feed.get("title", feed_url),
                        "title": title,
                        "url": link,
                        "score": 0,
                        "comments": 0,
                    })
        except Exception as e:
            print(f"RSS fetch warning ({feed_url}): {e}", file=sys.stderr, flush=True)
    return topics


if __name__ == "__main__":
    topics = fetch_reddit() + fetch_rss()

    seen = set()
    unique = []
    for t in topics:
        key = t["title"][:60].lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)

    unique.sort(key=lambda x: x["score"], reverse=True)
    print(json.dumps(unique[:15], indent=2))
