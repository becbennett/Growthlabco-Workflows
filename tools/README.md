# Tools

Python scripts that handle deterministic execution. Each script does one thing reliably.

## Conventions
- Scripts read inputs from arguments or stdin, write outputs to stdout or a file
- API keys loaded from `.env` via `python-dotenv`
- Errors exit with a non-zero status code and a clear message
- No side effects beyond the stated purpose

## Adding a New Tool
1. Create `tools/your_tool_name.py`
2. Add a docstring at the top: what it does, inputs, outputs
3. Reference it in the relevant workflow under "Tools Used"
