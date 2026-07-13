# Observer Protocol (research-agent2)

The in-session accountability loop. The live session (the **actor**) drives the
research exactly as in v1. On top of that, it runs a witness loop: it checkpoints
its own state at phase boundaries, spawns an **independent witness subagent** to
audit that state against the critical core, and cannot continue Q&A until the
witness signs off. Deviations that are caught and fixed become **gotchas** that
seed every future session.

Enforcement is mechanical, not honor-system: `witness-gate.py` (PreToolUse) blocks
`notebooklm ask` until the methodology is confirmed read, the last verdict is not
FAIL, and the ask cadence has not exceeded the witness interval.

Path shorthand used below:
- `witness.py` = `$RESEARCH_AGENT_HOME/observer/witness.py` (default `~/research-agent/observer/witness.py`).
- `critical-core.json` — after a standard install lives at
  `~/.claude/skills/research-agent2/critical-core.json`; the witness/critic
  subagents read it from there (override with `WITNESS_CRITICAL_CORE`).

---

## Step 0 — Initialize observer state (before touching NotebookLM)

```bash
python3 witness.py init --notebook <ID> --question "<one-sentence central question>" --mode <output-mode>
```
This enables observer mode and prints the **top recurring gotchas**. Read them.
They are the specific ways prior sessions failed. Do not repeat them.

## Step 1 — Read the full methodology, then confirm it

Read `methodology/SKILL.md` and the appendices it references. Then:
```bash
python3 witness.py loaded --notebook <ID>
```
Until this is recorded, `witness-gate.py` blocks ALL Q&A. This is the fix for the
thin-stub skip: you cannot proceed on the summary.

## Steps 2-N — Research the phases (0-7) per methodology/SKILL.md

Drive Phases 0-7 normally. The witness loop overlays two triggers:

**Trigger A — phase boundary.** When you complete a phase (3A→3B, 3B→3C, etc.),
before entering the next:
1. Write a checkpoint:
   ```bash
   python3 witness.py checkpoint --notebook <ID> --phase <P> \
     --data '{"sources":N,"tier_1_3":N,"questions_asked":N,"checks_run":["falsification","ach"],"deviations_noticed":"..."}'
   ```
2. Spawn the witness subagent (below). Record its verdict.

**Trigger B — cadence.** If you hit `max_asks_without_witness` (default 8) Q&A
questions within a phase, the gate blocks further asks until you checkpoint and
witness. This catches long unwitnessed stretches. **The cadence checkpoint is NOT
a saturation signal.** Pausing because you hit 8 questions does not mean the phase
is done. Never conflate a protocol checkpoint with mastery.

**Fan-out and linchpins (during every phase, not deferred):**
- Fan out from every answer. A response that surfaces a thin-spot, a new entity,
  an unexplored sub-topic, or a single-source linchpin MUST spawn follow-up
  questions. Running a pre-scripted list instead of chasing what answers reveal is
  a logged deviation.
- Triangulate load-bearing single-source findings DURING Phase 3. If a conclusion
  or a taxonomy cell rests on one source, either find corroboration now or
  explicitly cap its confidence now. Deferring it to a Phase-5 flag is a deviation.

**There is no minimum.** The DA-minimum tier, the 5-round ladder, and the
phase-transition criteria are floors, never targets. Do not converge early to hit
a deadline or a check-in. A user saying "let's talk when you're done with X" is
pause-and-report, not permission to wrap up. The only end-state is demonstrated
mastery, certified adversarially (below).

## The witness subagent — spawn via the Agent tool (Task)

The witness must be a **fresh, independent** agent (its independence is the entire
point — a self-check shares the actor's blind spots). Use a read-capable agent
(e.g. Explore or general-purpose). Hand it this prompt, filling the placeholders:

```
You are an adversarial research-methodology WITNESS. You did not conduct this
research and you have no stake in it. Your job is to find where the session
deviated from its required methodology. Assume there IS a deviation and hunt for
it. Do not be charitable.

Inputs:
- Critical core (the non-negotiable rules): read ~/.claude/skills/research-agent2/critical-core.json
- Notebook under audit: <ID>
- Phase just completed: <P>
- The actor's self-reported checkpoint: <paste the --data JSON>
- The evidence trail: run `notebooklm note list --notebook <ID>` and read the
  saved Q&A notes. Read the actual notebook state; do not trust the checkpoint
  alone (a checkpoint can omit the actor's own misses).

For EVERY rule in critical-core.json whose phase applies to phase <P> or earlier,
render a verdict: PASS / FAIL / NOT-YET-DUE. For each FAIL, quote the specific
evidence (or the specific absence of evidence) that proves the deviation. A rule
whose `verify` condition you cannot confirm from the actual notebook state is a
FAIL, not a pass-by-default.

Pay special attention to blocker-severity rules: persona-set, corpus-gate,
falsification, no-single-source-anchor, no-fabrication, methodology-loaded.

UNDER-EXPLORATION / TERRITORY-COVERAGE AUDIT (do this every phase — it is why the
witness exists, not just compliance). Compliance ("did they do the step") is not
depth. A phase that ran a handful of questions and moved on can pass every rule
and still be shallow. You do NOT need prior domain knowledge to catch this — ask
the CORPUS how big the territory is, then measure coverage:
1. From the phase's central question, probe the corpus for its FULL territory:
   `notebooklm ask "Exhaustively list every distinct mechanism, approach,
   competing method, failure mode, and sub-topic in these sources relevant to
   <the phase's question>. Group them; do not summarize." --notebook <ID>`
2. Compare that territory to what the actor actually asked (the saved notes).
   Count: distinct high-value threads the corpus supports vs. threads the actor
   explored. If the actor sampled (e.g., explored a handful while the corpus
   supports many more distinct load-bearing threads), that is UNDER-EXPLORATION.
3. List the specific high-value threads the actor left untouched, and whether the
   corpus can answer them (if yes → they are misses, not boundaries).
Under-exploration is a **major** fail: the phase may not be exited on floor depth.
"It hit the phase minimum" is never a reason to pass — minimums are floors.

Return ONLY this JSON:
{
  "result": "PASS" | "FAIL",
  "severity": "none" | "minor" | "major" | "blocker",
  "per_rule": [{"id":"...","verdict":"PASS|FAIL|NOT-YET-DUE","evidence":"..."}],
  "territory_coverage": {"corpus_threads": <n>, "explored": <n>, "untouched_high_value": ["..."]},
  "under_explored": true | false,
  "deviations": "<one paragraph: what failed and why it matters, or 'none'>",
  "required_remediation": "<what the actor must do before proceeding, or 'none'>"
}
result is PASS only if zero blocker/major rules FAIL AND under_explored is false.

```

## Record the verdict

```bash
python3 witness.py verdict --notebook <ID> --phase <P> --result <PASS|FAIL> \
  --severity <sev> --deviations "<summary>"
```
- **Under-exploration is handled differently from a deviation FAIL.** If the
  witness returns `under_explored: true`, do NOT record a `--result FAIL` — that
  blocks Q&A, and remediating under-exploration *requires* more Q&A (a deadlock).
  Instead: the phase is simply **not exitable yet**. Keep asking — fan out into the
  witness's `untouched_high_value` threads — then re-run the phase witness. Only
  record the phase's `--result PASS` once a fresh witness returns
  `under_explored: false`. Under-exploration reopens by *continuing*, not by
  blocking. (The terminal completeness certification also requires every phase's
  final witness to show `under_explored: false`.)
- **PASS** resets the ask counter and unlocks Q&A. Proceed.
- **FAIL** (a real deviation: fabrication, skipped step, contradiction) keeps Q&A
  blocked. Remediate the deviation (re-run the missed step),
  then record the fix as a gotcha and record a corrected PASS verdict:
  ```bash
  python3 witness.py gotcha-add --text "<what went wrong and the fix>" --rule <rule-id>
  python3 witness.py verdict --notebook <ID> --phase <P> --result PASS --severity none
  ```

## Escalation

If the witness and actor disagree twice on the same phase, or a blocker deviation
cannot be remediated from the corpus, STOP and surface it to the user. Do not
self-certify past an unresolved blocker.

## Termination — the hybrid completeness critic (mandatory, hard-gated)

You may not write the findings deliverable until an adversarial completeness
critic certifies saturation. This is the termination hard-wall: `completeness-gate.py`
blocks the write of any `**/findings/**.md` for an active observer session until
`witness.py completeness --result CLEAN` has been recorded. There is no minimum
question count; the bar is mastery, not a checkpoint.

The completeness pass is **hybrid** — two parts, because the test showed a pure
cold critic under-surfaces deep veins while the actor alone rationalizes "done":

**Part 1 — cold-subagent spec-coverage audit (independent).** Spawn a fresh agent
whose only job is to read the record and the deliverable spec and find what is
missing. Prompt:

```
You are an adversarial COMPLETENESS critic. You did not run this research.
Assume the session stopped too early and find where.

Inputs:
- Central question / deliverable spec: <paste it verbatim>
- Critical core: read ~/.claude/skills/research-agent2/critical-core.json (see the
  saturation_bar: distinct axis / multi-source / taxonomy- or conclusion-changing)
- Notebook: <ID>. Read the saved notes: `notebooklm note list` then `note get`.

Do FOUR things:
1. SPEC-COVERAGE: decompose the central question into its required parts. For each
   part, state SATURATED or THIN with evidence from the notes. A compound question
   half-answered while looking exhaustive is the failure you are hunting.
2. OPEN LEADS: list every single-source load-bearing claim not triangulated, every
   corpus-flagged gap not chased, every cross-answer contradiction unresolved, and
   every surfaced-but-unfollowed thin-spot.
3. CONCLUSION-DEPENDENCY ATTACK (do this hardest): state the session's surviving
   conclusion, then list what it LEANS ON — every fallback, backstop, mitigating
   assumption, or "survives only in bounded form because X" escape hatch. For each
   dependency, ask whether the corpus actually supports it, and probe the corpus to
   find out. Then scan for ONE-DIRECTIONAL EVIDENCE USE: did the session cite a
   source to support one point while ignoring that the same source undercuts its own
   conclusion? A conclusion whose backstop was never interrogated is not saturated.
4. HIGH-VALUE UNASKED QUESTIONS: list the questions that, if asked, would clear the
   saturation_bar (distinct axis / multi-source / taxonomy- or conclusion-changing).
   Ignore questions that would not clear the bar.

Return ONLY JSON:
{ "spec_parts":[{"part":"...","status":"SATURATED|THIN","evidence":"..."}],
  "open_leads":["..."],
  "conclusion_dependencies":[{"dependency":"...","corpus_supports":"yes|no|contradicts","evidence":"..."}],
  "one_directional_evidence":["..."],
  "bar_clearing_questions":["..."],
  "verdict":"CLEAN|OPEN" }
verdict is CLEAN only if every spec part is SATURATED, open_leads is empty, no
conclusion dependency is contradicted by the corpus, no one-directional evidence use
remains, and bar_clearing_questions is empty.
```

**The FINAL certifying pass is non-negotiably a FRESH INDEPENDENT critic.** The
actor and the in-loop critic share the session's blind spots and will declare CLEAN
too early (this is a documented failure: a self-certified run left a
conclusion-changing contradiction unchased; a fresh critic caught it in one pass).
So: the actor's own passes may run during research, but the LAST completeness pass
before certification must be spawned as a brand-new subagent with zero session
context, running this exact prompt. Only its CLEAN verdict may back
`witness.py completeness --result CLEAN`.

**Part 2 — actor deep vein critique (contextual).** With your full accumulated
context, generate the highest-value veins the cold critic could not see, held to
the same bar. Merge with the cold critic's output.

**If either part returns OPEN:** record it, chase every bar-clearing lead (which
will fan out into more questions), and re-run the completeness pass. Repeat until
both parts are CLEAN. This may take several passes — in the validation run it took
seven. That is correct behavior, not a problem.

**When both are CLEAN**, record it (this unlocks the deliverable write):
```bash
python3 witness.py completeness \
  --notebook <ID> --result CLEAN --parts "<deliverable parts confirmed saturated>"
```
If it is not clean, record `--result OPEN --veins "..."` and keep working.

## Final witness + accountability report

After completeness is certified, run one final compliance witness pass over the
whole session (phase = "final"). Then append an **Accountability Record** to the
findings document:

```markdown
## Accountability Record
**Witness verdicts:** <N> compliance passes (PASS: <n>, FAIL-then-corrected: <n>)
**Completeness-critic passes:** <N> (<n> found open veins that were then closed; final pass CLEAN)
**Deviations caught and corrected:** <list, or "none">
**Blocker rules — final status:** methodology-loaded ✅ · scope-recorded ✅ · persona-set ✅ · corpus-gate ✅ · linchpin-triangulation ✅ · falsification ✅ · no-single-source-anchor ✅ · spec-coverage ✅ · exhaustion ✅ · no-fabrication ✅
**Protocol-adherence confidence:** High / Moderate / Low — <one-sentence basis>
**Saturation basis:** <what the final completeness pass certified — every deliverable part saturated, zero bar-clearing veins>
**Gotchas logged this session:** <list>
```

This record is the trust signal. A finding without a clean final witness pass does
not ship to a decision-maker without explicit human review.
