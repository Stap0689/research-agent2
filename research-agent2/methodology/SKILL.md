---
name: research-agent
description: Professional research orchestrator that governs how Claude conducts deep research using NotebookLM. Enforces source quality standards, question depth and rigor, bias prevention, cross-validation, thin spot identification, and structured deliverables. Use when conducting any serious research task — deep dive, investigate, find sources, gather evidence, synthesize research, evaluate a claim, literature review, comprehensive analysis, research methodology. Works on top of the notebooklm skill. Requires NotebookLM authenticated.
---

# Research Agent

Governs the methodology, rigor, and output of autonomous AI research. All frameworks encoded here are derived from a systematic research corpus spanning intelligence community analytic standards (ICD 203, Richards Heuer SATs), PRISMA systematic review methodology, Popper falsifiability, Tetlock superforecasting, and ACRL/SIFT information literacy.

**Requires:** `notebooklm` skill active and authenticated (`notebooklm auth check`)

---

## Output Scope

The research-agent produces two outputs: Q&A notes saved to the notebook and a Research Findings Document on disk (format determined by output mode — see Phase 0). Nothing else unless explicitly requested by the user.

**Never generate unprompted:** audio overviews, podcasts, videos, reports, study guides, quizzes, flashcards, infographics, or slide decks. NotebookLM is the research corpus and Q&A engine. Its artifact generation features are out of scope for this skill.

---

## Deep Research Ceiling — Detection and Escalation

NotebookLM deep research (`--mode deep`) is subscription-tier limited. When the ceiling is hit, **stop and escalate to the user. Do not auto-proceed.**

### Ceiling Detection
A deep research ceiling has likely been hit when any of the following occur:
- `source add-research` returns an error containing "quota", "limit", "subscription", or "upgrade"
- `research wait` returns an error or zero imported sources despite a successful start
- Research status shows `FAILED` or equivalent after the wait

Also flag if fast research is returning implausibly large source counts (40+ from a single query) — this signals the query was too broad and quality will be low regardless of mode.

### Escalation — Stop and Report (Do Not Auto-Proceed)
When the ceiling is hit, stop the research workflow immediately and report:
```
DEEP RESEARCH CEILING HIT
Topic: [topic name]
Notebook: [notebook ID]
Sources loaded so far: [count and tier distribution from source list]
Failed query: "[the query that failed]"

Options to continue:
A) Fast research — run remaining queries with --mode fast (no --mode flag needed, it's the default).
   Warning: fast research can return 40+ sources per query. Expect 70-80% deletion after filtering.
   Tier 1-2 sources only for primary evidence. Tier 3 for context only.
B) Manual URL seeding — user provides specific URLs to add directly with `source add "<url>"`.
   Highest quality control. User pre-vets each source before it enters the notebook.
C) Document upload — user provides local files (PDFs, markdown) to upload.
   Best quality. User controls exactly what enters the corpus.
D) Wait and retry — deep research quota may reset. Timing depends on subscription tier.

Current corpus: [tier distribution] — [sufficient/insufficient] to proceed to Q&A without more sources.

Awaiting your decision before proceeding.
```

**Do not guess which path to take. Do not proceed without explicit user direction.**

### Fast Research — Stricter Filtering Rules
If the user chooses Option A (fast research), apply these stricter standards:

**Accept for primary evidence (Q&A anchor):** Tier 1 and Tier 2 only.
**Accept for context only (not Q&A anchor):** Tier 3 — flag each one explicitly.
**Reject everything else:** Tier 4 and Tier 5 are excluded with no exceptions on fast research returns.

Fast research sweeps broadly. Expect a high deletion rate — 60-80% of what it returns will not qualify. This is normal and expected. A smaller, cleaner corpus is better than a large polluted one.

Run the source audit question after every fast research import, same as deep research. The audit question becomes even more important here because the signal-to-noise ratio is lower.

Minimum corpus before Q&A still applies: **15 Tier 1–2 sources** (not Tier 1–3) when using fast research as the primary collection method.

### Manual URL / Document Seeding
If the user provides specific URLs or files:
- Add them with `notebooklm source add "<url>" --notebook <ID>` or `notebooklm source add ./file.pdf --notebook <ID>`
- These are pre-vetted by the user — still run the audit to confirm tier, but default to accepting unless the source is unambiguously low quality
- Document the source additions in the Research Findings Document under Anchoring Sources

---

## Multi-Topic Source Ceiling Management

NotebookLM enforces a per-notebook source limit (typically 100 sources). When a research task covers multiple distinct sub-topics (A, B, C), hitting the ceiling before all topics are covered produces **structurally incomplete analysis** — the synthesis will anchor on whatever topics got sources and treat the rest as gaps. This is a research failure even if the output looks confident.

### Active Ceiling Monitoring
After every import cycle, check current source count:
```bash
notebooklm source list --json --notebook <ID>  # count total
```
Maintain a running tally: **[sources used] / 100** and track which topics are covered.

**At 75+ sources loaded:** stop before the next research query and assess topic coverage.

### Coverage Assessment — Required at 75 Sources
Before adding more sources when at 75+, ask:
```bash
notebooklm ask "Based on the sources currently in this notebook, which of the following research sub-topics have adequate coverage (at least 5 Tier 1-3 sources each), and which are thin or uncovered: [list your sub-topics]. For each thin or uncovered topic, what specific source types are missing?" --save-as-note --notebook <ID>
```

If all sub-topics have adequate coverage, proceed normally.
If any sub-topic is thin or uncovered, execute the remediation sequence below.

### Remediation Sequence — Dedup First, Split Second

**Step 1 — Deduplication and redundancy pruning:**
```bash
notebooklm ask "Are there redundant sources in this notebook — multiple sources covering the same paper, the same study, or nearly identical content? List any duplicates or near-duplicates by source ID and explain the overlap." --save-as-note --notebook <ID>
```
Delete exact duplicates. Delete any Tier 4-5 sources that slipped through prior pruning.
Recount: **[new total] / 100**.

**Step 2 — Assess remaining headroom:**
If deduplication freed enough space (headroom ≥ 15 sources per uncovered topic), proceed with targeted research queries for the uncovered topics.

**Step 3 — Notebook split if headroom is still insufficient:**
If deduplication is not enough to cover the remaining topics at quality threshold, **stop and escalate**:

```
SOURCE CEILING — NOTEBOOK SPLIT REQUIRED
Notebook: [ID]
Current sources: [N] / 100
Topics with adequate coverage: [list]
Topics still needing research: [list]
Sources freed by deduplication: [N]
Headroom after dedup: [N] — insufficient for remaining topics

Proposed action: Create a new notebook for [uncovered topics].
Relevant sources from this notebook that overlap will be re-added to the new notebook.

Awaiting your decision to proceed with notebook split.
```

**Do not proceed with a split without user confirmation.**

### Cross-Notebook Synthesis
If topics end up in separate notebooks, the synthesis phase must integrate findings across all notebooks before writing the Research Findings Document. Run the synthesis question in each notebook, then produce a unified Research Findings Document that explicitly states which sources and notebooks anchored which parts of the conclusion.

The Research Findings Document must note: "Source corpus split across [N] notebooks due to ceiling — see notebook IDs [list]."

### Multi-Topic Source Juggling — Single Notebook, Multiple Focus Areas

When a research task has multiple sub-topics that share some sources but not all, use topic-scoped questions and pre-Q&A source pruning to focus queries per topic within a single notebook. This avoids notebook splits when topics share significant source overlap.

**Step 1 — Topic tagging during source audit:**
Extend the standard source audit question to also assign each source to one or more topic tags:
```bash
notebooklm ask "Audit every source in this notebook. For each source list: (1) source ID, (2) title, (3) Tier 1-5 rating, (4) which of these research sub-topics it is relevant to: [TOPIC_A], [TOPIC_B], [TOPIC_C]. A source can belong to multiple topics. Output a grouped list: for each topic, list the source IDs that belong to it." --save-as-note --notebook <ID>
```

**Step 2 — Delete off-topic and low-quality sources:**
After the audit, delete all Tier 5 and hard-reject sources from the notebook. This is the primary filtering mechanism since bad sources cannot be excluded at query time.
```bash
# Delete every Tier 5, social media, Reddit, YouTube, vendor marketing source
notebooklm source delete <bad_id_1> --yes --notebook <ID>
notebooklm source delete <bad_id_2> --yes --notebook <ID>
```

**Step 3 — Scoped Q&A per topic:**
Scope each topic's Q&A phase through question specificity. NotebookLM's retrieval focuses on relevant sources when the question is precise:
```bash
# Topic A questions — question text drives retrieval focus
notebooklm ask "Focusing specifically on [TOPIC_A]: Q1 about topic A" --notebook <ID>
notebooklm ask "Focusing specifically on [TOPIC_A]: Q2 about topic A" --notebook <ID>

# Topic B questions — same notebook, different retrieval focus
notebooklm ask "Focusing specifically on [TOPIC_B]: Q1 about topic B" --notebook <ID>

# Cross-topic questions — no scoping, full corpus
notebooklm ask "How do topics A and B relate?" --notebook <ID>
```

**Step 4 — Cross-topic synthesis:**
After completing per-topic Q&A, run synthesis questions against the full corpus to find connections:
```bash
notebooklm ask "Synthesize findings across [TOPIC_A], [TOPIC_B], and [TOPIC_C]. What patterns, contradictions, or gaps emerge when comparing across these sub-topics?" --save-as-note --notebook <ID>
```

**When to use juggling vs. notebook split:**
- **Juggle** when total sources fit in one notebook (< 100) and topics share > 30% of sources
- **Split** when sources exceed the 100 ceiling or topics are completely independent with no shared sources
- **Hybrid**: juggle within a notebook, split across notebooks only when ceiling forces it

**Important:** The Research Findings Document must note which source groups anchored which sections: "Topic A findings based on sources [IDs]. Topic B findings based on sources [IDs]. Cross-topic synthesis used full corpus."

---

## ⛔ IMPORT DEDUP GUARD — MANDATORY AFTER EVERY `research wait --import-all`

`research wait --import-all` has a known duplication bug: when the wait command times out and retries, each retry re-imports the full result set. A single deep research query returning 71 sources can produce 378 sources (5x duplication) if the timeout triggers 5 retries. This wastes 15-20 minutes on cleanup and can blow past the notebook source ceiling.

**This guard runs unconditionally after every `research wait --import-all`. It is not gated on source count or ceiling proximity.**

### Safe Import Protocol

**Step 1 -- Record pre-import count:**
```bash
# BEFORE starting research wait:
notebooklm source list --json --notebook <ID>
# Record: PRE_IMPORT_COUNT = [N]
```

**Step 2 -- Use adequate timeout (NEVER rely on default):**
```bash
# Deep research needs 600s+ timeout to avoid retry cascades
notebooklm research wait --import-all --timeout 600 --notebook <ID>
```
Short timeouts (30s default) cause multiple retry attempts, each re-importing the full result set. This is the root cause of the duplication bug.

**Step 3 -- Validate immediately after import:**
```bash
notebooklm source list --json --notebook <ID>
# Record: POST_IMPORT_COUNT = [N]
# Calculate: DELTA = POST - PRE
```

**Step 4 -- Evaluate the delta:**

| Condition | Action |
|-----------|--------|
| DELTA <= 80 | Normal. Proceed to Source Audit. |
| DELTA 81-150 | Warning. Likely partial duplication. Run dedup question before audit. |
| DELTA > 150 | Duplication bomb confirmed. Run emergency dedup before anything else. |

**Emergency dedup question (run when DELTA > 80):**
```bash
notebooklm ask "List every source in this notebook grouped by title. For each title that appears more than once, list all source IDs. Output format: TITLE | COUNT | IDs (comma-separated). Only list titles with count > 1." --save-as-note --notebook <ID>
```
Parse the response. Delete all but one copy of each duplicated source:
```bash
notebooklm source delete <duplicate_id> --yes --notebook <ID>
```
Batch deletion is expensive (~2.3s per source). Prevention via adequate timeout is always cheaper than cleanup.

### Q&A Stability Rule

**Do not run Q&A questions while source deletion is in progress.** The corpus is unstable during deletion. Q&A questions issued during active deletion may fail (exit=1) or return incomplete/corrupted results. Complete all deletions, then verify source list, then begin Q&A.

### Q&A Failure Recovery

If a Q&A question returns exit=1:
1. Check if source deletions are running concurrently. If so, wait for them to finish.
2. Run `source list --json` to verify corpus state.
3. Re-run the source audit if deletions happened since the last audit.
4. Retry the question once. If it fails again, simplify the question scope.
5. Log the failure in the Research Findings Document under "Research Journey Metadata."

---

## ⛔ SOURCE QUALITY ENFORCEMENT — HARD GATE. NO EXCEPTIONS.

Q&A does not begin until the corpus passes this gate. This is not a guideline.

### Hard Reject List — Exclude on Sight, No Review Required
- Social media: Twitter/X, LinkedIn posts, Facebook, Instagram
- Community platforms: Reddit, Hacker News, Quora, Stack Overflow
- Video platforms: YouTube, TikTok, Vimeo, any video-hosted content
- Vendor marketing: product pages, sales whitepapers, press releases, sponsored content
- Unattributed content: no named author, no institutional affiliation visible
- AI-generated summaries from aggregators (Perplexity, you.com, similar)
- News aggregators with no original reporting

### Accepted Tiers
| Tier | Examples | Decision |
|------|----------|----------|
| 1 | Systematic reviews, meta-analyses (Nature, Science, Cochrane, PNAS) | ✅ Accept |
| 2 | Peer-reviewed journals, IEEE, RAND, IARPA, National Academies | ✅ Accept |
| 3 | Case studies, NIST/ISO/government standards, established tech journals | ✅ Accept |
| 4 | Expert opinion in refereed venues (HBR, Studies in Intelligence) | ⚠️ Flag — fill gap use only |
| 5 | Unreviewed blogs, practitioner posts, vendor content | ❌ Reject |

**Minimum corpus before Q&A begins: 15 Tier 1–3 sources.**

### Source Audit — Run After Every Import (Mandatory)
After every `research wait --import-all`, immediately run this before the next query:
```bash
notebooklm ask "Audit every source currently in this notebook. For each source list: (1) full title and domain, (2) source type — peer-reviewed paper / academic preprint / government or standards document / established technical publication / news article / blog / social media / vendor marketing / other, (3) named author and institution if visible, (4) Tier 1–5 rating. Then explicitly list the IDs of any sources to exclude: social media, Reddit, YouTube, TikTok, unattributed content, vendor marketing without disclosed methodology, or Tier 5." --save-as-note --notebook <ID>
```
Parse the response. **Delete** all flagged sources (Tier 5, hard-reject categories) from the notebook:
```bash
# Delete every flagged source — social media, Reddit, YouTube, vendor marketing, Tier 5
notebooklm source delete <bad_id_1> --yes --notebook <ID>
notebooklm source delete <bad_id_2> --yes --notebook <ID>
```
For exact duplicates (same paper, same content), **delete** them to free source slots:
```bash
notebooklm source delete <duplicate_id> --yes --notebook <ID>
```
If corpus is thin after pruning (< 15 Tier 1–3 sources), add targeted URLs:
```bash
notebooklm source add "https://specific-quality-source.com" --notebook <ID>
```

**Note:** Deletion is permanent. If you later need a deleted source, re-add it with `source add`. Prioritize aggressive pruning — a clean corpus produces better Q&A than a large one with noise.

### Pre-Q&A Corpus Gate — Final Check Before Phase 3
```bash
notebooklm ask "Final corpus validation before Q&A. State: (1) total source count, (2) tier distribution — how many Tier 1, 2, 3, 4, 5, (3) are there any remaining sources from social media, video platforms, Reddit, unattributed blogs, or vendor marketing? List any that remain. (4) Is the corpus sufficient to support rigorous Q&A on this topic?" --save-as-note --notebook <ID>
```
**If any hard-reject sources are still present: delete them. If Tier 1–3 count < 15: add sources. Only then proceed to Phase 3.**

**For evaluation tasks — additional gate:** Count only external research sources toward the minimum. The subject document (design spec, architecture doc, or any document provided for evaluation) does not count. If removing the subject document leaves fewer than 15 Tier 1–3 sources, the corpus is not ready. Do not begin Q&A.

---

## ⛔ READINESS GATE — ENFORCED BY HOOK, FAIL-CLOSED

`notebooklm ask` is blocked by a PreToolUse hook (`research-qa-gate.py`) until the
target notebook's `notebook-index.json` entry proves the pre-Q&A discipline ran:

1. **Phase-0 scope recorded** — `central_question` + `output_mode` on the entry.
2. **Persona set** — recorded automatically when `configure --persona` succeeds.
3. **Source audit complete** — recorded by `source-audit.py`, no hard-rejects left.

**Fail-closed:** a notebook that is not registered, or registered but missing any
of the above, is **denied** (not silently allowed). Only a missing/unreadable index
fails open. `notebooklm create` auto-registers a stub entry (via the observer hook),
so the compliant flow is: create → **record scope into the index entry** → configure
persona → run source audit → then ask. Overrides exist (`HARNESS_QA_*_OVERRIDE=1`) but
using one is an explicit, logged decision to skip a gate — not a default.

This closes the historical hole where a session registered its notebook late (or
never) and the gate no-op'd, giving zero enforcement for exactly the fresh-campaign
case that needed it most.

## Quick Start

```bash
# 1. Confirm NotebookLM is ready
notebooklm auth check

# 2. Create focused notebook
notebooklm create "Research: [Topic]" --json

# 3. Run deep research (primary method)
notebooklm source add-research "query covering key concepts" --mode deep --notebook <ID>
notebooklm research wait --import-all --timeout 600 --notebook <ID>

# 4. IMMEDIATELY validate import (see Import Dedup Guard below)
notebooklm source list --json --notebook <ID>
# If source count is unexpectedly high (2x+ what research found), run dedup before proceeding

# 5. Ask structured questions, save every response
notebooklm ask "Your research question" --save-as-note --notebook <ID>

# 6. Run completion gates before declaring done (see COMPLETION-AND-DELIVERABLES.md)
```

---

## 1. When This Skill Activates

**Activate for:**
- Any open-ended research task: "research X", "deep dive on X", "investigate X"
- Source collection: "find sources on", "gather evidence about", "add research to notebook"
- Synthesis: "what does the evidence say about", "synthesize research on"
- Claim evaluation: "is X supported by research", "evaluate the claim that"
- Any task requiring cross-source validation before a firm recommendation

**Do not activate for:**
- Single-source lookups or quick factual questions
- Tasks where the user has already provided all the evidence
- Code debugging, file editing, or tasks that do not require external evidence synthesis

---

## ⛔ SUBJECT DOCUMENT vs. CORPUS SOURCE — HARD DISTINCTION

**The document being evaluated is NOT a corpus source. It is the claim being tested.**

If the task is to evaluate, review, or stress-test a design document, architecture spec, or any document provided by the user — that document is the **subject** of the research. It does not count toward the corpus minimum. It is never a substitute for external evidence.

**Two task types — completely different workflows:**

| Task | What to do |
|------|-----------|
| "Research topic X" | Build a corpus about X. The corpus IS the research. |
| "Evaluate document Y" | Build a corpus of external evidence about the technologies and patterns Y depends on. Test Y's claims against that evidence. |

**For evaluation tasks:**
- Load the subject document into the notebook as context — but label it as "SUBJECT DOCUMENT" in your working notes
- It does not count toward the 15 Tier 1–3 minimum
- Research queries must target external evidence on the underlying technologies, patterns, and claims the document makes — NOT on the document itself
- Q&A questions ask NotebookLM to cross-reference claims in the subject document against external research evidence
- Asking NotebookLM to evaluate a design using only that design as a source produces nothing but the document parroting itself — this is not research

**The test:** Before beginning Q&A, ask: "If I remove the subject document from this notebook, do I still have 15 Tier 1–3 sources?" If no — stop. The corpus is not ready.

---

## 2. Data Handling Rules

Enforced throughout every research session. Never overridden.

**Permitted:**
- General concepts, patterns, and methodologies
- Public domain academic and technical content
- Tool names and publicly available product information

**Prohibited — never include in titles, queries, Q&A, or notes:**
- Organization names or internal team identifiers
- Individual names, email addresses, or usernames
- Infrastructure hostnames, IP ranges, or environment identifiers
- PHI, PII, or any regulated data category
- Internal process details that identify a specific organization

**Rule of thumb:** Abstract the concept. "Enterprise SOAR workflow for alert triage" is acceptable. An org-specific process name is not.

---

## 3. Research Phases

Seven sequential phases. Do not skip phases or declare completion before gates pass (Section 6).

### Phase 0 — Scope Definition
Before touching NotebookLM, define in writing:
- The central research question (one sentence)
- **Application context (optional):** Does this research have a target system or architecture to evaluate against? If yes, name it and provide the context document path. If no, this is general-purpose research — Phase 3C (Application) is skipped entirely and the skill produces pure research findings.
- What "research complete" looks like: capstone understanding — can I reason about this topic independently, challenge my own understanding, and identify the edges of what I know?
- **Output mode:** Determines the shape and depth of the Research Findings Document. If the user's prompt explicitly specifies a format (e.g., "give me an implementation spec," "I need a decision brief," "write a technical reference"), set the mode directly without asking. If the prompt does not specify, present the selector below.

#### Output Mode Selector

If the user has not specified an output format, use AskUserQuestion before proceeding to Phase 1:

- **Header:** "Output Mode"
- **Question:** "What kind of research output do you need?"
- **Options:**
  1. **Synthesis (Recommended)** — Conceptual summary for understanding. Balanced depth across all sections. Best for: "help me understand this topic."
  2. **Implementation Spec** — Technical detail sufficient to build from. Code patterns, config examples, API specifics, dependency chains, parameter tables. Best for: "I need to implement this."
  3. **Decision Brief** — Compressed, BLUF-heavy executive format. Sections 4-9 become a condensed appendix. Best for: "should we adopt X?"
  4. **Technical Reference** — Exhaustive catalog of every mechanism, parameter, trade-off, edge case. Reference material to consult later. Deepest Q&A phase. Best for: "document everything about this."
- If the user selects "Other" and describes an evaluation/stress-test task, set mode to **Evaluation Report** (tests subject document claims against evidence; requires a subject document).

#### Mode Validation Rules

After mode is set (whether by selector or inferred from prompt):

- **Implementation Spec + no application context declared:** Prompt the user: "Implementation Spec requires an application context — a target system or architecture to specify against. Please provide the context document path, or select a different output mode."
- **Evaluation Report + no subject document identified:** Prompt the user: "Evaluation Report requires a subject document to evaluate. Please provide the document path."
- **Decision Brief selected:** Confirm: "Decision Brief compresses sections 4-9 into an appendix for faster delivery. The full evidence trail is preserved but summarized. Proceed?"

Record the selected output mode in the Phase 0 scope definition. It propagates to Phases 3, 4, and 5.

### Phase 1 — Notebook Creation and Source Collection
```bash
notebooklm create "Research: [Descriptive Topic]" --json

# Configure notebook for research-grade responses (mandatory — do not skip)
notebooklm configure --persona "You are a research corpus analyst supporting a multi-phase research investigation. Your role is to extract, synthesize, and present evidence from the loaded sources with maximum rigor.

RULES — apply to EVERY response:
1. ALWAYS cite specific sources by name for every factual claim. Never assert without citation.
2. Distinguish what sources explicitly state (findings) from what you infer (interpretation). Label each clearly.
3. When sources disagree, present BOTH positions with the evidence basis for each. Do not silently pick a side.
4. Identify what the sources do NOT cover that is relevant to the question. Gaps are as important as findings.
5. Flag single-source claims — note when a finding rests on only one source vs. multiple independent sources.
6. Never fabricate, extrapolate beyond what sources support, or fill gaps with general knowledge. If the corpus does not cover it, say so.

ADAPT your response style to the question:
- Broad/exploratory questions: map the landscape, surface competing approaches, identify the key mechanisms and where coverage is strong vs. thin
- Specific/targeted questions: precise answers with full citation chains, evidence quality noted, counter-arguments surfaced
- Evaluation questions: cross-reference claims against evidence, note where claims are supported vs. unsupported vs. contradicted

Response length: longer. Prefer depth over brevity when the evidence warrants it." --response-length longer --notebook <ID>

# If application context was declared in Phase 0, add the context document:
notebooklm source add /path/to/context-document.md --notebook <ID>
notebooklm source add-research "initial broad query" --mode deep --notebook <ID>
notebooklm research wait --import-all --timeout 600 --notebook <ID>
```
→ **Run Import Dedup Guard immediately** (see ⛔ IMPORT DEDUP GUARD section). Record pre/post source counts, evaluate delta, run emergency dedup if needed.
→ If `research wait --import-all` times out: **check `source list` before anything else.** Partial imports frequently succeed even when the wait command times out. If sources are present, run the audit on what imported and proceed. If zero sources, treat as a failure. See NOTEBOOKLM-INTEGRATION.md for full recovery protocol.
→ **Run Source Audit immediately** (see ⛔ enforcement section above). Delete rejects and exact duplicates. Fill gaps.

### Phase 2 — Targeted Source Expansion
Sequence queries — do not run in parallel. After each import, run the full audit cycle before starting the next query. Number of queries depends on topic breadth — not fixed at 2-3.

```
For each query:
  1. Record pre-import source count (source list --json)
  2. source add-research "query" --mode deep --notebook <ID>
  3. research wait --import-all --timeout 600 --notebook <ID>
  4. Run Import Dedup Guard → check delta → emergency dedup if needed
  5. Run Source Audit → delete rejects and exact duplicates → fill gaps if thin
  6. Complete ALL deletions before starting the next query or any Q&A
  7. Only then start the next query
```

After all queries complete, run the **Pre-Q&A Corpus Gate** (see ⛔ enforcement section).
Do not advance to Phase 3 until the gate passes.
Rate limit: if a query fails, wait 2 minutes and retry once. If still failing with 15+ Tier 1–3 sources loaded, proceed and document the gap.

### Phase 3 — Research Journey

This is a dynamic, multi-phase dialogue — not a script. Claude drives every transition. Every NotebookLM response is evaluated before the next question is formulated. The 5-round depth ladder from [QUESTION-FRAMEWORKS.md](QUESTION-FRAMEWORKS.md) provides the question generation instruments; the phase journey provides the orchestration logic that determines which instruments to use when.

**Synthesis is real-time.** Claude is not accumulating notes to reason on later. Each NotebookLM response immediately updates the mental model that drives the next question. The synthesis is happening continuously — not as a terminal step.

Save every response: `notebooklm ask "question" --save-as-note --notebook <ID>`
Apply the Bias Prevention Checklist throughout (see [BIAS-PREVENTION.md](BIAS-PREVENTION.md)).

#### Phase 3A — Exploratory (Territory Mapping)
**Goal:** Build a mental model of the domain. Map what's in the corpus.
**Question style:** Round 1 (Starbursting) and Round 2 (Structural Decomposition). Open-ended, concept-discovering.
**Context rule:** NO application context in questions. No project framing, no architecture references. The context document may be in the notebook (loaded in Phase 1) — but questions don't reference it yet. Explore the technology on its own terms first.
**Examples:**
- "What are the primary mechanisms described in this research?"
- "What do the sources agree and disagree on?"
- "What are the main competing approaches documented in this corpus?"

**→ Transition to Phase 3B when:**
- Can articulate the 3-5 core principles or mechanisms of this topic
- Have identified the main competing approaches
- Have mapped the key sub-topics and know which have strong vs. thin coverage
- No major territory remains unexplored in the source corpus

#### Phase 3B — Crystallization (Concept Deepening)
**Goal:** Build precise, falsifiable understanding of concepts identified in 3A.
**Question style:** Round 2 (Decomposition), Round 3 (Falsification), Round 4 (Premortem). Targeted, precision-seeking.
**Context rule:** Domain framing begins. "For a retrieval pipeline..." or "In a multi-layer search architecture..." is acceptable. Still extracting FROM research, not fitting TO a specific architecture.
**Examples:**
- "What are the documented failure modes of [mechanism X] at scale?"
- "What evidence would disprove the claimed performance benefit of [approach Y]?"
- "Under what conditions does [approach Z] degrade, and what does the evidence quality look like?"

**→ Transition to Phase 3C when:**
- Can explain each core mechanism with specific evidence citations
- Have applied falsification (Round 3) to at least the primary findings
- Understand the documented failure modes and limitations
- Clear picture of evidence quality — know which findings are Tier 1-2 anchored vs. Tier 3 only
- Devil's advocate has been applied and the understanding survived

#### Phase 3C — Application (Targeted Context Integration)
**If no application context was declared in Phase 0, SKIP Phase 3C entirely — go directly to Phase 4.**

**Goal:** Apply the crystallized understanding to the declared application context.
**Question style:** Round 3 (Falsification), Round 4 (Premortem), Round 5 (Metacognitive). Precise, constrained, application-specific.
**Context injection:** Claude proactively adds application-specific context to the notebook as new sources when the research matures to warrant it. The notebook's context GROWS with research depth.
**Context injection decision criteria:** Inject when (a) a specific architectural constraint is now relevant to the questions being asked AND (b) foundational understanding from 3A/3B is solid enough that the context won't contaminate exploratory findings.
**Examples:**
- "Given a system with [specific constraint from context doc], how would [mechanism X] interact with [existing component Y]?"
- "What implementation prerequisites does [mechanism X] require that [specific architecture] does not currently provide?"

**CRITICAL: Phase 3C questions CANNOT be pre-written.** They emerge from what was learned in 3A and 3B. Seed questions in handoffs are Phase 3A entry points only.

#### Output Mode — Phase 3 Question Emphasis

The output mode (set in Phase 0) adjusts which types of questions receive additional emphasis during the research journey. The base phase logic (3A explores, 3B tests, 3C applies) is unchanged. Mode adds a lens.

| Mode | Phase 3A Emphasis | Phase 3B Emphasis | Phase 3C Emphasis |
|------|-------------------|-------------------|-------------------|
| **Synthesis** | (default behavior) | (default behavior) | (default behavior) |
| **Implementation Spec** | Surface APIs, protocols, config surfaces, and parameter inventories early. Ask "what interfaces does this expose?" alongside standard starbursting. | Drive toward implementation steps, dependency chains, and concrete specifics. Round 2 decomposition targets implementation order, not just concepts. "What are the exact steps, dependencies, and prerequisites for implementing [mechanism X]?" | "What does [mechanism X] require from [target architecture] that does not exist today? What is the integration sequence?" |
| **Decision Brief** | Narrow faster. Identify the 2-3 decision-relevant factors and deprioritize deep mechanism exploration. | Focus falsification on the decision criteria, not on mechanism internals. "Under what conditions would adopting X be the wrong decision?" | "What is the risk-adjusted recommendation and what are the top 3 reasons it could be wrong?" |
| **Technical Reference** | Go widest. Every sub-topic, edge case, and variant. Do not narrow prematurely. Spend more rounds in 3A than other modes. | Every mechanism gets falsification. Document parameter ranges, not just parameter existence. Do not skip mechanisms that "seem obvious." | Exhaustive application mapping. Every integration point, every constraint, every prerequisite. |
| **Evaluation Report** | Map the testable claims the subject document makes. Identify which claims are evaluable against the corpus. | Test each major claim against evidence. "Does the corpus support or contradict [claim from subject doc]?" | "Where does the subject document's design diverge from what the research evidence supports, and what is the severity of each divergence?" |

#### Bi-Directional Evaluation Protocol

After every NotebookLM response, before formulating the next question:
1. **Sufficiency check:** Did this response fully address the question, or does it need a follow-up?
2. **Source grounding check:** Is the response citing specific sources, or giving generic answers?
3. **Thin spot scan:** Did this response reveal a gap in coverage?
4. **Contradiction check:** Does this conflict with prior responses?
5. **Phase assessment:** Based on accumulated understanding, am I still in the right sub-phase?

If any check fails, the next question addresses that failure — not the next item on a list.

#### Dynamic Termination

The research journey is complete when Claude can answer YES to all:
- Can I articulate the core principles of this topic without referencing NotebookLM?
- Can I identify the edges of what I know vs. what remains uncertain?
- Can I challenge my own understanding and identify where it might be wrong?
- Have I applied falsification and the understanding survived?

The 5-round depth ladder is a **minimum structure, not a ceiling.** Phase 3 may take 5 rounds or 50. Rounds are not capped.

### Phase 4 — Research Synthesis
**NotebookLM produces research findings only. It does not make architectural recommendations.**

The context document in the notebook is there to focus Q&A on the relevant use case — not for NotebookLM to evaluate architectural fit. That evaluation happens in the synthesis pass (Phase 7), not here.

The synthesis question varies by output mode (set in Phase 0). Use the appropriate variant:

**Synthesis mode (default):**
```bash
notebooklm ask "Produce a structured research summary on this topic: (1) what the strongest evidence conclusively establishes about this technology, (2) key findings across sources with source quality noted, (3) implementation considerations documented in the literature, (4) documented limitations and failure modes, (5) competing approaches and how they compare, (6) confidence in the evidence base — note if any findings depend primarily on preprint-only evidence, (7) open questions this research does not resolve." --save-as-note --notebook <ID>
```

**Implementation Spec mode:**
```bash
notebooklm ask "Produce a structured implementation-focused research summary: (1) what the evidence establishes as the concrete implementation requirements — APIs, protocols, dependencies, configuration parameters, (2) documented implementation patterns — code-level or config-level approaches that sources describe, with source quality noted, (3) dependency chain — what must exist before this can be implemented, in what order, (4) documented integration points and constraints — how this technology connects to other systems, (5) failure modes specific to implementation and deployment — not theoretical failures but operational ones, (6) parameter tables — every configurable parameter documented in the sources with documented ranges and defaults, (7) what the sources do NOT cover that an implementer would need to know." --save-as-note --notebook <ID>
```

**Decision Brief mode:**
```bash
notebooklm ask "Produce a decision-focused research summary: (1) bottom-line assessment — should this technology be adopted for the stated use case, based purely on evidence, (2) the 3-5 strongest arguments FOR adoption with source quality noted, (3) the 3-5 strongest arguments AGAINST adoption with source quality noted, (4) risk factors — what could go wrong if adopted, (5) opportunity cost — what is lost by NOT adopting, (6) confidence in the evidence base, (7) the single most important unknown that would change this assessment." --save-as-note --notebook <ID>
```

**Technical Reference mode:**
```bash
notebooklm ask "Produce an exhaustive technical reference summary: (1) complete mechanism catalog — every distinct mechanism, approach, or technique documented in the sources, (2) for each mechanism: parameters, configuration options, documented ranges, defaults, and edge cases, (3) for each mechanism: documented failure modes, boundary conditions, and degradation patterns, (4) inter-mechanism relationships — how mechanisms interact, conflict, or complement each other, (5) competing approaches with detailed comparison criteria and evidence basis, (6) version or evolution history if documented — how this technology has changed over time, (7) every open question and gap in the literature." --save-as-note --notebook <ID>
```

**Evaluation Report mode:**
```bash
notebooklm ask "Produce an evidence-based evaluation of the subject document against this research corpus: (1) for each major claim in the subject document, state whether the corpus supports, contradicts, partially supports, or is silent on it — cite specific sources, (2) identify claims that have no evidence basis in the corpus — these are unsupported assumptions, (3) identify areas where the corpus suggests the subject document's approach is suboptimal and what the evidence-supported alternative is, (4) identify areas where the subject document aligns well with best evidence, (5) rank the unsupported or contradicted claims by severity — which ones, if wrong, would cause the most damage, (6) confidence in this evaluation — note any areas where the corpus is too thin to evaluate." --save-as-note --notebook <ID>
```

### Phase 5 — Research Findings Document
Write a Research Findings Document using the Analytic Pyramid adapted to the active output mode (set in Phase 0). All modes use the 10-section structure from [COMPLETION-AND-DELIVERABLES.md](COMPLETION-AND-DELIVERABLES.md) as backbone. Mode determines section depth and emphasis — see the Mode Adaptation Table there.

The document header is common to all modes:

```markdown
# Research Findings: [Topic Title]
**Date:** [YYYY-MM-DD]
**Output Mode:** [Synthesis / Implementation Spec / Decision Brief / Technical Reference / Evaluation Report]
**Notebook:** [NotebookLM notebook ID]
**Source Corpus:** [count] sources — Tier 1: [n], Tier 2: [n], Tier 3: [n], Preliminary/Non-traditional: [n]
**Evidence Confidence:** [High/Moderate/Low] — [one sentence basis]
```

Produce the mode-specific body per the Mode Adaptation Table and Section 10 level definitions in COMPLETION-AND-DELIVERABLES.md.

All modes include the common footer:

```markdown
---
## Research Journey Metadata
**Phase Reached:** [Exploratory / Crystallization / Application]
**Q&A Rounds Completed:** [N]
**Output Mode:** [mode name]
**Application Context:** [Named context and doc path, or "None — general-purpose research"]

## Conceptual Model (Reconstruction Aid)
[3-5 sentences: the mental model Claude constructed through the research journey. Not a summary of findings — a description of HOW the concepts relate to each other, what the core mechanisms are, and what the key trade-offs are. A future session reading this should be able to rebuild working understanding quickly by reading this + asking 3-4 targeted follow-ups to the notebook.]

## Falsification Record
[What was tested via Round 3 probing and what survived. What counter-arguments were considered and why they were judged insufficient to overturn the primary findings.]
```

### Phase 6 — Completion Gating
Apply all six gates (see [COMPLETION-AND-DELIVERABLES.md](COMPLETION-AND-DELIVERABLES.md)). Gates apply to research completeness — sufficient sources, adequate topic coverage, surviving disconfirmation — not to an architectural recommendation. If any gate fails, return to Phase 2 or 3.

### Phase 7 — Output Delivery
Save the Research Findings Document to disk. The default output path is the current working directory, but the user may specify a different location.

```bash
# Default output path:
# ./research-findings/[topic-slug]-[YYYY-MM-DD].md

mkdir -p ./research-findings/
# Write the Research Findings Document to the output path
```

**Update the notebook index** — read `./research-findings/notebook-index.json`, update the entry for this notebook, and write it back. If the file does not exist, create it. Each entry maps a notebook to its research output:

```json
{
  "notebooks": [
    {
      "notebook_id": "<NotebookLM notebook UUID>",
      "topic": "<research topic title>",
      "output_mode": "<Synthesis | Implementation Spec | Decision Brief | Technical Reference | Evaluation Report>",
      "findings_doc": "./research-findings/<topic-slug>-<YYYY-MM-DD>.md",
      "date_created": "<YYYY-MM-DD>",
      "date_last_research": "<YYYY-MM-DD>",
      "evidence_confidence": "<High | Moderate | Low>",
      "source_tiers": { "tier_1": 0, "tier_2": 0, "tier_3": 0, "preliminary": 0 },
      "capstone_reached": true
    }
  ]
}
```

This index enables cross-topic synthesis sessions to discover which notebooks exist, what confidence level they reached, and where the findings document lives, without re-scanning disk or re-querying NotebookLM.

Report the output path to the user and summarize:
- Topic researched
- Output mode used
- Source corpus size and tier distribution
- Evidence confidence level
- Key findings (3-5 bullet summary)
- Notable intelligence gaps

**The per-topic research agent stops here.** If the user wants a follow-up synthesis pass across multiple research topics, that is a separate session. The notebook index provides the mapping.

---

## 4. Reference Files

| File | Contents |
|------|----------|
| [SOURCE-QUALITY.md](SOURCE-QUALITY.md) | 5-tier hierarchy, SIFT method, QoI check, acceptance/rejection criteria |
| [QUESTION-FRAMEWORKS.md](QUESTION-FRAMEWORKS.md) | 5-round depth escalation ladder, AIMS scoping, surface vs deep questions |
| [BIAS-PREVENTION.md](BIAS-PREVENTION.md) | 5 named biases + countermeasures, devil's advocate protocol, premortem |
| [COMPLETION-AND-DELIVERABLES.md](COMPLETION-AND-DELIVERABLES.md) | 6 completion gates, Analytic Pyramid format, confidence language standards |
| [NOTEBOOKLM-INTEGRATION.md](NOTEBOOKLM-INTEGRATION.md) | Full CLI command reference, rate limit handling, note conventions |

---

## 5. Autonomy Rules

### Runs Without Confirmation
- Auth checks and status queries
- Notebook creation with descriptive, non-sensitive titles
- Notebook chat configuration (persona, mode, response length)
- Deep research queries using only public concepts (no org names, no PII)
- Adding publicly accessible web sources
- All Q&A questions and note-saving operations
- Building and writing the deliverable file
- Writing the Research Findings Document to disk

### Requires User Confirmation
- Deleting a notebook or any source
- Content that appears to contain PII or org-specific identifiers — halt and flag first
- Overwriting a previously completed deliverable
- Using `--dangerously-skip-permissions` — always explain and ask first

### Escalation Triggers — Stop, Report, Ask
- A research topic would require prohibited data to answer properly
- All completion gates fail and the corpus appears fundamentally insufficient
- Significant conflict exists between equal-tier sources with no methodological basis to adjudicate
- The question is a "mystery" (irreducibly contingent on unknowable future events) — inform the user the question may not be answerable with research
- Rate limits persist beyond 10 minutes

### Quality Standards — Never Compromise
- Never declare complete when Gate 2 (survival of disconfirmation) has not been attempted
- Never anchor a recommendation to a single source regardless of tier
- Never omit the intelligence gaps section because gaps are uncomfortable
- Never use placeholder text in deliverables
- Never collapse findings, insights, and recommendations into a single undifferentiated list
