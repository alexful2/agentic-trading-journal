# C14 — Share Issuance & Dilution Drag

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** Firms that increase shares outstanding subsequently underperform; net share issuance is one of the strongest cross-sectional return predictors in modern US data — stronger, individually, than size, value, or momentum.

**Sources.**
- Pontiff & Woodgate (2008), "Share Issuance and Cross-sectional Returns," *Journal of Finance* 63(2):921–945. DOI 10.1111/j.1540-6261.2008.01335.x *(citation of record)*. Working paper: SSRN 679143 ("Shares Outstanding and Cross-Sectional Returns").
- *Corroboration:* McLean, Pontiff & Watanabe (2009), "Share issuance and cross-sectional returns: International evidence," *Journal of Financial Economics* 94(1):1–17 — replicates the effect across 41 countries (issuance predictability exceeds size and momentum, similar to B/M).

**Evidence setting.** Measure = split/dividend-adjusted **log change in shares outstanding** over the prior 12 months (June→June). All NYSE/AMEX/Nasdaq common stocks sorted into deciles, value-weighted, held 12 months. Sample **1970–2003**. Cross-sectional, portfolio-level — **not** single-stock.

**Replication & decay.** Post-1970, issuance predicts the cross-section *more statistically significantly than size, B/M, or momentum individually* (the paper's headline claim). Net-issuance decile spread (low-issuance/repurchasers minus high-issuance) ≈ **8 percentage points/year** raw, ≈ **6%/year** after a Fama-French 3-factor adjustment — not absorbed by size/value/market *(these exact spread figures are from an industry summary, not yet read from PW's own tables — see Verification)*. **Pre-1970: no significant predictive ability** for most holding periods (the effect is a modern-era phenomenon). Related to, but not fully subsumed by, the FF investment factor (CMA). Like other public anomalies it has compressed since publication ([[C1 - Publication & Arbitrage Decay]]).

**What this is NOT.** A cross-sectional average — **not a single-name sell signal.** Distinct from [[C13 - Asset Growth and Capex Caution]]: C13 is *total-asset* growth (the operating/buildout channel); C14 is the **financing channel specifically** — equity supply. A name can trip both.

**How to apply.** This is the **dilution lens** for serial issuers. Firms that fund their buildouts through ATM programs and secondary offerings sit in the high-issuance decile by construction. C14 says that's a *structural return headwind* stacked on top of C13's asset-growth headwind. The thesis has to clear both.

**Decision-rule translation.**
- Track **net share growth**, not just market cap or revenue — a name whose share count is climbing is paying the issuance headwind even if the stock is up.
- The exception condition (same logic as C13): issuance is only "good" dilution if the proceeds fund **contracted, demand-matched, NPV-positive** capacity — verify via `execution-thesis` / `projects.md`, don't assume. Issuing to fund a signed offtake is repricing; issuing to fund a speculative overbuild (or to time a high stock price) is exactly what the anomaly punishes.
- Read the dossier's `financials.md` dilution-overhang field at thesis-check time; a fast-rising share count raises the burden of proof on the bull case.

**Tension / failure mode.** For a genuine land-grab, issuing equity to capture demand-matched capacity can be the *right* move even though the average heavy issuer underperforms — the anomaly is dominated by firms that issued to empire-build or to time an overvalued price. Don't let C14 veto a financed, contracted buildout; let it force the question *"is this issuance funding demand, or funding dilution?"* If you can't answer, assume the latter.

**Links.** [[C13 - Asset Growth and Capex Caution]] · [[C5a - Gross Profitability Premium]] · [[C9 - Most Stocks Underperform T-Bills]] · [[C1 - Publication & Arbitrage Decay]] · `execution-thesis` · `company-dossier`

**Verification.** **Qualitative claim CONFIRMED** 2026-06-06 against the primary abstract (Wiley DOI / RePEc / SSRN): post-1970 issuance predicts returns more significantly than size/B/M/momentum individually; pre-1970 insignificant; not subsumed by FF3. **Effect independently corroborated** by McLean-Pontiff-Watanabe 2009 (JFE, 41-country replication) and Spiegel-Watanabe (monotonic negative shares-change→return relation; same pre-1970 null) — so the *finding* is robust and replicated. **The exact decile-spread magnitude (~8pp/yr raw, ~6%/yr FF3) remains SECONDARY / illustrative:** a firsthand read of PW's own tables was attempted 2026-06-06 but the Wiley full text was unavailable ("technical difficulties") and the SSRN PDF wasn't machine-fetchable; the spread number comes from an industry summary citing the paper's deciles (D1 ≈17%/yr, D10 ≈9%/yr), not from PW's table. Treat the number as illustrative; the directional/relative claim is firsthand-solid.
