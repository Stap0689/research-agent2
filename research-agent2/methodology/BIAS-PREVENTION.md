# Bias Prevention and Devil's Advocate Protocol

## Five Named Biases — Countermeasures Required

Run all five checks during synthesis. Awareness alone is not a countermeasure. Each requires an active structural intervention.

### 1. Confirmation Bias
**Definition:** Searching for, interpreting, or overvaluing information that confirms pre-existing beliefs while dismissing contradictory evidence.
**Risk:** Critical — the single most common cause of research failure.

**Countermeasure — Analysis of Competing Hypotheses (ACH):**
Force transition from confirmation-seeking to systematic disconfirmation. Evaluate each piece of evidence against ALL plausible hypotheses simultaneously. The hypothesis with the lowest inconsistency score — the one that the most evidence is inconsistent with least — is tentatively accepted. You are looking for the hypothesis that survives the most attacks, not the one that accumulates the most support.

**Self-check:** "Have I actively tried to disprove my lead hypothesis, or only to support it?"

---

### 2. Satisficing
**Definition:** Selecting the first identified alternative that appears "good enough" rather than assessing all possibilities.
**Risk:** High — stops synthesis prematurely at a local optimum.

**Countermeasure — Multiple Hypotheses Generation:**
At the outset, use structured brainstorming to generate a full set of mutually exclusive hypotheses before evaluating any of them. Ensure outlier explanations are not dismissed without evaluation. The number of hypotheses considered should exceed the number you expect to survive.

**Self-check:** "Did I generate more than two competing hypotheses before converging?"

---

### 3. Anchoring Bias
**Definition:** Over-relying on the first piece of information encountered, or on a prior analysis, failing to update sufficiently when new data arrives.
**Risk:** High — most dangerous when building on prior research.

**Countermeasure — Bayesian Updating:**
Periodically re-evaluate the problem from scratch rather than updating incrementally. State explicitly: the prior probability before new evidence, the likelihood ratio of the new evidence, and the resulting posterior probability. If a new source significantly shifts the probability but your conclusion hasn't changed, that is a red flag.

**Self-check:** "Is this conclusion the result of updating from a starting point, or has it been stress-tested without that anchor?"

---

### 4. Availability Heuristic (Vividness Bias)
**Definition:** Weighting information based on memorability or emotional salience rather than actual evidential value. Vivid anecdotes outweigh abstract statistics.
**Risk:** Moderate-High — especially dangerous in case study-heavy research.

**Countermeasure — Outside View and Base Rates:**
Prioritize aggregate statistical data and base rates of similar events over single vivid case histories. Explicitly identify "missing evidence" — the dog that didn't bark. The absence of expected evidence is itself evidence and should be weighted accordingly.

**Self-check:** "Am I weighting a compelling anecdote more heavily than base rate data that contradicts it?"

---

### 5. Mirror Imaging
**Definition:** Assuming that others will behave based on the same values, logic, and cost-benefit calculus as the researcher.
**Risk:** High — causes systematic misreading of how actors in different contexts will behave.

**Countermeasure — Red Hat Analysis:**
Model the actual incentive structure and cultural norms of the subject. The question is not "What would I do?" but "How would this specific actor, given their context, most likely respond?" Build their decision model explicitly before projecting outcomes.

**Self-check:** "Have I assumed the subject thinks the same way I do, or have I modeled their actual incentive structure?"

---

## Devil's Advocate Protocol

### When to Invoke — Mandatory in These Scenarios
- Stakes are high: the conclusion will drive a significant decision
- Apparent consensus has emerged without meaningful dissent
- The conclusion confirms what the researcher expected at the outset
- The evidence base is thin (fewer than 3 Tier 1–2 sources on the central claim)

### Four-Phase Method

**Phase 1: Preparation and Role Setting**
1. Precisely articulate the research conclusion or recommendation being challenged — write it out explicitly
2. Commit to authentic dissent — the advocate must present genuine disagreement, not performative criticism. The technique fails entirely when treated as box-checking.

**Phase 2: Decomposition and Deconstruction**
3. Document the mainline judgment and the evidence currently supporting it
4. Identify the assumptions that must be true for the original conclusion to hold — select the most vulnerable and test them
5. Audit the evidence for ignored anomalies, major information gaps, or questionable validity. Ask whether any contradictory data was dismissed as "misleading" or "unimportant"

**Phase 3: Synthesis of the Contrarian Case**
6. Using the same information, develop a distinctly different but well-supported alternative assessment
7. Logical audit: review supporting arguments for faulty logic and causation-correlation confusion. Check for "garden path fallacies" — steps that seem sound individually but lead to an incorrect overall path

**Phase 4: Presentation and Adjudication**
8. Present findings explicitly. Highlight flawed assumptions, poor-quality evidence, and gaps
9. Reassess confidence: does the original conclusion stand, require heavier caveating, or must it change?

### Critical Success Factors
- Avoid binary traps — explore nuanced alternatives, not just the polar opposite
- Avoid smugness — the goal is genuine reflection, not better defense of an entrenched position
- If working solo, explicitly shift cognitive mode before Phase 1; do not begin the devil's advocate immediately after finishing the main analysis

### DA Round Type Catalog

The catalog defines composable round types for DA batteries. Rounds marked ALWAYS form the mandatory floor. Context-dependent rounds are added per the DA Round Expansion Policy in QUESTION-FRAMEWORKS.md.

| Round Type | Purpose | When Mandatory |
|:-----------|:--------|:---------------|
| Logical Fallacy Detection | Identify formal fallacies in claims being evaluated | When evaluating vendor/external party claims |
| Red Hat / Incentive Analysis | Model the incentive structure of the subject actor | When recommendation comes from party with financial/reputational interest |
| Steelman | Present strongest possible version of opposing argument | ALWAYS (confirmation bias prevention) |
| Fix-by-Fix Separation | Granular valid/invalid verdict per recommendation in bundle | When evaluating 2+ recommendations |
| Architectural Fragility | Assess whether problem is environmental or design-level | When proposed fix is environmental and failure mode is architectural |
| Multi-Bias Audit | Check for availability heuristic, anchoring, mirror imaging | ALWAYS (mandatory bias gate before synthesis) |
| Alexander's Question | Define what evidence would overturn the conclusion | ALWAYS (Gate 6 requirement, dedicated round) |
| Verification Protocol | Exact diagnostic steps to collect definitive evidence | When findings inform real-world decisions with operational consequences |

---

## Premortem Analysis

Apply before finalizing any conclusion.

Imagine the analysis has been completed, published, and acted upon — and it turned out to be completely wrong. Work backward to identify specific reasons why.

Ask:
- What was the single most likely cause of failure?
- Which assumption turned out to be false?
- What piece of evidence was given too much weight? Too little?
- Was there a source of information that was not consulted but should have been?

Premortem increases identification of failure modes by approximately 30% compared to standard forward-oriented questioning. It is not optional on high-stakes research.
