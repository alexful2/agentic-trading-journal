# Weekly Review Template

Output path: `vault/reports/weekly/YYYY-WW.md`

---

```markdown
---
date: {{YYYY-MM-DD}}
week: {{YYYY-WW}}
type: weekly-macro-review
reports_read: {{count}}
deep_dives_read: {{count}}
searches_run: {{count}}
---

# Weekly Macro Review — Week of {{Month DD, YYYY}}

## Dominant Themes

- **{{Theme 1}}** — {{current state, one line. Confirms / complicates
  the AI infrastructure thesis? Be specific: name the actual force.}}
- **{{Theme 2}}** — {{…}}
- **{{Theme 3}}** — {{…}}

<!-- 2–3 bullets. Name the force, not a category. "Data center power
     constraints tightening as utilities push back on new load" beats
     "energy is a factor." -->

---

## Thesis Pressure Test

<!-- Test the week's dominant themes against your core long-term thesis.
     One bullet per lens where there's signal this week. Skip silent lenses. -->

- **Compute scaling:** {{…}}
- **Energy buildout:** {{…}}
- **Government / geopolitics:** {{…}}
- **Demand / adoption:** {{…}}

**Overall:** {{One sentence. Did this week confirm, challenge, or
complicate the core thesis? "Confirms" is not the default.
"Nothing this week materially moves the thesis" is a valid result.}}

---

## Wait-for-Deal Watch

<!-- 0–3 small-to-mid AI infrastructure names approaching wait-for-deal
     territory. Synthesized from this week's reports + broad searches
     only — no extra searches. If nothing compelling, say so and move on. -->

### {{Company Name}} ({{TICKER or "pre-IPO"}})
- **What they do:** {{one line}}
- **Why they fit:** {{one line — which lane, what signals they're right
  before a deal}}
- **Status signal:** {{e.g., "rumored Anthropic talks", "quiet but
  buildout on schedule"}}

<!-- If nothing: "Nothing compelling this week." -->

---

## What Shifted vs. Last Week

{{1–2 sentences comparing against the prior weekly-review file. If the
picture is largely unchanged, say that — useful signal too. If this is
the first weekly-review (no prior file), write:
"No prior weekly-review to compare against — this is the baseline."}}

---

## Deep Dive Anchors

{{If any deep dive was run this week, note whether this week's macro
confirms or complicates its verdict. Reference by wikilink:
[[TICKER-YYYY-MM-DD]]. If no deep dives this week:
"No deep dives this week."}}

---

## Verdict Distribution Check

<!-- Output of Step 3c. Skip table + read entirely if N < 3, write
     "Insufficient sample (N=X) — skipping." instead. -->

This week: {{N deep-dives, M pre-earnings reports}}.

| Ticker | Type | Verdict | Pattern flag |
|--------|------|---------|--------------|
| {{NVDA}} | deep-dive | {{WATCH}} | {{Extended Run}} |
| {{DLR}}  | deep-dive | {{ADD}}   | {{Dip Buyer}}    |
| {{VRT}}  | pre-earnings | {{HOLD}} | {{—}}          |

**Skew:** {{X WATCH/REDUCE, Y ADD/HOLD}}. **Extended-Run share among
deep-dives:** {{Z/N}}.

**Read:** {{One of the four templates from Step 3c. If selection bias
is the call, end with a candidates list — watchlist Tier 2/3 names with
no deep-dive in 30+ days that are worth queueing for next week:
"Candidates worth deep-diving instead: TICKER, TICKER, TICKER."}}

---

## Watchlist Housekeeping

<!-- Output of Step 3b. Promotion of new triggers/tranches happens at
     write-time inside deep-dive / pre-earnings / pre-ipo (each runs
     apply_watchlist_updates.py). This section records pruning only.
     If nothing was pruned, write "No housekeeping needed this week."
     and skip the subsections. -->

**Expired tranches removed:**
- {{TICKER — Buy 15% of pos @$40, expired YYYY-MM-DD}}
- {{…}}

**Stale price-trigger rows removed (`vault/price-triggers.md`, >60 days):**
- {{TICKER (last reviewed YYYY-MM-DD)}}
- {{…}}

**Apply-script backstop (only if you suspect a missed mid-week run):**
- {{[[TICKER-YYYY-MM-DD]] — re-applied; no-op}}
- {{…}}

---

*Generated: {{timestamp}}*
```

## Rules

1. **Wikilinks.** Use `[[filename]]` when referencing vault files (deep
   dives, library entries, prior weekly-reviews).
2. **Sources required.** Every claim in Dominant Themes, Thesis Pressure
   Test, or Wait-for-Deal Watch must trace to a search result or a
   recent daily alert / deep dive.
3. **Honest null state.** If the week was quiet, say so. A short honest
   review beats a padded one.
4. **Brevity.** Under ~500 words total. The user reads this weekly and
   the Friday email quotes from it — keep it tight.
5. **No persona cosplay.** The pressure test is an analytical framework,
   not a voice. Don't write "a guru would say…" — write what the lens
   reveals.
