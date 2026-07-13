# Completion Criteria and Deliverable Format

## Six Completion Gates

Research is complete when it passes all six gates. A failed gate requires returning to Phase 2 or 3. Do not declare research complete early.

### Gate 1: Methodological Veracity
The central claim is anchored in Tier 1 or Tier 2 evidence. If all supporting sources are Tier 3-4, the research is not complete — return to Phase 2 with a more targeted query.

### Gate 2: Survival of Disconfirmation
The lead hypothesis has been run through ACH and emerged with the lowest inconsistency score. It has been tested by the devil's advocate protocol and survived. This gate cannot be passed by skipping the check.

### Gate 3: Linchpin Stability
A sensitivity analysis has confirmed the conclusion remains valid when the most critical linchpin assumptions are varied or challenged. Identify the top 2-3 premises the conclusion depends on, then ask: "If this premise is false, does the conclusion reverse?" If yes, that premise must be supported by at least 2 independent Tier 1-2 sources.

### Gate 4: Consensus Through Dissent
A structured devil's advocacy or premortem has been conducted. The core logic has survived a genuine attempt to refute it. This is not the same as Gate 2 — Gate 2 is about evidence, Gate 4 is about reasoning.

### Gate 5: Standardized High Confidence
The conclusion can be assigned at minimum Moderate Confidence (55-80%): the information is credibly sourced, consistent across sources, and remaining gaps do not overturn the conclusion. If only Low Confidence is achievable, the deliverable must state this explicitly and explain why more research did not resolve the uncertainty.

### Gate 6: Alexander's Question Answered
The researcher has specified in advance what data would change the conclusion, and has confirmed that such data does not currently exist in the loaded sources. This is a falsifiability commitment — it must be documented in the deliverable.

---

### When More Research Is Required (Gate Failure Conditions)
- Gaps in diagnostic evidence remain — missing information that would discriminate between two viable hypotheses
- Anomalous data — events that should have occurred if the hypothesis were true but did not — remains unexplained
- The conclusion relies on Tier 4-5 anchor with no Tier 1-2 corroboration
- Sensitivity analysis shows the conclusion reverses when a linchpin assumption changes

### Actionability vs. Delay Tradeoff
In time-sensitive situations, research may be declared actionably complete before all gates pass if the risk of delay outweighs the marginal accuracy gain from more research. This must be explicitly documented as a qualified recommendation with identified residual risk and a plan to close the gap.

---

## Deliverable Format — The Analytic Pyramid

All research outputs follow this 11-section structure. Every section must contain real content. No placeholder text. No omissions.

### Section 1: Problem Statement
One to two sentences. A clear, unbiased definition of the core question or decision being addressed. Does not contain the answer.

### Section 2: Research Design
The analytic approach: which structured analytic techniques were used (ACH, devil's advocacy, premortem, red hat), the number and tier distribution of sources loaded, and the Q&A methodology applied.

### Section 3: Bottom Line Up Front (BLUF)
The most significant insights and the bottom-line recommendation, stated first. Follows the AIMS structure:
- Audience and their knowledge level
- Issue they are struggling with
- Message — the bottom-line judgment
- Storyline — the logical sequence to the conclusion

### Section 4: Linchpin Assumptions
Explicitly list the foundational premises that must be true for the judgment to hold. For each:
- State the assumption
- State why it is accepted (evidence basis)
- State what would falsify it

### Section 5: Evidence Summary
Key data points, evidence items, and logical arguments considered. Organized by Tier. Cite source quality levels. Include the tier distribution of the source base.

### Section 6: Alternative Hypotheses
Discuss the relative likelihood of all competing possibilities considered. Justify why each alternative was rejected as less likely. Do not omit alternatives that were seriously considered — their rejection is part of the analysis.

### Section 7: Calibrated Uncertainty
Assign standardized confidence levels to each judgment. Use specific language (see standards below). Supplement with numeric probabilities where supported by the evidence.

### Section 8: Intelligence Gaps
State explicitly what is still unknown. Distinguish:
- **(a) Diagnostically significant gaps** — must be filled; their resolution would change the conclusion
- **(b) Acknowledged limitations** — noted but do not change the conclusion

### Section 9: Milestones for Revision
Specify which future events or data points would prove the current analysis incorrect and trigger re-evaluation. This is the Gate 6 falsifiability commitment, written in the deliverable.

### Section 10: Findings, Insights, and Recommendations
All conclusions across three distinct, never-collapsed levels:

| Level | Definition | Answers |
|-------|-----------|---------|
| **Finding** | Raw data, observable facts, documented evidence | "What is?" |
| **Insight** | Interpreted meaning, patterns, causal forces | "What does this mean?" |
| **Recommendation** | Specific proposed action, contingency plan, or collection requirement | "What should be done?" |

Never state a fact as a recommendation. Never state an assumption as a finding.

### Section 11: DA Due Diligence Register

Required in every findings document. One entry per DA round conducted. The register pairs each original theory or claim with its DA finding, creating a structured audit trail of the devil's advocate work.

Format per entry:

```markdown
### DA-N: [Topic]
| | Content |
|:--|:--------|
| **Original Theory** | [What the subject claims] |
| **DA Finding** | [What the evidence actually shows] |
| **Fallacy Identified** | [If any; "None" if clean] |
| **Sources** | [URLs] |
| **Steelman Concession** | [What is valid in the original theory] |
```

The Steelman Concession line is mandatory. It prevents the register from becoming a one-sided prosecution document. If the original theory has no merit whatsoever, state that explicitly with evidence rather than leaving the field blank.

---

## Mode Adaptation Table

The Analytic Pyramid 11-section structure applies to all output modes. Modes modify section depth and emphasis, not section existence. Every section must still contain real content, but "real content" scales from a single focused paragraph (compressed) to multiple pages with tables and code blocks (expanded).

| Section | Synthesis | Implementation Spec | Decision Brief | Technical Reference | Evaluation Report |
|---------|-----------|-------------------|----------------|--------------------|--------------------|
| 1. Problem Statement | Standard | Standard + implementation goal stated | Standard + decision framing | Standard | Standard + subject doc identified |
| 2. Research Design | Standard | Standard | Compressed (2-3 sentences) | Standard | Standard + evaluation methodology noted |
| 3. BLUF | Standard AIMS | AIMS + "implementable in N steps" framing | **Expanded** — executive-ready, primary section | Standard AIMS | AIMS + evaluation verdict |
| 4. Linchpin Assumptions | Standard | Adapted — linchpins are dependency and integration assumptions | Compressed (top 3 only) | Standard | Adapted — subject doc assumptions tested |
| 5. Evidence Summary | Standard | **Expanded** — include code patterns, config examples, API details, parameter tables per source | Compressed (top 5 sources only) | **Expanded** — exhaustive per-source catalog | Adapted — organized by subject doc claim |
| 6. Alternative Hypotheses | Standard | Adapted — alternative implementation approaches compared | Compressed (top 2 alternatives only) | Standard | Adapted — alternative designs the evidence supports |
| 7. Calibrated Uncertainty | Standard | Adapted — confidence per implementation step, not per concept | Compressed (single confidence band) | Standard | Adapted — confidence per evaluation finding |
| 8. Intelligence Gaps | Standard | Adapted — "unknowns an implementer will encounter" | Compressed (top 3 gaps only) | **Expanded** — exhaustive gap catalog | Adapted — gaps that prevent full evaluation |
| 9. Milestones for Revision | Standard | Adapted — "implementation will fail if..." | Compressed (single revision trigger) | Standard | Adapted — "re-evaluate the subject doc when..." |
| 10. Findings/Insights/Recs | Standard 3-tier | **Renamed** — see below | **Renamed** — see below | Standard 3-tier (exhaustive) | **Renamed** — see below |
| 11. DA Due Diligence Register | Standard | Standard | Standard | Standard | Standard |

### Section 10 — Mode-Specific Level Definitions

**Synthesis mode (default):** No change from standard definitions above.

**Implementation Spec mode:**

| Level | Definition | Answers |
|-------|-----------|---------|
| **Finding** | Raw data, documented technical facts, measured parameters | "What is?" |
| **Specification** | Concrete requirement derived from evidence — API call, config value, dependency version, protocol constraint | "What must be built?" |
| **Implementation Step** | Ordered action with prerequisites, expected output, and verification criteria | "How do I build it?" |

**Decision Brief mode:**

| Level | Definition | Answers |
|-------|-----------|---------|
| **Finding** | Raw data, observable facts | "What is?" |
| **Assessment** | Interpreted significance for the decision at hand | "What does this mean for us?" |
| **Recommendation** | ADOPT / REJECT / CONDITIONAL with conditions stated | "What should we do?" |

**Technical Reference mode:** Same level names as Synthesis. Findings are exhaustive (every documented mechanism, not just key ones). Insights cover every inter-mechanism relationship. Recommendations include "areas requiring further research."

**Evaluation Report mode:**

| Level | Definition | Answers |
|-------|-----------|---------|
| **Finding** | Evidence from corpus relevant to subject document claims | "What does the research say?" |
| **Evaluation Result** | Whether the subject document's claim is supported, contradicted, partially supported, or unaddressable | "How does the design hold up?" |
| **Remediation Step** | Specific change to the subject document to align with evidence, ordered by severity | "What should be changed?" |

---

## Completion Gate Adjustments by Mode

All six gates apply to all modes. Modes adjust gate weight, not gate existence.

### Implementation Spec — Gate Adjustments
- **Gate 2 (Survival of Disconfirmation):** Test implementation viability claims, not theoretical hypotheses. "Has the proposed implementation approach been tested against documented failure modes?"
- **Gate 3 (Linchpin Stability):** Linchpins are dependency assumptions. "If dependency X is unavailable or behaves differently than documented, does the implementation plan survive?"
- **Gate 4 (Consensus Through Dissent):** Devil's advocate on approach selection. "Is there a documented alternative implementation approach that the evidence suggests is superior?"
- **Gate 6 (Alexander's Question):** "What evidence would indicate this implementation approach will fail in the target environment?"

### Decision Brief — Gate Adjustments
- **Gates 3, 4:** Reduced weight — note in appendix, do not require full analysis. The brief format prioritizes decision speed over exhaustive rigor.
- **Gate 6:** Advisory — state what would change the recommendation in one sentence.
- The existing **Actionability vs. Delay Tradeoff** (Section "When More Research Is Required") is the primary governing principle for Decision Brief completion.

### Evaluation Report — Gate Adjustments
- **Gate 2:** Applies to the evaluation's own conclusions, not to the subject document. "Has the evaluation itself been tested — could the evidence be interpreted differently?"
- **Gate 6:** "What new evidence would change this evaluation's conclusions about the subject document?"

### Technical Reference + Synthesis
All gates at full weight. No adjustments.

---

## Confidence Language Standards

| Level | Criteria | Signal Language | Approximate Probability |
|-------|----------|-----------------|------------------------|
| **High** | Credibly sourced, consistent across sources, few critical gaps | "almost certainly", "highly likely", "we assess with high confidence" | 80–95%+ |
| **Moderate** | Credibly sourced, plausible, but significant assumptions or gaps remain | "likely", "probably", "we assess" | 55–80% |
| **Low** | Sparse, questionable, or inconsistent evidence; major gaps remain | "possible", "unlikely", "remote" | Below 55% or below 20% for negative claims |

**Do not use bare probability language without a confidence level.** Verbal qualifiers alone are "empty shells" — readers interpret them differently based on their own preconceptions. Pair qualitative language with the probability range.

**Do not express false precision.** "67% probability" implies a level of quantitative rigor the research cannot support. Use ranges.
