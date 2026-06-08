# C4 — Momentum & Trend Persistence

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** Stocks that have outperformed over the past 3–12 months tend to keep outperforming over the next 3–12 months — winners persist, losers keep losing, on average.

**Sources.**
- Jegadeesh & Titman (1993), "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency," *Journal of Finance* 48(1):65–91. DOI 10.1111/j.1540-6261.1993.tb04702.x *(discovery)*. Free copy: U-Houston Bauer PDF.
- Jegadeesh & Titman (2001), "Profitability of Momentum Strategies: An Evaluation of Alternative Explanations," *Journal of Finance* 56(2):699–720. DOI 10.1111/0022-1082.00342 *(out-of-sample defense)*.

**Evidence setting.** Cross-sectional relative-strength: rank stocks by trailing return, go long winners / short losers, hold 3–12 months. US equities, **1965–1989** (1993 paper); 16 formation/holding combinations. **Long-short portfolio — not a single-stock rule.**

**Replication & decay.** The 6-month/6-month winners-minus-losers strategy earns **~0.95%/month (t = 3.07)** with a one-week skip (≈**12.01%/yr** compounded for the no-skip 6/6 variant); the 12-month-formation/3-month-holding variant reaches **~1.49%/month**. Out-of-sample, momentum *persisted*: **1.39%/month over 1990–1998** (published 2001), confirming it wasn't data-snooping. Important reversals bracket the effect: ~half the first-year abnormal return **reverses over the following two years**, and there is short-term (1-month) reversal at the front. One of the best-replicated anomalies — but subject to rare, severe **"momentum crashes"** in sharp market rebounds.

**What this is NOT.** A cross-sectional, diversified long-short result — **NOT a license to chase any single name.** The factor's attractive Sharpe comes from holding many names; a concentrated holder bears the crash risk without that diversification.

**How to apply.** This is the empirical counterweight to the "extended, foolish to chase" instinct. The base rate says medium-horizon winners persist, so strength is not automatically FOMO — check whether a fresh catalyst is in play before reaching for that label. It's also *consistent with* (doesn't contradict) the idea that deal-driven names can run rather than dip — medium-horizon strength isn't automatically FOMO. But this is a weak cross-sectional prior: the deal/catalyst thesis does the real work, not the momentum factor.

**Decision-rule translation.**
- A name extended on a *fresh, thesis-confirming catalyst* is consistent with momentum continuation — separate repricing from FOMO before reaching for "don't chase."
- But respect the reversal structure: don't add on a 1-month vertical spike (short-term reversal zone), and don't expect a 2-year-old run to keep compounding (long-run reversal).
- Because a concentrated holder can't diversify away momentum crashes, the takeaway is "don't *fear* strength," not "concentrate *into* strength" — size via [[C8 - Kelly Criterion and Position Sizing]].

**Tension / failure mode.** Two live tensions to preserve, not resolve: (1) vs [[C12 - Lottery Stocks (MAX Effect)]] — medium-horizon cumulative momentum persists, yet *extreme single-day* spikes predict underperformance; reconcile by distinguishing steady trend from a hype blow-off. (2) The single-name concentration risk: momentum crashes hit high-beta concentrated books ([[C11 - Betting Against Beta]]) hardest, exactly where a high-torque sleeve lives.

**Links.** [[C12 - Lottery Stocks (MAX Effect)]] · [[C11 - Betting Against Beta]] · [[C8 - Kelly Criterion and Position Sizing]] · [[C3 - Post-Earnings-Announcement Drift]]

**Verification.** CONFIRMED 2026-06-06 against primary sources (JT 1993 U-Houston PDF; JT 2001 Wharton PDF). 0.95%/mo (6/6, t=3.07), 12.01%/yr (6/6 no-skip), ~1.49%/mo (12/3), 1965–1989 sample; out-of-sample 1.39%/mo (1990–1998). **Version trap:** JT 2001 out-of-sample is 1.39%/mo published (1990–1998) vs 1.01%/mo in the NBER WP (1990–1997) — published figure used.
