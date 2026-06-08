---
name: quarterly-review
description: >
  Quarterly meta-review of the trading-journal system itself. Two parts:
  (1) calibration pass — compares prior deep-dive verdicts and daily-alert
  severities against the outcomes of closed trades (read from
  `library/TICKER - YYYY-MM-DD Close.md` files following the trade-close
  template), plus pre-earnings ladder-probability calibration and
  execution-thesis H2 retraction-rate / watch-list hit-rate calibration;
  (2) echo-chamber audit — reviews the last ~90 days of daily
  alerts, weekly reviews, and deep-dives for framing drift, language
  staleness, and whether the system's conclusions are evolving with new
  data or recycling its own outputs. Writes to
  `vault/reports/quarterly/YYYY-QN.md`. Manual trigger only —
  not scheduled. Usage: "run quarterly review" or
  "run quarterly review for Q2 2026".
---

# Quarterly Review

## Purpose

This skill checks the **system**, not the portfolio. The other skills ask
"what should I do with my positions?" This one asks "is the system giving
me calibrated advice, and is it drifting into an echo chamber?"

Run it every ~3 months. The first few runs will be thin — you need
accumulated closed trades and report history for it to have material.
That's fine. The skill produces a smaller output when inputs are thin;
it doesn't fabricate patterns from nothing.

---

## Workflow

### Step 1: Parse quarter

From the user's invocation, determine the target quarter. If not
specified, default to the most recently completed quarter based on
today's date:
- Jan–Mar → previous year Q4
- Apr–Jun → current year Q1
- Jul–Sep → current year Q2
- Oct–Dec → current year Q3

Display as `YYYY-QN` (e.g., `2026-Q1`). Compute the quarter's date range
(three calendar months) for filtering inputs.

### Step 2: Load Inputs for Calibration Pass

**Closed trades (`vault/library/*Close.md`):**
- List files matching pattern `TICKER - YYYY-MM-DD Close.md` (following
  the trade-close template).
- Filter to closes where the `closed` date in frontmatter falls within
  the target quarter OR in the quarter immediately preceding (to catch
  trades that closed right at the boundary).
- For each: read frontmatter (ticker, opened, closed, pnl_pct, outcome)
  and the Calibration notes section.

**Deep-dives that were current at each close:**
- For each closed trade, find the most recent `vault/deep-dives/TICKER-*.md`
  file whose date is ≤ the close date. This is the last verdict the
  system had on record at the time of exit.
- Extract verdict, date, and key conditions.

**Daily alerts covering each trade's tenure:**
- For each closed trade, list `vault/reports/daily/*.md` files whose
  date is between `opened` and `closed`.
- Extract flagged items (sev ≥3) naming the ticker, with severity and
  action line.

**Pre-earnings files whose print date falls in the target quarter:**
- List `vault/reports/pre-earnings/*.md` where the `print_date` frontmatter
  is within the target quarter (regardless of whether the ticker is in a
  closed trade). These are the pre-commit plan artifacts — they get their
  own calibration row in Step 4 even if the position is still open.
- For each unique `(ticker, print_date)` pair, run:
  ```bash
  python .claude/scripts/score_print.py --ticker TICKER --print-date YYYY-MM-DD
  ```
  The script picks the gate file if present, falls back to initial,
  parses the Scenario Ladder, fetches the realized 5-trading-day
  post-print move from Yahoo, and emits JSON with: scenarios,
  `spot_at_print_close`, `spot_at_horizon_close`, `realized_move_pct`,
  `matched_scenario` (the row whose price zone contained the realized
  price), `boundary_miss` (true if the price landed between rows, with
  `closest_scenario` populated), and `did_plan_execute: "unverified"`
  (manual reconciliation by the user — leave as-is unless a note in
  `vault/notes/` explicitly records execution status). If the print
  date is in the future, `realized_move_pct` is `null` and the row is
  surfaced with a "pending" note rather than dropped.
- The Step 4 calibration table reads directly from these JSON outputs.
  Do not re-parse the ladder or re-fetch prices in the agent — let the
  script do it once.

**Execution-thesis + execution-audit files (across all tickers):**
- List all `vault/companies/*/execution-thesis.md` files. For each, read
  the **Refresh log** section (specifically "What changed since last
  refresh" entries dated within the target quarter) and the **audit-status
  banner**.
- List all `vault/companies/*/execution-audit.md` files. For each, read
  the self-contained verdict at the top + the updated confidence/gate
  matrix. Note whether the audit was `clean`, surfaced material
  corrections, or retracted H2.
- For each ticker with refreshes inside the quarter, also locate the most
  recent prior refresh log entry (which may be older than the quarter) so
  the in-quarter delta is interpretable.
- This is the **execution calibration substrate** for Step 4's new
  execution-thesis subsection. If no execution-thesis files exist on disk
  for this quarter, skip it — the layer hasn't accumulated material yet.

**If no closed trades in the quarter AND no pre-earnings files AND no
execution-thesis refreshes:** write "No closed trades, pre-earnings runs,
or execution-thesis refreshes this quarter — calibration pass skipped."
Proceed to echo-chamber audit.

### Step 3: Load Inputs for Echo-Chamber Audit

**Daily alerts:** last 90 days of `vault/reports/daily/*.md`.

**Weekly reviews:** last ~13 `vault/reports/weekly/*.md` files.

**Deep-dives:** all files in `vault/deep-dives/` whose date falls in the
target quarter.

Do not load notes/ or library/ for the audit — those are inputs to the
system, not outputs. The audit is about what the system produces.

### Step 4: Synthesize — Calibration Pass

For each closed trade with a deep-dive anchor:

- **Verdict vs. outcome:** Did the standing verdict (ADD / HOLD / REDUCE /
  WATCH) match the outcome (win / loss / breakeven)? Examples:
  - `ADD → win`: aligned
  - `ADD → loss`: verdict was wrong (or timing was off)
  - `REDUCE → win`: verdict was wrong in the other direction
  - `HOLD → win`: aligned (you held, it worked)
- **Severity vs. materiality:** Were the sev ≥3 alerts during the trade
  the ones that actually mattered to the outcome? Or did the system
  miss the key event (covered it at sev ≤2, or not at all), or
  over-flag noise?
- **User's own notes:** Did the `Transferable lesson` in the close file
  point to a system failure, a user failure, or an unknowable?

**Aggregate patterns across all closed trades in the quarter:**
- Any systematic directional bias? (e.g., "verdicts skewed ADD on AI
  infra even when thesis was already priced in")
- Any timing pattern? (e.g., "system flagged the news but the action
  line was `none` when it should have been `watch`")
- Any structural miss? (e.g., "3 of 4 closes mentioned regulatory
  events the system never caught")

If only 1–2 closes this quarter: produce observations only, not
patterns. "One trade is not a pattern" should appear in the output.

**Pre-earnings calibration (separate subsection):**

For each pre-earnings file whose print date fell in the quarter, emit a row:

| Ticker | Print | Realized post-print move | Scenario it matched | Ladder probability on that scenario | Pre-commit action (initial) | Did the plan execute? |
|---|---|---|---|---|---|---|

- **Realized move:** the actual 5-trading-day drift from print-date close.
- **Scenario it matched:** which ladder row's price zone contained the
  realized price. If it landed between rows, pick the closer one and note
  the boundary miss.
- **Ladder probability:** what the pre-earnings run assigned to that
  scenario. The calibration signal is whether low-probability scenarios
  are hitting too often (overconfident) or never (underconfident).
- **Did the plan execute?** Yes / No / Partial, based on whether the
  price triggers in the Pre-Commit Plan actually fired during the
  pre/post-print window. This requires the user to have tracked
  execution — if no note was left, write "unverified."

**Aggregate signal over multiple prints:**
- Are ladder probabilities well-calibrated? Across prints, realized
  scenarios should roughly match assigned probabilities (e.g., if "soft"
  was assigned ~15% across 10 prints, it should have hit on ~1–2).
- Is the Pre-Commit Plan actually being followed? Standing trims and
  post-print contingency orders that never execute are a behavioral
  signal, not a system signal — flag it for user review rather than
  treating it as a system miss.
- Were the Rotation Check verdicts (hold / rotate / cash) validated by
  what the capital actually did in the window?

If <3 pre-earnings runs in the quarter, write "Too few pre-earnings runs
for aggregate calibration — individual rows only." Two runs is not
a distribution.

**Execution-thesis calibration (separate subsection):**

For each ticker with an `execution-thesis.md` refreshed in the quarter,
emit a row:

| Ticker | Refresh date | H2 status this refresh | H2 status prior refresh | 30/60/90-day items resolved | Audit verdict |
|---|---|---|---|---|---|

- **H2 status this refresh / prior refresh:** `cleared` / `not proposed`
  / `retracted`. The transition `cleared → retracted` or `cleared →
  not-proposed` is the most informative — a previously-confident H2 that
  failed.
- **30/60/90-day items resolved:** count of prior-refresh watch-list
  items that resolved this refresh (confirmed/refuted/expired without
  signal). Pulled from the "Watch-list resolution" bullet in the refresh
  log's "What changed" subsection.
- **Audit verdict:** `clean` / `material corrections` / `H2 retracted` /
  `not audited`. Pulled from the corresponding `execution-audit.md` if
  present and its date is between the prior and current refresh.

**Aggregate signal across the quarter:**
- **H2 retraction rate.** Of H2 hypotheses proposed across the quarter,
  how many were retracted at the next refresh? **If >30%, the H2 gate
  is too lenient** — the 2+ independent Tier-A signal rule is being
  applied too generously. Flag as a system-calibration finding.
- **Watch-list hit rate.** Across all prior-refresh 30/60/90-day items
  that resolved this quarter, what fraction were confirmed (vs. refuted
  or expired silently)? Low hit rate suggests the falsification register
  is naming non-discriminating signals.
- **Audit recurrence pattern.** If audits are catching the same issue
  type every quarter (e.g., "H2 cited a single Tier-A filing dressed up
  as two"), that's a persistent skill blind spot — the execution-thesis
  prompt needs tightening, not just better per-run discipline. Flag as a
  recurring-pattern finding rather than a per-ticker one.

If <3 execution-thesis refreshes in the quarter: individual rows only,
no aggregate signal. The layer is too new for calibration to be stable.

### Step 5: Synthesize — Echo-Chamber Audit

Scan the loaded reports for:

- **Framing drift:** Are the same themes described with evolving
  vocabulary, or are phrases being recycled verbatim across weeks?
  Pick 2–3 recurring themes and quote how they're described in month
  1 vs. month 3. If the wording is near-identical, flag it.
- **Verdict stability:** How often did deep-dive verdicts change on
  the same ticker across the quarter? Zero changes might mean
  conviction — or might mean the system isn't updating on new data.
- **Severity clustering:** Count severity distribution across all
  daily alerts this quarter. If everything is clustered at sev 3 (the
  threshold), that's miscalibration — the system may be inflating to
  meet the surfacing bar.
- **Self-reference:** How often did a weekly review cite a prior
  weekly review's framing rather than re-deriving from that week's
  news? Some self-reference is healthy; constant self-reference is
  echo chamber.

Output format: 3–5 observations, each one line. No grand theory. If
the system looks fine, say "No significant drift observed."

### Step 6: Write Output

Output path: `vault/reports/quarterly/YYYY-QN.md`

If `vault/reports/quarterly/` doesn't exist, create it.

Use the template in `references/report-template.md`.

Also produce a terminal summary: 3–5 bullet key takeaways. The file is
the record; the terminal output is what the user reads first.

---

## Constraints

- **Never scheduled.** Manual trigger only. This is a slow-moving
  meta-review, not a routine.
- **Thin inputs produce thin outputs.** If there are no closed trades
  or <30 days of reports, the skill says so and produces a minimal
  output. No fabricating patterns from nothing.
- **No fresh searches.** This skill operates on historical vault data.
  No Exa, no WebSearch.
- **Writes only to `reports/quarterly/`.** Never touches `library/`,
  `notes/`, or other report folders.
- **Observations, not prescriptions.** The output flags patterns; the
  user decides whether to change the system in response.
