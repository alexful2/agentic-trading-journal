# Deep Dive Template

Output path: `vault/deep-dives/[TICKER]-YYYY-MM-DD.md`

---

```markdown
---
date: {{YYYY-MM-DD}}
ticker: {{TICKER}}
company: {{Company Name}}
type: deep-dive
verdict: {{HOLD | ADD | REDUCE | WATCH}}
---

# Deep Dive: {{TICKER}} — {{Company Name}} — {{Month DD, YYYY}}

> Not investment advice.

---

## Snapshot

| | |
|---|---|
| **Price** | ${{current}} |
| **52-week range** | ${{low}} – ${{high}} |
| **Analyst avg target** | ${{avg_target}} ({{upside}}% upside) |
| **Consensus** | {{Buy/Hold/Sell}} — {{buy_count}} Buy / {{hold_count}} Hold / {{sell_count}} Sell |
| **Next earnings** | {{date or "Unknown"}} |
| **Market cap** | ${{market_cap}} |

---

## Verdict: {{HOLD | ADD | REDUCE | WATCH}}

{{3-5 sentences. Clear reasoning, no "it depends." Written last, placed first — this is what the user reads on a re-open. Reference where advisors agree or clash (Council is below). If Blank-Slate conflicts with Portfolio & Timing sizing, resolve that conflict here. If WATCH: the Trigger line below must be specific.}}

**Trigger:** {{Specific price level or catalyst. Required for WATCH. Example: "Buy below $130 on earnings-miss pullback" or "Hold through May 5 earnings; revisit above $50."}}

> Price ladder and crux events follow. If this ticker is on `vault/watchlist.md`, the Proposed Watchlist Updates section at the bottom of this file is what `apply_watchlist_updates.py` reads (Step 8d) to write revised levels directly into the `## Price Triggers` and `## Planned Tranches` tables.

---

## Crux Events & Price Ladder

*Price ladder* — each level must cite at least one reference number from *Reference levels* below (fair-value band, ATR distance from current price, DMA, swing low, or analyst target). Not vague.
- **Buy below $X** — {{rationale, including which reference anchors this level — e.g., "top of P/S bear band ($15.06), –1.4 ATR from current, just above most recent swing low ($13.91)"}}
- **Hold $X–$Y** — {{rationale}}
- **Trim above $Y** — {{rationale}}

> If a ladder level sits outside every reference band (e.g., Buy Below far below the bear fair-value band), call that out in one sentence — either the thesis requires multiple expansion the reference numbers don't capture, or the level is too aggressive. Don't smooth it over.

*Upcoming crux events (next ~60 days):* For each event, date + positive-outcome price impact + negative-outcome price impact. Example:
"Sweetwater energization (any day): confirmed → $55–65; delay past Q2 → $35–40."

If no significant crux event within 60 days, state "No near-term crux event" and skip the EV math.

*Pre-event EV math* (only if a crux event is within 30 days): Compare buying now vs. waiting for resolution with arithmetic, not vibes. Example: "$48 → $77 median = +60% with the bear tail live; $55 → $77 median = +40% with execution confirmed and bear tail eliminated. Paying up for derisking is better risk-adjusted." Name the answer directly: buy now, wait, or doesn't matter. Call out the common trap: it's rarely a binary "buy now vs chase later" — there's usually a third option (pre-earnings window, macro dip, different catalyst).

*Reference levels* — the numbers the ladder above cites (from `get_stock_fundamentals.py` + `get_historical_patterns.py`). Appendix-style — the ladder and crux events above are the actionable view; this block exists so each level's anchor is verifiable.

**Fair-value bands** *(primary method: {{forward_pe | price_to_sales}})*:
- **{{primary method label}}:** bear ${{bear}} · base ${{base}} · bull ${{bull}}
- **{{secondary method label, if both emitted}}:** bear ${{bear}} · base ${{base}} · bull ${{bull}}
- *(Or: "N/A — {{reason from script note}}")*

**Volatility & technicals:**

| | |
|---|---|
| ATR(20) | ${{atr}} ({{atr_pct}}% of price) |
| 50 DMA | ${{sma_50}} (stock {{sma_50_rel_pct}}% {{above|below}}) |
| 200 DMA | ${{sma_200}} (stock {{sma_200_rel_pct}}% {{above|below}}) |
| Swing lows | ${{s1}} ({{d1}}) · ${{s2}} ({{d2}}) · ${{s3}} ({{d3}}) |

**Analyst target range:** low ${{low}} · avg ${{avg}} · high ${{high}} *(already in Snapshot — restated here for ladder reference)*

---

## Thesis Check

**Original thesis** (from [[{{note-filename}}]]):
{{1-2 sentence summary of the buy thesis extracted from the vault note.}}

**Current state:**
{{Intact / Partially intact / Broken}}

{{2-4 sentences. Cite specific metrics from the fundamentals below that confirm
or challenge the thesis. Be direct — if the thesis is weakening, say so and why.}}

---

## Your Portfolio & Timing

**vs. Current Holdings**
{{Direct comparison to other positions. If the user is implicitly considering a
pivot (e.g., selling DLR to fund more NVDA), address it by name and give a
verdict. Note whether this add is additive or duplicative to existing exposure.}}

**Timing**
{{Is now a good entry? Reason from: proximity to 52-week high/low, earnings
proximity (pre/post binary event risk), recent market rally streak (mean-reversion
risk), and whether the stock has already moved significantly on the thesis.
If waiting is smarter, name the specific price level or condition — not vague
language. If pre-earnings: be explicit about the bet you're actually making.}}

**Historical Patterns** *(from get_historical_patterns.py)*
{{State which preset(s) currently apply. Cite the actual numbers — win rate,
avg return, worst drawdown — for whichever preset matches today's setup.
Example: "NVDA is currently in the dip buyer zone (28% below 52w high). In
7 prior instances matching this condition, 30-day win rate was 71%, avg
return +6.2%, with an average max drawdown of –4.1% before recovery."
If a preset had insufficient history, say so explicitly. If no preset
applies to today's setup, state that and note what the current readings are.}}

**Sizing**
{{What's the right position size given portfolio composition? All-in / partial
add / already sized correctly? Push back if concentration is wrong for the
timing or risk level.}}

---

## Implied Expectations  *(thesis math — verifies the verdict above; never overrides it)*

> States what today's price *requires you to believe*, as an equation with sourced
> numbers, then the threshold that would prove it wrong. The output is a falsifiable
> assumption set, **not** a price target. Every variable traces to a script (Step
> 2/2b) or a filing/transcript (Step 2d); no invented inputs, and no invented
> probabilities ([[C8 - Kelly Criterion and Position Sizing]]).
>
> If the thesis names no falsifiable, quantifiable constraint at today's price,
> write `No binding implied-expectation constraint at ${{price}} — verdict rests
> on {{qualitative driver}}.` and skip the rest of this section. Don't manufacture
> an equation to fill space.

**Model:** {{one plain-English equation, archetype-appropriate, units on every term:
- *Multiple / backlog name:* `equity value ≈ contracted backlog × op-income conversion(%) × exit multiple − net financing need − net debt`; quick form: price-to-backlog = market cap ÷ contracted backlog.
- *Cash-flow name:* reverse-DCF — the revenue CAGR / terminal margin that today's price implies.
- *Unit-economics infra:* `value ≈ Σ(contracted MW × $/MW/yr × steady-state margin) discounted − net debt`.}}

**Variables:**

| Variable | Today's value | Source | Verdict flips if → |
|---|---|---|---|
| {{var}} | {{value}} | {{script / filing / transcript}} | {{threshold that changes ADD/HOLD/REDUCE}} |

**What has to be true:** {{the break-even line — solve for the implied growth / conversion rate / multiple that makes today's price fair, then one-line judgment: plausible or heroic? State a break-even **threshold** or required assumption — NOT a typed-in probability ("probability" is reserved for the Monte Carlo output below). Example: "at 0.55× backlog and 8.8× P/S, $100 already requires the H2 op-income ramp to print roughly on guide — little margin of safety; that's the unproven Q2 binary, not a given."}}

**Monte Carlo** *(if the equation is cleanly quantifiable — `monte_carlo_valuation.py`, seed 42; omit this line otherwise)*: break-even probability {{X%}} across {{N}} draws · implied price p25–p75 {{$lo–$hi}} · crux variable **{{var}}** (|r| {{0.xx}}). {{one line on what the spread says about margin of safety — report the break-even probability, not the p50 as a fair value.}}

**Crux variable:** {{the single input the verdict is most sensitive to — the one to watch; should match the Monte Carlo crux above when the simulation was run.}}

**Falsification thresholds:** {{1-3 numbers/dates/events that break the equation. These feed Step 8e and should match the rows written to `vault/tripwires.md`.}}

**Math check:** {{Corroborates | In tension with}} the {{HOLD/ADD/REDUCE/WATCH}} verdict. {{If "In tension," one sentence on why — surfaced, not smoothed.}}

---

## Fundamentals

| Metric | Value | Context |
|--------|-------|---------|
| P/E (TTM) | {{pe}} | {{vs sector or historical avg}} |
| EV/EBITDA | {{ev_ebitda}} | |
| Price/Sales | {{ps}} | |
| Revenue growth (YoY) | {{rev_growth}}% | |
| Gross margin | {{gross_margin}}% | |
| Return on Equity | {{roe}}% | |
| Debt/Equity | {{de}} | |

**EPS surprise trend (last 4 quarters):**
{{Q1: actual vs estimate, Q2: ..., Q3: ..., Q4: ...}}
<!-- Pattern: consistently beating / missing / mixed -->

**Forward estimates:**
{{Next quarter EPS estimate: $X. Next year revenue estimate: $X.}}

---

## Blank-Slate Reframe

**Starting from zero** — no existing position, just cash and the same vault context:

- **Would you buy {{TICKER}} today?** {{Yes / No}}
- **Blank-slate allocation:** {{X% of portfolio, or $X if portfolio size known}}
- **Anchor:** {{The price level the blank-slate sizing assumes is fair entry, with source — e.g., "fair at current $42; Buy Below $38 (P/S bear band, this deep dive Step 2)". If you reach for a target from a note older than ~30 days, re-derive from this run's numbers instead.}}
- **Current allocation:** {{Y% of portfolio, or $Y from the trade log; "unknown" if not tracked}}
- **P&L since entry:** {{Winning +X% / Losing −X% / Flat / New entry — from trade-log unrealized}}
- **Gap source:** {{Appreciation / Depreciation / Thesis revision / Both / N/A — what drove the blank-slate-vs-current delta}}
- **Bucket (raw):** {{Underweight / Overweight / Exit candidate / Correctly sized}}
- **P&L-adjusted action:** {{HOLD / ADD / REDUCE — partial / REDUCE — full exit. Apply the Step 4b override matrix. If raw bucket and adjusted action differ, name the override in one phrase, e.g., "Overweight → HOLD (let winner ride, thesis intact)" or "Exit candidate → HOLD (price-only gap, thesis intact)".}}

{{If the P&L-adjusted action *agrees* with the Portfolio & Timing sizing conclusion: one sentence confirming. No further prose.

If it *conflicts* with Portfolio & Timing: 2-3 sentences naming the conflict directly. The Verdict at the top of this file reflects the resolution — do not re-litigate it here.}}

---

## Founder Signal  *(omit this section entirely if no company dossier exists for this ticker)*

> Only include when `vault/companies/{{TICKER}}/leadership.md` exists.
> If absent, do not mention the founder anywhere in the report.

From `vault/companies/{{TICKER}}/leadership.md` *(dossier last refreshed {{meta_refresh_date}})*:

- **Net signal:** {{Positive / Neutral / Negative / Mixed — derive from the leadership.md "alignment signals" section}}
- **Takeaway:** {{1-2 sentences synthesizing founder background + recent insider activity into a directional read}}

{{1-2 sentences on how the founder signal affects the current decision at today's
price. Does it reinforce the thesis, pressure it, or not matter here? If the
profile's signal and the fundamentals disagree, the Verdict at top should reflect
that conflict — note it here briefly, don't re-litigate.}}

---

## Calls Consideration  *(omit this section entirely if conditions_met: false)*

> Only include when get_options_analysis.py returns conditions_met: true.
> If absent, do not mention options or calls anywhere in the report.

**Entry pattern:** {{pattern_name}} — {{pattern_win_rate_pct}}% win rate across {{pattern_instances}} historical instances, avg +{{pattern_avg_return_pct}}% ({{pattern_horizon}} / ~{{pattern_horizon_calendar_days}} calendar days)
**Active today:** {{Yes / No}}

| | |
|---|---|
| **Strike** | ${{strike}} ({{actual_otm_pct}}% OTM) |
| **Expiry** | {{expiry}} ({{expiry_days}} days / {{expiry_buffer_ratio}}x pattern duration buffer) |
| **Premium** | ${{premium}} → breakeven ${{breakeven_price}} (+{{breakeven_pct}}%) |
| **Pattern avg target** | ${{implied_target_price}} (+{{pattern_avg_return_pct}}%) |
| **Return if avg hits** | ~{{option_return_at_avg_pct}}% on option vs +{{pattern_avg_return_pct}}% on shares |
| **Leverage** | {{leverage_ratio}}x |
| **Delta** | {{delta or "N/A"}} |
| **IV ratio (ATM/realized)** | {{iv_ratio}} — {{iv_label}} |

**Risk:** Max loss = 100% of premium (${{premium}}/share). Compare: avg shares drawdown {{pattern_avg_drawdown_pct}}%, worst {{pattern_worst_drawdown_pct}}%.

**Sizing:** Max 1–2% of portfolio given 100% total-loss risk. This is a small, defined-risk bet — not a replacement for the shares position.

{{2-3 sentences. Synthesize: does the conviction level in this deep dive match the level needed to accept a total-loss outcome on a small position? Is the pattern active today, or does this depend on the pattern activating? Name any specific risk (e.g., earnings IV crush, extended run making options more expensive than usual). Direct call — yes or no on the calls idea.}}

---

## Conviction Check

{{2-4 sentences grounded in actual price and valuation data.
Pressure-test against the strongest version of your own long-term thesis:
would a high-conviction holder of that thesis buy at current prices, or
wait for a dip? Separate "good company" from "good entry."
If waiting: name the level. If rotating: name the alternative.
Don't riff generically — tie to specific numbers.}}

---

## The Council

### Contrarian
{{150-200 words. Bear case. What assumptions are most vulnerable?
What would have to be true for this to fail? No hedging.}}

### Bull
{{150-200 words. Upside case. What is the market underpricing?
What does this look like if things go better than expected? No hedging.}}

### First-Principles
{{150-200 words. Ignore price action. What does this company actually do,
who pays them, and is there a durable structural reason for that to continue?
Does the valuation make sense from the ground up? No hedging.}}

---

## Proposed Watchlist Updates  *(include only if this ticker is on `vault/watchlist.md` — any tier)*

> Applied to `vault/watchlist.md` immediately after this file is written
> via `apply_watchlist_updates.py` (Step 8d). The block is the audit trail
> — the apply script is the writer. Omit any subsection you don't want
> changed. For "no changes proposed," write `No changes proposed.` under
> the subsection and skip the other subsections.

### Price Trigger
- **Ticker:** {{TICKER}}
- **Buy Below:** {{price | "unchanged" | "—" to clear}}
- **Trim Above:** {{price | "unchanged" | "—" to clear}}
- **Funded-by:** {{short free-text capital source — e.g., "DLR trim tranche 1", "cash", "post-May-5 rotation"; "unchanged" or omit to keep existing; "—" to clear. Applies to the Buy side only; leave blank on trim-only rows.}}
- **Prefer-over:** {{comma-separated tickers this one should be funded before if both fire the same day — e.g., "DLR, VRT"; "unchanged" or omit to keep existing; "—" to clear. Applies to the Buy side only. All listed tickers must live in the same source file as this row — collision detection is single-file per invocation (see `check_price_triggers.py` docstring). Watchlist.md entries must name other watchlist tickers; price-triggers.md entries must name other price-trigger tickers.}}
- **Note:** {{short free-text; under ~80 chars; omit to keep existing note}}
- **Confidence:** {{low | med | high}}
- **Rationale:** {{1 sentence — what from this deep dive drove the change}}

### Planned Tranches
<!-- One line per operation. Formats:
     - Add: TICKER | {Buy|Trim} | {size} | @{price} | expires YYYY-MM-DD | order={GTC|Alert|Conditional GTC} | {note}
     - Remove: TICKER | {Buy|Trim} | @{price} | {reason}
     If no tranche changes, write: "No tranche changes." and delete these bullets.

     `order` field — choose based on whether the level needs a human at the moment of fire:
       - GTC: place limit order now, leave standing. Use for unconditional trims past thesis target, or buys past a thesis-confirmed level. No gate.
       - Alert: no order, just notify. Use for pre-binary tranches, cohort-gated buys, opportunity-cost-ranked rows (anything in the same-day collision detection logic).
       - Conditional GTC: place GTC only after a named condition resolves (post-print, post-Sweetwater, etc). Until then, behaves as Alert. The condition belongs in the {note} column. -->

- Add: {{TICKER}} | {{Buy|Trim}} | {{size}} | @{{price}} | expires {{YYYY-MM-DD}} | order={{GTC|Alert|Conditional GTC}} | {{note}}
- Remove: {{TICKER}} | {{Buy|Trim}} | @{{price}} | {{reason}}

---

*Generated: {{timestamp}}*
```

## Rules

1. **No hallucinated numbers.** Every figure in Snapshot and Fundamentals must
   come from FMP script output. If a data point is unavailable, write "N/A".
2. **Verdict is mandatory.** One of: HOLD, ADD, REDUCE, WATCH. No waffling.
   Placed at the top of the file (not the bottom) so re-reads are fast.
3. **WATCH requires a trigger.** If verdict is WATCH, the Trigger line must
   specify exactly what condition would move it to ADD or REDUCE.
4. **No duplicate verdicts.** The verdict appears once, at the top. The
   Portfolio & Timing section does not end with a "Bottom line" restatement —
   the Verdict at top already covers that.
5. **Council advisors don't hedge.** Each represents one angle fully.
   Balance comes from having all three, not from any single advisor.
6. **Wikilinks.** Use `[[filename]]` when referencing vault notes.
7. **Implied Expectations is a verifier, not a forecast.** It states what price
   *requires* and what would break it — never a fair-value price target, never an
   invented probability, never an additive "quality score." If there's no
   falsifiable constraint at today's price, write the one-line "no binding
   constraint" note and stop. A `Math check: In tension` is surfaced, not smoothed.

---

# Comparison Template

Output path: `vault/deep-dives/[TICKER_A]-vs-[TICKER_B]-YYYY-MM-DD.md`

---

```markdown
---
date: {{YYYY-MM-DD}}
tickers: [{{TICKER_A}}, {{TICKER_B}}]
type: comparison
verdict: {{ALL TICKER_A | ALL TICKER_B | SPLIT X%/Y% | WAIT}}
capital: {{amount stated by user, or "unspecified"}}
---

# Comparison: {{TICKER_A}} vs {{TICKER_B}} — {{Month DD, YYYY}}

> Not investment advice.
> Individual deep dives: [[{{TICKER_A}}-{{YYYY-MM-DD}}]] · [[{{TICKER_B}}-{{YYYY-MM-DD}}]]

---

## Head-to-Head Snapshot

| | {{TICKER_A}} | {{TICKER_B}} |
|---|---|---|
| **Price** | ${{price_a}} | ${{price_b}} |
| **% off 52w high** | {{pct_a}}% | {{pct_b}}% |
| **Valuation** | {{P/E or EV/Rev}}: {{val_a}} | {{P/E or EV/Rev}}: {{val_b}} |
| **Analyst avg target** | ${{target_a}} ({{upside_a}}% upside) | ${{target_b}} ({{upside_b}}% upside) |
| **Consensus** | {{Buy/Hold/Sell}} | {{Buy/Hold/Sell}} |
| **Next earnings** | {{date_a}} | {{date_b}} |
| **Active entry pattern** | {{pattern_a or "None"}} — {{win_rate_a}}% win rate | {{pattern_b or "None"}} — {{win_rate_b}}% win rate |

---

## Allocation Verdict: {{ALL TICKER_A | ALL TICKER_B | SPLIT X%/Y% | WAIT}}

{{3-5 sentences. Written last, placed first — the re-read target. Name the winner and the deciding factor. Address the loser: is it worth revisiting, and at what price or condition? If SPLIT: name the specific percentages and explain why concentration into one isn't clearly right — don't use a split as a hedge. If WAIT: give a specific price level or catalyst for each stock in the Triggers below.}}

**Triggers:**
- **{{TICKER_A}}:** {{specific price or catalyst}}
- **{{TICKER_B}}:** {{specific price or catalyst}}

---

## Thesis Alignment

**{{TICKER_A}}:** {{Intact / Partially intact / Broken}} — {{1-2 sentences on current state}}

**{{TICKER_B}}:** {{Intact / Partially intact / Broken}} — {{1-2 sentences on current state}}

**Which thesis is stronger right now:**
{{Direct answer. Name the winner and cite the specific metric(s) that make it so.
If they're genuinely equal, say that and explain why.}}

---

## Valuation & Value

{{Which is cheaper relative to its growth rate? Use forward P/E, EV/Revenue,
or a PEG-style ratio if the numbers support it. 2-3 sentences max. Cite numbers.
If both are pre-profit or the valuation frameworks are incompatible, note that.}}

---

## Entry Setup

{{Which historical pattern is active for each? State the win rates side by side.
A dip-buyer setup vs. an extended-run setup have very different risk profiles.
If neither has an active pattern, say so and note what the current readings are.
2-3 sentences.}}

---

## Risk Asymmetry

{{What's the realistic downside for each? Consider: beta, earnings proximity,
thesis invalidation risk, sector/macro exposure. Which has more bounded downside?
2-3 sentences.}}

---

## Allocation Logic

{{Given the capital amount and current portfolio context, what's the case for
concentrating vs. splitting? Is there a genuine diversification argument, or
is one stock clearly the better use of capital? 2-3 sentences. Be direct.}}

---

## Blank-Slate Allocation

**Starting from zero** — no positions in either ticker, just ${{capital}} cash and the same vault context:

| | {{TICKER_A}} | {{TICKER_B}} | Cash |
|---|---|---|---|
| **Blank-slate allocation** | {{X%}} | {{Y%}} | {{Z%}} |
| **Anchor** | {{fair-entry price + source from this run}} | {{...}} | — |
| **Current allocation** | {{current_a or "unknown"}} | {{current_b or "unknown"}} | — |
| **P&L since entry** | {{+/−X% or "new"}} | {{+/−Y% or "new"}} | — |
| **Gap source** | {{Appreciation / Depreciation / Thesis revision / Both / N/A}} | {{...}} | — |
| **P&L-adjusted action** | {{HOLD / ADD / REDUCE — partial / REDUCE — full exit}} | {{...}} | — |

{{If the P&L-adjusted action per ticker *agrees* with Allocation Logic above: one sentence confirming. No further prose.

If it *conflicts*: 2-3 sentences naming the conflict. The Allocation Verdict at the top reflects the resolution — do not re-litigate here.}}

---

## Founder Signal  *(omit this section entirely if neither ticker has a company dossier)*

> Only include if at least one of `vault/companies/{{TICKER_A}}/leadership.md`
> or `vault/companies/{{TICKER_B}}/leadership.md` exists. If only one exists,
> show just that ticker and note the absence of the other.

| | {{TICKER_A}} | {{TICKER_B}} |
|---|---|---|
| **Signal** | {{Positive / Neutral / Negative / Mixed / "No profile"}} | {{...}} |
| **Takeaway** | {{one-line Bottom Line paraphrase}} | {{...}} |

{{1-2 sentences on which founder signal is stronger and whether it changes the
allocation calculus. If a strong founder signal on one side pulls against the
fundamentals conclusion, the Allocation Verdict at top reflects that — note
briefly here, don't re-litigate.}}

---

## The Council (Allocation Frame)

### Contrarian
{{150-200 words. Argues against the obvious choice — whichever stock looks
better after the head-to-head analysis. What's the bear case for the "winner"?
What would have to be true for the underdog to outperform? No hedging.}}

### Bull
{{150-200 words. Makes the case for the underdog — the less obvious pick.
What is the market underpricing in the stock that looks weaker at first glance?
What's the upside scenario if things go right? No hedging.}}

### First-Principles
{{150-200 words. Ignores the comparison framing entirely. Reasons from scratch:
which of these two businesses, at these prices, is the better long-term bet for
this specific user given their vault context and investment thesis? No hedging.}}

---

*Generated: {{timestamp}}*
```

## Comparison Rules

1. **Three files always.** Two individual deep dives (standard template) plus
   one comparison file (this template). Never skip the individual files.
2. **Numbers from scripts only.** Same rule as single-stock — no fabricated figures.
3. **Allocation verdict is mandatory and at the top.** One of four options.
   No "it depends." Placed at the top so re-reads are fast.
4. **SPLIT requires justification.** Splitting is not a hedge. Only recommend
   a split if the stocks are genuinely uncorrelated and both have strong setups.
5. **Loser gets a revisit condition.** The verdict's Triggers section must
   name a specific price or catalyst for each ticker.
