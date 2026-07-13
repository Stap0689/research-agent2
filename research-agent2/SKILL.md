---
name: research-agent2
description: EXPERIMENTAL observer-model fork of research-agent. The full 7-phase NotebookLM research methodology PLUS an in-session witness/accountability loop that checkpoints the session, has an independent witness subagent audit it against a non-negotiable core, and mechanically blocks Q&A until the session followed protocol. Use when research accuracy is critical and must be provably followed. The stable research-agent skill remains the production fallback.
---

# Research Agent 2 — Observer Model

⚠️ **Experimental fork.** Self-contained copy of the research-agent methodology
plus an accountability layer. The stable `research-agent` skill is untouched and
remains the production fallback.

This stub is thin on depth (progressive disclosure) but **complete on the rules
that must never be skipped**. Do not treat the summary below as a substitute for
reading the full methodology — the witness-gate mechanically blocks Q&A until you
confirm you read it.

**Paths in this skill use `$RESEARCH_AGENT_HOME`** (default `~/research-agent`) as
the research workspace, and `witness.py` as shorthand for
`$RESEARCH_AGENT_HOME/observer/witness.py`. Set `RESEARCH_AGENT_HOME` to relocate
the workspace. See `../observer/README.md` for install and hook wiring.

---

## ⛔ THE NON-NEGOTIABLE CORE (source: `critical-core.json`)

These are the disciplines that, when skipped, silently compromise the corpus.
They are enforced three ways: stated here, re-injected after every Q&A by
`witness-reinject.py`, and audited by the witness subagent. **blocker** = research
is invalid if violated.

1. **methodology-loaded** (blocker) — Read the full `methodology/SKILL.md` + appendices this session. The stub is not a substitute.
2. **scope-recorded** (blocker) — One-sentence central question + output mode recorded before any NotebookLM work.
3. **persona-set** (blocker) — Configure the research-corpus-analyst persona before any Q&A. Never run `configure` without `--persona`.
4. **corpus-gate** (blocker) — Audit ran, hard-rejects deleted, ≥15 RECOGNIZED Tier 1-3 sources before Q&A. Unknown-domain and subject-doc sources do not count.
5. **no-context-in-exploration** (major) — Phase 3A questions carry no application/architecture framing.
6. **bidirectional-eval** (major) — After every response, run the 5 checks before the next question.
7. **save-every-note** (major) — Every Q&A saved with `--save-as-note`.
8. **falsification** (blocker) — Apply Alexander's Question to the central claim; name what would disprove it and confirm that evidence is absent.
9. **competing-hypotheses** (major) — Test alternatives (ACH / devil's advocate) before committing to the lead conclusion.
10. **no-single-source-anchor** (blocker) — No conclusion anchored to one source; triangulate every major claim.
11. **gaps-surfaced** (major) — Honest intelligence-gaps section in the findings.
12. **no-fabrication** (blocker) — Every factual claim traces to a corpus source; findings vs inference labeled; nothing from general knowledge.
13. **linchpin-triangulation** (blocker) — Load-bearing single-source findings are triangulated or confidence-capped DURING Phase 3, never deferred to a phase-5 flag.
14. **fan-out** (major) — Every answer's thin-spots/new entities/linchpins spawn follow-ups. A surfaced-but-unfollowed lead is a deviation. No pre-scripted lists.
14b. **phase-exit-depth** (major) — A phase may not be exited on floor depth. The per-phase witness territory-maps the phase from the corpus and measures coverage; sampling a few threads while the corpus supports many more reopens the phase. Compliance is not depth; a minimum is never a reason to advance.
15. **spec-coverage** (blocker) — Decompose the deliverable into its parts; saturate EACH. A compound question half-answered still looks exhaustive — that is the trap.
16. **exhaustion** (blocker) — Termination requires an adversarial completeness critic to certify saturation (zero veins clearing the bar: distinct axis / multi-source / taxonomy-changing). The FINAL certifying pass must be a FRESH INDEPENDENT critic, not the actor's self-view. Certified via `witness.py completeness --result CLEAN`; the deliverable write is hard-blocked until then.
17. **conclusion-dependencies** (blocker) — Before certifying, adversarially attack the surviving conclusion's OWN load-bearing dependencies (any fallback/backstop/"survives only in bounded form because X" escape hatch). Test every steelman/evidence citation in BOTH directions; one-directional evidence use is a deviation. A conclusion whose backstop was never interrogated is not saturated.

## ⛔ NO MINIMUM — THE BAR IS MASTERY

There is no minimum question count and no target. The DA-minimum tier, the 5-round
ladder, and the phase-transition criteria are **floors, never goals**. This skill's
purpose is to make you a subject-matter expert on the nominated topic — a brain
extension, not a frozen generalist. The only acceptable end-state is 100% mastery of
the corpus: able to reconstruct the field, challenge it, and locate its edges.
Whatever it takes to get there is the method. Converging early to hit a soft deadline
is a failure. A user check-in ("let's talk when you're done with X") is
pause-and-report, NOT permission to wrap up. Termination is a mastery condition
certified adversarially, never a self-declared floor-hit.

---

## Run order (mechanically gated)

**Step 0 — initialize observer + read the gotchas seed:**
```bash
python3 "$RESEARCH_AGENT_HOME/observer/witness.py" init \
  --notebook <ID> --question "<central question>" --mode <output-mode>
```

**Step 1 — read the full methodology, then confirm:**
Read `methodology/SKILL.md` and the appendices below. Then:
```bash
python3 "$RESEARCH_AGENT_HOME/observer/witness.py" loaded --notebook <ID>
```
Until this is recorded, all `notebooklm ask` calls are DENIED.

**Steps 2-N — run Phases 0-7 with the witness loop.**
Follow **`OBSERVER-PROTOCOL.md`** in this directory: checkpoint at every phase
boundary (and at least every 8 questions), spawn the independent witness subagent,
record its verdict. A FAIL blocks Q&A until remediated. Fan out from every answer;
triangulate load-bearing single-source findings in-phase.

**Before the deliverable — the termination hard-wall.** Run the hybrid completeness
critic (cold-subagent spec-coverage audit + actor deep vein critique). Chase every
open vein it finds; re-run until CLEAN. Then:
```bash
python3 "$RESEARCH_AGENT_HOME/observer/witness.py" completeness \
  --notebook <ID> --result CLEAN --parts "<parts saturated>"
```
`completeness-gate.py` DENIES writing the findings doc until this is recorded.
Finish with a final witness pass and an Accountability Record appended to the doc.

---

## Methodology (read in this order)

### FIRST — the authoritative SKILL (non-negotiable)
- **`methodology/SKILL.md`** — the 7-phase flow, Phase 0 scope, autonomy rules, hard gates.

### THEN — the appendices
- `methodology/SOURCE-QUALITY.md`
- `methodology/QUESTION-FRAMEWORKS.md`
- `methodology/BIAS-PREVENTION.md`
- `methodology/COMPLETION-AND-DELIVERABLES.md`
- `methodology/NOTEBOOKLM-INTEGRATION.md`

### Observer layer
- `OBSERVER-PROTOCOL.md` — the witness loop (checkpoint → witness subagent → verdict → remediate → gotchas).
- `critical-core.json` — the enforced rule spine.

---

## Workspace, notebook index, output paths

All under `$RESEARCH_AGENT_HOME` (default `~/research-agent`):

- Findings: `$RESEARCH_AGENT_HOME/findings/<slug>-YYYY-MM-DD.md`
  (the path must contain a `/findings/` segment — that is what `completeness-gate.py` guards).
- Notebook index: `$RESEARCH_AGENT_HOME/observability/notebook-index.json`
- Witness state: `$RESEARCH_AGENT_HOME/observability/witness-state/<ID>.json`
- Gotchas ledger: `$RESEARCH_AGENT_HOME/observability/gotchas.json`

## Requires
- `notebooklm` skill active and authenticated (`notebooklm auth check`)
- The observer runtime installed and its hooks wired (see `../observer/README.md`)
- Effort policy: run at the highest reasoning effort available. The observer loop
  is deliberately expensive; it exists for research where correctness dominates cost.
