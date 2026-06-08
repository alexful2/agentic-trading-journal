# Broader Price Triggers

> Not investment advice.

Price-only triggers for stocks **not** on `vault/watchlist.md`. The point
is to spot a good deal on a broader universe of names if it happens to
come by — not to replace the watchlist.

## How this file is used

- `check_price_triggers.py` parses the `## Price Triggers` table below,
  fetches current prices via yfinance, and any `FIRED_BUY` / `FIRED_TRIM`
  row becomes a **one-line bullet** in the daily report's
  `## Broader Price Triggers` section (above Macro awareness).
- This is intentionally a lighter treatment than watchlist fires. Watchlist
  tickers live in `vault/watchlist.md` and get the full sev-3 item format.
- Triggers **expire after 30 days** — if `Last Reviewed` is older than
  that, the trigger is marked STALE and does not fire. Same staleness rule
  as watchlist triggers (rationale: `memory/price_trigger_scope.md`).

## How rows get added

- **Auto (deep-dive)**: when `stock-deep-dive` runs on a ticker that is
  **not** in any tier of `vault/watchlist.md`, the skill upserts a row
  here using the ADD / TRIM levels from its Crux Events & Price Ladder.
  `Last Reviewed` becomes today's date; `Source` becomes a wikilink to
  that deep dive.
- **Auto (pre-earnings)**: when `pre-earnings` runs on a non-watchlist
  ticker AND surfaces a concrete long-horizon Buy Below / Trim Above
  level (rare — typically deep-dive's authority), it upserts using the
  same semantics. Most pre-earnings runs on non-watchlist tickers do
  not write here.
- **Manual**: add rows by hand for anything you want to opportunistically
  track. The file is intentionally designed to hold a wide net of names
  — including stocks you don't actively follow — so a good deal doesn't
  pass unnoticed. A `Source` is optional for manual rows.

## Table format

- Prices are plain numbers, no `$`. Use `—` for no trigger in that direction.
- `Buy Below` fires when price ≤ threshold. `Trim Above` fires when price ≥ threshold.
- `Funded-by` is short free-text capital source for Buy-side fires. Blank `—` if not specified.
- `Prefer-over` is a comma-separated list of tickers this buy should be funded before if both fire the same day. Used by `check_price_triggers.py` to flag capital-collision deferrals. Blank `—` if not specified.
- `Note` is free-form context — what the level represents.
- `Source` is a wikilink (e.g. `[[TICKER-YYYY-MM-DD]]`) to the deep dive
  that set the levels, or blank for manual entries.

## Price Triggers

| Ticker | Buy Below | Trim Above | Funded-by | Prefer-over | Last Reviewed | Note | Source |
| ------ | --------- | ---------- | --------- | ----------- | ------------- | ---- | ------ |
| RIVN   | 12        | —          | —         | —           | 2026-04-23    | Conditional on R2 Q1 delivery proof + no ATM | [[RIVN-2026-04-23]] |
| EOSE   | 6.00      | —          | cash      | —           | 2026-05-19    | Post-Frontier-deal wait-for-deal starter zone — 50 DMA + base FV + above 5/5 swing low; cohort-confirm before pulling. Replaces $5.50 (conditional on Q1 miss that didn't happen). | [[EOSE-2026-05-19]] |
| APLD   | 30        | —          | cash      | RIVN        | 2026-05-19    | 50 DMA + 200 DMA + bear FV cluster; Dip Buyer ACTIVE 5/19; cohort-drawdown OR 2026-07-15 Pre-Earnings window. Cloud spun off 5/5; bridge facility closed 5/4. | [[APLD-2026-05-19]] |
| CIFR   | 15        | —          | post-May-5 HNGE rotation | —    | 2026-04-20 | Post-May-5 print pullback; historical drawdown band + analyst-low cluster | [[CIFR-2026-04-20]] |
| NBIS   | 138       | —          | cash + post-May-5 HNGE rotation | —    | 2026-04-30 | Tranche 1 starter at current; tranche 2 at 125-130 cohort-red dip — Q1 in-line print + $725B capex confirmation closed Apr 20 gates | [[NBIS-2026-04-30]] |
| TWST   | 48        | 67         | cash      | —           | 2026-05-15    | Trigger fired today on -8.54% drop; ADD verdict. Post-print thesis confirmed (rev accel, Q4 breakeven, AWS partnership). Tranche 2 at $43 swing-low cluster. Trim at $67 = bull-FV cap. | [[TWST-2026-05-15]] |
| TEM    | 43        | —          | post-HNGE-$62-trim rotation | — | 2026-05-13    | Refined to swing-low cluster post-mixed-print; clean-print $48 invalidated (50 DMA broke + HCW PT $95→$64, BTIG $90→$80, Baird $68→$59); SOTP fair ~$25–31 per First-Principles; sub-$40 = thesis re-evaluation | [[TEM-2026-05-13]] |
| LITE   | 650       | —          | post-May-5 HNGE rotation | —    | 2026-04-28    | Post-May-5-print pullback only; Mar 30 swing low + below 50 DMA cluster; deeper-test starter at 558 (P/S bear) | [[LITE-2026-04-28]] |
| SNDK   | 800       | —          | post-May-5 HNGE rotation | LITE, APLD, INTC | 2026-04-30 | Cohort-confirmed cyclical-fear pullback only; 50 DMA + P/S bear cluster; behind AMZN GTCs and IREN Sweetwater | [[SNDK-2026-04-30]] |
| INTC   | 70        | —          | post-May-5 HNGE rotation | LITE, APLD | 2026-04-30 | Analyst-avg + P/S bear cluster + Bernstein/KeyBanc/Tigress zone; structural fit with the long-term AI-capex thesis; deeper add at 55 (50 DMA) on cohort drawdown | [[INTC-2026-04-30]] |
| VIVO   | 3.00      | —          | cash      | —           | 2026-05-15    | 50 DMA + recent swing-low cluster; conditional on open RFP still active + 0.5-1% Tier-3 sizing | [[VIVO-2026-05-15]] |
| TE     | 5.74      | —          | —         | —           | 2026-05-19    | 50 DMA + −2 ATR retrace; speculative US solar mfg, NOT AI-infra cohort. Requires thesis authored in library/ before pulling. | [[TE-2026-05-19]] |
| DGXX   | 5.40      | 11         | cash      | APLD        | 2026-05-19    | Post-Cerebras $1.1B MSA reset — P/S bear band; cohort-confirm req'd; 1-2% lottery sizing only; trim @ P/S bull | [[DGXX-2026-05-19]] |
| MARA   | 12        | —          | cash      | —           | 2026-05-31    | PRIMARY ACTION = 1-2% lottery starter NOW (asymmetric pre-deal; buy-below structure missed the cohort's deal runs — see [[MARA-2026-05-31]] base-rate note). Buy 12 here is the ADD-on-dip level (swing low $12.18 + 200 DMA $12.67); deeper $10.50 (50 DMA + bear FV) on BTC washout. Beta 5.43, cohort-confirm adds. Re-rate needs SIGNED tenant on Starwood/Long Ridge. | [[MARA-2026-05-31]] |

---

*Rows are written by `stock-deep-dive` Step 8b and `pre-earnings` Step 3m
for non-watchlist tickers, plus manual entries. The daily check
(`check_price_triggers.py`) reads this file; nothing else writes here at
runtime.*
