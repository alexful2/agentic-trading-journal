# {TICKER} execution-thesis.md — Audit

**Subject file:** `vault/companies/{TICKER}/execution-thesis.md` (refreshed {YYYY-MM-DD})
**Audit date:** {YYYY-MM-DD}
**Source model:** {what wrote the source — Claude / GPT / etc.}
**Audit model:** {what's running this audit — should differ from source}
**Method:** Round 1 fresh primary-source verification ({N} targeted searches, weighted toward H2) + Round 2 whole-document structural pass.

---

## Verdict in one paragraph

{Self-contained summary. Lead with H2 gate status:
- "H2 was proposed at synthesis and the audit independently verified both Tier-A signals — gate stands."
- "H2 was proposed but one of the two Tier-A signals failed audit verification — H2 retraction recommended for next refresh."
- "H2 was correctly not proposed; the closest-candidate signal {X} remains too thin."

Then state whether H1/H3/H4 confidence levels match audit findings, and the 1-2 most consequential corrections elsewhere.}

---

## Round 1: Fresh primary-source corrections

{For each consequential claim verified, present the original claim, the corrected claim if different, and the primary-source URL. H2 evidence rows are ALWAYS individually verified in this section even if no correction surfaces.}

### H2 gate verification (priority — always included if H2 is in source)

- **Tier-A signal #1:** {claim} → {audit result: verified at URL / not found at URL / says something different / URL broken}
  - Source citation: {URL from execution-thesis.md}
  - Audit verification: {fresh search result with URL}
- **Tier-A signal #2:** {claim} → {audit result}
  - Source citation: {URL}
  - Audit verification: {fresh search result}
- **Independence check:** {confirm signals are from different agencies / filing types — or flag if not}

**Gate result:** {PASS / FAIL — if FAIL, retraction recommendation goes in §Recommendations}

### Other Round 1 corrections

#### Correction 1: {short title}

- **Source claim:** {direct quote or paraphrase, with section reference}
- **Corrected claim:** {what the primary source actually says}
- **Primary source:** {URL}
- **Hypothesis affected:** {H1 / H2 / H3 / H4}
- **Confidence impact:** {brief reason}

#### Correction 2: ...

{If Round 1 found no corrections beyond gate verification, state explicitly: "Round 1 verified all consequential claims beyond the H2 gate; no factual deltas surfaced."}

---

## Round 2: Structural findings

{Include only subsections with findings. Omit subsections where the source is clean.}

### 2a. H2 gate compliance

{Walk the gate-compliance checks from Step 4a:
- 2+ Tier-A signals cited?
- Different agencies / filing types?
- Independence explicitly stated?

If H2 is absent: verify the "H2 not proposed this refresh" note exists with a concrete closest-candidate description, and confirm the candidate is on the watch list.}

### 2b. Cross-hypothesis evidence overlap

{Build the overlap table for facts cited in 2+ hypotheses. Compare against the source's own overlap section. Flag any overlaps the source missed.}

| Fact | H1 frame | H2 frame | H3 frame | H4 frame | In source's overlap section? |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | yes / no |

**Confidence implication:** {if H1 and H3 share 3+ rows and neither acknowledges the same-substrate issue, recommend the half-tier confidence drop the skill spec requires}

### 2c. Tier-laundering

{List rows where cited tier doesn't match cited source's actual tier.}

| Row (location in source) | Cited tier | Cited URL | Recommended tier | Why |
|---|---|---|---|---|
| ... | [A] | press release URL | [B] | press release is not a regulatory filing |

### 2d. Inference cited as fact

{Narrative claims in Description sections not grounded in Tier-D inference rows. Quote the claim, then note the missing inference acknowledgment.}

### 2e. Hire / role / status verification

{Claimed roles, employers, partnerships, statuses without primary corroboration.}

### 2f. Schedule baseline accuracy

{Flag if mgmt commitments are paraphrased in ways that strip hedge language. The source should preserve "expected in Q3 CY26" as forward-language, not promote to "Q3 CY26 commitment."}

### 2g. 30/60/90-day watch list specificity

{Watch-list signals concrete enough to definitively check next refresh? Flag vague entries.}

---

## Updated confidence / gate matrix

| Hypothesis | Source state | Audit-recommended | Why |
|---|---|---|---|
| H1 On Schedule | {source confidence} | {audit confidence — "unchanged" is fine} | {brief reason} |
| H2 Ahead / Undisclosed | {gate cleared / not proposed} | {gate verified / gate fails on audit / correctly omitted} | {which Tier-A signal failed verification, if any} |
| H3 Behind / Slip | ... | ... | ... |
| H4 Pivot | ... (or N/A if not in source) | ... | ... |

---

## Recommendations

### For the next execution-thesis refresh on this ticker

{Concrete corrections to fold in. If the audit failed the H2 gate, **H2 retraction must be the FIRST bullet.**}

- ...

### For the execution-thesis skill itself

{Optional. Only include if the audit surfaced a pattern likely to appear across multiple tickers. Most audits won't produce skill-level recommendations. If nothing skill-level surfaces, omit this subsection entirely.}

---

## Sources

- Subject: `vault/companies/{TICKER}/execution-thesis.md` (refreshed {YYYY-MM-DD})
- Round 1 primary-source URLs:
  - {URL 1} — {what was verified, hypothesis it relates to}
  - {URL 2} — ...
- Cross-referenced dossier files:
  - `vault/companies/{TICKER}/projects.md` (signal-provenance check)
  - `vault/companies/{TICKER}/_meta.md` (SEC-filed-facts check)
  - {others if used}
