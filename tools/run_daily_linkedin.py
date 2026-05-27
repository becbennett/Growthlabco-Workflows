"""
Master orchestrator for the daily LinkedIn content workflow.
Runs all 4 steps in sequence: fetch → write → generate → deliver
Usage: python3 tools/run_daily_linkedin.py
"""

import subprocess
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(script, *args):
    cmd = [sys.executable, os.path.join(BASE, "tools", script)] + list(args)
    result = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR in {script}:\n{result.stderr}")
        sys.exit(1)
    return result.stdout


print("=" * 50)
print("Growth Lab Co — Daily LinkedIn Content")
print("=" * 50)

print("\n[1/4] Fetching trending topics...")
topics_path = os.path.join(BASE, ".tmp", "topics.json")
with open(topics_path, "w") as f:
    result = subprocess.run(
        [sys.executable, os.path.join(BASE, "tools", "fetch_trending_topics.py")],
        cwd=BASE, stdout=f, text=True
    )
    if result.returncode != 0:
        print(f"ERROR in fetch_trending_topics.py")
        sys.exit(1)
print("✓ Topics saved to .tmp/topics.json")

print("\n[2/4] Writing LinkedIn post with Claude...")
run("write_linkedin_post.py", ".tmp/topics.json")

print("\n[3/4] Generating infographic slides...")
run("generate_infographic.py")

print("\n[4/4] Delivering via email + Drive...")
run("deliver_content.py")

print("\n✓ Done! Check your inbox.")
