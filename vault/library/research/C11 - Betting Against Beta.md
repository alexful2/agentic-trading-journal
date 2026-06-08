# C11 — Betting Against Beta

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** High-beta stocks earn *lower risk-adjusted* returns than low-beta stocks — the empirical security market line is flatter than the CAPM predicts. Beta is not, by itself, a paid-for source of return.

**Sources.**
- Frazzini & Pedersen (2014), "Betting Against Beta," *Journal of Financial Economics* 111(1):1–25. DOI 10.1016/j.jfineco.2013.10.005 *(citation of record)*. NBER WP 16601. Free copy: authors' NYU Stern PDF.

**Evidence setting.** Construct a "BAB" factor: long *leveraged* low-beta assets, short high-beta assets, to isolate the slope of the risk/return line. Tested across US stocks (1926–March 2012), 19 international equity markets, Treasuries, credit, and futures.

**Replication & decay.** The US BAB factor earns a 3-factor alpha of **0.73%/month (t = 7.39)**; **0.55%/mo (t = 5.59)** after adding momentum; **0.55%/mo (t = 4.09)** in a 5-factor model — and a **Sharpe ratio of 0.78** (1926–2012), ~2× the value effect. Alphas and Sharpes decline ~monotonically in beta; the flat-SML result holds in **18 of 19** global markets, plus bonds and futures. **Mechanism:** leverage-constrained investors (who can't borrow to lever a low-beta portfolio) instead bid up high-beta assets to reach their target risk, depressing high-beta risk-adjusted returns.

**What this is NOT.** **NOT "high-beta stocks underperform in absolute terms."** In a bull regime, high-beta can and does outperform on *raw* return. The claim is strictly *risk-adjusted*: you're not compensated for the beta per se. Cross-sectional/portfolio result — not a single-name signal.

**How to apply.** Translation: **beta is not edge; sharp exposure must earn its keep through thesis-specific upside.** High-beta names give you torque, but BAB says the beta alone won't pay you — so each must justify itself with specific, identifiable upside (contracted demand, deal optionality, execution ahead of schedule), not just "more torque on the trade."

**Decision-rule translation.**
- Don't treat high beta as a reason to *expect* higher return — strip the beta out and ask what thesis-specific edge remains.
- Size the high-beta sleeve smallest where the edge is least calibrated ([[C8 - Kelly Criterion and Position Sizing]]); high beta + uncalibrated edge is the worst combination.
- The actionable takeaway is the *caution on high-beta*, not "go build a levered low-beta book" — for an unlevered holder the BAB construction itself isn't a strategy to run; the cross-sectional lesson is what transfers.

**Tension / failure mode.** BAB is a long-horizon, risk-adjusted, leverage-arbitrage result; in a strong bull regime a high-beta sleeve may be the right *raw-return* bet even though it's "unpaid beta" on paper. The error would be using BAB to veto the sharp sleeve outright — instead use it to demand the thesis-specific upside and to keep the sizing honest. Reinforces the "safety" penalty in [[C5b - Quality Minus Junk]].

**Links.** [[C5b - Quality Minus Junk]] · [[C8 - Kelly Criterion and Position Sizing]] · [[C12 - Lottery Stocks (MAX Effect)]] · [[C9 - Most Stocks Underperform T-Bills]]

**Verification.** CONFIRMED 2026-06-06 against primary source (F&P 2014 JFE, authors' NYU Stern PDF + NBER w16601). BAB alphas 0.73 / 0.55 / 0.55 %/mo, Sharpe 0.78 (1926–2012), flat SML in 18/19 markets — all match. Version trap: the Dec-2010 NBER WP used a shorter sample; figures above are the published 2014 version.
