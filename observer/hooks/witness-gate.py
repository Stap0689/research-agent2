#!/usr/bin/env python3
"""PreToolUse gate: enforce the research-agent2 in-session accountability loop.

Runs ALONGSIDE research-qa-gate.py (does not replace it). Fires on `notebooklm
ask`. It is a strict NO-OP for any notebook that is not running under the
observer protocol -- i.e. it only acts when a witness-state file exists for the
notebook AND observer_mode is true. This is what keeps the stable /research-agent
skill completely unaffected: v1 sessions never create observer state.

For an observer notebook, it blocks Q&A when:
  1. methodology_loaded is not true       -> full methodology was not read (fixes the thin-stub skip)
  2. the last witness verdict is FAIL      -> a deviation was found and not yet remediated
  3. asks_since_witness >= max cadence     -> too long without an independent witness checkpoint

On allow, it increments asks_since_witness so the cadence advances.

Reads pre-computed state only; no network calls. Fail-open on any exception.

Env overrides:
  WITNESS_GATE_OVERRIDE=1   -- bypass this gate for one call
  WITNESS_STATE_DIR         -- override witness-state directory
  WITNESS_CRITICAL_CORE     -- override critical-core.json path
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
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
DEFAULT_MAX_ASKS = 8


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


def max_asks() -> int:
    try:
        core = json.loads(CRITICAL_CORE.read_text())
        return int(core.get("config", {}).get("max_asks_without_witness", DEFAULT_MAX_ASKS))
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return DEFAULT_MAX_ASKS


def load_state(notebook_id: str) -> dict | None:
    p = STATE_DIR / f"{notebook_id}.json"
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def bump_asks(notebook_id: str, state: dict) -> None:
    state["asks_since_witness"] = state.get("asks_since_witness", 0) + 1
    p = STATE_DIR / f"{notebook_id}.json"
    try:
        fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
        with os.fdopen(fd, "w") as fh:
            json.dump(state, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, p)
    except OSError:
        pass


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main() -> None:
    if os.environ.get("WITNESS_GATE_OVERRIDE") == "1":
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
        sys.exit(0)  # research-qa-gate already denies missing notebook IDs

    state = load_state(notebook_id)
    if not state or state.get("observer_mode") is not True:
        sys.exit(0)  # NOT an observer session -> no-op (v1 stays pristine)

    w = "witness.py"

    if state.get("methodology_loaded") is not True:
        deny(
            f"BLOCKED (observer): full methodology not confirmed read for notebook {notebook_id}.\n\n"
            "The stub summary is not a substitute. Read methodology/SKILL.md and the appendices "
            "it references, then record it:\n"
            f"  python3 {w} loaded --notebook {notebook_id}\n\n"
            "To bypass: WITNESS_GATE_OVERRIDE=1"
        )
        return

    lv = state.get("last_verdict")
    if isinstance(lv, dict) and lv.get("result") == "FAIL":
        deviations = lv.get("deviations", "") or "(see witness verdict)"
        deny(
            f"BLOCKED (observer): last witness verdict for notebook {notebook_id} was FAIL "
            f"at phase {lv.get('phase','?')}.\n\n"
            f"Deviations: {deviations}\n\n"
            "Remediate the deviation, log the fix as a gotcha, then record a corrected verdict:\n"
            f"  python3 {w} gotcha-add --text '<what went wrong + fix>' --rule <rule-id>\n"
            f"  python3 {w} verdict --notebook {notebook_id} --phase {lv.get('phase','?')} --result PASS\n\n"
            "To bypass: WITNESS_GATE_OVERRIDE=1"
        )
        return

    limit = max_asks()
    asks = state.get("asks_since_witness", 0)
    if asks >= limit:
        deny(
            f"BLOCKED (observer): {asks} Q&A questions since the last witness checkpoint "
            f"(limit {limit}) for notebook {notebook_id}.\n\n"
            "Independent witness review is due. Write a phase checkpoint, spawn the witness "
            "subagent per OBSERVER-PROTOCOL.md, and record its verdict:\n"
            f"  python3 {w} checkpoint --notebook {notebook_id} --phase <P> --data '{{...}}'\n"
            f"  python3 {w} verdict --notebook {notebook_id} --phase <P> --result PASS|FAIL\n\n"
            "A PASS verdict resets the counter and unlocks Q&A.\n"
            "To bypass: WITNESS_GATE_OVERRIDE=1"
        )
        return

    # Allowed -> advance the cadence counter.
    bump_asks(notebook_id, state)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
