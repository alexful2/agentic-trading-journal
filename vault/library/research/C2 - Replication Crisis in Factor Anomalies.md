# C2 — Replication Crisis in Factor Anomalies

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** Most published cross-sectional return anomalies do not replicate once microcaps are controlled (NYSE breakpoints + value-weighted returns) and multiple testing is accounted for — many were artifacts of method, not real edges.

**Sources.**
- Hou, Xue & Zhang (2020), "Replicating Anomalies," *Review of Financial Studies* 33(5):2019–2133. DOI 10.1093/rfs/hhy131 *(citation of record)*. Free copy: global-q.org PDF. *(NBER WP 23394, 2017, is the earlier working-paper version with different counts — see Tension.)*
- Harvey, Liu & Zhu (2016), "…and the Cross-Section of Expected Returns," *Review of Financial Studies* 29(1):5–68 / NBER w20592 — the multiple-testing t-stat hurdle.

**Evidence setting.** 452 anomaly variables across six categories (57 momentum, 69 value-vs-growth, 38 investment, 79 profitability, 103 intangibles, 106 trading frictions). US equities, CRSP/Compustat. Replication = high-minus-low decile return significant at |t| ≥ 1.96, using NYSE breakpoints + value-weighted returns to keep microcaps from dominating. Portfolio-level long-short — **not** single-stock.

**Replication & decay.** 65% of the 452 fail the |t| ≥ 1.96 single-test hurdle (~35% replicate); 96% of the trading-frictions category fail; raising to the multiple-testing hurdle |t| ≥ 2.78 pushes the failure rate to 82%. Even the anomalies that do replicate have economic magnitudes well below their original reports. Microcaps are the culprit: ~3.2% of aggregate market cap but ~60.7% of the *number* of stocks, so equal-weighting (common in the original studies) hands them outsized influence. Harvey-Liu-Zhu argue a newly claimed factor should clear **t > 3.0**, not 2.0, because hundreds have been tested.

**What this is NOT.** NOT "factors don't exist" — roughly a third *do* replicate (momentum, value, profitability, investment survive best). NOT a statement about decay-over-time (that's [[C1 - Publication & Arbitrage Decay]]) — these largely never replicated to begin with. The mechanism is **method** (microcap overweighting + p-hacking + multiple testing), not arbitrage.

**How to apply.** This is the **first gate** on the whole empirical-priors layer. Before importing any "strategy" finding, ask: would it survive HXZ-style replication (value-weighted, multiple-testing hurdle)? If it isn't in the surviving third — or you can't tell — treat it as decoration, not a prior. Most of what gets blogged about lives in the failing 65%.

**Decision-rule translation.**
- Default prior on any single published anomaly: *probably doesn't replicate.* Burden of proof is on the finding.
- Trust surviving **categories** (momentum / value / profitability / investment) over exotic single-signal anomalies.
- Be most skeptical of anything that needs small or illiquid stocks to work — that's where the fake edges concentrate, and most discretionary holders trade liquid large/mid names anyway.
- Demand a high t-stat (think t > 3, HLZ), not merely "statistically significant."

**Tension / failure mode.**
- *Version trap:* the 2017 NBER WP (447 anomalies / 64% fail / t>3 → 85%) and the 2020 RFS paper (452 / 65% / t≥2.78 → 82%) report slightly different numbers. Cite the RFS figures; don't mix them.
- Don't over-rotate into nihilism — "nothing replicates" is as wrong as "everything does." ~35% is a real, usable core.
- Replication is about *average* effects in a broad universe; it says nothing about a specific mispriced single name where your edge is informational, not factor-based (see [[C1 - Publication & Arbitrage Decay]]).

**Links.** [[C1 - Publication & Arbitrage Decay]] · [[C13 - Asset Growth and Capex Caution]] · `execution-thesis` · `company-projects`

**Verification.** **HXZ figures CONFIRMED** 2026-06-06 against primary source (HXZ 2020 RFS abstract + body via global-q.org and theinvestmentcapm.com author PDFs; cross-checked NBER w23394) — 452 anomalies, 65% fail at |t|≥1.96, 96% of trading frictions, 82% at |t|≥2.78, category counts all match. **HLZ t>3 hurdle: SECONDARY-CONFIRMED via HXZ's explicit citation only** — the Harvey-Liu-Zhu paper was not separately fetched; check it directly before relying on the t>3 threshold as primary-sourced.
