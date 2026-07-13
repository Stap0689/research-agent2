# Source Quality Standards

Derived from the Maryland Scientific Methods Scale (MSMS) and standard evidence pyramid.

## 5-Tier Credibility Hierarchy

### Tier 1 — Gold Standard (Score: 5)
Designed to minimize selection bias and establish causation.
- Systematic reviews and meta-analyses (PRISMA-compliant, Cochrane Collaboration)
- Randomized controlled trials with test and control groups
- **Trusted venues:** Nature, Science, PNAS, The Lancet, JAMA, Cochrane Library

### Tier 2 — Structured Observational (Score: 4)
Robust methodologies with some vulnerability to confounding variables.
- Peer-reviewed cohort studies and case-control studies
- Institutional research reports from established standards bodies
- **Trusted venues:** IEEE Transactions, National Academies (NAS/NAE/NAM), RAND Corporation, IARPA, ACM Digital Library
- **AI/ML peer-reviewed conference papers:** NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR — competitive review comparable to journals
- **arXiv preprints with strong corroboration signals** (see arXiv Handling section below)

### Tier 3 — Hypothesis-Generating (Score: 3)
Valuable for pattern identification. Insufficient to establish causation alone.
- Detailed case reports and case series
- Government reports and official standards (NIST frameworks, ICD 203, ISO)
- Established technical journals (Intelligence and National Security, Applied Cognitive Psychology)
- **Preliminary and non-traditional sources — default placement** (arXiv, SSRN, tech research posts, workshop papers, institutional reports, dissertations, IETF informational RFCs). Include; do not exclude. See Preliminary Sources Policy below.

## Preliminary and Non-Traditional Sources Policy

Some high-quality research does not fit the traditional peer-review pipeline — either because the field moves too fast, the venue is non-standard, or formal review hasn't completed yet. Excluding these sources wholesale creates artificial blind spots, particularly in fast-moving AI/ML domains where the most relevant work often hasn't cleared formal review.

**The governing rule applies to all sources in this category equally: Tier 3 by default, upgradeable to Tier 2, confidence ceiling when primary.**

### What Qualifies as Preliminary/Non-Traditional (Do Not Exclude)

| Source Type | Examples | Notes |
|-------------|----------|-------|
| Preprint servers | arXiv, SSRN, bioRxiv, OSF Preprints | Named author + institution required |
| Tech research posts | Google AI Blog, Meta AI Research, DeepMind, Microsoft Research, Anthropic research | Must describe methodology and results, not sell a product |
| Conference workshop papers | NeurIPS/ICML/ICLR/ACL workshops | Lighter review than main track; still selected by program committees |
| Institutional technical reports | MIT CSAIL, Stanford AI Lab, CMU, major national labs | Same as arXiv — credentialed, no formal review |
| IETF RFCs (Experimental/Informational) | RFC documents not on standards track | Standards-track RFCs = Tier 2; experimental/informational = Tier 3 |
| PhD dissertations | From accredited universities with named advisors | Original research; rigorous methodology; not journal-published |
| Standards body working drafts | NIST SP drafts, ISO working drafts before final publication | Institution is unambiguously credentialed — treat as Tier 2; note draft status |

### What Does NOT Qualify (Hard Reject List Unchanged)
This policy does not open the door to: social media, Reddit, YouTube, TikTok, vendor marketing, unattributed content, AI-generated aggregators, or community platforms. Those remain hard rejects with no exceptions.

The distinction: **credentialed author + disclosed methodology** separates this category from the reject list. No author, no institution, no methodology = reject regardless of how it's presented.

### The Three Rules (Apply to All Sources Above)

**Rule 1 — Default tier: Tier 3.**
Treat as preliminary findings — valuable, includable, not the final word.

**Rule 2 — Upgrade to Tier 2 when ALL corroboration signals are present:**
- Named author(s) with affiliation at a recognized institution (major universities, national labs, established research organizations)
- Substantial citation count, high citation velocity, OR corresponding published version in a Tier 1/2 venue
- Methodology is explicit and reproducible

**Rule 3 — Confidence ceiling when these sources are primary evidence:**
When a conclusion rests primarily on preliminary/non-traditional sources — because no published equivalent yet exists — the decision record must:
1. Identify which findings rest on this evidence
2. Cap confidence at **Moderate** (55-80%) maximum — never High
3. Include: *"Primary evidence for [finding] is preliminary or non-traditional research. This reflects the current state of the art in a fast-moving field. Confidence is provisional; conclusions should be revisited as formal peer review validates or challenges these findings."*

This is not a disqualifier. It is honest accounting of where the evidence stands.

### Tier 4 — Expert Elicitation (Score: 2)
Acceptable to fill empirical gaps. Cannot anchor primary conclusions.
- Peer-reviewed expert opinion
- Senior practitioner experience in refereed venues
- Harvard Business Review, Studies in Intelligence (CIA)

### Tier 5 — Anecdotal (Score: 1)
Never sufficient as primary evidence. Context only.
- Single anecdotes, unverified accounts
- Non-peer-reviewed blog posts, vendor marketing materials
- Anonymous or unattributed sources

## Scoring Modifiers
- **+1 Falsifiability bonus:** Source presents testable hypotheses that could be disproven
- **+1 Peer review bonus:** Independent professional scrutiny is documented
- **-1 Timeliness penalty:** Data is outdated or superseded by newer research

## Acceptance and Rejection Criteria

| Decision | Criteria |
|----------|----------|
| **Accept** | Score ≥ 3, with at least 2 Tier 1–2 sources per major claim |
| **Reject** | Score = 1, no identifiable authorship or methodology, self-citing only |
| **Flag for review** | Score = 2 supporting a linchpin assumption — requires corroboration before use |

"Independent" means different authors, institutions, and methodologies. Three sources citing the same original study do not count as three independent sources.

## SIFT Method — Web Source Evaluation

Apply before accepting any web-based source:

1. **Stop** — Do not read or share until source identity is confirmed
2. **Investigate the source** — Use lateral reading: leave the original site and search what others say about its reputation and expertise
3. **Find better coverage** — If a claim seems significant, verify it exists in a higher-tier source
4. **Trace claims to original context** — Follow citations back to primary sources; information stripped of context is unreliable

## Quality of Information Check (Intelligence Community Standard)

Evaluate three dimensions independently:
- **Source Reliability:** Trustworthiness of the origin — track record, independence, access to the information claimed
- **Information Credibility:** Plausibility of the content — consistency with known facts, internal logic, specificity
- **Corroboration:** Whether critical claims have independent verification from a different source with different access

A source can be reliable but carry low-credibility information (a trustworthy source repeating an unverified rumor). Assess both dimensions, not just one.

## Triangulation Requirement

For every major claim, verify it holds across three independent vectors:
1. **Source type diversity** — empirical study + institutional standard + practitioner synthesis
2. **Time diversity** — not all sources from the same period; finding should hold across eras
3. **Methodological diversity** — quantitative + qualitative, or experimental + observational

A claim supported by three sources all using the same methodology is weaker than one supported by two sources using different methodologies.

## Rejected Source Categories

Never use as primary evidence regardless of apparent credibility:
- YouTube, TikTok, or other video platform content
- Social media posts (including LinkedIn, Twitter/X, Reddit)
- Vendor whitepapers with no disclosed methodology
- Press releases without independent corroboration
- Content from sites with undisclosed authorship or funding
