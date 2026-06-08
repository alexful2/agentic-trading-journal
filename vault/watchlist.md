> Not investment advice.

## How Tiers Work

- **Tier 1 — Core Holdings:** Searched every run (2 searches per ticker).
  These are stocks I actually own and have the most at stake in.
- **Tier 2 — Active Watchlist:** Searched every run but lighter (1 search
  per ticker). Stocks I'm seriously considering buying or closely tracking.
- **Tier 3 — Peripheral Interest:** No dedicated searches. Only shows up
  in reports if it surfaces in broad/thematic news. Stocks or sectors I
  want to keep a loose eye on.

---

## Tier 1 — Core Holdings

| Ticker | Company      | Why I Own It (brief)                                                       |
| ------ | ------------ | -------------------------------------------------------------------------- |
| HNGE   | Hinge Health | Digital healthcare platform, AI-powered MSK care                           |
| AMZN   | Amazon       | Cloud (AWS), AI infrastructure, e-commerce moat                            |
| IREN   | Iris Energy  | Bitcoin mining / AI data center infrastructure — see [[2026-04-19 IREN thesis]] |
| NBIS   | Nebius       | Multi-tenant GPU cloud / hyperscaler-capex play — see [[NBIS-2026-06-05]]   |
| CRWV   | CoreWeave    | GPU cloud / AI infrastructure pure play — see [[CRWV-2026-06-06]]           |

## Tier 2 — Active Watchlist

| Ticker | Company         | Why I'm Watching                                    |
| ------ | --------------- | --------------------------------------------------- |
| BE     | Bloom Energy    | Fuel cells for data center power, AI energy play    |
| CORZ   | Core Scientific | Mining-to-AI data center conversion; AI-infra power buildout |
| CBRS   | Cerebras Systems | Recent IPO — alt-compute lane vs. NVDA, large OpenAI contract anchor. Tier-2 during the IPO window for halt/news/8-K coverage; revisit tier placement once trading settles. |

## Tier 3 — Peripheral Interest

| Ticker | Company    | Loose Interest                                                       |
| ------ | ---------- | -------------------------------------------------------------------- |
| RKLB   | Rocket Lab | Reusable-launch cost-collapse play, vertical-integration pattern     |

---

## Alert Triggers (non-ticker)

Watch for these in broad/thematic searches — treat as severity ≥3 catalysts
for named holdings:

- **AI-lab power/compute deal.** Any new AI-lab partnership, large GPU
  procurement, or data-center power contract. Likely counterparties: CORZ,
  IREN, CRWV (compute), BE (on-site power). This is the wait-for-deal trigger
  for the AI-infrastructure cohort.

---

## Price Triggers

Pre-set price conditions. The daily run calls `check_price_triggers.py`,
which parses this table, pulls live prices, and any row where price crosses
the threshold becomes an automatic severity 3 item.

Triggers **expire after 30 days** — if `Last Reviewed` is older than that,
the trigger is marked STALE and does not fire. Update the date to re-confirm.

Format notes:
- Prices are plain numbers, no `$`. Use `—` for no trigger in that direction.
- `Buy Below` fires when price ≤ threshold. `Trim Above` fires when price ≥ threshold.
- `Funded-by` is short free-text capital source for Buy-side fires. Blank `—` on trim-only rows.
- `Prefer-over` is a comma-separated list of tickers this buy should be funded before if both fire the same day.
- `Note` is free-form context — what the trigger represents, what to check if it fires.

| Ticker | Buy Below | Trim Above | Funded-by              | Prefer-over | Last Reviewed | Note                                                                     |
| ------ | --------- | ---------- | ---------------------- | ----------- | ------------- | ------------------------------------------------------------------------ |
| BE | 245 | 398 | HNGE $62 trim tranche | — | 2026-05-30 | Mean target $260 − ~0.6 ATR; Dip Buyer zone (~24% off ATH). Spot $285 above mean target, no active preset — WATCH stands. Trim 398 = P/S bull band ≈ above analyst high. |
| CORZ | 20 | 30 | cash | — | 2026-05-30 | Post-financing/4.5GW standalone; dip-buyer reactivation $20 (swing low + 50 DMA); trim @30 = median target. |
| CRWV | — | 150 | cash | — | 2026-06-06 | HOLD refresh — fair value ($100.44 base FV) at 200 DMA; no standing buy-below (adds governed by $90 Conditional GTC tranche). Trim 150 above bull P/S band ($140.39) + new median $140. NVIDIA $2B equity at ~$138 = institutional mark. |
| IREN | 50 | 83 | HNGE $62 trim proceeds | — | 2026-06-07 | Refreshed 2026-06-07 — verdict HOLD at $54.35 (−12% cohort macro day: NFP +172K → 10Y 4.54%, chip selloff; NOT IREN-specific — B. Riley $96 / Canaccord $79 upgrades unabsorbed). Position OFF the 28% cap → ~22% on price, so Buy Below raised $46→$50 (50 DMA $49.89) = genuine add, ranked BEHIND NBIS underweight on opportunity-cost. Sub-$50 → ADD. Trim ladder $83/$100 stands. Crux = Aug-27 first MSFT RPO recognition. Break-even prob 73% (MC). |
| RKLB | 95 | — | cash | — | 2026-05-19 | Refreshed from stale $62 anchor; per [[RKLB thesis]] $80-95 base-FV zone; separate lane from AI-infra (cash-funded only). Alt triggers: Neutron static-fire failure OR Space Sys contract >$500M. |
| AMZN | 230 | — | cash | — | 2026-05-30 | Refreshed 2026-05-30: 200 DMA ($231.52) + Jan swing-low cluster; Dip Buyer preset activates here (~17% off ATH). 50 DMA has lifted to $246.67 but rung still well-supported. |
| HNGE | 47 | 62 | cash | — | 2026-05-19 | Buy 47 = 200 DMA + fwd-P/E bear FV ($46.84); Trim 62 = 52w high break + new base FV ($62.45). Resets stale $38/$58 from pre-rerate ladder. |
| NBIS | 200 | 290 | cash | BE | 2026-06-05 | Refreshed 2026-06-05 — verdict ADD (small starter now). Q1 (5/13) beat: rev $399M/+684%, ARR $1.92B, EBITDA ~45%; tape re-rated (Citi $287, Citizens $270). Stock −12% today on cohort macro selloff, 18% off $278.84 ATH = green-gate entry. Position underweight (6.9% vs 12–16%). Starter at market now + $200 add-on-dip; trims $290/$340. Q2 print Aug 6 = next fork. |
| CBRS | 185 | — | cash | — | 2026-05-14 | IPO floor entry — small starter for alt-compute optionality. Cohort-confirm before pulling. |

---

## Planned Tranches

Staged buy/sell plans for Tier 1/2 with an active position or near-term buy
intent. **Different from Price Triggers** — triggers are "alert me when price
crosses X"; tranches are explicit staged position-adjustment plans at known
levels.

Fired tranches (price crossed the level) surface as sev-3 items in the daily
alert, grouped with fired price triggers but labeled `[tranche]`. Fired rows
**stay in the table** until manually removed after execution. Expired rows
(where `Expires < today`) are stripped by `weekly-review` during consolidation.

Format notes:
- Prices are plain numbers, no `$`.
- `Action` is one of: `Buy` (fires when price ≤ At Price) or `Trim` (fires when price ≥ At Price).
- `Size` is free-form but keep it compact (e.g., `15% of pos`, `50 shares`, `$2k notional`).
- `Expires` is `YYYY-MM-DD`. A row with a past expiry is ignored by the daily check and cleaned up weekly.
- `Order`: `GTC` (place the limit order now, fire-and-forget), `Alert` (notify only — needs a human at fire), or `Conditional GTC` (place the GTC after a named condition; acts as `Alert` until then).
- `Note` is short free-form context.

Tranche rows are proposed by `stock-deep-dive`, `pre-earnings`, and `pre-ipo`
(via a `## Proposed Watchlist Updates` block) and applied at write-time via
`.claude/scripts/apply_watchlist_updates.py`.

| Ticker | Action | Size      | At Price | Expires    | Order           | Note                                                                  |
| ------ | ------ | --------- | -------- | ---------- | --------------- | --------------------------------------------------------------------- |
| CORZ | Trim | 25% of pos | 30 | 2026-09-30 | GTC | Median analyst target ($30) + near mean ($32.05); trim into thesis-confirming rip if a starter fills and the stock re-rates. |
| AMZN | Buy | 20 shares | 258 | 2026-08-15 | Alert | Tactical 2.1 ATR pullback; cohort-confirm per [[macro-cohort-confirmation]] before pulling (SPY flat-to-down, AI infra cohort not simultaneously red). |
| AMZN | Buy | 40 shares | 230 | 2026-12-31 | GTC | High-conviction long-horizon — 50/200 DMA + Jan swing low cluster; Dip Buyer pattern activates here (+42d 72.7% win rate avg +7.9% historically). Brings position to 100 sh / ~$25,200 cost / ~25% portfolio if it fills. |
| HNGE | Trim | 200 shares | 62 | 2026-09-30 | GTC | First post-rerate trim: 52w high break + new base FV ($62.45); 1,100→900 |
| HNGE | Trim | 200 shares | 72 | 2026-09-30 | GTC | Mid-rerate trim: new analyst median $70 + above bull P/S band ($76.85); 900→700 |
| HNGE | Trim | 200 shares | 85 | 2026-12-31 | GTC | Stretch trim: above new fwd-P/E bull FV ($78.06), midway between analyst mean ($70) and high ($95); 700→500 core |
| CRWV | Buy | 50-70 sh (~$5,000-$6,300) | 90 | 2026-08-15 | Conditional GTC | Re-gated conviction add: only if $3B converts price strike <$120 OR cohort-weakness extends (10Y>4.5% sustained + chip selloff) with thesis intact. Behaves as Alert until the convert 8-K. From [[CRWV-2026-06-06]]. |
| CRWV | Trim | 50 sh | 150 | 2026-12-31 | GTC | First profit-take above bull P/S band ($140.39) + median ($140). From [[CRWV-2026-06-06]]. |
| CRWV | Trim | 80 sh | 175 | 2027-03-31 | GTC | Second trim — requires H2 op-income ramp printing OR third hyperscaler anchor. From [[CRWV-2026-06-06]]. |
| CBRS | Buy | 20 sh (~$3,700) | 185 | 2026-08-15 | Alert | First starter — IPO offer floor; cohort-confirm per [[macro-cohort-confirmation]] before pulling. Underwriter stabilization typically active first ~30 cal days. |
| CBRS | Buy | 30 sh (~$4,500) | 150 | 2026-11-30 | Alert | Second tranche — raised-range midpoint zone; requires real give-back (lockup digestion start, Q2 miss, or macro selloff). Position cap at ~50 sh / 3-4% of portfolio combined. |
| RKLB | Buy | $10k starter (~100 sh) | 95 | 2026-09-30 | Alert | Per [[RKLB thesis]] entry plan — small starter from CASH only (not AI-infra rotation); cohort-confirm + check whether macro risk-off OR a Neutron event drove the trigger before pulling. Separate lane from AI-infra capital queue. |
| BE | Buy | 5–8% starter | 245 | 2026-07-31 | Alert | Mean target − 0.6 ATR; first Dip Buyer-zone entry. Cohort-confirm per [[macro-cohort-confirmation]]; fund from HNGE $62 trim. |
| BE | Buy | 5–8% conviction add | 200 | 2026-07-31 | Alert | P/S bear band ($199.75); requires real risk-off (SPY −5%+ given beta 3.83). Cohort-confirm. |
| CORZ | Buy | 5-8% starter | 20 | 2026-08-15 | Alert | Primary starter — dip-buyer reactivation (swing low $19.56 + 50 DMA $20.43); cohort-confirm. Duplicative of IREN + CRWV-counterparty exposure — opportunity-cost check before pulling. |
| CORZ | Buy | second tranche | 17 | 2026-08-15 | Alert | At 200 DMA ($17.75) / bear P/S band ($18.75); requires broad cohort/BTC washout. Floor-less post-merger-rejection, so size small. |
| IREN | Trim | ~60 sh | 83 | 2026-08-15 | GTC | First thesis-confirmation trim — ≈ analyst median $82.5, above NVIDIA $70 warrant strike; ~10% of position. From [[IREN-2026-06-07]]. |
| IREN | Trim | ~100 sh | 100 | 2026-12-31 | GTC | Second trim — ≈ Cantor $99 / B. Riley $96, ~21% below analyst high $126. From [[IREN-2026-06-07]]. |
| NBIS | Buy | 50 sh (~$10,000) | 200 | 2026-08-06 | Alert | Fade entry to close the underweight — swing low $191.82 + 1.5 ATR below spot + sub-mean entry; cohort-confirm; cash-funded. → 90 sh / ~14% = upper blank-slate. From [[NBIS-2026-06-05]]. |
| NBIS | Trim | 10 sh | 290 | 2026-12-31 | GTC | First thesis-confirmation trim — ≈ Goldman pre-print $291 zone, below bull P/S FV $323.64; light (position small + underweight). From [[NBIS-2026-06-05]]. |
| NBIS | Trim | 20 sh | 340 | 2026-12-31 | GTC | Second trim — above bull P/S FV $323.64, ~11% below analyst high $380; keeps a structural-insurance core. From [[NBIS-2026-06-05]]. |
| IREN | Buy | ~60-90 sh (~$3,000-$4,500) | 50 | 2026-08-15 | Alert | Primary cohort-red add — 50 DMA $49.89 + 6/05 "$50 reassess" line; HNGE-trim-funded, RANKED BEHIND NBIS $200 fill (opportunity-cost). Position off-cap (~22%). Sub-$50 on clean non-IREN-specific tape flips verdict to ADD. From [[IREN-2026-06-07]]. |
| IREN | Buy | ~50-70 sh (~$2,500-$3,500) | 46.5 | 2026-08-15 | Alert | Deeper washout rung — 200 DMA $46.77 + 5/19 swing low $47.74; broad cohort wash only, do-not-buy checklist clean. From [[IREN-2026-06-07]]. |

---

*Last updated: 2026-06-07*
