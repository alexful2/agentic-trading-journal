---
name: execution-thesis
description: >
  Build or refresh a 1-12 month execution-thesis file at
  `vault/companies/TICKER/execution-thesis.md`. Reads `projects.md` (mosaic
  signal layer) as primary input + pulls fresh oddly-specific primary sources,
  then synthesizes 2-4 hypotheses about what management is **actually** doing
  vs. what they say: On Schedule / Ahead-or-Undisclosed / Behind / Pivot.
  Every hypothesis tied to specific signals from projects.md or fresh searches,
  with 30/60/90-day falsification conditions. Tightly coupled to
  `company-projects` (data layer) and `stock-deep-dive` (consumer). Distinct
  from deep-dive's 3-advisor council — that runs at current-price horizon;
  this runs at execution-verification horizon. Manual refresh on demand.
  Usage: "execution-thesis VRT" or "refresh execution-thesis on VRT".
---

# Execution Thesis

## Purpose

Synthesize the oddly-specific mosaic signals collected by `company-projects`
into 2-4 falsifiable hypotheses about whether the company is **actually**
executing on management's claimed schedule, on a **1-12 month horizon**.

The question this file answers:

> *Given the public mosaic of permits, grid filings, satellite, freight,
> hiring, and vendor signals — is what's happening on the ground consistent
> with what management says is happening, and is anything happening that
> management hasn't disclosed yet?*

This is **not** the 3-5 year strategic-pattern question. That horizon was
mostly redundant with `stock-deep-dive`'s council. The 1-12 month
execution-verification question is what the user's mosaic source-bucket list
naturally answers, and what neither deep-dive nor projects.md alone produce:
- `company-projects` collects raw signals into a structured stage-gate file —
  *what's happening, by signal*
- `execution-thesis` reads those signals and asks *what does it all mean,
  and is mgmt telling the truth* — synthesis layer
- `stock-deep-dive` uses both as inputs for the current-price decision

## Why a separate skill (not folded into projects.md or deep-dive)

- **Not folded into `company-projects`:** projects.md is signal compilation
  with explicit source citations. Mixing synthesis into that file would blur
  the data/interpretation line. Keeping them separate means projects.md stays
  a clean, citable substrate that this skill (and others) can read without
  having to peel synthesis off the top.
- **Not folded into `stock-deep-dive`:** deep-dive runs on current-price-
  decision horizon (will I hold/add/reduce today). Execution-thesis runs on a
  longer horizon (is this buildout real over the next 1-12 months) using
  signal types deep-dive doesn't pull (county permits, satellite, freight,
  vendor refs, fiber records). The output is a structured input *to*
  deep-dive, not a duplicate of it.

## When to use

- After a `company-projects` refresh on the same ticker (the natural pair —
  fresh signals → fresh synthesis)
- Before a major print where execution status will be tested (Q3/Q4 earnings,
  capacity-update calls)
- When management announces a new schedule or scope (verify the announcement
  is consistent with on-the-ground signals)
- Quarterly default cadence; faster on event-driven triggers

Do **not** run on Tier-1 names that already have a fresh deep-dive (<7 days)
unless `projects.md` has materially updated. Doing so just rephrases what
deep-dive already covered.

Do **not** auto-build for tickers without a consumer. Build when the user
asks or when downstream skill (deep-dive, pre-earnings) flags the absence.

## Prerequisites

- **`vault/companies/TICKER/projects.md` must exist and be <60 days old.**
  This is the primary input. If missing or stale, **stop and recommend
  running `company-projects` first.** Don't synthesize off thin air.
- **`vault/companies/TICKER/_meta.md` must exist.** Read for industry +
  business model + named projects baseline.
- Helpful but optional: `overview.md`, `financials.md`, `leadership.md`.

If projects.md is missing, the skill cannot run. The signal layer must
exist before the synthesis layer.

## Web search

Required. Even though projects.md provides the substrate, this skill must
also pull **fresh primary sources** to:
- Verify the highest-leverage projects.md signals
- Fill signal gaps for hypothesis evaluation (especially H2 — see Step 5a)
- Catch news that landed *after* the projects.md refresh

Prefer `mcp__claude_ai_Exa__web_search_exa` (project standard). Fall back to
`WebSearch` if Exa MCP isn't exposed. Preserve URLs in cited evidence rows.

**Token budget:** the user has explicitly stated that this skill is valued for
**depth**, not efficiency. Corner-cutting on searches is a documented failure
mode (see `feedback_mosaic_research_depth.md`) — the 2026-05-11 VRT refresh
ran only 9 searches and missed the $11.9B commitments cliff, the Nostrum price
(EUR 165M), the ATM dilution math, and the Goldman/JPM commitment-letter-vs-
closed-financing distinction, because the agent cited the 10-Q as a Tier-A
anchor without opening and extracting from it.

**Round 1 target: 15-30 fresh searches across multiple ≤5-parallel batches.**
Cover the full set of channels named in projects.md, not just the headline 4-8.
The required channels are the ones in the Variable Map and Search Coverage Ledger,
not a universal VRT/GEV channel list. Always include direct SEC/source-filing
extraction for public companies, then select the pattern-specific channels that
match the ticker:

1. **Pull the most recent 10-K, 10-Q, and material 8-Ks directly.** Open the
   filings (not press release summaries). Extract: commitments balances, share
   counts at the most recent date (not the prior 10-Q's date), ATM/shelf
   activity, contract specifics (payment terms, vesting triggers, expiry
   dates, tranche structure, conditions precedent), financing-letter-vs-closed
   distinctions. This is the single highest-leverage source and the most-
   commonly-skipped one.
2. **Physical buildout channels** when that pattern is claimed: lane-specific
   freight/permit searches, county records by name, TDLR/TCEQ equivalents,
   state PUC / utility dockets, site-specific hiring, vendor/EPC press, local
   site press, satellite imagery, and international regulatory equivalents for
   non-US sites.
   If the Search Coverage Ledger shows all direct site-verification channels
   (permits / utility dockets / environmental records / deed records /
   satellite / EPC or lien records) as `Defer`, say so in Signal Gap Inventory.
   In that case, H1 may still be MED-HIGH on SEC/customer evidence, but cannot
   be HIGH on physical-buildout execution until at least one real independent
   physical channel verifies the construction state.
3. **Hyperscaler / single-customer concentration channels** when claimed:
   counterparty earnings-call mentions, customer-side filings, lease amendments,
   exclusivity terms, provider-diversification signals, and counterparty credit
   signals.
4. **Enterprise SaaS adoption channels** when claimed: split by route rather
   than treating adoption as one flat bucket. For private self-insured employers,
   use DOL Form 5500 / BenefitsLink, employer benefit guides, and open-enrollment
   PDFs. For public sector, use state benefit guides, procurement awards, board
   packets, contract registers, open-enrollment PDFs, and vendor directories
   (Form 5500 generally is not the public-sector channel). For
   partner-distributed lives, use payer/TPA/PBM member guides and plan-specific
   directories. Broker decks and partner press are discovery channels unless
   they contain direct member-facing or employer-specific records.
5. **Clinical credibility / regulated rollout channels** when claimed: PubMed
   / journal pages with quality scoring (DOI/PMID, journal, funding/conflicts,
   sample size, comparator, follow-up, endpoint quality, study type),
   ClinicalTrials.gov, FDA 510(k) / MAUDE / recall / AdComm / warning-letter
   databases, state board actions, peer-reviewed conference abstracts, patent
   filings, and direct certification registries.
6. **Engagement / utilization channels** when claimed: app-rank/review metrics,
   member/eligible-life disclosures, case-study utilization data, traffic/app
   telemetry, benefit-guide removals / year-over-year diffs, client retention,
   NDR/RPO/deferred revenue, sessions/member, completed-session yield, and
   customer-success / implementation / clinical-ops hiring. For products where
   users can graduate, app retention is not the same as account durability.
7. **Capital structure / post-IPO / restructuring channels** when claimed:
   shelf/ATM/convert filings, debt covenants, TRACE/bond data, Form 4/Form 144,
   10b5-1 plan changes, lockup/RSU schedules, bankruptcy-court filings, and
   post-emergence contract disputes.

If a channel is truly inapplicable to this ticker, state that explicitly in
the file rather than silently skipping. The discipline is "every channel
named in projects.md was tested," not "the first 8 channels that returned
something."

**Load-bearing deferred channels.** If a claimed bull case depends on a count
or channel that has not been independently pulled (for example, "21 studies,"
"24 state plans," "5M public-sector employees," or "no churn/removals"), hard-
flag that in Signal Gap Inventory, Execution read, and What's NOT yet captured.
Do not let a `searched` map read as `mature` simply because the surface was
visited once.

**Parallel cap remains ≤5 searches per tool-call batch** (per
`parallel_tool_call_cap.md`). Run 4-6 batches sequentially.

## Workflow

### Step 1: Load context

**Map maturity gate (FIRST check, before any other reads).** Read the Variable Map section
at the top of `vault/companies/TICKER/projects.md` and check its `Map maturity` header value:

- **`draft`** → **STOP.** The Variable Map exists but no real channel searches have been run yet.
  Refuse to produce an execution-thesis off a draft-only map — the synthesis would be thin or
  confabulated. Surface to the user: "projects.md Variable Map is `draft` (no channels searched).
  Run `company-projects TICKER` to upgrade to `searched` before running execution-thesis."
- **`searched`** → Proceed. At least one real search batch has been run per active variable.
- **`mature`** → Proceed. Map has been audit-confirmed across ≥1 quarter of refreshes.

If the projects.md file exists but has no Variable Map (legacy structure before the Variable Map
Step 0 was added to `company-projects`), prompt the user to run `company-projects TICKER` first to
build the map. Do not proceed without one.

Read in order:
1. `vault/companies/TICKER/projects.md` — primary input. **Read the Variable Map first** — it
   defines the binding constraints, bull/bear tells per variable, and the patterns this company
   exhibits. Hypothesis frames (H1/H2/H3/H4) stay constant, but the schedule baseline rows and
   evidence rows should be organized AROUND the variables when relevant. The Search Coverage Ledger
   tells you which channels were tested-and-empty vs. never-tested — both inform "signal gap"
   classifications in Step 3.
2. `vault/companies/TICKER/_meta.md` — for management's claimed schedule
   baseline (recent prints, guidance, IR commentary)
3. `vault/companies/TICKER/overview.md` — business model context
4. (optional) `vault/companies/TICKER/leadership.md` if hiring is one of the
   key signal channels
5. **`vault/companies/TICKER/execution-thesis.md` (prior version, if it exists)** —
   the file this refresh is about to overwrite. Required for the refresh log's
   "What changed since last refresh" delta. Extract: prior hypothesis confidences,
   prior H2 gate status, and the prior 30/60/90-day watch list (so resolution can
   be tracked).
6. **`vault/companies/TICKER/execution-audit.md` (if it exists)** — the audit of
   the prior thesis. Required so this refresh folds in audit corrections rather
   than re-asserting the prior framing. Extract: Round 1 factual corrections,
   Round 2 structural findings, the updated confidence/gate matrix. The new
   thesis must reflect these corrections; cite the audit explicitly in the
   refresh log under "Retracted claims" or "Hypothesis confidence shifts."

Do **not** read every file in the dossier. Selective reads only.

If items 5 or 6 are absent, this is the first build (or audit hasn't run yet) —
proceed without a delta entry in the refresh log.

### Step 2: Extract management's claimed schedule

From the dossier `_meta.md` and projects.md stage-gate table, write down:
- What management has publicly committed to delivering in the next 1-12
  months (energizations, contract handoffs, capacity additions, project
  milestones)
- The dates management has committed to
- What management is implying but not committing to (forward language,
  guidance ranges)

This becomes the **schedule baseline** that hypotheses test against.

### Step 3: Cross-check projects.md signals against the schedule

Walk through projects.md's stage gates and signals. For each gate or
milestone in the next 12 months, classify:
- **Confirmed by independent signals?** (e.g., a county permit, ERCOT
  filing, vendor PR, or satellite imagery supports the claimed status)
- **Inferred only from management?** (only mgmt-source statements; no
  independent confirmation)
- **Contradicted by signals?** (independent source suggests different status)
- **Signals exceed disclosure?** (signals point at scope or projects mgmt
  hasn't talked about)
- **Signal gap?** (no public substrate exists yet — too early or channel
  not pulled)

Build a mental inventory before going to Round 1 search. The Round 1
queries are aimed at filling the most consequential gaps.

### Step 4: Round 1 — Fresh primary-source searches (15-30 queries minimum)

See "Token budget" section above for the channel coverage requirement and
the 10-Q/10-K direct-extraction rule. The 4-8 query cap is retired; corner-
cutting on this step is the documented failure mode for this skill.

Search to verify the most consequential gates and to fill the gaps from
Step 3. Cover the primary channels named in the Variable Map and any high-priority
`Defer` rows in the Search Coverage Ledger. If a channel returns nothing, record
that in the thesis as a signal gap or "searched-empty" fact rather than silently
skipping it.

**Parallel cap:** ≤5 searches per tool-call batch.

Cite every fresh signal with a primary-source URL. Each fresh signal
becomes a candidate evidence row in Step 5.

### Step 5: Synthesize hypotheses

Build hypotheses against the schedule baseline from Step 2, using signals
from projects.md + Round 1 fresh searches.

**Hypothesis frames:**

#### H1 — On Schedule (REQUIRED, always present)

The boring base case. Independent signals match management's claimed
schedule. Permits filed when expected, equipment arriving on cadence,
hiring scaling at the right sites, satellite shows construction at
expected pace.

This is the null hypothesis. Always include it even if signals are
weak — the absence of confirmation is itself the question H3 raises.

#### H2 — Ahead / Undisclosed Scope (CONDITIONAL — strict gate, see Step 5a)

Signals exceed what management has publicly disclosed. Possible early
indicators of:
- An unannounced customer contract about to land
- A capacity expansion not yet announced
- A new site or geographic entry not yet announced
- Equipment being procured for a use case not in the disclosed roadmap

This is the highest-value hypothesis output mode but also the most
confabulation-prone. **See Step 5a for the strict evidence gate.**

#### H3 — Behind / Schedule Slip (REQUIRED, always present)

Signals lag management's claimed schedule. Mgmt may not have admitted
slip yet. Possible shapes:
- Permits not filed by the date they'd need to be for stated delivery
- Equipment not yet ordered or in transit
- Hiring at the site is anemic vs. the claimed buildout pace
- Construction-pace satellite imagery doesn't match claimed phase
- Vendor counterparties haven't issued matching press releases

Always include even if signals don't support it. State explicitly: "no
slip indicators surfaced this refresh" if that's the conclusion. The
discipline is forcing a look, not forcing a finding.

#### H4 — Pivot / Off-Roadmap (CONDITIONAL — Tier B+ evidence required)

Capex or capability-build flowing toward something that diverges from
the stated strategy. Distinct from H2 (which is "more of what's
disclosed, ahead of schedule") — H4 is "different from what's
disclosed."

Examples: senior hires whose backgrounds don't match the disclosed
roadmap; trademark filings for products outside the disclosed product
line; job postings for skill-sets that don't fit the stated business
model; vendor relationships with companies in adjacent industries.

Include only if Tier B+ evidence supports. Don't manufacture pivots
from a single ambiguous signal.

#### What's gone vs. old long-game

The Base/Bull/Bear/Wild Card structure was 3-5 year strategic
speculation. Bull and Bear at that horizon largely duplicated deep-
dive's council. The new H1-H4 frames are bounded to 1-12 months and
specific to whether management is executing as claimed — a distinct
question from "what is this company quietly becoming."

### Step 5a: H2 strict-evidence gate (REQUIRED before proposing H2)

H2 (Ahead / Undisclosed) is the most exciting hypothesis frame and the
most likely to anchor a decision. It's also the easiest to confabulate —
every loose signal can be retrofitted into "they're secretly building X."

**Strict gate: H2 may only be proposed if 2+ independent Tier-A signals
point at the same undisclosed scope.**

Tier-A signals here means SEC filings, primary regulatory filings (ERCOT
interconnection queue, county building permit, PUCT docket, FCC
authorization, etc.), or executed permits/utility filings on agency
websites. Press releases, decks, and interviews are Tier B and **don't
count toward the H2 gate** — those are management-side sources, and the
whole point of H2 is to detect what management isn't saying.

**Independence check:** the two Tier-A signals must come from different
agencies or different filing types. A county permit + an ERCOT load
study at the same site = independent. Two ERCOT filings on the same
docket = not independent.

If the gate is not cleared:
- Do not propose H2.
- Add a note in the file: "H2 not proposed this refresh — fewer than 2
  independent Tier-A signals support an undisclosed-scope reading. The
  closest candidate signal was {X}, but {missing corroborator}."
- Add the candidate signal to the 30/60/90-day watch list so the next
  refresh checks for the missing corroborator.

This is the highest-stakes discipline in the skill. Loose H2 claims
will anchor user decisions and erode the skill's credibility. When in
doubt, don't propose.

### Step 6: Score evidence — required structured shape

Same evidence-tier discipline as `company-projects` and the prior
`long-game` v3 spec. Each hypothesis includes:

```markdown
**Evidence supporting:**
- [A] {primary regulatory filing — SEC, ERCOT, county permit, etc., with URL}
- [A] ...
- [B] {company PR, vendor PR, IR deck, careers page direct, etc.}
- [C] {secondary news / Substack / mainstream coverage of a primary signal}
- [D] Inference: {explicit acknowledgment}

**Evidence mix:** X Tier A, Y Tier B, Z Tier C, W inference
```

**Tier definitions:**
- **[A]** Direct primary / legal / peer-reviewed records - SEC EDGAR, FDA
  databases, DOL Form 5500, state procurement / board / contract records,
  ERCOT/MISO/PJM/etc. interconnection-queue records, PUCT/CPUC/state-PUC
  dockets, county building permits, executed utility filings, FCC equipment
  authorizations, TDLR/TCEQ-equivalent state filings, audited financials, and
  direct peer-reviewed journal / DOI / PMID pages. Press releases and decks are
  NOT [A].
- **[B]** Direct primary outputs that aren't regulatory filings — earnings
  call transcripts, IR-website content, official company press releases,
  vendor press releases, careers-page job postings (direct check), USPTO/
  national-IP-office trademark/patent filings, government records like
  county commissioner agendas (when the agenda itself is the source).
- **[C]** Secondary reporting on primary signals — mainstream news,
  AInvest/Substack/Motley-Fool summaries, interviews surfacing facts,
  LinkedIn-tracker observations, third-party fan sites.
- **[D]** Inference / pattern-matching only.

**Citation hygiene:** A row may wear `[A]` only when the cited URL itself is the direct primary
source (SEC/FDA/agency/peer-reviewed journal), not a mirror, aggregator, or media summary of that
source. Mirrors may be used for discovery, but once the fact is promoted into `[A]`, replace the
mirror with the direct primary URL or downgrade the row.

**Pre-write `[A]`-row gate (REQUIRED — quarterly-review calibration).** A
recurring `execution-audit` finding is the *same* defect class across builds:
tier-laundering (rows marked `[A]` that actually cite a mirror/media URL) and
un-extracted or mis-extracted primary figures (a client count rounded instead
of quoting the filed number, a capex line misread, an ATM draw double-counted,
a convertible conversion price left blank when the filing states it). Because
it recurs, it is enforced here as a gate, not left to per-run discipline.
**Before writing the file, walk every `[A]` row and confirm both hold; if a
row fails either test, fix it or downgrade it to `[B]/[C]` — do not write an
`[A]` row that hasn't passed:**

1. **Direct primary URL.** The cited link resolves to the SEC/FDA/agency/
   peer-reviewed-journal document itself (e.g. `sec.gov` / `data.sec.gov`,
   `fda.gov`, the PUC/ERCOT docket, the county permit portal, a DOI/PMID
   page) — not a press release, aggregator, Substack, or news write-up *about*
   that document. A mirror used for discovery must be replaced with the direct
   URL before the row earns `[A]`.
2. **Extracted filed figure.** The row quotes the *specific number/date/term
   as filed* (balance, share count at the most recent date, capex line,
   conversion price, tranche/expiry), not a rounded approximation or a
   secondary-source paraphrase. "~3,000" when the 10-Q says 2,849 is a fail.
   If the figure exists in the filing but you didn't open and extract it, the
   row is not `[A]` yet — open the filing (`edgar_fetch.py` for SEC URLs).

If a figure genuinely can't be located in the primary document after a real
look, record it as a signal gap rather than citing a secondary number at `[A]`.

**Threshold freshness:** If `projects.md` or a fresh filing changes the numeric baseline that a
hypothesis/watch-list threshold depends on, recalibrate the threshold in the same refresh. Do not
carry forward a threshold that was derived from an older rounded approximation.

**Hard rule:** if a hypothesis's evidence mix is mostly Tier C/D, its
confidence cannot exceed LOW. **A hypothesis with zero Tier A signals
cannot exceed MEDIUM.** H2 specifically requires 2+ independent Tier A
signals (Step 5a).

**Cross-hypothesis evidence overlap.** Same fact cited under multiple
hypotheses with different framings = double-counting. Build the overlap
table in the output (see Step 7 required sections). If H1 and H3 share
3+ rows, both must acknowledge they're reading the same operational
substrate from different posture assumptions.

### Step 7: Write the file

**Path:** `vault/companies/TICKER/execution-thesis.md` (deterministic
filename — overwrites prior version on each refresh).

**The normative template is `references/execution-thesis-template.md`.**
Mirror its section ordering and required content.

**Required sections in order:**

1. **Header** — purpose, reader-warning, last refreshed, evidence-tier
   legend, projects.md-as-primary-input note, and **audit-status banner**
   (set from the Step 1 prior-audit read):
   - No prior `execution-audit.md` exists → `unaudited`
   - Prior audit exists, refresh folded in corrections, no H2 retraction →
     `audited {YYYY-MM-DD} — corrections folded this refresh` (use the
     audit file's date)
   - Prior audit exists and was clean (no material findings) →
     `audited {YYYY-MM-DD} — clean, no material corrections`
   - Prior audit retracted H2 and this refresh dropped/reframed H2 in
     response → `audited {YYYY-MM-DD} — corrections folded this refresh`
     (the new file no longer carries the failed H2)
   - The `audit-failed …` banner values are written **only** when the
     thesis file has not yet been re-run since a failed audit — that
     state arises naturally because the audit file is newer than the
     thesis file, and the next refresh resolves it. Don't write
     `audit-failed` on a fresh build.
2. **Execution read** - human-first summary block that appears before
   Schedule baseline and answers the reader's actual first question:
   - **Execution verdict** - not a stock verdict, but the execution-state call
   - **Most likely hypothesis posture** - which of H1/H2/H3/H4 dominates and why
   - **What changed / what is newly clarified** - the 2-5 decision-relevant
     findings that were not already obvious from the prior synthesis
   - **Evidence that drove the read** - the load-bearing facts a human should
     inspect first
   - **What this means for downstream work** - one line for deep-dive /
     pre-earnings consumers
3. **Schedule baseline** — what management has committed to over the next
   1-12 months (from Step 2)
4. **Signal gap inventory** — short table from Step 3 classifying each
   stage gate as confirmed/inferred-only/contradicted/exceeds-disclosure/
   gap. This is the substrate the hypotheses synthesize over.
5. **Hypothesis 1 (On Schedule)** — required. Description, evidence-with-
   tiers, evidence mix, confidence, "What would falsify in 30/60/90 days",
   "What to watch"
6. **Hypothesis 2 (Ahead / Undisclosed Scope)** — only if Step 5a gate
   cleared. If not, write a single paragraph stating "H2 not proposed
   this refresh" with the closest-candidate signal and what's missing.
7. **Hypothesis 3 (Behind / Schedule Slip)** — required, same shape as H1
8. **Hypothesis 4 (Pivot / Off-Roadmap)** — only if Tier B+ evidence
   supports. Otherwise omit entirely (don't write "not proposed" — only
   H2 gets that note since it's the gated hypothesis).
9. **Cross-hypothesis evidence overlap** — overlap table from Step 6
10. **30/60/90-day watch list** — concrete, dated signals to look for in
   the next 30/60/90 days that would resolve hypothesis tension. This is
   the falsification register.
11. **Caveats / Methodology** — stale-source bias, mgmt-statement
    reliability, pattern-matching confabulation risk, especially for H2
12. **Sources** — primary-source links organized by hypothesis
13. **Refresh log** — dated entries; on every refresh after the first,
    include `### What changed since last refresh` (deltas in hypothesis
    confidence, new signals, retracted claims)
14. **What's NOT yet captured** — channels not pulled, signals deferred

### Step 8: Verify file integrity

Before reporting complete:
1. File exists at `vault/companies/TICKER/execution-thesis.md`
2. H1 (On Schedule) and H3 (Behind / Slip) both present (always required)
3. If H2 present: 2+ independent Tier-A signals cited per Step 5a
4. If H2 absent: explicit "H2 not proposed this refresh" note with
   closest-candidate signal explained
5. Each hypothesis has cited evidence rows with [A]/[B]/[C]/[D] tags
5a. **Every `[A]` row passed the pre-write gate (Step 6):** direct primary
   URL (not a mirror/aggregator) AND a specific extracted filed figure. No
   `[A]` row cites a press release or quotes a rounded/secondary number.
6. Each hypothesis has 30/60/90-day falsification subsection (NOT 3-5
   year — that was the prior skill's failure mode)
7. Execution read section present and starts the human-facing analysis
8. Schedule baseline section present (mgmt's claimed schedule)
9. Signal gap inventory present (the synthesis substrate)
10. Cross-hypothesis evidence overlap section present
11. 30/60/90-day watch list present with concrete dated signals
12. Refresh log entry added

## Constraints

- **Public sources only.** Standard mosaic-theory ethics. No private
  outreach, no scraped non-public data.
- **projects.md is the substrate, not the limit.** This skill reads
  projects.md as primary input but also pulls fresh sources. If projects.md
  is incomplete on a key channel, run a Round 1 search to fill the gap
  rather than synthesizing off thin substrate.
- **30/60/90-day falsification, not 3-5 year.** The prior skill's failure
  was vague long-horizon falsification ("if 3 years pass without an
  acquisition, the wild card is wrong"). Useless. New rule: every
  hypothesis names a signal expected within 90 days that would falsify
  or confirm.
- **H2 strict gate non-negotiable.** When in doubt, don't propose H2.
- **Multi-hypothesis required (minimum H1 + H3).** Producing only an
  upside thesis or only a downside thesis turns the skill into spin.
- **No verdict on the stock.** This skill does not produce HOLD/ADD/
  REDUCE/WATCH. Verdict is `stock-deep-dive`'s job. The output of this
  skill is a structured frame deep-dive can consume.

## Output ownership

`vault/companies/TICKER/execution-thesis.md` is owned by this skill.
Other skills should **read** it, not write to it. The next refresh
overwrites the file (deterministic name, no date stamp).

## Consumed by

| Consumer | What it reads | Why |
|----------|---------------|-----|
| `stock-deep-dive` | All hypotheses + 30/60/90-day watch list | "Is the buildout actually on track" becomes a structured input rather than something deep-dive has to re-derive. The 3-advisor council's "Bull" voice can specifically check whether H2 (Ahead / Undisclosed) has cleared its gate. |
| `pre-earnings` | H1 + H3 evidence + 30/60/90-day watch list | Identifies which schedule claims are independently verified going into the print. Slip indicators predict negative-surprise risk. |
| `execution-audit` | The whole file | Audit's primary input. Reads to fresh-search-verify H2 signals especially, structural-pass the rest. |
| `quarterly-review` | Refresh-log delta entries across audited tickers | Calibration signal: are the schedule slips this skill flagged actually realizing? Are H2 (Ahead / Undisclosed) hypotheses that cleared the gate confirmed at later announcement? |

## What this skill does NOT do

- **Does not collect raw mosaic signals.** That's `company-projects`'s job.
  This skill consumes projects.md and adds primary-source verification
  searches, but the broad signal-gathering pass lives in projects.md.
- **Does not produce a stock verdict.** No HOLD/ADD/REDUCE/WATCH. That's
  `stock-deep-dive`.
- **Does not predict probabilities.** Confidence levels describe evidence
  quality, not outcome probability.
- **Does not run on tickers without a fresh projects.md.** Hard prereq.
- **Does not run a 3-5 year horizon.** That was the predecessor skill's
  failure mode — too speculative, too redundant with deep-dive's council.
- **Does not write to other dossier files.** Only writes execution-thesis.md.
- **Does not auto-refresh.** Manual trigger only.

## Reference

- **Normative template:** `.claude/skills/execution-thesis/references/execution-thesis-template.md`
- **Predecessor:** the `long-game` skill (retired 2026-05-08). Two versions
  of the VRT long-game (`vault/companies/VRT/long-game.md` and the
  meta-audits at `long-game-meta-2026-05-08.md` / `meta-long-run-2.md`)
  remain as historical artifacts but are no longer the canonical format.

History:
- v1 (2026-05-08): initial build, replacing the retired `long-game` skill
  after the VRT two-agent meta-audit demonstrated long-game's 3-5 year
  horizon was redundant with deep-dive's council. New skill bounds to
  1-12 month execution-verification, requires projects.md as primary
  input, replaces Base/Bull/Bear/Wild with On-Schedule / Ahead-Undisclosed /
  Behind / Pivot frames, and gates H2 strictly behind 2+ independent
  Tier-A signals.
