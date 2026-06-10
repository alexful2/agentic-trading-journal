# C12 — Lottery Stocks (MAX Effect)

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** Stocks with extreme recent positive daily returns ("lottery" stocks) systematically *underperform* afterward — investors overpay for lottery-like payoffs.

**Sources.**
- Bali, Cakici & Whitelaw (2011), "Maxing Out: Stocks as Lotteries and the Cross-Section of Expected Returns," *Journal of Financial Economics* 99(2):427–446. DOI 10.1016/j.jfineco.2010.08.014 *(citation of record)*. Free copy: Whitelaw's NYU Stern PDF.

**Evidence setting.** Sort stocks by **MAX = the single highest daily return in the prior month**, form deciles, track next-month returns. US equities (NYSE/AMEX/Nasdaq), **July 1962–December 2005** (522 months). *(The "average of the 5 highest daily returns" — MAX(5) — is a robustness variant, not the headline definition.)*

**Replication & decay.** Highest-MAX minus lowest-MAX decile (value-weighted) earns **−1.03%/month raw (t = 2.83)** and a **−1.18%/month four-factor alpha (t = 4.71)**. Crucially, including MAX **reverses** the puzzling negative idiosyncratic-volatility/return relation (Ang et al.) — lottery demand, not idio-vol, is doing the work. **Mechanism:** poorly-diversified, lottery-preferring investors overpay for stocks that just printed extreme positive days, so those names are overpriced and subsequently underperform.

**What this is NOT.** A cross-sectional average — **NOT** a claim that every high-flier underperforms, and not a single-name short signal. Note the corrected definition: MAX is the *single* max daily return, not the 5-day average.

**How to apply.** A common playbook is to "size as lottery" on pre-deal/speculative names — small, lose-it-all-OK. This finding is the counterweight: lottery *demand* is systematically overpriced, so a lottery sleeve carries a structural headwind. The lottery framing is fine as a **sizing discipline**, but don't expect the bucket to have positive expected return *from its lottery characteristic* — the edge has to come from a specific catalyst, not the payoff shape.

**Decision-rule translation.**
- Keep "size as lottery" as a *risk-control* rule, not a return thesis.
- A name that has spiked on hype with **no** fresh catalyst is exactly the MAX setup — fade/avoid, don't chase.
- A name extended on a **real pending catalyst** (a deal, a print) still *is* high-MAX mechanically — MAX is just the prior month's single highest daily return, catalyst or not. The catalyst can *offset or explain* the MAX headwind (the edge is informational/structural — [[C10 - Limits to Arbitrage]]), but it does **not** exempt the name from the headwind: you're paid for the catalyst while still *taxed* for the lottery look.

**Tension / failure mode.** Two deliberate tensions: (1) vs [[C4 - Momentum and Trend Persistence]] — medium-horizon cumulative winners persist, yet extreme single-*day* spikes predict underperformance; the reconciliation is trend vs blow-off. (2) vs [[C10 - Limits to Arbitrage]] — C10 says a patient holder can be *paid* in deal-driven small caps; C12 says lottery demand is *overpriced*. Resolution: you're paid for the **wait-for-deal catalyst**, not for the lottery payoff profile. If you can't name the catalyst, MAX wins and the position is just overpaying for a spike.

**Links.** [[C4 - Momentum and Trend Persistence]] · [[C10 - Limits to Arbitrage]] · [[C8 - Kelly Criterion and Position Sizing]] · [[wait-for-deal-thesis]]

**Verification.** CONFIRMED 2026-06-06 against primary source (Bali-Cakici-Whitelaw 2011 JFE, NYU Stern PDF). Raw spread −1.03%/mo (t=2.83), 4-factor alpha −1.18%/mo (t=4.71), sample 1962–2005, IVOL-reversal result — all match. **Correction vs draft:** headline MAX = single highest daily return (not the 5-day average, which is the MAX(5) robustness variant); and the risk-adjusted spread (−1.18%/mo) is *larger* than the drafted "−0.65 to −1.0%" range.
