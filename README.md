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
- [notebooklm-py](https://github.com/teng-lin/notebooklm-py): `pip install notebooklm-py`
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

## When to Use This vs. v1

Use **research-agent2** when the research is decision-informing, adversarial, or
high-stakes and adherence must be provable. Use the stable
**[research-agent](https://github.com/Stap0689/research-agent)** for everyday
research where the overhead of the witness loop is not warranted. v1 is the
production fallback and is never affected by this fork.

## License

MIT
