# IREN execution-thesis.md - Audit

**Subject file:** `vault/companies/IREN/execution-thesis.md` (refreshed 2026-05-11)
**Audit date:** 2026-05-11
**Source model:** not stated in subject file; likely Claude from the prior execution-thesis run
**Audit model:** GPT-5 Codex
**Method:** Round 1 fresh primary-source verification across SEC, ERCOT, TDLR, IREN/GlobeNewswire, and current-news sources; Round 2 whole-document structural pass focused on H2 gate discipline, tier labels, schedule-baseline language, and testability.

---

## Verdict in one paragraph

H2 was correctly not proposed: the audit found no second independent Tier-A signal proving undisclosed IREN scope beyond the public 5GW pipeline, and the closest candidate (ERCOT PGRR145-12 IREN comments) remains only a policy-process participation signal, not an IREN site-application signal. H1 broadly stands, but its evidence mix is overstated: several rows tagged `[A]` are company press releases, decks, or a transcript furnished through EDGAR and should be `[B]`, while the TDLR Childress permit verifies an operations/office building rather than a Horizon data-hall permit. H3 should be softened from "confirmed slip" to "disclosure mismatch / ramp-timing risk": the sources support 2028+ ramp language for additional Sweetwater/Kiowa data-center capacity, but IREN's website still lists Sweetwater 2 substation energization in 2027, and those two claims can coexist. A fresh May 11 financing signal also landed: IREN announced a proposed $2.0B convertible senior notes offering, plus a $300M purchaser option, which should be added to the next thesis refresh as a capital-structure execution signal.

---

## Round 1: Fresh primary-source corrections

### H2 candidate verification

- **Candidate signal:** ERCOT PGRR145-12 IREN Comments filed 2026-03-19.
  - **Audit result:** Verified that ERCOT's PGRR145 page is about the Batch Zero Process for Large Load Interconnections and lists `145PGRR-12 IREN Comments 031926` in the key documents. This verifies IREN participation in the rulemaking record.
  - **Correction:** The audit did not verify that this document names any specific IREN site, new IREN site, or capacity beyond disclosed Sweetwater/Kiowa scope. Treat it as "IREN engaged in Batch Zero policy process," not "IREN filed a site application."
  - **Primary source:** https://www.ercot.com/mktrules/issues/PGRR145

**Gate result:** H2 omission stands. The only verified Tier-A-adjacent candidate is too thin for undisclosed-scope inference.

### Other Round 1 corrections

#### Correction 1: NVIDIA 8-K watch condition already substantially cleared by the 10-Q

- **Source claim:** The H1 30-day falsifier says no IREN 8-K Item 1.01 for the NVIDIA Securities Purchase Agreement by 2026-06-10 would soften H1.
- **Corrected claim:** IREN's May 7, 2026 Form 10-Q already discloses the NVIDIA Securities Purchase Agreement, the 30M-share investment rights, the $70 exercise price, the May 7, 2031 expiry, and the NVIDIA Cloud Services Agreement. A separate 8-K Item 1.01 is no longer the right binary watch item.
- **Primary source:** https://www.sec.gov/Archives/edgar/data/1878848/000187884826000026/iren-20260331.htm
- **Hypothesis affected:** H1
- **Confidence impact:** Strengthens H1 contract-formality evidence; revise the watch item to "filed definitive exhibits / amendments or delivery-acceptance milestones," not "wait for first regulatory disclosure."

#### Correction 2: TDLR Childress permit is real but narrower than the thesis uses it

- **Source claim:** TDLR TABS2026003980 is cited as active Childress construction permit evidence supporting Horizon 1 / Childress buildout schedule.
- **Corrected claim:** The TDLR record verifies `Childress Data Center Campus Upgrades`, but the facility is `Childress Operations Building` and scope is a 29,000 SF office building with $15M estimated cost. It is a real campus-activity signal, not direct data-hall, liquid-cooling, or Horizon 1-4 construction proof.
- **Primary source:** https://www.tdlr.texas.gov/TABS/Search/Project/TABS2026003980
- **Hypothesis affected:** H1
- **Confidence impact:** H1 still stands, but do not count this row as direct Tier-A proof of Microsoft/Horizon data-center construction.

#### Correction 3: Sweetwater 2 "slip" is not cleanly proven

- **Source claim:** H3 says Sweetwater 2 / Kiowa have shifted from earlier 2027 framing to 2028 ramp, an "admission of slip."
- **Corrected claim:** IREN's Q3 FY26 release says additional Sweetwater and Kiowa data-center capacity is expected to ramp from 2028. IREN's Sweetwater page still lists Sweetwater 2 `2027 Substation Energization`. These can be reconciled as substation energization in 2027 followed by data-center capacity ramp in 2028. The evidence supports a timing mismatch and slip risk, not a confirmed slip unless the thesis distinguishes energization from revenue/data-center ramp.
- **Primary sources:** https://www.sec.gov/Archives/edgar/data/1878848/000187884826000025/irenreportsq3fy26results.htm and https://www.iren.com/data-centers/sweetwater
- **Hypothesis affected:** H3
- **Confidence impact:** Downgrade H3 from MEDIUM-HIGH to MEDIUM.

#### Correction 4: May 11 convertible offering landed after the thesis

- **Source claim:** The thesis captures capital-structure watch items but does not include a post-refresh financing announcement.
- **Corrected claim:** On 2026-05-11, IREN announced a proposed $2.0B convertible senior notes offering due 2033, plus an option for up to $300M additional principal. Use of proceeds includes capped-call costs, then general corporate purposes and working capital.
- **Primary source:** https://www.globenewswire.com/news-release/2026/05/11/3291756/0/en/IREN-Announces-Proposed-Convertible-Notes-Offering.html
- **Hypothesis affected:** H1 / capital execution caveat
- **Confidence impact:** Execution funding remains active, but dilution/debt dependency is more concrete. This does not falsify H1; it should be a financing-row addition.

#### Verified accurate: Microsoft contract core terms

- **Audit result:** The Microsoft 8-K verifies the November 2, 2025 agreement, approximate $9.7B total contract value, 20% prepay mechanics, Childress Horizon 1-4 GPU services, and delivery/acceptance process.
- **Primary source:** https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm
- **Hypothesis affected:** H1

#### Verified accurate: Sweetwater 1 energization

- **Audit result:** IREN's May 1, 2026 release verifies successful energization of Sweetwater 1's 1.4GW site and connection of the high-voltage substation to ERCOT.
- **Primary source:** https://www.globenewswire.com/news-release/2026/05/01/3286213/0/en/IREN-Announces-Successful-Energization-of-Sweetwater-1.html
- **Hypothesis affected:** H1

---

## Round 2: Structural findings

### 2a. H2 gate compliance

H2 is absent and the subject file explicitly explains why: one ERCOT candidate signal plus weaker Tier-B/C/D signals did not clear the 2+ independent Tier-A gate. That is the right outcome.

The closest-candidate description is concrete enough for the next refresh, but one phrase should be tightened: do not call the ERCOT comments "site filings" unless the underlying document names IREN-specific sites. The watch item should look for an ERCOT-published Batch Zero applicant/site list or county/TDLR/PUCT filings naming IREN entities, not generic rulemaking comments.

### 2b. Cross-hypothesis evidence overlap

| Fact | H1 frame | H2 frame | H3 frame | In source's overlap section? |
|---|---|---|---|---|
| ERCOT PGRR145 / Batch Zero | IREN engaged in Batch Zero process | closest H2 candidate | not used | yes |
| Sweetwater campus disclosures | Sweetwater 1 is progressing | not used | later Sweetwater/Kiowa capacity may be 2028+ | yes |
| 5GW NVIDIA / global pipeline | public scope validates scale | not undisclosed scope | phasing implies longer ramp | yes |

**Confidence implication:** The subject file handles most overlap correctly. The main adjustment is H3: same-campus evidence is not enough to prove slip unless the phase distinction is kept precise.

### 2c. Tier-laundering

| Row / location in source | Cited tier | Recommended tier | Why |
|---|---:|---:|---|
| Q3 FY26 SEC press release / deck used for NVIDIA contract, 5GW partnership, 2026/2027/2028 roadmap | [A] | [B], except facts repeated in Form 10-Q | The skill's own tier rule says press releases and decks are not `[A]`, even if furnished through EDGAR. Use the Form 10-Q subsequent-events disclosure as `[A]` where available. |
| Q3 FY26 earnings call transcript filed as SEC exhibit | [A] | [B] | Transcript is management commentary / direct primary output, not an independent regulatory filing. |
| TDLR TABS2026003980 as direct Childress construction proof | [A] | [A] but narrow scope | The record is regulatory, but it proves a 29,000 SF operations building, not Horizon data-hall construction. |
| IREN / GlobeNewswire Sweetwater 1 energization PR | [B] in some places, functionally treated as stronger | [B] | Direct company PR is valid primary output but not regulatory proof. |

### 2d. Inference cited as fact

- **"NVIDIA contract + 5GW partnership lands at a moment of confirmed operational execution rather than speculation."** This is reasonable synthesis, but it is an inference from financing/procurement/construction signals. Keep it, but label it as synthesis rather than a fact.
- **"Sweetwater 2 / Kiowa slip happened."** The evidence supports mismatch/ramp risk. It should not be stated as fact without separating substation energization, data-center construction, customer signing, and revenue ramp.

### 2f. Schedule baseline accuracy

Several schedule rows should preserve management's hedge language:

- `480MW total AI cloud capacity by year-end CY26` should be "2026 expansion to 480MW on track / targeted," not a hard commitment.
- `$3.7B ARR target` should retain the Q3 release caveat that it is not fully contracted and depends on delivery, commissioning, utilization, and pricing.
- `Horizon 1 Microsoft handoff - Q3 CY26` is management transcript/deck guidance and should be written as "scheduled / targeted for Q3 CY26," not a contractual date unless tied to a contract exhibit.
- `NVIDIA ramp early 2027` is target language, while the 10-Q says the three tranches are targeted for deployment during 2027 and subject to extension in certain circumstances.

### 2g. 30/60/90-day watch list specificity

The watch list is mostly testable. Two fixes:

- Replace "No NVIDIA SPA 8-K by 2026-06-10" with "confirm definitive NVIDIA agreement exhibits / any amendments and track delivery-acceptance milestones." The Form 10-Q already disclosed the agreements.
- Keep the ERCOT Batch Zero watch item, but avoid relying on the July 15 deadline unless the next refresh verifies it directly in the PGRR text or ERCOT materials. The ERCOT issue page verifies the process and IREN comments, not the deadline in the opened source.

---

## Updated confidence / gate matrix

| Hypothesis | Source state | Audit-recommended | Why |
|---|---|---|---|
| H1 On Schedule | HIGH | HIGH, with evidence-mix correction | Core contracts, financing, Sweetwater 1 energization, and Q3/10-Q disclosures support the on-schedule frame. But raw Tier-A count is overstated because press releases/decks/transcripts should be `[B]`, and TDLR is narrower than claimed. |
| H2 Ahead / Undisclosed | Not proposed | Correctly omitted | ERCOT PGRR145 IREN comments are verified as participation in Batch Zero rulemaking, but no second independent Tier-A signal and no verified site-specific undisclosed-scope filing. |
| H3 Behind / Slip | MEDIUM-HIGH | MEDIUM | 2028+ ramp language is real, but it does not conclusively contradict a 2027 Sweetwater 2 substation-energization target. Treat as disclosure mismatch / ramp-risk watch, not confirmed slip. |
| H4 Pivot | Omitted | Correctly omitted | No Tier-B+ evidence found of a pivot away from the AI-infrastructure roadmap. Mirantis/Nostrum/NVIDIA are on-roadmap expansion moves. |

---

## Recommendations

### For the next execution-thesis refresh on this ticker

- Keep H2 omitted unless a second independent Tier-A signal appears. The ERCOT comments alone should remain a candidate signal, not a hypothesis.
- Re-tier the Q3 FY26 press release/deck and earnings transcript rows from `[A]` to `[B]`; use the May 7 Form 10-Q as the `[A]` source for NVIDIA SPA, NVIDIA Cloud Services Agreement, site portfolio, financing commitments, and subsequent events.
- Rewrite the TDLR row to say it verifies a Childress operations-building project, not Horizon 1-4 data-center construction.
- Soften H3 to "Sweetwater/Kiowa ramp-timing mismatch" unless a primary source explicitly revises Sweetwater 2 substation energization from 2027 to 2028.
- Replace the NVIDIA 8-K watch item because the Form 10-Q already disclosed the NVIDIA agreements.
- Add the May 11, 2026 proposed $2.0B convertible notes offering (+$300M option) to the capital-structure / funding watch section.
- Preserve hedge language in all schedule rows: "targeting," "on track," "expected," and "subject to extension" should not be upgraded into hard commitments.

### For the execution-thesis skill itself

- Add a tiering note: EDGAR-furnished press releases, investor decks, and transcript exhibits are still company outputs; classify them as `[B]` unless the same fact appears in a Form 10-Q/10-K/8-K item disclosure or contract exhibit.
- Add a schedule-baseline check that separates substation energization, data-center construction, customer delivery acceptance, and revenue ramp. Treating these as the same milestone can create false "slip" findings.

---

## Sources

- Subject: `vault/companies/IREN/execution-thesis.md` (refreshed 2026-05-11)
- Round 1 primary-source URLs:
  - https://www.sec.gov/Archives/edgar/data/1878848/000187884826000026/iren-20260331.htm - Form 10-Q; NVIDIA SPA, NVIDIA Cloud Services Agreement, site portfolio, commitments, subsequent events
  - https://www.sec.gov/Archives/edgar/data/1878848/000187884826000025/irenreportsq3fy26results.htm - Q3 FY26 business update / roadmap language
  - https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm - Microsoft agreement 8-K
  - https://www.tdlr.texas.gov/TABS/Search/Project/TABS2026003980 - Childress TDLR project record
  - https://www.ercot.com/mktrules/issues/PGRR145 - ERCOT PGRR145 issue page and IREN comments listing
  - https://www.iren.com/data-centers/sweetwater - current Sweetwater 1 / Sweetwater 2 website dates
  - https://www.globenewswire.com/news-release/2026/05/01/3286213/0/en/IREN-Announces-Successful-Energization-of-Sweetwater-1.html - Sweetwater 1 energization
  - https://www.globenewswire.com/news-release/2026/05/07/3290760/0/en/IREN-Secures-3-4bn-AI-Cloud-Contract-with-NVIDIA.html - NVIDIA contract PR
  - https://www.globenewswire.com/news-release/2026/05/11/3291756/0/en/IREN-Announces-Proposed-Convertible-Notes-Offering.html - proposed 2033 convertible notes offering
- Cross-referenced dossier files:
  - `vault/companies/IREN/projects.md`
  - `vault/companies/IREN/_meta.md`
  - `vault/companies/IREN/financials.md`
  - `vault/companies/IREN/insider-activity.md`

Not investment advice.
