# Report Template

Output path: `vault/reports/daily/YYYY-MM-DD.md`

The daily report is an alert, not a digest. Two shapes depending on the day.

---

## Busy day (1+ items clear sev ≥3)

```markdown
---
date: {{YYYY-MM-DD}}
type: daily-news-alert
tags:
  - daily-alert
  - news-analysis
---

# Daily Alert — {{Month DD, YYYY}}

<!-- Price Levels Hit — include ONLY when at least one watchlist trigger
     fires (FIRED_BUY/FIRED_TRIM, label=watchlist) OR at least one tranche
     fires (FIRED_TRANCHE_BUY/FIRED_TRANCHE_TRIM). One bullet per fire.
     Trigger + tranche at the same price on the same ticker → ONE merged
     bullet (see Step 1b merge rule).

     Placement: first body section, directly below the H1 and ABOVE the
     News section. These are routine "your level hit" reminders, not
     breaking news — keep them visually separate from the scored news
     items below.

     Omit the section entirely when nothing fires.

## Price Levels Hit

- **{{TICKER}} — ${{price}} hit ({{buy zone | trim zone}}).** {{one short
  sentence in plain English from the Note}}. {{Funded by Y.}} {{⚠ {{preferred
  ticker(s)}} also fired today, preferred first — defer.}} → {{action verb}}
- **{{TICKER}} — ${{price}} tranche hit ({{size}}, {{Buy|Trim}}).** {{one
  short sentence — plain English}}. → execute {{tranche action by Order field}}
- **{{TICKER}} — ${{price}} hit (buy zone).** Trigger + planned tranche
  ({{size}}) both at this level. {{Funded by Y.}} → execute manually after gating check

Action verb forms:
- Trigger-only buy/trim → `→ run deep-dive TICKER`
- Tranche order = GTC → `→ execute tranche: {Action} {Size} at ${at_price}`
- Tranche order = Alert → `→ execute manually after gating check`
- Tranche order = Conditional GTC → `→ execute if gating condition met. Condition: {note}`
-->

<!-- News items section — H2 header included when both Price Levels Hit
     and News items appear. If Price Levels Hit is omitted today and only
     News items render, the `## News` header can be omitted (items go
     directly under the H1, matching the legacy shape).

## News

### {{TICKER}} — {{short headline}}
- **Source:** {{publication}} ({{Month DD}}) — [{{verbatim article title}}]({{URL}})
- **Why it matters:** {{one line, ~25 words max. Cite the specific
  position, thesis, or verdict condition this touches. Link with
  `[[wikilinks]]` where useful. Plain English, not finance jargon.}}
- **Action:** {{`run deep-dive TICKER` | `watch for [condition]` | `none`}}

### 🔥 {{TICKER}} — {{short headline}}
- **Source:** {{publication}} ({{Month DD}}) — [{{verbatim article title}}]({{URL}})
- **Why it matters:** {{…}}
- **Action:** {{…}}

Title rules:
- Sev 3: plain "### TICKER — headline". No severity prefix.
- Sev 4+: prepend a 🔥 emoji ("### 🔥 TICKER — headline").
- Severity is NEVER displayed (no "[sev X]" tag, no "## Flagged"
  header). Severity is internal — used for sorting, threshold
  decisions, and the auto-deep-dive gate, not for display.

Sort items by severity descending, then ticker alphabetic.
If an item meaningfully updates a prior day's coverage, append
"(Update)" to the headline and note what changed in one phrase.
-->

<!-- Auto deep-dive item example (use when Step 4b fires or folds in a recent file).
     The Auto deep-dive line REPLACES the normal Action line — never both.
     Two visual forms — Fresh and Reused — distinguished by language so
     the reader can tell at a glance whether a verdict was just produced
     or recalled from cache.

Freshly fired:

### 🔥 {{TICKER}} — {{short headline}}
- **Source:** {{publication}} ({{Month DD}}) — [{{verbatim article title}}]({{URL}})
- **Why it matters:** {{one line, ~25 words max}}
- **🤖 Fresh deep-dive — run today ([[{{TICKER}}-{{YYYY-MM-DD}}]]):** Verdict **{{HOLD | ADD | REDUCE | WATCH}}**. {{≤2-sentence condensed take, optionally one figure}}

Reused recent file (within staleness threshold — 7d for sev 4+ news, 14d
for trigger-only — not re-run):

### 🔥 {{TICKER}} — {{short headline}}
- **Source:** {{publication}} ({{Month DD}}) — [{{verbatim article title}}]({{URL}})
- **Why it matters:** {{one line, ~25 words max}}
- **Auto deep-dive ([[{{TICKER}}-{{YYYY-MM-DD}}]], {{N}} days old):** Verdict **{{HOLD | ADD | REDUCE | WATCH}}**. {{≤2-sentence condensed take}}
-->

<!-- Broader Price Triggers — include ONLY when at least one row from
     vault/price-triggers.md fires (label=broader). One line per fire.
     Watchlist fires are NOT rendered here — they keep their sev-3 item
     format above. Omit the whole section when nothing fires.

     Buy-side fires ("consider buying") and trim-side fires ("entry zone
     dormant") use DIFFERENT phrasing — the broader file is for tickers
     the user does not hold, so a trim fire isn't a "consider trimming"
     signal, it's a "bear-case ceiling has been undercut, entry zone
     dormant" signal.

     Placement: directly below the flagged items, above Price Trigger
     Housekeeping and Macro awareness.

---

## Broader Price Triggers

- **{{TICKER}}** — price ${{current}} hit buy below ${{threshold}} ({{Note}}) — consider buying. See [[{{TICKER}}-{{YYYY-MM-DD}}]].
- **{{TICKER}}** — price ${{current}} above thesis ceiling ${{threshold}} ({{Note}}) — entry zone dormant. See [[{{TICKER}}-{{YYYY-MM-DD}}]].

If Source is blank in the table, omit the trailing `See [[…]]` clause.
-->

<!-- Price Trigger Housekeeping — include ONLY if at least one of the
     following is non-empty:
       - STALE / ERROR rows from check_price_triggers.py
       - EXPIRED tranche rows (script-flagged; weekly-review will prune)
       - Tranche rows with Expires == today that didn't fire (vault-internal
         maintenance reminder; per Step 4)
       - Planning-note date reminders matching today (per Step 4; usually
         omit — only include if the reader genuinely needs the nudge)
     Omit the whole section when none of the above apply.
     Placement: directly below Broader Price Triggers (grouped with it),
     above Macro awareness.

---

## Price Trigger Housekeeping

- **{{TICKER}}** — stale ({{N}} days since last review). Re-confirm or update in `vault/watchlist.md`.
- **{{TICKER}}** — price fetch failed. Check ticker symbol or network.
- **{{TICKER}}** — tranche {{action}} @ ${{price}} expired (cleanup by weekly-review).
- **{{TICKER}}** — tranche {{action}} @ ${{price}} expires EOD today; did not fire.
- **{{TICKER}}** — planning note [[{{NOTE}}]] flagged today as the re-deep-dive checkpoint; consider running deep-dive.
-->

---

## Macro awareness

{{If a major index or any held ticker moved ≥3% today, lead with a
1-2 sentence diagnosis of the catalyst (not the move). Plain English.
Example: "AI infra sold off ~7% today on a Bloomberg report that
Microsoft is renegotiating its OpenAI compute commitment lower — VRT,
DLR, GEV all down 6-9%." If no big move, omit the lead diagnosis.}}

- {{one-line bullet from broad searches — specific catalyst, no generic platitudes}}
- {{…}}
- {{…}}

<!-- As many bullets as the broad searches warrant. One line each. Plain
     English, not finance-speak. Every bullet must name a specific catalyst
     ("Fed minutes signaled two cuts in 2026" — not "rate environment
     remains uncertain"). If something deserved a severity, it belongs in
     News, not here. -->

<!-- Active Earnings Windows — include ONLY when get_upcoming_earnings.py
     returns at least one row in `upcoming` for a watchlist ticker within
     the next 14 trading days. Sort by trading_days_until ascending.
     Omit the whole section if `upcoming` is empty.
     Placement: directly below Macro awareness.

---

## Active Earnings Windows

- **{{TICKER}}** — print {{YYYY-MM-DD}} (T-{{N}} trading days). Pre-commit plan in [[{{TICKER}}-{{print_date}}-{{initial|gate}}]]. Re-read before acting on news today.
- **{{TICKER}}** — print {{YYYY-MM-DD}} (T-{{N}} trading days). No pre-commit plan on file — consider running pre-earnings.

Use the first form when a pre-earnings file exists; the second when only a
dossier-derived `next_earnings:` date is on file.
-->

<!-- Active IPO Windows — include ONLY when at least one row in
     vault/ipo-calendar.md is within 7 trading days of pricing AND the
     row's status is not `passed` / `pulled`. Sort by trading-day distance
     ascending. Omit the whole section if nothing fires.
     Placement: directly below Active Earnings Windows (or directly below
     Macro awareness if Earnings Windows is omitted today).

---

## Active IPO Windows

- **{{Ticker_or_TBD}} ({{Company}})** — IPO T-{{N}} TD, expected {{YYYY-MM-DD}}. No pre-commit plan on file — consider running `pre-ipo {{Ticker_or_slug}}`.
- **{{Ticker}} ({{Company}})** — IPO T-{{N}} TD, expected {{YYYY-MM-DD}}. Initial plan in [[{{TICKER}}-{{expected_date}}-initial]]. Run `pre-ipo {{Ticker}} gate` before pricing.
- **{{Ticker}} ({{Company}})** — IPO T-{{N}} TD, expected {{YYYY-MM-DD}}. Gate plan in [[{{TICKER}}-{{expected_date}}-gate]]. Re-read before open.
-->

<!-- Verdict Drift — include ONLY when check_verdict_drift.py returns at
     least one row in `drifts` (a deep-dive verdict that has moved ≥10%
     in <60 days). Sort by |drift_pct| descending (the script pre-sorts).
     Omit the whole section if `drifts` is empty.
     Placement: final state section before the disclaimer footer, directly
     below Active IPO Windows (or below whichever of the
     Earnings/IPO/Macro sections is the last one emitted today).

---

## Verdict Drift

- **{{TICKER}}** — was **{{VERDICT}}** at ${{price_at_verdict}} on {{verdict_date}} ({{age_days}}d ago). Now ${{current_price}} ({{drift_pct ± sign}}%). See [[{{deep_dive_file}}]] — re-evaluate.
-->

---

*Not investment advice. Generated by {{agent/model name and version}}*
```

---

## Quiet day (no items clear sev ≥3)

```markdown
---
date: {{YYYY-MM-DD}}
type: daily-news-alert
tags:
  - daily-alert
  - news-analysis
---

# Daily Alert — {{Month DD, YYYY}}

<!-- Include `## Price Levels Hit` here too (directly below H1, above the
     "no severity ≥3 items" line) on quiet days if any watchlist trigger
     or tranche fired. Same one-liner format and merge rule as the
     busy-day template. Omit entirely when nothing fires. -->

No severity ≥3 items today.

<!-- Include `## Broader Price Triggers` here too (above Macro awareness)
     on quiet days if any broader triggers fired. Same one-liner format as
     the busy-day template. Omit entirely when nothing fires. -->

<!-- Include Price Trigger Housekeeping here too (above Macro awareness,
     directly below Broader Price Triggers) if STALE/ERROR/expired-today
     rows exist; omit the section entirely otherwise. -->

## Macro awareness

- {{3–5 one-line bullets from broad searches}}
- {{…}}

<!-- On quiet days, Active Earnings Windows / Active IPO Windows /
     Verdict Drift still go BELOW Macro awareness (same order as the
     busy-day shape) when they have content. Same silence-is-the-signal
     rule per section. -->

---

*Not investment advice. Generated by {{agent/model name and version}}*
```

---

## Rules

1. **No top-of-report disclaimer blockquote.** Do NOT add
   `> Automated research digest, not investment advice.` (or any
   variant) under the H1. The footer line at the bottom is the only
   disclaimer.
2. **No "Flagged" section header.** Items go directly under the H1.
   Do NOT add `## Flagged (severity ≥3)`, `## Items`, or any other
   wrapper heading around the scored items.
3. **Severity is never displayed.** No `[sev X]` prefix in titles, no
   sev tag anywhere in the rendered report. Severity is used only
   internally for sorting, the email threshold, and the auto-deep-dive
   gate. Sev 4+ items get a 🔥 emoji prefix in the title; sev 3 items
   get nothing extra.
4. **Flagged items only.** Severity 1–2 items are dropped entirely — no
   appendix, no background list.
5. **"Why it matters" is one line, ~25 words max.** If the item demands
   more explanation, the action line should say `run deep-dive TICKER` —
   that's where longer analysis lives.
6. **Action is always one of three forms.** Never freeform:
   - `run deep-dive TICKER`
   - `watch for [specific condition]`
   - `none`
7. **Macro awareness is always present.** Even on busy days. One line per
   bullet, as many as the broad searches warrant. No padding, no filler.
8. **Wikilinks.** Use `[[filename]]` when referencing vault files
   (thesis notes, deep-dives, library entries).
9. **Sort.** Severity descending, then ticker alphabetic.
10. **Sources.** Format: `Reuters (Apr 17) — [Verbatim Article Title](URL)`. Always include the exact title and URL as returned by Exa.
11. **Only write to `reports/daily/`.** Never touch `notes/` or `library/`.
12. **No persona/conviction sections in the daily report** — those live in
    the weekly review and deep dive.
13. **No off-watchlist idea generation.** That's `vault-curator`'s job.
14. **No wait-for-deal lens.** That's `weekly-review` and `vault-curator`.
15. **Price triggers — two sources, two behaviors.**
    - `label: watchlist` fires (from `vault/watchlist.md` — both
      `## Price Triggers` and `## Planned Tranches` rows) → one-line
      bullet in the `## Price Levels Hit` section at the very top of the
      report (directly below H1, above News). Trigger + tranche at the
      same price on the same ticker collapse to one bullet (see Step 1b
      merge rule). NOT a sev-3 item. NOT a `### TICKER — …` header.
    - `label: broader` fires (from `vault/price-triggers.md`) → one-line
      bullet in a `## Broader Price Triggers` section placed below News
      and above `## Macro awareness`. No sev-3 item, no auto-deep-dive,
      no merge with news. Omit the section entirely if nothing fires.
    - `STALE` / `ERROR` rows from either source go in
      **Price Trigger Housekeeping** directly below Broader Price Triggers
      and above `## Macro awareness`; omit if none.
16. **Section order.** Price Levels Hit → News (scored items) → Broader
    Price Triggers → Price Trigger Housekeeping → Macro awareness →
    Active Earnings Windows → Active IPO Windows → Verdict Drift →
    disclaimer footer. Each state section is independently silence-is-the-
    signal: omit if empty. Macro awareness is the only section that is
    always present.
18. **Language style — plain English, not finance-speak.** This report
    is read on a phone over coffee, not by a sell-side analyst.
    - Short sentences. Active voice.
    - No jargon when a plain word works: "sold off" not "exhibited
      downside pressure"; "buy zone" not "accumulation tranche"; "the
      Fed minutes" not "the FOMC communication". A reader who doesn't
      live in finance Twitter should follow every line.
    - Specific over abstract: "down 7% on a Bloomberg report that MSFT
      is renegotiating compute commitments" beats "weakness on capex
      concerns". The job of the alert is to name the catalyst.
    - "Why it matters" is one line, ~25 words. If you need more, the
      action is `run deep-dive TICKER`, not more sentences here.
17. **Auto deep-dive line.** When Step 4b fires or folds in a recent file,
    the item uses a deep-dive line in place of `Action` — never both. Two
    visual forms, intentionally distinct so the reader can tell at a glance
    whether the verdict was just produced or recalled from cache:
    - **Fresh fire (just run today):**
      `**🤖 Fresh deep-dive — run today ([[TICKER-YYYY-MM-DD]]):** Verdict **{V}**. {{take}}`
    - **Reused file (within staleness threshold — 7d for sev 4+ news, 14d for trigger-only):**
      `**Auto deep-dive ([[TICKER-YYYY-MM-DD]], {{N}} days old):** Verdict **{V}**. {{take}}`
    Never collapse the two into a shared "Auto deep-dive" prefix — the
    `Fresh deep-dive — run today` language is the explicit signal that
    this verdict was produced as part of this alert.
