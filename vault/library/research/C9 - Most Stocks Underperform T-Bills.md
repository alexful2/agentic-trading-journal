# C9 — Most Stocks Underperform T-Bills

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** The median stock is a loser. Aggregate market returns come from a tiny minority of extreme winners; most individual stocks underperform Treasury bills over their lifetimes.

**Sources.**
- Bessembinder (2018), "Do Stocks Outperform Treasury Bills?", *Journal of Financial Economics* 129(3):440–457. DOI 10.1016/j.jfineco.2018.06.004 *(citation of record)*. Free copy: ASU W.P. Carey author manuscript.

**Evidence setting.** All 25,967 CRSP common stocks (25,332 distinct firms), 1926–2016, lifetime buy-and-hold returns vs one-month T-bills.

**Replication & decay.** Only **42.6%** of stocks beat T-bills over their lifetime (so **57.4%** do not — "slightly more than four of every seven"). The **modal lifetime return is ≈ −100%** (a total loss; 11.8% of stocks lost essentially everything). Yet US stocks created **$34.82 trillion** in net wealth — and just **1,092 firms (4.31%)** account for *all* of it, with the other ~96% collectively only matching T-bills; **90 firms (0.36%)** account for *half*. Not an anomaly that decays — a structural fact about the positive skew of compounded returns.

**What this is NOT.** NOT an argument for indexing per se, and NOT a claim that stock-picking is hopeless. It's a statement about the *shape* of the return distribution: the payoff is a lottery on being in the tail.

**How to apply — the honest mirror.** This is the strongest pushback in the catalog on a concentrated style, and it should not be softened: *"most stocks underperform T-bills" argues against single-name concentration unless you can identify the rare winners ex ante.* Concentration is rational **only** when a thesis has unusually strong evidence of power-law upside; absent that, the base rate punishes single-name picking. So the question every concentrated position must answer is not "do I like this story?" but "is there specific, checkable evidence this is plausibly one of the ~4% — ideally one of the 90?"

**Decision-rule translation.**
- For each core holding, write the explicit power-law case: what makes this a tail-winner candidate, with evidence, not narrative. If the answer is thin, the position is too big.
- The flip side cuts the other way too: because the market's return is concentrated in the few, *diworsifying* into mediocre names is also punished. The resolution is "concentrate only where there's real tail evidence," not "own a little of everything."
- Pair with [[C5b - Quality Minus Junk]] (defines what a durable tail-winner looks like) and [[C8 - Kelly Criterion and Position Sizing]] (size for the skew — most bets lose, so don't over-bet any one).

**Tension / failure mode.** The danger is using the "few winners drive everything" half to *justify* concentration while ignoring the "57.4% underperform / modal return −100%" half. Both are the same fact. Hold them together: the upside is real but rare, so the burden of proof on any concentrated bet is high, and the downside (total loss) is the *typical* outcome, not the tail. **Counterweight:** [[C15 - Concentration Done Right]] shows concentration *is* rewarded when it reflects genuine information advantage in under-covered names — that *narrows the gate* a concentrated bet must pass, it doesn't open it.

**Links.** [[C15 - Concentration Done Right]] · [[C5b - Quality Minus Junk]] · [[C8 - Kelly Criterion and Position Sizing]] · [[C13 - Asset Growth and Capex Caution]] · [[opportunity-cost lens]]

**Verification.** CONFIRMED 2026-06-06 against primary source (Bessembinder 2018 JFE, author manuscript). 42.6% outperform / 57.4% underperform, $34.82T, 1,092 firms (4.31%) for all net wealth, modal return ≈ −100%, 1926–2016 — all match. **Correction vs draft:** the count of firms creating *half* of net wealth is **90 (0.36%)**, not 86 — the "86" is a press-release artifact and was dropped.
