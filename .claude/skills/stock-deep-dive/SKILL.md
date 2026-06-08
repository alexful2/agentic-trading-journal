---
name: stock-deep-dive
description: >
  On-demand fundamentals-driven deep research on a specific stock. Pulls live
  data via yfinance (valuation, earnings, analyst consensus, price targets,
  options chain), validates the buy thesis against current fundamentals, runs
  a 3-advisor mini-council (Contrarian / Bull / First-Principles), and produces
  a Hold/Add/Reduce/Watch verdict. Includes a conviction check.
  Requires the `yfinance` Python package; no API key.
  Usage: "run deep dive on NVDA", "deep dive VRT", or "deep dive NVDA vs VRT"
  (comparison mode: provide two tickers to get individual deep dives + allocation verdict)
---

# Stock Deep Dive

## Purpose

Systematic fundamentals analysis on a stock you hold or are considering.
This is not news-driven — it's a cold-eyed look at current valuation,
earnings trajectory, analyst consensus, and whether your original thesis
still holds at today's price.

Run this when:
- You're uncertain whether to hold, add, or reduce a position
- A stock has moved significantly and you want a fresh read
- You haven't reviewed a position's fundamentals in a while
- The daily report flagged something material and you want to go deeper

**Requires:** `yfinance` Python package — install with `pip install yfinance`.

---

## Comparison Mode

**Detect:** If the user provides two tickers (e.g., "NVDA vs VRT" or
"deep dive NVDA and VRT"), activate comparison mode.

**What changes:**
- Run Steps 1–5 fully for Ticker A, then fully for Ticker B. Each gets
  its own scripts, its own thesis check, its own historical patterns.
  Treat them as two independent deep dives first.
- After both are complete, run Step 3b (Head-to-Head) instead of going
  straight to the council.
- The 3-advisor council is reframed around the allocation question
  (see Step 6 notes below).
- The verdict format changes to an allocation answer, not HOLD/ADD/REDUCE/WATCH
  (see Step 7 notes below).
- Write three output files: one individual deep dive per ticker (normal
  format, normal template) plus one comparison file (see Step 8).

**What stays the same:**
- All vault context loading (Step 1) — read once, applies to both.
- All script calls run normally per ticker.
- Conviction check runs for both tickers individually within their
  respective deep dive files.
- The individual deep dive files are complete standalone reports — the
  comparison file is the synthesis layer on top.

---

## Workflow

### Step 0: Staleness Check

Before loading vault context or running any scripts, check what already
exists in `vault/deep-dives/` for today's date.

**Single-stock mode:**

Check for `vault/deep-dives/TICKER-YYYY-MM-DD.md` (today's date).

- **File exists:** Stop. Tell the user a deep dive for this ticker was
  already run today and surface the verdict line from the existing file.
  Do not rerun. If the user explicitly says "rerun it anyway" or "refresh
  it," proceed and overwrite.
- **File does not exist:** Continue to Step 1.

**Comparison mode:**

Check for all three possible files (TICKER_A individual, TICKER_B
individual, comparison file) using today's date.

| TICKER_A file | TICKER_B file | Comparison file | Action |
|---|---|---|---|
| exists | exists | exists | Stop — surface allocation verdict from comparison file |
| exists | exists | missing | Skip Steps 2–3 for both. Read existing files for data. Jump to Step 3b. |
| exists | missing | missing | Skip Steps 2–3 for TICKER_A only. Run normally for TICKER_B. Then Step 3b. |
| missing | exists | missing | Run normally for TICKER_A. Skip Steps 2–3 for TICKER_B. Then Step 3b. |
| missing | missing | missing | Run normally for both. |

**When reusing an existing file instead of running scripts:**
- Read the existing `TICKER-YYYY-MM-DD.md` file.
- Extract: price, 52w range, valuation metrics, analyst target, pattern
  preset and win rate, thesis check result, and verdict — these are all
  present in the file's Snapshot, Fundamentals, and Thesis Check sections.
- Use these extracted values wherever you would have used script output.
- Skip Step 2c (options analysis) for the reused ticker — the existing
  file already has the result (or correctly omits it). Do not re-derive it.
- Note in the comparison file: "TICKER_A data from existing deep dive
  dated YYYY-MM-DD."

---

### Step 1: Load Vault Context

Identify the target ticker from the user's request.

Apply temporal reasoning (see CLAUDE.md) when reading notes — newest wins, flag revisions explicitly in your analysis (e.g., "the $135–150 VRT target in [[DLR - 2026-04-09 Buy]] was revised in [[VRT - 2026-04-14 Speculation]]").

**Read from vault — read ALL of these, not just the target ticker's files:**
- `vault/notes/` — read every file. Extract the original buy thesis, entry
  price, and any stated invalidation criteria for the target ticker. Also
  read all other notes to understand the full portfolio: what else is held,
  recent decisions, and any patterns in the user's thinking (e.g., tendency
  to hold through dips, notes about pivot candidates, emotional state around
  specific positions).
- `vault/watchlist.md` — full tier list. Know what's held vs. watched vs.
  peripheral so you can make direct comparisons.
- `vault/library/` — read every file **except `vault/library/research/`**
  (that subfolder is handled separately, and selectively, in the next
  bullet). Extract principles and frameworks relevant to this stock's
  sector. Also note any general investing rules the user has written for
  themselves.
- `vault/library/research/` — the **empirical-priors catalog** (C1–C13:
  foundational finance findings distilled into decision priors). Read
  **selectively**, not all 14 — pull only the notes relevant to this
  ticker/decision and apply each note's **Decision-rule translation** while
  respecting its **What this is NOT** / **Tension** guards. These are
  burden-of-proof priors, never single-name buy/sell signals. Relevance map:
  - **Capital-intensive / aggressively-building name** (most AI-infra) →
    [[C13 - Asset Growth and Capex Caution]] + [[C14 - Share Issuance and Dilution Drag]] + [[C5a - Gross Profitability Premium]] (apply in Step 3 Thesis Validation).
  - **Sizing / concentration** → [[C9 - Most Stocks Underperform T-Bills]] + [[C15 - Concentration Done Right]] (Step 4b)
    + [[C8 - Kelly Criterion and Position Sizing]] (Step 4 Sizing — no fake-precise Kelly numbers).
  - **"Is it extended / am I chasing?"** → [[C4 - Momentum and Trend Persistence]] (Step 4 Timing).
  - **Holding-a-loser / "give it more time"** → the [[C6 - Disposition Effect]] +
    [[C10 - Limits to Arbitrage]] pair (Step 4b override + Step 7 verdict).
  - **High-beta sharp-exposure name** → [[C11 - Betting Against Beta]] + [[C5b - Quality Minus Junk]].
  - Frame all of it with the skepticism spine ([[C2 - Replication Crisis in Factor Anomalies]],
    [[C1 - Publication & Arbitrage Decay]]): these are calibration priors, and the
    durable edge is the private execution work (`execution-thesis` / `projects.md`),
    not the public factor. Skip the catalog entirely if no note is relevant.
- `vault/reports/daily/` — read the 3 most recent daily alerts (sort by filename
  date descending). Extract any mentions of the target ticker or related
  names. This gives you recent market context and what's been flagged lately.
- `vault/!Journalit/` — instead of scanning files yourself, call:
  ```bash
  python .claude/scripts/get_positions.py --format json
  ```
  This returns one row per open position with shares, weighted-avg cost,
  realized P&L, and live unrealized P&L (Stooq). The target ticker's row
  drives the Step 4 Portfolio Fit & Timing — cite the actual position
  size and unrealized %, not vague "you hold this." Other tickers' rows
  give you the cross-position context (how much capital is already tied up
  in adjacent infra names, what's working, what's underwater).
  If the script errors entirely, fall back to scanning `!Journalit/` files
  yourself. Don't fabricate a position size.
- `vault/deep-dives/` — read the most recent deep dive per ticker.
  List all files (format: TICKER-YYYY-MM-DD.md), group by ticker, and
  for each ticker read only the most recent file (sort by date descending,
  take the first). Do not read multiple files for the same ticker.
  For the target ticker: track how the thesis has evolved, what the prior
  verdict was, and whether anything flagged last time has played out.
  For other tickers: understand recent positioning context and any
  cross-stock reasoning that may inform this decision.
- `vault/reports/pre-earnings/` — read the most recent pre-earnings file
  for the target ticker only (format: `TICKER-YYYY-MM-DD-{initial|gate}.md`).
  Prefer the `-gate` file if both exist for the same print date. Extract:
  the Pre-Commit Plan, the Scenario Ladder's realized outcome if the print
  has passed (for calibration context), and any thesis cracks the pre-earnings
  run surfaced. If the print date is in the future, the plan is live — the
  deep-dive should not propose changes that invalidate the user's pre-committed
  orders without flagging the conflict explicitly. If the print has already
  passed and the post-print drift contradicts the pre-commit plan, note it
  in the Thesis Check section. Skip if no pre-earnings file exists for this
  ticker.
  - **If the print date is in the past, also run:**
    ```bash
    python .claude/scripts/score_print.py --ticker TICKER --print-date YYYY-MM-DD
    ```
    The JSON gives realized 5-TD post-print move, which scenario row
    contained the realized price, and that scenario's assigned probability.
    Feed into the Contrarian advisor (Step 6) — was the pre-commit plan
    well-calibrated, or did a low-probability scenario fire? — and the
    Thesis Check (Step 3) — does post-print drift confirm or contradict
    the thesis? Especially relevant when invoked as "deep dive NVDA —
    earnings just dropped, fresh verdict." Skip the script call if the
    print is in the future or no pre-earnings file exists.
- `vault/companies/{TICKER}/` — SEC-sourced company dossier (built by the
  `company-dossier` skill). For the deep-dive, read these files **selectively**
  (comparison mode: read for both tickers):
  - `_meta.md` — check the "Last refreshed" date. If >90 days stale, flag at
    the top of the Snapshot section and suggest the user rerun `company-dossier`.
    If missing entirely, suggest building it but proceed without — this is
    not a blocker.
  - `leadership.md` — extract founder/management signal (alignment, founder
    selling pressure, recent governance changes). Drives the Founder Signal
    section of the output.
  - `risks.md` — distilled 10-K risk factors. Cross-check against the user's
    thesis to identify risks the user hasn't acknowledged.
  - `financials.md` — revenue concentration, dilution overhang, multi-year
    trends not surfaced by the fundamentals script.
  - `insider-activity.md` — current 10b5-1 plan cadence, recent insider
    selling pressure at today's price level.
  - `execution-thesis.md` (if it exists) — 1-12 month execution synthesis.
    Read the **Execution read** first, then the Schedule baseline, the active
    hypotheses (especially whether H2 cleared its gate), and the 30/60/90-day
    watch list. Feeds the
    Bull voice's "is the buildout actually on track" check in Step 6 and
    informs Step 4's Portfolio Fit & Timing. **Respect the audit-status
    banner at the top of the file:** if `audit-failed … H2 retracted` or
    `audit-failed … structural issues`, also read `execution-audit.md`
    and prefer its corrections over the thesis file's content. If
    `unaudited`, weight H2 lower than audited H2. If the
    `execution-thesis.md` file's mtime is older than `execution-audit.md`'s
    mtime (audit is newer than thesis), the thesis is pre-audit-fold —
    read both files and respect the audit's verdict.
  - `projects.md` (if it exists, and only if execution-thesis.md is
    absent or >60 days stale) — raw mosaic signal layer. Skip if a fresh
    execution-thesis is on file; that file is the synthesis you actually
    want.
  - Skip `overview.md`, `compensation.md`, `ownership.md` unless the user's
    question specifically targets business model, exec pay, or voting control.

If no note exists for the target ticker, proceed with what's in watchlist.md
and library/. Note the absence — the output should flag that no buy thesis is
on file.

---

### Step 2: Fetch Fundamentals

Run the fundamentals script to pull live data:

```
python .claude/skills/stock-deep-dive/scripts/get_stock_fundamentals.py --ticker TICKER
```

The script fetches (all via yfinance / Yahoo Finance — no API key required):
- **Quote:** current price, day change %, 52-week high/low, market cap, beta
- **Profile:** company name, sector, industry
- **Key metrics (TTM):** P/E, forward P/E, EV/EBITDA, price/sales, ROE, debt/equity, margins
- **Quarterly financials:** revenue, gross profit, net income, EPS — last 4 quarters
- **Earnings history:** EPS actual vs estimate — last 4 quarters
- **Next earnings date**
- **Analyst targets:** avg/median/high/low price targets, buy/hold/sell recommendation
- **Fair-value bands** (`fairValueBands`): bear/base/bull price bands from
  fwd-P/E (15/20/25× fwd EPS) and P/S (0.7×/1.0×/1.4× current multiple).
  Both are emitted when computable; the `suggested` field flags which is
  likely the useful ladder anchor (fwd-P/E for 8–30× fwd PE stocks, P/S
  for higher-multiple growth names). Used in Step 4's Level Context block.

**If the script fails** (network error, bad ticker, yfinance not installed): abort
the run and tell the user what went wrong. Do not proceed with estimated or
hallucinated numbers. Every figure in the output must come from the script.

**If individual fields return null:** note "N/A" in the output and continue —
partial data is acceptable, fabricated data is not.

---

### Step 2b: Historical Entry Patterns

Run the historical patterns script to backtest how this stock has behaved
in conditions similar to today's setup:

```
python .claude/skills/stock-deep-dive/scripts/get_historical_patterns.py --ticker TICKER --format json --output patterns_temp.json
python .claude/skills/stock-deep-dive/scripts/get_historical_patterns.py --ticker TICKER
```

The first command saves `patterns_temp.json` for use in Step 2c. The second produces the human-readable output you'll cite in the report.

The script runs three presets against 5 years of daily price history:

- **Preset 1 — Dip Buyer:** when price was 15–30% below its rolling 52-week
  high, what happened at +21/+42/+63 trading days?
- **Preset 2 — Extended Run:** when price had gained >20% in the last 20
  trading days (i.e., chasing a run), what happened next?
- **Preset 3 — Pre-Earnings Entry:** when bought 10 trading days before
  earnings, what was the return through earnings + 5 days?

The script also flags **which preset the stock is currently in** — so you
immediately know which historical analog applies to today's decision.

**Level Context (`levelContext`):** alongside the pattern output, the script
emits ATR(20d), 50 DMA, 200 DMA, and up to 3 recent swing lows from the last
~6 months. These are reference numbers for the Step 4 Price Ladder — every
ladder level must tie to at least one of them (or to a fair-value band, or
to an analyst target).

**If the script fails:** note the failure in the output and proceed without
pattern data. Do not fabricate win rates or return figures.

**If a preset shows "insufficient data"** (fewer than 4 instances): skip
that preset in the report. Note "insufficient history" rather than inventing
a conclusion.

Store the script output — you'll use it in Step 4.

---

### Step 2c: Options Analysis (conditional)

Run the options analysis script using the JSON saved in Step 2b:

```
python .claude/skills/stock-deep-dive/scripts/get_options_analysis.py --ticker TICKER --pattern-file patterns_temp.json
```

This evaluates three conditions in sequence:
1. Best entry pattern win rate ≥ 60%
2. ATM implied volatility ≤ 1.5× 30-day realized volatility (options not currently expensive)
3. Pattern's average return clears the breakeven % for some reasonable OTM call at the target expiry

The target expiry is automatically set to ~2× the pattern's typical duration — giving the move time to play out without buying too close to expiration.

**If `conditions_met: true`:** Include the "Calls Consideration" section in the report (see template). Populate it with the recommendation data from the script output.

**If `conditions_met: false`:** Omit the section entirely. Do not mention calls anywhere in the report — a failed screen is not interesting.

**If the script errors** (no options data available, yfinance issue): omit the section silently.

---

### Step 2d: Targeted Research Searches

**Search tools:**
- `web_search_exa` — use for both searches below. If unavailable, fall
  back to built-in `WebSearch` instead.
- `company_research_exa` — optionally run this for the ticker before the
  searches to get a structured company profile (products, recent news,
  funding/ownership). Useful for stocks with limited vault context.
  Skip if unavailable.

Run exactly 2 searches per ticker. These are not news searches — they're
looking for analyst reasoning and management guidance that the fundamentals
scripts don't capture.

```
"[TICKER] earnings call [most recent quarter and year]"
"[TICKER] analyst outlook [current year]"
```

**What to extract:**
- From the earnings call search: what did management say about guidance,
  growth drivers, or risks? Any forward-looking language that confirms
  or challenges the thesis?
- From the analyst outlook search: what is the sell-side bull/bear thesis?
  Any recent target revisions or rating changes, and what drove them?

**How to use this:**
Feed it into Step 3 (Thesis Validation) and Step 4 (Portfolio Fit & Timing).
If management's guidance contradicts a key thesis assumption, say so explicitly.
If the analyst community's reasoning aligns with or diverges from the vault
thesis, note that in the council setup.

**What to ignore:**
General price movement commentary, short-term trading takes, and anything
already covered in the vault's recent daily reports. You're looking for
durable reasoning, not noise.

**In comparison mode:** run these 2 searches for each ticker independently.
Skip for any ticker whose today's file is being reused from Step 0.

---

### Step 3: Thesis Validation

Cross-reference the original buy thesis (from vault notes) against the
fundamentals just fetched. Answer:

1. **Is the thesis intact, partially intact, or broken?**
2. **Which specific metrics confirm the thesis?** (cite actual numbers)
3. **Which specific metrics challenge the thesis?** (cite actual numbers)
4. **What has materially changed since the buy decision?**

Be direct. If revenue growth is slowing and the thesis assumed acceleration,
say so. If the stock has re-rated to a valuation that prices in the thesis
fully, say so. This section should be uncomfortable to write if things have
changed — that's the point.

---

### Step 3b: Head-to-Head Comparison *(comparison mode only — skip in single-stock mode)*

Run this after completing Steps 1–3 for both tickers. This is the synthesis
layer that the individual deep dives can't provide.

**Side-by-side snapshot:**
Pull the key numbers from both scripts and lay them out in a table:
current price, % off 52-week high, P/E or EV/Revenue (use whichever is
most meaningful per stock — don't force P/E on a pre-profit company),
analyst avg target + implied upside, next earnings date, and which
historical pattern preset is active today for each.

**Thesis alignment:**
Which stock's thesis is more intact right now? Be direct — if one thesis
is clearly stronger at current prices, say so and cite the specific metrics
that make it so.

**Valuation comparison:**
Which is cheaper relative to its growth rate? Use EV/Revenue or forward P/E
divided by growth rate (PEG-style) if the numbers support it. If one is
clearly better value for the expected growth, name it.

**Entry setup comparison:**
Which historical pattern is active for each? A dip-buyer setup vs. an
extended-run setup have very different risk profiles. Cite the actual win
rates from the pattern scripts side by side.

**Risk asymmetry:**
What's the realistic downside for each? Volatility (beta), earnings event
proximity, and any thesis invalidation risk. Which has more bounded downside?

**Allocation logic:**
Given a fixed capital amount (use whatever the user stated, or default to
"standard position size"), what's the case for concentrating vs. splitting?
Splitting dilutes conviction — it's only right if the two stocks are truly
uncorrelated and both have strong setups. If one is clearly better, say so.

---

### Step 4: Portfolio Fit & Timing

This is the section the user reads to answer the actual decision they're
facing. It must be direct. No hedging.

**How to reason here:**
Do NOT try to identify and name scripted scenarios (e.g., "you're
considering pivoting X to Y"). Instead, read everything loaded in Step 1
and reason as if you ARE the user — holding their positions, their plans
at different price levels, their emotional state, their watchlist, their
constraints. The vault gives you all of this. Synthesize it. The user's
real decision is often layered and unstated: it might be "if my current
position hits target next week, which stock do I move to — and does the
timing of a buy now vs. later actually matter?" That question can't be
pulled from a single vault note; it requires holding the full context and
reasoning on their behalf.

Answer what the user is actually wrestling with — even if you have to
infer it. Speak to the real tradeoffs, not a simplified version of them.

**Cover the following:**

**Portfolio context**
- What does the current portfolio look like? What's working, what isn't?
- How does the target stock fit — additive or duplicative exposure?
- Are there plans or price targets documented in the notes that affect
  this decision (e.g., "sell X at $40–45, then rotate")? If so, reason
  through the downstream implications at each price level.

**Timing**
- Is now a good entry point, or is there a better one visible?
  Reason from: proximity to 52-week high/low, pre/post earnings risk,
  recent market run, and whether the stock has already moved on the thesis.
- **Use the historical pattern output from Step 2b.** The script flags which
  preset applies right now (dip zone / extended run / pre-earnings window).
  Cite the actual win rate and average return: e.g., "NVDA has been in the
  dip buyer zone 7 times in 5 years — 30-day win rate 71%, avg +6.2%."
  If the stock is currently in an extended-run zone, cite those numbers to
  quantify the chasing risk. If we're in a pre-earnings window, cite the
  historical earnings-day move distribution.
- If a preset had insufficient history, say so and fall back to qualitative
  reasoning only for that dimension.
- If waiting is smarter: give a specific price level or condition
  (not vague — say "$228–$238" or "after the April 23 print").
- If pre-earnings: be explicit about what bet is actually being made.

**Crux Events & Price Ladder**

Ordering inside this section matters — the user reads top-down and wants
the actionable view first. Lead with the ladder. The reference numbers
go in an appendix block at the *bottom* of the section, not the top.

- **Lead with the buy / hold / trim price ladder.** Every ladder level must
  cite at least one reference number from the *Reference levels* block at
  the bottom of the section (a fair-value band, an ATR distance from
  current price, a DMA, a recent swing low, or an analyst target). This
  is the cross-check: the thesis still picks the level, but the math has
  to back it up.
- **If a ladder level sits outside every reference band** (e.g., Buy Below
  is far below the bear fair-value band), call it out in one sentence —
  either the thesis requires multiple expansion the reference numbers
  don't capture, or the level is too aggressive. Don't smooth it over;
  the disagreement is the signal.
- List crux events in the next ~60 days (earnings, contract news, catalysts
  from the notes, macro events touching the thesis). For each: date,
  positive-outcome price impact, negative-outcome price impact.
- If no crux event within 60 days, state that and skip the EV math.
  Forcing scenarios where none exist creates scaffolding.
- If a crux event is within 30 days, compare buy-now vs. wait-for-resolution
  with arithmetic: target price × upside %, with tail scenarios weighted in.
  Often paying up for derisking is mathematically superior to "getting a
  deal" while tail risk is live — let the math decide, don't assume cheaper
  is better. Targets also tend to get revised up after derisking events.
- Common trap: framing it as binary ("buy now at X vs chase at Y"). There's
  usually a third option — a pre-earnings window, a different catalyst, a
  macro dip. Reason across the full set of entry opportunities.
- **End the section with the *Reference levels* block** (see template) using
  the numbers from Step 2 (`fairValueBands`) and Step 2b (`levelContext`):
  fair-value bear/base/bull, a 2-column Volatility & technicals mini-table
  (ATR(20), 50 DMA, 200 DMA, recent swing lows), and the analyst target
  range. Use the script's `suggested` field to choose which fair-value
  method is labeled primary (fwd-P/E vs P/S), but emit both when both are
  computable — the non-primary one is useful color. Keep this block
  compact; it is appendix, not narrative.

**Sizing**
- Given conviction and portfolio composition, how much is appropriate?
  Starter / add / full position / already sized correctly?

**The Direct Take**
2-3 sentences. Directly answer the question the user is most likely
wrestling with, given everything in the vault. Yes / No / Wait until X.
No hedging.

---

### Step 4b: Blank-Slate Reframe

A separate check on the sizing conclusion from Step 4. Forget current
holdings entirely. Imagine the user has only cash and is building a
portfolio from scratch today — same vault context, same theses, same
fundamentals you just analyzed, but no existing positions to anchor on.

Answer two questions:

1. **Would you buy this stock at today's price at all, starting from zero?**
   Not "is the thesis intact," not "is it a hold." Would you initiate a
   position today given everything you know?
2. **How much would you allocate?** Name a specific % of total portfolio
   (or specific $ amount if the total is known from Journalit / notes).

**Anchor in today's numbers.** The blank-slate sizing must cite the
current price (Step 2) and the ladder built in Step 4 — not a buy-below
or fair-value target lifted from a note older than ~30 days that this
deep dive hasn't re-derived. If you catch yourself re-using a stale
anchor, re-derive from this run's `fairValueBands`, analyst targets, or
pattern levels. Stale anchors are the main failure mode here — they
let the blank-slate recommit to yesterday's thesis at yesterday's
price, which is the opposite of what this check is for.

Compare blank-slate to current, **diagnose the gap source** (price
action since entry vs. fresh-conviction change vs. both), then apply
the P&L-direction override:

| Raw bucket | Default signal | Override (P&L direction × thesis state) |
|---|---|---|
| Blank-slate ≈ current | Confirms HOLD | None. |
| Blank-slate > current | Supports ADD | If thesis *weakening* per Step 3, downgrade to HOLD — don't add into a degrading thesis just because price came to you. |
| Blank-slate < current | Supports REDUCE | If *winning + thesis intact*: override to HOLD (let winners ride; the gap is appreciation, not stale conviction). If *losing + thesis broken*: REDUCE to zero (full exit), not partial trim — REDUCE alone is too soft. |
| Blank-slate ≈ 0 | Exit candidate (REDUCE to zero) | If *thesis intact + deeply underwater* and the only reason blank-slate is zero is price action: downgrade to REDUCE (partial) or HOLD — don't capitulate on price alone. If thesis is broken: REDUCE to zero stands. |

The override only fires when you've named both axes (P&L direction +
thesis state). If both moved since entry, name both — that's the most
informative case.

**Apply the empirical priors here.** [[C9 - Most Stocks Underperform T-Bills]]
is the base-rate spine of the blank-slate question — concentration is only
rational with specific power-law-upside evidence, so either name that
evidence or size down. And when the position is underwater, the P&L override
must distinguish [[C6 - Disposition Effect]] (loss aversion — the data says
the held loser tends to keep losing, so lean exit) from
[[C10 - Limits to Arbitrage]] (thesis-intact, constrained-capital divergence —
hold, but *only* with a written falsification line, never as a bare excuse).

**This is the anti-status-quo check, but the override stops it from
becoming an anti-momentum check.** When the resolved action conflicts
with the Step 4 sizing conclusion, name the conflict — the verdict in
Step 7 addresses it directly.

**Data sources:**
- Current position size, cost basis, unrealized P&L: Journalit (via
  `get_positions.py` from Step 1) — don't fabricate.
- Total portfolio value: Journalit or user-stated. If neither is
  available, reason in % terms only and note that.
- Thesis state: the Step 3 verdict (intact / partial / broken).

**In comparison mode:** joint blank-slate — imagine the stated capital
amount, no positions in either ticker, allocate across TICKER_A,
TICKER_B, and cash. Apply the P&L override per ticker before feeding
Step 7's allocation verdict.

---

### Step 4c: Implied Expectations (Thesis Math)

Make the valuation **spine** explicit: convert the thesis into one equation that
states *what today's price requires you to believe*, with every input sourced,
then derive the threshold that would prove it wrong. This is a **verifier**, not
the thesis engine — it cross-checks the Step 4 ladder and the Step 7 verdict; it
never originates them and never emits a price target.

Renders as the `## Implied Expectations` section, placed **below** the actionable
ladder/timing in the output (see template) — the human-actionable view stays on
top; the math sits underneath as the check.

**Build it:**

1. **Pick the archetype equation** that fits the name (units on every term — a
   term with no unit and no source doesn't go in the equation):
   - **Multiple / backlog name** (VRT-type): `equity value ≈ contracted backlog
     × op-income conversion(%) × exit multiple − net financing need − net debt`;
     quick form: price-to-backlog = market cap ÷ contracted backlog.
   - **Cash-flow name:** reverse-DCF — solve for the revenue CAGR / terminal
     margin that today's price *implies*, then judge whether that's plausible.
   - **Unit-economics infra** (GEV / CEG / DLR-type): `value ≈ Σ(contracted MW ×
     $/MW/yr × steady-state margin) discounted − net debt` — the binding
     constraint (power, land, contracts) is an explicit variable.
2. **Fill the variables table** — `Variable | Today's value | Source | Verdict
   flips if →`. Every value must trace to Step 2/2b script output or a Step 2d
   filing/transcript. No invented inputs.
3. **State what has to be true** — solve for the **break-even threshold**: the
   implied growth / conversion rate / multiple that makes today's price fair, then
   judge it plausible or heroic. **"Break-even probability" is a reserved term — it
   means the Monte Carlo output (P(implied ≥ price)) and nothing else.** When you
   have NOT run the script, state a break-even *threshold* or *required assumption*
   ("the price requires ≥X% of the targeted ARR to convert"), **never** a typed-in
   probability — both "P(bull) = 40%" and "the bull case is ~55% likely" are
   forbidden ([[C8 - Kelly Criterion and Position Sizing]]: no fake-precise
   probabilities, ever). Do **not** sum heterogeneous factors into a single
   "quality score" — name the factors, don't add apples to percentages.
4. **Name the crux variable** — the single input the verdict is most sensitive to.
5. **List the falsification thresholds** — the number/date/event that breaks the
   equation. These are the inputs to Step 8e; they should match the tripwires you
   write to `vault/tripwires.md`.
6. **Tag the math check** — `Corroborates` or `In tension with` the verdict. The
   math is subordinate to the Step 7 verdict and never competes with it as a
   third verdict — but if it lands *In tension*, say so in one sentence rather
   than smoothing it over. Tension is the signal to re-examine the verdict.

**Quantify the break-even with Monte Carlo when the inputs are sourceable.** If the
equation is cleanly quantifiable and you can source a low/base/high for each
uncertain input (analyst low/mean/high, guidance band, historical vol, the Step 2
fundamentals, the dossier), build a JSON spec and run the simulation instead of
hand-waving the probability:

```bash
python .claude/scripts/monte_carlo_valuation.py --spec-file spec.json --format human
```

Cite the resulting **break-even probability** (= P(implied ≥ today's price)), the
p25–p75 implied-price band, and the **crux variable** (the script's top sensitivity
entry — it should match the crux you named in step 4). Report the break-even
probability, *not* the p50 as a "fair value." Keep the default seed so the number
is reproducible. Models + spec format: `.claude/scripts/quant-tools.md`. If the
inputs aren't cleanly sourceable, reason the break-even qualitatively and skip the
simulation — a Monte Carlo on guessed ranges is false precision, not rigor. When
you run it, record the break-even probability in Step 8's `log_verdict` call so it
survives in the ledger.

**If the thesis names no falsifiable, quantifiable constraint at today's price**
(the verdict rests on a qualitative driver — a pending catalyst, a sentiment
read), write one line — `No binding implied-expectation constraint at $X —
verdict rests on {{driver}}.` — and move on. Do not manufacture an equation to
fill the section; a forced model is exactly the false-precision failure this
block exists to avoid.

**Comparison mode:** run this per ticker inside each individual deep-dive file.
The comparison file itself does not get an Implied Expectations section — its
math is the head-to-head valuation table (Step 3b).

---

### Step 5: Conviction Check

Pressure-test the position against the *strongest version of your own
long-term thesis*. Would a high-conviction holder of that thesis buy this
name at today's price, or wait for a dip? The point is to separate "good
company" from "good entry," and to stop a broad secular thesis from
auto-justifying any price. Using the fundamentals from Step 2:

- **Would a high-conviction holder still buy this stock at its current
  price?** Ground this in the actual P/E, price vs. analyst target, and how
  the stock fits (or doesn't fit) the long-term thesis.
- **Or would they wait for a dip?** If so, at what specific price level?
  Reason from valuation multiples or technical levels, not vibes.
- **Or would they rotate to a different name?** If so, which one and why —
  what looks more compelling under the thesis right now?

This should be 2-4 sentences tied to specific numbers. Not a generic
"the secular thesis is bullish" take.

---

### Step 6: 3-Advisor Mini-Council (run sub-agents in parallel)

Spawn three sub-agents simultaneously. Each receives:
- The original buy thesis (from vault)
- A structured fundamentals summary (key numbers from Step 2)
- Their specific role and thinking style

Each advisor writes 150-200 words. No hedging. No balance. Each represents
one angle as strongly as the evidence supports.

**In comparison mode:** reframe the council around the allocation question.
Each sub-agent receives both tickers' fundamentals and is explicitly asked
to weigh in on the allocation, not just analyze a single stock:
- **Contrarian:** argues against the obvious choice — whichever stock looks
  better on paper. What's the bear case for the "winner" of Step 3b?
- **Bull:** makes the case for the underdog — the less obvious pick. What is
  the market underpricing in the stock that looks weaker at first glance?
- **First-Principles:** ignores the comparison framing entirely. Reasons from
  scratch: which of these two businesses, at these prices, is the better
  long-term bet for this specific user given their vault context?

---

**Contrarian sub-agent prompt:**

```
You are the Contrarian advisor in a stock analysis council.

Your job: find what's wrong. Assume there is a fatal flaw in the thesis
and try to identify it. Look at the fundamentals for evidence that the
bear case is more likely than the bull case. Be specific — cite numbers.

Stock: {{TICKER}}
Original thesis: {{thesis from vault}}
Key fundamentals: {{structured summary}}

150-200 words. No hedging. What's the bear case?
```

---

**Bull sub-agent prompt:**

```
You are the Bull advisor in a stock analysis council.

Your job: find what the market is underpricing. Look at the fundamentals
for evidence that the upside case is stronger than consensus suggests.
What would this look like if things go better than expected? Be specific
— cite numbers and name the mechanism.

Stock: {{TICKER}}
Original thesis: {{thesis from vault}}
Key fundamentals: {{structured summary}}

150-200 words. No hedging. What's the bull case?
```

---

**First-Principles sub-agent prompt:**

```
You are the First-Principles advisor in a stock analysis council.

Your job: ignore price action and sentiment. What does this company
actually do? Who pays them and why? Is there a durable structural reason
for that to continue? Work from the ground up to decide if the current
valuation makes sense for what this business actually is.

Stock: {{TICKER}}
Original thesis: {{thesis from vault}}
Key fundamentals: {{structured summary}}

150-200 words. No hedging. What does first-principles analysis say?
```

---

### Step 7: Verdict Synthesis

Read all three advisor outputs and produce a final verdict. **The verdict is
placed at the top of the output file** (right after the Snapshot), not at the
bottom — re-reads of a deep dive are usually just the verdict, so it goes
first. Write it last (after the Council work informs it), but position it
at the top.

Exactly one of:

| Verdict | When to use |
|---------|-------------|
| **HOLD** | Thesis intact, current price reasonable — no strong case to add or reduce |
| **ADD** | Thesis intact AND current price is attractive vs. fundamentals/targets |
| **REDUCE** | Thesis weakening OR price materially ahead of what fundamentals support |
| **WATCH** | Insufficient signal — name the specific trigger or price to revisit |

Follow with 3-5 sentences. Do not just restate that the thesis is intact —
address the *action*: should the user buy more right now, at this price,
or not? Reference where advisors agree or clash. Reference the Portfolio Fit
& Timing section's conclusion. **If the Step 4b blank-slate reframe
conflicts with the Step 4 sizing conclusion (e.g., blank-slate says
overweight but Step 4 landed on HOLD), resolve it here — the verdict must
face that conflict directly, not smooth it over.** No "it depends." WATCH
requires a specific price level or catalyst to revisit, not a vague condition.

**In comparison mode:** replace the standard verdict with an allocation verdict.
Exactly one of:

| Allocation Verdict | When to use |
|-------------------|-------------|
| **ALL [TICKER]** | One stock is clearly the better use of capital right now |
| **SPLIT [X% TICKER A / Y% TICKER B]** | Both have strong setups AND they are genuinely uncorrelated — concentration into one is not clearly right. Name the specific percentages. |
| **WAIT** | Neither is a compelling entry right now — name what to wait for (price level or catalyst) for each |

Follow with 3-5 sentences answering: which stock wins and why, what the
deciding factor was, and whether the loser is worth revisiting (and when).
Splitting is not a hedge — only recommend a split if the two stocks are
genuinely additive to each other in the portfolio. If one is just
"safer," that's not a reason to split — it's a reason to size smaller.

---

### Step 8: Write Output & Clean Up

**Single-stock mode:** write to `vault/deep-dives/[TICKER]-YYYY-MM-DD.md`
using the single-stock template in `references/deep-dive-template.md`.

**Comparison mode:** write only the files that don't already exist from
today (per the staleness check in Step 0):
1. `vault/deep-dives/[TICKER_A]-YYYY-MM-DD.md` — skip if already exists today
2. `vault/deep-dives/[TICKER_B]-YYYY-MM-DD.md` — skip if already exists today
3. `vault/deep-dives/[TICKER_A]-vs-[TICKER_B]-YYYY-MM-DD.md` — always write

The individual files are complete standalone reports — future agents can
read them without knowing a comparison was run. The comparison file is the
synthesis layer: head-to-head table, reframed council, and allocation verdict.

If `vault/deep-dives/` doesn't exist, create it first.

**After writing each file, delete stale files for that ticker:**

Agents only ever read the most recent deep dive per ticker. Older files
are never used. After writing (or confirming today's file already exists),
delete all previous files for that ticker in `vault/deep-dives/`:

- For each ticker written: delete all `TICKER-*.md` files where the date
  in the filename is not today. Example: if today is 2026-04-15 and
  `NVDA-2026-04-10.md` exists, delete it.
- For comparison files: delete all `TICKER_A-vs-TICKER_B-*.md` files
  where the date is not today. The ticker order in the filename must
  match — `NVDA-vs-VRT` and `VRT-vs-NVDA` are treated as separate
  patterns; clean up both.
- Never delete today's files.
- Never delete files for other tickers.

**After writing each individual deep-dive file, append a row to the verdict ledger:**

```bash
python .claude/scripts/log_verdict.py \
    --ticker TICKER \
    --verdict {{HOLD|ADD|REDUCE|WATCH}} \
    --price {{snapshot price}} \
    --file TICKER-YYYY-MM-DD.md \
    --breakeven-prob {{Step 4c break-even probability as 0-1, e.g. 0.45; omit if none}}
```

Use the `Price` value from the file's Snapshot table (e.g., `$41.47` →
`--price 41.47`) and the verdict from the frontmatter you just wrote. Pass
`--breakeven-prob` only when Step 4c produced a quantifiable break-even
probability (omit the flag entirely otherwise — it records `—`). The
script appends one row to `vault/deep-dives/_verdicts.md` and is idempotent
— re-runs for the same filename are silent no-ops, so it's safe to call
this even if the auto-deep-dive chain fired the same skill twice.

**Comparison mode:** call once for each individual deep-dive file written
(skip if the file already existed and was reused — no new verdict). The
comparison file (`TICKER_A-vs-TICKER_B-*.md`) is NOT logged; allocation
verdicts don't map to a single ticker's drift.

The ledger feeds two consumers: `news-analyst` runs
`check_verdict_drift.py` daily to surface tickers where price has moved
≥10% since the verdict, and `quarterly-review` reads it for the
calibration pass.

### Step 8b: Update Broader Price Triggers (conditional)

**Only applies to tickers NOT in `vault/watchlist.md`.** For watchlist
tickers (any tier), this step is skipped — watchlist updates happen via
Step 8c (Watchlist Updates), which writes directly to
`vault/watchlist.md` via the shared apply script.

**When the ticker is not on the watchlist**, upsert one row into
`vault/price-triggers.md` based on the Crux Events & Price Ladder
produced in Step 4:

1. Read `vault/price-triggers.md`. Parse the `## Price Triggers` table.
2. Extract the levels from the Step 4 ladder:
   - `Buy Below` = the clearest ADD level named in the ladder (lowest
     "buy zone" dollar level, not a range midpoint).
   - `Trim Above` = the clearest TRIM level. Leave `—` if the ladder
     doesn't name one (don't fabricate a sell level just to fill the cell).
3. If a row for this ticker already exists, **replace** it. Otherwise,
   **append** a new row. Preserve the existing order of other rows.
4. Populate the columns:
   - `Last Reviewed` = today's date (YYYY-MM-DD). This resets the 30-day
     staleness clock.
   - `Funded-by` = short free-text capital source for the Buy side, if the
     deep dive's Portfolio & Timing section named one (e.g., `"DLR trim
     tranche 2"`, `"cash"`, `"post-May-5 rotation"`). Leave `—` if unstated
     or if only a trim level is being set. Keep under ~40 chars.
   - `Prefer-over` = comma-separated tickers this one should be funded
     before if both fire the same day (derived from the deep dive's
     Opportunity-cost / vs.-Current-Holdings reasoning). Leave `—` if the
     deep dive doesn't rank this entry against other named candidates.
   - `Note` = a short free-text phrase summarizing what the level
     represents (e.g., `"Analyst-target low-end"`, `"Post-dip entry"`).
     Keep under ~60 chars.
   - `Source` = `[[TICKER-YYYY-MM-DD]]` — wikilink to the deep-dive file
     just written.
5. If the ladder names neither a buy nor a trim level, skip the upsert
   entirely. Don't write empty rows.

**Comparison mode:** apply the same rule independently for each ticker
side of the comparison — each gets its own upsert (or skip) based on
its own ladder and watchlist status. Don't write a row for the
comparison file itself.

For watchlist tickers, use Step 8c (Watchlist Updates) — that step writes
directly to `vault/watchlist.md` via the shared apply script after writing
the proposal block to this file. Both `vault/price-triggers.md` (here) and
`vault/watchlist.md` (Step 8c) are first-party writers from this skill.

---

### Step 8c: Watchlist Updates (conditional)

**Only applies to tickers that ARE on `vault/watchlist.md`** (any tier).
For non-watchlist tickers this step is skipped — those go through Step 8b
into `vault/price-triggers.md` instead.

**What this is:** a markdown block appended to the deep-dive file (see
the Proposed Watchlist Updates section in
`references/deep-dive-template.md`). The block is the audit trail —
human-readable record of what the deep dive proposed. After writing it,
Step 8d (below) immediately applies it to `vault/watchlist.md` via the
shared script, so the new triggers/tranches are live in the intraday
Pushover loop the same day.

**How to fill it:**

1. **Price Trigger subsection** — propose the refreshed buy/trim levels
   based on the Crux Events & Price Ladder from Step 4. **Both Buy Below
   and Trim Above must reflect the levels named in the ladder. Distance
   from spot is irrelevant** — a "Trim above $200" line in the ladder
   gets propagated even if spot is $138 and the deep dive flags it "not
   actionable today." That phrase means "won't fire today," not "skip
   the trigger" — forward-looking triggers exist precisely to fire when
   price gets there.
   - `Buy Below`: clearest ADD level from the ladder. Write `unchanged`
     only if this deep dive doesn't revise an existing level. Write `—`
     only to deliberately clear an existing buy side.
   - `Trim Above`: clearest TRIM level from the ladder. Same conventions.
     If the ladder names any "Trim above $X" / "Don't hold above $X" /
     "Engineered cap $X" level, propagate it as the price — never default
     to `unchanged` when the body produced a fresh level.
   - `Funded-by`: where the capital comes from when the Buy trigger fires
     — derive from the deep dive's Portfolio & Timing / Sizing sections.
     Format: short free-text under ~40 chars (e.g., `"DLR trim tranche 1"`,
     `"cash"`, `"post-May-5 rotation"`). Write `unchanged` to keep the
     existing value, `—` to clear, or omit the key to keep the existing
     value. Applies to the Buy side only — blank on trim-only rows.
   - `Prefer-over`: comma-separated tickers this one should be funded
     before if both fire the same day. Derive from the deep dive's
     Opportunity-cost lens and vs.-Current-Holdings reasoning — if the
     deep dive says "VRT tranche 1 wins the marginal dollar over DLR
     and GEV," this row's `Prefer-over` is `DLR, GEV`. Write `unchanged`
     or omit to keep existing; `—` to clear. Applies to the Buy side only.
   - `Note`: short replacement note (under ~80 chars). Omit the key to
     keep the existing note.
   - `Confidence`: one of `low`, `med`, `high`. The apply script (Step 8d)
     applies `med` and `high` directly; `low` is logged as skipped so the
     user can review and apply manually. Calibrate:
     - `high` — a crux event resolved or a specific ladder level is
       grounded in hard numbers (analyst target low-end, explicit thesis
       invalidation level, earnings-derisked price).
     - `med` — the level is reasoned but could reasonably move within a
       week (e.g., within-range of analyst target, qualitative catalyst
       timing).
     - `low` — speculative, or the deep dive itself is uncertain. Prefer
       this when the verdict is WATCH.

2. **Planned Tranches subsection** — only include if the Step 4 analysis
   points toward explicit staged buys or trims. Use `Add:` lines for new
   tranches and `Remove:` lines for tranches the deep dive invalidates.
   If the deep dive has no view on tranches, write `No tranche changes.`
   under the subsection. Never fabricate tranches just to fill space.

   Each `Add:` line includes an `order=` field — `GTC`, `Alert`, or
   `Conditional GTC`. Choose deliberately:
   - **GTC** when the level is fire-and-forget: unconditional trims at or
     past the thesis target, or unconditional buys at a thesis-confirmed
     level. No human gate needed at the moment of fire. Right for trim
     levels especially — overnight gaps and intraday spikes will execute
     a GTC that an alert misses.
   - **Alert** when a human gate is the entire point. Anything subject to
     [[macro-cohort-confirmation]] (cohort-red gate before pulling the
     trigger), [[Opportunity-cost lens]] same-day capital-collision
     ranking, or pre-binary tranches where intraday context governs the
     decision. The default for buy-side levels in the AI infra cohort.
   - **Conditional GTC** when the gate is a single discrete event (a
     print, an energization announcement, a contract signing). Until the
     event resolves, behaves as Alert. After the event, the user converts
     it to a real GTC. Put the gating condition in the `note` field so
     the user knows what to wait for.

3. **Rationale** — one sentence tying the proposal back to this specific
   deep dive's findings (not vague — name the metric, target, or catalyst
   that drove it). Read by the user during weekly-review diff audit.

**If this deep dive has no changes to propose** (verdict is HOLD and the
existing watchlist levels still fit), still emit the section and write:

```
### Price Trigger
- **Ticker:** {{TICKER}}
- **Buy Below:** unchanged
- **Trim Above:** unchanged
- **Funded-by:** unchanged
- **Prefer-over:** unchanged
- **Note:** unchanged
- **Confidence:** high
- **Rationale:** No change — current levels still reflect the thesis.

### Planned Tranches
No tranche changes.
```

This explicit "no change" signal lets the apply script bump `Last Reviewed`
on the Price Triggers row (preventing 30-day staleness from killing the
trigger) without actually modifying the levels.

**Comparison mode:** each individual deep-dive file includes its own
Proposed Watchlist Updates section if its ticker is on the watchlist.
The comparison file itself does not — it's a synthesis document, not a
per-ticker proposal surface.

---

### Step 8d: Apply to watchlist.md

Immediately after Step 8c writes the proposal block, run the shared
apply script to write the changes into `vault/watchlist.md`:

```bash
python .claude/scripts/apply_watchlist_updates.py vault/deep-dives/TICKER-YYYY-MM-DD.md
```

The script parses the `## Proposed Watchlist Updates` block from the
deep-dive file and upserts into `vault/watchlist.md` → `## Price Triggers`
and `## Planned Tranches`. It is idempotent (re-applying is a no-op apart
from refreshing `Last Reviewed`). `med` and `high` confidence levels apply;
`low` is logged as skipped.

This replaces the old propose-via-block / weekly-review-promotes pattern.
Now that intraday Pushover notifications fire on `## Planned Tranches`
rows, trigger freshness matters more than batched consolidation —
proposals must land in the watchlist on the same day.

**Comparison mode:** call the script once per individual deep-dive file
(each side of the comparison). Skip on the comparison file itself.

---

### Step 8e: Thesis Tripwires (write/refresh)

Convert the **Step 3 Thesis Validation** invalidation criteria **and the
Step 4c falsification thresholds** into 1–3 **measurable** tripwires and upsert
them into `vault/tripwires.md` (the falsification ledger — see that file's header
for schema). The Step 4c thresholds are already number/date/event-shaped, so they
map to tripwire rows directly — keep the two in sync (a tripwire that isn't a
Step 4c falsification threshold, or vice versa, is a drift signal worth a second
look). Each tripwire must
name a number, date, or event that would prove the thesis wrong (e.g.,
"gross margin negative 2 consecutive quarters", "contracted power capacity
still <X GW by YYYY-MM-DD"); **"stock drops" is not a tripwire** — pure price
levels belong in the watchlist / price-trigger tables (Steps 8b–8d).

- Append rows with `Type` (fundamental / event / price), `Set` = today,
  `Source` = `` `TICKER-YYYY-MM-DD` `` (backticked, **not** a `[[wikilink]]` —
  the deep-dive file is auto-deleted when superseded, and a dead wikilink
  becomes an Obsidian phantom note; same convention as `_verdicts.md`),
  `Status` = `ARMED`.
- Mark `RETIRED` any prior ARMED tripwire for this ticker that this deep-dive
  supersedes (the thesis changed).
- If the thesis names no falsifiable condition, write none — don't fabricate.
- **Comparison mode:** do this per ticker; skip the comparison file itself.

---

## Constraints

- **Never write to `notes/`, `library/`, or `reports/` directly.**
  Output goes to `vault/deep-dives/` (deep-dive files, which include a
  Proposed Watchlist Updates block for watchlist tickers),
  `vault/price-triggers.md` (non-watchlist ticker rows via Step 8b),
  `vault/watchlist.md` (watchlist tickers via Step 8d's apply script),
  and `vault/tripwires.md` (thesis tripwires via Step 8e).
- **Output checklist — verify before reporting the run complete:**
  1. Deep-dive markdown written to `vault/deep-dives/TICKER-YYYY-MM-DD.md`.
  2. Verdict logged via `log_verdict.py` (single-stock runs only), with
     `--breakeven-prob` when Step 4c produced a Monte Carlo break-even.
  3. **If watchlist ticker:** the file contains a `## Proposed Watchlist
     Updates` H2 heading, with a `### Price Trigger` subsection where both
     `Buy Below` and `Trim Above` reflect the Step 4 price ladder (not
     defaulted to `unchanged` when the ladder produced fresh levels), and
     `apply_watchlist_updates.py` was invoked against the file. Skipping
     the block is a defect — silent levels in the ladder body do not
     propagate to the intraday Pushover loop.
  4. **If non-watchlist ticker:** Step 8b row upserted into
     `vault/price-triggers.md` (or skipped per Step 8b rule 5).
- **No fabricated numbers.** Every figure in Snapshot and Fundamentals
  must come from the FMP script output. If unavailable, write "N/A".
- **Abort on total script failure.** If the script returns no data at all,
  stop and tell the user what went wrong rather than proceeding blind.
- **Verdict is required.** One of four options. No waffling.
- **Council advisors don't self-censor.** Each represents one angle fully.
  If the Contrarian sees a fatal flaw, they say it clearly.
