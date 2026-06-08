---
name: company-dossier
description: >
  Build or refresh a SEC-sourced company data dossier at
  `vault/companies/TICKER/`. Pulls 10-K, 10-Q, DEF 14A, S-1/424B4 (if recent
  IPO), Form 4s/144s, recent 8-Ks from EDGAR and writes 8 files: overview,
  financials, risks, leadership, compensation, ownership, insider-activity,
  _meta. Used as input by stock-deep-dive, pre-earnings, and other agents.
  Manual refresh on demand. Usage: "build company dossier for VRT" or
  "refresh companies/VRT".
---

# Company Dossier

## Purpose

Build a structured, SEC-sourced reference dossier for a single ticker so that
other skills (stock-deep-dive, pre-earnings, ad-hoc analysis) can read just the
file they need without re-pulling EDGAR each time.

This skill **populates files**. It does not analyze, opine, or produce verdicts.
Other skills do that, on top of the data this skill writes.

## When to use

- User explicitly asks to build/refresh `vault/companies/TICKER/`
- A consuming skill (e.g., pre-earnings, pre-ipo) finds the dossier missing or stale
- After a material new filing (new 10-K, new 10-Q, new DEF 14A, new S-1/A) for an existing dossier

Do **not** auto-build dossiers for tickers that have no consumer — only populate
on demand or when a downstream skill needs the data.

## Pre-IPO mode

Triggered when the company has filed an S-1 with EDGAR but is not yet trading
publicly (no live ticker on Yahoo / Stooq). The user invokes with the proposed
ticker from the S-1 (e.g., "build company dossier for VLT" when VoltaGrid is
pre-IPO and proposing the VLT ticker), or with the company name + CIK
("build company dossier for VoltaGrid Inc CIK 1234567").

**What changes in pre-IPO mode:**
- **Primary source is the S-1** (or latest amendment S-1/A, and the 424A
  red-herring if available). The 10-K, 10-Q, and DEF 14A do not exist yet
  for a pre-IPO company.
- **Folder location:** still `vault/companies/{PROPOSED_TICKER}/`. If no
  proposed ticker is in the S-1, fall back to a company-name slug:
  `vault/companies/{COMPANY-SLUG}/` (uppercased, spaces → hyphens, e.g.,
  `vault/companies/VOLTAGRID/`). Note the slug in `_meta.md` so the
  `pre-ipo` skill knows what to glob for.
- **`insider-activity.md`:** populated from the S-1 principal-stockholders
  section + any Form 3s already filed. Form 4s typically don't exist
  pre-IPO. If empty, write "No insider transaction history pre-IPO. Watch
  for Form 3s at registration and Form 4 cadence post-lockup-expiry."
- **`financials.md`:** S-1 audited financials only (typically 2–3 years).
  No quarter-by-quarter trajectory the way a public company has. Note the
  cohort year transparency is limited.
- **`_meta.md` extra fields** (in addition to the standard ones):
  ```
  expected_ipo_date: YYYY-MM-DD          # or "TBD" if range only
  expected_ipo_date_confidence: confirmed | estimated | range-only
  proposed_ticker: SYMBOL                # if given in S-1
  cik: 0001234567                        # always include
  s1_filed: YYYY-MM-DD
  s1_latest_amendment: YYYY-MM-DD        # or "none"
  ipo_status: filed | priced | trading | withdrawn
  ```
  These mirror the `next_earnings:` fields and let the `pre-ipo` skill
  grep for the date.
- **Skip `next_earnings:` fields** — they don't apply pre-IPO. The
  upcoming-earnings script silently skips dossiers without that field,
  so a pre-IPO dossier won't pollute the daily earnings reminder.
- **Refresh trigger:** any new S-1 amendment, the 424A red-herring,
  pricing announcement, or the 424B4 final prospectus. Once the company
  starts trading, the next refresh becomes a normal post-IPO refresh —
  pull the first 10-Q if it's been filed, drop the pre-IPO-only flags,
  set `ipo_status: trading`.

**Refresh promotion:** when a pre-IPO dossier is refreshed after the
company starts trading, the workflow becomes the standard public-company
flow (Step 1 onward). Strip the pre-IPO-only `_meta.md` fields once the
first post-IPO 10-Q is on file (the `cik:` and `s1_filed:` lines stay as
permanent history; `ipo_status:` flips to `trading`; `expected_ipo_date`
fields go away).

## EDGAR access — critical gotcha

`WebFetch` returns 403 on sec.gov. Use `curl` with a SEC-compliant User-Agent header:

```bash
curl -H "User-Agent: Your Name you@example.com" \
  "https://data.sec.gov/submissions/CIK<10-digit-padded>.json" \
  -o submissions.json
```

Same UA header is required for every fetch (filings, XMLs, archives). Without it,
all SEC requests fail.

## Workflow

### Step 1: Resolve CIK
If user gave the CIK, use it. Otherwise look it up via the SEC ticker map:
`https://www.sec.gov/files/company_tickers.json` (also needs the UA header).

### Step 2: Pull submissions JSON
`https://data.sec.gov/submissions/CIK<padded>.json` returns the filings index.
Identify:
- Latest **10-K** (annual)
- Latest **10-Q** (quarter)
- Latest **DEF 14A** (proxy)
- Latest **424B4** + initial **S-1** (only relevant for recent IPOs — last 2 years)
- All **Form 4s** (insider transactions) and **Form 144s** (planned-sale notices)
- All **Form 3s** (initial ownership reports)
- Recent **8-Ks** (especially earnings 8-Ks and 5.02 events for officer/director changes)
- **Schedule 13G/13G/A** (institutional 5%+ holders)

### Step 3: Download key documents
Use curl with the UA header. Save to a temp directory. Strip HTML to plaintext
(BeautifulSoup works) so you can grep for sections efficiently. The 10-K is
typically 500KB–1MB+ of text — read sections by line range, not whole-file.

### Step 4: Sample insider activity
You don't need to parse all 50+ Form 4 XMLs. Sample the most recent ~10–15 plus
the lockup-expiry cluster (if recent IPO) to characterize the pattern. Note
whether sales are 10b5-1 (planned) or opportunistic — this is the signal that
matters more than gross volume.

### Step 5: Write 8 files to `vault/companies/TICKER/`

| File | Contents |
|------|----------|
| `overview.md` | Business, programs, technology, GTM, partners/clients, regulatory exposure |
| `financials.md` | Multi-year P&L, key metrics, revenue concentration, dilution overhang, IPO terms (if applicable) |
| `risks.md` | Distilled from 10-K Item 1A. Tier by materiality. Add cross-reference risks not in the 10-K. |
| `leadership.md` | NEO bios, full board, founder profile, governance characteristics, alignment signals |
| `compensation.md` | Summary Comp Table, Outstanding Equity Awards, severance arrangements, equity plan info |
| `ownership.md` | Beneficial ownership, 5%+ holders, dual-class voting math (if applicable), float estimate |
| `insider-activity.md` | Form 4/144 timeline, per-insider parsed transactions (sample), 10b5-1 plans, signals to watch |
| `_meta.md` | Source filings + dates + URLs, refresh log, what's NOT captured, key facts agent must know |

**Use `vault/companies/VRT/` as the structural template.** Match the file
shapes, section headers, and density. Optimize for agent consumption (dense,
factual, scannable, source-cited tables) — not human browsing.

### Step 6: Update `_meta.md` refresh log
Always append a refresh entry with the date and what was pulled. If this is a
re-run on an existing folder, note what changed (new filings since last refresh,
material updates).

### Step 6b: Emit a structured `next_earnings:` line
At the end of the "Key facts agent must know before recommending" section in
`_meta.md`, include two lines in this exact format (no leading bullet, plain
key:value so consumers can grep for them):

```
next_earnings: YYYY-MM-DD
next_earnings_confidence: confirmed | estimated
```

Use `confirmed` once IR has formally posted the date. Use `estimated` when
the date is inferred from prior-quarter cadence (typical for newly-public
or quiet names). Always emit both lines — `news-analyst`'s upcoming-earnings
script (`get_upcoming_earnings.py`) reads these to render the daily
"Active Earnings Windows" section. If you can't pin a date even
approximately, omit both lines (the script silently skips tickers without
the field).

The narrative `**Next earnings:**` bullet above can stay too — it's
human-readable context. The `next_earnings:` line is the machine-parseable
source of truth.

### Step 7: Clean up
Delete temp files. Don't leave HTML/XML/JSON downloads in the repo.

## Constraints

- **EDGAR-sourced only.** Don't pull from press releases, news sites, or
  paywalled sources. The dossier's value is that it cites authoritative
  primary sources.
- **No analysis or recommendations.** This skill writes facts. Verdicts and
  thesis validation belong in `stock-deep-dive`.
- **Cite the filing for any non-obvious fact.** Future agents need to know
  whether something came from the 10-K, the proxy, or a Form 4.
- **N/A for missing data.** Don't fabricate. Some companies don't file S-1s
  recently, don't have dual-class stock, don't have 5%+ holders. Just say so.
- **Refresh = full re-pull.** Don't try to patch old files. Re-run the whole
  workflow and overwrite. The cost is small; the staleness risk is real.

## Output ownership

Files in `vault/companies/TICKER/` are owned by this skill. Other skills should
**read** them but not write to them — if they find the dossier stale, they
should prompt the user to refresh, not patch the files themselves.

## Consumed by

Quick reference for which consumers read which files. Each consumer reads
selectively — none should pull the whole folder.

| Consumer | Files read | Why |
|----------|-----------|-----|
| `stock-deep-dive` | `_meta.md`, `leadership.md`, `risks.md`, `financials.md`, `insider-activity.md` | Founder signal, risk cross-check, revenue concentration, insider behavior at price |
| `news-analyst` | `insider-activity.md` only, and only conditionally | When a news item is about insider trading for a ticker with a dossier, calibrate severity against the expected 10b5-1 cadence (planned sales = low signal; outside-plan sales = higher signal). Don't read for non-insider news. |
| `pre-earnings` | `_meta.md`, `financials.md`, `risks.md`, `insider-activity.md`, `compensation.md` | Trend baseline, what to watch, behavior into print, KPIs comp pays on |
| `pre-ipo` | `_meta.md`, `overview.md`, `financials.md`, `risks.md`, `leadership.md`, `compensation.md`, `ownership.md` | S-1-derived fact base for the trade-shape decision; insider-activity is typically empty pre-IPO and skipped |
| Other skills | none currently | Pre-trade, weekly-review, vault-curator, quarterly-review don't need company-fact data |

**Staleness convention:** consumers should check `_meta.md`'s "Last refreshed"
date. Default threshold: flag if >90 days stale; hard-prompt to rerun if
>180 days. Adjust per consumer's tolerance for stale data (pre-earnings cares
more than deep-dive).

## What this skill does NOT cover

- Earnings call transcripts (not on EDGAR — separate concern)
- Real-time price/quote data (FMP / yfinance — separate concern)
- News, sentiment, analyst notes (Exa / web search — `news-analyst`'s job)
- Thesis validation, council debates, verdicts (`stock-deep-dive`'s job)
