# Project Index: open-source-research-agent2

**Last Updated:** 2026-07-13
**Harness Version:** n/a (public distribution — harness conventions apply on the private development side)
**Active Plan:** None (contribution workflow TBD)
**Current Phase:** N/A

---

## Active Work

| Plan Folder | Phase | Status | Latest Handoff |
|-------------|-------|--------|----------------|
| — | — | — | — |

---

## Open Handoffs (awaiting next session)

- None.

---

## Recent ADRs (last 5)

- None yet. `_design/adrs/` reserved for public-distribution decisions.

---

## Key Files & Purposes (manually maintained)

| File | Purpose |
|------|---------|
| `research-agent2/SKILL.md` | Observer-model stub: non-negotiable core + gated run order |
| `research-agent2/OBSERVER-PROTOCOL.md` | Witness loop + completeness critic protocol |
| `research-agent2/critical-core.json` | Enforced rule spine (single source of truth) |
| `research-agent2/methodology/` | Full research-agent methodology (7-phase workflow + appendices) |
| `notebooklm/SKILL.md` | Full NotebookLM API wrapper + CLI reference |
| `observer/witness.py` | Accountability state hub (checkpoints, verdicts, completeness, gotchas) |
| `observer/hooks/` | witness-gate · witness-reinject · completeness-gate |
| `quality-gates/` | Source-quality enforcement (shared with v1) |
| `assets/` | README hero image |

---

## Code Index Artifacts

- `_design/code-index.json` — observer runtime (`observer/`, `quality-gates/`) `.py` files
- `_design/code-index-compact.md` — compact dependency map

---

## Distribution Notes

This repo is a public skills distribution **with runtime code** (the observer
layer). It deliberately has **no `CLAUDE.md`** and **no `.claude/settings.json`** —
the repository is consumed as skills by end users, not developed against by Claude
Code, and it must not depend on private harness paths. Hook wiring is documented in
`observer/README.md` for the consumer to add to their own `settings.json`.

This `INDEX.md` exists for structural parity with other harness-retrofit projects;
it is **not** `@import`ed from any CLAUDE.md (since there is none).

---

*This file is part of the canonical `_design/` tree documented in the private harness governance.*
