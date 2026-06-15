# C8 — Kelly Criterion & Position Sizing

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** There is a growth-optimal fraction of capital to bet given a known edge; betting *more* than that fraction lowers long-run growth *and* raises variance (strictly dominated). The practical lesson is directional, not numeric.

**Sources.**
- Kelly (1956), "A New Interpretation of Information Rate," *Bell System Technical Journal* 35(4):917–926. DOI 10.1002/j.1538-7305.1956.tb03809.x *(citation of record)*. Free copy: Princeton-hosted PDF (reproduced with AT&T permission).
- Over-betting penalty / fractional-Kelly trade-off: **post-Kelly practitioner & log-growth literature** (Thorp; MacLean–Thorp–Ziemba) — *not* in the 1956 paper. Attributed accordingly.

**Evidence setting.** A gambler maximizing the long-run exponential growth rate of capital, G = lim (1/N)·log(V_N/V_0). For a binary bet the optimal fraction is ℓ = q − p (bet the edge). The criterion is **log-optimal / growth-optimal**, explicitly *not* expected-wealth-maximizing — betting the whole bankroll maximizes expected wealth but leads to ruin with probability one.

**Replication & decay.** Not an empirical anomaly — a mathematical result, so no decay. The growth function G(ℓ) is concave and peaks at full Kelly; over-betting beyond ~2× Kelly drives long-run growth negative. Fractional (e.g. half) Kelly keeps most of the growth at far lower drawdown (Thorp et al.).

**What this is NOT — read this first.** **NOT a formula to compute a "position size" from a guessed probability.** Kelly requires *known* p, q, and odds; change the assumed edge and the optimal fraction moves one-for-one. A calibrated edge estimate is rarely available, so any agent (or person) computing a precise "Kelly size" from a vibe probability is manufacturing false precision — explicitly forbidden, and a corollary of the no-hallucinated-numbers rule.

**How to apply.** Use it as the sizing *philosophy* under a concentrated book. "Size for the durable thesis playing out over years, not for nailing a single date" is qualitatively a fractional-Kelly argument: uncertainty about the edge means you bet *below* the point-estimate optimum, not at it.

**Decision-rule translation.**
- Never derive a numeric position size from an uncalibrated probability. Use Kelly as a *direction*, not a calculator.
- The robust, usable lessons: (1) over-betting is punished twice (lower growth + higher variance), so when uncertain, **size down**; (2) treat full Kelly as a ceiling you stay well under (fractional Kelly), never a target.
- Size *smallest* exactly where edge estimates are least reliable — the lottery sleeve ([[C12 - Lottery Stocks (MAX Effect)]]) and high-beta names ([[C11 - Betting Against Beta]]).

**Tension / failure mode.** The whole apparatus assumes a known edge you don't have — so the danger is reverse-engineering a confident probability just to justify a size. If you find yourself doing that, the honest move is to size as if the edge is smaller than it feels. Under-betting only costs growth linearly; over-betting can compound to ruin.

**Links.** [[C9 - Most Stocks Underperform T-Bills]] · [[C11 - Betting Against Beta]] · [[C12 - Lottery Stocks (MAX Effect)]] · [[opportunity-cost lens]]

**Verification.** CONFIRMED 2026-06-06 against primary source (Kelly 1956, Princeton author-permission PDF). Citation (35(4):917–926), the ℓ = q − p growth-optimal result, and the "get ahead and stay ahead with probability one" framing all verified verbatim. Attribution discipline: the over-betting-penalty and fractional-Kelly results are explicitly *post-1956* practitioner/log-growth literature, **not** Kelly's paper — flagged as such above.
