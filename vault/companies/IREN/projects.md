# IREN — Projects (mosaic research)

**Purpose:** Track real-world execution against IREN's site portfolio using public, indirect signals (mosaic theory). Distinct from `_meta.md` / `financials.md` — those are SEC-sourced. This file synthesizes press releases, grid filings, permits, satellite, hiring, and freight data to answer: *is the buildout actually progressing on the schedule management is claiming?*

**Last refreshed:** 2026-05-11 (deep-channel mosaic refresh; prior refresh 2026-05-07 was post-Q3 FY26 print but did not pull all named channels)
**Next refresh suggested:** after Horizon 1 Microsoft handoff (target Q3 CY26 = Jul-Sep 2026) — that's the inflection point where management's claimed schedule meets first contracted revenue. Quarterly otherwise.

**Refresh discipline note (2026-05-11):** This refresh pulled the full channels-watchlist set (~25 channels across SEC, ERCOT, TDLR, county records, LinkedIn site hiring, BC Hydro, Spanish regulatory, AEMC Australia, NVIDIA-counterparty, Mirantis-side validation, competitive context at Abilene/Sweetwater). Prior refresh missed: $11.9B commitments cliff disclosed in 10-Q Note 21, Nostrum EUR 165M price (10-Q subsequent events), Roberts brothers post-Sep-11 Form 4 silence as positive credibility signal, Aterio satellite confirmation of Horizon 3-4 status, IE US Development Holdings 3 Texas Comptroller record, Childress Reinvestment Zone #2 (Oct 2024) Chapter 312 expansion, Spain regulatory headwind (Red Eléctrica denial for CC Green), AEMC draft rule for Australian connections (March 2026), BC Hydro Jan 30 2026 competitive process for AI data centers. All folded below.

---

## Variable Map (Research Design)

**Last reviewed:** 2026-05-11
**Map maturity:** `searched` — ~25 channels actually pulled and known-noisy channels documented in the Search Coverage Ledger. Not yet `mature`: the existing 2026-05-11 Codex audit predated the Variable Map coverage check, so a later audit must explicitly validate map fit + ledger coverage before upgrading.
**Patterns:** Physical buildout + Capital structure dependency + (emerging) Hyperscaler concentration
**Map seed:** Q3 FY26 10-Q (2026-05-07), deep-channel mosaic refresh 2026-05-11, prior projects.md (2026-05-07), _meta.md (2026-04-25), the prior IREN deep-dive and thesis work, and tranche-execution notes.

### Execution model

IREN's revenue conversion path: secure land + grid capacity → build data center shells + electrical infrastructure → install GPUs (~$14-16M per IT MW at Childress) → reach delivery acceptance for named hyperscaler/anchor customer → recognize contracted revenue. **Binding constraints, in order of where execution can break:** (1) capital availability — the $11.9B 12-month commitments cliff (10-Q Note 21) vs. funded stack ($2.2B cash + $1.94B MSFT prepay + $3.6B Goldman/JPM commitment letter pending close + $2.0B+ convertibles in flight + ATM at ~$680M/month) is the dominant near-term variable; (2) construction pace at Childress + Sweetwater 1 — Aterio satellite, county permits, TDLR records, LinkedIn site hiring all corroborate; (3) customer concentration risk — MSFT is the marquee anchor, NVIDIA second customer, $3.7B ARR target assumes $1.8B "estimated" beyond contracted; (4) Sweetwater 2 / Kiowa 2028+ ramp execution and Spain regulatory headwind for Nostrum sites. **Bear-case shape this map needs to test:** dilution spiral (commitments cliff outpacing funding), Goldman/JPM commitment letter failing to close to definitive agreement, $3.7B ARR composition slips on the $1.8B "estimated" portion, Sweetwater 2 substation slips beyond 2027 with no S2 contractor signal.

### Active execution variables

| Variable | Binding constraint | Bull tell | Bear tell | Primary channels | Known-noisy channels | Pattern | Next refresh question |
|---|---|---|---|---|---|---|---|
| **Childress capacity ramp (Horizons 1-4)** | Construction pace at primary revenue site | Q1 FY27 print (~Aug 2026) shows first MSFT delivery acceptance + unsatisfied RPO recognition | No RPO recognition at Q1 FY27 + slip language; Aterio satellite shows static or contractor PR drop-off | SEC 8-K item disclosures, Aterio/Sentinel-2 satellite, TDLR TABS records under IE US Development Holdings 3, Childress County permits, LinkedIn hiring at Tier-III mission-critical depth | General TX flatbed trucking rates (too macro), generic ERCOT load forecasts (don't isolate IREN) | Physical buildout | Did Q1 FY27 print recognize first MSFT revenue tranche? |
| **Sweetwater 1 200MW IT load Phase 1** | Second campus construction; first non-Childress execution proof | Sweetwater-specific TDLR record surfaces (currently none); Fisher County substation permits filed; named customer contract signed for 2027 capacity | No S1-specific TDLR or Fisher County permits by Aug 2026; "capacity available 2027 is extremely scarce" language hardens into named slip | Fisher County records, Taylor Electric Coop INC filings (S1 distribution utility), AEP Texas (transmission), TDLR TABS by site, ConstructConnect tracker | Hobbs Holler local blog (Tier C; useful but not authoritative), datacenter.fyi entries (database, not regulatory) | Physical buildout | Has Sweetwater 1 commissioning date been disclosed yet? |
| **Sweetwater 2 + Kiowa 2028 ramp** | Long-horizon capacity vs. mgmt's "ramp from 2028" framing | iren.com site page updated from "2027 Substation Energization" to match Q3 deck "2028" framing (closes disclosure mismatch); Q4 FY26 print provides Kiowa specifics | iren.com still lists 2027; no Fisher County or Kiowa OK construction signals by Q4 FY26 print; "remaining" Sweetwater capacity slips again | iren.com site pages (direct check), Q4 FY26 print + transcript, Fisher/Nolan County records, Kiowa OK county records, SPP grid filings | "Kiowa" name (codename vs. location ambiguity — verify in next print) | Physical buildout | Did Q4 FY26 print clarify whether S2 substation is still 2027 or now 2028? |
| **Capital execution: commitments-vs-funding race** | $11.9B 12-month commitments must be funded without distress | $2.0B convertibles price within Dec 2025 range (0.25%/1.00% coupons, 25% conversion premium); Goldman/JPM commitment letter converts to definitive agreement at full size; no covenant breaches | Convertibles price with materially higher coupon or lower conversion premium; Goldman/JPM fails to close to definitive at $3.6B; ATM acceleration above $700M/month (forced dilution) | SEC 8-K Item 2.03 (convertibles pricing), Item 1.01 (Goldman/JPM definitive), Item 8.01 (offerings), 10-Q quarterly capital filings, Form 4 (insider context) | News-aggregator "dilution" headlines (often stale); third-party convertible commentary (often misframed) | Capital structure | Did Goldman/JPM commitment letter convert to executed definitive agreement? |
| **Customer concentration / hyperscaler dependency** | Microsoft + NVIDIA together = ~$2.6B of $3.1B ARR under contract; $1.8B of $3.7B is "estimated" | NVIDIA Q1 FY27 (May 20 call) mentions IREN partnership scope; named additional hyperscaler signing for Sweetwater or remaining 2026 capacity (~50k air-cooled GPUs uncontracted) | NVIDIA Q1 FY27 silent on IREN; no new named hyperscaler by Q1 FY27 print; Microsoft RPO recognition slips beyond Q1 FY27 | SEC 8-K Item 1.01 for new material contracts, NVIDIA earnings calls, Microsoft earnings calls, customer-side PRs, hyperscaler counterparty press | Generic "AI demand strong" macro coverage (doesn't validate IREN specifically) | Hyperscaler concentration (emerging) | Did any new named customer sign for the remaining 2026 capacity? |
| **Roberts brothers governance / insider behavior** | Founder credibility — Sep 2025 non-10b5-1 sales pre-MSFT-deal flagged a pattern | No further Form 4 sales filed (current state — quietly positive); 10b5-1 plan adoption disclosed (most credible exit) | New non-10b5-1 sale Form 4 filed at $70+ stock price; large registered-direct via Roberts-controlled vehicle | SEC EDGAR Section 16 (Roberts Daniel John CIK 0001909120, Roberts William Gregory CIK 0001909308), Awassi Capital Trust #1 filings | Anti-dilution proxy votes (different governance issue from selling pattern) | (cross-pattern: Capital structure + governance) | Has any new Form 4 been filed since 2025-09-11? |
| **Project Iris Monarch (undisclosed Childress scope)** | If verified, materially expands disclosed pipeline beyond 4.5GW NA | Childress County Appraisal District query returns Monarch Investment → IE US Development Holdings (3 or new entity) deed transfer 2024-2026; ERCOT Batch Zero applicant list (post-July 15, 2026) names IREN-affiliated entity for new Childress capacity | County deed query returns no IREN-affiliated Monarch transfer; ERCOT Batch Zero applicants exclude IREN beyond Sweetwater+Kiowa | [childresscad.org](https://www.childresscad.org/home) (Previous/Current Owner search), ERCOT PGRR145 issue page, ERCOT board materials post-July 15, Childress County Commissioners Court agendas | irenlimited.com fan site (Tier C — directional only); generic "AEP source said" social media (Tier D) | (H2 candidate signal) | Does the Childress County Appraisal District show a Monarch Investment → IREN-affiliated deed transfer? |
| **Spain / Nostrum integration** | EUR 165M acquisition; 490MW claimed but mixed regulatory status across 6 sites | 8-K Item 2.01 confirming closing; Red Eléctrica approval for additional CC Green capacity in 2030 horizon plan; first Spanish customer signing | Closing slip; CC Green 186MW denial held + extended across other sites; no customer pipeline color for Spain by end CY26 | SEC 8-K Item 2.01, Red Eléctrica (REE) Plan de Desarrollo de la Red de Transporte filings, Spanish regional planning portals (Extremadura, Castilla-La Mancha, Basque Country, Galicia), local Spanish press | Generic "EU AI strategy" coverage (too macro) | Physical buildout (Spain) | Has Nostrum acquisition closed yet, and did REE approve any pending requests? |

### Channel map (per variable — deeper detail)

The channels watchlist further down this file is the practical channel reference. The above table picks the **primary** channels per variable. Secondary/Tier-C channels are documented in the original Channels Watchlist section (Tier A / B / C tables below). Known-dead channels are flagged in the Search Coverage Ledger.

### Search coverage ledger

This ledger tracks what was actually searched in the most recent refresh (2026-05-11 deep-channel pull). Lets the next refresh know what was tested-empty vs. never-tested vs. dropped-as-noise.

| Channel | Query / source checked | Date | Result | Kept / Dropped / Defer | Why |
|---|---|---|---|---|---|
| SEC EDGAR — 10-Q for quarter ended Mar 31, 2026 | Full-text pull via curl + Python text extraction | 2026-05-11 | 9 material new specifics surfaced (commitments cliff, ATM activity, Nostrum price, Goldman/JPM commitment-letter, NVIDIA warrant terms, Microsoft RPO, Dell payment terms, $3.7B ARR bridge, Q3 cash burn shape) | **Kept** | Most important single source. Re-pull on every quarterly print. |
| SEC EDGAR — Section 16 (Roberts Daniel, Roberts William, Awassi Capital Trust) | Direct CIK lookup | 2026-05-11 | No Form 4 sales since Sep 11, 2025 (credibility-positive silence) | **Kept** | Re-check monthly; especially before Form 4 filing-window dates around 10-Q prints. |
| ERCOT PGRR145 issue page + IREN Comments | ercot.com/mktrules/issues/PGRR145 + 145PGRR-12 IREN Comments 031926 | 2026-05-11 | IREN participation in Batch Zero rulemaking confirmed (Tier-A); no specific IREN sites named | **Kept** | Watch for July 15, 2026 application deadline; post-deadline ERCOT may publish applicant list. |
| TDLR TABS search — IE US Development Holdings 3 | TABS2026003980 (Childress operations building) + TABS2024024946 (prior Childress) | 2026-05-11 | Only Childress operations-building permit found; no Sweetwater-tagged record | **Kept** | Re-pull next refresh; Sweetwater 1 Phase 1 should generate a TDLR record. |
| Texas Comptroller — IE US Development Holdings entities | opengovus.com/texas-taxpayer search + Texas SOS records | 2026-05-11 | Holdings 3 verified (Delaware foreign profit corp, TX COA #0804499938 active since 2022); Holdings 5/7 NOT in SEC 10-K Exhibit 21.1 significant-subsidiaries list | **Kept** (Holdings 3 confirmed); **Defer** (Holdings 5/7 primary verification) | Holdings 5/7 may be datacenter.fyi naming artifacts; defer until next refresh and try direct Texas SOS query. |
| Childress County Appraisal District | childresscad.org Previous/Current Owner search | 2026-05-11 | Site reachable, but interactive search not executable from this run | **Defer** (high priority) | **Critical**: query "Monarch Investment" → IREN-affiliated entity deed transfers 2024-2026. This is the H2 gate-clear test. Next refresh must attempt direct search. |
| Fisher County / Nolan County records | Hobbs Holler local blog + Double Mountain Chronicle | 2026-05-11 | Citizen complaint Feb 2026 about IREN construction on FM 540 (Fisher County) — surprised commissioners; resident concerns about S2 area; KTAB-TV earlier reporting | **Kept** | Re-pull quarterly; check Fisher County Commissioners Court agenda + Nolan County for any IREN-tagged actions. |
| TxDOT oversize/overweight permit search | TxDMV permit lookup + TxDOT district restrictions | 2026-05-11 | Generic TxDOT permit framework pages only; no IREN-specific lane records surfaced via search engine | **Defer** | Direct lane-specific search of TxDMV permit DB requires authenticated portal access; defer until next refresh has API/scraping path. |
| LinkedIn jobs by site | "IREN" + "Childress, TX" filter | 2026-05-11 | Mechanical Supervisor – Construction (Nov 2025), Electrical Engineer (Jul 2025), Network Engineer Data Center; **IE US Operations Inc.** employs all roles | **Kept** | Re-pull quarterly; specifically watch for Sweetwater-tagged roles (none yet); look for customer-success roles (would indicate customer scale-up). |
| H-1B / DOL LCA disclosure data | dol.gov/agencies/eta/foreign-labor/performance | 2026-05-11 | Not directly queried this refresh | **Defer** | Specifically search for IE US Operations / IE US Development Holdings 3 / IREN Limited LCA filings next refresh — useful for engineering-role hiring depth. |
| Aterio third-party satellite | aterio.io events for IREN | 2026-05-11 | Jan 13, 2026 event: "satellite imagery confirming active work on Horizons 3 and 4" | **Kept** | Tier-C source but useful as independent corroboration; check quarterly. |
| Sentinel-2 direct imagery | apps.sentinel-hub.com/eo-browser | 2026-05-11 | Not directly inspected this refresh | **Defer** | Visual inspection delta-over-time would corroborate Aterio + add construction-pace metric; defer until skill has imagery-inspection tooling. |
| Frans Bakker satellite analysis | Twitter/X imagery via Reddit citations | 2026-05-11 | HD satellite of Horizon 1 (Feb 2025) confirms steel frame + substation + cable trenches; Agrippa Investments Nov 2025 deep dive cites Frans Bakker as image source | **Kept** | Useful Tier-C analyst; check for updates on X for ~quarterly cadence. |
| BC Hydro filings + competitive process | bchydro.com news + BC PUC dockets | 2026-05-11 | Jan 30, 2026 announcement of new competitive process for AI data centers; no Mackenzie-specific filing yet | **Kept** | Re-pull to track Mackenzie 80MW GPU deployment H2 2026; watch for IREN-named applications under the new process. |
| Spanish REE (Red Eléctrica) registry + regional planning portals | ree.es + Extremadura/Castilla-La Mancha portal searches | 2026-05-11 | CC Green Cáceres 186MW request DENIED for 2030 horizon ("not sufficiently advanced"); other Nostrum sites at various permit stages | **Kept** | Re-pull to track Plan de Desarrollo de la Red de Transporte cycle; CC Green is on the next 2027-2030 plan submission. |
| AEMC / NEM Australia | aemc.gov.au news + draft rules | 2026-05-11 | March 12, 2026 draft rule for DC connections, submissions closed May 7, 2026, final rule mid-2026 | **Kept** | Re-pull mid-2026 to track final rule; affects when IREN's Australian projects can connect. |
| NVIDIA fiscal calls + newsroom | nvidianews.nvidia.com + investor.nvidia.com | 2026-05-11 | Q1 FY27 earnings call set May 20, 2026; NVIDIA STX Storage Architecture (BlueField-4) names IREN as early adopter; 5GW partnership press at May 7 announcement | **Kept** | **Re-check May 20, 2026** — counterparty-validation window for IREN partnership. |
| Microsoft earnings + counterparty mentions | microsoft.com IR + counterparty press | 2026-05-11 | No new MSFT-side IREN-specific signal beyond Nov 2025 announcement and Microsoft/Crusoe Abilene project context | **Kept** | Re-check at Microsoft FY26 Q4 earnings (~late July 2026) for MSFT-side delivery acceptance commentary. |
| Mirantis ecosystem PRs | mirantis.com news + customer logos | 2026-05-11 | k0rdent + Supermicro (Mar 3, 2026), + Netris (Mar 10, 2026), + NVIDIA AI Cloud Ready founding ISV (Mar 16, 2026); existing customers Adobe, Ericsson, Inmarsat, MetLife, PayPal, Societe Generale | **Kept** | Confirms Mirantis is real software platform, not paper acquisition; re-check for IREN-customer logos post-close. |
| Lancium / Crusoe / Stargate / Vantage competitive map | DCD coverage + KTXS local + Lancium IR | 2026-05-11 | Lancium Stargate One 1.2GW Abilene; Microsoft/Crusoe 900MW Abilene; Vantage Frontier 1.4GW Shackelford; Crusoe Nolan 200MW/$7B (tax abatement approved Apr 14, 2026) — IREN is one of several active in West Texas | **Kept** | Competitive context; re-pull quarterly. |
| ERCOT Long-Term Load Forecast + adjustment methodology | ercot.com news + board materials | 2026-05-11 | Apr 15, 2026 preliminary 2026-2032 forecast: 367,790 MW by 2032; ERCOT applies 49.8% haircut on requested data center demand (acknowledges over-stating) | **Kept** | Macro context for what fraction of IREN's 4.5GW pipeline will actually energize on schedule. |
| Project Iris Monarch via irenlimited.com fan site + Frans Bakker | irenlimited.com + Reddit + Agrippa Investments | 2026-05-11 | Fan site claims Childress County deed records show IREN purchase from Monarch Investment adjacent to MISAE 1 Solar; Frans Bakker surfaced; alleged AEP source flagged "Project Iris Monarch" months ago | **Defer** (Tier-C currently; **upgrade priority for direct deed verification next refresh**) | If primary deed record found, this becomes Tier-A and the H2 gate-clear test. |
| Sweetwater Reporter / Childress Index / local press | Direct site searches | 2026-05-11 | Local press for Sweetwater + Childress lighter than expected; Hobbs Holler + Double Mountain Chronicle most useful | **Kept** | Check quarterly; especially around Fisher County Commissioners Court meeting dates. |
| Burns & McDonnell project announcements | burnsmcd.com news | 2026-05-11 | Burns & McDonnell confirmed as design firm for Childress operations building (TDLR record); no S1 substation announcement found | **Defer** | Direct Burns & McDonnell IREN project page search next refresh. |
| General TX flatbed trucking rates | DAT/FreightWaves | (not run) | — | **Dropped** | Per existing projects.md "What NOT to track" — too macro for IREN-specific signal absent lane-specific data. |
| Bitcoin hash rate | mempool.space + miner data | (not run) | — | **Dropped** | Per existing projects.md — IREN paused BTC mining at 50 EH/s June 2025; further declining post-Childress transition. Noise for AI thesis. |
| Panjiva / ImportGenius bill-of-lading | (subscription) | (not run) | — | **Dropped** | Per existing projects.md — IREN buys from Dell domestically; no significant IREN-side import flow to track. |

### Patterns claimed

1. **Physical buildout** (primary) — IREN's core execution story is multi-site physical construction (Childress 4 horizons, Sweetwater 1 and 2 substations + data halls, Mackenzie GPU installs, Childress retrofits, Spain Nostrum sites). Channels: grid filings, county permits, freight, satellite, EPC PR, contractor liens, construction-supervisor hiring.
2. **Capital structure dependency** (primary) — The $11.9B 12-month commitments cliff vs. ~$6-8B funded stack is the dominant near-term execution variable. IREN runs an active ATM (~$680M/month), serial convertibles, customer prepay, and GPU-secured debt. Channels: SEC capital filings, Form 4 founder activity, debt-covenant disclosures, refinancing windows.
3. **Hyperscaler / single-customer concentration** (emerging) — Microsoft + NVIDIA together represent ~84% of contracted ARR ($2.6B of $3.1B). Channels: counterparty earnings, lease/contract amendments, 8-K item disclosures, customer-side press.

Capital execution patterns aren't claimed (e.g., Post-IPO lockup doesn't apply — IREN IPO'd Nov 2021; Restructuring overhang doesn't apply; Clinical credibility doesn't apply). Engagement/utilization could apply if IREN started disclosing GPU hour utilization metrics — currently it doesn't, so not claimed.

### Carry-overs from prior work

- **From _meta.md (2026-04-25)**: Roberts brothers Sep 2025 sales NOT under 10b5-1 — flagged as governance signal. Variable Map now tests via "no new Form 4 since" (currently bull-tell holding).
- **From projects.md prior (2026-05-07)**: Sweetwater 2 2027 vs 2028 ramp ambiguity — variable map separates substation energization from data-center capacity ramp; iren.com vs. Q3 deck mismatch tracked.
- **From projects.md prior**: Project Iris Monarch flagged "UNVERIFIED, treat as speculation" — variable map upgrades to "CANDIDATE H2 SIGNAL — needs primary deed verification" with explicit verification path.
- **From projects.md prior**: $14-16M per IT MW Childress capex was disclosed — variable map uses this to size the capital-execution math (4.5GW × 27% IT × $15M ≈ $18B data center infra alone; vs. $6-8B funded → dilution load).
- **From the prior IREN deep-dive:** Position has graduated from pre-deal entry to execution-phase hold after NVIDIA contract; trim ladder exists at $77 / $90. Projects map tests execution and funding, not current-price sizing.
- **From the prior IREN thesis and tranche notes:** Wait-for-deal setup has already fired; remaining variables are delivery acceptance, funding quality, dilution cadence, and whether the third-customer temptation becomes an overreach.
- **From the post-print NVIDIA deal read:** Do not extrapolate NVIDIA into "a third hyperscaler will surely follow" without fresh evidence; H2 gate discipline is especially important.

### What changed since last review

- **2026-05-11 first build of Variable Map (this section)** — restructured projects.md to put Variable Map at top per company-projects SKILL Step 0. Substrate was already deep after ~25 channels pulled in the 2026-05-11 refresh. Codified the bull/bear tells per variable + populated Search Coverage Ledger from the deep-refresh search trail. Map maturity = `searched`; upgrade to `mature` only after a later audit validates map fit + coverage under the new 4h audit check.

---

## Stage Gates

Discrete dated milestones — the binary "did it happen" events that anchor everything else.

| Gate | Site | Status | Date | Source | Implication |
|------|------|--------|------|--------|-------------|
| Microsoft contract signed | Childress | DONE | 2025-11-03 | [Reuters](https://www.reuters.com/technology/microsoft-signs-97-billion-contract-with-iren-nvidia-chips-2025-11-03/) · [SEC 8-K](https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm) | $9.7B / 5y / 20% prepay (credited to years 3-5) anchors Childress revenue |
| Dell GPU agreement (Microsoft) | Childress | DONE | 2025-11-03 | [IREN PR](https://iren.gcs-web.com/news-releases/news-release-details/iren-secures-97bn-ai-cloud-contract-microsoft/) | $5.8B GPU/equipment purchase for MSFT contract |
| Dell GPU agreement (additional) | Canada + USA | DONE | 2026-03-04 | _meta.md / 8-K | $3.5B aggregate ($2.3B CA + $1.2B USA), 2H 2026 delivery |
| Substation energization | Sweetwater 1 (1.4 GW) | DONE | 2026-05-01 | [IREN PR](https://www.globenewswire.com/news-release/2026/05/01/3286213/0/en/IREN-Announces-Successful-Energization-of-Sweetwater-1.html) | First major non-Childress site live; campus on schedule |
| Mirantis acquisition signed | corporate | DONE | 2026-05-05 | [IREN PR](https://www.globenewswire.com/news-release/2026/05/05/3287514/0/en/IREN-Announces-Acquisition-of-Mirantis-to-Strengthen-AI-Cloud-Delivery-Capabilities.html) | $625M in IREN shares — adds k0rdent / Kubernetes orchestration |
| **Q3 FY26 earnings printed** | corporate | DONE | 2026-05-07 AMC | [Q3 FY26 deck via SEC](https://www.sec.gov/Archives/edgar/data/1878848/000187884826000025/irenreportsq3fy26results.htm) · [10-Q](https://www.sec.gov/Archives/edgar/data/1878848/000187884826000026/iren-20260331.htm) | **Revenue $144.8M** (not $219.69M as prior refresh listed — that was an error). Q3 net loss $(247.8)M including $140.4M BTC-mining impairments + $23.7M unrealized cap-call losses. Adj EBITDA $59.5M. Cash $2,213.3M. 9-month revenue $569.8M. **Q3 revenue was FLAT y/y** (Q3 FY25 was also $144.8M) — striking given the ramp narrative. The growth is showing up in 9-month numbers and forward ARR commitments. |
| **NVIDIA second hyperscaler-grade contract signed** | Mackenzie / Childress (air-cooled Blackwell) | DONE | confirmed in Q3 FY26 deck | [Q3 FY26 deck](https://www.marketscreener.com/news/iren-q3-fy26-results-presentation-ce7f5bdadf88f520) | **5-year contract for air-cooled Blackwell GPUs**, $0.7B ARR, expected to ramp early 2027. Customer #2 after Microsoft |
| **Horizon 1 commissioning underway** (NVIDIA GB300 NVL72) | Childress | DONE | confirmed Q3 FY26 deck | same | Active commissioning; super cluster handoff to Microsoft scheduled Q3 CY26 |
| **Sweetwater 1 200MW liquid-cooled IT load construction underway** | Sweetwater 1 | DONE | confirmed Q3 FY26 deck | same | Critical IT load disclosed for first time; designed for NVIDIA Vera Rubin |
| **Nostrum Group acquisition (Europe)** | Spain (490MW) | DONE | confirmed Q3 FY26 deck | same | EU platform entry; 50+ person team; GW+ global pipeline |
| Horizon 1 Microsoft handoff | Childress | UPCOMING | Q3 CY26 (Jul-Sep 2026) per Q3 FY26 deck | same | **First Microsoft revenue tranche.** The single most material upcoming gate |
| Horizon 2-4 commissioning (additional 150MW IT load) | Childress | UPCOMING | end of CY26 per Q3 FY26 deck | same | Completes the 200 MW Microsoft scope at Childress |
| British Columbia + Childress +180MW expansion live | BC + Childress | UPCOMING | H2 2026 | same | Prince George 50MW operating/commissioning; Mackenzie 80MW + Childress 50MW retrofits underway |
| Substation energization | Sweetwater 2 (600 MW) | NOT YET | mgmt: 2027 (Q1 FY26); Q3 FY26 deck has 2028 for "remaining 1,700MW" Sweetwater capacity — possible date slip | [IREN site](https://iren.com/data-centers/sweetwater) · Q3 FY26 deck | Slip watch — Sweetwater 2 may have moved from 2027 → 2028 in the Q3 deck (compares NOT YET → check next print) |
| Substation energization | Kiowa, OK (1,600MW) | NOT YET | from 2028 (mgmt) | Q3 FY26 deck | Diversifies away from ERCOT (SPP grid). **Note: Q3 FY26 deck refers to the OK site as "Kiowa" — was previously labeled "Oklahoma"** |
| Childress 2027 expansion +400MW | Childress | UPCOMING | 2027 | Q3 FY26 deck | Horizon 5-6 = 100MW IT load liquid + 250MW air-cooled retrofit |
| Canal Flats +30MW retrofit | Canal Flats, BC | UPCOMING | 2027 | Q3 FY26 deck | Existing 30MW air-cooled converted to AI-ready |

---

## Site Portfolio (>4.5 GW secured + Spain 490MW)

Total secured grid-connected power: **>4.5 GW** in NA. New Spain platform adds 490MW post-Nostrum acquisition. **>2,600 workers on site** at Childress per Q3 FY26 deck (hiring-scale signal).

Listed in order of revenue linkage (closest to recognized revenue first).

### Childress, TX — 750 MW (the revenue anchor)

**Why first:** Direct line to recognized revenue via Microsoft contract (~$1.9B ARR at full run-rate). Plus an additional 450MW headroom available for further customers (Horizon 5-10 concept).

**Disclosed capex per MW (IT load) per IREN's Microsoft contract presentation:** $14-16M per MW
- $9-11M: data center infrastructure (Tier III equivalent concurrent maintainability)
- $3M: supercluster architecture, flexible rack densities (130-200kW)
- $2M: acceleration costs to achieve 2026 delivery

**Estimated project EBITDA margin:** ~85% (per Microsoft contract investor deck)

**Horizon 1-4 (Microsoft contract scope):** 4 × 50MW IT load liquid-cooled phases, 200MW total
- **Horizon 1 super cluster commissioning underway**, Microsoft handoff Q3 CY26
- Horizon 2-4 on track for end-CY26 delivery
- **>2,600 workers on site** for accelerated build-out
- Repeatable model speeding subsequent phases

**Horizon 5-6 (2027 expansion):** 100MW IT load additional liquid-cooled
**Plus 250MW air-cooled retrofit** for 2027 (NVIDIA Blackwell)

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Horizon 1 commissioning underway, NVIDIA GB300 NVL72 | Q3 FY26 deck | 2026-05-07 | Active commissioning; on schedule for Q3 CY26 handoff | HIGH | Direct |
| **Microsoft handoff scheduled Q3 CY26** (Horizon 1 super cluster) | Q3 FY26 deck | 2026-05-07 | First Microsoft revenue tranche window | HIGH | Direct |
| Horizon 2-4 on track for end of CY26 | Q3 FY26 deck | 2026-05-07 | Full 200MW critical IT load delivery on schedule | HIGH | Direct |
| 2,600 workers on site | Q3 FY26 deck | 2026-05-07 | Construction labor force at peak — accelerated build-out signal | HIGH | Indirect (execution proxy) |
| Capex $14-16M per MW IT load | [IREN MSFT contract deck](https://iren.gcs-web.com/static-files/a421bb34-0156-4687-be7d-19f53a5236e5) | 2025-11-03 | Industry baseline for AI-data-center build cost | HIGH | Indirect (valuation lens) |
| ~85% project EBITDA margin | same | 2025-11-03 | Mgmt-claimed; reflects ownership of land + grid + DC | HIGH | Indirect |
| Microsoft contract: 5y, $1.9B ARR, 20% prepay | IREN PR / SEC 8-K | 2025-11-03 | Schedule binds Childress to dated commissioning | HIGH | Direct ($1.94B ARR) |
| Microsoft prepay credited to years 3-5 | [SEC 8-K](https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm) | 2025-11-03 | Cash up front; revenue offset deferred to back end | HIGH | Direct (cash flow) |
| Dell $5.8B GPU agreement | IREN PR | 2025-11-03 | Equipment commitment matches contract scope | HIGH | Direct |
| $3.6B GPU financing at <6% interest secured (Goldman + JPM) | Q2 FY26 release | 2026-02-05 | Together with $1.9B MSFT prepay covers 95% of GPU capex | HIGH | Direct (de-risks delivery) |
| 99,900 GPUs installed-or-on-order at Dec 31, 2025 (vs. ~1,900 at June 30, 2025) | _meta.md / 10-Q | 2026-02-05 | Procurement pace tracking ramp | HIGH | Direct |

### Sweetwater 1 — 1,400 MW (200MW IT load liquid-cooled under construction)

**This site upgraded materially in Q3 FY26 disclosures:**

- 1,300 acres (IREN) / 1,700 acres (DCD)
- **Substation energized 2026-05-01** — connection of 345kV/138kV bulk substation to ERCOT grid
- Power delivery ramps progressively in line with phased construction & commissioning
- **NEW: Construction underway for initial 200MW (IT load) of liquid-cooled data centers** (Q3 FY26 deck) — first explicit critical IT load number for Sweetwater
- **NEW: Designed for next-generation chip architectures, including NVIDIA Vera Rubin**
- **NEW: "Initial phase establishes foundation for accelerated buildout across remaining site capacity"** — repeatable scaling implied

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Substation energization (1.4 GW bulk) | IREN PR | 2026-05-01 | First major stage gate post-Childress hit on schedule | HIGH | Indirect |
| **200MW IT load liquid-cooled construction underway** | Q3 FY26 deck | 2026-05-07 | Critical IT load now disclosed (out of 1.4 GW gross) — implies ~14% IT load efficiency for Phase 1 | HIGH | Indirect (no contracted customer yet) |
| **Designed for NVIDIA Vera Rubin** | Q3 FY26 deck | 2026-05-07 | Next-gen chip architecture readiness — competitively positioned | HIGH | Indirect |
| **"Negotiating large-scale AI Cloud deployments across 2027 capacity"** | Q3 FY26 deck (page 16) | 2026-05-07 | Customer pipeline language for Sweetwater. **Still no specific tenant signed** — watch for shift to "tenant signed" / named customer | HIGH | Watch — language shift = potential signing |
| 700,000+ GPU capacity at full Sweetwater Hub (across S1+S2) | IREN site | current | Sets max theoretical scale | HIGH (capacity claim) / LOW (timing) | Indirect |

### Sweetwater 2 — 600 MW (energization slip watch)

- 500 acres
- Q1/Q2 FY26 disclosure: substation energization **2027**
- **Q3 FY26 deck mentions "remaining 1,700MW" of Sweetwater capacity expected to ramp from 2028** — could imply Sweetwater 2 has slipped from 2027 → 2028, OR could just be referring to the post-S1-Phase1 capacity ramp

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| 2027 substation energization target | Q1/Q2 FY26 releases | through 2026-02-05 | Multi-year horizon, post-MSFT-ramp | MED (date conflict appearing) | Indirect |
| **Q3 FY26 deck implies 2028 ramp for "remaining 1,700MW Sweetwater"** | Q3 FY26 deck | 2026-05-07 | **Possible Sweetwater 2 slip from 2027 → 2028** — confirm on next refresh by checking earnings call audio | MED (interpretation needed) | Indirect |

### Childress (additional sites beyond Horizon 1-4)

**Childress retrofits underway** ahead of GPU deliveries in H2 2026 — separate 50MW capacity at Childress getting ready for additional GPU deployment outside the MSFT scope. Likely tied to the NVIDIA Blackwell second contract.

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| 50MW Childress retrofit underway H2 2026 | Q3 FY26 deck | 2026-05-07 | Expanded near-term capacity beyond MSFT scope | HIGH | Direct (likely tied to NVIDIA Blackwell contract) |
| 450MW additional Childress headroom (Horizon 5-10 concept) | [MSFT contract deck](https://iren.gcs-web.com/static-files/a421bb34-0156-4687-be7d-19f53a5236e5) | 2025-11-03 | Strategic optionality — full 750MW campus convertible to liquid-cooled AI | HIGH | Indirect |

### British Columbia — 160 MW operational (transitioning)

- **Mackenzie (80 MW)**: Data centers prepared for GPU installations commencing H2 2026
- **Prince George (50 MW)**: All GPUs operating or undergoing commissioning. ~$0.4B ARR contracted; remaining contract negotiations supporting >$0.5B
- **Canal Flats (30 MW)**: Retrofitting for AI-ready capacity, target 2027

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Prince George GPUs operating/commissioning | Q3 FY26 deck | 2026-05-07 | $0.4B+ ARR active or near | HIGH | Direct |
| Mackenzie GPU installations H2 2026 | Q3 FY26 deck | 2026-05-07 | 80 MW capacity online by end of 2026 | HIGH | Direct |
| Canal Flats 30MW retrofit (2027 expansion) | Q3 FY26 deck | 2026-05-07 | BC capacity expansion at small scale | HIGH | Indirect |
| ASIC-to-GPU transition by end 2026 | Q1 FY26 release | 2025-11-06 | BC pivots from BTC to AI cloud | HIGH | Direct |
| Mining hardware impairments $(31.8)M H1 FY26 | _meta.md / 10-Q | 2026-02-05 | Real cost of ASIC retirement showing in P&L | HIGH | Direct |

### Kiowa, OK — 1,600 MW (SPP grid; renamed from "Oklahoma")

- 2,000 acres, announced Q2 FY26 (Feb 5, 2026)
- Q3 FY26 deck refers to the site as **"Kiowa"** — possibly a project codename or named after a county/town. Verify on next refresh.
- Power scheduled to ramp **from 2028**
- Grid studies complete
- <6ms latency to network hubs
- Strategic value: **diversifies away from ERCOT concentration**

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Site announced | IREN Q2 FY26 release | 2026-02-05 | Total secured power crosses 4.5 GW | HIGH | None near-term (2028+) |
| Grid studies complete | IREN site | current | Pre-construction phase de-risked | HIGH | None near-term |
| **Site renamed to "Kiowa"** in Q3 FY26 deck | Q3 FY26 deck | 2026-05-07 | Possible local town/county naming; verify | MED | Indirect |

### Spain (Nostrum Group) — 490 MW + GW+ pipeline (NEW)

**Acquisition closed Q3 FY26** — Nostrum Group brings:
- 50+ person team (development, construction, operations)
- 490 MW secured power in Spain
- GW+ global development pipeline
- Spain market: favorable AI policies, abundant renewables, lower build/operating costs

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Nostrum acquisition (EU entry) | Q3 FY26 deck | 2026-05-07 | First non-NA capacity; geopolitical + regulatory diversification | HIGH | None near-term (no construction timeline disclosed) |
| 490 MW secured in Spain | Q3 FY26 deck | 2026-05-07 | First disclosed EU capacity | HIGH | Indirect |

### APAC — Australia (NEW)

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Progressing large-scale Australian projects | Q3 FY26 deck | 2026-05-07 | APAC platform under development | HIGH | None near-term |
| Australian submarine connectivity references | Q3 FY26 deck | 2026-05-07 | Regional fiber strategy emerging | HIGH | None near-term |

### Project Iris Monarch — ~1 GW Childress County (CANDIDATE H2 SIGNAL — needs primary deed verification)

**Status upgraded from "UNVERIFIED" → "CANDIDATE H2 SIGNAL" 2026-05-11** after triangulating multiple secondary sources:

- **irenlimited.com (third-party fan site)** claims Childress County land records show IREN purchased from Monarch Investment in Childress County adjacent to MISAE 1 solar farm, south of Highway 287. Notes a double 345kV line + 138kV AEP-owned line through the site.
- **Frans Bakker (@FransBakker9812)** is a real IREN analyst (Agrippa Investments cited him as image source in Nov 2025 deep dive) who surfaced the alleged Childress County land records. Bakker has visited the Childress site (late May 2025) and produces HD satellite imagery analysis (cited in Reddit IREN community).
- **MISAE 1 Solar Park is real**: [misaesolar.com](https://www.misaesolar.com/misae-solar-park) — 320 MWdc on 1,674 acres in Childress County, owned by Copenhagen Infrastructure Partners (acquired July 2018). ERCOT interconnection queue confirms (240.8 MW operational since Dec 20, 2021, project 18INR0045).
- **Reinvestment Zone #2** was created October 14, 2024 in Childress County, adding ~80.12 acres within Section 421 to the Iris Energy Reinvestment Zone. Source: [northwiseproject.com](https://northwiseproject.com/iren-stock-childress/) citing Childress County Commissioners Court (June 14, 2021 = Zone #1; Oct 14, 2024 = Zone #2). This is Tier-A regulatory context for expansion beyond the original Childress footprint.
- **Agrippa Investments (Nov 2025 deep dive)** corroborates: "the company now has a consistent record of annual site additions and capacity expansions" and references "more than 5 GW in the pipeline."
- **AEP source allegedly flagged "Project Iris Monarch" months ago** — initially dismissed as the Lancium project; fan site claims the deed records resolve it as internal project name simply named after the seller.

**Primary verification path:** Childress County Appraisal District ([childresscad.org](https://www.childresscad.org/home)) supports search by Previous Owner / Current Owner / Volume / Page / Deed Date. **The next refresh should query this database directly** for "Monarch Investment" → "IE US Development Holdings" or similar IREN-affiliated entity deed transfers in 2024-2026. If a deed record materializes, this becomes the second independent Tier-A signal (alongside ERCOT PGRR145-12 IREN comments) that could clear the H2 strict gate in execution-thesis.

**Why this matters now:** The fan site explicitly hypothesizes "Land acquisition to demonstrate site control for ERCOT Batch Zero eligibility (June 1 board vote)." Batch Zero eligibility requires demonstrated site control + completed studies — which fits the timeline if IREN is positioning the Monarch site as a Batch Zero candidate. ERCOT's Batch Zero application deadline is July 15, 2026 per Foley & Lardner legal analysis; ERCOT publishes the applicant list after that. If IREN files a Batch Zero application naming the Monarch site, that's a third independent Tier-A signal.

---

## Cross-Site Signals

### Customer pipeline — second contract validates platform

**$3.1B ARR now under contract** as of Q3 FY26 (up materially from prior). Including:
- $1.9B ARR — Microsoft / Childress Horizon 1-4 (contracted)
- $0.7B ARR — **NEW: NVIDIA 5-year contract** for air-cooled Blackwell GPUs, ramps early 2027
- $0.5B ARR — additional capacity contracted (likely Prince George + minor sites)

**Targeting $3.7B ARR by end of CY26** (raised from prior $3.4B target).

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| **$3.1B ARR under contract** (was prior smaller number) | Q3 FY26 deck | 2026-05-07 | Visible, contracted revenue runway | HIGH | Direct |
| **$3.7B ARR target by end CY26** (raised from $3.4B) | Q3 FY26 deck | 2026-05-07 | Mgmt growth target raised post Mirantis + NVIDIA | HIGH | Direct |
| **NVIDIA 5-year contract for air-cooled Blackwell GPUs** | Q3 FY26 deck | 2026-05-07 | $0.7B ARR; ramps early 2027. **Second hyperscaler-grade customer** (after Microsoft) | HIGH | Direct |
| 480 MW capacity contracted | Q3 FY26 deck | 2026-05-07 | Customer-mapped capacity now sized | HIGH | Direct |
| Active customer engagement for remaining capacity (H2 CY26 delivery) | Q3 FY26 deck | 2026-05-07 | Pipeline of additional customers being negotiated | HIGH | Indirect |

### Capital structure

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Cash $2.8B (Jan 31, 2026) | Q2 FY26 release | 2026-02-05 | Strong liquidity going into Childress capex | HIGH | Indirect |
| >$9.2B funding secured FYTD (prepayments + converts + GPU lease/financing) | Q2 FY26 release | 2026-02-05 | Capital structure can support pipeline at announced pace | HIGH | Indirect |
| **Capex per MW (IT load) at Childress: $14-16M** | Microsoft contract deck | 2025-11-03 | Disclosed unit-economics baseline | HIGH | Direct (valuation lens) |
| **Sweetwater-tied financing: not yet disclosed** | Q3 FY26 deck (no Sweetwater financing line) | 2026-05-07 | Watch row — once a Sweetwater customer signs, customer-prepay-funded capex should be disclosed | UPCOMING | Watch |
| **Sweetwater customer prepayments: not applicable yet** | Q3 FY26 deck | 2026-05-07 | No customer signed → no prepay. **Watch on next refresh** | UPCOMING | Watch |
| Stock-based comp $130.6M H1 FY26 (vs $42.6M FY25 full yr) | _meta.md | 2026-02-05 | ~30% of revenue going to equity comp — flag for ongoing dilution | HIGH | Indirect (cost structure) |
| Mirantis acquisition $625M in shares | IREN PR | 2026-05-05 | Software/Kubernetes orchestration layer — competitive positioning vs. CRWV | HIGH | Indirect (margin / customer-stickiness) |
| **Stock +42% past week, +73% past month per 247WallSt** | [247WallSt](https://247wallst.com/investing/2026/05/07/dont-focus-too-heavily-on-irens-q3-today-look-at-what-comes-next/) | 2026-05-07 | Mirantis + NVIDIA contract impact pricing in | HIGH | Indirect (sentiment) |

### Capital structure & dilution risk

Frame: IREN's pipeline (~4.5 GW NA + 490 MW Spain) at disclosed Childress capex of $14-16M per IT MW implies a multi-year capex burn that vastly exceeds today's funding stack. The gap between funded capex and committed pipeline = the implied dilution load. Track this so a "stock up huge" reflex doesn't obscure the multi-billion equity issuance still likely ahead.

**THE COMMITMENTS CLIFF (added 2026-05-11 from 10-Q Note 21).** As of March 31, 2026, the Group's total commitments were **$11,902,471 thousand ($11.9B)**, up from **$368,805 thousand ($368.8M) at June 30, 2025** — a 32× increase in 9 months. **$11,899,054 thousand is payable within 12 months** of the balance date. This is the single cleanest "execution is now a funding machine" datapoint and dwarfs anything previously on the radar. The commitments reflect the GPU purchase obligations (Dell + others) and data center infrastructure procurement tied to the Microsoft + NVIDIA contracts. The funding-vs-commitments race is now the dominant near-term execution variable, not the ARR target.

**ATM activity timeline (from 10-Q Note 17 + Subsequent Events):**

| Window | ATM issuance | Net/Gross proceeds | Avg implied price |
|---|---:|---:|---:|
| Q1 FY26 (Jul-Sep 2025) | 23,041,102 shares | $599.9M net | $26.03 |
| Q2 FY26 (Oct-Dec 2025) | nil ATM (but $1.63B equity raise Dec 8, 39.7M shares @ $41.12) | — | — |
| Q3 FY26 (Jan-Mar 2026) | 8,857,303 shares | $380M gross | $42.91 |
| **Apr 1 – May 7, 2026 (subsequent event)** | **15,877,502 shares** | **$683.5M gross** | **$43.05** |
| **Cumulative under new $6B shelf (Mar 4, 2026 - May 7, 2026)** | **24.7M shares** | **~$1.06B gross** | **$42.91** |

Prior $1B ATM facility (filed Jan 21, 2025) was **exhausted by Sep 2025** — 66,707,732 shares for ~$999.9M.

**Share count timeline** (from 10-Q rollforward + cover page):

| Date | Ordinary shares outstanding |
|---|---:|
| Jun 30, 2024 | 186,367,686 |
| Jun 30, 2025 | 257,211,899 |
| Sep 30, 2025 | 282,876,303 |
| Dec 31, 2025 | 331,759,177 |
| Mar 31, 2026 | 340,979,966 |
| **Apr 30, 2026 (10-Q cover page)** | **357,378,674** |

Dilution rate over the past 12 months: ~91M shares = **+35% share count growth**. Pending dilution: Mirantis ~9M shares + Nostrum ~35% × EUR 165M ≈ 0.9M shares + NVIDIA warrant up to 30M = ~40M potential, **~11% additional**. Plus the May 11 $2.0B + $300M convertibles ($2.3B max) — at $70 share price and 25% conversion premium → ~$87.50 conversion price → up to ~26M more shares if fully converted.

**Convertibles cap table (verified via SEC filings):**

| Tranche | Principal | Coupon | Conversion price | Maturity | Status |
|---|---:|---:|---:|---|---|
| 2029 Convertibles | ~$445.7M aggregate | 3.50% | $13.64 | 2029 | Partial Repurchase done Dec 2025 |
| 2030 Convertibles | (rolled into 2029 aggregate above) | 3.25% | $16.81 | 2030 | Partial Repurchase done Dec 2025 |
| 2031 Convertibles | $1.0B | TBD | TBD | Jul 1, 2031 | Issued Oct 14, 2025 |
| 2032 Convertibles | $1.15B | 0.25% | $51.40 | Jun 1, 2032 | Priced Dec 3, 2025 @ $41.12 spot, 25% premium |
| 2033 Convertibles | $1.15B | 1.00% | $51.40 | Jun 1, 2033 | Priced Dec 3, 2025 |
| **Proposed 2033 (2nd issue)** | **$2.0B + $300M option** | TBD | TBD (likely ~$87.50 if 25% premium to ~$70 spot) | 2033 | **Announced May 11, 2026 — pricing pending** ([primary source](https://www.globenewswire.com/news-release/2026/05/11/3291756/0/en/IREN-Announces-Proposed-Convertible-Notes-Offering.html)) |

Total convertible principal outstanding **before May 11 issuance: ~$3.75B**. Post-issuance (if priced as announced): **~$5.75B-$6.05B**. Capped calls on the 2032/2033 notes have $82.24 cap price (200% of spot at pricing).

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Shares outstanding 332.3M (Jan 30, 2026) | _meta.md / 10-Q | 2026-02-05 | Baseline for dilution math | HIGH | Indirect |
| Dec 2025 capital raise: $2.3B convertibles + $1.63B equity (39.7M shares @ $41.12) + $0.20B capped calls | _meta.md / 8-K | 2025-12-08 | ~13.5% share dilution from one event; converts are 2032 + 2033 with $51.40 conversion | HIGH | Indirect (dilution) |
| Mirantis $625M paid in IREN ordinary shares | IREN PR | 2026-05-05 | At ~$70 share price ≈ ~9M shares ≈ ~3% additional dilution | HIGH | Indirect |
| Stock-based comp $130.6M H1 FY26 (vs $42.6M FY25 full year) | _meta.md / 10-Q | 2026-02-05 | Equity comp at ~30% of revenue — ongoing dilution drift | HIGH | Indirect |
| GPU financing $3.6B at <6% (Goldman + JPM) | Q2 FY26 release | 2026-02-05 | Debt-funded portion; doesn't dilute equity but creates debt service obligation | HIGH | Indirect |
| Microsoft prepay $1.94B (covers ~33% of $5.8B GPU capex) | Microsoft contract deck | 2025-11-03 | Customer-funded portion; reduces external funding need for the MSFT scope | HIGH | Direct |
| **Implied capex for full pipeline (back-of-envelope)** | derived from $14-16M/MW IT load × ~27% IT-to-gross ratio at Childress | 2026-05-07 | 4.5 GW gross × ~27% IT load × $15M/MW ≈ **~$18B** for data center infra alone (excl. GPUs). Plus Spain ~$2B. **GPUs at MSFT-scope rate (~$29M per IT MW) ≈ another ~$35B over the buildout.** Order of magnitude: **$50-55B over multi-year** | MED (rough estimate) | Indirect (sizing the funding gap) |
| Funded position FYTD: ~$11-12B (cash + prepayments + converts + GPU financing) | Q2 FY26 release | through 2026-02-05 | Substantial baseline — but the gap to a fully built ~$50B pipeline is the open dilution question | HIGH | Indirect |
| **Dilution offset:** Sweetwater customer prepay would reduce equity issuance need | Q3 FY26 deck | 2026-05-07 | A MSFT-style 20% prepay on a Sweetwater hyperscaler signing could fund $2-3B of IT-load capex without dilution. **The dilution burden is partly a customer-pipeline question, not just a capital-markets question.** | UPCOMING | Watch |

### Governance / insider behavior

| Signal | Source | Date | Implication | Confidence | Revenue relevance |
|--------|--------|------|-------------|------------|-------------------|
| Roberts brothers Sept 2025 ordinary share sales (NOT under 10b5-1) | SEC Form 4 | 2025-09-11 | Each sold 1,000,000 ordinary shares @ $33.131 = $33.13M (indirect, via Awassi Capital Trust #1). Pre-MSFT-deal selling — concerning pattern | HIGH | Indirect (governance signal) |
| Roberts brothers Sept 2025 stock option dispositions | SEC Form 4 | 2025-09-03, 2025-09-04 | Each disposed of 500,000 stock options on Sep 3 + 500,000 on Sep 4 (right to buy). Compounds the Sep 11 ordinary-share sales — total cash event from options + shares = ~$66M each ($33M shares + ~$33M monetized options at $33 strike vs nominal $3.27 internal strike) | HIGH | Indirect (governance signal) |
| Roberts brothers RSU/award grants | SEC Form 4 | 2025-07-01 | Each granted 1,793,392 ordinary shares as RSU/award | HIGH | Indirect (offset to sales) |
| **Roberts brothers POST-Sep 11, 2025: NO further Form 4 sales filed (through 2026-05-11)** | SEC EDGAR Section 16 | — | **Positive credibility signal.** Stock ran from $33 to $70+ over the period. No new disposals filed. Holding intact. Could be: (a) 10b5-1 plan adopted but not yet disclosed; (b) lockup tied to Microsoft deal; (c) genuine conviction holding the run-up. The absence is itself information. | MED-HIGH | Indirect |
| Australian-incorporated dual-class voting | _meta.md | through 2026 | Two B Class shares held by Roberts brothers carry 43.5% combined voting on a 4.6% economic stake | HIGH | Indirect |

---

## Channels Watchlist (Playbook for Next Refresh)

### Tier A — High signal, low effort

| Channel | URL / How | What to check | Cadence |
|---------|-----------|---------------|---------|
| IREN press releases | [iren.gcs-web.com/news-releases](https://iren.gcs-web.com/news-releases) | Sweetwater customer signings, Horizon handoff dates, capacity updates, EU/APAC progress | Weekly |
| SEC EDGAR (IREN 8-Ks) | [EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001878848&type=8-K) | Material agreements, capital raises, M&A | Weekly |
| Earnings calls (transcript + slides) | [iren.com/investors/presentations](https://iren.com/investors/presentations) | Forward guidance, Horizon phase commissioning dates, ARR contract conversion, **Sweetwater customer-language watch** | Quarterly |
| ERCOT large-load interconnection queue | [ercot.com/gridinfo](http://www.ercot.com/gridinfo) | New IREN-named projects, status changes for Childress / Sweetwater | Quarterly |
| **NVIDIA partnership announcements** | NVIDIA newsroom + IR | Updates on Blackwell deployment cadence at IREN sites | Quarterly + on NVIDIA earnings |
| **CRWV / Microsoft / NVIDIA earnings call transcripts** | each company's IR | Customer-side mentions of IREN delivery cadence, capacity ramp | Quarterly |

### Tier B — Real signal, moderate effort

| Channel | URL / How | What to check | Cadence |
|---------|-----------|---------------|---------|
| **Childress County, TX permits** | Childress County Clerk records | Foundation, electrical, mechanical permits at Horizon site (verifies "footings" / "vertical construction" claims) | Quarterly |
| **Fisher County, TX permits (Sweetwater)** | Fisher County records | Construction permits for Sweetwater 1 phase 2+ build | Quarterly |
| **Kiowa, OK county permits** | County records | Pre-construction permits for 1.6 GW site | Quarterly |
| **Spain regulatory / planning permits** (Nostrum sites) | Spanish regional planning portals | Site identification + construction permits — confirms Nostrum integration is real | Quarterly |
| Local press (Childress Index, Sweetwater Reporter, OK papers) | Manual web search | Construction milestones, hiring fairs, road work, equipment arrivals | Quarterly |
| LinkedIn — IREN by site | LinkedIn People search "IREN — Childress" / "— Sweetwater" / "— Mackenzie" | **Headcount delta** — surge at Sweetwater = commissioning ramp; >2,600 Childress baseline established Q3 FY26 | Quarterly |
| LinkedIn / Indeed job postings | Manual search | Open reqs at Childress / Sweetwater — surge = commissioning phase | Quarterly |
| H-1B disclosure data | [DOL LCA Disclosure](https://www.dol.gov/agencies/eta/foreign-labor/performance) | IREN filings for ML/network engineer / commissioning roles, work locations | Quarterly |
| **Equipment freight watch** | local press, FreightWaves SONAR (paid), DAT public | **Specifically watch for: precast concrete walls, transformers, switchgear, chillers, generators, modular electrical rooms, fuel infrastructure, steel, fiber conduit** to Sweetwater area | Quarterly |
| **Texas oversize/overweight permits** | TxDOT permit search | Heavy-haul deliveries — transformers, chillers, generators arriving at Sweetwater / Childress. **The lane-specific freight signal we wanted, public and free** | Quarterly |
| **Nolan County records** (parallel to Fisher) | Nolan County Clerk + appraisal district | Sweetwater area straddles Fisher / Nolan. Conservative cross-coverage; permits, deeds, easements, road-use approvals | Quarterly |
| **County clerk lien filings** (Childress / Fisher / Nolan) | County clerk records | Mechanic's liens / UCC filings = contractor financing patterns; late payment is an early-stress signal | Quarterly |
| **County commissioner / planning meeting minutes** | County commissioners' court agendas + minutes | Tax abatements, easements, road-use approvals, transmission line right-of-way grants — pre-construction signals before permits visible | Quarterly |
| Mirantis customer wins | Mirantis newsroom | Mirantis-stamped customer logos = IREN pipeline color | Quarterly |

### Tier C — Slower / specialty signals

| Channel | URL / How | What to check | Cadence |
|---------|-----------|---------------|---------|
| Sentinel-2 satellite imagery | [Sentinel Hub Browser](https://apps.sentinel-hub.com/eo-browser/) | Visible buildout: laydown yards, crane presence, substation sprawl. Childress + Sweetwater + new 50MW retrofit | Quarterly |
| TCEQ environmental filings | [TCEQ public records](https://www.tceq.texas.gov/) | Water/air permits at Childress + Sweetwater — pre-construction signal | Annual |
| BGP / ASN / peering | [PeeringDB](https://www.peeringdb.com/), Hurricane Electric BGP toolkit | When IREN sites announce IP space and join exchanges = network-ready for customer traffic | Quarterly |
| FERC filings (PPAs) | [FERC eLibrary](https://www.ferc.gov/) | Power purchase agreements naming IREN sites | Annual |
| Childress County deed records | County clerk | Land purchases — Project Iris Monarch verification | Quarterly |
| **Spanish wholesale electricity registry** (REE) | Spain's Red Eléctrica | Validate Nostrum's 490 MW power claims | Annual |

### What NOT to track (high noise, low signal for IREN)

- **General flatbed trucking rates** — directionally interesting but oil/gas, wind, solar, public infra all share West TX freight market. Without lane-specific data this is macro AI-infra commentary, not IREN-specific signal.
- **Bitcoin hash rate** — IREN paused mining at 50 EH/s June 2025; the BTC business is in wind-down. Hash rate changes are noise for the AI thesis.
- **Bill-of-lading data (Panjiva)** — IREN buys from Dell domestically; no significant import flow to track at IREN itself (Dell upstream may have signal).

---

## Deep mosaic — added 2026-05-11 refresh

### Aterio / third-party satellite confirmation (Tier C — but useful as independent verification)

| Signal | Source | Date | Implication | Confidence |
|---|---|---|---|---|
| **Aterio satellite intelligence (Jan 13, 2026)**: "IREN's Childress campus (leased to Microsoft) has entered a new construction phase, with satellite imagery confirming active work on Horizons 3 and 4, including concrete foundations poured for Horizon 3 and site grading underway for Horizon 4." | [aterio.io/events/iren-childress-campus-42193](https://www.aterio.io/events/iren-childress-campus-42193) | 2026-01-13 | **Independent satellite confirmation** that Horizons 3 and 4 were physically progressing (concrete poured, grading underway) BY mid-January 2026. This was 4 months before the Q3 FY26 print disclosed Horizon 1 commissioning. Validates mgmt's "repeatable build" framing — Horizons 3-4 were being prepared in parallel with Horizon 1, not sequentially. | HIGH |
| **Frans Bakker HD satellite imagery (Feb 2025)**: Horizon 1 row 1 full steel frame; row 2 mid-slab pour; row 3 green trenches; PS6 substation with dual transformers ready for ~50MW energization | [Reddit r/irenstocks community post citing Frans Bakker X imagery] | 2025-02-XX | Confirms Horizon 1 was at primary substation + steel-frame stage Feb 2025 — meets the "Q4 2025 delivery" timeline IREN guided at the time | MED-HIGH (Tier-C source, Tier-A inference) |
| **IREN official X post (Dec 2025)**: 1,200+ workers onsite; Horizon 1 electrical/mechanical advancing; Horizon 2 halls rising; Horizons 3-4 civils underway | IREN X account, cited in Reddit subscriber thread | 2025-12 | Mgmt-side workforce datapoint. >2,600 quoted on Q3 FY26 call (May 2026) suggests labor force ~doubled from Dec to May. ~3,000 quoted by CEO during the actual call. | MED (mgmt-side; Tier-B) |

### Site-tagged hiring evidence (Tier B — operational ramp signal)

LinkedIn job postings under "IREN" with location filter (verified via direct LinkedIn page checks):

| Role | Location | Posted | Source URL | Implication |
|---|---|---|---|---|
| **Mechanical Supervisor – Construction** | Childress, TX | 2025-11-05 | [linkedin.com/jobs/view/4229273263](https://www.linkedin.com/jobs/view/mechanical-supervisor-construction-at-iren-4229273263) | Direct-to-chip liquid cooling + rear-door heat exchangers experience required. 7+ years mechanical construction. **Operational confirmation that liquid-cooled buildout is at construction-supervisor staffing depth** — not just early-stage design. Pay $39-$43/hr. |
| **Electrical Engineer** | Childress, TX | 2025-07-07 | [linkedin.com/jobs/view/4263448893](https://www.linkedin.com/jobs/view/electrical-engineer-at-iren-4263448893) | Tier III mission-critical data center experience required. Texas P.Eng. Owner's representative role across HPC project life-cycle. **The hire required to scale beyond Horizon 1** to multi-phase delivery. |
| **Network Engineer, Data Center** | Childress, TX | (recent) | [jobs.weekday.works](https://jobs.weekday.works/iren-network-engineer%2C-data-center) | Fortinet/Cisco Nexus experience preferred. Fiber, switches, PDUs. **Operational network ramp** for energizing live infrastructure. |
| **Operations Manager (Trey Lee testimonial)** | Childress, TX | — | [iren.com/company/careers](https://iren.com/company/careers) | Career page confirms electrician + project manager career path on-site. Validates the "promote-from-within" claim and stable labor base. |

**Employing entity**: All Childress roles list **"IE US Operations Inc."** as the employing entity (different from property owner IE US Development Holdings 3 Inc.). This confirms the corporate-entity separation: Holdings 3 owns the land + permits; Operations runs the workforce.

### Subsidiary entity verification (Tier A — Texas Comptroller + SEC 10-K Exhibit 21.1)

| Entity | State of Inc | Texas COA File | Permit Date | Role | Confirmed in 10-K Exhibit 21.1 (Significant Subsidiaries)? |
|---|---|---|---|---|---|
| IE US Holdings Inc. | Delaware | (parent US holding) | — | US holdco | YES — significant |
| **IE US Development Holdings 3 Inc.** | **Delaware** | **0804499938** | **2022-03-14** | **Owner of 620 FM 1033, Childress (the operating site)** | **YES — significant** |
| IE US Hardware 1 Inc. | Delaware | (TX hardware leasing) | — | GPU lessee under Dell US Purchase Agreement | YES — significant |
| IE CA Leasing | (Canadian) | — | — | GPU lessee under Dell Canada Purchase Agreement | — (Canadian sub) |
| IE US Operations Inc. | Delaware | — | — | Texas employer (LinkedIn job postings) | (operating sub, separate from above) |
| "IE US Development Holdings 5 Inc. Data Center" | unconfirmed | unconfirmed | unconfirmed | datacenter.fyi entry only | **NO** — not in 10-K Exhibit 21.1 |
| "IE US Development Holdings 7 Inc. Data Center" | unconfirmed | unconfirmed | unconfirmed | datacenter.fyi entry only | **NO** — not in 10-K Exhibit 21.1 |

**Critical correction:** The previous projects.md treated Holdings 5 and 7 as candidate H2-signal entities pointing at undisclosed Texas sites. The **SEC 10-K Exhibit 21.1 lists ONLY three Holdings-numbered entities (3) as significant subsidiaries** — no Holdings 5 or 7 named. If datacenter.fyi is tracking those entities, they may be: (a) datacenter-naming-convention numbers used by the tracker, not legal entities; (b) small non-significant subsidiaries below the 10-K threshold; (c) tracker errors. **Until primary TDLR / Texas SOS records are pulled for Holdings 5 and 7, treat them as Tier-D inference, not Tier-C database evidence.** The H2 candidate hinges on Project Iris Monarch + ERCOT PGRR145-12, not on these speculative entities.

### Site utility partners (Tier B/C — datacenter.fyi corroborated by datacenter.fyi entries; primary regulatory filings still to be pulled)

| Site | Utility partner | Connection type | Source |
|---|---|---|---|
| Childress | **Greenbelt Electric Coop, INC** at distribution layer; **AEP Texas** at transmission (345kV connection per 2022 8-K, amended 2024 for +150MW) | 345kV / via on-site IREN-owned substations | [datacenter.fyi](https://www.datacenter.fyi/project/iren-childress-horizon-1-4-0f870c1f) + [2022 AEP Texas 8-K](https://www.sec.gov/Archives/edgar/data/1878848/000114036122002298/brhc10033000_ex99-1.htm) |
| Sweetwater 1 | **AEP Texas** at transmission | 1.4 GW bulk substation 345kV/138kV + primary substations 138kV/34.5kV | IREN PRs + 2025-03-17 Sweetwater 2 PR confirms AEP across the hub |
| **Sweetwater 2** | **Taylor Electric Coop INC** at distribution + AEP Texas at transmission | 600MW grid connection — non-refundable connection costs $4.1M + refundable deposits $26.9M over 12 months per March 2025 PR | [datacenter.fyi Sweetwater 2 entry](https://datacenter.fyi/public-record/iren-sweetwater-2-0e9253e3) + March 17, 2025 IREN PR |
| Mackenzie, BC | BC Hydro | Rate Schedule 1830 | _meta.md / 10-K |
| Prince George, BC | BC Hydro | Rate Schedule 1830 | _meta.md / 10-K |
| Canal Flats, BC | BC Hydro | Rate Schedule 1830 | _meta.md / 10-K |
| Kiowa/Oklahoma | (SPP grid) | TBD (1.6 GW grid studies complete) | [northwiseproject.com IREN Oklahoma analysis](https://northwiseproject.com/iren-oklahoma-site/) |

### Childress Reinvestment Zone (Tier A — Chapter 312 Texas Tax Code)

| Action | Date | Source | Implication |
|---|---|---|---|
| **Iris Energy Reinvestment Zone #1** established | June 14, 2021 | Childress County Commissioners Court | Tax abatement framework on Section 421, Abstract 208, Block H, W&NW RR Co Survey. ~416 acres core parcel. APN 11100-02864-00000-000000. |
| **Reinvestment Zone #2 (expansion)** | **October 14, 2024** | Childress County Commissioners Court | **Added ~80.12 acres within Section 421 to accommodate Horizon data center scaling and related infrastructure.** This is the regulatory paper trail for the Horizons expansion BEYOND the original 750MW envelope — material context for Project Iris Monarch and the "5GW pipeline" framing. |
| Total Childress freehold | through Q3 FY26 | iren.com/childress + Q3 FY26 10-Q | **576 acres** (Section 421 + adjacent acquisitions) |

### Spain / Nostrum Group site breakdown (Tier B — Spanish regulatory verification still partial)

Pre-acquisition (Andera Partners minority stake since 2023): Nostrum (formerly Ingenostrum) listed 6 development projects across 4 regions:

| Site | Region | Capacity (claimed) | Status |
|---|---|---|---|
| Badajoz | Extremadura | 214 MW | Development |
| **Cáceres ("CC Green")** | **Extremadura** | **220 MW requested** (currently allocated 34 MW + 9 MW urbanization; **186 MW additional REJECTED by Red Eléctrica for 2030 horizon — project deemed "not sufficiently advanced"**) | **Regulatory headwind** ([HOY article via ingenostrum.com](https://ingenostrum.com/cc-green-planea-tener-en-marcha-el-centro-de-datos-en-caceres-a-mediados-de-2027/)). Targeted operational mid-2027; €800M investment claimed. |
| Guadalajara (Pinto-area) | Castilla-La Mancha | 29 MW | Development |
| Pinto | Castilla-La Mancha | 21 MW | Development |
| Zamudio | Basque Country | 21 MW | Development |
| Galicia | Galicia | 18 MW (first 8.5MW live; expandable to 40MW) | **Partially operational** |

**Total claimed before IREN acquisition: ~321 MW. Total claimed after acquisition: 490 MW** (per Q3 FY26 release) **or 500 MW IT capacity + 300 MW expansion = 800 MW** (per Nostrum's Jan 2026 announcement). Discrepancy suggests IREN's 490MW figure represents grid-secured capacity, not site-claimed maximum.

**Regulatory headwind worth flagging**: Spanish data center development requires Red Eléctrica (REE) approval for additional grid capacity via the Plan de Desarrollo de la Red de Transporte (PDRT) cycles. CC Green's 186MW request was DENIED for the 2030 horizon — implying Nostrum's biggest project will need 2027-2030 plan approval. **The 490MW IREN claims is real but uneven**: some sites have secured connection, others are still pending REE approval. Execution timeline for full Spain ramp may be slower than the headline number implies.

**Earlier negotiation context (July 2025 BeBeez via Bloomberg)**: Nostrum was attempting to raise up to €400M ($468M) by selling stakes in development sites. CEO Gabriel Nebreda was looking for non-binding offers on up to 60% of overall data center business by end of July 2025. IREN ended up acquiring 100% for €165M — substantially below the €400M Nostrum was trying to raise. Either the market re-priced sharply (likely given Spain regulatory uncertainty), or Nebreda accepted a lower multiple to join a larger global platform.

### Australia connection agreement context (Tier A — AEMC + B — IREN guidance)

| Signal | Source | Date | Implication |
|---|---|---|---|
| **IREN CEO Daniel Roberts confirms Australian DC expansion from 2028** | [Capital Brief](https://www.capitalbrief.com/article/iren-eyes-australian-data-centre-expansion-in-2028-05aab68b-5662-4fbb-8232-027e556d620f/) | 2026-05-08 | "We have been progressing large scale Australian projects towards secured grid access for some time, and we think the opportunity here is as significant as anywhere in our portfolio." Previously Roberts was critical of Australian red tape — this is a posture change. |
| **AEMC draft rule for large data center connections to NEM** | [aemc.gov.au](https://www.aemc.gov.au/news-centre/media-releases/aemc-proposes-new-grid-standards-data-centre-connections) | 2026-03-12 | New 30MW threshold (up from 5MW) for "large inverter-based loads" requiring stricter technical standards. Aligned with Texas/Ireland/Finland practice. Submissions closed May 7, 2026. Final rule expected mid-2026. **This is the regulatory framework IREN will need to navigate.** |
| **Industry context** | Capital Brief | 2026-05-08 | Data Centres Australia CEO Belinda Dennett: "the opportunity for Australia is right here, right now." |

### BC Hydro context for Mackenzie expansion (Tier A — BC government)

| Signal | Source | Date | Implication |
|---|---|---|---|
| **BC launches competitive process for clean power in AI/data center sectors** | [bchydro.com news release](https://www.bchydro.com/news/press_centre/news_releases/2026/ai-data-centres.html) | 2026-01-30 | New "clear, transparent approach for future projects." **Affects how IREN's 80MW Mackenzie expansion + Canal Flats 30MW retrofit get approved going forward.** BC Hydro line upgrade in August 2025 already affected IREN operations (planned site outages); this competitive process is the longer-term framework. |
| **BC crypto mining connection moratorium continues** | _meta.md / 10-K | through 2026 | Dec 2022 suspension on new BC Hydro connections for crypto mining, extended in June 2024. Existing IREN operations NOT affected. **Important**: as IREN converts from ASICs to GPUs at Mackenzie + Prince George, the mining moratorium becomes less of a constraint, BUT if they wanted to add NEW BC connections that's still locked. The AI/data center competitive process is the new path. |

### Mirantis ecosystem validation (Tier B — post-acquisition)

Mirantis is the May 5, 2026 acquisition. Post-signing customer wins / validations:

| Date | Validation | Source |
|---|---|---|
| 2026-03-03 | **Mirantis + Supermicro**: k0rdent validated with Supermicro modular server architecture (AS-8126GS-TNMR + BigTwin AS-2124BT-HNTR), AMD Instinct MI325X GPUs | [mirantis.com PR](https://www.mirantis.com/company/press-center/company-news/mirantis-and-supermicro-accelerate-sovereign-ai-and-hybrid-cloud-deployments) |
| 2026-03-10 | **Mirantis + Netris**: K8s + network automation integration, hardware-enforced multi-tenancy | [mirantis.com PR](https://www.mirantis.com/company/press-center/company-news/mirantis-and-netris-unify-kubernetes-orchestration-and-network-automation-for-ai-infrastructure-operators/) |
| 2026-03-16 | **Mirantis joins NVIDIA AI Cloud Ready Initiative as founding ISV partner** | [mirantis.com PR](https://www.mirantis.com/company/press-center/company-news/mirantis-joins-nvidia-ai-cloud-ready-initiative-as-founding-isv-partner-bringing-a-validated-metal-to-model-stack-to-nvidia-cloud-partners/) |
| Existing | Mirantis serves Adobe, Ericsson, Inmarsat, MetLife, PayPal, Societe Generale | Mirantis website |
| 2026-03 | k0rdent AI validated with NVIDIA GB200 NVL72; **<0.1% performance degradation vs bare metal** (vs NVIDIA's 5% maximum threshold) | Mirantis blog |

**Implication for IREN's Mirantis acquisition logic**: Mirantis is a real software platform with enterprise customers AND deep NVIDIA validation, not a paper acquisition. The k0rdent AI control plane is the orchestration layer that lets IREN serve multi-tenant AI cloud workloads efficiently across its hardware portfolio. This is on-roadmap vertical integration, NOT a pivot or distraction.

### Competitive context at Abilene / Sweetwater (Tier B — competitor IR + DCD reporting)

The Sweetwater / Abilene region is becoming the AI data center capital of the US. IREN is NOT the only operator there. Important competitive context:

| Project | Operator | Location | Capacity | Status | Source |
|---|---|---|---|---|---|
| **Stargate One (Lancium Clean Campus)** | Lancium + Crusoe (operator) + Oracle (customer) — backed by SoftBank/OpenAI/Oracle/MGX | Abilene (Taylor County) | 1.2 GW (Phase I 200MW+ + Phase II 6 buildings ~4M sq ft) | Phase I energizing H1 2025; Phase II construction through Q1 2027; **9,000 craft workers daily** | [KTXS](https://ktxs.com/news/local/lancium-crusoe-executives-brief-abilene-leaders-on-major-northside-investment) + [DCD](https://www.datacenterdynamics.com/en/news/crusoe-begins-construction-on-second-phase-of-abilene-texas-data-center-campus-will-add-six-buildings/) |
| **Microsoft/Crusoe AI Factory** | Microsoft + Crusoe | Abilene | 900 MW + on-site power | Land clearing; switch-on mid-2027 | explainthistech.com |
| **Vantage Frontier** | Vantage Data Centers | Shackelford County | 1.4 GW / $25B | First building operational H2 2026 | explainthistech.com |
| **Crusoe Nolan County (separate from Stargate)** | Crusoe Energy Systems | Nolan County | 200 MW / $7B | **Tax abatement approved April 14, 2026** (10-year, ~$3M/yr PILT + $2M/yr charitable contributions) | [KTXS](https://ktxs.com/news/big-country/it-will-change-our-rural-town-tax-abatement-for-7-billion-texas-data-center-approved) |
| **IREN Sweetwater 1+2** | IREN | Fisher County | 2 GW (Phase 1 200MW IT under construction) | Sweetwater 1 substation energized May 1, 2026 | IREN PRs |

**Implication**: West Texas has gone from "IREN's quiet pipeline" to "one of the most competitive AI infrastructure regions globally" within ~12 months. IREN's S1 substation energization on May 1 was 1 month after Crusoe's $7B Nolan County tax abatement approval (April 14). The competitive pressure on power, land, and workforce is real — but IREN's freehold ownership and earlier secured grid commitments mitigate.

### ERCOT macro context (Tier A — ERCOT board materials)

| Signal | Source | Date | Implication |
|---|---|---|---|
| **ERCOT preliminary Long-Term Load Forecast 2026-2032** | [ercot.com](https://www.ercot.com/news/release/04152026-ercot-releases-preliminary) | 2026-04-15 | Projects ~**367,790 MW** of demand in ERCOT region by 2032. Current all-time peak: 85,508 MW (Aug 10, 2023). **>4× current peak.** Driven primarily by data centers. **ERCOT itself acknowledges this is likely overstated** ("higher than expected future load growth"). |
| **ERCOT Adjusted Large Load Forecast methodology** | ERCOT April 2025 board materials | 2025-04-07 | ERCOT now applies haircuts: 180-day in-service delay for all new large loads; **all new Data Center Load reduced to 49.8% of requested amount**; Officer Letter loads reduced to 55.4%. **Material**: ERCOT publicly assumes that data center developers (including IREN) will deliver only ~half of their requested capacity on the stated schedule. |
| **ERCOT tracking ~410 GW of large load interconnection requests; ~87% data centers** | ERCOT April 9, 2026 House State Affairs hearing | 2026-04-09 | The 5GW IREN pipeline is part of an absolutely massive queue. **Allocation is now the binding constraint.** |
| **Batch Zero process timeline** | [Foley & Lardner analysis](https://www.foley.com/p/102mnfa/ercots-proposed-batch-zero-process-what-developers-of-large-loads-need-to-kno/) | 2026-03-19 | July 15, 2026 = full project info submission deadline; Jan 29, 2027 = ERCOT delivers Batch Zero Interconnection Study results showing capacity allocations per year for 2028-2032; March 1, 2027 = developer commitment deadline; **$100,000/MW financial security required** (non-refundable, converts to interconnection fee). |

---

## Caveats

- **Mosaic ≠ certainty.** Signals like "energization announced on schedule" reduce probability of major delay; they do not confirm revenue is being recognized at the rate management is guiding. Revenue confirms only on quarterly disclosure.
- **Stage gates ≠ revenue. But Horizon 1 Microsoft handoff (Q3 CY26) IS the gate where revenue starts.** Track this gate intensely — it's the difference between "construction story" and "revenue story."
- **Sweetwater 1 has a 200MW IT load disclosed, but no customer signed.** Construction is real; revenue is optionality until a tenant contracts. Watch for language shift "negotiating" → "tenant signed."
- **Founder selling pattern** — September 2025 Roberts brothers sales (NOT under 10b5-1) ahead of November Microsoft deal warrants ongoing attention. Watch for new Form 4 filings.
- **Possible Sweetwater 2 slip 2027 → 2028.** Q3 FY26 deck implies 2028 ramp for "remaining 1,700MW Sweetwater capacity." Earnings call audio may resolve, or wait for Q4 FY26 (Aug 2026) print.
- **Project Iris Monarch (1 GW unconfirmed)** — third-party fan site claim only. Not in any IREN primary source through Q3 FY26.
- **One-quarter-removed staleness on permits and satellite** — county permit databases update quarterly; Sentinel-2 imagery is most useful as a delta over months.
- **Public sources only.** No trespassing, no hacked data, no MNPI, no private employee outreach.

---

## Sources

| Section | Primary sources |
|---------|----------------|
| Q3 FY26 print | [Q3 FY26 deck via MarketScreener](https://www.marketscreener.com/news/iren-q3-fy26-results-presentation-ce7f5bdadf88f520) · [MarketBeat](https://www.marketbeat.com/earnings/reports/2026-5-7-iris-energy-ltd-stock/) · [247WallSt context](https://247wallst.com/investing/2026/05/07/dont-focus-too-heavily-on-irens-q3-today-look-at-what-comes-next/) |
| Site portfolio | [iren.com/data-centers/childress](https://iren.com/data-centers/childress) · [/sweetwater](https://iren.com/data-centers/sweetwater) · [/oklahoma](https://iren.com/data-centers/oklahoma) |
| Microsoft contract | [SEC 8-K (signed)](https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm) · [SEC 8-K Nov 2025 exhibit](https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_ex99-1.htm) · [Reuters](https://www.reuters.com/technology/microsoft-signs-97-billion-contract-with-iren-nvidia-chips-2025-11-03/) · [MSFT contract deck](https://iren.gcs-web.com/static-files/a421bb34-0156-4687-be7d-19f53a5236e5) |
| Sweetwater 1 energization | [GlobeNewswire May 2026](https://www.globenewswire.com/news-release/2026/05/01/3286213/0/en/IREN-Announces-Successful-Energization-of-Sweetwater-1.html) · [DCD coverage](https://www.datacenterdynamics.com/en/news/iren-energizes-first-phase-of-2gw-sweetwater-data-center-campus-in-texas/) |
| Q2 FY26 results (financing detail) | [iren.gcs-web.com — Q2 FY26](https://irisenergy.gcs-web.com/news-releases/news-release-details/iren-reports-q2-fy26-results) |
| Q1 FY26 results | [iren.gcs-web.com — Q1 FY26](https://iren.gcs-web.com/news-releases/news-release-details/iren-reports-q1-fy26-results) |
| Mirantis acquisition | [GlobeNewswire May 2026](https://www.globenewswire.com/news-release/2026/05/05/3287514/0/en/IREN-Announces-Acquisition-of-Mirantis-to-Strengthen-AI-Cloud-Delivery-Capabilities.html) |
| Project Iris Monarch (UNVERIFIED) | [irenlimited.com](https://irenlimited.com/) — third-party fan site only |

## Refresh log

- 2026-05-06 — Initial population. Verified all site MW capacities, Microsoft contract terms, Sweetwater 1 energization date, Horizon 1-4 naming, Mirantis acquisition, and Q3 FY26 earnings date against IREN press releases, SEC filings, Reuters, and DCD. Flagged Project Iris Monarch as third-party-only claim. Built channels watchlist with no per-channel data pulled yet (Tier B/C are URLs to bookmark for next refresh). Audit identified 9 missing tracking items (Sweetwater customer-language watch, critical-IT-load disclosure, data-hall commissioning schedule, transmission/power-delivery ramp specifics, Sweetwater-tied equipment financing watch, customer-prepayments watch, capex-per-MW signal, hiring evidence rows, equipment-items enumeration in channels).

- 2026-05-11 — Deep-channel refresh after user feedback ("dozens of searches, no corner-cutting"). Ran ~25 fresh searches across the full channel watchlist + pulled the May 7 10-Q directly (1.96MB HTML, extracted via local script). Major additions: $11.9B commitments cliff (10-Q Note 21), ATM dilution timeline (Q1-Q3 FY26 + post-3/31 subsequent events), Nostrum price (EUR 165M / 65% cash / 35% shares), Goldman/JPM as binding commitment letter (NOT closed financing), Childress Reinvestment Zone #2 (Oct 14, 2024), Aterio Jan 13 2026 satellite confirmation, LinkedIn site-tagged hiring evidence with specific roles, IE US Development Holdings 3 Texas Comptroller record, Spain Nostrum 6-site breakdown with Red Eléctrica regulatory headwind, AEMC Australia draft rule (March 2026), BC Hydro AI/data center competitive process (Jan 30, 2026), Mirantis ecosystem validation (Supermicro, Netris, NVIDIA AI Cloud Ready Initiative founding ISV), Lancium/Crusoe/Stargate/Vantage competitive map at Abilene, ERCOT preliminary 2026-2032 load forecast + haircut methodology. Project Iris Monarch status upgraded to "CANDIDATE H2 SIGNAL — needs primary deed verification" pending direct Childress County Appraisal District query. **Corrected error**: Q3 FY26 revenue was $144.8M (not $219.69M as listed in prior refresh — that figure was wrong). **Refined entity treatment**: Holdings 5/7 entities (from datacenter.fyi) NOT in SEC 10-K Exhibit 21.1 significant-subsidiaries list — downgraded to Tier-D inference until primary records pulled.

- 2026-05-07 — Post-Q3 FY26 print (AMC 2026-05-07). Integrated Q3 disclosures + closed audit gaps surfaced in 2026-05-06 audit.

  ### What changed since last refresh (2026-05-06 → 2026-05-07)
  - **Stage gate flips:**
    - `Q3 FY26 earnings UPCOMING → DONE` (printed 2026-05-07 AMC; rev $219.69M; consensus EPS -$0.22)
    - `Sweetwater 200MW IT load construction underway` — DID NOT EXIST → DONE (new gate created and immediately confirmed)
    - `Horizon 1 commissioning underway` — DID NOT EXIST → DONE (new gate)
    - `NVIDIA second contract signed` — DID NOT EXIST → DONE (new gate; major customer #2)
    - `Nostrum acquisition (Europe entry)` — DID NOT EXIST → DONE (new gate; new geographic platform)
  - **Numerical deltas:**
    - ARR target end CY26: $3.4B → **$3.7B** (raised)
    - ARR contracted: prior smaller number → **$3.1B** under contract
    - Customer count (named hyperscaler-grade): 1 (Microsoft) → **2 (Microsoft + NVIDIA)**
    - Childress workers on site: not previously disclosed → **>2,600**
    - Sweetwater 1 critical IT load Phase 1: not disclosed → **200MW** (out of 1.4GW gross)
    - Capex per MW IT load (Childress): not previously consolidated → **$14-16M per MW** (disclosed in MSFT contract deck Nov 2025)
    - Total secured power: 4.5 GW NA → 4.5 GW NA + 490 MW Spain
  - **New evidence rows:** 16 added across Stage Gates, Childress (Q3 FY26 commissioning detail), Sweetwater 1 (200MW IT load, Vera Rubin design, language watch), Sweetwater 2 (slip watch), Childress retrofits, BC sites detail, Spain (Nostrum), APAC (Australia), Customer pipeline ($3.1B contracted, $0.7B NVIDIA).
  - **Retracted / invalidated claims:** Site name "Oklahoma" → "Kiowa" (renamed in Q3 FY26 deck — unclear if codename or location; verify). Sweetwater 2 energization 2027 status now MED-confidence due to Q3 deck implying 2028 ramp.
  - **New stage gates added:** Q3 FY26 print (DONE 2026-05-07); NVIDIA second contract signed (DONE Q3 FY26); Horizon 1 commissioning underway (DONE); Sweetwater 1 200MW IT load construction (DONE); Nostrum/Europe (DONE); Horizon 1 Microsoft handoff Q3 CY26 (UPCOMING); Horizon 2-4 end CY26 (UPCOMING); BC + Childress +180MW H2 2026 (UPCOMING); Childress 2027 +400MW (UPCOMING); Canal Flats +30MW 2027 (UPCOMING).

## What's NOT yet captured

- **Q3 FY26 earnings call audio** — would disambiguate the Sweetwater 2 2027 vs 2028 question and provide commentary on capex pacing, cash burn, dilution outlook.
- **Childress County permit pulls** — channels listed but no records actually queried. Bookmark for next refresh — would verify "footings set" / "precast walls" claims with timestamps.
- **Fisher County (Sweetwater) permit pulls** — no records queried yet.
- **ERCOT interconnection queue snapshot** — IREN sites are connected, but a snapshot of queued capacity changes would add detail.
- **Sentinel-2 imagery diff for Childress + Sweetwater** — needs visual inspection across May refresh delta.
- **LinkedIn headcount baseline by site** — Q3 FY26 deck disclosed 2,600 workers at Childress; LinkedIn could confirm IREN-employed vs contractor split.
- **NVIDIA contract disclosure in 8-K** — the $700M ARR / 5-year air-cooled Blackwell contract was mentioned in the Q3 FY26 deck. Watch for an 8-K Item 1.01 filing detailing terms.
- **Nostrum acquisition specifics** — purchase price, share count issued, Spain site addresses, specific 490MW utility partners. Check 8-K when filed.
- **Sweetwater customer pipeline color** — Q3 deck says "negotiating large-scale AI Cloud deployments across 2027 capacity." No customer names disclosed; tracking for any 8-K Item 1.01.
- **APAC project specifics** — Australian sites not yet named; submarine cable references suggest fiber strategy in development.
- **Sweetwater-tied equipment financing structure** — when first Sweetwater customer signs, customer-prepay-funded capex disclosure is the watch row.
