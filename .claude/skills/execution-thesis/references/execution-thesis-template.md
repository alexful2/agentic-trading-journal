# {TICKER} — Execution Thesis (1-12 month horizon)

**Purpose:** Synthesize the mosaic signals in `projects.md` (plus fresh primary-source searches) into 2-4 hypotheses about whether {TICKER} is **actually** executing on management's claimed schedule, on a 1-12 month horizon. Each hypothesis tied to specific signals with 30/60/90-day falsification conditions. Distinct from `_meta.md` (SEC reference data), `projects.md` (signal compilation), `long-game.md` (retired — was 3-5 year strategic speculation), and `stock-deep-dive` (current-price verdict).

**Critical reader-warning:** H2 (Ahead / Undisclosed Scope) is the most exciting frame and the most prone to confabulation. It only appears in this file when 2+ independent Tier-A signals (different agencies or filing types) point at the same undisclosed scope. If H2 is absent below, that's a feature — the gate didn't clear.

**Last refreshed:** {YYYY-MM-DD}
**Primary input:** `vault/companies/{TICKER}/projects.md` (refreshed {YYYY-MM-DD})
**Audit status:** {one of: `unaudited` | `audited {YYYY-MM-DD} — clean, no material corrections` | `audited {YYYY-MM-DD} — corrections folded this refresh` | `audit-failed {YYYY-MM-DD} — H2 retracted, see execution-audit.md` | `audit-failed {YYYY-MM-DD} — structural issues, see execution-audit.md`}

> **For downstream consumers:** If status is `audit-failed … H2 retracted`, treat H2 as not-cleared regardless of what this file says, and prefer the audit's confidence matrix over the section-level confidence rows. If status is `unaudited`, treat H2's gate-clearance as self-asserted and weight it lower than audited H2. If status is `audited … clean` or `corrections folded`, trust the file as written.

**Evidence tiers (strict):**
- **[A]** Direct primary / legal / peer-reviewed records — SEC EDGAR, FDA databases, DOL Form 5500, state procurement / board / contract records, ERCOT/MISO/PJM/etc. interconnection-queue records, PUCT/state-PUC dockets, county building permits, FCC equipment authorizations, executed utility filings, audited financials, and direct peer-reviewed journal / DOI / PMID pages. Press releases and decks are NOT [A].
- **[B]** Direct primary outputs that aren't regulatory filings — earnings transcripts, IR-website content, official company/vendor press releases, careers-page job postings (direct check), USPTO/IP-office filings, government-agenda records.
- **[C]** Secondary reporting on primary signals — mainstream news, AInvest/Substack, interviews surfacing facts, LinkedIn-tracker observations.
- **[D]** Inference / pattern-matching only.

---

## Execution read

**Execution verdict:** {A concise execution-state call, not a stock verdict. Example: "Contracted buildout is tracking; the open risk is commercialization of the unleased expansion pipeline."}

**Most likely hypothesis posture:** {Name the dominant hypothesis / combined posture, e.g. "H1 is dominant, with a medium-strength H3 overlay around financing runway."}

**What changed / what is newly clarified:**
- {2-5 bullets. Prioritize findings that were not already obvious from the previous thesis, or corrections that materially sharpen the read.}
- ...

**Evidence that drove the read:**
- {The 3-5 load-bearing facts a human should inspect first, with terse source references.}
- ...

**What this means for downstream work:** {One concise sentence for deep-dive / pre-earnings users.}

---

## Schedule baseline

{What management has publicly committed to delivering in the next 1-12 months. Pull from _meta.md, recent prints, IR commentary, and projects.md stage gates. List the dated commitments + the forward-language commitments separately.}

**Dated commitments (next 1-12 months):**
- {Project / milestone} — {date} — source: {filing or PR}
- ...

**Forward-language (not committed, but implied by mgmt):**
- {Item} — {what mgmt has said, with hedge language preserved}
- ...

---

## Signal gap inventory

For each upcoming gate or milestone in the 1-12 month window, classify what the mosaic substrate supports.

| Gate / milestone | Date claimed | Signal status | Notes |
|---|---|---|---|
| {gate 1} | {date} | confirmed by independent signals / inferred from mgmt only / contradicted by signals / signals exceed disclosure / signal gap | {1-line reason} |
| {gate 2} | ... | ... | ... |

**This is the substrate the hypotheses synthesize over.** Items in "signals exceed disclosure" are the H2 candidate signals. Items in "contradicted by signals" are H3 candidates. Items in "signal gap" feed Round 1 fresh searches at next refresh.

---

## Hypothesis 1 — On Schedule (REQUIRED)

**Description.** {2-3 sentences. The boring base case: independent signals match management's claimed schedule. State which gates are most cleanly confirmed.}

**Evidence supporting:**
- [A] {primary regulatory filing — URL}
- [A] ...
- [B] {company/vendor PR, IR deck, careers-page entry, etc. — URL}
- [B] ...
- [C] {secondary if cited}
- [D] Inference: {explicit acknowledgment if any}

**Evidence mix:** {X Tier A, Y Tier B, Z Tier C, W inference}

**Confidence:** {HIGH | MED-HIGH | MEDIUM | MEDIUM-LOW | LOW}

**What would falsify in 30/60/90 days:**
- 30 days: {specific dated signal whose absence/presence would weaken H1}
- 60 days: {another}
- 90 days: {another}

**What to watch:**
- {specific upcoming primary-source signal}
- ...

---

## Hypothesis 2 — Ahead / Undisclosed Scope (CONDITIONAL — strict gate)

{If H2 not proposed this refresh, replace this entire section with:

> **H2 not proposed this refresh.**
>
> The strict gate (2+ independent Tier-A signals pointing at the same undisclosed scope) was not cleared. The closest candidate signal was {description with primary-source URL}, but {what corroborator is missing}. The candidate signal has been added to the 30/60/90-day watch list so the next refresh checks for the missing corroborator.

If H2 IS proposed, the section follows the full hypothesis shape:}

**Description.** {2-3 sentences. Specifically what's the undisclosed scope — unannounced customer, capacity expansion, geographic entry, capability buildout. Be precise about what management has and has NOT said.}

**The 2+ independent Tier-A signals supporting (gate verification):**
- [A] {Tier-A signal #1, with URL — name the agency / filing type}
- [A] {Tier-A signal #2, with URL — name a DIFFERENT agency / filing type}
- {explicitly state how the two signals are independent}

**Additional supporting evidence (Tier B and below):**
- [B] {supporting evidence — URL}
- ...
- [D] Inference: ...

**Evidence mix:** {X Tier A, Y Tier B, Z Tier C, W inference} — confirms ≥2 Tier A

**Confidence:** {LOW | MEDIUM | MED-HIGH — note H2 confidence cannot exceed MED-HIGH; the gate proves the signal exists, not that it predicts the outcome}

**What would falsify in 30/60/90 days:**
- 30 days: {specific signal that would refute the undisclosed-scope reading}
- 60 days: ...
- 90 days: ...
- **What would confirm:** {what announcement / filing would publicly disclose the scope this hypothesis is naming?}

**What to watch:**
- {specific upcoming primary-source signal}

---

## Hypothesis 3 — Behind / Schedule Slip (REQUIRED)

**Description.** {2-3 sentences. Independent signals lag management's claimed schedule. Be specific about which gates are at risk and what signals are missing or contradicting.}

{If signals don't support a slip narrative this refresh, write:

> No slip indicators surfaced this refresh. {Brief reason — e.g., "every dated commitment in the next 90 days has at least one Tier-A independent corroborator." OR "the schedule's first slip-vulnerable gate is {date}, which is too far out for current signals to test."} The discipline of forcing this section is to confirm the look was made, not to manufacture a finding.

If signals DO support slip, follow full hypothesis shape:}

**Evidence supporting:**
- [A] {primary regulatory filing showing lag — URL}
- [B] ...
- [D] Inference: ...

**Evidence mix:** {X Tier A, Y Tier B, Z Tier C, W inference}

**Confidence:** {HIGH | MED-HIGH | MEDIUM | LOW}

**What would falsify in 30/60/90 days:**
- 30 days: {what announcement / signal would disconfirm the slip reading}
- 60 days: ...
- 90 days: ...

**What to watch:**
- {specific upcoming primary-source signal}

---

## Hypothesis 4 — Pivot / Off-Roadmap (OMIT entirely if no Tier B+ evidence)

{Only include if Tier B+ signals support. Don't manufacture pivots. If omitted, omit the entire section header — don't write "no pivot evidence" placeholder.}

**Description.** {2-3 sentences. Capex or capability-build flowing toward something diverging from stated strategy. Distinct from H2 (more of disclosed, ahead) — H4 is different from disclosed.}

**Evidence supporting:**
- [B] {senior hire whose background doesn't match disclosed roadmap, with URL}
- [B] {trademark filing for product outside disclosed line, with URL}
- [B] {job postings for skill-sets not in stated business model, with URL}
- ...

**Evidence mix:** {X Tier A, Y Tier B, Z Tier C, W inference}

**Confidence:** {HIGH | MED-HIGH | MEDIUM | LOW — note H4 typically caps at MEDIUM without Tier A signals}

**What would falsify in 30/60/90 days:**
- 30 days: ...
- 60 days: ...
- 90 days: ...

**What to watch:**
- ...

---

## Cross-hypothesis evidence overlap

{Required even when overlap is minimal. Lists every evidence row that is materially the same fact across hypotheses with different framings.}

| Fact / signal | H1 frame | H2 frame | H3 frame | H4 frame |
|---|---|---|---|---|
| {fact 1} | {how H1 reads it} | {how H2 reads it, or "—"} | {how H3 reads it} | {how H4 reads it, or "—"} |
| {fact 2} | ... | ... | ... | ... |

{If no material overlap: write "No material overlap detected this refresh — each hypothesis's evidence rows are factually distinct."}

**Implication for confidence:** {if H1 and H3 share 3+ rows in the table, both must explicitly acknowledge that on-schedule and slip readings are interpreting the same operational substrate from different posture assumptions. If a hypothesis's de-duplicated evidence base is materially smaller than its raw count, drop confidence half a tier.}

---

## 30/60/90-day watch list

The falsification register. Concrete, dated signals to look for in the next 30/60/90 days that would confirm or refute the hypotheses above. This is the single most actionable section for setting up the next refresh.

| Window | Signal to watch | Where to find it | What it would confirm/refute |
|---|---|---|---|
| 30 days | {specific signal} | {primary source — agency / filing type / URL pattern} | {which hypothesis it tests} |
| 30 days | ... | ... | ... |
| 60 days | ... | ... | ... |
| 90 days | ... | ... | ... |

{Aim for 6-10 entries total across the three windows. Concrete > comprehensive — a signal in this list must be specific enough that the next refresh can definitively check whether it happened.}

---

## Caveats / Methodology

- **This is execution synthesis, not prediction.** Confidence describes evidence quality, not outcome probability.
- **Stale-source bias.** Tier C signals older than 6 months should be flagged or dropped. Mosaic data decays fast.
- **Management-statement reliability.** Mgmt commentary is Tier B but reflects mgmt's incentive to paint the most favorable schedule. Independent signals (Tier A from agencies, Tier B from vendor counterparties) carry more weight when they conflict with mgmt.
- **H2 confabulation risk is the highest single risk in this file.** The strict 2+ independent Tier-A gate is non-negotiable. If you find yourself wanting to propose H2 with weaker evidence, don't.
- **Pattern-matching across hires/trademarks/job postings is Tier D inference** even when the underlying signals are Tier A facts. The interpretation is the leap, not the underlying signal.

---

## Sources

| Hypothesis | Anchored in |
|------------|-------------|
| H1 On Schedule | {primary-source URLs} |
| H2 Ahead / Undisclosed | {2+ independent Tier-A URLs explicitly listed; or "not proposed this refresh"} |
| H3 Behind / Slip | {primary-source URLs; or "no slip indicators surfaced"} |
| H4 Pivot / Off-Roadmap | {primary-source URLs; or hypothesis omitted} |

Linked files for cross-reference: [[_meta]] · [[overview]] · [[projects]] · [[insider-activity]]

---

## Refresh log

- {YYYY-MM-DD} — {Initial build / refresh}. {1-2 sentences: what projects.md state was synthesized from, what fresh searches Round 1 ran.}

(On every refresh after the first, include `### What changed since last refresh ({prev YYYY-MM-DD} → {this YYYY-MM-DD})`):

  - **Hypothesis confidence shifts:** {hypothesis} {OLD → NEW} ({reason})
  - **H2 gate status change:** {if H2 cleared the gate this time but not last refresh, or vice versa, explain why}
  - **Watch-list resolution:** {which 30/60/90-day items from the prior refresh resolved, and what they confirmed/refuted}
  - **New evidence rows:** {count} added across {hypothesis names}
  - **Retracted claims:** {what and why}

(Omit bullets that don't apply this refresh — don't write "none.")

---

## What's NOT yet captured

- {Channels not pulled this refresh — e.g., satellite imagery, county commissioner agendas, transformer-vendor press releases. Each line a candidate for next refresh's Round 1.}
- {Signals deferred for cost/complexity reasons.}
- {Load-bearing management claims still lacking independent substrate — e.g., study counts without DOI/PMID quality scoring, public-sector plan counts without state records, adoption claims without benefit-guide diffs/removal checks.}
- {Open questions surfaced by Round 1 searches that didn't get follow-up.}
