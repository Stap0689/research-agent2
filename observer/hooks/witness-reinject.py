#!/usr/bin/env python3
"""PostToolUse hook: re-inject the critical core after every observer Q&A.

Fires after `notebooklm ask`. For observer notebooks only, it injects a compact
reminder of the non-negotiable core plus the current witness cadence, as
additionalContext. This fights the real failure mode: the methodology is read
once at turn 1 and is faint by turn 40. Re-surfacing the core at the exact moment
the next question is being formed keeps it salient.

Strict no-op for non-observer notebooks (keeps /research-agent unaffected).
Fail-open on any exception.

Env overrides:
  WITNESS_REINJECT_OVERRIDE=1   -- skip for one call
  WITNESS_STATE_DIR / WITNESS_CRITICAL_CORE -- path overrides
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

NOTEBOOKLM_ASK_RE = re.compile(r"(?:^|[;&|]\s*|\$\(\s*)notebooklm\s+ask\b")
NOTEBOOK_FLAG_RE = re.compile(r"(?:--notebook|-n)\s+([0-9a-f-]{8,})")

PROJECT = Path(os.environ.get("RESEARCH_AGENT_HOME", str(Path.home() / "research-agent")))
STATE_DIR = Path(os.environ.get("WITNESS_STATE_DIR", str(PROJECT / "observability" / "witness-state")))
CRITICAL_CORE = Path(os.environ.get(
    "WITNESS_CRITICAL_CORE",
    str(Path.home() / ".claude" / "skills" / "research-agent2" / "critical-core.json"),
))
CONTEXT_CANDIDATES = [
    Path.home() / ".notebooklm" / "context.json",
    Path.home() / ".config" / "notebooklm" / "context.json",
]


def extract_notebook_id(command: str) -> str | None:
    m = NOTEBOOK_FLAG_RE.search(command)
    if m:
        return m.group(1)
    for path in CONTEXT_CANDIDATES:
        try:
            ctx = json.loads(path.read_text())
            nb = ctx.get("notebook_id") or ctx.get("active_notebook")
            if nb:
                return nb
        except (OSError, json.JSONDecodeError):
            continue
    return None


def load_json(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def main() -> None:
    if os.environ.get("WITNESS_REINJECT_OVERRIDE") == "1":
        sys.exit(0)
    try:
        raw = sys.stdin.read()
    except OSError:
        sys.exit(0)
    if not raw.strip():
        sys.exit(0)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)
    command = (data.get("tool_input", {}) or {}).get("command", "") or ""
    if not NOTEBOOKLM_ASK_RE.search(command):
        sys.exit(0)

    notebook_id = extract_notebook_id(command)
    if not notebook_id:
        sys.exit(0)

    state = load_json(STATE_DIR / f"{notebook_id}.json")
    if not isinstance(state, dict) or state.get("observer_mode") is not True:
        sys.exit(0)  # non-observer -> no-op

    core = load_json(CRITICAL_CORE) or {}
    rules = core.get("rules", [])
    limit = int(core.get("config", {}).get("max_asks_without_witness", 8))
    asks = state.get("asks_since_witness", 0)

    blockers = [r for r in rules if r.get("severity") == "blocker"]
    lines = [f"  - {r['id']}: {r['text'].split('.')[0]}." for r in blockers[:6]]
    remaining = max(0, limit - asks)
    cadence = (
        f"witness review DUE now ({asks}/{limit})" if remaining == 0
        else f"{asks}/{limit} questions since last witness checkpoint ({remaining} left)"
    )

    msg = (
        f"[research-agent2 witness] {cadence}.\n"
        "Non-negotiable core (do not skip, corpus integrity depends on these):\n"
        + "\n".join(lines)
        + "\nBefore your next question, run the 5-check bidirectional eval on the response you "
        "just got: sufficiency, source-grounding, thin-spot, contradiction, phase-fit. "
        "Your next question should address a failed check, not the next item on a list."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
