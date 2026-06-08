---
type: ipo-calendar
last_updated: 2026-06-05
---

# IPO Calendar

> Not investment advice.

Upcoming IPOs (and recent ones still in the lockup/quiet-period window) that
fit my AI-infrastructure thesis or have otherwise surfaced as worth tracking.

**Populated by:** `vault-curator` (Friday IPO Radar step) and manual entries.
**Read by:** `news-analyst` (daily — surfaces a one-liner reminder when an IPO
is ≤7 trading days out or ≤1 trading day out, mirroring the earnings reminder).
**Skill runs:** `pre-ipo TICKER` writes to `vault/reports/pre-ipo/` and updates
the `Skill Run` column here.

> Not a buy list. The calendar's job is to make sure the date doesn't sneak
> up; the `pre-ipo` skill is the research layer that decides whether to act.

---

## Status legend

| Status | Meaning |
|---|---|
| `30+ days out` | ≥30 calendar days from expected pricing |
| `this month` | <30 calendar days |
| `this week` | <7 calendar days — **news-analyst surfaces reminder** |
| `priced` | Pricing announced; opens within 1–2 trading days — **gate-mode reminder fires** |
| `trading` | Has begun trading; quiet-period clock running |
| `quiet-period` | Within first 25 trading days post-IPO |
| `lockup-soon` | Within 30 days of 180-day lockup expiry |
| `passed` | Trading period over for skill purposes; safe to remove on next curator run |
| `pulled` | IPO withdrawn or postponed indefinitely |

---

## Calendar

| Ticker | Company | Expected Date | Range | Lead UW | Sector | Thesis Fit | Status | Skill Run | Source |
|--------|---------|---------------|-------|---------|--------|------------|--------|-----------|--------|
| CBRS | Cerebras Systems | 2026-05-15 | $115–$125 | Morgan Stanley / Citigroup / Barclays / UBS | AI infra (compute) | High — alt-compute lane vs. NVDA, $20B OpenAI contract anchor (750 MW through 2028) | quiet-period | none | [[wiki-2026-W19]] (S-1/A May 4 2026: 28M shares + 4.2M overallotment, $3.5B raise high-end, $26.6B implied valuation, NASDAQ CBRS; began trading 2026-05-15, day-1 +84%) |
| TBD | VoltaGrid | TBD | TBD | TBD | AI infra (power) | High — power-constrained data center thesis; gas microgrid lane | 30+ days out | none | Manual seed 2026-04-25 + [[wiki-2026-W18]] (Bloomberg Feb 24 2026: weighing IPO or sale; BX/BLK among bidders; ~$10B+ valuation; $5B financing closed; 4.3GW contracted plan through 2028) |
| TBD | Fervo Energy | TBD | TBD | TBD | AI infra (power) | High — geothermal 24/7 firm clean power; pursuing multi-GW hyperscaler offtake; 658MW PPAs already signed | 30+ days out | none | [[wiki-2026-W18]] (S-1 filed; 500MW Cape Station first power late 2026; permits for 1.5GW additional; SCE + Shell PPA anchors) |
| TBD | Anthropic | 2026-10 | TBD | Goldman Sachs / JPMorgan / Morgan Stanley (preliminary) | AI orchestration | Medium-High — relevant to AMZN ~$33B stake + [[orchestration-vs-substrate]]; reads on AWS/Trainium dependency in S-1 | 30+ days out | none | [[wiki-2026-W18]] (AInvest Mar 27 2026: Oct 2026 target, $60B+ raise, $380B Feb valuation, $50B data-center build use of proceeds) |
| TBD | QumulusAI | TBD | TBD | TBD | AI infra (GPU cloud) | Medium — wait-for-deal lane; behind-the-meter gas / 21k Blackwell GPU target by EOY 2026; pre-IPO, no named hyperscaler contract yet | 30+ days out | none | [[wiki-2026-W18]] (Apr 28 2026: $45M ATW convertible note on top of $500M Permian Labs / USD.AI blockchain-backed financing; targeting 100MW behind-the-meter natural gas) |
| SPCX | SpaceX (merged with xAI Feb 2026) | 2026-06-12 | $1.75T valuation / $75B raise (per-share TBD at Jun 11 pricing) | TBD | Space / launch + xAI (AI/data) | Medium-High — [[Space Race]] thesis anchor + xAI merger adds AI-data flywheel; RKLB comp; $1.75T is 109–116× 2025 revenue; roadshow Jun 4 | this week | none | [[wiki-2026-W21]] (S-1 filed May 20 2026; Nasdaq SPCX; Jun 12 debut; roadshow Jun 4 — pre-ipo analysis window NOW as of 2026-05-29; SpaceX-xAI merged Feb 2026; Starlink 9M+ users, ~$15–16B Starlink revenue 2025; dual-class Musk 85.1% voting control) |
| TBD | Nscale | 2026-H2 | TBD | Goldman Sachs / JPMorgan | AI infra (GPU cloud) | High — NVIDIA-backed, no hyperscaler deal yet, CoreWeave-lane pre-deal profile; IPO creates public wait-for-deal entry | 30+ days out | none | [[wiki-2026-W19]] (March 2026: $14.6B valuation; GS + JPM engaged; 2H 2026 IPO target; Crunchbase 2026 IPO list) |
| TBD | X-energy | TBD | TBD | TBD | AI infra (nuclear power) | Medium-High — Amazon 960 MW anchor (~$50B); advanced SMR commercialization; IPO path likely post-Amazon de-risk; first power ~2029–2030 | 30+ days out | none | [[wiki-2026-W19]] (IAEA Bulletin + IEEE Spectrum 2026; Amazon–X-energy partnership confirmed) |
| TBD | Lambda Labs | 2026-H2 | TBD | Morgan Stanley / JPMorgan / Citi | AI infra (GPU cloud) | High — CoreWeave-lane pre-deal profile; NVIDIA-integrated; no named hyperscaler anchor yet; IPO creates public wait-for-deal entry | 30+ days out | none | [[wiki-2026-W19]] ($5.9B valuation after Nov 2025 Series E; H2 2026 IPO target reported; bankers engaged: MS/JPM/Citi confirmed 2026-05-29 search; 10,000+ research team users; GPU cloud, deep NVIDIA integration; NVIDIA leases back ~$1.5B of GPU capacity from Lambda; closest structural analogue to CRWV pre-IPO) |
| TBD | Verda (formerly DataCrunch) | TBD | TBD | TBD | AI infra (GPU cloud / EU sovereign) | High — NVIDIA Preferred Partner; Nordic clean power; pre-hyperscaler-deal EU sovereign AI lane; CoreWeave-lane in Europe | 30+ days out | none | [[wiki-2026-W19]] (Apr 24 2026: €100M / $117M raise led by Lifeline Ventures; cash-flow positive; $60M+ revenue run-rate; 100% Nordic hydro power; expanding to UK/US; no named hyperscaler deal yet) |
| TBD | Crusoe Energy | 2026-Q4 | TBD | Goldman Sachs (reportedly) | AI infra (compute + power) | High — "AI factory" model owning both GPU compute and power layers; 900 MW Microsoft Abilene TX campus confirmed; reportedly OpenAI customer; integrated lane distinct from pure GPU cloud or pure power plays | 30+ days out | none | [[wiki-2026-W20]] (Series E $1.375B at >$10B valuation Oct 2025; Mar 2026 Axios: targeting $40B valuation, GS engaged; Michael Gordon ex-MongoDB IPO CFO joined Dec 2025; Q4 2026 IPO target; sources: dealroom.net, accessipos.com, sacra.com) |
| ROZE | SoftBank Roze | 2026-H2 | TBD / ~$100B valuation target | Goldman Sachs / JPMorgan / Mizuho / Morgan Stanley | AI infra (construction + robotics) | Medium — autonomous robots + SoftBank infrastructure assets building AI data centers; construction layer of the picks-and-shovels thesis; not directly power or compute | 30+ days out | none | [[wiki-2026-W23]] (CNBC Apr 30 2026; TechCrunch Apr 29 2026; SoftBank announced banks May 26 2026; bundles ABB Robotics + energy/land assets; Masayoshi Son driving; targets H2 2026 US debut) |
| TBD | SoftBank SB Energy | 2026-H2 | TBD | TBD (banks engaged alongside Roze, May 26 2026) | AI infra (power / utility) | High — SoftBank US renewable energy subsidiary; 9.2 GW natural gas generation planned at Portsmouth, OH for 10 GW Stargate data center campus; utility-scale power for hyperscaler DC demand | 30+ days out | none | [[wiki-2026-W23]] (US News May 26 2026; DOE partnership Feb 2026; SoftBank announced IPO intentions alongside Roze; distinct from Roze — energy supply, not construction) |

---

## Field conventions

- **Ticker:** the proposed ticker from the S-1 if available (e.g., `VLT`),
  otherwise `TBD`. Once trading begins, replace with the live symbol.
- **Expected Date:** ISO `YYYY-MM-DD` for pricing/opening day if known;
  `TBD` if only a window is rumored. Update as the date firms.
- **Range:** the latest indicated price range (e.g., `$20–22`); update on
  S-1/A amendments and pricing announcements.
- **Lead UW:** lead bookrunner(s). Tier-1 (GS / MS / JPM / BofA) matters
  for the day-1 demand read.
- **Sector:** short tag — `AI infra (compute)`, `AI infra (power)`,
  `AI infra (DC)`, `digital health`, etc.
- **Thesis Fit:** one short phrase + score. `High`, `Medium`, `Low`, or
  `Not relevant`. The phrase should name the angle (e.g., `power-constrained
  data center thesis`).
- **Status:** from the legend above.
- **Skill Run:** `none` / `initial YYYY-MM-DD` / `gate YYYY-MM-DD`. Most
  recent run only; the file in `vault/reports/pre-ipo/` is the artifact.
- **Source:** wikilink to the curator suggestions file that surfaced it
  (`[[wiki-YYYY-WW]]`), the article URL, or `Manual seed YYYY-MM-DD`.

---

*Last updated: 2026-06-05 — vault-curator [[wiki-2026-W23]] sync: SPCX status updated
`this month` → `this week` (pricing Jun 11, 6 calendar days). Added Roze (SoftBank AI
robotics/construction, H2 2026, $100B target, GS/JPM/MS/Mizuho) and SB Energy (SoftBank
utility power subsidiary, H2 2026, banks engaged alongside Roze). No passed rows removed.*
