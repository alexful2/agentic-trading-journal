---
name: news-analyst
description: >
  Daily personalized portfolio news alert. Scans the user's Obsidian vault
  (notes/ for stock decisions and theses, library/ for principles and
  worldview, trades/ for open positions), gathers news via the active
  agent's web-search tool, and
  writes a severity-scored alert to `vault/reports/daily/`. Only severity
  ≥3 items are surfaced; sev 1–2 are filtered out as noise. The daily
  report is an alert, not an essay — deeper analysis is the job of the
  `stock-deep-dive` skill, which this alert triggers via action lines.
---

# News Analyst

## Runner Compatibility

This skill can run under Claude or Codex. Use the best current web-search
tool exposed by the active agent:

- Claude runs should prefer Exa MCP (`web_search_exa`) when available.
- Codex runs should use Codex native web search (`--search` on the CLI).

Do not skip searches because the preferred tool name differs between agents.
The report should name the actual agent/model in the footer.

## Purpose

Surface news that matters to my specific portfolio **today**. The output is
an alert — flag what deserves attention, name an action (often "run a
deep-dive"), and stop. Essays, persona checks, and opportunity surveys live
in other skills (`stock-deep-dive`, `weekly-review`, `vault-curator`).

## Workflow

### Step 1: Load Portfolio Context

Apply temporal reasoning (see CLAUDE.md) when reading notes — newest wins, flag revisions.

**From `vault/watchlist.md` (read first):**
- Load the tiered stock list.
- Tier 1 = current holdings (always search).
- Tier 2 = active watchlist (search on rotation).
- Tier 3 = peripheral interest (passive only, no dedicated searches).

**Cross-reference with the trade log (via `get_positions.py`):**

Run the position helper instead of scanning trade files yourself (it reads
`vault/trades/`, or `vault/!Journalit/` for Journalit users):

```bash
python .claude/scripts/get_positions.py --format json
```

Returns one row per OPEN position (entries minus exits > 0) with: shares,
weighted-avg cost, realized P&L from partial exits, current Stooq price,
unrealized %, and total P&L. Use these numbers later when:

- An item touches a held ticker — cite the actual position context, not
  vague "this is held." Good: "NVDA is +10% on 4 shares from $239.60";
  bad: "NVDA is in the portfolio."
- A fired price-trigger item is for a held ticker — name the unrealized
  context so the reader sees the trim/add in scale.
- The Direct Take or Action line touches sizing — cite the live unrealized
  % (it materially changes the read on a trim level).

Tickers in OPEN positions that are NOT in watchlist Tier 1 are an
inconsistency — flag them once in macro awareness ("Position in {ticker}
not reflected in watchlist tiers") so the reader can fix one or the other.

**From `vault/notes/`:**
- Read all files. Extract per-stock theses, rationale, past decisions,
  risk rules, and invalidation criteria.

**From `vault/library/`:**
- Read all files **except `vault/library/research/`**. Extract worldview,
  principles, and frameworks.
- **Skip `vault/library/research/`** — the empirical-priors catalog (C1–C13)
  is a set of decision-time calibration priors for `stock-deep-dive` and
  `pre-earnings`, not a daily-news input. Bulk-reading it every run is
  recurring token cost for notes that rarely bear on a given day's headlines.

**From the story ledger (durable "already-covered" memory — authoritative):**

Run:

```bash
python .claude/scripts/story_ledger.py --render
```

This prints every narrative thread you've surfaced before — keyed on
ticker + theme, with first/last-seen dates, times-seen, and last severity —
split into **Active** and **Dormant**. This is your **authoritative
recently-covered set** and replaces the old 3-day window: it remembers a
slow-burn story (e.g. a fund's standing stake in a held name) even if it went
quiet for weeks, so a resurfacing story is recognized as a repeat or an update
rather than re-flagged as brand-new. You use it in Step 3 to classify each item
and in Step 5 to record today's sightings. Each thread shows its stable `id`
(e.g. `nbis-leopold-stake`) — note these; you reuse the `id` in Step 5 when an
item belongs to an existing thread. If the ledger is empty (first run), every
item is new — that's expected.

**From `vault/reports/daily/` (recent prose context — last 3 reports):**

List files in `vault/reports/daily/`, sort by filename (`YYYY-MM-DD.md`),
and read the three most recent. The ledger above is the dedup authority; these
three files just give you recent *prose/framing* context (how a thread was last
worded, what action line it carried) so an "(Update)" reads as continuous with
the last coverage rather than disconnected.

**From `vault/deep-dives/` (verdict context — most recent per watchlist ticker):**

For each Tier 1 and Tier 2 ticker (and any other ticker confirmed as an
open position in the trade log), find the most recent deep dive file
(`TICKER-YYYY-MM-DD.md`) and read it. If no deep dive exists, skip
silently.

Extract:
- The verdict (HOLD / ADD / REDUCE / WATCH) and the date it was issued.
- Any specific price levels or conditions named.
- Any thesis flags or invalidation criteria called out.

Use this in Step 4 to frame news against standing verdicts. If today's
news materially changes a verdict condition, the item gets sev ≥3 and the
action line calls it out.

**Do NOT read `vault/reports/weekly/` or `vault/vault-suggestions/`.**
The daily alert is self-contained — macro context comes from today's
broad searches. The weekly-review file is only loaded on Fridays in
Step 6 when building the email brief's Weekly Review section.

### Step 1b: Price Trigger Check

Separate signal from news flow. Two inputs:

- `vault/watchlist.md` — `## Price Triggers` table for tickers I own or
  actively watch. Fires here are first-class actionable items.
- `vault/price-triggers.md` — broader stocks not on the watchlist. This
  is opportunistic ("spot a good deal if it passes by"). Fires here are
  a lighter heads-up.

Run the script once per file, labelling the results so the two can be
routed to different report sections:

```bash
python .claude/skills/news-analyst/scripts/check_price_triggers.py \
    --watchlist vault/watchlist.md --label watchlist \
    --output trigger_results_watchlist.json

python .claude/skills/news-analyst/scripts/check_price_triggers.py \
    --watchlist vault/price-triggers.md --label broader \
    --output trigger_results_broader.json
```

Each result row has:
- a `label` field (`watchlist` or `broader`),
- a `type` field (`trigger` or `tranche`),
- a `status` field — for triggers: `FIRED_BUY`, `FIRED_TRIM`, `ARMED`,
  `IDLE`, `STALE`, `ERROR`; for tranches: `FIRED_TRANCHE_BUY`,
  `FIRED_TRANCHE_TRIM`, `ARMED`, `IDLE`, `EXPIRED`, `ERROR`.
- (triggers only) `funded_by` — short text like `"DLR trim tranche 1"`
  or null. Pass-through free text from the table — the script doesn't
  validate or resolve it; render it to the reader.
- (triggers only) `prefer_over` — list of tickers this row should be
  funded before if both fire the same day.
- (triggers only) `deferred_due_to` — list of tickers (possibly empty)
  that fired on the same day AND name this ticker in their `prefer_over`
  list. Populated by the script's collision detector. Non-empty list
  means the reader should see this fire but not act on it — another
  preferred fire is consuming the capital first.

Tranche rows come from a `## Planned Tranches` table in `vault/watchlist.md`
(the broader file has no tranches section). A tranche is an explicit staged
buy/sell at a known price — different from a trigger, but surfaced in the
same place in the daily report with a different label. Tranche result rows
carry an additional `order` field — one of `GTC`, `Alert`, `Conditional GTC`,
or empty (legacy rows pre-Apr 2026). This field governs the action line
rendered for fired tranches; see the rendering rules below.

**How fired triggers and tranches enter the report:**

Price-trigger and tranche fires are **routine "your level hit" reminders**, not
breaking news. They render as one-line bullets in a dedicated
**`## Price Levels Hit`** section placed directly **below the H1 and above
the News items section** (i.e., the very first body section). They do NOT
get `### TICKER — …` sev-3 headers, and they do NOT mingle with news items.

*Watchlist trigger fires (`FIRED_BUY` / `FIRED_TRIM`, label=watchlist, type=trigger):*
- One bullet per fire (subject to the merge rule below).
- Bullet format:
  `- **TICKER — $X hit ({{buy zone | trim zone}}).** {{one short sentence: what this level represents from the Note}}. {{Funded by Y.}} {{⚠ Capital collision …}} → {{action}}`
- The action verb at the end of the line is short:
  - Buy trigger only (no tranche on this ticker today) → `→ run deep-dive TICKER` (the deep-dive is the next step before sizing).
  - Trim trigger only → `→ run deep-dive TICKER`.
- **Funded by** appears inline (not on its own line) only if `funded_by`
  is non-null and the fire is a `FIRED_BUY`. Pass through the vault's
  text verbatim; do not try to resolve whether the capital source is
  actually available today.
- **Capital collision** appears inline as `⚠ {{preferred ticker(s)}} also
  fired today, preferred first — defer.` only if `deferred_due_to` is
  non-empty. Join multiple tickers with `, ` and phrase naturally
  (single: "preferred first"; multiple: "preferred first").
- **Deferred fires short-circuit the auto-deep-dive chain** (see Step 4b):
  a `FIRED_BUY` with non-empty `deferred_due_to` does NOT qualify as a
  Step 4b candidate. The preferred ticker whose fire caused the deferral
  is the one that should consume any auto-deep-dive budget, not this one.
- **News interaction:** if Step 2 surfaces same-ticker news with
  thesis-changing material at sev ≥ 3, render the news item normally in
  the News section AND keep the one-liner in Price Levels Hit — cross-
  reference them with a short tail on the price-level bullet
  (`see News item below`). Do not collapse a price-level fire INTO a
  news item; the two have different read-modes (level-hit vs. headline).

*Watchlist tranche fires (`FIRED_TRANCHE_BUY` / `FIRED_TRANCHE_TRIM`, label=watchlist, type=tranche):*
- One bullet per fire, in the same `## Price Levels Hit` section as triggers
  (subject to the merge rule below).
- Bullet format:
  `- **TICKER — $X tranche hit ({{Size}}, {{Buy|Trim}}).** {{one short sentence — what the plan is from the Note, plain English}}. → {{action}}`
- Action verb varies by the tranche row's `order` field (read from the
  Order column in `vault/watchlist.md` → `## Planned Tranches`):
  - `GTC` (or empty/missing for legacy rows) → `→ execute tranche: {Action} {Size} at ${at_price}` (standing order already in place — confirmation only).
  - `Alert` → `→ execute manually after gating check` (intentionally not pre-placed; cohort-confirm gate per [[macro-cohort-confirmation]] / [[Opportunity-cost lens]]).
  - `Conditional GTC` → `→ execute if gating condition met. Condition: {note}` (surface the Note column verbatim).
- **Tranche fires do NOT qualify for the auto-deep-dive chain in Step 4b.**
  The deep-dive that produced the tranche already justified it.
- If multiple tranches fire for the same ticker on the same day at
  *different* prices (e.g., a gap-down hits two staged Buy levels), render
  each as its own bullet — the user needs to see each level was reached.

*Merge rule — trigger + tranche on the same ticker at the same price:*

A common setup: the user has both a `## Price Triggers` row (Buy Below $X)
and a `## Planned Tranches` row (Buy {size} at $X) for the same ticker at
the same price. When both fire on the same day, **collapse them into one
bullet** — they're the same signal, written twice in the vault for
different system reasons.

Match condition: same ticker AND same `at_price` (tranche) ≈ `threshold`
(trigger) within $0.50, AND both fired on the same side (buy/buy or
trim/trim). When matched:

- Render one bullet with the tranche's action verb (it's the more
  specific instruction). The trigger fire carries the `funded_by` /
  collision context, which folds into the tranche bullet.
- Bullet format example:
  `- **VRT — $245 hit (buy zone).** Trigger + planned tranche (5–10% starter) both at this level. Funded by DLR rotation. → execute manually after gating check.`
- Drop the redundant `Action: run deep-dive` line — the tranche's execute
  verb subsumes it. (The user can still run a deep-dive manually if the
  thesis context has shifted; mention it inline if the merge tail
  suggests one is warranted.)

If the trigger and tranche fire at *visibly different* prices (e.g.,
trigger Buy Below $250, tranche $245), keep them as two separate bullets
— that's two distinct signals.

*Broader-labelled fires (new one-liner section):*
- Every `FIRED_BUY` / `FIRED_TRIM` becomes a single bullet in a
  **`## Broader Price Triggers`** section placed directly below the
  flagged items and above `## Macro awareness`. One line per fire, no
  sev-3 item, no auto-deep-dive, no merge with news items.
- **Buy-side fires (`FIRED_BUY`)** — the broader file is the "spot a
  good deal" layer, so a buy fire is actionable. Format:
  `- **TICKER** — price $X.XX hit buy below $Y.YY ({{Note}}) — consider buying. See [[TICKER-YYYY-MM-DD]].`
  If `Source` is blank in the table, omit the trailing `See [[…]]` clause.
  If the row has a non-null `funded_by`, append ` Funded by {{funded_by}}.`
  before the `See […]` clause. If `deferred_due_to` is non-empty, append
  ` ⚠ Deferred — {{preferred tickers}} also fired, preferred first.`
  (Collisions are less common in the broader file since most rows have
  blank `Prefer-over`, but the logic is symmetric with watchlist.)
- **Trim-side fires (`FIRED_TRIM`)** — by definition the broader file
  is for tickers NOT in watchlist, so the user does not hold them.
  "Trim Above" on a non-held stock is **not** a "consider trimming"
  signal — it's the deep-dive's bear-case ceiling, and the fire means
  the entry zone is dormant. Render with that framing:
  `- **TICKER** — price $X.XX above thesis ceiling $Y.YY ({{Note}}) — entry zone dormant. See [[TICKER-YYYY-MM-DD]].`
  No `funded_by` line (buy-side concept). No `consider trimming` verb —
  the user doesn't own it. The point of surfacing the fire at all is so
  the reader knows the deep-dive's bear case has been undercut and
  doesn't need re-reading until price retraces.
- If no broader triggers fire, **omit the entire section**. Most days
  nothing here fires — that's expected, not a failure.
- Broader fires are NOT candidates for the Step 4b auto-deep-dive chain.
  They're intentionally lower-touch.

*Housekeeping (both labels, merged):*
- `STALE` (triggers) and `ERROR` (triggers or tranches) rows from either
  file get one-line entries in a **Price Trigger Housekeeping** section
  placed directly below Broader Price Triggers and above
  `## Macro awareness` (the two price-trigger sections are grouped
  together above macro). Note which file the row came from so the fix
  is unambiguous. Don't suppress silently.
- When the summary's top-level `diagnostic` field is non-null, **quote it
  verbatim** in the housekeeping section instead of inferring the cause.
  The script distinguishes network blocks, missing keys, unknown tickers,
  and parse failures — each has a different fix. Guessing hides the fix.
- `EXPIRED` tranche rows get one-line entries in the same housekeeping
  section noting that `weekly-review` will clean them up on Friday — no
  manual action needed unless the user wants to renew the tranche earlier.
- **Tranches with `expires == today` that did NOT fire today** also get
  a one-line entry in the housekeeping footer. The script does not flip
  these to `EXPIRED` until tomorrow (the row is technically still live
  until EOD), but the reader benefits from seeing "row rolls off after
  today" rather than discovering it gone tomorrow. Compute this by
  comparing `expires` to today's date on each tranche row whose status
  is not in the fired set. Format:
  `- **TICKER** — tranche {action} @ ${at_price} expires EOD today; did not fire.`
  This is the path that prevents an LLM from misreading a planning
  note and promoting "today is the expiry day" to a sev-3 item (see
  Step 4 — vault-internal planning reminders are not eligible for sev
  ≥3). If the tranche is already gone from `watchlist.md`, nothing
  surfaces here either; the cleanup already happened.
- `ARMED` and `IDLE` rows do not appear in the report.

**Script failure fallback:** if either invocation errors out, log one line in macro awareness ("price-trigger check unavailable today — {{reason}}") and continue. A failure on one file doesn't block the other.

### Step 1c: Active Earnings Windows

Run the upcoming-earnings script for watchlist tickers:

```bash
python .claude/scripts/get_upcoming_earnings.py --output upcoming_earnings.json
```

The script reads `vault/companies/TICKER/_meta.md` for a structured
`next_earnings:` field, computes trading-day distance, and notes whether a
pre-earnings file already exists for the print. Default window: 14 trading
days. Tickers without a dossier or without the `next_earnings:` field are
silently skipped (the script lists them in the JSON for housekeeping but
they don't render).

For each ticker in the JSON's `upcoming` array:

- Surface a one-liner in a **`## Active Earnings Windows`** section
  placed directly below `## Macro awareness`. The reminders live below
  macro, not above the price-trigger sections. Two formats by case:
  - **Pre-earnings file exists:**
    `- **TICKER** — print {{print_date}} (T-{{N}} trading days). Pre-commit plan in [[{{pre_earnings_file}}]]. Re-read before acting on news today.`
  - **No pre-earnings file:**
    `- **TICKER** — print {{print_date}} (T-{{N}} trading days). No pre-commit plan on file — consider running pre-earnings.`
- If no tickers qualify, omit the section entirely. Don't mention "no
  active windows" — silence is the signal.

This is a reminder section, not a trigger section. It does NOT produce
sev-3 items, does NOT feed the auto-deep-dive chain, and does NOT re-score
pre-earnings content. Its job is to remind you the print is coming so
today's news is filtered through it. If Step 2 surfaces news about a
ticker with an active window AND a pre-earnings file exists, score the
news normally but add a note in the Action line:
`check pre-commit plan in [[{{pre-earnings file}}]]`.

### Step 1d: Verdict Drift Check

Run the drift checker to find deep-dive verdicts that have aged badly:

```bash
python .claude/scripts/check_verdict_drift.py --output verdict_drift.json
```

The script reads `vault/deep-dives/_verdicts.md` (an append-only ledger
written by `stock-deep-dive` after each run), takes the most recent verdict
per ticker within the last 60 days, fetches current Stooq prices, and
emits any row where |drift| ≥ 10% since the verdict price.

For each row in the JSON's `drifts` array:

- Surface a one-liner in a **`## Verdict Drift`** section placed as the
  final state section before the disclaimer footer (below Active IPO
  Windows / Active Earnings Windows / Macro awareness — whichever was the
  last to render). Format:
  `- **TICKER** — was **{{VERDICT}}** at ${{price_at_verdict}} on {{verdict_date}} ({{age_days}}d ago). Now ${{current_price}} ({{drift_pct ± sign}}%). See [[{{deep_dive_file}}]] — re-evaluate.`
- Sort by `|drift_pct|` descending (largest drift first — it's already
  pre-sorted by the script).
- If `drifts` is empty, omit the section entirely. Same silence-is-the-signal rule.

This is a reminder section, not a trigger section — it does NOT produce
sev-3 items and does NOT feed the auto-deep-dive chain. The job is to
catch the case where the verdict is materially stale before the daily
alert quietly cites it as if it were current. A verdict with >10% drift
in <60 days usually means: something specific happened that the deep dive
didn't price in, OR the verdict was correct and the market is just now
catching up — either way, worth a re-read.

If a `drifts` row's ticker also surfaces in Step 2 news scoring, weave the
drift into the Why-it-matters line rather than rendering both
independently — don't double-list.

### Step 1e: Active IPO Windows

Read `vault/ipo-calendar.md`. The file is a manually-curated markdown table
maintained by `vault-curator` (Friday IPO Radar) and direct edits. No script —
parse it inline. If the file is missing or has no `## Calendar` table rows,
skip this step silently.

For each row in the `## Calendar` table:

1. Parse `Expected Date`. Skip rows where the value is `TBD` (date not pinned).
2. Skip rows whose `Status` column is `passed` or `pulled`.
3. Compute trading-day distance: business days from today to `Expected Date`,
   excluding weekends and not counting today. (Holiday calendars are nice-to-have;
   off by one trading day on a holiday week is acceptable noise here.)
4. **Reminder fires if** `0 ≤ trading_days ≤ 7` (within this trading week,
   today included).

For each firing row, look up the latest pre-ipo file in
`vault/reports/pre-ipo/`:

- Filename pattern: `{TICKER_OR_SLUG}-{EXPECTED_DATE}-{initial|gate}.md`.
- If `Ticker` is `TBD`, glob by the company-name slug instead (uppercased,
  spaces → hyphens, e.g., `VOLTAGRID-*-{initial|gate}.md`).
- Gate supersedes initial when both exist for the same expected date.

Surface a one-liner in a **`## Active IPO Windows`** section placed
directly below `## Active Earnings Windows` (or directly below
`## Macro awareness` if no earnings windows section was emitted today).
Sort by trading-day distance ascending. Three formats by case:

- **No pre-ipo file on record:**
  `- **{{Ticker_or_TBD}} ({{Company}})** — IPO T-{{N}} TD, expected {{YYYY-MM-DD}}. No pre-commit plan on file — consider running \`pre-ipo {{Ticker_or_slug}}\`.`
- **Initial pre-ipo file exists, no gate yet:**
  `- **{{Ticker}} ({{Company}})** — IPO T-{{N}} TD, expected {{YYYY-MM-DD}}. Initial plan in [[{{filename}}]]. Run \`pre-ipo {{Ticker}} gate\` before pricing.`
- **Gate pre-ipo file exists:**
  `- **{{Ticker}} ({{Company}})** — IPO T-{{N}} TD, expected {{YYYY-MM-DD}}. Gate plan in [[{{filename}}]]. Re-read before open.`

If no rows fire, omit the entire section. Same silence-is-the-signal rule
as the earnings windows.

This is a reminder section, not a trigger section. It does **not** produce
sev-3 items, does **not** feed the auto-deep-dive chain, and does **not**
re-score IPO-related news. Its job is to make sure the date doesn't sneak
up. If Step 2 surfaces news about an IPO ticker with an active window AND
a pre-ipo file exists, score the news normally but add a note to the
Action line: `check pre-commit plan in [[{{pre-ipo file}}]]`.

### Step 1f: Thesis Tripwire Check

Read `vault/tripwires.md`. For each `ARMED` tripwire, judge whether today's
news / filings bear on its condition:

- **News pushes a tripwire through its threshold** (the falsification condition
  is now met) → this is material. Score the underlying news item normally (it
  will almost always be sev ≥3) with action `run deep-dive TICKER`, and note in
  the Why-it-matters line that it **trips a pre-registered tripwire** (quote the
  condition). The news article is the external signal — this is not a banned
  vault-internal date reminder.
- **News moves a tripwire materially toward its threshold** (not yet tripped) →
  one-liner in a `## Thesis Tripwires` reminder section (reminder cluster below
  `## Macro awareness`, near Verdict Drift):
  `- **TICKER** — tripwire "{condition}" approaching: {what moved today}. See [[Source]].`
- **No news bears on any tripwire** → omit the section entirely
  (silence-is-the-signal, like the other reminder sections).

Do not re-evaluate slow fundamental tripwires from scratch here — that's
`weekly-review`'s job (Step 3d). The daily only reacts when today's flow
actually touches a tripwire. A tripwire is **not** auto-tripped by a date or by
price alone; pure price levels live in the price-trigger system (Step 1b).

### Step 2: Gather News (tiered search)

**Search tool:** Use `web_search_exa` for all searches — it returns
better-quality results for news and financial content. If `web_search_exa`
is unavailable (e.g. running in a remote trigger without Exa MCP), fall
back to the built-in `WebSearch` tool for every search instead.

**Tier 1 — Core Holdings (every run):**
- Two searches per ticker: `"[TICKER] stock news today"` and
  `"[COMPANY NAME] news"`.

**Tier 2 — Active Watchlist (rotation):**
- One search per ticker: `"[TICKER] news today"`.
- If >4 Tier 2 stocks, rotate — search half per run (alternate daily).

**Tier 3 — Peripheral:**
- No dedicated searches. Only appears if surfaced by broad searches.

**Broad/thematic searches (every run):**
- "stock market news today"
- "AI infrastructure spending news"
- "data center cloud computing news today"
- "Federal Reserve economic data today"
- "tariff trade policy news today"

Target: ~10–15 total searches per run.

**Batch in groups of ≤5 — never dispatch all searches in one parallel
block.** Aggregating 10+ Exa results in a single tool-call block times out
the API turn (this happened on 2026-04-25 with 14 calls — no report or
email was produced). Run searches as 3 sequential batches: Tier 1 first
(2 searches × ticker count), then Tier 2 (1 search × rotation half),
then the 5 broad/thematic queries. Within a batch, parallel is fine.
Wait for one batch's results before dispatching the next. Same rule when
mixing searches with file reads — keep any single tool block to ≤5 calls.

### Step 3: Filter & Classify

For each news item, determine connection type:

| Type | What it means |
|------|--------------|
| **Direct** | Names a stock I hold |
| **Competitor** | Affects a direct competitor |
| **Sector** | Affects the broader sector |
| **Supply Chain** | Affects suppliers or customers |
| **Macro** | Broad economic factor |
| **Thematic** | Relates to my worldview/thesis themes |
| **Geopolitical** | International event with market impact |

Think through 2nd and 3rd order effects — that's where the value is.

**Continuity filter (against the story ledger from Step 1):**

For each candidate item, find the matching thread in the rendered ledger
(match on ticker + theme — the `id` and summary make this explicit). Then
classify:

- **Pure repeat** — matches an **Active** thread and brings **no new
  development** (same fact, just restated by a fresh article): **drop it
  entirely.** This is the redundancy the ledger exists to kill — a standing
  fact (a fund's existing stake, an already-announced deal) is not news again
  just because a new article mentions it. Still record the sighting in Step 5
  (so the ledger's last-seen stays accurate) — dropping from the report and
  recording the sighting are separate actions.
- **Meaningful update** — matches an Active thread but carries a genuinely new
  data point, outcome, or materially changed severity: **keep it**, mark
  "(Update)" after the headline, and frame the Why-it-matters line as *what
  changed today* versus the prior coverage — not a re-statement of the standing
  fact. Lead with the new wrinkle.
- **Re-awakening** — matches a **Dormant** thread (went quiet, now resurfacing).
  Treat like a meaningful update: keep it only if there's an actual new
  development, and frame it as "back in the flow after N weeks — here's what's
  new," never as brand-new. A dormant thread resurfacing with no new
  development is still a pure repeat — drop it.
- **New story** — no ledger match: keep as normal. It becomes a new thread in
  Step 5.

When in doubt between pure-repeat and update, ask: *"Is there a fact in
today's article that wasn't true (or wasn't known) at the last sighting?"* If
no, it's a pure repeat — drop it.

**Insider-trade calibration (conditional):**
For any news item about insider transactions (Form 4 sales/buys, 13G/13D
filings, lockup expiry, option exercises), if the ticker has a dossier at
`vault/companies/TICKER/`, read `insider-activity.md` and use the "expected
cadence" pattern to calibrate. Specifically:
- Sale within the established 10b5-1 plan cadence and batch size → low
  information content; typically caps severity at 2 (drop) unless the
  price level is itself material (e.g., intersects a user thesis zone).
- Sale *outside* the 10b5-1 plan, larger than typical, or by an insider
  whose prior pattern was restraint → meaningful signal; bump severity.
- New 13G crossing 5% / exited 5% / large amendments → meaningful signal
  regardless of dossier state.
In the Why-It-Matters line, explicitly cite the comparison ("within
Mecklenburg's typical 30–50K/month 10b5-1 batch — no signal") rather than
just reporting the raw transaction. If no dossier exists for the ticker,
fall back to reading the news-article context (10b5-1 footnote, etc.).

### Step 4: Score Severity; Keep Only ≥3

Use the framework in `references/scoring-framework.md`.

Score relative to MY portfolio and beliefs, not the generic market. News
that threatens the AI infrastructure thesis is higher severity for me
than for a diversified index investor.

**Drop severity 1–2 items entirely.** They do not appear in the report —
not in an appendix, not as a background list. If nothing clears the sev
≥3 bar today, the report is short. That is correct, not a failure state.

**Not eligible for sev ≥3 — vault-internal planning reminders.**
A "scored item" must be tied to an *external* signal: a news article,
a fired price trigger (Step 1b), a fired tranche (Step 1b), a verdict
drift (Step 1d), an active earnings window (Step 1c), or an active IPO
window (Step 1e). If the only thing happening is that **today's date
matches a planning note's calendar entry**, that is not a scored item.
Do not promote it.

Specifically: do not write a sev-3 item for any of the following just
because today's date matches:

- A planning note that says "re-deep-dive TICKER around {date}" or
  "check in on TICKER {date}." The note is a reminder you wrote to
  yourself, not news.
- A tranche or GTC order's stated expiry date (with no fire today).
  If the level didn't fire and the row is still in `watchlist.md`,
  the row is live until end-of-day; if it's already been cleaned out
  of `watchlist.md`, it's gone. Either way, expiry alone is not news.
- A pre-earnings file's expected print date — Step 1c already handles
  that as a one-liner reminder; don't re-score it.

These date-matched reminders surface (when they surface at all) as
one-liners in **Price Trigger Housekeeping** (placed directly above
`## Macro awareness`), not as items above the fold. Specifically:

- **Tranche in `watchlist.md` with `Expires == today` that didn't
  fire today:** add a one-liner to housekeeping
  (`- **TICKER** — tranche {action} @ ${price} expires EOD today; did not fire.`).
  The script flips it to `EXPIRED` tomorrow and weekly-review prunes it
  on Friday — no action needed unless you want to renew earlier.
- **Planning-note reminder (re-deep-dive date, etc.) referencing
  today:** if you genuinely think the reader needs the nudge,
  one-liner in housekeeping
  (`- **TICKER** — planning note [[NOTE]] flagged today as the re-deep-dive checkpoint; consider running deep-dive.`).
  Most of the time, just don't surface this at all — the note will
  surface itself the next time the reader opens the vault.

The bar to clear for sev ≥3 is "something happened in the world today
that the reader should act on or read about." A date in a note isn't
that.

For each surviving item, decide the **action line**. One of exactly three
forms:

- `run deep-dive TICKER` — today's news materially affects a thesis,
  verdict condition, or price level. The next step is a deep-dive, not
  more words in this report.
- `watch for [specific condition]` — no action now, but there's a named
  trigger (e.g., `watch for first 2-day red sequence before NVDA earnings`).
- `none` — noteworthy, but no action implied.

Never freeform. If you're tempted to write paragraphs of advice, that's a
signal the item warrants `run deep-dive TICKER`.

### Step 4b: Auto Deep-Dive Chain (gated)

> **TEMPORARILY DISABLED.** Skip this entire step. Do not run any
> auto-deep-dive (fresh or reused), do not write `Auto deep-dive:` /
> `🤖 Fresh deep-dive` lines, and keep every qualifying item's standard
> `Action: run deep-dive TICKER` action line so the user can run it
> manually. Re-enable by deleting this notice. The rest of this section
> is preserved for when it's turned back on.

The sharpest catalysts should produce a deep-dive the same day, with the
verdict folded into this report. Un-gated, that would fire multiple
deep-dives per run and multiply cost. The gates below keep it rare
(typically 0 per run, occasionally 1) and high-signal.

**Candidate rule — a surfaced item is a candidate if BOTH hold:**

1. Connection type is **Direct** — names a single clearly-identified
   ticker I hold or watch. `Macro`, `Sector`, `Thematic`, `Supply Chain`,
   `Geopolitical`, and `Competitor` items never qualify; the chain
   targets one name at a time.
2. AND one of:
   - It's a `FIRED_BUY` or `FIRED_TRIM` price-trigger item from Step 1b
     with label=`watchlist` AND type=`trigger` AND empty
     `deferred_due_to` (broader-labelled fires don't qualify — they
     render as one-liners, not sev-3 items; tranche fires don't
     qualify — their action is "execute tranche," not "re-evaluate";
     deferred fires don't qualify — the preferred ticker whose fire
     caused the deferral is the one that should consume the auto-dive
     budget, not this one), or
   - It's a news item scored **severity ≥ 4**.

Severity 3 news items without a fired price trigger do **not** qualify.
The Tier 1 + sev 3 case is already handled by the email-brief threshold;
the deep-dive chain is for sharper catalysts only.

**Staleness gate — has a recent deep-dive been written for this ticker?**

For each candidate ticker, glob `vault/deep-dives/TICKER-*.md` and take
the newest by filename date. The threshold depends on **how the candidate
qualified** in the candidate rule above:

- **Sev ≥ 4 news item path** — sharp catalyst, likely thesis-affecting.
  Threshold is **7 days**. A verdict that pre-dates a sev-4 catalyst is
  presumed stale unless it specifically anticipated this exact news.
- **Fired-trigger path (no qualifying sev-4 news on the same ticker)** —
  price-only signal, slower-moving. Threshold stays at **14 days**.
- **Both paths qualify on the same ticker** — the lower threshold wins
  (7 days). News-driven catalysts dominate.

Apply the threshold:

- **Newest file ≤ threshold (today included):** do **not** re-fire.
  Read the existing file and fold its verdict into the item.
- **Newest file > threshold, or no file at all:** the ticker is eligible
  to fire a fresh deep-dive (subject to the per-run cap below).

**Per-run cap: at most 1 fresh deep-dive fire per run.**

Reusing an existing ≤14-day file is cheap (read-only) and has no cap —
any number of candidates can fold in a recent verdict. The cap only
applies to fresh runs.

If multiple tickers are eligible for a fresh fire, pick one by:
1. Highest severity first (price-trigger fires count as severity 3 for
   this ranking; a sev 4 news item outranks a price trigger alone).
2. Then Tier (1 > 2 > 3).
3. Then ticker alphabetic.

Overflow candidates keep their standard `run deep-dive TICKER` action
line so I can run them manually.

**Firing a fresh deep-dive:**

Execute the `stock-deep-dive` workflow for the chosen ticker in
**single-stock mode**. Never use comparison mode for an auto-fire, even
if two tickers would qualify — the chain does one stock at a time.

Either invoke the skill (e.g., via the Skill tool with
`skill=stock-deep-dive`, `args=TICKER`) or follow
`.claude/skills/stock-deep-dive/SKILL.md` inline. Either path writes
`vault/deep-dives/TICKER-YYYY-MM-DD.md`.

**Reading the outcome (fresh or reused):**

After the deep-dive file is confirmed to exist, read it and extract:

- **Verdict** — one of `HOLD` / `ADD` / `REDUCE` / `WATCH`.
- **Condensed take** — ≤ 2 sentences. Pull from the Direct Take
  subsection in Portfolio Fit & Timing if present; otherwise condense
  the verdict paragraph. Include at most one concrete figure (price
  target, win rate, % off 52w high, etc.) if one is readily available.
- For a reused file: compute the age in days (today = 0, yesterday = 1).

**Integrating into the report:**

The `Auto deep-dive:` line **replaces** the normal `Action:` line for
that item — never both.

For a freshly-fired run, use the explicit "run today" form so the reader
can immediately tell this verdict was produced as part of this alert
(not pulled from a cached file):

```
- **🤖 Fresh deep-dive — run today ([[TICKER-YYYY-MM-DD]]):** Verdict **{{VERDICT}}**. {{≤2-sentence condensed take}}
```

For a reused recent file (include age):

```
- **Auto deep-dive ([[TICKER-YYYY-MM-DD]], {{N}} days old):** Verdict **{{VERDICT}}**. {{≤2-sentence condensed take}}
```

The two forms are intentionally distinct — `Fresh deep-dive — run today`
vs `Auto deep-dive (…, N days old)`. Never collapse them; the reader
needs to know whether the verdict was just produced or recalled.

**Failure fallback:**

If the deep-dive workflow errors out partway through (FMP down, script
exception, ticker resolves to no data), do not block the report. Keep
the item's original `Action:` line (`run deep-dive TICKER`) and append
one line to **Macro awareness** noting the failure and reason. Never
write a partial or fabricated verdict.

**Email brief:** when the email brief fires in Step 6, the
`Auto deep-dive:` line travels with the item verbatim — same text, same
format. The email is still the report in email form.

### Step 5: Write Report

Output to `vault/reports/daily/YYYY-MM-DD.md` using the template in
`references/report-template.md`.

Two shapes:
- **Busy day** (1+ items clear sev ≥3): flagged items + macro awareness.
- **Quiet day** (nothing clears sev ≥3): short "no flagged items" + macro
  awareness. Do not pad. Do not promote sev 1–2 items to fill space.

Include `[[wikilinks]]` to relevant files in `notes/`, `library/`, or
`deep-dives/` when a specific stock or decision is referenced.

**Macro awareness block** (always present, both shapes): 3–5 one-line
bullets drawn from the broad searches. Unscored context — not items that
deserved a severity, but still shape the day. One line each. No padding.

**Macro diagnosis lead (mandatory on big-move days):** if a major index
(SPY / QQQ / IWM) OR any Tier 1 / Tier 2 holding moved ≥3% today, lead
the macro section with a 1-2 sentence diagnosis of **what drove the move**
before the bullet list. Name the catalyst, not the move. Bad: "AI stocks
were weak today on capex concerns." Good: "AI infra sold off ~7% today
on a Bloomberg report that Microsoft is renegotiating its OpenAI compute
commitment — VRT, DLR, GEV down 6–9%." Find this via the broad
searches; if you can't find a specific catalyst, say so plainly ("Tape
was risk-off across the board today, no single named catalyst surfaced
in the broad searches") rather than reaching for generic finance-speak.

**Every macro bullet names a specific catalyst.** No generic platitudes
("rate environment remains uncertain", "capex risk persists",
"valuations are stretched"). If you can't tie a bullet to a concrete
named event from today's broad searches, drop the bullet.

**Language style — plain English, not finance-speak.** This is read on
a phone over coffee.
- Short sentences. Active voice. Contractions are fine.
- No jargon when a plain word works: "sold off" not "exhibited downside
  pressure"; "buy zone" not "accumulation tranche"; "Fed minutes" not
  "FOMC communication". A reader who doesn't live in finance Twitter
  should follow every line.
- Specific over abstract. Name the catalyst, name the level, name the
  ticker. Skip the hedge clauses.
- "Why it matters" is one line, ~25 words. If you need more, the action
  is `run deep-dive TICKER`, not more sentences here.

**Split the write into two tool calls when 2+ items clear sev ≥3.**
Long single-Write generations have repeatedly hit "Stream idle timeout —
partial response received" on Anthropic's streaming API and lost the
whole report (no file, no commit, no email). Splitting forces a
mid-generation checkpoint — each tool call is its own streamed turn, so
if the second turn stalls the first turn's output is already on disk.

Pattern:
1. **Write** the file with: frontmatter (`email:` block included) +
   `## Price Levels Hit` (if any watchlist trigger/tranche fired) +
   `## News` section with the scored items. Stop there.
2. **Edit** (append) the trailing sections in the order they appear in
   the template: Broader Price Triggers → Price Trigger Housekeeping →
   Macro Awareness → Active Earnings Windows → Active IPO Windows →
   Verdict Drift → Thesis Tripwires. Skip sections that are empty per their
   own silence-is-the-signal rules. Macro Awareness is always present (the
   only section that always renders); Price Levels Hit sits at the very
   top (above News) when any watchlist fire happened, and the other
   reminder/drift sections sit below Macro Awareness.

On a quiet day (zero sev ≥3 items), one Write is fine — total output is
small enough that the timeout window is not the binding constraint.

**Frontmatter — add the `email:` block.** The markdown IS the email — Step
6's script parses this file and renders it via `templates/email-default.html.j2`.
Two editorial fields go in frontmatter because they're hook-craft, not
template-able: `subject` (click-through line) and `preheader` (inbox snippet).
Everything else — HTML styling, link rendering, sev-4+ red border, Friday
Weekly Review prepending — is derived automatically from the body.

```yaml
---
date: 2026-04-23
type: daily-news-alert
tags:
  - daily-alert
  - news-analysis
email:
  subject: "DLR just hit your trim level"
  preheader: "Rotation plan says 20–40 shares around here"
---
```

On quiet days (no sev ≥3 items), still write the two fields — see Step 6's
subject/preheader rules for how to pick them.

#### Step 5c: Record sightings in the story ledger

After the report file is written, record today's sightings so tomorrow's run
remembers them. Run one `--upsert` per **story you encountered today**, which
means:

- Every item you **surfaced** in the report (sev ≥3 news item — not price-level
  fires, earnings/IPO reminders, drift, or housekeeping; those have their own
  state). Record the severity you scored it.
- Every item you **dropped as a pure repeat / no-new-development re-awakening**
  in Step 3. Recording these keeps the thread's `last_seen` accurate so it
  doesn't drift to Dormant while it's actually still in the daily flow. Use the
  severity it would have scored (or its prior `last_severity`).

Do **not** upsert macro one-liners, sev 1–2 noise that isn't a tracked thread,
or vault-internal reminders.

For each, call:

```bash
python .claude/scripts/story_ledger.py --upsert '{"id":"<existing-id-or-omit>","ticker":"NBIS","theme":"leopold stake","summary":"one-line what-this-thread-is","severity":3,"date":"YYYY-MM-DD","surfaced":true}'
```

Rules:
- **If the item matched an existing thread in the Step 1 render, pass that
  thread's `id`** — this is the reliable join; don't rely on the fuzzy matcher.
  Omit `id` only for genuinely new stories (a new thread is created).
- `ticker` is the held/watched ticker, or omit/null for a cross-cutting macro
  or thematic thread (e.g. `"theme":"fed rate-cut timing"`, no ticker).
- `theme` is a short stable phrase (2–5 words). `summary` is the one-line
  description shown in future renders — keep it current (it's overwritten each
  sighting, so refresh it when the story evolves).
- `surfaced` is `true` if it appeared in today's report, `false` if dropped as
  a repeat.
- `date` is today's report date.

The command prints `NEW` / `RECURRING` / `REAWAKENED` so you can confirm the
join worked. Pruning (dormancy flip, overflow) is automatic — no housekeeping
call needed. If `story_ledger.py` errors, log one line in your final response
and continue; a ledger write failure must not block the report or email (both
are already saved).

### Step 6: Send Email Brief (always)

**Testing mode — always send.** The severity threshold gate is disabled
while I'm iterating on the email format, so every run sends — including
quiet days where nothing clears sev ≥3. Quiet days are just macro awareness
+ the "no flagged items" shape. Still write `email.subject` and
`email.preheader` in the frontmatter.

**Run this one command.** Markdown transform, HTML render, Friday
Weekly Review prepend, Resend send — all handled.

```bash
python news-visual/build_and_send.py --date YYYY-MM-DD
```

(`--dry-run` skips the actual send for local testing. Template swap:
`--email-template news-visual/templates/email-X.html.j2` — see the
template's header comment for the context contract.)

**What the script does for you** — so you don't need to think about it:
- Markdown → HTML (bold, italic, links, wikilink stripping, `&`/`<`/`>` escaping)
- Preheader hidden-div + zero-width-filler trick for the inbox snippet
- Severity 4+ items wrapped in the red left-border `<div>`
- Friday (`date.weekday() == 4`): loads the latest `vault/reports/weekly/*.md`
  and prepends 5–7 bullets from Dominant Themes / Thesis Pressure Test /
  Wait-for-Deal Watch / What Shifted sections
- Resend send via `send_brief.py`; `RESEND_API_KEY` read from env
- Plain-text fallback auto-generated for HTML-blocked mail clients

**Your remaining editorial job: the subject and the preheader.** Both live
in the markdown frontmatter from Step 5. These are the only pieces the
script can't generate — they're hook-craft, not style.

**Source URLs must be real article URLs**, not publication homepages. Exa
returns a specific URL for each search result — pass it through verbatim in
the `[article title](URL)` markdown. Linking to a homepage is worse than no
link at all because it implies the article is one tap away when it isn't.
If a source line is a roll-up of multiple publications, pick the single
best/earliest article and link only that one.

**Severity markers.** Write `### TICKER — Headline` for sev 3 and `### 🔥
TICKER — Headline` for sev 4+. Never write `[sev X]`. The script detects
the 🔥 prefix and applies the red left-border wrapper in the email and
prefixes `[HOT]` in the plain-text fallback.

**Skipped: the old HTML body structure, preheader div pattern, and Friday
Weekly Review HTML template.** All of these are now generated by the script
from the markdown + frontmatter. If you need to change the styling, edit
`news-visual/templates/email-default.html.j2` — don't try to emit raw HTML
here.

#### Failure behavior

If `build_and_send.py` exits non-zero:
- The daily report is already saved to `vault/reports/daily/YYYY-MM-DD.md`
  (Step 5) — the content is not lost.
- The error goes to stderr with a specific cause (missing `RESEND_API_KEY`,
  Resend rate limit, missing template, Jinja parse error).
- Do not retry automatically. Surface the error in your final response so
  the user can investigate.

#### Subject and inbox preview — the editorial part

Both go in `email.subject` and `email.preheader` under the frontmatter block
in Step 5. They are the two things the script can't infer — the rest of the
email derives from the body.

**Subject** — what makes the user want to open the email on their phone.
The job is click-through, not accuracy. The body has the accurate version;
the subject just has to feel interesting enough to tap.

Rules:
- **No date.** No `YYYY-MM-DD`. The email's own timestamp covers that.
- **No "Trading Brief", "Daily Alert", "News", or other generic prefix.**
  Skip the framing — go straight to the substance.
- **One thing only.** Pick the single highest-impact item; don't list
  multiple. If two items are equally critical, pick the one with a
  more concrete user action.
- **Keep it short — 3–6 words, ~30–45 characters.** Mobile inboxes
  truncate around 40. Prefer fewer words over packing detail.
- **Natural, conversational phrasing.** Read it aloud — if it sounds
  like a Bloomberg terminal ticker (`NVDA $25B GTC + $100B cloud
  commit + 5GW compute`) it's too dense. Write like a person would
  say it: `NVDA's big GTC day`, `DLR just hit your trim level`.
  Prepositions, articles, and contractions are fine.
- **Punchy, not clickbait.** No "BREAKING", no "🚨", no all-caps unless
  it's an intentional `SELL NOW`-style action.

**Selection logic:**
1. Sort scored items by severity descending.
2. Among the top severity bucket, prefer items with the strongest action
   (a fired price trigger > sev 4+ news with a concrete watch level >
   sev 4+ news with `none` action > sev 3).
3. The chosen item drives the subject. Phrase the subject as either:
   - **The event, casually** — when news itself is the story.
     `NVDA's GTC day` · `Fed just surprised with a 50bps cut` · `Iran shuts Hormuz`
   - **The action, plainly** — when a user-actionable trigger is live.
     `DLR hit your trim level` · `VRT buy trigger just fired` · `GEV drifting into the add zone`
   - **Combined, still short** — only if it truly reads naturally.
     `Iran sell-off drags NVDA to your add zone`

**Quiet days (no items clear sev ≥3):** the email still sends. Pick the
subject from the macro awareness bullet with the strongest read-through
to my watchlist — preheader can just say `Quiet day — macro only`.

**Friday emails with the Weekly Review prepended:** subject still comes
from the day's scored items, not the weekly review. The Weekly Review is
context, not the lead.

**Preheader (inbox preview, ~50–80 chars)** — the snippet that appears
under the subject in Gmail/iOS Mail. Rules:

- Expand on the subject without repeating it.
- Lead with *what it means for me*, not the news event. Subject = event/action;
  preheader = what to do or watch.
- Conversational, same voice as the subject. Avoid dense "$230–240/May 13/beta 4.3"
  data-dumps — the body has the numbers.
- One short phrase, no period at the end.
- Same severity discipline — derived from the same top item; don't try
  to summarize multiple items.

Examples (paired with their subject):

| Subject | Preheader |
|---------|-----------|
| `Iran sell-off drags NVDA to your add zone` | `Worth a look before you open the app` |
| `VRT buy trigger just fired` | `Check the thesis before adding into the open` |
| `NVDA's GTC day` | `Gap-up exits the deep-dive add window — no chase` |
| `DLR hit your trim level` | `Rotation plan says 20–40 shares around here` |
| `Fed just surprised with a 50bps cut` | `Power infra (VRT, GEV) is the main read-through` |

---

## Constraints

- Output goes to `vault/reports/daily/`. Never modify `notes/` or `library/`.
- Don't make up news. Exa/WebSearch only.
- Sev 1–2 items get dropped, not filed. The daily alert surfaces what
  warrants attention, nothing else.
- Be honest when news challenges the thesis. I want to know.
- Don't create thesis, beliefs, or watchlist files. Read what's there.
- **No persona/conviction sections in the daily report** — those live in
  the weekly review (thesis pressure test) and deep dive (conviction check).
- **No wait-for-deal lens in the daily report.** It lives in `weekly-review`
  and `vault-curator` (Opportunity Radar). The daily alert is about
  triggering action on today's news, not surveying opportunity themes.
- **No off-watchlist idea generation in the daily report.** Surfacing new
  names is the job of `vault-curator` (weekly) and `weekly-review`.
- **No vault-internal date reminders as scored items.** Planning notes
  saying "today is the re-deep-dive date" or "tranche expires today"
  are not news — they're calendar entries the user wrote to themselves.
  If genuinely worth surfacing, they go as one-liners in Price Trigger
  Housekeeping (placed below Broader Price Triggers and above Macro
  awareness), never as sev-3 items above the fold. See Step 4 for the
  eligibility rule.
