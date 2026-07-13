#!/usr/bin/env python3
"""PreToolUse gate: the termination hard-wall for research-agent2.

Termination in a research session is not a tool call (it is the absence of more
questions plus writing the deliverable), so the enforceable choke point is the
DELIVERABLE WRITE. This hook fires on Write/Edit of a research findings document
and blocks it until an adversarial completeness critic has certified saturation
(`witness.py completeness --result CLEAN`, which sets completeness_certified).

Scope guards that keep this from ever blocking unrelated work:
  - Only findings-deliverable paths (contain '/findings/' and end in '.md').
  - Only when a genuinely ACTIVE observer session is uncertified: a witness-state
    file with observer_mode=true, completeness_certified!=true, updated within
    RECENCY_HOURS. Stale/abandoned observer states never block.
  - No active uncertified observer session  ->  no-op (v1 and normal work untouched).

Fail-open on any exception.

Env overrides:
  COMPLETENESS_GATE_OVERRIDE=1  -- bypass for one call
  WITNESS_STATE_DIR             -- override witness-state directory
  COMPLETENESS_RECENCY_HOURS    -- active-session window (default 12)
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(os.environ.get("RESEARCH_AGENT_HOME", str(Path.home() / "research-agent")))
STATE_DIR = Path(os.environ.get("WITNESS_STATE_DIR", str(PROJECT / "observability" / "witness-state")))
RECENCY_HOURS = float(os.environ.get("COMPLETENESS_RECENCY_HOURS", "12"))

# Deliverables carry "**Notebook:** <uuid>" in their header; used to scope the gate
# to the specific notebook this write belongs to (parallel-session safety).
NOTEBOOK_HEADER_RE = re.compile(
    r"(?i)notebook\W{0,4}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
)


def is_findings_path(path: str) -> bool:
    p = path.lower()
    return "/findings/" in p and p.endswith(".md")


def is_blocking_state(st: dict) -> bool:
    """An observer session that has done real work but is not yet certified."""
    return (
        st.get("observer_mode") is True
        and st.get("completeness_certified") is not True
        and st.get("terminated") is not True
        and bool(st.get("checkpoints") or st.get("verdicts"))
    )


def load_state_for(notebook_id: str) -> dict | None:
    try:
        return json.loads((STATE_DIR / f"{notebook_id}.json").read_text())
    except (OSError, json.JSONDecodeError):
        return None


def target_notebook_id(data: dict) -> str | None:
    """The notebook this deliverable belongs to: parse the header from Write content,
    or from the target file for an Edit. None if undeterminable."""
    ti = data.get("tool_input", {}) or {}
    content = ti.get("content") or ""
    m = NOTEBOOK_HEADER_RE.search(content)
    if m:
        return m.group(1)
    fp = ti.get("file_path")
    if fp:
        try:
            m = NOTEBOOK_HEADER_RE.search(Path(fp).read_text()[:4000])
            if m:
                return m.group(1)
        except OSError:
            pass
    return None


def parse_ts(s: str):
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def active_uncertified_observer() -> dict | None:
    """Return an active, uncertified observer state if one exists, else None."""
    if not STATE_DIR.is_dir():
        return None
    now = datetime.now(timezone.utc)
    for f in STATE_DIR.glob("*.json"):
        try:
            st = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if st.get("observer_mode") is not True:
            continue
        if st.get("completeness_certified") is True:
            continue
        if st.get("terminated") is True:
            continue
        # A never-started stray (init only, no checkpoints and no verdicts) is not
        # an active research session and must not block unrelated deliverable writes.
        if not st.get("checkpoints") and not st.get("verdicts"):
            continue
        ts = parse_ts(st.get("updated_at") or st.get("created_at") or "")
        if ts is None:
            continue
        age_h = (now - ts).total_seconds() / 3600.0
        if age_h <= RECENCY_HOURS:
            return st
    return None


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
    if os.environ.get("COMPLETENESS_GATE_OVERRIDE") == "1":
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

    if data.get("tool_name") not in ("Write", "Edit"):
        sys.exit(0)
    tool_input = data.get("tool_input", {}) or {}
    path = tool_input.get("file_path", "") or ""
    if not is_findings_path(path):
        sys.exit(0)

    w = "witness.py"

    # Parallel-session safety: scope the gate to the deliverable's OWN notebook when
    # identifiable, so a co-running uncertified session (e.g. R1b) never blocks a
    # certified one's write (e.g. R1a).
    target = target_notebook_id(data)
    if target:
        st = load_state_for(target)
        if not st or not is_blocking_state(st):
            sys.exit(0)  # this deliverable's notebook is certified / not observed -> allow
        nb = target
    else:
        # Notebook undeterminable -> conservative fallback (block on any active uncertified).
        st = active_uncertified_observer()
        if not st:
            sys.exit(0)
        nb = st.get("notebook_id", "unknown")
    deny(
        f"BLOCKED (observer): cannot write the findings deliverable for notebook {nb} — "
        "completeness is not certified.\n\n"
        "Termination requires an adversarial completeness critic to certify saturation "
        "before the deliverable is written. Run the hybrid completeness pass "
        "(cold-subagent spec-coverage audit + actor deep vein critique) per "
        "OBSERVER-PROTOCOL.md. If it finds open veins, chase them; when it returns clean:\n"
        f"  python3 {w} completeness --notebook {nb} --result CLEAN --parts '<deliverable parts saturated>'\n\n"
        "There is no minimum and no count target — the bar is demonstrated mastery, not a "
        "checkpoint. Pausing at the witness cadence is not saturation.\n"
        "To bypass: COMPLETENESS_GATE_OVERRIDE=1"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
