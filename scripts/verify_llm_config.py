#!/usr/bin/env python3
"""Verify the LLM provider config end-to-end.

Runs in three phases:
  1. Env sanity   — confirm .env variables are loaded
  2. Simple call  — one short messages.create() without tools
  3. Tool-use     — a call that defines a tool and expects tool_use response

If OpenRouter + Anthropic SDK + tool-use all work, you're done. If the simple
call works but tool-use fails, we need to rewrite to the openai SDK.
"""
# ---- auto-activate venv ----
import os
import sys
from pathlib import Path

_VENV_DIR = Path(__file__).resolve().parents[1] / ".venv"
_VENV_PY = _VENV_DIR / "bin" / "python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

GREEN = "\033[92m"
RED   = "\033[91m"
DIM   = "\033[2m"
B     = "\033[1m"
R     = "\033[0m"

MODEL = os.environ.get("LEXAI_MODEL", "claude-sonnet-4-6")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def header(s):
    print(f"\n{B}── {s} ──{R}")


def ok(msg):
    print(f"  {GREEN}✓{R} {msg}")


def fail(msg):
    print(f"  {RED}✗{R} {msg}")


# ---------------------------------------------------------------------------
header("Phase 1 — env sanity")
if not API_KEY or "PASTE" in API_KEY or API_KEY.startswith("sk-XXX"):
    fail("ANTHROPIC_API_KEY not set. Edit .env and paste your key.")
    sys.exit(1)

ok(f"ANTHROPIC_API_KEY set ({len(API_KEY)} chars, starts with '{API_KEY[:7]}...')")
ok(f"ANTHROPIC_BASE_URL = {BASE_URL}")
ok(f"LEXAI_MODEL         = {MODEL}")

provider = "OpenRouter" if "openrouter" in BASE_URL else (
    "Direct Anthropic" if "anthropic.com" in BASE_URL else "Custom"
)
print(f"  {DIM}provider inferred: {provider}{R}")

# ---------------------------------------------------------------------------
header("Phase 2 — simple messages.create() (no tools)")
client = Anthropic()  # picks up ANTHROPIC_API_KEY + ANTHROPIC_BASE_URL from env

try:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=60,
        messages=[
            {"role": "user", "content": "Reply in exactly 5 words: Why is the sky blue?"}
        ],
    )
    text = ""
    for b in resp.content:
        if hasattr(b, "text"):
            text = b.text
            break
    ok(f"model responded: {text!r}")
    ok(f"stop_reason = {resp.stop_reason}")
    ok(f"usage: input={resp.usage.input_tokens} output={resp.usage.output_tokens}")
except Exception as e:
    fail(f"simple call failed: {type(e).__name__}: {e}")
    print(f"\n{DIM}  → likely fixes:")
    print(f"     · check API key is correct")
    print(f"     · check model ID '{MODEL}' is available on this provider")
    print(f"     · if using OpenRouter, model should be like 'anthropic/claude-sonnet-4.6'{R}")
    sys.exit(1)

# ---------------------------------------------------------------------------
header("Phase 3 — tool-use call")
TOOL = {
    "name": "get_weather",
    "description": "Get the current weather for a given city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}

try:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        tools=[TOOL],
        messages=[
            {"role": "user", "content": "What's the weather in Mumbai right now? Use the tool."}
        ],
    )
    ok(f"stop_reason = {resp.stop_reason}")
    tool_use_found = False
    for b in resp.content:
        if hasattr(b, "type") and b.type == "tool_use":
            tool_use_found = True
            ok(f"tool_use emitted: name={b.name}, input={b.input}")
            break
    if tool_use_found:
        ok("native Anthropic tool-use format is supported → our pipeline will work unchanged")
    else:
        fail("no tool_use block in response — tool-calling may not work via this provider")
        print(f"  {DIM}response content blocks: {[type(b).__name__ for b in resp.content]}{R}")
        for b in resp.content:
            if hasattr(b, "text"):
                print(f"  {DIM}text: {b.text[:200]}{R}")
except Exception as e:
    fail(f"tool-use call failed: {type(e).__name__}: {e}")
    print(f"\n{DIM}  → if 'tool_use' is not supported via {BASE_URL}, we'd need to rewrite")
    print(f"  → to the openai SDK format (different tool-calling protocol).{R}")
    sys.exit(1)

print(f"\n{B}{GREEN}all three phases passed ✓{R}")
print(f"{DIM}configuration is ready — run scripts/interactive_demo.py or streamlit run app.py{R}\n")
