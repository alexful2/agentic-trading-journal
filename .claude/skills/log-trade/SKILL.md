---
name: log-trade
description: >
  Log a buy or sell into the vault's trade log directly from a Claude Code
  session — no separate plugin needed. Handles opening a position, adding a
  tranche, trimming, and fully closing. Writes/updates one markdown trade file
  per trade in the format get_positions.py reads (Journalit-compatible). Use
  when the user says they bought or sold a stock, e.g. "I just bought 50 NVDA
  at 118.40", "sold half my VRT at 132", "log a buy: 100 IREN @ 9.20",
  "close out my DLR position at 178". This skill writes a financial record —
  it never invents a price or size; if either is missing, it asks.
---

# Log Trade

## Purpose

Record an actual fill into the vault's trade log without leaving the session.
The natural workflow is: deep-dive a name, talk it through, decide, place the
order in your broker, then tell Claude "done, I bought X" — and this skill
writes it to the same files `get_positions.py` reads, so every other skill
(news-analyst, pre-trade, stock-deep-dive, pre-earnings, the intraday worker)
immediately sees the updated position.

This replaces the manual step of logging trades in the Journalit Obsidian
plugin. The file format is identical to Journalit's export, so the two are
interchangeable — Journalit stays an optional GUI, not a requirement.

**This skill writes a financial record. Two hard rules:**

1. **Never fabricate a number.** Entry/exit price and size come from the user.
   If either is missing or ambiguous, ask — do not guess, and do not pull a
   live market price to fill in a fill price.
2. **Echo before you write.** Restate the parsed action (ticker, buy/sell,
   size, price, resulting position) in one line, then write. The user already
   intends to log it, so don't block on a yes/no — but the echo lets them catch
   a misparse.

This is not investment advice; it is bookkeeping.

---

## Where trades live

The parser (`get_positions.py`) **pools** two folders: the neutral
`vault/trades/` and the legacy `vault/!Journalit/`. So:

- **Opening a NEW position:** always write to `vault/trades/` (create the
  folder if it doesn't exist) — even in a vault that still has `!Journalit/`
  history. New positions go to `trades/`; old history stays where it is; the
  parser counts both. This is the migration path off Journalit.
- **Add / trim / close to an EXISTING position:** append to wherever that
  trade's file already lives. A migrated-from-Journalit position keeps living
  in its `!Journalit/…/TICKER-*.md` file — append there, don't make a
  duplicate in `trades/`.

One file per trade, named `TICKER-YYYY-MM-DD.md` using the **open date** of the
trade (the date of the first entry). Adds and trims update that same file.

---

## Workflow

### Step 1: Parse the instruction

Extract from the user's message:

- **Ticker** — uppercase.
- **Action** — buy or sell.
- **Size** — number of shares. Phrases like "half", "a third", "all" are
  relative to the current `shares_held` (see Step 2) — resolve them to a
  concrete share count and show your arithmetic in the echo.
- **Price** — per-share fill price. If the user gives a total dollar amount
  instead ("put $5k in at 118.40"), derive size = floor(amount / price) and say
  so. If price is missing, **ask** — never invent it.
- **Time** — if the user states a time/date, use it. Otherwise use today's date
  (from the session's current-date context) with no intraday time. Format as
  `YYYY-MM-DDTHH:MM:SS`, `YYYY-MM-DDTHH:MM`, or `YYYY-MM-DD`.
- **Direction** — assume `long` unless the user says short.

If size or price can't be determined, ask one concise clarifying question and
stop. Do not write a partial record.

### Step 2: Find current state

Run the position helper for the ticker to see what's already open:

```bash
python .claude/scripts/get_positions.py --ticker TICKER --format json --no-prices
```

Also list **both** trade-log folders (`vault/trades/` and `vault/!Journalit/`,
the latter recursively) for any existing `TICKER-*.md` file — an existing
position may live in either. Determine which of four cases applies:

- **OPEN (new position):** no OPEN trade file for the ticker in either folder →
  create one in `vault/trades/`.
- **ADD (tranche):** an OPEN file exists and the action is a buy → append to
  `entries`.
- **TRIM (partial sell):** an OPEN file exists, action is a sell, and the sell
  size is less than `shares_held` → append to `exits`, keep `tradeStatus: OPEN`.
- **CLOSE (full exit):** an OPEN file exists, action is a sell, and the sell
  size equals (or rounds to) `shares_held` → append to `exits` and flip
  `tradeStatus: CLOSED`.

If more than one OPEN file exists for the ticker (e.g. a Journalit history with
several open trades), append to the **most recent** one and note in the echo
that older open files for the ticker also exist. Never silently merge files.

Guardrails:

- A sell larger than `shares_held` → stop and ask (likely a misparse or a short;
  don't write a negative position).
- A sell with no open position → stop and ask.

### Step 3: Write the file

**Open (new file):**

```markdown
---
type: trade
instrument: TICKER
direction: long
tradeStatus: OPEN
entries:
  - size: 50
    price: 118.40
    time: 2026-06-15
exits: []
tags: []
images: []
---

Opened 2026-06-15. {{one-line rationale if the user gave one, else omit}}
{{Link the governing thesis/deep-dive if obvious from context, e.g.
[[2026-06-10 NVDA thesis]].}}
```

**Add / trim / close (existing file):** append a single item to the relevant
list (`entries` for a buy, `exits` for a sell), preserving every existing item
exactly. On a full close, set `tradeStatus: CLOSED` and append a one-line
"Closed YYYY-MM-DD" note to the body. Use the Edit tool for surgical appends —
never rewrite the whole file from memory, or you risk dropping prior tranches.

Match the existing file's indentation and key order. Keep `exits: []` (not a
bare `exits:`) when there are no exits yet, so the parser reads it as an empty
list.

### Step 4: Confirm

Print a one-line result, e.g.:

> Logged **BUY 25 NVDA @ $112.10** (tranche). NVDA now: **75 sh @ $116.30 avg**,
> file `vault/trades/NVDA-2026-05-12.md`.

For a close, report realized P&L from the helper if available. Then, if the
trade closed a position, remind the user (one line) that a trade-close arc
(`vault/templates/trade-close-template.md` → `library/`) feeds the quarterly
calibration pass — but don't write it unless asked.

---

## What this skill does NOT do

- It does not place orders or touch a broker — it records fills you already made.
- It does not research, score, or produce a verdict (that's `stock-deep-dive` /
  `pre-trade`).
- It does not write theses or notes — only the trade-log file. If the user wants
  the rationale captured, point them at `notes/` or offer to draft a note
  separately.
- It does not edit `watchlist.md`, tripwires, or any other vault file.
