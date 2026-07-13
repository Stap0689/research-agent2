#!/usr/bin/env python3
"""PreToolUse gate: prevent accidental persona wipe via partial configure calls.

Intercepts 'notebooklm configure' commands that include --response-length or
--mode but NOT --persona. These commands reset the notebook chat goal to DEFAULT,
silently destroying any custom persona previously configured.

The root cause is notebooklm-py's configure() logic: when --persona is omitted,
it defaults goal to ChatGoal.DEFAULT (1) instead of preserving the existing goal.
This gate blocks the dangerous patterns and instructs the caller to include
--persona to preserve their custom configuration.

Fail-open on all exceptions (exit 0).

Env overrides:
  PERSONA_GUARD_OVERRIDE=1  -- bypass this gate for one call
"""

from __future__ import annotations

import json
import re
import os
import sys

CONFIGURE_RE = re.compile(r"\bnotebooklm\s+configure\b")
HAS_PERSONA_RE = re.compile(r"--persona\b")
HAS_MODE_RE = re.compile(r"--mode\b")
HAS_RESPONSE_LENGTH_RE = re.compile(r"--response-length\b")


def deny(reason: str) -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(out))
    sys.exit(0)


def main() -> None:
    if os.environ.get("PERSONA_GUARD_OVERRIDE") == "1":
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

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""

    if not CONFIGURE_RE.search(command):
        sys.exit(0)

    has_persona = HAS_PERSONA_RE.search(command)
    has_mode = HAS_MODE_RE.search(command)
    has_response_length = HAS_RESPONSE_LENGTH_RE.search(command)

    if has_persona:
        sys.exit(0)

    if has_mode:
        deny(
            "BLOCKED: 'notebooklm configure --mode' will reset any custom persona to DEFAULT.\n\n"
            "If you intend to keep the custom persona, use:\n"
            '  notebooklm configure --persona "..." --response-length longer\n\n'
            "If you intentionally want to switch away from custom persona to a preset mode, "
            "set PERSONA_GUARD_OVERRIDE=1 and re-run."
        )
        return

    if has_response_length:
        deny(
            "BLOCKED: 'notebooklm configure --response-length' without --persona will reset "
            "the chat goal to DEFAULT, destroying the custom persona.\n\n"
            "To change response length while preserving your persona, include --persona:\n"
            '  notebooklm configure --persona "..." --response-length <value> --notebook <ID>\n\n'
            "To bypass: PERSONA_GUARD_OVERRIDE=1"
        )
        return

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
