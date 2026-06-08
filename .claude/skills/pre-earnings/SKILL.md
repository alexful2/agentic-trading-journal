---
name: pre-earnings
description: >
  On-demand pre-earnings analysis for a single ticker. Produces a scenario
  ladder priced in your actual share count, an options-implied move vs.
  historical realized compare, a management credibility check (guidance vs.
  actual), insider behavior going in, and a specific pre-commit action plan.
  Two modes: initial (run ~10–15 trading days before print) and gate (run
  T-1 or day-of to lock in orders). Mode auto-detects from the next-earnings
  date in vault/companies/TICKER/_meta.md, or force explicitly:
  "pre-earnings VRT" (auto), "pre-earnings VRT gate", "pre-earnings VRT initial".
  Requires an existing dossier at vault/companies/TICKER/ (build via
  company-dossier skill first if missing).
---

# Pre-Earnings

## Purpose

Answer the specific time-boxed question: **"How do I not get destroyed on
this print — or miss the setup — given my actual share count?"**

This is not deep-dive. Deep-dive answers "should I hold/add/reduce this at
today's price." Pre-earnings answers "given my plan already exists, what's
my exact pre-commit action around *this specific print*."

Two runs per print, by design:
- **Initial** (T-10 to T-15 trading days) — build the scenario ladder and
  pre-commit the rules ("if X happens, I do Y") while you still have
  emotional distance.
- **Gate** (T-1 or day-of) — pull the last 14 days of movement (analyst
  revisions, insider filings, news) and lock in the specific order you
  will place before close. Short. A delta, not a re-run.

**Requires:** `yfinance` Python package (`pip install yfinance`).

---

## Workflow

### Step 0: Preconditions & Mode Detection

**0a. Parse ticker and optional mode flag.**
- `"pre-earnings VRT"` → auto-detect mode
- `"pre-earnings VRT gate"` → force gate
- `"pre-earnings VRT initial"` → force initial

**0b. Require dossier.** Check `vault/companies/{TICKER}/_meta.md` exists.
- **If missing:** stop. Output:
  > `No dossier found at vault/companies/{TICKER}/. This skill requires the
  > SEC-sourced dossier. Run "build company dossier for {TICKER}" first,
  > then re-run pre-earnings.`
- **If present:** read `_meta.md` and extract the next-earnings date from
  the "Key facts" or similar section. If the date is not explicitly stated,
  fall back to the fundamentals script output from Step 2.

**0c. Detect mode (if auto).**
- `next-earnings-date − today` = trading days until print (positive number for a future print).
- `≤ 2 trading days` → **gate mode**.
- `> 2 trading days` → **initial mode**.
- If trading days is unknown, default to initial and flag that the
  print date couldn't be confirmed.

**0d. Staleness & filename resolution.**
- Initial mode: target file `vault/reports/pre-earnings/{TICKER}-{PRINT-DATE}-initial.md`.
- Gate mode: target file `vault/reports/pre-earnings/{TICKER}-{PRINT-DATE}-gate.md`.

If the target file already exists **and was written today**, stop and
surface the Pre-Commit Plan section. The user can say "rerun" to overwrite.

If gate mode is requested but no initial file exists for this print date,
run initial mode first, then gate mode — two files, written in sequence.

### Step 1: Load Context

**From the dossier — selective reads only:**
- `vault/companies/{TICKER}/_meta.md` — key facts (dual-class, 10b5-1 status,
  emerging growth flags, next-earnings date, any agent-must-know warnings).
  Age check: if last refreshed >90 days ago, flag at the top of the output.
- `vault/companies/{TICKER}/financials.md` — prior-quarter actuals,
  management guidance history, revenue/segment breakdowns. This is the
  primary source for the Management Credibility Check.
- `vault/companies/{TICKER}/insider-activity.md` — 10b5-1 plan cadence, any
  deviation, recent filings. Primary source for Insider Behavior Going In.
- `vault/companies/{TICKER}/risks.md` — distilled 10-K risk factors; map
  to KPIs the call could touch.
- `vault/companies/{TICKER}/compensation.md` — which KPIs exec comp pays
  on. These are the numbers management will lean on in commentary.
- `vault/companies/{TICKER}/execution-thesis.md` (if it exists) — 1-12
  month execution synthesis. Read H1's evidence rows (which schedule
  claims have independent corroboration going into the print), H3's slip
  indicators (which gates are at risk — predictors of negative-surprise
  risk on the call), and the 30/60/90-day watch list (signals the call
  itself may update). Feeds the Management Credibility Check (Step 3 in
  the pre-earnings workflow) — if H3 is active, the call is the moment
  mgmt either admits slip or doubles down. **Respect the audit-status
  banner:** if `audit-failed … H2 retracted` or `audit-failed …
  structural issues`, or if `mtime(execution-audit.md) >
  mtime(execution-thesis.md)` (audit is newer than thesis — corrections
  not yet folded), also read `execution-audit.md` and prefer its
  corrections over the thesis file's content. If `unaudited`, weight H2
  lower than audited H2.
- Skip `overview.md`, `leadership.md`, `ownership.md`, and `projects.md`
  (the raw signal layer — execution-thesis.md is the synthesis you want)
  unless something specific in the dossier flags them as relevant for
  this print.

**From the rest of the vault — narrow reads only:**
- `vault/notes/` — read only files whose name contains the ticker. Sort
  by date desc. Read the most recent 2–3. Extract stated plan around the
  print, price targets, invalidation conditions. Apply temporal reasoning
  (newest supersedes older). **Also scan the same files for mentions of
  other tickers** — those are rotation candidates the user is actively
  considering; they seed Step 3j.
- `vault/deep-dives/{TICKER}-*.md` — read only the most recent. Extract
  verdict, named price levels, thesis summary, and the blank-slate sizing
  from the Blank-Slate Reframe section (anchor for Step 3j).
- `vault/!Journalit/` — instead of scanning files yourself, call:
  ```bash
  python .claude/scripts/get_positions.py --ticker TICKER --format json
  ```
  Returns shares_held, avg_cost (weighted), realized_pnl from partial
  exits, current_price, and unrealized_pct. The scenario ladder priced
  in "your actual share count" anchors on `shares_held` from this output;
  Step 3a's snapshot table reads the rest. If no row is returned, the
  user has no open position — note it explicitly so the ladder switches
  to a "starter position" frame instead of a "managing existing exposure"
  frame.
- `vault/watchlist.md` — full file. Extract Tier 1 tickers (for Step 3j
  rotation candidates) and any notes on the target ticker.
- `vault/deep-dives/` — for each Tier 1 ticker *also mentioned in the
  target ticker's recent notes* (rotation-candidate filter), read the
  most recent deep-dive file. Extract verdict, current ladder zone, own
  next-earnings date. If no deep-dive on file for a candidate, skip it —
  don't guess. Cap at 2 candidates total — this is a pre-earnings check,
  not a portfolio review.
- `vault/library/research/C3 - Post-Earnings-Announcement Drift.md` — read
  this ONE empirical-priors note (only this one; pre-earnings does not
  bulk-read `library/`). It's the single research prior relevant to a print.
  Apply it as **adjacent** evidence in the Scenario Ladder (3c) and
  Pre-Commit Plan (3b): a genuine earnings surprise drifts for weeks-to-
  quarters and re-accelerates at the *next* print, so the plan / holding
  window should **allow for** persistence (longer than the +5d horizon).
  **Do not increase position size solely because of PEAD** — it shapes the
  holding window, not a sizing multiplier. Respect its **What this is NOT**:
  PEAD is a cross-sectional average (not a single-name guarantee) that has
  decayed as it's been arbitraged, so it shapes *expectation of persistence*,
  not a sizing multiplier.

**Do not read** full `notes/`, full `library/`, or every `reports/daily/`
— that's the deep-dive's job. Pre-earnings is scoped to the print question
plus the rotation alternatives that are already on the user's radar.
*Exception:* the single research note named above
([[C3 - Post-Earnings-Announcement Drift]]), and Step 4 (gate-mode-only)
reads the most recent daily alert covering the ticker, if one exists,
before its own news search.

### Step 2: Fetch Live Data

Run two scripts:

```
python .claude/skills/pre-earnings/scripts/get_earnings_setup.py --ticker {TICKER}
python .claude/skills/pre-earnings/scripts/get_implied_move.py --ticker {TICKER}
```

The setup script emits:
- `nextEarnings` (date, trading days until)
- `consensusEstimates` (EPS + revenue, current Q / next Q / current FY, with
  analyst counts and YoY growth)
- `consensusEstimates.revisions` (up/down last 7d / 30d)
- `beatMissHistory` (last 8 quarters: date, estimate, reported, surprise %,
  1-day reaction %)
- `guidanceTrajectory` (accelerating / decelerating / steady + avg surprise)

The implied-move script emits:
- `impliedMovePct` (ATM straddle / spot on first expiry ≥ print date)
- `historicalRealized` (n, mean, median, max of abs 1-day post-print moves)
- `richness` (rich / fair / cheap based on implied vs. realized median)

**If either script fails:** record the failure in the output and continue
with partial data. Do not fabricate numbers.

**Pre-IPO / thin-history tickers (e.g., a name public <1 year):** beat/miss history and
realized moves may be insufficient. Emit "insufficient history" and move
on — the scenario ladder still works off thesis + consensus + implied move.

### Step 3: Build the Report

Use the template at `references/pre-earnings-template.md`. The template is
split into two halves — actionable sections above the horizontal rule,
reference sections below. This mirrors the deep-dive layout: the reader
should see the orders and the decision at the top; the numbers that
support them live below.

**Write sequence matters:** analyze the reference sections first (you need
the numbers), then write the actionable sections last (you need the
analysis to write concrete orders). The order in the file is inverted
from the order of reasoning.

---

**Actionable (top of file, above the rule):**

**3a. Snapshot** — compact table: shares × basis × % portfolio, unrealized
P&L, spot, implied move + richness, last deep-dive verdict + age,
**blank-slate sizing vs. current** (this one line is the anchor for the
entire rotation check), most recent thesis note, stated plan going in.

**3b. Pre-Commit Plan** — 2–5 lines. Exact orders, exact conditions, exact
share counts. Written last, placed here. Synthesizes from the Scenario
Ladder, Concentration Stress Test, and Rotation Check below it. If
Rotation Check fired (trim-and-rotate or trim-to-cash), the standing trim
order goes FIRST — it executes regardless of the print outcome.

**3c. Scenario Ladder** — five rows, keyed to the user's actual share
count. Columns: scenario, probability, price zone, $ move from spot, $
P&L on position, **pre-commit action**. The core artifact — it's what
the Pre-Commit Plan rolls up.

**3d. Rotation Check — [[Opportunity-cost lens]]** — the capital at tail
risk is not free; it could be deployed to a Tier 1 watchlist name instead.
This section names 1–2 specific rotation candidates (from Tier 1 **and**
already mentioned in the target ticker's recent notes), pulls their most
recent deep-dive verdict + current ladder zone + own next-earnings timing,
and produces one of three verdicts:

- **Hold full size through print** — no compelling rotation (candidates
  in trim zone, or have own earnings tail risk within 30d, or no deep-dive
  on file to anchor the alternative)
- **Trim N shares → rotate to [TICKER]** — candidate is in buy-below zone
  per its deep-dive, no own earnings catalyst < 30d, prior verdict was
  ADD — redeployed capital has higher 30d EV than absorbing this print's
  tail risk
- **Trim N shares → hold cash** — overweight per blank-slate, tail risk
  asymmetric, but no Tier 1 name compelling right now — lock the hedge,
  wait for next deep-dive-flagged setup

If the deep-dive's Blank-Slate Reframe said the position is overweight,
the rotation check must address it. If blank-slate said underweight, a
rotation-out is unlikely — emphasize the hold case. If the deep-dive is
>30 days old, flag that the sizing anchor may be stale.

Do not re-analyze candidates from scratch. The deep-dive files are the
authority; pre-earnings synthesizes the rotation question on top of them.
If a candidate has no deep-dive on file, skip it — don't guess. Pre-earnings
does not re-run blank-slate analysis; it references the deep-dive's existing
blank-slate output as the sizing anchor.

**3e. Concentration Stress Test** — tail scenario (Miss + cut) $ loss at
current weight vs. trimmed-to-X weight. 1–2 sentences on expected value
across the ladder, not just "what if it rips."

**3f. Gate Update** — populated in gate mode only. Blank/omitted in initial mode.

---

**Reference (bottom of file, below the rule):**

**3g. Consensus & Setup** — consensus table, revisions last 30d, beat/miss
trajectory table. Describe the pattern the numbers show (don't invent one).

**3h. Business-Specific KPIs** — 4–6 KPIs pulled from the dossier's
`financials.md` + the most recent thesis note. Generic EPS is not enough;
for a subscription / SaaS name it's net revenue retention / revenue per
customer / adj EBITDA margin / guidance. For an infra stock it might be
power contracted / utilization / backlog / customer concentration. The
point is: the numbers that move *this*
stock when reported, not every stock.

**3i. Management Credibility Check** — prior-quarter guidance (from
`financials.md`) vs. what they delivered. If there's no prior guidance on
record (first-year public), say so. Incentive-context line: what KPIs
exec comp pays on (from `compensation.md`).

**3j. Implied Move — Detail** — the full table from the implied-move
script (strike, straddle, richness) plus historical moves detail. The
Snapshot already shows the headline implied% and richness tag.

**3k. Insider Behavior Going In** — from `insider-activity.md`. The key
distinction: 10b5-1 sales are routine (no signal); deviations from plan
or unusual timing are signal. Be explicit about which applies.

**3l. Questions for the Call** — 3–5 specific, thesis-tied questions. Not
generic. If the user's thesis bets on member growth re-accelerating,
question 1 is about member growth, not about "how's demand."

**3m. Proposed Watchlist Updates** *(only if ticker is on `vault/watchlist.md` — any tier)* — appended at the bottom of the file. Same format as the `stock-deep-dive` block. After Step 5 writes the file, Step 5b (below) runs the shared apply script to write the proposals directly into `vault/watchlist.md`'s `## Price Triggers` and `## Planned Tranches` tables. The block in this file is the audit trail.

Scoping rules — pre-earnings proposals are tactical; deep-dive proposals are strategic:

- **Price Trigger (Buy Below / Trim Above):** default to `unchanged`. Only revise these if the print already happened (gate-mode post-print retrospective, rare) or the pre-earnings analysis surfaces a thesis-level change. Long-horizon levels are the deep-dive's authority.
- **Backstop for missing deep-dive levels:** before defaulting to `unchanged`, compare the most recent deep-dive's price ladder against the current `vault/watchlist.md` row. If the deep-dive's ladder names a `Trim above $X` (or `Buy below $X`) level that is **missing** from the watchlist row (cell is `—` or absent), propose it here with `Confidence: med` and a Rationale citing `[[TICKER-YYYY-MM-DD]]`. This is a defect-recovery path for cases where the deep-dive failed to emit its own Proposed Watchlist Updates block. Do **not** override a level the watchlist already has — that's the deep-dive's authority. Only fill empty cells the deep-dive should have filled.
- **Planned Tranches:** this is where pre-earnings contributes most. Emit one `Add:` line per concrete pre-commit order in Step 3b. Expiries should anchor to the print date:
  - Pre-print trims (standing trim, momentum-trim contingency): expire on `print_date - 1` (the gate run will execute or cancel).
  - Post-print contingency orders (buy-the-dip, trim-the-rip, sell-on-miss): expire `print_date + 5 to 10 trading days` — the scenario ladder is a one-week horizon, orders past that should re-anchor to a fresh deep-dive.

  Each `Add:` line includes an `order=` field — `GTC`, `Alert`, or
  `Conditional GTC`. For pre-earnings tranches:
  - **Conditional GTC** is the typical case for post-print contingency
    orders. The print is the gating event; once it resolves, the user
    converts the row to a real GTC. Put the gating condition in the
    note (e.g., "place GTC after May 5 print on beat-and-raise" or
    "place GTC after May 5 print on miss confirmation").
  - **Alert** for pre-print contingencies that depend on intraday
    momentum reads (e.g., "trim 20 if stock runs to $46 before T-2") —
    those need a human at the screen to validate the run is genuine
    pre-print momentum and not a false start.
  - **GTC** is rare in pre-earnings. Use only when the order should
    execute regardless of the print outcome — typically a standing
    rotation trim already pre-committed in a prior deep-dive. Don't
    default to GTC; the binary risk of an earnings print is the entire
    reason the gate-mode pattern exists.
- **Confidence:** set `high` for orders with specific prices and conditions (most pre-commit plans); set `med` if the order has a soft condition ("if it runs..."); use `low` rarely — pre-earnings is supposed to produce committed plans.
- **Rationale:** cite the Scenario Ladder row that justifies the tranche.

**Gate mode:** emit a refreshed proposal block. Re-emit the post-print orders with updated prices. If the gate delta was small, re-emit the same tranches with the same expiries — the apply script is idempotent on identical rows. Use `Remove:` lines to explicitly retire tranches the gate has invalidated.

**Non-watchlist tickers:** skip the Proposed Watchlist Updates block (no watchlist row to update). Instead, follow the same Step 8b semantics from `stock-deep-dive`:

- **If the pre-earnings analysis surfaces a concrete long-horizon Buy Below or Trim Above level** (e.g., the post-print scenario ladder names a clean dip-buy zone, or the gate run identifies a thesis-invalidation level), upsert one row into `vault/price-triggers.md`. Use today's date as `Last Reviewed`, set `Source` to a wikilink to this pre-earnings file, and populate `Funded-by` / `Prefer-over` only if the analysis named them. **Guardrail:** if a row already exists for this ticker AND its `Source` points to a deep-dive file dated within the last 14 days, leave the row alone — deep-dive owns long-horizon levels, and a recent deep-dive's authority should not be silently overwritten by a tactical pre-earnings run.
- **If the analysis only produces tactical print-anchored tranches** (the typical case), do not write to `vault/price-triggers.md`. Tactical orders without a long-horizon level have nowhere durable to land — they expire with the print and don't belong in the broader-universe alert pipeline.
- **Default is no-op.** Most pre-earnings runs on non-watchlist tickers should not write here — long-horizon levels are deep-dive's authority. The pre-earnings path exists to plug the gap when a print materially establishes a new entry/exit level on a ticker that doesn't have a recent deep dive.

### Step 4: Gate-Mode Specifics *(gate mode only)*

Gate runs read the initial file first and compute a delta:

- Consensus delta: has EPS / revenue consensus moved since initial?
- Revisions delta: analyst up/down in the last 7d only.
- Implied-move delta: implied now vs. implied at initial run.
- Stock delta: price at initial vs. price now.
- Insider delta: any new filings since initial run date.
- News delta: max 3 bullet items. If the user has a recent daily alert
  covering the ticker, pull from that; otherwise use a single Exa search:
  `"[TICKER] news last 7 days"`.

The gate file re-emits the full scenario ladder with updated probabilities
where warranted, and a single-line **Final order** that collapses the
initial plan's conditional logic into the one order being placed today.

### Step 5: Write & Surface

Write the file to `vault/reports/pre-earnings/`. Create the folder if
absent.

After writing, print the **Pre-Commit Plan** section to chat verbatim. Do
not duplicate any other section to chat — the user can open the file for
the rest.

**Do not delete prior pre-earnings files.** Each print is its own event and
the history is valuable for quarterly-review calibration (comparing what
you thought would happen to what did).

### Step 5b: Apply Watchlist Updates *(watchlist tickers only)*

For watchlist tickers, immediately after Step 5 writes the file, run the
shared apply script to write the proposal block into `vault/watchlist.md`:

```bash
python .claude/scripts/apply_watchlist_updates.py vault/reports/pre-earnings/TICKER-PRINTDATE-{initial|gate}.md
```

The script upserts the Price Trigger row and applies `Add:` / `Remove:`
tranche operations. Idempotent — safe to re-run on the same file. `med`
and `high` confidence levels apply; `low` is logged as skipped.

This replaces the old propose-via-block / weekly-review-promotes pattern.
Pre-earnings tranches are most valuable in the days right after the run
(intraday Pushover triggers fire on `## Planned Tranches` rows), so
proposals must land on the same day, not the following Friday.

**Skip for non-watchlist tickers** — they have no row in `watchlist.md`,
so there's nothing to apply. The non-watchlist Step 3m branch already
writes directly to `vault/price-triggers.md` when applicable.

---

## Constraints

- **Require the dossier.** Step 0b is a hard gate. Do not try to build the
  dossier inline — that's the `company-dossier` skill's job.
- **No verdict mixing.** Pre-earnings does not produce HOLD/ADD/REDUCE/WATCH.
  Those are the deep-dive's output. If the initial run surfaces a thesis
  crack, flag it and recommend running `stock-deep-dive` — do not try to
  resolve it here.
- **No hallucinated numbers.** Every number cited in the output must come
  from a script, the dossier, or a vault file. If unavailable, write "N/A"
  or "insufficient history."
- **Scoped reads.** Read the selective dossier files (Step 1) + narrow
  vault files only. Don't re-read the whole vault.
- **Pre-commit, not predict.** The scenario ladder's job is to force
  decisions in advance of emotional pressure, not to forecast outcomes.
  Probabilities are anchors for the action column, not calibrated bets.
- **Temporal reasoning.** Newest thesis note supersedes older ones. If a
  note from 4 months ago says "trim at $60" and a note from last week
  says "hold through $70," the recent note wins — the old one is context.
- **Gate is not a re-run.** If you catch yourself re-doing the scenario
  work from scratch in a gate run, stop — the initial file already has
  it. The gate's job is *delta*: what moved, does the plan still hold,
  what's the one order I'm placing today.
- **Watchlist writes go through Step 5b's apply script.** Pre-earnings emits the `Proposed Watchlist Updates` block to its report file (audit trail) and then runs `apply_watchlist_updates.py` for watchlist tickers. Non-watchlist tickers' long-horizon levels write to `vault/price-triggers.md` per the rules above. Do not edit `vault/watchlist.md` or `vault/price-triggers.md` by hand from this skill — go through the documented paths.

---

## Example invocations

- `"pre-earnings VRT"` → auto-detect mode from `_meta.md`'s next-earnings date
- `"run pre-earnings on VRT"` → same
- `"pre-earnings VRT gate"` → force gate mode (runs initial first if absent)
- `"pre-earnings VRT initial"` → force initial (even if <2 TD out)

---

## Interactions with other skills

- **`company-dossier`** is a hard dependency. If the dossier is missing
  or >90 days stale, pre-earnings flags and (for missing) stops.
- **`stock-deep-dive`** is the escape hatch when the thesis itself cracks.
  Pre-earnings never resolves a thesis dispute; it escalates. Deep-dive
  also reads the most recent pre-earnings file for the ticker during its
  own context-load step (for pre-commit plan context).
- **`news-analyst`** may flag earnings-related news in daily reports —
  gate-mode reads the most recent daily alert for the ticker before
  running its own search. Also: when a Tier 1 ticker has a pre-earnings
  file with print date within ~10 trading days, `news-analyst` surfaces a
  one-liner reminder (pre-commit plan exists, check it before acting).
- **`weekly-review`** runs housekeeping over `vault/watchlist.md` —
  expired-tranche cleanup and stale-row pruning. Pre-earnings (and
  deep-dive, pre-ipo) write proposed updates directly via Step 5b's
  apply script; weekly-review no longer promotes proposal blocks.
- **`quarterly-review`** reads `vault/reports/pre-earnings/` during
  calibration: did the pre-commit plans play out? Were the scenario
  ladder probabilities reasonable vs. the realized post-print move? This
  is why pre-earnings files are not deleted after the print.
