# Question Formulation Frameworks

Research questions govern the depth and quality of everything that follows. Shallow questions produce shallow research.

## Surface vs. Deep Question Distinction

**Surface questions** address "puzzles" — factual inquiries with a single correct answer, answerable given sufficient data. They are often solution-driven or assumption-driven, which limits thinking by building conclusions into the query.

**Deep questions** address "mysteries" — contingent, nonlinear problems where simple models fail. They explore clashing causal forces, strategic interaction, and actors behaving in ways that appear irrational. These are the questions worth asking.

---

## Five-Round Question Depth Escalation Ladder

### Round 1 — Parameter Definition (Starbursting)
Generate questions, not answers. Map the full problem space before narrowing.

Apply 5W1H to the focal issue:
- "Who are the key actors affected by [X] and what are their incentives?"
- "What are the conditions under which [X] would NOT hold?"
- "How much of [Problem X] is NOT caused by [Factor Y]?" — the 180-degree turn
- "When does [X] produce the opposite of the expected effect?"

**Goal:** Define the boundaries. Identify what you're *not* researching before committing to what you are.

### Round 2 — Structural Decomposition (Fermi-izing)
Break intractable problems into smaller, independently evaluable sub-problems.

- "What are the three smallest sub-components of [X] that could be independently evaluated?"
- "If [Problem X] were broken into [Factor A], [Factor B], [Factor C], which has the most diagnostic evidence?"
- "What is the minimum viable version of [X] — stripped to its core claim?"

**Goal:** Prevent mission creep. Establish which sub-questions have strong evidence and which are still open.

### Round 3 — Falsification Probing (Alexander's Question)
Transition from "what is known" to "what would disprove my current view."

- "If my lead hypothesis is true, what evidence should I expect NOT to see?"
- "What new data would convince me that [current view] is incorrect?"
- "Could this have been true in the past but no longer valid today?"
- "What is the strongest published argument against this conclusion?"

**Goal:** Force active disconfirmation. This is the round most frequently skipped, and the most important.

### Round 4 — Cognitive Reframing (Prospective Hindsight / Premortem)
Shift perspective by imagining the analysis has already failed and working backward.

- "It is [date+6 months]. This conclusion turned out to be completely wrong. What were the top three reasons for that failure?"
- "What is the strongest argument a serious critic would make against this conclusion?"
- "Which assumption, if wrong, would most damage this recommendation?"

**Goal:** Surface failure modes before they occur. Prospective hindsight increases identification of failure modes by ~30% vs standard questioning.

### Round 5 — Metacognitive Critique
Think about the thinking process itself. Audit for information gaps, deception, and causation-correlation confusion.

- "What information gaps remain, and which are diagnostically significant vs negligible?"
- "Where have I confused correlation with causation in this analysis?"
- "What would a novice examining this same data conclude, and where would their reasoning differ from mine?"
- "What is this research corpus missing that I have not thought to look for?"

**Goal:** Close the loop. Ensure the methodology itself has not introduced error.

---

## AIMS Framework — Scoping Before You Ask

Before finalizing any research question, filter through:

| Letter | Question | Purpose |
|--------|----------|---------|
| **A** — Audience | Who will use this research and at what knowledge level? | Calibrates depth and vocabulary |
| **I** — Issue | What specific problem are they struggling with now? | Keeps research action-oriented |
| **M** — Message | What is the bottom-line judgment this research must produce? | Defines success criteria upfront |
| **S** — Storyline | What logical sequence takes the reader from evidence to conclusion? | Structures the deliverable before writing it |

---

## Question Quality Checklist

Before submitting a question to NotebookLM, verify:

- [ ] It cannot be answered "yes" or "no" — forces elaboration
- [ ] It does not contain the answer — avoids leading questions
- [ ] It is specific enough to be answerable from the loaded sources
- [ ] It advances the research — not just filling time
- [ ] At least one question per session uses Round 3 (falsification) framing
- [ ] The synthesis question (Phase 4) explicitly asks for competing hypotheses considered and gaps remaining

---

## Phase-Specific Question Selection

The 5-round depth ladder provides the instruments. The research journey phase (Phase 3 of SKILL.md) determines which instruments to use:

| Phase | Primary Rounds | Secondary Rounds | Avoid |
|-------|---------------|-----------------|-------|
| 3A — Exploratory | Round 1 (Starbursting), Round 2 (Decomposition) | — | Rounds 3-5 (premature before territory is mapped) |
| 3B — Crystallization | Round 2 (Decomposition), Round 3 (Falsification) | Round 4 (Premortem) | Round 1 (territory already mapped) |
| 3C — Application | Round 3 (Falsification), Round 4 (Premortem), Round 5 (Metacognitive) | — | Round 1 (too broad for application phase) |

Phase 3A questions discover. Phase 3B questions test. Phase 3C questions apply.

---

## DA Round Expansion Policy

After the standard 5 rounds (R1-R5), every research session adds mandatory Devil's Advocate rounds. Round type definitions and their analytic purposes are in the DA Round Type Catalog in BIAS-PREVENTION.md.

### Tier Selection

| Tier | DA Rounds | Required Types | When |
|:-----|:----------|:---------------|:-----|
| **Minimum** | 3 | Steelman + Multi-Bias Audit + Alexander's Question | ALL research, no exceptions |
| **Standard** | 5 | Minimum + Logical Fallacy Detection + Verification Protocol | Research that informs real-world decisions |
| **Extended** | 8 | Full catalog | Vendor claims, adversarial parties, or high-stakes operational decisions |

The catalog is a floor, not a ceiling. The user can always request additional rounds beyond the tier requirement.

### Tier Escalation Rules

- Default to Minimum unless the research context triggers Standard or Extended.
- If any source is a vendor or party with financial/reputational interest in the outcome, escalate to Extended.
- If the findings will be presented to decision-makers or used to justify operational action, escalate to at least Standard.
- When in doubt, escalate. The cost of an unnecessary DA round is minutes; the cost of a missed bias is a flawed conclusion.

---

## Output Mode Question Overlays

When an output mode is active (set in Phase 0 of SKILL.md), add these question types to the phase-appropriate rounds. These supplement the standard question instruments, they do not replace them.

### Implementation Spec — Additional Question Instruments

- **Round 1 addition:** "What are the concrete interfaces, APIs, protocols, and configuration surfaces this technology exposes?"
- **Round 2 addition:** "Break [mechanism X] into its implementation dependencies — what must exist before it can be built, and in what order?"
- **Round 3 addition:** "What are the documented implementation failures — not conceptual failures, but cases where a technically sound approach failed in deployment due to integration, performance, or operational issues?"
- **Round 4 addition:** "If we implemented this and it failed in production, what would the most likely cause be — and is it a cause the research addresses?"

### Decision Brief — Additional Question Instruments

- **Round 1 addition:** "What are the 3 factors most likely to determine whether adopting this technology is the right decision for the stated use case?"
- **Round 3 addition:** "What is the strongest argument AGAINST adoption, from someone who understands the technology well?"

### Technical Reference — Additional Question Instruments

- **Round 1 addition:** "What are ALL the parameters, configuration options, and operational knobs this technology provides? Do not summarize — enumerate."
- **Round 2 addition:** "For each sub-component, what are the boundary conditions, edge cases, and failure modes?"

### Evaluation Report — Additional Question Instruments

- **Round 2 addition:** "List every testable claim in the subject document. For each, state whether the corpus supports, contradicts, or is silent on it."
- **Round 3 addition:** "For each unsupported or contradicted claim, what would the subject document need to change to align with the evidence?"

---

## Phase 3C Integrative Synthesis Pattern

The highest-value Phase 3C questions follow a specific pattern identified from research sessions that produced strong architectural insights:

> **"X is true of the technology. The application context already does Y. Does X therefore suggest the system should Z?"**

This pattern forces the connection between what the research established (X) and what already exists in the target architecture (Y) to derive a specific architectural implication (Z). It is more productive than asking "should we adopt X?" because it grounds the question in existing capability rather than a blank slate.

**Examples of this pattern in practice:**

- *"Research establishes that neuro-symbolic systems use dense neural retrieval (System 1) + symbolic exact matching (System 2). The target system already has dense vector search + BM25 keyword matching. Does this mean it is already a de facto neuro-symbolic system, and is the only question whether to extend symbolic reasoning into the response phase?"*

- *"Research shows Logic Tensor Network constraints can be applied at inference time on frozen models as post-retrieval filters. The target system uses frozen embedding models. Does this mean LTN-style constraints are achievable without retraining, and the question is only what constraints to formalize?"*

- *"Research shows hierarchical attention mechanisms use high-level category signals to restrict lower-level computation. The target system has a topic hierarchy above its retrieval layers. Does this suggest topic confidence should gate retrieval fan-out scope?"*

**When to use it:** Phase 3C, after 3B transition criteria are met. This pattern only works when foundational understanding is solid — applying it prematurely produces superficial conclusions. It is the natural question that emerges when genuine Phase 3B depth meets Phase 3C application context.
