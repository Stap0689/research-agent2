## open-source-research-agent2 Code Dependency Map
Generated: 2026-07-13 | 6 files, LoC total 1278 | stdlib-only, no internal import edges

### High-Impact Modules (change = most ripple)
| Module | LoC | Impact | Notes |
|--------|-----|--------|-------|
| `research-agent2/critical-core.json` | (data) | High | Single source of truth consumed by the stub, `witness-reinject.py`, and the witness rubric. Editing a rule changes all three. |
| `observer/witness.py` | 327 | High | State hub for the whole observer loop; every hook reads the state it writes. |
| `observer/hooks/witness-gate.py` | 183 | Med | Q&A gate; reads witness state + critical-core config. |
| `observer/hooks/completeness-gate.py` | 189 | Med | Deliverable-write hard-wall; reads witness state. |
| `observer/hooks/witness-reinject.py` | 125 | Low | Non-blocking context re-injection; reads critical-core + state. |
| `quality-gates/source-audit.py` | 351 | Med | Standalone source classifier/deleter (shared with v1). |
| `quality-gates/persona-guard.py` | 103 | Low | PreToolUse guard against persona wipe (shared with v1). |

### Zone Totals
| Zone | Files | LoC Total |
|------|-------|-----------|
| observability (`observer/`) | 4 | 824 |
| quality-gates | 2 | 454 |
| **Grand Total** | **6** | **1278** |

### Architecture Notes
- No internal import edges: each script is a self-contained CLI or hook. Coupling is via **shared JSON state** (witness-state files, `gotchas.json`, `critical-core.json`), not Python imports.
- All scripts are stdlib-only and fail-open. Configuration is via environment variables (see `observer/README.md`).

*Full index: `_design/code-index.json`*
