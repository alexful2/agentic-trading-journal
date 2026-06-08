# Thesis Tripwires

> Not investment advice.

Pre-registered, **measurable** invalidation conditions per holding — written at
conviction time (deep-dive / entry), checked against reality, surfaced when tripped.
Decide what would prove you wrong *before* you're attached, so you can't quietly
move the goalpost later. The vault's antidote to the disposition effect
([[C6 - Disposition Effect]]) and to [[C10 - Limits to Arbitrage]] being abused as
an excuse to hold a loser.

**A tripwire must be falsifiable and measurable** — a number, a date, or a named
event. "Stock goes down" is not a tripwire. "Gross margin negative for 2
consecutive quarters" or "contracted power capacity still <2 GW by 2026-12-31" is.

- **Who writes them:** `stock-deep-dive` (Step 8e, from the Thesis Validation
  invalidation criteria) + manual entry.
- **Who checks them:** `news-analyst` daily (reactive — when today's news/filings
  touch a tripwire) and `weekly-review` (Step 3d — systematic pass for slow
  fundamentals).
- **On a trip:** `run deep-dive TICKER`. A tripwire is a pre-committed "you may be
  wrong" signal, not an auto-sell.

**Status:** `ARMED` (live, untripped) · `TRIPPED` (condition met — re-evaluate) ·
`RETIRED` (thesis changed / position closed / condition obsolete).
**Type:** `fundamental` (margins / KPIs / financials) · `event` (contract, filing,
guidance) · `price` (prefer the price-trigger system for pure price levels; only put
a price level here if it is a genuine *thesis-invalidation* level).

| Ticker | Tripwire (measurable condition) | Type | Set | Source | Status |
|--------|---------------------------------|------|-----|--------|--------|
| CRWV | $3B convertibles price with a strike below $120 (dilution overhang fires) | event | 2026-06-06 | `CRWV-2026-06-06` | ARMED |
| CRWV | Q2 FY26 op income below the guided $30M floor, OR FY26 op-income guide cut below $900M | fundamental | 2026-06-06 | `CRWV-2026-06-06` | ARMED |
| CRWV | Backlog flat-or-down sequentially at Q2 (from $99.4B), OR a top-3 customer publicly cuts/cancels | fundamental | 2026-06-06 | `CRWV-2026-06-06` | ARMED |
| IREN | Adj EBITDA flat-or-down a 2nd consecutive quarter at Q4 FY26 (Aug 27) — first leg already fired (Q3 $59.5M vs $75.3M) | fundamental | 2026-06-07 | `IREN-2026-06-07` | ARMED |
| IREN | Microsoft RPO still $0 at the Q4 FY26 print (Aug 27), OR Horizon-1 tranche-1 slips past Q3 CY26 — the ARR ramp (the valuation crux) isn't starting | event | 2026-06-07 | `IREN-2026-06-07` | ARMED |
| IREN | Goldman/JPM $3.6B term loan closes at materially reduced size or punitive terms, OR the $2.0B converts price punitively — financing fails to gate the ramp | event | 2026-06-07 | `IREN-2026-06-07` | ARMED |

*Last updated: 2026-06-07 — IREN rows added from [[IREN-2026-06-07]] Implied Expectations falsification thresholds; deep-dives populate real rows.*
