# IREN — Overview

## Business

IREN Limited (Nasdaq: IREN; formerly Iris Energy Limited) is a vertically integrated owner and operator of grid-connected, renewable-powered data centers in North America. As of June 30, 2025 the business runs on two product lines: Bitcoin self-mining (the legacy revenue base) and AI Cloud Services (NVIDIA GPU compute leased to AI training/inference customers). A planned third line — Colocation Services for HPC/AI — is being built out at Childress (Horizon 1) and the Sweetwater sites.

The business model is "own the dirt, the grid connection, the building, and the silicon" — IREN holds **freehold land** (~500 acres at Childress, ~1,836 acres at Sweetwater, ~42 acres across three BC sites), executed grid connection agreements totaling **2,910 MW** of secured capacity (95% in Texas), and the ASIC/GPU hardware in the racks. The thesis is that vertical integration captures more margin than third-party hosting and provides operational control during the pivot from Bitcoin-only to mixed Bitcoin/HPC/AI workloads. (Source: 10-K FY2025, Item 1)

## Operating sites

| Site | Location | Capacity (MW) | Hashrate (EH/s) | Status |
|------|----------|--------------:|----------------:|--------|
| Canal Flats | British Columbia, Canada | 30 | 1.6 | Operating since 2019 |
| Mackenzie | British Columbia, Canada | 80 | 5.2 | Operating since Apr 2022 |
| Prince George | British Columbia, Canada | 50 | 3.1 | Operating since Sep 2022; AI Cloud GPUs deployed here |
| Childress (BTC mining) | Childress County, Texas | 650 | 40.1 | Operating since Apr 2023 |
| **Total operating** | | **810** | **50.0** | |
| Childress Horizon 1 | Texas | 75 (50 IT) | N/A (HPC/AI) | Under construction; direct-to-chip liquid cooled; energization targeted end of CY2025 |
| Sweetwater 1 | ~40 mi from Abilene, TX | 1,400 | N/A | Substation under construction; grid connection targeted Q2 CY2026 |
| Sweetwater 2 | ~40 mi from Abilene, TX | 600 | — | Connection agreement signed; targeted energization Q4 CY2027 |
| Childress Expansion | Texas | 25 | — | Power available |
| Additional pipeline | Multiple | >1,000 | — | Conditional/unconditional development rights |
| **Total announced** | | **>3,910** | | |

A direct fiber loop is designed between Sweetwater 1 and Sweetwater 2 — the explicit ambition is a **2 GW HPC/AI hub**. (Source: 10-K FY2025, Item 1 + Item 2 Properties)

## Power & energy strategy

- **British Columbia sites:** Connected to BC Hydro under regulated transmission tariff (Rate Schedule 1830). Energy charge $0.03845/kWh and demand charge $8.304/kVA as of June 30, 2025; 4.5% Deferral Account Rate Rider applied as discount. ~98% sourced from clean/renewable (hydro/wind/solar/biomass per BC Hydro), ~2% via REC purchase. Contracts are 1-year initial, extending until 6 months' notice.
- **Childress (Texas):** Deregulated market; participates in ERCOT wholesale spot since Aug 2024 (closed out fixed-price hedges at $7.2M cost in Aug-Sep 2024). Optimizes via demand response, ancillary services, and 4CP peak management. RECs purchased for 100% of consumption through June 30, 2025.
- **Regulatory headwind in BC:** December 2022 Government of BC announced 18-month suspension on new BC Hydro connection requests for crypto mining; extended another 18 months June 2024 (upheld on appeal). Existing operations not affected. (Source: 10-K FY2025, Item 1A)

## Bitcoin mining

- **Strategy:** "Non-HODL" — liquidates ~all mined Bitcoin daily via Kraken (with Coinbase as backup, unused as of June 30, 2025). No Bitcoin on balance sheet at fiscal year-end. Etana Custody handles fiat transfer.
- **Mining pools:** Antpool and Foundry as primary providers.
- **Pause in expansion:** IREN reached 50 EH/s of self-mining capacity by June 2025 and **announced a pause in further Bitcoin mining expansion** at that point. May reduce Bitcoin mining capacity if AI/HPC opportunities offer better shareholder value. (Source: 10-K FY2025, Item 1 — "Consider Bitcoin mining expansion opportunities")

## AI Cloud Services & HPC

- **Launch:** AI Cloud Services launched 2024 (revenue began Feb 5, 2024).
- **GPU fleet (as of June 30, 2025):** ~1.9k NVIDIA H100 + H200 GPUs, deployed at Prince George.
- **Subsequent procurement (post-FY25):** ~5.5k B200, ~2.3k B300, ~1.2k GB300 — to be installed at Prince George by end of CY2025, bringing total fleet to ~10.9k GPUs.
- **Q2 FY26 update (10-Q Dec 31, 2025):** ~99,900 GPUs **installed or on order** for IREN data centers — order book has scaled ~50× during the half.
- **Strategy:** Customer mix from on-demand to 3-year contracts, including white-labeled compute for leading US AI cloud providers.
- **Microsoft Agreement (Nov 2, 2025):** Dedicated GPU services in tranches at Childress, **5-year average term, total contract value ~$9.7 billion**, 20% paid prior to each tranche delivery. Reported in Q2 FY26 10-Q. As of Dec 31, 2025, no tranches had been delivered/accepted, so $0 in unsatisfied RPO recognized yet. (Source: 10-Q Q2 FY26, Note 5 Strategic Customer Agreement)
- **Dell GPU agreements (Mar 4, 2026):** $2.3B (Dell Canada → IE CA Leasing) + $1.2B (Dell USA → IE US Hardware) for GPUs delivering 2H 2026, payable in installments within 30 days of each tranche shipping; IREN parent-guaranteed. Total $3.5B order. (Source: 8-K filed 2026-03-04)

## Customers & competition

- **Stated competitors (Bitcoin mining):** Bitdeer (BTDR), Bitfarms (BITF), Cipher Mining (CIFR), CleanSpark (CLSK), Core Scientific (CORZ — historical), Hut 8 (HUT), MARA Holdings (MARA), Riot Platforms (RIOT), TeraWulf (WULF). Same set used in IREN's self-constructed peer group index in Item 5.
- **Stated competitors (AI Cloud / HPC):** Amazon Web Services, CoreWeave (CRWV), Crusoe Cloud, Google Cloud, Lambda, Microsoft Azure, Nebius, Oracle Cloud (cloud); Digital Realty, QTS, CyrusOne, Equinix, Vantage, Aligned (colocation).
- **Customer concentration:** AI Cloud Services has and is expected to continue to have **significant customer concentration** in early-stage and private AI companies. Microsoft is now an explicit named anchor customer (post-FY25).

## Hardware & supplier relationships

- ASIC supplier: Bitmain (referenced as long-standing partner).
- HPC/AI suppliers: Dell Technologies, Hunton Trane, Lenovo, NVIDIA, Supermicro, WekaIO.
- Utility partnerships: BC Hydro (Canada), AEP Texas (Childress).
- Tariff exposure: Historically sourced miners/equipment from China and Southeast Asia. April 2025 NOA from US Customs disputed country-of-origin on miners imported Apr 2024-Feb 2025 from Indonesia/Thailand/Malaysia — **potential additional tariff exposure of up to ~$100M** if challenge fails. April 2025 reciprocal tariffs and Aug 7, 2025 proposed 100% semiconductor tariff add ongoing cost risk. (Source: 10-K FY2025, Item 1A)

## Geography & employees

- **257 employees** (June 30, 2025) across US, Canada, Australia + ~200 contractors at US sites.
- **Office locations:** Sydney (principal executive — Level 6, 55 Market Street, NSW 2000); Childress, TX (operations); 1411 Broadway, NY (US office).
- **Non-current asset split (FY25):** 83% US / 17% Canada.

## Corporate identity

- **Originally incorporated:** November 6, 2018 as "Iris Energy Pty Ltd" (NSW, Australia, ACN 629 842 799).
- **Conversion:** Public company "Iris Energy Limited" October 7, 2021.
- **IPO:** November 19, 2021 on Nasdaq under "IREN".
- **Doing business as "IREN":** February 15, 2024.
- **Legal name change:** "IREN Limited" effective November 27, 2024.
- **FPI status loss:** As of December 31, 2024, IREN no longer met the foreign private issuer definition under US federal securities regs. Began filing 10-K (annual), 10-Q (quarterly), DEF 14A (proxy), Section 16 forms instead of 20-F + 6-K. First 10-K (FY2025) filed August 28, 2025; transitioned IFRS → GAAP for all reported periods.
- **Auditor (Australian/IFRS):** Referenced but not named in 10-K excerpt; Item 9 confirms no changes/disagreements with accountants.

## What's distinctive vs. the peer set

Three things show up repeatedly that differentiate IREN from the Bitcoin-miner peer group:

1. **Land + grid ownership at scale.** 2,910 MW of secured grid-connected capacity, 95% in Texas, with 80% of operating capacity owned-and-operated rather than leased. The Sweetwater 1+2 fiber loop and 2 GW design intent is more "AI hyperscaler infra" than "miner."
2. **The Microsoft Agreement.** A $9.7B 5-year named-customer contract for dedicated GPU services is the largest disclosed customer commitment among the public Bitcoin-mining peer set as of the Q2 FY26 reporting period.
3. **Australian incorporation + dual-class voting carryover.** Founders Daniel and William Roberts hold the only two B Class shares; together they control 43.5% of the voting power on a 4.6% economic stake (as of August 31, 2025). The 2025 DEF 14A proposes a classified board structure that would sunset starting 2030 AGM. (See `leadership.md` for governance detail.)
