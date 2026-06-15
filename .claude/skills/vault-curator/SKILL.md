---
name: vault-curator
description: >
  Weekly vault health and knowledge curation skill. Scans notes/ and library/
  for implicit beliefs worth articulating, stale library entries, trade-arc
  candidates, and coverage gaps. Runs topic-driven web searches for new
  essays or frameworks worth adding to library/, and an opportunity radar
  for wait-for-deal candidates and upcoming AI infrastructure IPOs. Reads
  the most recent weekly-review file for macro context. Outputs a human-review
  suggestions file to vault/vault-suggestions/. Never writes directly to
  library/ or notes/.
---

# Vault Curator

## Purpose

A weekly knowledge-curation run. Read the vault for implicit beliefs not
yet articulated, flag gaps or stale entries, consolidate closed trades
into library arcs, and run web radar searches for essays, frameworks, or
opportunity candidates worth surfacing.

Macro synthesis is **not** in scope here — that's the `weekly-review` skill's
job. This skill reads the most recent weekly-review output as context for
judging what's stale or newly relevant, but it does not redo the synthesis.

Output is a suggestions file for human review. You never write directly
to `library/` or `notes/`. The user promotes anything they want.

---

## Workflow

### Step 1: Load Vault Context

Read the entire vault to understand current state before doing anything else.

**`vault/library/` — read all files:**
- What principles and frameworks are already articulated?
- What thesis areas are covered? What's missing?
- Note the filename of each file — you'll reference these when flagging stale entries.

**`vault/notes/` — read all files:**
- What stocks does the user hold and why?
- What implicit beliefs show up repeatedly across notes but aren't in library/?
- What patterns exist in how decisions are made?

**`vault/reports/weekly/` — read the most recent weekly-review file:**
- List files (format: `YYYY-WW.md`), sort descending, read the most recent.
- Extract: dominant themes, thesis check, what shifted vs. last week.
- This is your macro context. It shapes which library entries might be
  stale, which implicit beliefs are worth articulating now, and which
  opportunity-radar searches to emphasize.
- Do NOT redo the synthesis. Trust the weekly-review output. If no
  weekly-review file exists yet, proceed without macro context and note
  that in the suggestions file footer.

**`vault/deep-dives/` — read all deep dives from the past 7 days:**
- List files (format: TICKER-YYYY-MM-DD.md), read any dated within
  the last 7 days.
- Extract: the verdict reached, key thesis points, any price levels or
  conditions named, and whether the stock is on the watchlist.
- Use these when judging stale library entries and when framing the
  Opportunity Radar — if a deep dive was already run on a candidate
  this week, surface that rather than re-suggesting.

**`vault/vault-suggestions/` — read the last 4 weeks of suggestions:**
- List all files (format: wiki-YYYY-WW.md), sort by filename descending,
  read the 4 most recent.
- **Check the `status:` frontmatter field on each.** Files marked
  `handled`, `dismissed`, or `superseded` are resolved — skim only for
  context and do NOT re-flag any item from them as carry-forward. Items
  in `pending` files (or files with no status field, treated as pending)
  are fair game for carry-forward.
- Extract: what was flagged before, what's still pending, any recurring
  themes or gaps that have surfaced multiple weeks in a row.
- Use this to avoid re-suggesting things already seen, and to flag when
  a previously noted gap still hasn't been addressed.

---

### Step 2: Vault Introspection

**Search tools (for Step 3 below):**
- `web_search_exa` — use for all web searches. If unavailable (e.g.
  running in a remote trigger without Exa MCP), fall back to built-in
  `WebSearch` for every search instead.
- `crawling_exa` — use when a Block A search surfaces a promising essay
  URL and you want the full article text before deciding whether to suggest
  it. Targeted use only (1-2 URLs max per run). Skip if unavailable.

Using only what you read in Step 1 (no new searches), answer:

**Trade consolidation candidates:**

Cross-reference every note in `vault/notes/` against the trade log (run
`get_positions.py`, or scan the trade-log folder directly for CLOSED trades).
For each note that references a specific trade or position:
- If the corresponding trade-log file has `tradeStatus: CLOSED`, the trade
  is a candidate for a library arc summary. The original notes stay in
  `notes/` — they are the raw record. The arc summary is a synthesized
  lesson that belongs in `library/` for agents to reference quickly.
- Suggest a bullet-point "trade arc" summary to add to `library/`. The arc
  should capture: thesis at entry, how thinking evolved during the hold
  (key updates, pivots, emotional beats), exit reason and outcome, and one
  durable lesson to carry forward.
- Do NOT write the summary yourself. Flag the note(s) and provide a
  short template showing what the arc should contain. The user writes
  or approves the final version before it goes to library/.
- Only flag trades that are definitively closed in the trade log. Open
  positions are never consolidation candidates.
- **Permanently dismissed trade arcs — do NOT re-flag these:**
  - **VRT-OLD** (VRT-OLD-260326-T1, VRT-OLD-010426-T1, VRT-OLD-080426-T1) — user
    declined arc 2026-05-02; trades predate the journal, no recoverable
    pre-trade reasoning, lessons already captured inline in
    [[VRT - 2026-04-30 Retrospective]] and [[extended-with-vs-without-catalyst]].
    Do not surface VRT-OLD as a trade-arc candidate in any future curator run.

Example flag:
> **[[DLR - 2026-04-09 Buy]]** — the trade log shows DLR-140126-T1 is CLOSED.
> Consider writing a trade arc for `library/` capturing: entry rationale,
> how the VRT/pivot thesis evolved, and exit decision. Original notes stay.

**Implicit beliefs worth articulating:**
Look for patterns in `notes/` that recur across multiple entries but have
no corresponding principle in `library/`. Examples of what to look for:
- A decision-making pattern: "the user always does X when Y happens"
- A risk rule that appears implicitly: "the user avoids Z because..."
- A mental model being applied without being named

Only flag these if they're genuinely recurring and non-obvious. One strong
implicit belief surfaced is more useful than five thin ones.

**Possibly stale library entries:**
Cross-reference `library/` against recent notes and this week's macro picture
(from the weekly-review file loaded in Step 1). Flag any library entry where:
- The thesis it describes has been materially challenged recently
- The facts it relies on are from a period that may no longer apply
- Recent notes suggest the user's thinking has evolved past it

**Coverage gaps:**
What themes appear actively in `notes/` that have no counterpart in `library/`?
These are areas where the user clearly has a view but hasn't written it down.

---

### Step 3: Web Radar

Run searches in two blocks: (A) essay/framework radar and (B) opportunity radar.
Both feed into the suggestions file — essays go to Library Suggestions,
stocks go to the Opportunity Radar section.

---

#### Block A: Essay / Framework Radar

4-6 topic-driven searches for durable thinking worth adding to `library/`.
These are NOT stock news searches.

**Search approach:**
- Search by thesis area, not by author.
- Prioritize: essays with a clear framework or mental model, not news articles.
- Skeptical filter: only flag something if it adds a perspective or framework
  that isn't already represented in `library/`. If the user's library already
  covers the idea well, skip it even if the essay is good.

**Searches to run (adapt to current thesis areas):**
- `site:substack.com "AI infrastructure" essay OR analysis`
- "AGI timeline thesis essay [current year]"
- "data center energy power investment framework essay"
- "macro investing principles essay [current year]"
- "technology infrastructure secular trend essay"
- One wildcard: pick a theme from the weekly-review macro synthesis (loaded
  in Step 1) that seems newly important and search for analytical essays on it.

**For each candidate, ask:**
- Does this add something genuinely new relative to what's already in `library/`?
- Is this durable thinking or just a news take that'll be irrelevant next month?
- Would this change how the user thinks about a thesis area, or just restate
  what they already believe?

If the answer to all three isn't clearly yes, skip it. Aim for 1-3 strong
suggestions, not an exhaustive list.

---

#### Block B: Opportunity Radar

This implements the wait-for-deal thesis from `vault/library/Wait-for-deal
thesis.md`. The thesis: AI labs are bottlenecked by compute and energy.
They will sign large partnership deals with smaller GPU providers and power
companies. Buying *before* the deal is the play. The same pattern may apply
to adjacent fields (space industry, biotech compute).

Run 4-5 searches specifically to surface companies that fit this thesis
and haven't yet signed major deals:

**Searches to run:**
- "AI compute GPU cloud provider startup [current year]" — looking for
  small/mid GPU cloud and bare-metal compute companies
- "data center energy power company AI partnership [current year]" — energy
  and power infrastructure companies pursuing AI customers
- "AI infrastructure IPO [current year] OR upcoming [next year]" — IPOs
  in the AI compute/energy/infra space worth watching
- "data-center power/cooling suppliers" OR "alternative AI compute providers" —
  companies in the same lane as companies that have already signed deals
- One wildcard search based on the weekly-review dominant theme most
  relevant to compute/energy bottlenecks this week

**For each company surfaced, ask:**
- Does it fit the wait-for-deal profile? (Small/mid AI infrastructure,
  compute or energy, no mega-deal signed yet, but in the right lane)
- Is it publicly traded? If IPO stage, is it a named upcoming IPO?
- Is it already on the watchlist? If yes, skip — this section is for
  new discoveries only.
- Is there a plausible reason an AI lab would want this company specifically?

Flag 1-3 strong candidates max. If nothing fits the profile, say so — don't
force it. Each flag should say: company name, ticker (or "pre-IPO"), what
they do, why they fit the wait-for-deal lens, and one verification link.

---

### Step 4: Write Suggestions File

Output to `vault/vault-suggestions/wiki-YYYY-WW.md`.

If `vault/vault-suggestions/` doesn't exist, create it first.

Use the template in `references/suggestion-template.md`.

Include `[[wikilinks]]` when referencing specific files in the vault.

**Checkbox per recommendation.** Every actionable suggestion must start
with a `- [ ]` line naming the concrete action and target file path
(e.g. `- [ ] **Promote to** \`library/foo.md\``,
`- [ ] **Run** \`deep-dive TICKER\``,
`- [ ] **Update entry** — reason`). Items with no checkbox are
context-only and won't be processed.

**Layout: heading-style for every suggestion, no `---` between items
within a section.** Each suggestion gets its own `#### {{Title}}` heading,
then the checkbox + placeholder, then a body paragraph. Suggestions stack
back-to-back with only a blank line between them. `---` horizontal rules
appear ONLY at `###` category boundaries (and `##` Part boundaries),
never between items inside the same category. This keeps the placeholder
visually adjacent to its checkbox and avoids ruler clutter.

**Empty placeholder under every checkbox.** Seed a `    - ` (4-space
indent + dash + space) line directly under every `- [ ]` line. This
gives the user a ready indent point to type item-specific instructions
when they tick the box. If left empty, the implementation agent ignores
it.

**Checkbox semantics:** A checked `- [x]` means *"I want this done OR it's
already been done."* The implementation agent that processes ticked items
must verify state per item before acting — if the target file already
exists, the wikilink pointer is already in place, the dossier was already
built, etc., skip with a one-line note rather than overwriting. Unticked
items are ignored entirely. (Carry-forward across weeks still keys off the
file-level `status:` frontmatter, not item-level checkboxes.)

**Nested-bullet override (user-only feature):** the user may indent one or
more bullets directly under a checked `[x]` line to give the implementation
agent item-specific instructions (e.g. length cap, framing emphasis, file
path override). Example:

```
- [x] **Promote to** `library/foo.md`
    - Keep under 80 lines, lead with cohort-fragility ranking, skip macro stats
```

The curator never writes these — the curator's output always has bare
checkboxes. They appear only when the user manually adds them after
checking. The implementation agent reads any indented bullets following a
`[x]` line as item-specific instructions that override or refine the
default action named on the checkbox line.

**Brevity is a hard rule.** Keep each suggestion to ~3-5 lines after the
checkbox. No multi-paragraph syntheses, no compounding "this also relates
to..." threads. If a suggestion needs more than 2-3 sentences to justify,
it's not a suggestion — it's a deep-dive, and the right move is to flag it
as a deep-dive candidate. The whole file should read in under 5 minutes.

---

### Step 4b: IPO Calendar Sync

After writing the suggestions file, sync IPO findings from Block B into
`vault/ipo-calendar.md`. This is the only place outside the `pre-ipo`
skill that writes to that file. The calendar is the date-anchored
reminder layer that `news-analyst` reads daily; vault-curator's job is
to keep its rows current and add new candidates.

If `vault/ipo-calendar.md` doesn't exist, create it from the structure
the file documents (frontmatter + `## Status legend` + `## Calendar`
table). Otherwise, edit in place with the Edit tool — preserve the
existing rows and table column widths.

**1. Add new IPO candidates from Block B.**
For each IPO Radar candidate (any item where the ticker is `pre-IPO`
or where Block B specifically flagged an upcoming IPO), check whether
a row for the company already exists in the `## Calendar` table. Match
on company name first, then ticker (since pre-IPO tickers may be `TBD`).

If no existing row, append a new row. Populate every field you can
ground in the search results; use `TBD` for fields that aren't pinned
yet. Required fields: Company, Sector, Thesis Fit, Source. Optional but
preferred: Expected Date, Range, Lead UW.

- **Source:** wikilink to this week's suggestions file —
  `[[wiki-YYYY-WW]]`. This lets the user trace the candidate back to
  the search results.
- **Skill Run:** always `none` for new rows. The `pre-ipo` skill flips
  this column when run.

**2. Update existing rows with new information.**
For each existing row, the source precedence for `Expected Date`,
`Range`, `Lead UW`, and similar S-1-derived fields is:

1. **Dossier `_meta.md`** (highest priority) — if a dossier exists at
   `vault/companies/{Ticker_or_slug}/`, read its `expected_ipo_date:` /
   `expected_ipo_date_confidence:` fields and use them. The dossier was
   pulled from the actual S-1, which is more authoritative than any
   search result. If `expected_ipo_date_confidence` is `range-only`,
   leave the calendar's `Expected Date` as `TBD` — don't fake precision.
2. **Block B search results** (fallback) — when no dossier exists yet,
   use search-derived dates / ranges / underwriters from this run.
3. **Existing calendar value** (lowest priority) — keep it if neither
   above source has fresher data.

Apply the same precedence rule for `Range` and `Lead UW` (use dossier
when present, otherwise search results). Do not overwrite a more-specific
value with `TBD` — only revise toward more specificity.

**3. Recompute the `Status` column for every row** based on the
`Expected Date` (or the earliest known date if there's a window):

| Distance from today | Status |
|---|---|
| ≥30 calendar days out, or `TBD` | `30+ days out` |
| 7–29 days out | `this month` |
| 1–6 days out | `this week` |
| 0 days (today) or pricing announced | `priced` |
| Pricing past, within 25 trading days | `trading` (or `quiet-period`) |
| 150–180 calendar days post-IPO | `lockup-soon` |
| Beyond ~210 days post-IPO | `passed` |

For pulled or postponed offerings (verified via search results), set
status to `pulled` and leave the row in place — don't delete history.

**4. Clean up `passed` rows.** Remove rows whose status is `passed`
unless the user added a manual note worth preserving (look for
non-source-link content in the Source column). On removal, log it in
the weekly review output's Watchlist Housekeeping section
("IPO calendar cleanup: removed TICKER (Company) — passed").

**5. Update the `last_updated:` frontmatter field** and the footer
line to today's date if anything changed. If nothing changed, leave
both as-is — silence is the signal.

---

## Constraints

- **Never write to `library/`, `notes/`, or `reports/`.** Output goes
  to `vault/vault-suggestions/` (weekly suggestions file) and
  `vault/ipo-calendar.md` (Step 4b sync only).
- **Suggestions only.** The user reviews everything and decides what to
  promote to `library/`. Frame all suggestions as "worth considering,"
  not as directives.
- **Don't hallucinate sources.** Web radar suggestions must come from
  actual search results. If searches return nothing compelling, say so.
- **Quality over quantity.** Three strong suggestions beat ten weak ones.
  If nothing compelling surfaces, the report should say "nothing standout
  this week" — that's a valid and honest output.
- **Implicit beliefs must be recurring.** Don't flag a one-off note entry
  as an implicit belief. It needs to appear across multiple notes or
  decisions to be worth articulating.
