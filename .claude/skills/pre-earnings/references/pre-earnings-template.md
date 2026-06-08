# Pre-Earnings Template

Output path: `vault/reports/pre-earnings/[TICKER]-[PRINT-DATE]-{initial|gate}.md`

Dates in the filename are the **earnings print date**, not the run date.

---

**Section ordering rule:** Actionable sections first (Snapshot → Pre-Commit Plan → Scenario Ladder → Rotation Check → Concentration Stress Test). Reference sections below the horizontal rule. A re-read of this file should surface the orders and the decision without scrolling. Mirrors the deep-dive layout (verdict → ladder at top, reference numbers as appendix).

---

```markdown
---
ticker: {{TICKER}}
company: {{Company Name}}
run_date: {{YYYY-MM-DD}}
print_date: {{YYYY-MM-DD}}
mode: {{initial | gate}}
type: pre-earnings
---

# Pre-Earnings: {{TICKER}} — {{Company Name}} — {{mode}} run ({{YYYY-MM-DD}})

> Not investment advice.

**Print:** {{print_date}} (AMC / BMO / unknown) · **T-{{N}} trading days** · **Run:** {{run_date}}

---

## Snapshot

| | |
|---|---|
| **Current position** | {{shares}} shares @ ${{basis}} ({{pct}}% of portfolio, opened {{YYYY-MM-DD}}) |
| **Unrealized P&L** | {{$delta}} ({{pct_delta}}%) |
| **Spot** | ${{spot}} |
| **Implied move** | ±{{implied}}% (${{low}}–${{high}}) · {{rich / fair / cheap}} vs. historical median {{median}}% |
| **Last deep-dive verdict** | {{HOLD/ADD/REDUCE/WATCH}} ({{deep-dive date}}, {{N days old}}) |
| **Blank-slate sizing** (from last deep-dive) | {{Y%}} weight → current is **{{overweight / underweight / correct}}** |
| **Most recent thesis note** | [[{{note filename}}]] ({{date}}) |
| **Stated plan going in** | {{1 sentence from the note on what the user intended to do around this print, or "No explicit pre-print plan on file."}} |

---

## Pre-Commit Plan

{{The point of this skill. Exactly the orders you will place, when, and under what trigger. 2–5 lines. Specific share counts and prices. No hedging.

Synthesize from: Scenario Ladder actions (conditional on the print), Concentration Stress Test (if trimming for tail insurance), and Rotation Check (if redeploying capital to a Tier 1 name). Rotation orders are standing orders — they execute regardless of the print outcome and should appear first.

Example (initial run, no rotation):
- **Hold 150 shares through print** — core position. No action unless scenario below fires.
- **Trim to 100 on close 2026-05-04** if stock is >$48 that day — realize pre-print gains if setup gets frothy.
- **Add 25 on open 2026-05-06** if stock drops <$38 after print on beat-and-raise — overreactions mean-revert.

Example (initial run, with rotation):
- **Standing trim: sell 50 shares by close 2026-04-30** — per Rotation Check, overweight vs. blank-slate; redeploy to NVDA at buy-below $180.
- **Hold remaining 100 shares through print** — core position, appropriately sized post-trim.
- **Add 25 on open 2026-05-06** if drops <$38 on beat-and-raise overreaction.

Example (gate run):
- **Executing trim: sell 50 shares at market today, close.**
- **Standing order for post-print:** buy 25 @ $38 GTC through 2026-05-09.
}}

---

## Scenario Ladder

Five scenarios, each keyed to *your actual share count*. Probability is your best estimate, not a forecast — it's the anchor for the pre-commit plan above.

| Scenario | Prob | Price zone | Move from spot | $ P&L on position | Pre-commit action |
|---|---|---|---|---|---|
| **Blowout + raise** (beat top-line >10%, raise guidance) | {{p}}% | ${{low}}–${{high}} | +{{x}}% | ${{delta}} | {{"Hold core. Trim 25 @ $X if >$X+ on open — take some ATH money off." / "No action — let it run."}} |
| **Beat + inline guide** (solid beat, guidance steady) | {{p}}% | ${{low}}–${{high}} | +{{x}}% | ${{delta}} | {{action}} |
| **Inline** (meets on both, no surprise) | {{p}}% | ${{low}}–${{high}} | ±{{x}}% | ${{delta}} | {{action}} |
| **Soft** (miss one OR weak guide, not both) | {{p}}% | ${{low}}–${{high}} | -{{x}}% | -${{delta}} | {{"Hold — single-quarter wobble doesn't break thesis. Add 25 if <$X — overreaction zone."}} |
| **Miss + cut guide** (thesis-breaker) | {{p}}% | ${{low}}–${{high}} | -{{x}}% | -${{delta}} | {{"Exit on open. Thesis is the business executing — a cut means they don't know their own customers."}} |

**Probability anchor:** {{1 line: what's the market priced for via options? If implied ±Y% = roughly 1 stdev, that means the market is implying roughly symmetric outcomes. State your edge if you think the distribution is skewed.}}

---

## Rotation Check — [[Opportunity-cost lens]]

{{Applies the opportunity-cost lens: the capital at tail risk on this print isn't free — it could be deployed elsewhere. This section doesn't survey the whole watchlist; it names 1–2 specific Tier 1 candidates already active in recent notes and compares.}}

**Blank-slate anchor** (repeated from Snapshot for reasoning context): {{"Blank-slate said X shares / Y% weight → current weight Z% is overweight / underweight / correct" — 1 line. If no deep-dive exists, say "no deep-dive on file; rotation check is qualitative only." If the deep-dive is >30 days old, add: "Deep-dive is {{N}} days old — sizing anchor may not reflect current setup."}}

**Capital at tail risk on this print:** ${{tail_loss}} ({{% of position / % of portfolio}})

**Candidates** (from Tier 1 watchlist, filtered to names appearing in recent notes):

| Ticker | Last deep-dive verdict | Current setup | Own earnings timing | 30d view |
|---|---|---|---|---|
| {{T1-ticker-A}} | {{HOLD/ADD/WATCH + date}} | {{1 line — ladder zone, price vs ladder buy-below}} | {{next earnings date or "no catalyst < 30d"}} | {{1 line reasoning}} |
| {{T1-ticker-B}} | ... | ... | ... | ... |

**Verdict:** {{Exactly one of:

- **Hold full size through print** — "No compelling rotation. [Candidate A] is in trim zone per own deep-dive; [Candidate B] has own earnings in [N] days and similar tail risk. Better to absorb this print."

- **Trim {{N}} shares → rotate to [{{TICKER}}]** — "[Candidate] is in buy-below zone per [[deep-dive-file]], no own earnings catalyst in the 30-day window, verdict was ADD on {{date}}. EV of redeployed capital is higher than EV of same dollars sitting through this print's tail."

- **Trim {{N}} shares → hold cash** — "Position is overweight vs. blank-slate; tail risk asymmetric; no compelling Tier 1 name in buy-below zone right now. Lock in the hedge and wait for the next deep-dive-flagged setup."
}}

---

## Concentration Stress Test

Tail scenario: **Miss + cut** → price zone ${{low}}–{{high}} → position would be worth ${{tail_value}} ({{tail_pct_drawdown}}% from today).

| If I do nothing | If I trim to {{N}} shares today |
|---|---|
| Tail P&L: -${{current_tail_loss}} | Tail P&L: -${{trimmed_tail_loss}} |
| Cost of trimming (if blowout happens): -${{foregone_gain}} | |

{{1–2 sentences. Is the insurance worth the cost? Frame it as expected value across the scenario ladder, not "what if it rips."}}

---

## Gate Update *(gate-mode runs only — skip in initial mode)*

**What's moved since initial run ({{initial run date}}):**

- Consensus EPS: {{$X → $Y}} ({{delta}})
- Analyst revisions (last 7d): ↑{{n}} / ↓{{n}}
- Implied move: {{X% → Y%}}
- Stock price: {{$X → $Y}}
- Insider filings: {{N new, nature}}
- Relevant news: {{1-line each, max 3 bullets}}

**Scenarios that shifted:** {{"Soft scenario probability up from 20% to 30% — three analyst cuts in 48h" / "Nothing moved materially, plan stands."}}

**Final order:** {{The one-line pre-commit action you're placing before close today. If initial said "trim 50 at T-2 if >$48," the gate run either executes or cancels based on whether the condition is live.}}

---
---

*Everything below this line is reference / supporting detail. The actionable view is above.*

---
---

## Consensus & Setup

| Metric | Consensus | YoY | Analyst count |
|---|---|---|---|
| **Revenue (Q)** | ${{rev}} | {{growth}}% | {{n}} |
| **EPS (Q)** | ${{eps}} | {{growth}}% | {{n}} |
| **Revenue (FY)** | ${{rev_fy}} | {{growth_fy}}% | — |

**EPS revisions — last 30 days:** ↑ {{n_up}} · ↓ {{n_down}} → {{direction or "net flat"}}

**Beat/miss trajectory (last {{N}} quarters):**

| Date | Est EPS | Reported | Surprise % | 1-day reaction |
|---|---|---|---|---|
| {{YYYY-MM-DD}} | {{est}} | {{actual}} | {{+/-}}% | {{+/-}}% |
| ... | | | | |

**Pattern:** {{"Beat magnitude decelerating (+710% → +82% → +15%) — Street catching up to earnings power" / "Steady high-single-digit beats, price muted afterward" / "Volatile — reactions not linked to surprise magnitude" / "Too little history — IPO year" — whatever the data actually shows.}}

---

## Business-Specific KPIs to Watch

{{4–6 KPIs that drive THIS stock's reaction, not generic EPS. Pulled from vault/companies/TICKER/financials.md and the most recent thesis note. Each row: name, prior value, what bulls expect, what bears expect, why it matters.}}

| KPI | Prior quarter | Bull case (this Q) | Bear case (this Q) | Why it matters |
|---|---|---|---|---|
| {{e.g., Members}} | {{value}} | {{bull}} | {{bear}} | {{1 line}} |
| {{e.g., Revenue per member}} | ... | ... | ... | ... |
| ... | | | | |

**Guidance update (next Q / FY):** {{What the market expects management to say about forward guidance. Cite prior guidance from vault/companies/TICKER/financials.md.}}

---

## Management Credibility Check

**Prior guidance → actual:**

| Guided | Guidance | Delivered | Result |
|---|---|---|---|
| {{Last call}} | {{what they said}} | {{what they did}} | {{beat / hit / missed}} |
| {{Call before}} | ... | ... | ... |

**Verdict:** {{"Habitual beat-and-raise — they sandbag guidance" / "One-for-two — credibility wobble" / "No guidance given — too early in public life" — the actual read.}}

**Incentive context:** {{1 line: what KPIs exec comp pays on — these will be emphasized on the call. From companies/compensation.md.}}

---

## Implied Move — Detail

| | |
|---|---|
| **Spot** | ${{spot}} |
| **Expiry used** | {{YYYY-MM-DD}} |
| **ATM strike** | ${{strike}} |
| **ATM straddle** | ${{straddle}} |
| **Implied move** | ±{{implied}}% (${{low}}–${{high}}) |
| **Historical \|moves\|** | mean {{mean}}% · median {{median}}% · max {{max}}% (n={{count}} prints) |
| **Richness** | {{rich / fair / cheap}} |

{{1–2 sentences on what the market is pricing vs. what this stock has actually done. If "rich": options market is overpaying for moves → sell-straddle / write-cover flavors get cheap. If "cheap": market is underestimating move → small ATM call/put can work. If insufficient history (IPO year): note that and skip the compare.}}

---

## Insider Behavior Going In

{{From vault/companies/TICKER/insider-activity.md.

- **10b5-1 plans active:** yes/no; when adopted; typical cadence.
- **Recent transactions ({{window}}):** N sales totaling {{shares}} at avg ${{price}}; N buys totaling {{shares}} at avg ${{price}}.
- **Pattern:** "Selling matches 10b5-1 schedule — routine" OR "Deviation from plan — flag."
- **Unusual filings:** any Form 4s outside plan, new 10b5-1 adoptions, 144 filings in the blackout-window approach.
}}

**Read:** {{1 sentence. 10b5-1 sales are not signal; opportunistic sales against the plan are.}}

---

## Questions I Want Answered On The Call

{{3–5 specific questions tied to this quarter's thesis. Not generic ("how's demand?"). Specific ("did member additions re-accelerate after the Q3 slowdown management attributed to sales-force retraining?"). These are what you listen for on the call; if they're dodged, that's signal.}}

1. {{question}}
2. {{question}}
3. {{question}}

---

## Appendix: What Not To Use This For

- **Thesis reset.** If the initial run raised thesis doubts, that's a deep-dive job, not a pre-earnings job. Flag it; don't resolve it here.
- **Longer-horizon allocation.** Scenario ladder is 1-week horizon. If you're thinking 6 months out, this isn't the right tool.
- **Fresh blank-slate sizing.** Pre-earnings *references* the deep-dive's blank-slate output to anchor the rotation check; it does not re-run the analysis. If the deep-dive is stale (>30 days), that's flagged in the Snapshot but not re-computed here.

---

## Proposed Watchlist Updates  *(include only if this ticker is on `vault/watchlist.md` — any tier)*

> Same format as the `stock-deep-dive` block. Applied to
> `vault/watchlist.md` immediately after this file is written via
> `apply_watchlist_updates.py` (Step 5b). The block is the audit trail
> — the apply script is the writer. Omit any subsection you don't want
> changed. For "no changes proposed," write `No changes proposed.` and
> skip the rest.
>
> **Pre-earnings proposals are tactical and short-lived.** Tranche
> expiries should be anchored to the print date (typically `print_date
> + 5 to 10 days`) so post-print contingency orders self-retire if
> unused. Do not revise the long-horizon `Buy Below` / `Trim Above`
> levels unless this print materially changes the thesis — those are
> the deep-dive's authority.

### Price Trigger
- **Ticker:** {{TICKER}}
- **Buy Below:** unchanged  *(deep-dive owns long-horizon levels; override only if this print materially breaks the thesis)*
- **Trim Above:** unchanged  *(same — override only on thesis change)*
- **Note:** {{short free-text; under ~80 chars; omit to keep existing note}}
- **Confidence:** {{low | med | high}}
- **Rationale:** {{For "unchanged," write: "No revision — deep-dive levels still fit; pre-earnings only adds tranches." Override only when the print cracks the thesis.}}

### Planned Tranches
<!-- One line per operation. Formats:
     - Add: TICKER | {Buy|Trim} | {size} | @{price} | expires YYYY-MM-DD | order={GTC|Alert|Conditional GTC} | {note}
     - Remove: TICKER | {Buy|Trim} | @{price} | {reason}
     Expiries should tie to print_date (typically print_date + 5 to 10d).
     If no tranche changes, write: "No tranche changes." and delete these bullets.

     `order` field for pre-earnings tranches — most are `Conditional GTC`
     (place after the print, conditional on the scenario row firing) or
     `Alert` (pre-print contingencies that depend on intraday momentum
     reads). True `GTC` is rare in pre-earnings — it applies only when
     the scenario action is unconditional regardless of print outcome
     (e.g., a standing rotation trim that fires whether print is good
     or bad). Reference the scenario ladder row in the {note}, and for
     `Conditional GTC` rows include the gating condition explicitly
     (e.g., "place GTC after May 5 print on beat-and-raise"). -->

- Add: {{TICKER}} | {{Buy|Trim}} | {{size}} | @{{price}} | expires {{YYYY-MM-DD}} | order={{GTC|Alert|Conditional GTC}} | {{note — reference the scenario ladder row + gating condition for Conditional GTC}}
- Remove: {{TICKER}} | {{Buy|Trim}} | @{{price}} | {{reason}}

---

*Sources: vault/companies/{{TICKER}}/, vault/notes/, vault/deep-dives/ (most recent), yfinance (live data). Scripts: `get_earnings_setup.py`, `get_implied_move.py`. Generated by `pre-earnings` skill on {{run_date}}.*
```
