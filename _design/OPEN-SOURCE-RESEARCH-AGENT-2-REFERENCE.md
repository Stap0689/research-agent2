# OPEN-SOURCE-RESEARCH-AGENT-2-REFERENCE

**Status:** Active (public distribution)
**Last Major Update:** 2026-07-13
**Harness Version:** n/a — this is a public skills repo; harness conventions apply on the private development side only

---

## 1. Purpose & Scope

Public GitHub distribution of the **observer-model fork** of the research-agent
skill. It carries the full 7-phase NotebookLM research methodology (identical to
[research-agent](https://github.com/Stap0689/research-agent)) PLUS an in-session
accountability layer: a witness/completeness loop and three Claude Code hooks that
mechanically block Q&A and the deliverable write until the session provably
followed a non-negotiable core (`critical-core.json`).

The repository is the sanitized export of the private development work. No
private-skill internals, no enterprise identifiers, no personal references, no
AIMIS-specific content (the private synthesis-pass protocol is deliberately
excluded).

---

## 2. Zone Mapping

Unlike the v1 distribution (markdown + assets only), this repo ships **runtime
code** — the observer state hub and hooks — so the four-zone model partially
applies.

| Zone | Realization | Notes |
|------|-------------|-------|
| control-plane | n/a | No orchestration config in the repo; hooks are wired by the consumer's settings.json |
| pipeline | `research-agent2/`, `notebooklm/` | Skill directories — each carries a `SKILL.md` plus supporting markdown |
| observability | `observer/` | The accountability runtime: `witness.py` state hub + PreToolUse/PostToolUse hooks |
| _design | `_design/` | Project knowledge (canonical harness path) |

`quality-gates/` (source-audit + persona-guard) is shared verbatim with v1.

---

## 3. Layer / Module Table

| Path | Role |
|------|------|
| `research-agent2/SKILL.md` | Thin stub: the non-negotiable core + mechanically gated run order |
| `research-agent2/OBSERVER-PROTOCOL.md` | The witness loop — checkpoint, witness subagent, verdict, remediation, completeness critic |
| `research-agent2/critical-core.json` | Single source of truth for the enforced rule spine (consumed by stub, re-inject hook, and witness rubric) |
| `research-agent2/methodology/*.md` | The full research-agent methodology (7-phase workflow + 5 appendices), identical to v1 |
| `notebooklm/SKILL.md` | Full NotebookLM API wrapper + CLI reference |
| `observer/witness.py` | State hub: scope, methodology-read, checkpoints, verdicts, completeness cert, gotchas ledger |
| `observer/hooks/witness-gate.py` | PreToolUse gate on `notebooklm ask` (methodology-read / verdict / cadence) |
| `observer/hooks/witness-reinject.py` | PostToolUse re-injection of the core after every observer Q&A |
| `observer/hooks/completeness-gate.py` | PreToolUse termination hard-wall on `/findings/*.md` writes |
| `quality-gates/source-audit.py` | Classify + auto-delete hard-reject sources |
| `quality-gates/persona-guard.py` | Prevent silent custom-persona wipe |
| `assets/` | README hero image |

---

## 4. Dependencies & Constraints

**External:**
- Google NotebookLM (account required; OAuth handled by notebooklm-py)
- `notebooklm-py` CLI — https://github.com/teng-lin/notebooklm-py
- Claude Code (Agent/Task tool for the witness subagent; hooks for the gates)
- Python 3.10+ (uses `from __future__ import annotations`; no third-party deps in the observer runtime)

**Configuration (env vars, all defaulted):**
`RESEARCH_AGENT_HOME` (default `~/research-agent`), `WITNESS_STATE_DIR`,
`WITNESS_GOTCHAS`, `WITNESS_CRITICAL_CORE` (default
`~/.claude/skills/research-agent2/critical-core.json`), `COMPLETENESS_RECENCY_HOURS`.

**Hard constraints:**
- No private references (AIMIS, enterprise identifiers, internal tooling paths, personal home paths)
- No dependence on private host-local paths in skill content or scripts
- Every hook must fail open and no-op for non-observer notebooks (v1 must stay pristine)

---

## 5. Canonical Conventions (Deviations)

| Convention | Deviation | Why |
|------------|-----------|-----|
| Top-level control-plane/, pipeline/, observability/ directories | `observer/` used instead of `observability/` | Consumer-facing runtime; name reflects the accountability model |
| .claude/settings.json with local harness hook | Not created | Public repo must not depend on private harness paths; hook wiring is documented for the consumer to add |
| CLAUDE.md | Not created | Repo is consumed as skills by end users, not developed as a code project |
| Plan folders + handoffs under _design/plans/ | Seeded empty | Reserved for future contribution process |
| Private synthesis-pass protocol | Excluded | AIMIS/enterprise-specific; not generalizable, not shipped |
| ra2 methodology appendices | Sourced from the v1 public package | The private ra2 copies carried enterprise-specific worked examples; the v1 public versions are already sanitized |

---

## 6. Plan History (Closed Plans, Chronological)

None — this distribution tracks upstream skill revisions via git history, not phased plans.

---

## 7. Open Plans

None — contribution workflow TBD.

---

## 8. ADR Index

None yet. `_design/adrs/` reserved for architectural decisions about the public distribution.

---

## 9. Migration Notes

### 2026-07-13 — Initial public export

Sanitized export of the private research-agent2 (observer model) work into a
standalone public repository, mirroring the structure of the v1
open-source-research-agent distribution. Observer scripts were genericized: the
`RESEARCH_AGENT_HOME` default was changed from a personal `~/projects/research-agent`
path to a neutral `~/research-agent`, and help-text paths were reduced to bare
`witness.py`. Methodology appendices were sourced from the already-sanitized v1
public package (not the private ra2 copies, which carried enterprise worked
examples). The private AIMIS synthesis-pass protocol was excluded and its stub
reference removed.

---

*Master reference is the semantic single source of truth for this public distribution. Private development state lives off-repo.*
