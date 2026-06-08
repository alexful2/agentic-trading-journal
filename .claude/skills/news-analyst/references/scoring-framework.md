# Severity Scoring Framework

Score each news item 1-5 based on how much it matters to THIS portfolio.

## The Scale

### 1 — Noise
No meaningful impact. Routine coverage, unrelated sectors.

*Examples:*
- Analyst reiterates target on a stock I don't hold
- Routine executive hire at an unrelated company
- Generic market commentary ("stocks could go up or down")

### 2 — Low / Background
Slight relevance. Worth noting, no action needed. Could matter if a trend develops.

*Examples:*
- A competitor of a held stock launches an incremental product
- Minor regulatory comment about an industry I'm exposed to
- Small commodity price moves in inputs my holdings use
- Analyst initiates coverage on a stock adjacent to my holdings

### 3 — Moderate / Noteworthy
Meaningful relevance. Could affect a position over weeks/months. Worth reading.

*Examples:*
- Competitor reports surprisingly strong/weak earnings (sector demand signal)
- Fed signals shift in rate trajectory (affects growth valuations)
- Significant regulatory proposal targeting an industry I hold
- Supply chain disruption that touches 1-2 holdings indirectly
- Credible M&A rumors in my sector
- Major AI infrastructure spending announcement or cut

### 4 — High / Direct Impact
Direct, significant impact on a position or portfolio risk. Demands attention today.

*Examples:*
- A held stock misses/beats earnings by >10%
- CEO departure or major restructuring at a held company
- Regulatory action directly targeting a held company
- Major tariff/trade restriction on a held stock's supply chain
- Unexpected Fed rate decision
- Multiple positions affected by the same event simultaneously

### 5 — Critical / Thesis-Threatening
Could invalidate the core thesis for a position. Rare — a few times per year max.

*Examples:*
- Fraud, accounting issues, or SEC investigation at a held company
- Government bans a held company's core product
- Breakthrough that makes a held company's technology obsolete
- Systemic financial event (bank failures, credit crisis)
- Broad, confirmed AI capex cuts across multiple hyperscalers
  (this would directly threaten the AI infrastructure thesis)

## Scoring Principles

1. **Score for MY portfolio.** A Fed hike is severity 4 for leveraged growth,
   severity 2 for stable value names.

2. **My AI conviction raises the stakes.** News that threatens the AI
   infrastructure thesis is higher severity because my portfolio is
   concentrated there. Conversely, news confirming AI momentum can be
   lower severity (it's already priced into my thesis).

3. **Don't cluster at 3.** Most items on a typical day should be 1-2.
   A 4 or 5 should feel uncomfortable to write.

4. **Second-order effects matter.** "China restricts rare earth exports"
   might seem like a 2 for software stocks, but if my holdings depend on
   hardware using those materials, it could be 3-4.

5. **When unsure, give the range.** "Severity 3-4 (depends on whether
   the exemption is extended)" is better than false precision.

## Daily Heat Score (optional summary metric)

```
Heat = sum of (severity × weight) for top 5 items

Weights by connection type:
  Direct = 1.0, Competitor = 0.7, Sector = 0.5,
  Supply Chain = 0.5, Macro = 0.3, Thematic = 0.3

Interpretation:
  0-3: Quiet day     4-7: Normal
  8-12: Active       13+: High alert
```
