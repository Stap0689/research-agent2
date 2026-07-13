# Observer Runtime

The mechanical accountability layer for `research-agent2`. It turns the research
methodology from honor-system into enforced protocol: a state hub plus three
Claude Code hooks that block Q&A and the deliverable write until the session has
provably followed the non-negotiable core.

Nothing here fires for the stable `research-agent` (v1) skill — every hook is a
strict no-op unless a witness-state file with `observer_mode: true` exists for the
target notebook. v1 sessions never create that state, so they are untouched.

## Components

| File | Type | Role |
|------|------|------|
| `witness.py` | CLI | State hub. Records scope, methodology-read, phase checkpoints, witness verdicts, completeness certification, and a ranked gotchas ledger. |
| `hooks/witness-gate.py` | PreToolUse (Bash) | Blocks `notebooklm ask` when methodology isn't confirmed read, the last verdict was FAIL, or the ask cadence exceeded `max_asks_without_witness`. Advances the cadence counter on allow. |
| `hooks/witness-reinject.py` | PostToolUse (Bash) | After every observer `notebooklm ask`, re-injects the critical core + current cadence as context, fighting methodology decay over a long session. |
| `hooks/completeness-gate.py` | PreToolUse (Write/Edit) | The termination hard-wall. Blocks writing a `**/findings/**.md` deliverable for an active observer session until completeness is certified CLEAN. |

## Configuration (environment variables)

| Var | Default | Meaning |
|-----|---------|---------|
| `RESEARCH_AGENT_HOME` | `~/research-agent` | Research workspace root. Witness state and gotchas live under `observability/` here. |
| `WITNESS_STATE_DIR` | `$RESEARCH_AGENT_HOME/observability/witness-state` | Per-notebook observer state. |
| `WITNESS_GOTCHAS` | `$RESEARCH_AGENT_HOME/observability/gotchas.json` | Ranked recurring-deviation ledger. |
| `WITNESS_CRITICAL_CORE` | `~/.claude/skills/research-agent2/critical-core.json` | The enforced rule spine (shipped with the skill). |
| `COMPLETENESS_RECENCY_HOURS` | `12` | How recently an observer session must have been updated to still gate deliverable writes. |

Per-call bypasses (each is an explicit, logged decision to skip a gate — not a default):
`WITNESS_GATE_OVERRIDE=1`, `WITNESS_REINJECT_OVERRIDE=1`, `COMPLETENESS_GATE_OVERRIDE=1`.

## Install

```bash
# 1. Pick a workspace root and place the runtime there.
export RESEARCH_AGENT_HOME=~/research-agent
mkdir -p "$RESEARCH_AGENT_HOME/observer/hooks" "$RESEARCH_AGENT_HOME/observability" "$RESEARCH_AGENT_HOME/findings"
cp observer/witness.py "$RESEARCH_AGENT_HOME/observer/"
cp observer/hooks/*.py "$RESEARCH_AGENT_HOME/observer/hooks/"
chmod +x "$RESEARCH_AGENT_HOME/observer/hooks/"*.py "$RESEARCH_AGENT_HOME/observer/witness.py"

# 2. Install the skills (research-agent2 carries critical-core.json).
cp -r research-agent2/ ~/.claude/skills/research-agent2/
cp -r notebooklm/     ~/.claude/skills/notebooklm/
```

Persist `RESEARCH_AGENT_HOME` in your shell profile (or in the hook `env` block
below) so every session and hook resolves the same workspace.

## Wire the hooks (Claude Code `settings.json`)

Add these to `~/.claude/settings.json`. Point the commands at wherever you copied
the hooks (the `$RESEARCH_AGENT_HOME/observer/hooks` location from the install
step). Set `RESEARCH_AGENT_HOME` in an `env` block if it isn't already exported to
the Claude Code process.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$HOME/research-agent/observer/hooks/witness-gate.py", "timeout": 5 }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "$HOME/research-agent/observer/hooks/completeness-gate.py", "timeout": 5 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$HOME/research-agent/observer/hooks/witness-reinject.py", "timeout": 5 }
        ]
      }
    ]
  }
}
```

If you also run the v1 source-audit gate (`../quality-gates/`), both PreToolUse
Bash hooks coexist — `witness-gate.py` only adds enforcement for observer notebooks.

## witness.py command reference

```bash
witness.py init       --notebook ID [--question Q] [--mode M]   # enable observer mode, print top gotchas
witness.py loaded     --notebook ID                             # mark full methodology as read (unlocks Q&A gate)
witness.py status     --notebook ID [--json]                    # show current state
witness.py checkpoint --notebook ID --phase P [--data JSON]     # append a phase-boundary snapshot
witness.py verdict    --notebook ID --phase P --result PASS|FAIL [--severity S] [--deviations TXT]
witness.py completeness --notebook ID --result CLEAN|OPEN [--parts "..."] [--veins "..."]
witness.py gotcha-add --text TXT [--rule ID]                    # add/increment a recurring deviation
witness.py gotcha-list [--top N] [--json]                       # list ranked gotchas
```

## Fail-open by design

Every hook fails open: any exception, unparseable input, missing state, or missing
notebook ID results in "allow." The gates add friction only when they can prove a
notebook is an active, uncertified observer session. They never block unrelated
work, and they never hard-fail a session on their own error.
