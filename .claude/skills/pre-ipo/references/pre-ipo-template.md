# Pre-IPO Template

Output path: `vault/reports/pre-ipo/{ROOT}-{EXPECTED-DATE}-{initial|gate}.md`

`{ROOT}` is the proposed ticker if known, otherwise the uppercased
company-name slug (spaces → hyphens). `{EXPECTED-DATE}` is the expected
pricing date in `YYYY-MM-DD`.

---

**Section ordering rule:** Actionable sections first (Snapshot → Verdict
→ Pre-Commit Plan → Trade-Shape Decision Matrix). Reference sections
below the horizontal rule. A re-read should surface the verdict and the
plan without scrolling. Mirrors deep-dive and pre-earnings layouts.

---

```markdown
---
ticker: {{TICKER_OR_TBD}}
company: {{Company Name}}
run_date: {{YYYY-MM-DD}}
expected_date: {{YYYY-MM-DD or TBD}}
mode: {{initial | gate}}
type: pre-ipo
verdict: {{SKIP | WATCH FOR PRICING | SUBSCRIBE IF ELIGIBLE | WATCH FOR OPEN-AND-FLIP | WATCH FOR D30 ENTRY | WATCH FOR LOCKUP DIP | BUILD VIA TRANCHES}}
---

# Pre-IPO: {{Company Name}} ({{TICKER_OR_TBD}}) — {{mode}} run ({{YYYY-MM-DD}})

> Not investment advice.

**Expected pricing:** {{expected_date}} ({{T-N trading days}}) · **Indicated range:** {{$X–Y or TBD}} · **Lead UW:** {{names}} · **Run:** {{run_date}}

---

## Snapshot

| | |
|---|---|
| **Proposed ticker** | {{TICKER}} (or `TBD`) |
| **Company / sector** | {{Company}} · {{sector tag}} |
| **Thesis fit** | {{High / Medium / Low / Not relevant}} — {{one phrase}} |
| **Expected pricing** | {{YYYY-MM-DD}} ({{T-N trading days}}) |
| **Indicated range** | {{$X–Y}} → implied market cap {{$M–N}} at midpoint |
| **Lead UW (tier)** | {{names}} ({{Tier 1 / Tier 2}}) |
| **Cornerstone investors** | {{named anchors, or "None disclosed"}} |
| **Float at IPO** | {{N% of company}} ({{M shares}}) |
| **Lockup expiry** | {{YYYY-MM-DD}} (~180d post-IPO) |
| **Quiet period ends** | {{YYYY-MM-DD}} (~25 TD post-IPO) |
| **Dossier age** | {{N days since last refresh}} |
| **Prior pre-ipo run** | {{[[wikilink to prior file]] or "first run"}} |

---

## Verdict

**{{VERDICT}}**

{{One sentence: why this trade shape over the others.}}

**What would change it:** {{One sentence: the specific signal that would flip
this verdict to SKIP or to a different shape. E.g., "If pricing comes
below indicated range, flip to SKIP — weak demand kills both the flip
and the d30 dip-buy thesis." or "If a Tier-1 cornerstone is confirmed
in the 424A, upgrade to BUILD VIA TRANCHES."}}

---

## Pre-Commit Plan

{{2–5 lines. Concrete conditional orders or watch levels keyed to the
verdict. No hedging.

For `SUBSCRIBE IF ELIGIBLE`:
- **Submit IPO Access request through Robinhood by {{date}}.** Sizing if filled: {{N% of portfolio = $X at $Y midpoint}}. Time-priority placement helps; submit early.
- **If not filled:** fall through to {{next-best verdict — typically WATCH FOR D30 ENTRY at $X or BUILD VIA TRANCHES starting tranche 1 at $Y}}.

For `WATCH FOR OPEN-AND-FLIP`:
- **Pre-market check on opening date {{Y-M-D}}:** read the indicated opening price. Buy {{$X position size}} at first print **only if** opening indication is <{{Z%}} above IPO price (regime check at first tick).
- **Abort condition:** if opening indication is >{{Z%}} over IPO price, do not buy. Flippers will dump into you.
- **Sell:** GTC limit at {{$X target}} or market sell by EOD-{{N}}, whichever fires first.

For `WATCH FOR D30 ENTRY`:
- **Set price alert at $X for ~{{date + 25 TD}}.** Quiet-period dip historically fades the IPO premium.
- **Re-evaluate with fresh deep-dive** once trading starts (T+5 onward). Do not commit a buy level until live trading data exists.
- **Trigger to abort the d30 plan entirely:** if first 5 TD show price >{{Y%}} above IPO price with strong volume — regime is too hot for a dip.

For `WATCH FOR LOCKUP DIP`:
- **Calendar reminder for {{lockup_date - 14d}}** to re-evaluate.
- **Initial expected entry zone: $X–$Y** ({{Z% below estimated post-IPO trading range}}). Refine 30 days before expiry with a fresh deep-dive.

For `BUILD VIA TRANCHES`:
- **Tranche 1: $X (initial position, {{N shares}}).** First entry once trading establishes a price.
- **Tranche 2: $Y (post-quiet-period, {{M shares}}).** Targeted at the day-30 dip if it materializes.
- **Tranche 3: $Z (post-lockup, {{P shares}}).** Targeted at the day-180 lockup-pressure dip.
- **Total target sizing:** {{N% of portfolio at full build}}.

For `SKIP`:
- **No participation.** Remove from active monitoring.
- **Re-trigger condition:** {{the specific signal — e.g., "if a Tier-1 cornerstone is announced before pricing" or "if the comp regime turns hot before d30"}}.
}}

---

## Trade-Shape Decision Matrix

For each non-SKIP shape: does it apply here?

| Trade shape | Applies? | Supporting signal | Disqualifier |
|---|---|---|---|
| **Subscribe if eligible** | {{Yes / No / Maybe}} | {{e.g., "Tier-1 UW, RH IPO Access likely; thesis fit High"}} | {{e.g., "secondary share % is 60% — book is heavy with VC cash-out"}} |
| **Watch for open-and-flip** | {{Yes / No / Maybe}} | {{e.g., "Sector regime hot — last 3 IPOs averaged +45% day 1"}} | {{e.g., "Indicated float is 25% — too large for a meme-style melt-up"}} |
| **Watch for D30 entry** | {{Yes / No / Maybe}} | {{e.g., "Regime supports it; thesis fit High; common pattern in this sector"}} | {{e.g., "Quiet-period overlap with FOMC — too noisy"}} |
| **Watch for lockup dip** | {{Yes / No / Maybe}} | {{e.g., "Heavy VC overhang — 80% locked at IPO; willing to wait"}} | {{e.g., "Founder pre-committed not to sell at lockup"}} |
| **Build via tranches** | {{Yes / No / Maybe}} | {{e.g., "Strong long-term thesis fit; valuation reasonable at midpoint"}} | {{e.g., "Range implies 12x revenue at high end — premium"}} |

**The verdict above is the row marked "Yes" with the cleanest supporting
signal and weakest disqualifier.** If multiple rows are "Yes," the
verdict picks one and the others appear in the Pre-Commit Plan as
fallbacks (e.g., SUBSCRIBE → if not filled → BUILD VIA TRANCHES).

---

## Gate Update *(gate-mode runs only — skip in initial mode)*

**What's moved since initial run ({{initial run date}}):**

- **Final pricing:** {{$X}} ({{above range / at high end / mid / low end / below}}) vs. indicated {{$Y–Z}}
- **Range movement:** {{upsized to $A–B / held / cut to $C–D / unchanged}}
- **Cornerstone investors confirmed:** {{names, or "no new anchors named"}}
- **Sector regime delta:** {{any new IPOs that priced this week and how they traded}}
- **Robinhood IPO Access:** {{eligible / not eligible / unconfirmed}}
- **Relevant news ({{last 7 days}}):** {{1-line each, max 3 bullets}}

**Verdict shift:** {{"Initial said WATCH FOR PRICING; now upgraded to SUBSCRIBE IF ELIGIBLE — priced at high end, anchors confirmed" / "Initial said WATCH FOR OPEN-AND-FLIP; now downgraded to SKIP — priced below range, regime turned cold this week"}}

**Final order:** {{The one-line action being placed today. For SKIP, write "No participation; remove from active watch." For SUBSCRIBE, write "IPO Access request submitted at {{share count}} target." For OPEN-AND-FLIP, write the specific buy-at-first-print conditional.}}

---
---

*Everything below this line is reference / supporting detail. The actionable view is above.*

---
---

## What the company does

{{1 paragraph from the dossier's overview.md, plain English. Cover:
what they sell, who buys it, how they make money, what makes them
different from incumbents. No marketing-speak. No "leveraging AI to
disrupt." Just the actual business.}}

---

## Thesis fit

{{Does the company fit the AI infrastructure / power-constrained / wait-
for-deal lens? Cite library files and watchlist context.

If thesis fit fails: say so explicitly. Often the curator's "Thesis Fit:
High" tag in the calendar was based on a marketing pitch that doesn't
hold up against the S-1's actual revenue mix. Be honest — that often
flips the verdict to SKIP.}}

**Cited library frameworks:** {{[[Wait-for-deal thesis]], [[Broader AI beliefs]], etc.}}

---

## The S-1 essentials

| Metric | Value | As of |
|---|---|---|
| Revenue (last full year) | ${{X}} | {{FY YYYY}} |
| Revenue (most recent stub) | ${{Y}} | {{stub period end date}} |
| Revenue growth (YoY) | {{N}}% | {{period}} |
| Gross margin | {{N}}% | {{period}} |
| GAAP net income / (loss) | ${{X}} / (${{Y}}) | {{period}} |
| Operating cash flow | ${{X}} | {{period}} |
| Cash & equivalents (pre-IPO) | ${{X}} | {{date}} |
| Expected IPO proceeds (net) | ${{X}} | midpoint of range |
| Cash runway (post-IPO, est.) | {{N quarters}} | at current burn |
| Top-10 customer concentration | {{N}}% | {{period}} |
| Use of proceeds | {{breakdown — growth investment / debt paydown / cash to existing holders / GCP}} | per S-1 |
| Dual-class structure | {{Yes (vote ratio X:Y, founder controls Z%) / No}} | per S-1 |

**Read:** {{1–2 sentences synthesizing the financials. Are they growing
fast and unprofitable, growing fast and profitable, slowing and
unprofitable, etc.? What's the one number that matters most for the
verdict?}}

---

## Quality of the offering

**Underwriter tier:** {{Lead bookrunners — Tier 1 (GS / MS / JPM / BofA / Citi / WFC) or Tier 2; co-managers}}

**Cornerstone / anchor investors named:** {{Fidelity / T. Rowe / Tiger / Coatue / Sequoia / etc., per prospectus or roadshow reporting. If none disclosed: say "None disclosed in S-1; watch for confirmation in 424A or roadshow press."}}

**Insider/VC selling at IPO:**
- **Primary shares (new from company):** {{N shares, ${{X}}M raised}}
- **Secondary shares (existing holders cashing out):** {{N shares, {{%}} of offering}}
- **Read:** {{"Heavy secondary at IPO — 60% of the deal is VC cash-out — bearish day-1 signal" / "Pure primary — company-friendly book" / "Mixed — 30% secondary, in line with norms."}}

**Lockup terms:** {{180 days standard; or shorter if hot deal — cite the exact terms from the S-1's underwriting section}}

---

## Comp regime check

Last {{N}} IPOs in {{sector}} over the past 6–12 months:

| Ticker | IPO Date | IPO Price | Day-1 Close | Day-30 Close | Today | Day-1 Pop % | D30 vs IPO % | Today vs IPO % |
|---|---|---|---|---|---|---|---|---|
| {{T}} | {{date}} | ${{p}} | ${{c1}} | ${{c30}} | ${{cnow}} | {{X}}% | {{Y}}% | {{Z}}% |
| {{T}} | ... | ... | ... | ... | ... | ... | ... | ... |

**Regime read:** {{"Hot — average day-1 pop {{N}}%, day-30 still {{M}}% over IPO. Open-and-flip and d30-entry both viable here." / "Cold — last {{N}} IPOs underwater within 30 days. Regime alone is enough to argue SKIP unless thesis fit is strong." / "Mixed — pops then fades; d30 entry is the cleaner play than open-and-flip." / "Insufficient comps — sector is thin on recent IPOs; regime read is qualitative only."}}

---

## Comp valuation

At indicated range midpoint of ${{midpoint}}, implied market cap ${{M}} / EV ${{E}}.

| Comp | Mkt Cap | EV | Revenue | Growth | EV/Rev | P/S | Source |
|---|---|---|---|---|---|---|---|
| {{Peer A}} | ${{}} | ${{}} | ${{}} | {{N}}% | {{X}}x | {{Y}}x | [[deep-dive-file]] |
| {{Peer B}} | ... | ... | ... | ... | ... | ... | ... |
| **{{Subject}} (at IPO midpoint)** | **${{}}** | **${{}}** | **${{}}** | **{{N}}%** | **{{X}}x** | **{{Y}}x** | S-1 + range |

**Read:** {{"Priced at peer multiples — fair." / "Priced at premium ({{X}}x EV/Rev vs. peer median {{Y}}x) — premium needs justifying via growth or margin advantage." / "Discount to peers — but the discount may be deserved if the offering is forced (e.g., needs cash, secondary-heavy)."}}

---

## Lockup & quiet-period calendar

| Date | Event | Why it matters |
|---|---|---|
| {{expected_date}} | Pricing / IPO opens | Day 0 of the post-IPO clock |
| {{expected_date + 1 BD}} | First trading day | The flip window starts here |
| {{expected_date + 25 TD}} | Quiet period ends | Underwriter analysts launch coverage — typical volatility event |
| {{expected_date + 90 calendar days}} | First post-IPO 10-Q | First public earnings; pre-earnings skill becomes the active workflow |
| {{expected_date + 180 calendar days}} | Lockup expires | Insider/VC selling pressure; common dip-buy zone |

---

## Risks & red flags

{{Distilled from risks.md, prioritized by what would flip the verdict.

Tier 1 (verdict-flipping):
- **{{Risk title}}:** {{1–2 sentences}}

Tier 2 (worth tracking, not verdict-flipping):
- **{{Risk title}}:** {{1 sentence}}

Tier 3 (boilerplate):
- {{One-line list, no analysis}}
}}

---

## Council pass — three lenses

**Contrarian** — what's the strongest case this IPO breaks issue or fades after day 1?
{{1 paragraph. Not a hedge. The actual best argument against participation in any form.}}

**Bull** — what's the strongest case it pops and holds?
{{1 paragraph. Not a hedge. The actual best argument for it.}}

**First-Principles** — strip the IPO frame entirely. If this were already public at the indicated price, would it be a buy?
{{1 paragraph. Often the most honest read — it's the deep-dive question with the IPO premium pre-paid.}}

---

## Open questions

{{3–5 specific items that, if answered between now and the gate run, would flip or sharpen the verdict.}}

1. {{e.g., "Will the range be raised, held, or cut after the roadshow?"}}
2. {{e.g., "Will any Tier-1 cornerstones (Fidelity, T. Rowe, Tiger) be confirmed in the 424A?"}}
3. {{e.g., "Will any AI-lab partnership be announced in the pre-IPO window?"}}
4. {{e.g., "How does {{specific peer that's pricing this week}} trade on its day 1?"}}

---

## Appendix: What Not To Use This For

- **Live-price decisions.** Pre-IPO has no live price. Once trading starts,
  `stock-deep-dive` takes over for any further analysis.
- **First earnings print.** When the company files its first post-IPO 10-Q,
  switch to `pre-earnings`. The pre-ipo file's lockup/quiet-period
  framing doesn't carry into normal earnings cadence.
- **Allocation arbitrage.** The skill doesn't price your specific RH IPO
  Access odds. It tells you whether subscribing is the right *shape* if
  you're filled — not whether you'll be filled.

---

## Proposed Watchlist Updates  *(only if verdict is BUILD VIA TRANCHES, WATCH FOR D30 ENTRY, or WATCH FOR LOCKUP DIP)*

> Same format as the `stock-deep-dive` and `pre-earnings` blocks.
> Applied to `vault/watchlist.md`'s `## Planned Tranches` table
> immediately after this file is written via `apply_watchlist_updates.py`
> (Step 5b). The block is the audit trail — the apply script is the
> writer. Pre-IPO does not emit Buy Below / Trim Above (Price Trigger)
> lines — those are deep-dive's authority for established public stocks.
> Tranche expiries are anchored to the expected IPO date.
>
> For `SUBSCRIBE IF ELIGIBLE`, `WATCH FOR OPEN-AND-FLIP`, and `SKIP`,
> write `No changes proposed.` and skip the rest.

### Price Trigger
- **Ticker:** {{TICKER}}
- **Buy Below:** unchanged  *(deep-dive owns long-horizon levels; pre-ipo never overrides — no live price to anchor)*
- **Trim Above:** unchanged
- **Note:** {{short free-text; under ~80 chars; omit to keep existing note}}
- **Confidence:** med
- **Rationale:** No revision — pre-ipo only adds tranches; long-horizon levels are deep-dive's after the IPO trades.

### Planned Tranches
<!-- One line per operation. Formats:
     - Add: TICKER | {Buy|Trim} | {size} | @{price} | expires YYYY-MM-DD | order={GTC|Alert|Conditional GTC} | {note}
     - Remove: TICKER | {Buy|Trim} | @{price} | {reason}
     Expiries anchor to expected_ipo_date — see SKILL.md for shape-by-shape windows.
     If no tranche changes, write: "No tranche changes." and delete these bullets.

     order field for pre-ipo tranches:
     - BUILD VIA TRANCHES: each tranche `Conditional GTC` (gating condition: post-IPO trading establishes price; user converts to GTC manually once trading)
     - WATCH FOR D30 ENTRY: single `Alert` at the post-quiet-period entry price
     - WATCH FOR LOCKUP DIP: `Conditional GTC` at lockup-window entry price

     Reference the trade-shape verdict in the {note}.
-->

- Add: {{TICKER}} | Buy | {{size}} | @{{price}} | expires {{YYYY-MM-DD}} | order={{Conditional GTC|Alert}} | {{note — reference the trade-shape verdict + gating condition}}

---

*Sources: vault/companies/{{ROOT}}/, vault/ipo-calendar.md, vault/notes/, vault/library/, vault/deep-dives/ (sector peers), Exa search results. Generated by `pre-ipo` skill on {{run_date}}.*
```
