---
name: weekly-review
description: >
  Weekly macro synthesis skill. Reads the past 7 days of daily alerts and
  recent deep dives, runs 5–6 targeted macro searches, and produces a
  dominant-themes / thesis-pressure-test / wait-for-deal
  watch / what-shifted writeup. Output feeds the Friday vault-curator run
  (for library curation context) and the Friday email's Weekly Review
  section (via news-analyst). The daily alert does NOT consume this file
  — daily macro context comes from each day's own broad searches. Writes
  to `vault/reports/weekly/YYYY-WW.md`.
---

# Weekly Review

## Purpose

A weekly macro synthesis, one layer above the daily noise. Step back from
headline-by-headline scoring and identify the 2–3 forces that actually
drove the week. Pressure-test them against your core long-term thesis,
and survey whether any small-to-mid AI infra names are approaching
wait-for-deal territory.

This skill does **only** macro synthesis. It does not scan `notes/` or
`library/` for curation candidates — that's `vault-curator`'s job.

---

## Workflow

### Step 1: Load Context

**`vault/reports/daily/` — past 7 daily alerts:**
- List files, sort by filename (`YYYY-MM-DD.md`), read any dated from
  last Friday through yesterday (Thursday) — the 7 completed days ending
  on Thursday. Do not read today's report; it has not been written yet.
- Extract: dominant themes, recurring news topics, any items that kept
  resurfacing across multiple days, any `run deep-dive` action lines
  issued that didn't turn into deep dives.
- This gives you "what dominated this week" before you search.

**`vault/deep-dives/` — past 7 days:**
- List files (format: `TICKER-YYYY-MM-DD.md`), read any dated within the
  last 7 days.
- Extract: verdict reached, key thesis points, price levels/conditions
  named, whether the stock is on the watchlist, and which historical
  pattern preset applied to today's price (Extended Run / Dip Buyer /
  Pre-Earnings / none — usually labelled in the pattern table).
- Use these to anchor the thesis check — if a deep dive was run this
  week, your synthesis should note whether this week's macro confirms or
  complicates that verdict. The verdict + pattern fields also feed
  Step 3c's distribution check.

**`vault/reports/pre-earnings/` — past 7 days:**
- List files (format: `TICKER-PRINTDATE-{initial,gate}.md`), read any
  whose **file mtime** falls within the last 7 days (the print date in
  the filename can be future-dated). Extract: verdict.
- Used in Step 3c only. If none in the window, skip silently.

**`vault/reports/weekly/` — the prior weekly-review file:**
- List files (format: `YYYY-WW.md`), sort by filename descending, read
  the most recent one (should be last week's).
- This is what you compare against for "What Shifted vs. Last Week".
- If no prior file exists (first-ever run), note that and write:
  "No prior weekly-review to compare against — this is the baseline."

**`vault/library/` — light pointer-read only:**
- List file names. Do not read every file. The purpose is to know what
  thesis areas the user has articulated (e.g., "wait-for-deal-thesis.md",
  "ai-energy-thesis.md").
- If during synthesis you want to cite a specific library entry, read
  that single file then. Don't preload the whole directory.
- **Do read `vault/library/wait-for-deal-thesis.md`** in full before
  Step 3's Wait-for-Deal Watch — that's the actual thesis you're
  applying, so load it once.

**Do NOT load `vault/notes/`.** Notes are vault-curation territory. The
curator reads them; you don't. This keeps the weekly-review run cheap.

---

### Step 2: Macro Searches

**Search tool:** Use `web_search_exa` — it returns better-quality results
for financial and analytical content. If `web_search_exa` is unavailable
(e.g. running in a remote trigger without Exa MCP), fall back to the
built-in `WebSearch` tool for every search instead.

Run 5–6 broad searches to build a current picture of the macro
environment. These are synthesis searches, not stock-specific.

**Searches to run:**
- "macro economic outlook this week [current month year]"
- "AI infrastructure spending investment trends [current month year]"
- "Federal Reserve interest rate outlook latest"
- "US China trade tariff economic impact latest"
- "energy data center power investment news"
- "technology sector macro headwinds tailwinds"

Adapt the wording to the current month/year. If a search returns nothing
useful, skip it rather than padding with a similar query.

---

### Step 3: Synthesize

**Dominant themes (2–3 bullets):**
Identify the forces that actually drove markets this week — not a list of
every story. Each bullet names the theme, describes its current state,
and notes whether it confirms or complicates the AI infrastructure thesis.
Be specific: "data center power constraints tightening as utilities push
back on new load" beats "energy is a factor."

**Thesis Pressure Test:**
Test the week's dominant themes against your core long-term thesis — what
genuinely confirms it, what complicates it? "Confirms" is not the default;
"neutral" and "complicates" are valid results. Use one short bullet per
lens where there's signal this week — skip any lens that was silent:

- **Compute scaling** — hyperscaler capex, GPU buildout, compute bottlenecks
- **Energy buildout** — nuclear, gas, grid investment, power constraints
- **Government / geopolitics** — national security framing, export controls,
  regulatory posture, sovereign AI efforts
- **Demand / adoption** — any concrete evidence the multi-year demand
  trajectory is on or off track

Close with one sentence: overall, did this week confirm, challenge, or
complicate the core thesis? **"Confirms" is not the default answer.**
Honest null is fine — "nothing this week materially moves the thesis" is
a valid result.

**Wait-for-Deal Watch:**
Survey this week's daily alerts and broad searches for small-to-mid AI
infrastructure names that fit the wait-for-deal profile — right lane
(GPU cloud, power/energy for data centers, DC REITs, networking /
interconnect, cooling), no mega-deal signed yet. **No extra searches** —
synthesize from what's already been covered this week.

Output format: 0–3 candidates. For each: name (+ ticker or "pre-IPO"),
one-line "what they do", one-line "why they fit", and a status signal
(e.g., "rumored deal talks with Anthropic" or "quiet, but buildout on
schedule"). If nothing compelling this week, write "Nothing compelling
this week." and move on — don't force candidates.

**What shifted vs. last week (1–2 sentences):**
Compare against the prior weekly-review file. Is anything meaningfully
different from last week's picture, or is it more of the same? "Largely
unchanged" is a valid answer if it's true — don't manufacture shifts.

**Deep dive anchors (conditional):**
If any deep dive was run this week (found in Step 1), note whether this
week's macro confirms or complicates its verdict. If no deep dives this
week, write "No deep dives this week." and move on.

---

### Step 3c: Verdict Distribution Check

Meta-pattern across all reports loaded in Step 1 — catches the failure
mode where every analysis comes back "good stock, don't buy now" and
that's really a macro signal (or analyzer bias), not N independent
ticker calls.

**Skip entirely** if total reports (deep-dives + pre-earnings) < 3. A
one- or two-row tally is more misleading than no tally. Write
"Insufficient sample (N=X) — skipping." in the section and move on.

**Tally:**
1. For each deep-dive: extract verdict (HOLD / ADD / REDUCE / WATCH) and
   the pattern-preset flag for today's price (Extended Run / Dip Buyer /
   Pre-Earnings / none).
2. For each pre-earnings file: extract verdict.
3. Count the WATCH+REDUCE share (cautious) vs. ADD share (constructive).
4. Count the Extended Run share among deep-dives (proxy for "I've been
   asking about names that already ran").

**Compare with this week's macro read** (already synthesized above in
Dominant Themes + Thesis Pressure Test). Pick one of four templates:

1. **Cautious skew + Extended-Run share high + macro not-rich** →
   *Selection bias.* Most deep-dives this week were on names that had
   already run; the WATCH verdicts are likely correct but uninteresting.
   Recommend looking elsewhere — list watchlist Tier 2/3 tickers that
   haven't been deep-dived in 30+ days as candidates for next week's
   selection. Source: `vault/watchlist.md` cross-referenced with
   filenames in `vault/deep-dives/` (most recent file per ticker).
2. **Cautious skew + Extended-Run share low + macro rich/late-cycle** →
   *Skew matches macro.* Sectors broadly rich, sit on hands. This isn't
   analyzer bias.
3. **Constructive skew + macro late-cycle/risk-off** → *Skew contradicts
   macro.* Re-check the ADD calls before sizing up; analyzer may be
   missing risk.
4. **Mixed distribution, no clear pattern** → *Distribution looks
   healthy — verdicts vary, no obvious bias.* Move on.

**Honest null is fine.** If only one ticker was deep-dived but the
extended-name-bias signal is loud, you can still flag it as a
single-data-point hint without forcing a four-quadrant call. Don't
manufacture a pattern.

---

### Step 3d: Tripwire Review

Read `vault/tripwires.md`. For each `ARMED` tripwire, check it against this
week's daily alerts, deep dives, and macro searches — the **systematic** pass
that catches slow fundamental tripwires the daily news flow won't trigger on.
For each:

- **Tripped** (the written condition is now met) → flag it in the weekly output
  (a `Tripwires:` line) with `run deep-dive TICKER`, and set its `Status` to
  `TRIPPED` in `vault/tripwires.md` (Edit in place).
- **Approaching** → one-line note; leave it `ARMED`.
- **Obsolete** (thesis changed, position closed) → set `RETIRED`.

If no tripwires are `ARMED`, write "No active tripwires." and move on. Don't
fabricate trips — a tripwire fires only when its written condition is met.

---

### Step 3b: Watchlist Housekeeping

Promotion of `## Proposed Watchlist Updates` blocks happens at write-time
inside `stock-deep-dive`, `pre-earnings`, and `pre-ipo` (each runs
`apply_watchlist_updates.py` immediately after writing its file). This
step is now housekeeping only — pruning rows that have aged out.

**Expired tranche cleanup:**
Scan `vault/watchlist.md` → `## Planned Tranches` for rows where the
`Expires` date is older than today. Delete each. Note the deletion in
the weekly review output. Use the Edit tool to modify in place;
preserve the rest of the table formatting.

**Stale price-trigger cleanup:**
Scan `vault/price-triggers.md` → `## Price Triggers` for rows where
`Last Reviewed` is older than **60 days**. Delete each and list them in
the weekly review output under `Price-trigger cleanup:` with format
`TICKER (last reviewed YYYY-MM-DD)`. Rationale: deep-dive auto-writes
to this file for non-watchlist tickers, but nothing else removes rows
once they age past the 30-day STALE threshold in `check_price_triggers.py`.
Without this pass, the file accumulates dead rows indefinitely. The
60-day threshold gives a 30-day post-STALE grace window before cleanup.
If `price-triggers.md` doesn't exist yet, skip silently.

**Re-application backstop (optional, defensive):**
If the apply script failed to run for any reason during a deep-dive /
pre-earnings / pre-ipo run earlier in the week (e.g., a transient error
in the routine), the proposal block is still in the source file. Rerun
the apply script across the past-week's files to catch any misses:

```bash
for f in $(ls -1t vault/deep-dives/*.md vault/reports/pre-earnings/*.md vault/reports/pre-ipo/*.md 2>/dev/null | head -20); do
  python .claude/scripts/apply_watchlist_updates.py "$f"
done
```

The script is idempotent — already-applied changes are no-ops apart from
refreshing `Last Reviewed`. Skip this step if you have no reason to
suspect a missed run.

**Update the footer:** if anything changed, bump
`*Last updated: YYYY-MM-DD*` to today's date.

**Capture the cleanup diff** for the weekly-review output —
`## Watchlist Housekeeping` section per the template, listing what was
pruned.

---

### Step 4: Write Output

Output path: `vault/reports/weekly/YYYY-WW.md` where `YYYY-WW` is the
current ISO week (e.g., `2026-W16`).

If `vault/reports/weekly/` doesn't exist, create it.

Use the template in `references/report-template.md`.

Include `[[wikilinks]]` when referencing specific vault files (deep dives,
library entries, prior weekly-reviews).

---

## Constraints

- **Grounded only.** Every claim must tie back to a search result or a
  recent daily alert / deep dive. No riffing on general macro vibes.
- **Bearish signal gets reported.** If the thesis is genuinely challenged
  this week, the synthesis must say so. Do not soften.
- **No hallucinated sources.** If a search returns nothing compelling
  for a theme, say so rather than inventing citations.
- **Quality over length.** A short, honest synthesis beats a padded one.
  Target: under ~500 words total.
- **Do not write to `library/`, `notes/`, or the daily `reports/daily/`.**
  Writable locations: `vault/reports/weekly/` (this week's review file),
  `vault/watchlist.md` (Step 3b housekeeping — expired-tranche pruning),
  `vault/price-triggers.md` (Step 3b housekeeping — stale-row pruning),
  and `vault/tripwires.md` (Step 3d — tripwire status updates only).
  Promotion of new triggers/tranches happens at write-time in deep-dive,
  pre-earnings, and pre-ipo via `apply_watchlist_updates.py` — not here.
- **The pressure test is not a persona cosplay.** Apply the thesis as an
  analytical lens, not as a "what would a guru say" riff. Tie each bullet
  to specific news items from this week's reports or searches.
