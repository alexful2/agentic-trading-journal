# IREN — Risks

Distilled from 10-K FY2025 Item 1A (filed 2025-08-28). Tiered by materiality to the *current* business posture (mid-FY26, post-Microsoft/Dell deals, post-Dec 2025 capital raise).

## Tier 1 — Most material to thesis

### 1.1  Bitcoin price + halving sensitivity
The Bitcoin Mining segment is still the revenue base (~94% of FY25 revenue, ~94% of H1 FY26 revenue). Bitcoin price is volatile and correlates with macro risk-on flows. Block reward halves to **1.5625 BTC/block in approximately April 2028** — IREN explicitly flags that Bitcoin price may not adjust to compensate for the reduction. Difficulty growth from competing miners further compresses per-EH economics. Specific to IREN: the non-HODL strategy means daily liquidation at spot — they don't get the upside of holding through a rally beyond a single trading day. (Source: Item 1A — Risks Related to Bitcoin)

### 1.2  AI Cloud customer concentration + counterparty risk
AI Cloud revenue is concentrated in a small number of customers, "many of whom are in their early stages and/or private companies, predominantly operating in the AI sector, that may have increased risk of insolvency, bankruptcy or other issues impacting their creditworthiness." After the November 2025 Microsoft Agreement ($9.7B / 5-year), Microsoft is now an explicit named anchor. **The risk profile has shifted from many-small-AI-companies to a barbell of one anchor + tail.** Counterparty default by Microsoft, or Microsoft electing not to take subsequent tranches, would be catastrophic to the AI Cloud trajectory. As of Dec 31, 2025 no Microsoft tranches had been delivered/accepted, so the contract is fully forward-looking. (Source: Item 1A — Risks Related to Third Parties)

### 1.3  Capital intensity + dilution overhang
IREN consumed $1.38B in investing cash in FY25 and $1.13B in H1 FY26 alone. Funding has come from a combination of:
- ATM equity sales (~$1.0B raised through Dec 31, 2025 via 66.7M new shares; current prospectus exhausted, more to be registered)
- Convertible note issuances ($400M + $500M + $1.0B + $1.15B + $1.15B = $4.2B aggregate at issuance, partially offset by ~$1.6B Dec buyback)
- Equity offering Dec 8, 2025 (39.7M shares at $41.12)

Share count has gone from 187.9M (June 2024) to **332.3M (January 2026)** — a 77% increase in 18 months. Convertibles on the balance sheet at Dec 2025 conversion prices of $51.40 (2032 + 2033) and $85.63 (2031) imply **further dilution overhang** if shares run. Capped calls reduce but do not eliminate this. The Dell $3.5B GPU purchase commitment (Mar 4, 2026) and ongoing data center construction will require **additional capital raises** — management is "actively exploring alternative financings."

### 1.4  Power supply / grid policy / Texas cluster risk
95% of secured power capacity is in Texas (Childress + Sweetwater 1 + Sweetwater 2). This is a deliberate concentration but creates regulatory/policy and weather exposure:
- ERCOT participation depends on ongoing political support; Texas legislature periodically reviews data-center grid impact
- Severe weather events (Uri-style) can cause electricity outages or massive spot-price spikes
- Energy-intensive AI/Bitcoin operations are increasingly the focus of state and federal energy regulator scrutiny
- BC suspension on new BC Hydro crypto mining connections is a precedent for jurisdiction-level shutdowns

### 1.5  Hardware supply + tariff exposure
- US Customs NOA April 2025 — country-of-origin dispute on Bitcoin miners imported Apr 2024-Feb 2025 from Indonesia/Thailand/Malaysia. **If IREN loses, additional tariffs of up to ~$100M.**
- Aug 7, 2025 proposed 100% semiconductor tariff would directly impact GPU procurement costs (IREN already has $3.5B in Dell GPU orders for 2H 2026 delivery — exact tariff treatment depends on final import classification).
- April 2025 reciprocal tariffs already imposed — costs of subsequent procurement higher.
- Few suppliers for high-end GPUs (NVIDIA pipeline) — supply allocation risk.

### 1.6  Execution risk on AI/HPC pivot at scale
IREN explicitly states limited experience in HPC/AI services. The pivot involves:
- Building direct-to-chip liquid cooled facilities (Horizon 1 → Horizon 2/3/4)
- Connecting Sweetwater 1 (1,400 MW; targeted Q2 CY2026 substation energization) and Sweetwater 2 (600 MW; Q4 CY2027) with the planned 2 GW fiber loop
- Standing up customer-facing AI Cloud operations at scale
- Transitioning BC sites from Bitcoin to AI Cloud (impairment $48M H1 FY26 partly reflects this)

Schedule slips, cost overruns, or technical execution failure would materially compress the AI revenue ramp.

## Tier 2 — Standard but material

### 2.1  Convertible debt covenants & cross-default
IREN now has 5 series of convertible notes (excluding the partially repurchased 2029/2030 portions). Cross-default provisions across the indentures plus equipment-lease guarantees create a tightly coupled capital structure. Significant subsidiary defaults of $100M+ trigger note acceleration.

### 2.2  Equipment leasing parent guarantees
Existing equipment leases use non-recourse SPVs but **are guaranteed by IREN Limited**. The Nov 2025 Dell Financial Services $199.8M lease is parent-guaranteed. The Mar 2026 Dell USA + Dell Canada $3.5B GPU purchase agreements are parent-guaranteed. If the SPV-level cash flows underperform (insufficient AI Cloud demand), the lessor can call on IREN parent — same structural problem as the NYDIG default triggered in 2022.

### 2.3  NYDIG legacy litigation closure
Settlement signed Aug 12, 2025 but **not yet effective** as of 10-K FY25 filing. Effectiveness requires court approval of dismissal/termination of Australian Recognition Proceedings, Canadian Receivership Proceedings, and Canadian Bankruptcy Proceedings. Bankruptcy steps expected to take ~6 months to finalize. Settlement payment includes $18.2M in excess of prior accruals.

### 2.4  Securities class action (NJ District Court)
Pending putative class action filed Dec 2022, second amended complaint Nov 2024, motion to dismiss fully briefed and pending. Claims tied to 2021 IPO disclosures and Nov 2021–Nov 2022 statements. IREN believes claims are without merit; outcome unpredictable. Damages unspecified.

### 2.5  Canada CRA permanent-establishment + GST dispute
- IREN filed Notice of Appeal with Tax Court of Canada (June 23, 2025) disputing CRA's determination that IREN has a Canadian PE and the related GST assessment.
- Ongoing CRA audit on GST/HST input tax credits — unfavorable outcome reduces historical credits and going-forward recoveries on Canadian inputs (electricity, hardware, services).

### 2.6  Regulatory environment for digital assets
The CLARITY Act (passed House July 2025) and GENIUS Act (signed July 2025 — federal stablecoin law) signal a shifting US framework. Trump executive orders March 2025 (Strategic Bitcoin Reserve + Digital Asset Stockpile) are favorable on net but the regulatory dust hasn't settled. State-level licensure regimes (CA DFAL, NY BitLicense, LA, etc.) and possible "money transmitter" reclassification of mining-pool-related activities create incremental compliance cost risk.

### 2.7  Bitcoin proof-of-work obsolescence
Risk-factor explicitly flagged: a transition from PoW to PoS validation on the Bitcoin network would significantly impair the value of IREN's mining-specific capex (ASICs, cooling, power infrastructure tuned for SHA-256). Probability is low near-term but the asset stranding risk is total.

### 2.8  Stock-based compensation magnitude
Stock-based compensation expense was $42.6M in FY25 and **$130.6M in just H1 FY26** — running at ~30% of revenue. This funds executive comp (see `compensation.md`) and broader headcount but is direct economic dilution.

## Tier 3 — Lower-likelihood / harder-to-affect

- **Climate / extreme weather** affecting operations, especially Texas heat and Canadian winter
- **Cybersecurity** (Item 1C disclosure)
- **AI Act / state AI regulation** affecting customer demand or IREN as infrastructure provider
- **OTC trading desk disruption** affecting Bitcoin liquidation
- **Banking partner risk** (post-SVB era)
- **Australian incorporation governance differences** (different shareholder rights vs. Delaware/US incorporation; classified board proposal in 2025 DEF 14A would entrench)

## Risks NOT in 10-K Item 1A but worth tracking

These don't appear as standalone risk factors but matter to the thesis:

1. **Contract value vs. revenue recognition lag.** The $9.7B Microsoft contract has $0 in unsatisfied RPO recognized as of Dec 31, 2025 because no tranches have been delivered/accepted. Markets tend to anchor on the headline number; the realized P&L will lag by at least 12-24 months as Childress Horizon 1+ comes online.

2. **2 GW Sweetwater hub is not yet energized.** Sweetwater 1 substation targets Q2 CY2026; Sweetwater 2 targets Q4 CY2027. Multi-year construction risk on the most strategic assets.

3. **Dilution math.** At Dec 31, 2025 share count of ~311.7M (post Dec equity offering), the convertibles add ~28M (2032 max conversion) + 28M (2033 max conversion) + 11.7M (2031 conversion at initial rate) = ~67.6M potential additional shares from converts alone. Plus uncapped ATM authority (current supplement exhausted but more to be registered). A bull-case stock run accelerates conversion and dilution.

4. **Founder concentration of voting power.** Roberts brothers control 100% of B Class shares = 43.5% voting power on 4.6% economic. Classified board structure proposed in 2025 DEF 14A (sunset 2030 AGM) further entrenches.

5. **Hyperscaler-as-customer competitive risk.** IREN's customer set now includes Microsoft, while named competitors include Microsoft Azure, AWS, Google Cloud. The line between "infrastructure supplier to hyperscalers" and "competitor to hyperscalers" matters for future contract terms and pricing power.
