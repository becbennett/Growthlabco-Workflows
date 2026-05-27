# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools) managed by Growth Lab Co.

## The WAT Architecture

**Layer 1: Workflows** — Markdown SOPs in `workflows/`
**Layer 2: Agents** — This is your role. Read workflows, run tools, handle failures.
**Layer 3: Tools** — Python scripts in `tools/` that do the actual execution.

## How to Operate

1. Check `tools/` before building anything new
2. Fix errors, update the workflow, move on
3. Final outputs go to Google Drive or email — never just local files
4. If a tool uses paid API calls, confirm with the client before retrying after an error

## File Structure

```
.tmp/           # Temporary files — regenerated as needed, never commit
tools/          # Python execution scripts
workflows/      # Markdown SOPs
.env            # API keys (NEVER commit)
token.json      # Google OAuth (NEVER commit)
```
