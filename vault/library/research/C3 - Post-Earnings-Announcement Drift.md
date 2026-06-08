# C3 — Post-Earnings-Announcement Drift (PEAD)

> Empirical-priors research note (research/ catalog). Not investment advice.

**Claim.** After an earnings surprise, prices keep drifting in the direction of the surprise for weeks-to-quarters, because the market underreacts to what current earnings imply for *future* earnings.

**Sources.**
- Bernard & Thomas (1989), "Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium?", *Journal of Accounting Research* 27(Suppl):1–36. DOI 10.2307/2491062.
- Bernard & Thomas (1990), "Evidence That Stock Prices Do Not Fully Reflect the Implications of Current Earnings for Future Earnings," *Journal of Accounting and Economics* 13(4):305–340. DOI 10.1016/0165-4101(90)90008-R. Free copy: U-Michigan Deep Blue.

**Evidence setting.** Stocks sorted into deciles by standardized unexpected earnings (SUE); abnormal returns tracked after the announcement. US equities, ~1974–1986. The 1990 companion paper studies the autocorrelation structure of seasonally-differenced quarterly earnings.

**Replication & decay.** The long-best-SUE / short-worst-SUE hedge earns **+4.19% over the 60 trading days** post-announcement and ~**7.98% over ~240 days (~1 year)**; ~1/6 of it accrues in the first five days; the top-minus-bottom decile spread was positive in **41 of 48 quarters** (1974–1985). BT find the hedge return is bounded around **~4%** over the standard window (roughly transaction costs for the average firm). **Mechanism (1990):** investors price earnings as if they follow a seasonal random walk, ignoring the real autocorrelations of seasonally-differenced earnings (**0.34, 0.19, 0.06, −0.24** at lags 1–4), so they are predictably surprised at the next four prints — abnormal announcement returns of **+1.32%, +0.70%, +0.04%, −0.66%** at t+1…t+4. PEAD has weakened over the decades (consistent with [[C1 - Publication & Arbitrage Decay]]) but is one of the most durable anomalies.

**What this is NOT.** NOT validation of any specific short holding window, and NOT a single-name guarantee. It is *adjacent* evidence for a day-1-vs-multi-day split in pre-earnings planning — and notably it argues the drift window is **longer** (60–240 days, clustered around the *next* print) than a +5-day trade captures.

**How to apply.** This directly sharpens any pre-earnings ladder and the day-1-vs-+5d drift split. The key reframe: a genuine earnings surprise is a multi-week-to-multi-quarter signal, not a one-day pop. If a print confirms the thesis, the drift literature says the move tends to *continue* (and re-accelerate at the next earnings date), so fading strength on day 1 can leave the drift on the table.

**Decision-rule translation.**
- Treat a real surprise as a persistence signal: the ladder should allow for adds/holds over weeks, and pay attention to the *next* earnings date as a second leg, not just day-1 reaction.
- Don't over-anchor to the +5d window — that's a common short-horizon frame, but PEAD says the effect runs longer; size the expectation to the longer horizon.
- Distinguish a true SUE surprise (drift candidate) from a price move on guidance/sentiment with no earnings surprise (not PEAD).

**Tension / failure mode.** PEAD is an *average cross-sectional* effect, has decayed as it's been arbitraged ([[C1 - Publication & Arbitrage Decay]]), and several studies lean on small/illiquid names ([[C2 - Replication Crisis in Factor Anomalies]]) — so the magnitude for a liquid large-cap is smaller than the headline. Use it to shape *expectation of persistence*, not as a sizing multiplier.

**Links.** [[C1 - Publication & Arbitrage Decay]] · [[C2 - Replication Crisis in Factor Anomalies]] · [[C4 - Momentum and Trend Persistence]]

**Verification.** PARTIAL (2026-06-06). **BT 1990 CONFIRMED firsthand** — abstract/mechanism + autocorrelations + announcement-return pattern via DOI/ScienceDirect + U-Michigan Deep Blue. **BT 1989 figures SECONDARY-CORROBORATED, not read firsthand** — the original PDF could not be rendered (JSTOR paywall/crawl timeout); its figures (+4.19% / 7.98% / 41-of-48 quarters / ~4% bound) are corroborated via multiple independent academic papers quoting BT 1989's Table 1 (strong, but one step removed). Pending a firsthand JSTOR/PDF check before treating BT 1989's numbers as fully confirmed. **Correction vs draft:** the "~18% annualized hedge" figure is wrong and was dropped; the primary figures are +4.19% (60d) / ~7.98% (240d).
