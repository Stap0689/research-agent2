#!/usr/bin/env python3
"""witness.py -- state hub for the research-agent2 in-session accountability layer.

Manages per-notebook witness state and a ranked gotchas ledger. The witness-gate
PreToolUse hook reads this state to decide whether a notebook may run Q&A; the
live research session (the actor) and the witness subagent write to it.

State model (observability/witness-state/<notebook_id>.json):
  observer_mode        -- is this notebook running under the observer protocol
  methodology_loaded   -- did the session actually read the full methodology
  asks_since_witness   -- Q&A questions issued since the last witness verdict
  last_verdict         -- {phase, result PASS|FAIL, severity, at, deviations}
  checkpoints[]        -- actor-emitted phase-boundary snapshots
  verdicts[]           -- witness verdicts, append-only

Gotchas ledger (observability/gotchas.json): deviations discovered and corrected,
ranked by recurrence, surfaced at the top of every new observer session so the
methodology self-improves.

Commands:
  init      --notebook ID [--question Q] [--mode M]   create/refresh state, print top gotchas
  loaded    --notebook ID                             mark full methodology as read
  status    --notebook ID [--json]                    show current state
  checkpoint --notebook ID --phase P [--data JSON]    append a phase checkpoint
  verdict   --notebook ID --phase P --result PASS|FAIL [--severity S] [--deviations TXT]
  gotcha-add --text TXT [--rule ID]                   add/increment a gotcha
  gotcha-list [--top N] [--json]                      list ranked gotchas

Exit 0 on success, 1 on usage/state error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(os.environ.get("RESEARCH_AGENT_HOME", str(Path.home() / "research-agent")))
STATE_DIR = Path(os.environ.get("WITNESS_STATE_DIR", str(PROJECT / "observability" / "witness-state")))
GOTCHAS_PATH = Path(os.environ.get("WITNESS_GOTCHAS", str(PROJECT / "observability" / "gotchas.json")))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def state_path(notebook_id: str) -> Path:
    return STATE_DIR / f"{notebook_id}.json"


def load_state(notebook_id: str) -> dict | None:
    p = state_path(notebook_id)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def save_state(state: dict) -> None:
    _atomic_write(state_path(state["notebook_id"]), state)


def load_gotchas() -> list[dict]:
    if not GOTCHAS_PATH.is_file():
        return []
    try:
        data = json.loads(GOTCHAS_PATH.read_text())
        return data.get("gotchas", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    except (json.JSONDecodeError, OSError):
        return []


def save_gotchas(gotchas: list[dict]) -> None:
    _atomic_write(GOTCHAS_PATH, {"gotchas": gotchas})


def ranked_gotchas(top: int | None = None) -> list[dict]:
    g = sorted(load_gotchas(), key=lambda x: (x.get("count", 1), x.get("last_seen", "")), reverse=True)
    return g[:top] if top else g


# --- commands ---------------------------------------------------------------

def cmd_init(a: argparse.Namespace) -> int:
    state = load_state(a.notebook) or {}
    state.update({
        "notebook_id": a.notebook,
        "observer_mode": True,
        "created_at": state.get("created_at", now()),
        "updated_at": now(),
        "methodology_loaded": state.get("methodology_loaded", False),
        "asks_since_witness": state.get("asks_since_witness", 0),
        "last_verdict": state.get("last_verdict"),
        "checkpoints": state.get("checkpoints", []),
        "verdicts": state.get("verdicts", []),
    })
    if a.question:
        state["central_question"] = a.question
    if a.mode:
        state["output_mode"] = a.mode
    save_state(state)
    print(f"Observer mode ENABLED for notebook {a.notebook}")
    print(f"  state: {state_path(a.notebook)}")
    print(f"  methodology_loaded: {state['methodology_loaded']} (run `witness.py loaded` after reading the full SKILL)")
    top = ranked_gotchas(top=a.top or 7)
    if top:
        print(f"\n  Top recurring gotchas (seed for this session -- avoid repeating):")
        for i, g in enumerate(top, 1):
            rule = f" [{g['rule']}]" if g.get("rule") else ""
            print(f"    {i}. (x{g.get('count',1)}){rule} {g.get('text','')}")
    else:
        print("\n  No gotchas recorded yet.")
    return 0


def cmd_loaded(a: argparse.Namespace) -> int:
    state = load_state(a.notebook)
    if not state:
        print(f"ERROR: no observer state for {a.notebook}. Run `witness.py init` first.", file=sys.stderr)
        return 1
    state["methodology_loaded"] = True
    state["updated_at"] = now()
    save_state(state)
    print(f"methodology_loaded = True for {a.notebook}. Q&A gate unlocked (pending witness cadence).")
    return 0


def cmd_status(a: argparse.Namespace) -> int:
    state = load_state(a.notebook)
    if not state:
        print(f"No observer state for {a.notebook}.", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(state, indent=2))
        return 0
    lv = state.get("last_verdict")
    print(f"Notebook {a.notebook}")
    print(f"  observer_mode:       {state.get('observer_mode')}")
    print(f"  methodology_loaded:  {state.get('methodology_loaded')}")
    print(f"  asks_since_witness:  {state.get('asks_since_witness')}")
    print(f"  checkpoints:         {len(state.get('checkpoints', []))}")
    print(f"  verdicts:            {len(state.get('verdicts', []))}")
    print(f"  last_verdict:        {lv['result'] + ' @ phase ' + lv.get('phase','?') if lv else 'none'}")
    print(f"  completeness_certified: {state.get('completeness_certified', False)}")
    print(f"  completeness_passes: {len(state.get('completeness_passes', []))}")
    return 0


def cmd_checkpoint(a: argparse.Namespace) -> int:
    state = load_state(a.notebook)
    if not state:
        print(f"ERROR: no observer state for {a.notebook}. Run `witness.py init` first.", file=sys.stderr)
        return 1
    data = {}
    if a.data:
        try:
            data = json.loads(a.data)
        except json.JSONDecodeError:
            print("ERROR: --data must be valid JSON.", file=sys.stderr)
            return 1
    state.setdefault("checkpoints", []).append({"phase": a.phase, "at": now(), "data": data})
    state["updated_at"] = now()
    save_state(state)
    print(f"Checkpoint recorded for phase {a.phase} ({len(state['checkpoints'])} total).")
    return 0


def cmd_verdict(a: argparse.Namespace) -> int:
    state = load_state(a.notebook)
    if not state:
        print(f"ERROR: no observer state for {a.notebook}. Run `witness.py init` first.", file=sys.stderr)
        return 1
    result = a.result.upper()
    if result not in ("PASS", "FAIL"):
        print("ERROR: --result must be PASS or FAIL.", file=sys.stderr)
        return 1
    verdict = {
        "phase": a.phase,
        "result": result,
        "severity": a.severity or ("none" if result == "PASS" else "major"),
        "at": now(),
        "deviations": a.deviations or "",
    }
    state.setdefault("verdicts", []).append(verdict)
    state["last_verdict"] = verdict
    state["asks_since_witness"] = 0  # witness ran -> reset the cadence counter
    state["updated_at"] = now()
    save_state(state)
    print(f"Witness verdict {result} recorded for phase {a.phase}. Ask counter reset.")
    if result == "FAIL":
        print("  Q&A remains BLOCKED until a corrected PASS verdict is recorded.")
        print("  After remediating, record the fix as a gotcha: witness.py gotcha-add --text '...' --rule <id>")
    return 0


def cmd_completeness(a: argparse.Namespace) -> int:
    """Record an adversarial completeness-critic pass. CLEAN sets
    completeness_certified=true, which the completeness-gate requires before the
    findings deliverable may be written. OPEN records remaining veins and keeps
    termination blocked."""
    state = load_state(a.notebook)
    if not state:
        print(f"ERROR: no observer state for {a.notebook}. Run `witness.py init` first.", file=sys.stderr)
        return 1
    result = a.result.upper()
    if result not in ("CLEAN", "OPEN"):
        print("ERROR: --result must be CLEAN or OPEN.", file=sys.stderr)
        return 1
    entry = {
        "result": result,
        "at": now(),
        "critic": a.critic or "cold-subagent+actor",
        "veins": a.veins or "",
        "parts": a.parts or "",
    }
    state.setdefault("completeness_passes", []).append(entry)
    state["last_completeness"] = entry
    state["completeness_certified"] = (result == "CLEAN")
    state["updated_at"] = now()
    save_state(state)
    if result == "CLEAN":
        print(f"Completeness CERTIFIED for {a.notebook}. Deliverable write unlocked.")
        print("  (spec-coverage + zero bar-clearing veins, per the saturation_bar).")
    else:
        print(f"Completeness OPEN for {a.notebook}: remaining veins recorded. Termination BLOCKED.")
        if a.veins:
            print(f"  Open veins: {a.veins}")
        print("  Chase the veins, then re-run the completeness critic. Do NOT write the deliverable yet.")
    return 0


def cmd_gotcha_add(a: argparse.Namespace) -> int:
    gotchas = load_gotchas()
    text = a.text.strip()
    for g in gotchas:
        if g.get("text", "").strip().lower() == text.lower():
            g["count"] = g.get("count", 1) + 1
            g["last_seen"] = now()
            if a.rule:
                g["rule"] = a.rule
            save_gotchas(gotchas)
            print(f"Gotcha incremented (count={g['count']}): {text}")
            return 0
    gotchas.append({
        "text": text,
        "rule": a.rule or "",
        "count": 1,
        "first_seen": now(),
        "last_seen": now(),
    })
    save_gotchas(gotchas)
    print(f"Gotcha added: {text}")
    return 0


def cmd_gotcha_list(a: argparse.Namespace) -> int:
    g = ranked_gotchas(top=a.top)
    if a.json:
        print(json.dumps(g, indent=2))
        return 0
    if not g:
        print("No gotchas recorded.")
        return 0
    for i, x in enumerate(g, 1):
        rule = f" [{x['rule']}]" if x.get("rule") else ""
        print(f"{i}. (x{x.get('count',1)}){rule} {x.get('text','')}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="research-agent2 witness state hub")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init"); pi.add_argument("--notebook", required=True)
    pi.add_argument("--question"); pi.add_argument("--mode"); pi.add_argument("--top", type=int)
    pi.set_defaults(fn=cmd_init)

    pl = sub.add_parser("loaded"); pl.add_argument("--notebook", required=True); pl.set_defaults(fn=cmd_loaded)

    ps = sub.add_parser("status"); ps.add_argument("--notebook", required=True)
    ps.add_argument("--json", action="store_true"); ps.set_defaults(fn=cmd_status)

    pc = sub.add_parser("checkpoint"); pc.add_argument("--notebook", required=True)
    pc.add_argument("--phase", required=True); pc.add_argument("--data"); pc.set_defaults(fn=cmd_checkpoint)

    pv = sub.add_parser("verdict"); pv.add_argument("--notebook", required=True)
    pv.add_argument("--phase", required=True); pv.add_argument("--result", required=True)
    pv.add_argument("--severity"); pv.add_argument("--deviations"); pv.set_defaults(fn=cmd_verdict)

    pcomp = sub.add_parser("completeness"); pcomp.add_argument("--notebook", required=True)
    pcomp.add_argument("--result", required=True, help="CLEAN | OPEN")
    pcomp.add_argument("--veins", help="remaining high-value veins if OPEN")
    pcomp.add_argument("--parts", help="deliverable parts confirmed saturated")
    pcomp.add_argument("--critic", help="critic composition label")
    pcomp.set_defaults(fn=cmd_completeness)

    pga = sub.add_parser("gotcha-add"); pga.add_argument("--text", required=True)
    pga.add_argument("--rule"); pga.set_defaults(fn=cmd_gotcha_add)

    pgl = sub.add_parser("gotcha-list"); pgl.add_argument("--top", type=int)
    pgl.add_argument("--json", action="store_true"); pgl.set_defaults(fn=cmd_gotcha_list)

    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
