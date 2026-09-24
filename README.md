<div align="center">

<img src="assets/hero.png" alt="Research Agent 2" />

# Research Agent 2 — Observer Model

An experimental fork of [research-agent](https://github.com/Stap0689/research-agent) that makes methodology adherence *provable*, not honor-system.

</div>

## The Problem

A research skill can define a rigorous methodology and the agent can still skip
half of it. The methodology is read at turn 1 and faint by turn 40. Source audits
get waved through. A conclusion rides one source. The session declares itself done
because it hit a round count, not because the topic was saturated. The output
looks exhaustive and cites sources, so nobody notices the corners that were cut.

Documentation alone does not prevent this. Research Agent 2 adds an enforcement
layer that does.

## What This Adds Over v1

Research Agent 2 carries the **entire** [research-agent](https://github.com/Stap0689/research-agent)
methodology — the same 7-phase workflow, source-quality gates, bias
countermeasures, and completion criteria — and wraps it in an in-session
**witness / accountability loop**:

1. **A non-negotiable core.** A single `critical-core.json` defines the ~17 disciplines that, when skipped, silently compromise a corpus. It is the single source of truth, consumed three ways: inlined in the skill, re-injected after every question, and used as the witness rubric.
2. **A methodology-read gate.** Q&A is mechanically blocked until the session confirms it read the *full* methodology, not the summary stub. This closes the "proceed on the thin stub" failure.
3. **An independent witness subagent.** At every phase boundary (and at least every 8 questions), a *fresh, adversarial* agent audits the actual notebook state against the core. It doesn't just check that steps ran — it probes the corpus for the phase's full territory and measures coverage, so a phase can't be exited on floor depth.
4. **A termination hard-wall.** The findings deliverable cannot be written until an adversarial completeness critic certifies saturation — spec-coverage of every deliverable part, zero un-triangulated linchpins, and a conclusion-dependency attack. The *final* certifying pass must be a brand-new critic with zero session context, because the actor shares its own blind spots.
5. **A self-improving gotchas ledger.** Every deviation caught and fixed is recorded, ranked by recurrence, and surfaced at the top of the next session so the methodology learns from its own failures.

**The bar is mastery, not a minimum.** There is no target question count. Minimums
are floors, never goals. The only accepted end-state is demonstrated, adversarially
certified saturation of the corpus.

## How Enforcement Works

Three Claude Code hooks make the loop mechanical rather than advisory:

| Hook | Fires on | Blocks until |
|------|----------|-------------|
| `witness-gate.py` (PreToolUse) | `notebooklm ask` | Methodology confirmed read, last verdict not FAIL, ask cadence within limit |
| `witness-reinject.py` (PostToolUse) | after `notebooklm ask` | (non-blocking) re-injects the core + cadence into context |
| `completeness-gate.py` (PreToolUse) | Write/Edit of a `/findings/*.md` | Completeness certified CLEAN |

Every hook is a **strict no-op** unless the target notebook is an active observer
session, and every hook **fails open**. The stable v1 skill never creates observer
state, so it is completely unaffected — v1 remains the production fallback.

## Repository Layout

```
research-agent2/          The observer skill (install to ~/.claude/skills/research-agent2/)
  SKILL.md                Thin stub: the non-negotiable core + run order (progressive disclosure)
  OBSERVER-PROTOCOL.md    The witness loop: checkpoint → witness subagent → verdict → remediate
  critical-core.json      The enforced rule spine (single source of truth)
  methodology/            The full research-agent methodology (identical to v1)
    SKILL.md              7-phase workflow, source audit, autonomy rules, hard gates
    SOURCE-QUALITY.md · QUESTION-FRAMEWORKS.md · BIAS-PREVENTION.md
    COMPLETION-AND-DELIVERABLES.md · NOTEBOOKLM-INTEGRATION.md

notebooklm/               The corpus skill (install to ~/.claude/skills/notebooklm/)
  SKILL.md                Full NotebookLM CLI reference

observer/                 The accountability runtime
  witness.py              State hub (scope, checkpoints, verdicts, completeness, gotchas)
  hooks/                  witness-gate.py · witness-reinject.py · completeness-gate.py
  README.md               Install + hook wiring + env configuration

quality-gates/            Source-quality enforcement (shared with v1)
  source-audit.py         Classify + auto-delete hard-reject sources
  persona-guard.py        Prevent silent custom-persona wipe
```

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (the witness subagent uses the Agent/Task tool; the gates use hooks)
- [notebooklm-py](https://github.com/teng-lin/notebooklm-py) **0.8.1+**: `pip install notebooklm-py` (NotebookLM is now [Gemini Notebook](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/); 0.8.1+ points at the current `notebook.google.com` host)
- NotebookLM authenticated: `notebooklm login`
- Python 3.10+

## Install

```bash
export RESEARCH_AGENT_HOME=~/research-agent

# Skills
cp -r research-agent2/ ~/.claude/skills/research-agent2/
cp -r notebooklm/     ~/.claude/skills/notebooklm/

# Observer runtime
mkdir -p "$RESEARCH_AGENT_HOME/observer/hooks" "$RESEARCH_AGENT_HOME/observability" "$RESEARCH_AGENT_HOME/findings"
cp observer/witness.py       "$RESEARCH_AGENT_HOME/observer/"
cp observer/hooks/*.py       "$RESEARCH_AGENT_HOME/observer/hooks/"
chmod +x "$RESEARCH_AGENT_HOME/observer/hooks/"*.py "$RESEARCH_AGENT_HOME/observer/witness.py"
```

Then wire the three hooks into `~/.claude/settings.json` — see [observer/README.md](observer/README.md) for the exact block and environment configuration.

## Usage

Activate the skill on a research-intent prompt, then follow the mechanically gated
run order (Research Agent 2 will not let you skip a step):

```
Research the current state of retrieval-augmented generation architectures — use the observer model, accuracy is critical.
```

Under the hood the session runs `witness.py init`, reads and confirms the full
methodology (unlocking the Q&A gate), then drives the 7 phases with a witness
checkpoint at every boundary. Before the findings document can be written, an
adversarial completeness critic must certify saturation. The final deliverable
carries an **Accountability Record** — the trust signal that the protocol was
followed.

## Operational Notes (First Run)

A few behaviors are worth knowing before your first session. None are defects in the
skill; they are properties of the runtime it sits on.

- **Do not interrupt while a witness or completeness critic is running.** The witness
  and completeness critics are Claude Code subagents spawned via the Agent/Task tool.
  Interrupting the parent turn tears down the in-flight subagent, so it returns no
  verdict. Let each pass finish (you are notified on completion), then continue.
- **Gemini Notebook cites factual-lookup questions well and analytical ones poorly.**
  Falsification, premortem, and synthesis questions often return with no citation
  markers. Do not treat an uncited analytical answer as grounded. Verify its
  load-bearing claims against the corpus with `notebooklm source search "<claim>"`
  before relying on them. A claim that surfaces in no source is inference, not a finding.
- **Triangulate on the specific claim, not keyword overlap.** `source search`
  co-occurrence is not corroboration. Read the snippet: a co-citing source may support
  an adjacent general principle while the specific load-bearing claim is still
  single-source. Confidence-cap single-source claims accordingly.
- **A second deep-research pass in the same notebook needs `--task-id`.** If a prior
  `source add-research` task is still in flight when you start another, `research wait`
  becomes ambiguous ("N research tasks in flight"). Pass the specific `--task-id` /
  `--run-id` reported by `source add-research` to import the one you want.
- **The source audit reports tiers; it does not block.** `quality-gates/source-audit.py`
  classifies each source (hard-reject, Tier 5, or a positive Tier 1-3 via `DOMAIN_TIER_MAP`)
  and prints an effective Tier 1-3 count against the 15-source minimum in `SOURCE-QUALITY.md`.
  If a legitimate authoritative domain (a standards body, a peer-reviewed venue, a
  government or framework source) shows up as `unclassified`, add it to `DOMAIN_TIER_MAP`.
  The count is advisory; nothing here blocks Q&A.

## When to Use This vs. v1

Use **research-agent2** when the research is decision-informing, adversarial, or
high-stakes and adherence must be provable. Use the stable
**[research-agent](https://github.com/Stap0689/research-agent)** for everyday
research where the overhead of the witness loop is not warranted. v1 is the
production fallback and is never affected by this fork.

## License

MIT
