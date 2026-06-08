Status: #library
Tags: #framework #AI-infra #sizing

---

# AI Capex ROIC J-Curve: When Does This Trade Actually Pay Back?

A sizing-time framework for the AI infrastructure thesis. It answers the question that [[ai-infra-thesis-kill-switches]] and [[ouroboros-economy-circular-financing]] don't: assuming the buildout *isn't* breaking, *when* does the math work?

## The shape of the J-curve

Hyperscaler capex is running near $785B–$1T annualized against AI-product revenue of "low hundreds of billions." Sell-side models put return on invested capital below a ~12% cost-of-capital threshold until roughly year 9–10 of the cycle — the back half of the decade. The J-curve is the period during which FCF compresses and reported earnings get carried by depreciation accounting, not cash generation.

- **AMZN: FCF projected negative** for the first time in over a decade — the AI buildout consumes the pre-AI free cash flow and then some. The compression is intended, not accidental.
- **Alphabet: FCF down sharply YoY.** Same shape: revenue grows, capex grows faster, reported earnings stay up, cash collapses.
- **MSFT, META: same direction, smaller magnitude** because their pre-AI cash bases are larger.

This is not a sign the thesis is failing. It is the *expected* shape of a multi-year buildout where assets get spent first and revenue arrives years later. The same pattern applied to the rail buildout (1860s–1880s), the electrification of US factories (1900s–1920s), and the fiber buildout (late 1990s).

## Why this matters for sizing

The sizing question is "what payback horizon am I underwriting?" Three answers, three implications:

- **Underwriting a 2-year payback** — wrong. The capex hasn't paid back, and the J-curve says it won't for years. If sizing assumes near-term marks through earnings, every soft FCF print looks like a thesis break. It isn't.
- **Underwriting a 5-year payback** — sizing-aggressive. ROIC clears cost of capital around year 5–6 only on the bullish assumptions (faster revenue ramp, lower depreciation drag).
- **Underwriting a ~10-year compounding window** — sizing-correct under the central case. The thesis pays back when ROIC clears WACC durably, around year 9–10. This is the right horizon to size to: "AI capex compounds through the back half of the decade," not "a specific near-term date nails it."

## Operational rule

When a hyperscaler print shows FCF compression *without* a corresponding deceleration in capex guidance, the right read is "J-curve as expected" — not "thesis broken." The thesis breaks when **capex guidance itself decelerates** (the kill-switch #1 threshold of <10% YoY for two consecutive cycles), not when FCF compresses while capex is still ramping.

The trap is reading the FCF line as a forward indicator. It is a *consequence* of capex acceleration, not a signal about future cash generation. Cash generation lives in the post-J-curve period, years out — not next quarter.

## What would falsify the J-curve frame

- AI revenue ramps slower than the depreciation schedule (industry estimates of a large annual revenue shortfall by 2030). If realized, the curve doesn't J — it stays underwater.
- Asset useful life shorter than depreciation assumes (e.g. 3-year GPU obsolescence vs. 5–6-year accounting life). Compresses the back half of the curve.
- WACC rises before revenue arrives — connects to the [[ai-infra-thesis-kill-switches]] discount-rate path.

These aren't kill-switches — they're parameters that move the payback point. Worth tracking in deep-dives on hyperscalers where the FCF question is central.

## Pairs with

- [[ai-infra-thesis-kill-switches]] — names the *break conditions*; this entry names the *expected payback horizon* under non-break conditions.
- [[ouroboros-economy-circular-financing]] — describes where the dollars travel intra-cohort while the J-curve plays out.

---
# References
- [[ai-infra-thesis-kill-switches]]
- [[ouroboros-economy-circular-financing]]
