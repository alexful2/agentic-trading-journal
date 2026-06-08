---
name: execution-audit
description: >
  Adversarial post-write audit of a freshly-built `vault/companies/TICKER/execution-thesis.md`.
  Round 1 = fresh primary-source verification of consequential signals (heaviest weight on
  H2 "Ahead / Undisclosed Scope" claims since H2 has the strictest evidence gate and the
  highest decision-weight). Round 2 = whole-document structural pass (cross-hypothesis
  evidence overlap, tier-laundering, inferences cited as facts, schedule-baseline accuracy,
  H2 gate compliance). Writes `vault/companies/TICKER/execution-audit.md` with a
  self-contained verdict at the top + section-by-section corrections + an updated
  confidence/gate matrix. Designed for **agent diversity** — preferred invocation is via
  `codex` (GPT) so a different model is reading the file than wrote it. Manual trigger
  only. Usage: "audit VRT execution-thesis" or "execution-audit VRT".
---

# Execution Audit

## Purpose

The `execution-thesis` skill produces synthesis output where the highest-stakes
hypothesis (H2 — Ahead / Undisclosed Scope) is gated behind 2+ independent
Tier-A signals. The gate's whole job is to suppress confabulation at synthesis
time. This audit is the **second line of defense**: a fresh agent re-runs
primary-source searches on every cited signal (especially H2 ones) and does a
whole-document structural pass on tier-laundering, evidence overlap, inference-
as-fact, and schedule-baseline accuracy.

The audit's primary value over the source skill's own self-critique:

- **Fresh primary-source searches** — catches post-publication news the source
  writer didn't pull, mis-stated dollar figures, unverified hires/contracts, and
  H2 signals that don't actually exist as cited.
- **Whole-document structural reading** — catches patterns visible only with
  no investment in any specific hypothesis (cross-row evidence overlap that
  inflates evidence counts, tier-laundering where press releases wear Tier-A
  tags, narrative claims unsupported by inference rows).
- **Different model than the source** — a separate agent run with no shared
  priors avoids the failure mode where self-critique misses what was missed
  in composition.

## Why a separate skill (not folded into execution-thesis)

The two-agent VRT long-game audit (2026-05-08) demonstrated empirically that
~half of substantive corrections came from fresh searches the original writer
didn't run, ~half came from whole-document reading with no hypothesis
investment, and Claude vs. GPT caught largely *different* issues. Same-model
self-critique would have caught roughly half of the combined run.

The execution-thesis skill's H2 strict-gate is its own first line of defense,
but H2 is *exactly* the hypothesis where audit value is highest — wrong H2
claims will anchor user decisions hardest. Doubling up here is cheap insurance.

## When to use

- **Default:** immediately after every `execution-thesis` build/refresh on a
  ticker. Pairs naturally — running both together costs about the same as one
  longer execution-thesis run, and catches more.
- **Quarterly batch:** if a ticker's execution-thesis and audit are both >90
  days old, run both fresh.
- **Major-event trigger:** if the company announces a contract, schedule
  revision, or capacity update that the existing execution-thesis predates,
  run execution-thesis refresh + audit together.

Do **not** run the audit standalone against an execution-thesis that's >30
days stale — the audit's value comes from comparing against fresh primary
sources, and a stale source's conclusions are already in motion.

## Preferred invocation: codex (GPT) for agent diversity

**Strong preference: run via `codex` if the source was written by Claude**
(or Claude if the source was written by GPT). Same-model audit is the weakest
configuration.

```bash
# From the trading-journal repo root:
codex exec -p "Run the execution-audit skill on VRT. Read \
  .claude/skills/execution-audit/SKILL.md for the workflow. Read \
  vault/companies/VRT/execution-thesis.md as the subject document. Write \
  vault/companies/VRT/execution-audit.md."
```

If codex isn't available, run via Claude (this skill works in either model);
the agent-diversity benefit is reduced but the structural-audit pieces still
catch most of what the source missed.

## Prerequisites

- `vault/companies/TICKER/execution-thesis.md` exists (the subject document)
- `vault/companies/TICKER/projects.md` exists (cross-reference for signal
  provenance — does the cited signal actually appear in projects.md as
  claimed?)
- `vault/companies/TICKER/_meta.md` exists (for "is this consistent with SEC-
  filed facts" cross-reference)
- Helpful but optional: `insider-activity.md`, `financials.md`, `leadership.md`

If `execution-thesis.md` doesn't exist, **stop and recommend running
execution-thesis first.** The audit cannot operate on a missing source.

## Web search

Required. The audit's primary value over self-critique is fresh primary-source
checks. Prefer `mcp__claude_ai_Exa__web_search_exa` (Claude side) or whatever
web-search tool codex exposes.

**Token budget:** depth over efficiency. The previous "5-10 targeted queries"
cap is retired (see `feedback_mosaic_research_depth.md`). The 2026-05-11 VRT
audit ran ~8 searches and verified tier-discipline correctly but missed 9
substantive SEC-filed specifics (commitments cliff, Nostrum price, ATM activity,
Goldman/JPM commitment-letter wording, NVIDIA warrant vesting trigger) because
it didn't open the 10-Q text — it relied on the press release summary that the
thesis already cited.

**Round 1 target: 10-20 verification searches**, weighted toward H2 *and*
toward opening any SEC filing the thesis cites as a Tier-A anchor. **Facts-
completeness is now an audit responsibility, not just tier-discipline.**

## Workflow

### Step 1: Read the subject documents

1. `vault/companies/TICKER/execution-thesis.md` — the subject. Read fully.
2. `vault/companies/TICKER/projects.md` — for signal-provenance cross-check
3. `vault/companies/TICKER/_meta.md` — for SEC-filed-facts cross-check
4. `vault/companies/TICKER/insider-activity.md` (if exists) — bear-case
   insider-signal claims often need this
5. `vault/companies/TICKER/financials.md` (if exists) — for any ARR / revenue
   / cash-burn figures cited

Selective reads only. Don't re-read every dossier file.

### Step 2: Identify the audit-priority claim list

Triage the claims in execution-thesis.md by audit weight. **H2 claims are
always top priority** because they're the highest-stakes output mode and the
gate is the source's only confabulation defense.

Priority order:
1. **Every H2 evidence row** — verify each cited Tier-A signal independently
   exists at the cited URL and says what the source claims it says.
2. **Schedule baseline (Step 2 in execution-thesis spec)** — does the cited
   management commitment actually appear in the cited primary source?
3. **H1 and H3 evidence rows where the verdict hinges on a small number of
   signals** — a single mis-cited Tier-A row can flip a HIGH to MEDIUM.
4. **H4 Pivot evidence** if H4 is present.
5. **Fresh news that landed *after* execution-thesis.md was written** —
   especially if the file is >7 days old.

### Step 3: Round 1 — Fresh primary-source verification searches (10-20 queries)

For each priority claim, run targeted searches aimed at the primary source.
Coverage discipline:

**3a. Open every SEC filing the thesis cites as a Tier-A anchor.** Don't
verify by URL alone — actually pull the filing text via WebFetch and extract
material specifics the thesis may have missed:
- Commitments balances on the balance sheet (and the prior-period figure for
  comparison)
- Share count at the **most recent disclosed date** (often later than the
  prior 10-Q's date — e.g., a cover-page count current to a date in the next
  quarter)
- ATM / shelf activity in the subsequent-events note
- Contract specifics: payment terms, vesting triggers, tranche structure,
  expiry dates, conditions precedent
- Financing-letter-vs-closed distinctions (a "commitment letter" is not yet
  closed financing; the thesis must word this carefully)
- ARR / revenue bridge composition (what's contracted vs. what's assumed)

If the thesis cites a 10-Q or 10-K and missed ≥3 substantive specifics that a
direct read would surface, **flag as a facts-completeness miss** — this is a
new audit category alongside tier-discipline.

**3b. Heavy weight on H2 verification.** If H2 is present, verify both
Tier-A signals on the gate independently. If either signal doesn't verify
cleanly:
- The H2 hypothesis fails the gate retroactively.
- The audit must explicitly recommend retraction of H2 in the next
  execution-thesis refresh.

**3c. For H1 / H3 / H4**, weight by which signals are doing the most work
in the hypothesis (typically the Tier-A rows). Secondary B/C rows can stay
un-checked in Round 1 only if the corresponding Tier-A row already verified.

**3d. Fresh post-publication news.** Search for any material company news
between the thesis's last-refreshed date and the audit date. Anything that
materially affects a hypothesis should be flagged for the next refresh.

**Parallel cap:** ≤5 searches per tool-call batch. Run 2-4 batches.

**Expected output of Round 1:** a list of factual deltas (mis-stated,
unverified, or contradicted) + a list of **facts-completeness misses**
(specifics in cited SEC filings the thesis didn't extract) + a list of
"verified accurate" for the most consequential rows.

### Step 4: Round 2 — Whole-document structural pass (no searches)

Working through execution-thesis.md as a single document, flag:

#### 4a. H2 gate compliance check

If H2 is present:
- Are 2+ Tier-A signals explicitly cited in the gate-verification subsection?
- Are the two signals from **different** agencies / filing types?
- Does the source explicitly state how the two signals are independent?

If any of the three checks fails, flag as gate-non-compliance. The skill's
Step 5a is non-negotiable; the audit enforces compliance.

If H2 was correctly omitted (with the "H2 not proposed this refresh" note),
verify the closest-candidate-signal description is concrete enough that the
next refresh can act on it.

#### 4b. Cross-hypothesis evidence overlap

Walk the evidence rows and build the overlap table. Compare against the
source's own "Cross-hypothesis evidence overlap" section. Flag:
- Rows the source's overlap section missed (same fact appears in 2+
  hypotheses with different framings, but isn't in the source's table)
- Confidence not adjusted for overlap (if a hypothesis's de-duplicated
  evidence base is materially smaller than its raw count, did the source
  drop confidence half a tier?)

#### 4c. Tier-laundering

Walk through the evidence rows. For each [A] tag, verify the cited URL
points to a primary regulatory filing (SEC EDGAR, ERCOT, county permit,
PUCT, FCC, etc.). For each [B] tag, verify the URL points to a direct
primary output (company/vendor PR, IR page, careers page, USPTO).

Flag:
- [A] tag pointing to a press release, deck, or interview (downgrade to [B])
- [B] tag pointing to a secondary outlet (mainstream news, AInvest, Substack,
  LinkedIn-tracker) without a primary URL also cited (downgrade to [C])
- [C] tag where the row is actually inference, not a cited fact (downgrade
  to [D])
- [A] fact that is directionally right but cited through a mirror/media URL
  instead of the direct primary source (keep only if the direct primary source
  verifies; otherwise flag as both tier-discipline and source-hygiene miss)

#### 4d. Inference cited as fact

Look for narrative claims in the Description sections that aren't supported
by an explicit Tier-D inference row. Common patterns:
- "The hiring pattern is the tell" → must have a Tier-D row admitting
  inference, not a fact.
- "Management is being deliberately vague about X" → if no Tier-A signal
  contradicts mgmt, this is interpretation not fact, needs Tier-D row.

If a Description claim is more aggressive than the evidence rows support,
flag it.

#### 4e. Hire / role / status verification

For every claimed role, employer, partnership, or status, ask: is there a
primary VRT-side (or counterparty-side) source confirming this? Flag
anything resting on secondary observations (LinkedIn-tracker, podcast
mention, etc) without primary corroboration.

#### 4f. Schedule baseline accuracy

Verify the Schedule baseline section's dated commitments against the cited
primary source. Common failure mode: paraphrasing a guidance range as a
firm date. If management said "expected in Q3 CY26," that's not a "Q3
CY26 commitment" — the schedule baseline should preserve hedge language.

#### 4g. 30/60/90-day watch list specificity

Before moving on, verify that any **numeric watch threshold** in the thesis or upstream Variable Map
still uses the latest primary-source baseline. If the baseline moved but the threshold did not, flag
a recalibration miss.

Are the watch-list signals concrete enough that the next refresh can
definitively check whether they happened? Flag any vague entries
("watch for slip indicators") that wouldn't be testable.

#### 4h. Variable Map fit + coverage (added 2026-05-11)

Open `vault/companies/TICKER/projects.md` and read the Variable Map at the top. Three checks:

1. **Does the Variable Map fit the company's actual business?** A Variable Map dominated by
   "Physical buildout" channels for a pure-software company is mis-scaffolded. Look at the patterns
   claimed in the map vs. what `_meta.md` + `overview.md` say the business actually is. Flag any
   pattern that looks shoehorned or any missing pattern that's obvious from the dossier (e.g.,
   "post-IPO lockup" missing from a company that IPO'd 6 months ago; "hyperscaler concentration"
   missing from a company with 70%+ revenue from one named customer).

2. **Did searches actually cover the mapped channels?** Read the Search Coverage Ledger in
   projects.md. For each `Active execution variable` in the map, check whether its **Primary
   channels** (Tier-A targets) have entries in the Coverage Ledger. If a Primary channel for a
   high-weight variable is missing from the Ledger (not "Kept" or "Dropped" or "Defer" — just
   absent), flag it. **Untested Tier-A primary channels are an audit miss equivalent to
   tier-laundering** — both inflate the apparent evidence base. Common offenders: county deed
   records, lane-specific freight permits, state agency dockets, peer-reviewed databases.

   **Physical-buildout maturity check:** if Physical buildout is claimed, verify that the ledger
   contains at least one real site-verification batch before accepting `mature` status or HIGH
   physical-buildout confidence. A real site-verification batch means 2+ independent non-management
   physical channels across active sites (permits, utility/interconnection dockets, environmental
   permits, deed records, contractor liens, EPC/vendor records, or saved satellite imagery). Web-index
   searches that merely fail to reach the direct agency/satellite record count as `Defer`, not as
   coverage. If all physical channels are `Defer`, write: "Physical buildout coverage is searched but
   not independently site-verified; map may be `searched` but not `mature`."

3. **Are obvious patterns from the vocabulary missing?** The 9-pattern controlled vocabulary
   (Physical buildout, Hyperscaler concentration, Enterprise SaaS, Clinical credibility, Regulated
   rollout, Engagement, Capital structure, Post-IPO lockup, Restructuring) covers most companies.
   If the company exhibits a pattern not claimed in its Variable Map, recommend adding it on the
   next `company-projects` refresh. The audit doesn't modify projects.md — it surfaces the gap.

Output format: a 4h subsection in the audit with bulleted findings. If no issues: write "Variable
Map fits company; all high-priority mapped channels covered in Coverage Ledger; no missing
patterns."

### Step 5: Updated confidence / gate matrix

For each hypothesis, compute the audit's recommended confidence:

| Hypothesis | Source confidence / gate status | Audit-recommended | Why |
|---|---|---|---|
| H1 On Schedule | {source state} | {audit state} | {brief reason} |
| H2 Ahead / Undisclosed | {gate cleared / not proposed} | {audit-verified gate / gate-fails-on-audit} | {which Tier-A signal failed verification, if any} |
| H3 Behind / Slip | ... | ... | ... |
| H4 Pivot | ... (or N/A if not in source) | ... | ... |

The recommended state may match the source. State the reason in either case.

### Step 6: Write `execution-audit.md`

**Path:** `vault/companies/TICKER/execution-audit.md` (deterministic name —
overwrites prior audit on each run; no date stamp).

**Required sections in order:**

1. **Header** — subject file path, audit date, source-model + audit-model
   (e.g., "Source: Claude Opus 4.7 / Audit: GPT via codex"), method (one
   paragraph)
2. **Verdict in one paragraph** — self-contained summary so a reader can
   skip the source file. Lead with H2 gate status (cleared and verified /
   cleared at synthesis but failed audit / correctly not proposed). The
   most important section.
3. **Round 1: Fresh primary-source corrections** — each correction with
   the original claim, the corrected claim, and the primary-source URL.
   For H2 verification, explicitly list each Tier-A signal as verified or
   failed.
4. **Round 2: Structural findings** — sub-sections for 4a-4g from Step 4,
   only including those with findings (omit empty subsections).
5. **Updated confidence / gate matrix** — table from Step 5.
6. **Recommendations**, divided into:
   - **For the next execution-thesis refresh** — what corrections to fold
     in (especially H2 retraction if the audit failed the gate)
   - **For the execution-thesis skill itself** — patterns worth folding in
     to the skill spec if observed across multiple tickers (most audits
     won't produce skill-level recommendations)
7. **Sources** — URLs from Round 1 fresh searches; subject document path

### Step 7: Verify file integrity

Before reporting complete:

1. File exists at `vault/companies/TICKER/execution-audit.md`
2. Verdict paragraph is self-contained and leads with H2 gate status
3. Round 1 has at least 3 verifications (corrections OR explicit "verified
   accurate") — H2 evidence rows ALWAYS individually verified if H2 present
4. Round 2 has at least one finding under one of 4a-4g, OR an explicit "no
   structural issues found" line per subsection
5. Updated confidence / gate matrix present
6. Recommendations section present
7. If the audit recommends H2 retraction, that recommendation is the FIRST
   bullet under "For the next execution-thesis refresh"

## Constraints

- **Public sources only.** Same as execution-thesis: standard mosaic-theory
  ethics.
- **No re-write of the source.** This skill writes only `execution-audit.md`,
  never modifies `execution-thesis.md`. Folding corrections into the source
  is the next execution-thesis refresh's job.
- **Self-contained verdict required.** The top-of-file paragraph must stand
  alone. The user reads the audit; they shouldn't have to read both files
  to get the conclusions.
- **H2 verification is non-skippable.** If H2 is present in the source,
  every Tier-A gate signal must be individually verified in Round 1. No
  exceptions for budget reasons.
- **Don't manufacture findings.** If Round 1 surfaces no factual deltas,
  state so. Padding the audit with weak corrections defeats the purpose. If
  the source is genuinely solid, the audit should say so and be short.

## Output ownership

`vault/companies/TICKER/execution-audit.md` is owned by this skill. The
**next execution-thesis refresh reads the audit as input** and folds
corrections into the new execution-thesis.md. After that refresh, the prior
audit is historical — overwrite on the next audit run.

## Consumed by

| Consumer | What it reads | Why |
|----------|---------------|-----|
| Next `execution-thesis` refresh on the same ticker | Round 1 corrections + Round 2 findings + Updated confidence/gate matrix | Folds corrections into the new file without re-running the audit's searches; the refresh log "What changed since last refresh" should cite the audit findings explicitly |
| `quarterly-review` | Refresh log entries across audited tickers | System-calibration: are the audits catching the same issues every quarter (= persistent skill blind spot) or different issues (= execution-thesis is working as designed and audits are catching event-driven drift). H2 retraction frequency is a key calibration signal — if H2 retracts >30% of the time, the skill's gate is too lenient. |

## What this skill does NOT do

- **Does not modify `execution-thesis.md`.** Audit is a separate file.
- **Does not produce a stock verdict.** Same as execution-thesis. The audit's
  "verdict" is on the execution-thesis's logical/factual soundness, not on
  the company's prospects.
- **Does not auto-refresh.** Manual trigger only.
- **Does not run on tickers without an existing execution-thesis.md.**
- **Does not iterate beyond Round 1 + Round 2.**
- **Does not write to `notes/`, `library/`, `reports/`, or other dossier
  files.** Only writes `vault/companies/TICKER/execution-audit.md`.

## Reference

- **Normative template:** `.claude/skills/execution-audit/references/execution-audit-template.md`
- **Predecessor:** the `long-game-audit` skill (retired 2026-05-08). Its
  output template `long-game-audit-template.md` and the example output
  `vault/companies/VRT/long-game-meta-2026-05-08.md` (a manual two-agent
  meta-audit) inform this skill's design but are no longer the canonical
  format.

History:
- v1 (2026-05-08): initial build, replacing the retired `long-game-audit`.
  Same Round 1 + Round 2 structure as the predecessor, but the priority
  list is reweighted toward H2 verification (the strictest-gated and
  highest-decision-weight hypothesis), and Round 2 adds new sub-checks
  4a (H2 gate compliance) and 4f (schedule baseline accuracy) specific to
  the execution-thesis output shape.
