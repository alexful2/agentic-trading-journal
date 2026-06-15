---
name: pre-trade
description: >
  Quick pre-order context check before placing a buy or sell. Reads the
  most recent thesis notes, most recent deep-dive, recent severity ≥3
  daily alerts, and trade-log position status for a specific ticker.
  Outputs a terminal summary only — no file writes, no searches. This
  is the 20-second "are you sure?" gate, different in shape from the
  full `stock-deep-dive` skill. Usage: `pre-trade TICKER` or "run pre-trade
  on NVDA".
---

# Pre-Trade

## Purpose

A last-second context check before I click buy or sell. The goal is to
surface what I already know about this ticker — most recent thesis, most
recent verdict, any news the system has flagged, current position — and
make me confirm the action aligns with my own recent guidance.

This skill does **not** do research. It does not search the web. It does
not produce a verdict. It does not write a file. It's a mirror: "here's
what you already decided about this — still want to?"

When I need fresh research, I run `stock-deep-dive`. Pre-trade is faster
and cheaper and runs at a different moment — right before the order.

---

## Workflow

### Step 1: Parse ticker

From the user's invocation, extract the ticker (e.g., "pre-trade NVDA" →
`NVDA`). Case-insensitive, but always display as uppercase.

### Step 2: Load Context

**`vault/watchlist.md`:**
- Find the ticker's current tier (T1 / T2 / T3) and any notes beside it.
- If the ticker isn't in the watchlist, say so explicitly — that itself
  is a gut-check signal.

**Open position (via `get_positions.py`):**

Run the position helper for the target ticker:

```bash
python .claude/scripts/get_positions.py --ticker TICKER --format json
```

This walks the trade-log folder (`vault/trades/`, or `vault/!Journalit/`
for Journalit users) and aggregates all OPEN trades for the ticker into one
row. Extract from the JSON:
- `shares_held`, `avg_cost`, `first_entry_date`
- `current_price`, `unrealized_pct`, `unrealized_pnl`
- `realized_pnl` (gain/loss already booked from partial exits)

If `positions` is empty AND the ticker isn't on the watchlist, flag it: the
user is considering a brand-new name with no prior framing. If the script
errors (price fetch failure), still surface the position fields and note the
missing live price — the cost basis and entry date are useful even without
today's quote.

**`vault/notes/` — ticker-specific notes:**
- List files, find any whose filename or content references the ticker.
- Sort by date descending, read the most recent 2–3.
- Apply temporal reasoning: the newest note supersedes older ones. If
  targets or plans differ across notes, use the newest and flag the
  revision.

**`vault/deep-dives/TICKER-*.md`:**
- Find the most recent deep dive for this ticker (by filename date).
- Extract: verdict (HOLD / ADD / REDUCE / WATCH), date issued, specific
  price levels or conditions named, any thesis flags, the Portfolio Fit
  & Timing section's bottom-line guidance.
- If no deep dive exists, say so — that's useful too.

**`vault/reports/daily/` — last 14 days:**
- List files in `vault/reports/daily/`, filter to the 14 most recent.
- Scan each for any flagged item (severity ≥3) touching this ticker
  (direct or in the Why It Matters line).
- Collect: date, severity, one-line headline, action line from that alert.

### Step 3: Synthesize — Terminal Output

**Do not write any file.** Print the following structure to the terminal:

```
═══════════════════════════════════════════════════════════
  PRE-TRADE CHECK — {{TICKER}}
═══════════════════════════════════════════════════════════

Watchlist tier:    {{T1 / T2 / T3 / NOT ON WATCHLIST}}
Current position:  {{shares @ $cost_basis, opened YYYY-MM-DD | NONE}}
Live P&L:          {{unrealized $X (+Y%); realized $Z | unrealized N/A — price source error}}

─── Most recent thesis ─────────────────────────────────────
{{date}} — {{filename}}
{{1–2 line summary of the current thesis, targets, and any
named invalidation conditions. Flag revisions vs. older notes.}}

─── Most recent deep-dive ──────────────────────────────────
{{date}} — {{TICKER-YYYY-MM-DD}}
Verdict: {{HOLD / ADD / REDUCE / WATCH}}
Conditions: {{specific price levels, dates, or triggers named}}
Bottom line: {{1-line summary from Portfolio Fit & Timing}}
  [or: "No deep-dive on file. Consider running `deep-dive TICKER`
   before significant sizing decisions."]

─── Recent alerts (last 14 days, sev ≥3) ───────────────────
{{YYYY-MM-DD}} [sev {{X}}]  {{headline}}
  Action issued: {{action line from that alert}}
{{...repeat for each...}}
  [or: "No sev ≥3 alerts on this ticker in last 14 days."]

─── Gut-check questions ────────────────────────────────────
1. Does the action you're about to take match the most recent
   deep-dive verdict ({{verdict}})?
2. Have any named conditions been met or invalidated since then?
3. {{If >1 alert in last 14 days: "The system flagged this ticker
     {{N}} times recently — is your action consistent with those
     action lines?"}}
4. {{If the most recent thesis revised an older one: "Note: the
     {{old target/plan}} was revised on {{date}}. Are you acting
     on the revision or the stale version?"}}
5. {{If SELLING a winner or adding to a loser: "Disposition-effect check —
     investors systematically sell winners early and hold losers too long.
     Is this an opportunity-cost decision, or loss aversion?" — If BUYING
     into a name up sharply lately: "Chasing check — a fresh thesis-
     confirming catalyst makes strength repricing, not FOMO; with no new
     catalyst, extreme recent spikes tend to fade." Reflexive prompt only —
     pre-trade reads no research notes; the full priors live in
     library/research/ (C6 / C10 / C4 / C12).}}

═══════════════════════════════════════════════════════════
```

### Step 4: End

That's it. No verdict. No "you should do X." The user decides.

---

## Constraints

- **Read-only.** Never write to any file. Never create reports.
- **No web searches.** Exa, WebSearch — all forbidden in this skill.
  Fresh information is the `stock-deep-dive` skill's job.
- **No verdicts.** This skill surfaces context, it doesn't recommend.
- **Fast.** The whole run should complete in under ~30 seconds. If it's
  taking longer, cut scope — the user is waiting before clicking buy.
- **Ticker-scoped.** Do not analyze other tickers, don't riff on market
  conditions, don't summarize the portfolio. Just the ticker in question.
- **Temporal reasoning applies.** Newer notes supersede older notes.
  Flag revisions rather than presenting stale targets as current.
- **Honest nulls.** "No deep-dive on file" / "Not on watchlist" / "No
  recent alerts" are all useful outputs. Don't manufacture context.
