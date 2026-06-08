---
name: company-projects
description: >
  Build or refresh a mosaic-research projects file at
  `vault/companies/TICKER/projects.md`. Verifies management's claimed buildout
  schedule against public, indirect signals (press releases, SEC filings, grid
  filings, permits, satellite, hiring, freight). Distinct from `company-dossier`
  — that is SEC-sourced reference data; this is execution-tracking. Manual
  refresh on demand. Usage: "build projects file for VRT" or "refresh
  companies/VRT/projects".
---

# Company Projects (Mosaic Research)

## Purpose

Track real-world execution against a company's stated project schedule using
public, indirect signals. The question this file answers:

> *Is the buildout actually progressing on the schedule management is claiming?*

Distinct from `company-dossier`:

- **`company-dossier`** is SEC-sourced reference data: business, financials,
  risks, leadership, compensation, ownership, insider activity. Static-ish.
- **`company-projects`** is mosaic-sourced execution data: stage gates,
  per-project progress, channel watchlist. Decays faster.

This skill **populates one file**: `vault/companies/TICKER/projects.md`. It
does not write to any other dossier file. It does not produce verdicts.

## When to use

- User explicitly asks to build/refresh `vault/companies/TICKER/projects.md`
- After a major management announcement (energization, contract signing,
  capacity update, M&A) — re-verify and update stage gates
- After a print where management revises schedule guidance
- Quarterly is a reasonable default cadence; faster if a specific event lands

Do **not** auto-build for tickers without a consumer. Build when the user asks
or when a downstream skill (e.g., stock-deep-dive) flags the absence.

## Prerequisites

- **`vault/companies/TICKER/_meta.md` must exist.** The skill reads it to
  understand industry, business model, and recent management posture. If
  the dossier is missing, **stop and recommend running `company-dossier`
  first** — don't build a projects file for a company we don't have a
  business model for.
- If the dossier is >180 days stale (per the standard convention), flag
  that the projects file may anchor on outdated context, but proceed.

## Web search — use Exa MCP

Use `mcp__claude_ai_Exa__web_search_exa` for verification and `mcp__claude_ai_Exa__web_fetch_exa` for full-page reads when highlights are insufficient. This matches the project standard set in CLAUDE.md.

## Workflow

### Step 0: Build or refresh the Variable Map (research design)

**This step is non-negotiable.** Before any channel-search work, the skill must produce a
**company-specific Variable Map** that drives what gets searched and why. Going straight to "search
the AI infra channel preset" is the failure mode this step prevents. VRT and GEV are both "AI power
infra" but their binding constraints, customer concentration, and execution patterns are vastly
different. A digital-health name is "healthcare" but the right map is enterprise SaaS + clinical credibility +
post-IPO lockup, not "search PubMed and call it healthcare." The Variable Map is the durable
research design that makes the rest of the skill company-specific.

**Step 0a: Read prior work first (warm-start optimization).**

Read in order:
1. `vault/companies/TICKER/projects.md` (prior version, if exists) — extract the prior **Variable
   Map** if present. Most refreshes are warm-starts; the map evolves, it doesn't get rebuilt cold.
2. `vault/companies/TICKER/_meta.md` — SEC reference. Industry, business model, fiscal calendar,
   key agent-must-know facts.
3. `vault/companies/TICKER/overview.md` — business model context.
4. **Most recent `vault/deep-dives/TICKER-*.md` if exists** — extracts the user's working thesis,
   binding-constraint assumptions, and the watch-list items the deep dive flagged. The Variable Map
   should test the deep-dive's thesis claims, not invent its own.
5. **`vault/notes/`** — files whose names contain the ticker, sorted by date desc, read the most
   recent 2-3. Extracts what the user has stated as the bear case + execution invalidators. Map
   variables should make those testable.
6. (Optional) `vault/companies/TICKER/execution-thesis.md` if exists — the prior synthesis.
   Useful for understanding which variables the prior thesis depended on most.

If a deep-dive and notes both exist, **the prior thesis surface drives the map**, not industry
presets. Industry/execution-pattern presets (Step 0c below) are scaffolding for the
not-yet-covered slots, not the driver.

**Step 0b: Identify the execution model (1 paragraph).**

Write a 1-paragraph answer in projects.md to:
- **How do management's claims turn into revenue?** (e.g., grid energization → data hall
  construction → GPU install → customer delivery acceptance → revenue recognition)
- **What are the binding constraints?** (rate-limiting steps where execution can break:
  power, permits, capital, customer, regulation, clinical evidence)
- **What's the bear-case shape this map needs to be able to test?** (e.g., dilution
  spiral, customer concentration risk, schedule slip, lockup overhang, clinical-evidence
  gap)

This paragraph anchors everything below.

**Step 0c: Claim execution patterns from the controlled vocabulary.**

A company normally gets **1-3 patterns layered**, not "1 industry preset." Rarely, a company
can claim a fourth pattern when it has an independent execution failure mode that would otherwise
be hidden (e.g., a post-bankruptcy miner-to-AI name: Physical buildout + Hyperscaler concentration + Restructuring overhang +
Capital structure dependency). If claiming 4, explicitly write why it is not just a sub-variable
of another pattern. Patterns:

| # | Pattern | Channels it brings | Typical companies |
|---|---|---|---|
| 1 | **Physical buildout** | Grid filings, county permits, freight permits, satellite, EPC/contractor PR, contractor liens, construction-supervisor hiring | VRT, GEV, DLR, data centers, semiconductor fabs, mines, factories |
| 2 | **Hyperscaler / single-customer concentration** | Counterparty earnings disclosures, lease amendments, exclusivity terms, post-anchor pipeline signals | DLR (anchor-tenant leases), power suppliers with a single hyperscaler offtake, small-cap suppliers to FAANG |
| 3 | **Enterprise SaaS adoption** | Segment channels by buyer route: private self-insured employers (DOL Form 5500, employer benefit guides), public sector (state benefit guides, procurement awards, board packets, contract registers), partner-distributed lives (payer/TPA/PBM member guides), customer-logo diffs | digital-health platforms, B2B SaaS, HR-tech, benefits platforms |
| 4 | **Clinical credibility** | PubMed by company affiliation with quality scoring (DOI/PMID, journal, funding/conflicts, sample size, comparator, follow-up, endpoint quality), ClinicalTrials.gov, conference abstracts (AAOS/ACR/JAMA/NEJM), FDA MAUDE/recall/adverse-event databases | digital-health platforms, biotech, med device, digital therapeutics |
| 5 | **Regulated rollout** | Agency docket filings (FDA/FCC/state PUC/state Medicaid), state-level approvals, certifications (HITRUST/SOC2/HIPAA), regulatory commentary | digital-health platforms, fintech, defense, healthcare, energy |
| 6 | **Engagement / utilization** | Retention/durability signals at the right unit: client retention, NDR/RPO/deferred revenue, eligible-lives-to-active-members, sessions/member, completed-session yield, benefit-page removals/diffs, app review velocity, customer-success/implementation/clinical-ops hiring | digital-health platforms, consumer subs, gaming, social |
| 7 | **Capital structure dependency** | Shelf/convert/ATM filings, dilution cadence, debt covenants, refinancing windows, founder selling Form 4 cadence | GEV, heavy-capex names, anything with active dilution drumbeat |
| 8 | **Post-IPO lockup / secondary supply** | S-1 lockup expiry, VC/founder Form 4 cadence, RSU vesting schedule, 10b5-1 plan adoption, registered direct offerings | recent IPOs in first 12-18 months |
| 9 | **Restructuring overhang** | Bankruptcy court filings, post-emergence cap structure, legacy contract disputes, creditor recoveries vs. new equity | recently-emerged-from-bankruptcy names (e.g., miner-to-AI pivots) |

Most companies fit 1-3 patterns; 4 is an exception that requires justification. Write the chosen
patterns at the top of the Variable Map with a 1-sentence rationale each. **Expand the vocabulary
when a new company doesn't fit** — don't shoehorn.

**Step 0d: Build the Active Execution Variables table.**

For each binding-constraint area surfaced in Step 0b, define a variable. Aim for **4-8 variables
per company.** The required shape:

| Variable | Binding constraint | Bull tell | Bear tell | Primary channels | Known-noisy channels | Pattern | Next refresh question |

- **Variable**: 2-4 word name (e.g., "Childress capacity ramp," "Enterprise client adoption rate")
- **Binding constraint**: 1 sentence on what could break here
- **Bull tell**: a specific signal pattern that would CONFIRM execution is on track (e.g., "Q4 print
  shows first MSFT delivery acceptance + revenue recognition")
- **Bear tell**: a specific signal pattern that would REFUTE execution (e.g., "no MSFT revenue
  recognized at Q4 + slip language on call")
- **Primary channels**: Tier-A sources where the tell would surface
- **Known-noisy channels**: sources that look adjacent but produce false positives (e.g., "general
  flatbed trucking rates" for VRT — too macro)
- **Pattern**: which of the 9 patterns this variable belongs to
- **Next refresh question**: 1 sentence — the specific thing next refresh should answer

**Numeric baseline rule:** When a Variable Map uses thresholds ("client count > X", "eligible lives
above Y", "MW billing > Z"), calibrate those thresholds from the most recent primary-source
baseline in the same refresh. Do not round an exact filed value into a looser shorthand and then
build thresholds off the rounded shorthand. If a later filing changes the baseline, update the
threshold logic and log the recalibration in "What changed since last review."

**Forcing bull-tell AND bear-tell** is the discipline that makes the map evidence-seeking, not just
channel-seeking. An agent that only knows "search permits" will confirm-bias; one that knows "Bull
tell = construction permits in Q4 cadence; Bear tell = no permits + lien filings appearing" reads
the same data critically.

**Step 0e: Set map maturity status.**

At the top of the Variable Map, mark one of three states:

- **`draft`** — Variable Map written this refresh, no channels searched yet. Honest signal that the
  research design exists but the substrate doesn't. `execution-thesis` must NOT run against a
  draft-only map (see execution-thesis SKILL).
- **`searched`** — At least one real search batch (≥5 queries) has been run per active variable,
  with results recorded in the Search Coverage Ledger (Step 4 below). `execution-thesis` may run.
- **`mature`** — Map has been through a later execution-audit that includes the Variable Map
  coverage check, ≥1 quarter of consistent refreshes, and known-noisy channels documented. If
  **Physical buildout** is a claimed pattern, `mature` additionally requires at least one real
  site-verification batch (defined below) covering the highest-weight active construction sites.
  The strongest gate for downstream consumers. Same-day backfills should usually stop at `searched`.

A first build typically writes `draft` after Step 0, transitions to `searched` after Step 4 of this
skill, and to `mature` only after a subsequent `execution-audit` confirms map fit + channel
coverage under the 4h audit check.

**Step 0f: Write the Variable Map as Section 1 of projects.md.**

The Variable Map is **Section 1** of `vault/companies/TICKER/projects.md`, placed BEFORE Stage Gates.
On refresh, **preserve the existing map** — only append to the "What changed since last review" log
at the bottom and update tables in place. Don't regenerate the map from scratch unless the business
model has materially changed.

If this is a first build (no prior map), write a complete map and mark it `draft`. Then proceed to
the channel pulls (Steps 2-N below) to upgrade to `searched`.

---

### Step 1: Identify execution model + key projects

Read `vault/companies/TICKER/_meta.md` and `overview.md`. Classify the company
by the execution patterns claimed in the Variable Map, not by a single industry
bucket. If the company spans multiple businesses, let the revenue path and
binding constraints determine which patterns matter.

Identify the **named projects** the company is executing on — sites, programs,
clinical trials, store rollouts, product launches, capacity expansions. The
projects file is keyed off these named units.

### Step 2: Pick channels (pattern-keyed)

**Run every primary channel named in the Variable Map for this company's
execution patterns.** The previous "pick 4-6 highest-leverage channels" rule is
retired — corner-cutting on channel coverage is the documented failure mode for
the mosaic skills (see `feedback_mosaic_research_depth.md`). The 2026-05-11
VRT refresh enumerated the channel watchlist but only pulled 6-8 of ~25
channels, and the downstream execution-thesis missed the $11.9B commitments
cliff and Nostrum price (EUR 165M) because they weren't surfaced.

**Channel coverage discipline:**
- The Variable Map (Step 0) names which channels matter for THIS company. Use those first.
  Industry/pattern presets are scaffolding for the not-yet-covered slots, not the driver.
- Run **every primary channel named in the Variable Map** on every refresh. Run secondary channels
  on first build + 2-quarter cadence.
- When a channel returns nothing, **state that explicitly in the Search Coverage Ledger** (see
  below). Silence is not coverage. "Not searched" ≠ "no signal found" — both must be distinguishable
  in projects.md.
- Each county / state / regulatory body / utility is a separate search, not a category. "Childress
  / Fisher / Nolan / Kiowa county records" = four searches, not one.
- For SEC filings, **open the actual 10-K/10-Q/8-K text and extract specifics** — don't lean on the
  press-release summary. Commitments balances, share counts at the most recent date, contract
  terms, vesting triggers, payment terms, financing-letter-vs-closed distinctions all live in the
  filing text and not the headline release.

**Physical-buildout site-verification batch (required when Physical buildout is claimed):**
- Before a Physical-buildout map can be marked `mature`, run at least one direct site-verification
  batch for the highest-weight active sites. For a first same-day refresh this may remain `Defer`,
  but then maturity must stay `searched`.
- A site-verification batch means **2+ independent non-management physical channels** across the
  active sites, such as county/city permits, utility/interconnection dockets, environmental permits,
  deed/land records, contractor liens, EPC/vendor permits/PR, or saved satellite imagery. Web-index
  searches that fail to reach the actual county/agency/satellite record do **not** count; log them as
  `Defer` with the access blocker.
- If all physical channels are deferred or only management sources support the construction state,
  state that in the Search Coverage Ledger and cap downstream buildout confidence at `MED-HIGH`.
- For non-buildout patterns, use the equivalent pattern-native primary substrate (e.g., PubMed /
  ClinicalTrials.gov for Clinical credibility, broker/RFP records for Enterprise SaaS adoption).

**Search Coverage Ledger (required section in projects.md, updated every refresh):**

After the channel-pull batches complete, populate a table in projects.md called "Search Coverage
Ledger" with the shape:

| Channel | Query / source checked | Date | Result | Kept / Dropped / Defer | Why |

- **Channel**: name from the Variable Map (e.g., "Childress County Appraisal District," "TxDOT
  oversize permits Hwy 287 corridor," "Mercer benefit guides 2026")
- **Query / source checked**: the literal query string or URL pattern used
- **Date**: when the check happened (so future refreshes don't re-pull stale-known channels)
- **Result**: 1-line summary — "no VRT-named records returned," "12 records, 3 material (cited
  in Stage Gates)," "rate-limited, deferred"
- **Kept / Dropped / Defer**: `Kept` = useful channel, keep on next refresh's list; `Dropped` =
  known-dead, do NOT re-pull next refresh; `Defer` = deferred for cost/complexity, retry later
- **Why**: 1 sentence rationale, especially for Dropped

The Coverage Ledger solves the "did we check this or not" ambiguity. Future agents reading
projects.md should be able to see at a glance whether TxDOT was tested-and-empty (Kept, refresh
next quarter) vs. tested-and-useless (Dropped, don't waste tokens) vs. never-tested (Defer or
absent from ledger entirely).

**Upgrading map maturity:** After running ≥1 real search batch per active variable AND populating
the Coverage Ledger, update the Variable Map header from `draft` to `searched`. This is the gate
that allows `execution-thesis` to run.

The channel sets below are **source-utility examples**, not evidence-tier
definitions and not mandatory industry presets. Evidence tiering still follows
the strict `[A] / [B] / [C] / [D]` rules used by execution-thesis and
execution-audit: press releases, investor decks, and earnings transcripts are
company outputs (`[B]`) unless the same fact appears in a regulatory filing or
contract exhibit. Add channels that the specific company's Variable Map calls
for.

#### AI infra / datacenter / GPU cloud / crypto-mining-pivot

(VRT, DLR, GEV, CEG, etc.)

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, grid interconnection queues (ERCOT for TX, MISO/PJM/SPP/CAISO by geography), county/state permit records, utility dockets |
| Medium | Company press releases, earnings transcripts, local press, LinkedIn site-filtered headcount/role-mix, H-1B disclosure data (DOL LCA), FERC PPA filings |
| Specialty | Sentinel-2 satellite imagery, state environmental filings (TCEQ, etc.), BGP/ASN/PeeringDB for network-readiness, county deed records (land purchase confirmation) |

#### Hyperscaler

(GOOGL, MSFT, META, ORCL)

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, AWS/GCP/Azure region-launch announcements, customer-side regulatory disclosures |
| Medium | Company press releases, earnings transcripts, bill-of-lading data (ImportGenius, Panjiva), LinkedIn employee count by site, GitHub commit activity for public repos |
| Specialty | Customs HS-code imports, FCC/FAA filings, conference panel topic shifts |

#### Semiconductor

(NVDA, AMD, TSMC, AVGO)

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, FCC equipment authorizations, patent + trademark filings (USPTO), foundry capacity regulatory disclosures |
| Medium | Company press releases, earnings transcripts, foundry capacity news (TSMC, Samsung), customs HS-code imports |
| Specialty | Industry trade press (DigiTimes), conference announcements (GTC, OCP), supply-chain rumor channels |

#### Biotech / digital health

(a virtual-care / MSK / digital-therapeutics name, plus traditional biotech)

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, FDA 510(k)/MAUDE/recall databases, ClinicalTrials.gov primary completion dates, direct PubMed/JHEOR citations with study-quality scoring, state procurement/benefit records, DOL Form 5500 for private self-insured employers |
| Medium | Employer and payer/TPA member benefit guides, payer contract press releases, conference abstracts (ASCO, AHA, AAOS, ACR, etc.), patent filings, implementation/customer-success/clinical-ops hiring |
| Specialty | Broker benefit guides, app review/rank velocity, benefit-page year-over-year removals/diffs, KOL commentary, ICD-10/CPT code adoption rates |

For digital-health names, keep adoption channels split by route. DOL Form 5500 is high-signal for private self-insured employers, but not for government plans generally outside ERISA. Public-sector verification should use state benefit guides, board packets, procurement awards, RFP/contract registers, open-enrollment PDFs, and benefits vendor directories. Partner-distributed lives should be verified through payer/TPA/PBM member guides, not only partner press releases. Rank channels by independence: legal/primary records and direct member-facing guides beat employer pages, which beat broker decks, which beat partner/company press.

#### Energy / utility

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, FERC filings, EIA-923 monthly generation reports, state PUC dockets |
| Medium | Company press releases, earnings transcripts, environmental filings, LinkedIn |
| Specialty | Industry trade press, IEEE/utility conference proceedings |

#### Retail / consumer

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, app download rankings (Sensor Tower) where app engagement is central |
| Medium | Company press releases, earnings transcripts, foot traffic data (Placer.ai, SafeGraph), Glassdoor, LinkedIn role-mix shift |
| Specialty | Bill-of-lading imports, social listening, satellite parking-lot counts (RS Metrics) |

#### Software / SaaS

| Utility | Channels |
|------|----------|
| High | SEC filings / contract exhibits, customer logo wall changes (Wayback Machine diffs), pricing page changes |
| Medium | Company press releases, earnings transcripts, GitHub commit activity, LinkedIn role-mix shift, DNS / SSL Certificate Transparency logs (new product subdomains) |
| Specialty | App reviews velocity, conference attendance, executive commentary |

### Step 3: Verify management's claims

For each project the file will track, find primary-source verification of
key claims:

- Capacity / scope numbers (MW, GPUs, store count, drug pipeline)
- Schedule milestones (energization date, commissioning date, trial readout date)
- Customer / contract terms (named customer, $ value, prepayment %, term)
- Naming conventions (e.g., is "Horizon 1-4" the real program name or a
  third-party rendering?)

**Use `mcp__claude_ai_Exa__web_search_exa` aggressively** — token budget here
matters less than getting the numbers right. Cross-check at minimum two
sources for any specific number that goes into the file. If one source is
the company itself and the other is independent (Reuters, trade press, SEC
filing), that's good. If both sources trace back to the same press release,
that's one source.

**Flag third-party-only claims explicitly.** If a fact appears only on a
fan site, blog, or forum and not in any company filing or independent
press, mark it `(UNVERIFIED — third-party source only)` in the file.

### Step 4: Write `projects.md`

Mirror the structure used in `vault/companies/VRT/projects.md` (the
prototype). The required sections:

#### 4a. Header

```markdown
# {COMPANY} — Projects (mosaic research)

**Purpose:** {one-sentence what this file tracks for this company}.
Distinct from `_meta.md` / `financials.md` — those are SEC-sourced.
This file synthesizes {channel summary} to answer: *is the buildout
actually progressing on the schedule management is claiming?*

**Last refreshed:** YYYY-MM-DD
**Next refresh suggested:** {trigger — typically next earnings or
specific milestone}
```

#### 4b. Stage Gates

Discrete dated milestones — binary "did it happen" events. Status =
`DONE` / `UPCOMING` / `NOT YET` / `MISSED` (if announced and slipped).

```markdown
| Gate | Project | Status | Date | Source | Implication |
```

#### 4c. Project sections (one per named project)

Order by **revenue linkage**, not size. The project that anchors
recognized revenue goes first. Speculative / optionality projects go
later.

For each:
- One paragraph context (why this project, its current status)
- Evidence rows table:

```markdown
| Signal | Source | Date | Implication | Confidence | Revenue relevance |
```

`Confidence` = `HIGH` / `MED` / `LOW` based on source quality.
`Revenue relevance` = `Direct` (drives recognized revenue) / `Indirect`
(supports thesis but not contracted) / `None near-term`.

#### 4d. Cross-project signals

Things that span projects — financing, equipment procurement, customer
pipeline, M&A, founder behavior. Same evidence-row table format.

#### 4e. Channels Watchlist

Pattern-keyed channel table derived from the Variable Map. Each row:

```markdown
| Channel | URL / How | What to check | Cadence |
```

Plus an explicit **What NOT to track** subsection naming channels that
are high-noise/low-signal for this specific company. (E.g., for a pure
software company, bill-of-lading is noise.)

#### 4f. Caveats

A short section reminding the reader of mosaic-theory limits:
- Stage gates ≠ revenue
- One-quarter-removed staleness on slow channels
- Public sources only (legal boundary)
- Any company-specific noise factors

#### 4g. Sources + Refresh log + What's NOT yet captured

- **Sources:** primary-source URLs cited above, organized by topic
- **Refresh log:** dated entries describing what was pulled. **On every
  refresh after the first**, include a `### What changed since last
  refresh` subsection inside that refresh's entry, with structured deltas
  in this exact shape (so a future drift script can grep them):

  ```
  ### What changed since last refresh (YYYY-MM-DD → YYYY-MM-DD)
  - **Stage gate flips:** {Gate name} {OLD STATUS → NEW STATUS} ({optional reason})
    - e.g., `Site 2 substation energization NOT YET → MISSED (slipped from 2027 to 2028 per Q3 FY26 call)`
  - **Numerical deltas:** {metric}: {old value} → {new value}
    - e.g., `MW energized at VRT sites: 350 MW → 410 MW`
  - **New evidence rows:** {count} added to {section name}
  - **Retracted / invalidated claims:** {what and why}
  - **New stage gates added:** {gate names}
  ```

  If a delta type doesn't apply this refresh, omit that bullet entirely
  (don't write "none"). The first build skips this subsection — there's
  no prior to diff against. Keep entries terse and structured —
  paragraphs defeat the purpose.
- **What's NOT yet captured:** honest list of channels whose URLs are
  bookmarked but no actual data was pulled this refresh (typical for
  Tier B/C on first build)

### Step 5: Verify file integrity

Before reporting complete:
1. File exists at `vault/companies/TICKER/projects.md`
2. Every fact has a source (link or filing reference)
3. Confidence ratings present on every evidence row
4. Stage Gates table has at least one DONE and one UPCOMING entry
5. At least one project section with evidence rows
6. Channels Watchlist has at least Tier A populated
7. Refresh log entry added

## Constraints

- **Public sources only.** No trespassing, hacked data, MNPI, deception, or
  private employee outreach. The whole point of mosaic theory is that it's
  legal because everything is public. Bake this into the Caveats section
  for every file.
- **No fabricated numbers.** Every figure must trace to a primary source.
  When the source is a press release, link to it; when it's an SEC filing,
  cite the form type and date.
- **Verify before citing.** If another agent or third-party source provides
  a specific number, web-search it before putting it in the file. Pattern
  to avoid: "third party said X, file cites X, X turns out to be hallucinated."
- **Flag unverified claims.** Mark with `(UNVERIFIED — third-party source only)`
  in the file. Never silently launder a third-party claim through our file.
- **One file per ticker.** This skill writes only `projects.md`. Do not
  modify `_meta.md`, `overview.md`, or any other dossier file.
- **Refresh = full re-verify.** Don't try to patch — re-run verification on
  every claim and overwrite the file. Append to the refresh log.

## Output ownership

`vault/companies/TICKER/projects.md` is owned by this skill. Other skills
should **read** it but not write to it. If another skill finds the file
stale or missing, it should prompt the user to refresh, not patch the
file itself.

## Consumed by

| Consumer | What it reads | Why |
|----------|---------------|-----|
| `stock-deep-dive` | Stage Gates + Project sections | Validates the thesis against actual buildout pace; informs Portfolio Fit & Timing |
| `pre-earnings` | Stage Gates (recent + upcoming) | Anchors pre-commit orders to project schedule (e.g., "if energization slips, trim before next print") |
| `news-analyst` | Channels Watchlist (only as reference, not parsed) | When a news item references a specific project the file tracks, it's automatically more material |

The Channels Watchlist is for the user and future refresh runs — it's
not auto-pulled by any consumer. Treat it as a research playbook, not a
live feed.

## What this skill does NOT do

- **Does not treat inaccessible specialty channels as covered.** Permits,
  satellite, LinkedIn headcount, H-1B records, TRACE, and similar channels
  may require human review, paid tools, or specialized tooling. Pull what is
  accessible; when a direct record cannot be reached, write a `Defer` row in
  the Search Coverage Ledger with the access blocker. For Physical buildout,
  a map with all site-verification channels deferred can be `searched` but
  not `mature`.
- **Score severity or produce verdicts.** That's `news-analyst` and
  `stock-deep-dive`. This skill produces a research substrate.
- **Auto-refresh on a schedule.** Manual trigger only. Cadence judgment
  belongs to the user (typical: after each earnings print, after major
  announcements).
- **Write to `notes/`, `library/`, or `reports/`.** Output is exclusively
  `vault/companies/TICKER/projects.md`.

## Pattern classification — when in doubt

If a company spans multiple execution models (e.g., a hyperscaler that's also
building custom silicon), claim the patterns that **drive the projects you're
tracking**. A hyperscaler building cloud data centers may use hyperscaler + physical
buildout. NVDA's Jensen visiting TSMC may use semiconductor supply-chain +
capital-allocation patterns. The same company can have its projects file
reweighted if the strategic focus shifts — that's fine.

If the company's execution pattern is not covered by the vocabulary above,
propose a new pattern in the file's Channels Watchlist and note in the Refresh
log that the pattern is provisional. Future refresh can promote stable new
patterns into this skill's reference list.

## Reference: prototype file

`vault/companies/VRT/projects.md` is the structural template. When in
doubt about formatting, density, or section ordering, mirror that file.
It was hand-built for VRT before this skill was written, so its shape
defines the skill's output convention.
