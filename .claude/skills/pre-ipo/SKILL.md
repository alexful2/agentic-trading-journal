---
name: pre-ipo
description: >
  On-demand pre-IPO research for an upcoming offering. Reads the S-1-derived
  company dossier and synthesizes a trade-shape decision: SUBSCRIBE IF
  ELIGIBLE / WATCH FOR OPEN-AND-FLIP / WATCH FOR D30 ENTRY / WATCH FOR
  LOCKUP DIP / BUILD VIA TRANCHES / SKIP. Two modes: initial (run any time
  >2 trading days before pricing) and gate (run T-1 or day-of, after
  pricing announcement). Mode auto-detects from the expected date in
  vault/ipo-calendar.md. Force explicitly: "pre-ipo VLT" (auto),
  "pre-ipo VLT gate", "pre-ipo VLT initial", or "pre-ipo VoltaGrid"
  (company name fallback when the proposed ticker isn't pinned).
  Requires a row in vault/ipo-calendar.md (added by vault-curator
  Friday IPO Radar or manually). The dossier at
  vault/companies/{PROPOSED_TICKER_OR_SLUG}/ is built inline if
  missing — no separate command needed.
---

# Pre-IPO

## Purpose

Answer the time-boxed question: **"For this specific upcoming IPO, which
of the four trade shapes — if any — actually applies, and what are the
exact pre-commit conditions for it?"**

This is not a deep-dive. Deep-dive answers "should I hold/add/reduce at
today's price" — and IPOs don't have a today price yet. Pre-IPO answers
"given an upcoming offering, is the right play to subscribe, flip on day 1,
wait for the day-30 quiet-period dip, wait for the 180-day lockup, build
slowly, or skip — and on what conditions does that decision flip?"

The five trade shapes (the verdict picks one, or `WATCH FOR PRICING` /
`SKIP`):

| Verdict | Bet | When it applies |
|---|---|---|
| `SUBSCRIBE IF ELIGIBLE` | Get allocated at the IPO price | Tier-1 underwriter, RH IPO Access eligible, thesis fit, modest book size — institutions get most of it but retail allocation isn't zero |
| `WATCH FOR OPEN-AND-FLIP` | Buy first print, sell within 1–3 days | Hot regime (recent peer IPOs popped and held), small float (<15%), priced at high end / above range, thesis-fit not required |
| `WATCH FOR D30 ENTRY` | Wait ~25 trading days, buy quiet-period dip | Lukewarm regime, thesis-fit candidate where the IPO premium fades into the analyst-coverage launch — historically the most repeatable retail entry |
| `WATCH FOR LOCKUP DIP` | Wait ~180 days, buy into insider-selling pressure | Heavy VC overhang, thesis-fit candidate, willing to wait 6 months |
| `BUILD VIA TRANCHES` | Long-term position via multiple entries | Strong thesis fit, valuation reasonable at indicated range, ready to hold through volatility |
| `SKIP` | Don't participate at any entry shape | Thesis fit fails, or pricing/regime/fundamentals don't support any of the above |
| `WATCH FOR PRICING` | Defer final call to gate mode | Initial-mode-only — pricing matters too much to call it definitively before the announcement |

The skill stays neutral on which trade shape is "best." It evaluates each
against the specific IPO and lets the user pick.

---

## Workflow

### Step 0: Preconditions & Mode Detection

**0a. Parse arguments.**
- `"pre-ipo VLT"` → auto-detect mode
- `"pre-ipo VLT gate"` → force gate
- `"pre-ipo VLT initial"` → force initial
- `"pre-ipo VoltaGrid"` → company-name fallback (when the row's `Ticker`
  is `TBD`); resolve to the matching calendar row by company name

**0b. Require an `ipo-calendar.md` row.**
Read `vault/ipo-calendar.md`. Find the row matching the argument
(`Ticker` exact, then `Company` exact, then `Company` startswith).

- **No match:** stop. Output:
  > `No row found in vault/ipo-calendar.md for "{arg}". Add a row manually
  > or wait for the next vault-curator run to surface this candidate, then
  > re-run pre-ipo.`
- **Match found:** extract `Ticker` (may be `TBD`), `Company`, `Expected
  Date`, `Range`, `Lead UW`, `Sector`, `Thesis Fit`, `Skill Run`, `Source`.

**0c. Resolve (and auto-build if missing) the dossier.** Resolve the dossier
folder by:
- `vault/companies/{Ticker}/` if `Ticker` is not `TBD`
- otherwise `vault/companies/{COMPANY-SLUG}/` (uppercased, spaces → hyphens)

If the folder doesn't exist or `_meta.md` is missing, **auto-build the
dossier inline** by following `.claude/skills/company-dossier/SKILL.md`
in pre-IPO mode. The user's `pre-ipo` invocation is the consumer signal
that justifies the EDGAR pull — don't make them run a second command.

To auto-build:
- Surface a one-line status to chat: `No dossier on file — building one
  inline before research (this hits EDGAR; ~1–2 min).`
- Resolve the CIK. If the user provided one in the invocation, use it.
  Otherwise look up via the SEC ticker map
  (`https://www.sec.gov/files/company_tickers.json`) — pre-IPO companies
  with a proposed ticker often appear there once they file the S-1. If
  the lookup fails (no proposed ticker yet, name not in the map), stop
  and ask the user for the CIK explicitly. Don't guess.
- Run the full pre-IPO-mode workflow from `company-dossier/SKILL.md`
  (Steps 1–7), writing all 8 files plus the `expected_ipo_date:` /
  `cik:` / `s1_filed:` / `ipo_status:` fields in `_meta.md`.
- After the dossier is written, continue Step 0d below.

**Refresh path** (dossier exists but is stale): if `_meta.md`'s last
refresh date is >30 days ago AND there's a known S-1/A amendment or
pricing announcement since (you'll see this in the calendar row's
`Range` column changing, or in any prior pre-ipo file's open questions),
auto-refresh the dossier the same way. The 30-day window is intentionally
tighter than public-company dossier staleness because pre-IPO data shifts
fast.

**0d. Detect mode (if auto).**
- `expected_date − today` = trading days until pricing.
- `≤ 2 trading days` → **gate mode**.
- `> 2 trading days` → **initial mode**.
- If `Expected Date` is `TBD`, default to initial mode and flag in the
  output that the date isn't pinned yet — the gate run can't be scheduled
  until the date firms.

**0e. Staleness & filename resolution.**
- Filename root is the proposed ticker if known, otherwise the company
  slug (e.g., `VOLTAGRID`).
- Initial mode target: `vault/reports/pre-ipo/{ROOT}-{EXPECTED_DATE}-initial.md`.
- Gate mode target: `vault/reports/pre-ipo/{ROOT}-{EXPECTED_DATE}-gate.md`.

If the target file already exists **and was written today**, stop and
surface the Verdict + Pre-Commit Plan section. The user can say "rerun"
to overwrite.

If gate mode is requested but no initial file exists for this expected
date, run initial mode first, then gate mode — two files, written in
sequence.

If the expected date in the calendar row has changed since an existing
initial file was written, re-run initial mode (don't reuse the old
target file's date in the path — match the current calendar row).

### Step 1: Load Context

**From the dossier — selective reads:**
- `vault/companies/{root}/_meta.md` — proposed ticker, CIK, S-1 filing
  history, expected_ipo_date / confidence, ipo_status. Age check: if
  last refreshed >30 days ago AND there's been a known S-1/A amendment
  or pricing update since, flag at the top of the output and suggest a
  dossier refresh before continuing. (Pre-IPO data shifts faster than
  public-company data — tighter staleness window.)
- `vault/companies/{root}/overview.md` — what the company does. The
  one-paragraph plain-English summary feeds the report's "What the
  company does" section.
- `vault/companies/{root}/financials.md` — S-1 audited financials,
  customer concentration, use of proceeds.
- `vault/companies/{root}/risks.md` — distilled S-1 Item 1A risk
  factors. Cross-reference the named risks with the thesis-fit angle.
- `vault/companies/{root}/leadership.md` — founder profile, board,
  governance characteristics.
- `vault/companies/{root}/compensation.md` — exec comp structure,
  equity plan, severance — for governance/alignment read.
- `vault/companies/{root}/ownership.md` — principal stockholders, dual-
  class structure if any, expected post-IPO ownership %, lockup terms.
- Skip `insider-activity.md` if it's a placeholder (typical pre-IPO).
  Read it only if the dossier notes Form 3s or other pre-IPO insider
  data already on file.

**From the rest of the vault — narrow reads:**
- `vault/notes/` — read only files whose name contains the company name,
  the proposed ticker, or `IPO`. Sort by date desc. Read the most recent
  2–3. Use these to detect any prior thinking the user has written about
  this name (often nothing, since pre-IPO names rarely have notes yet).
- `vault/library/Wait-for-deal thesis.md` — read in full if the sector is
  AI infrastructure (compute, power, DC, networking, cooling). The
  wait-for-deal lens is directly relevant to most pre-IPO candidates the
  curator surfaces.
- `vault/library/` — list filenames. Read any file whose name suggests a
  relevant framework (e.g., `Broader AI beliefs.md`, `Opportunity-cost lens.md`).
  Don't preload the whole directory.
- `vault/watchlist.md` — full file. Use Tier 1 / Tier 2 lists as the
  comparison set when reasoning about portfolio fit.
- `vault/deep-dives/` — for each sector peer named in the dossier's
  `overview.md` or `financials.md` ("comparable companies" section, if
  present) that's already in the watchlist, read the most recent
  deep-dive file. Extract verdict, current valuation snapshot, and
  thesis check. These are the public-comp anchors for the valuation
  section. Cap at 3 peers.
- `vault/reports/daily/` — list the last 14 daily reports. Read any
  whose body mentions the company or the sector tag. Skim for sector
  regime signals (recent IPOs in the sector trading well or poorly).
- `vault/reports/pre-ipo/{ROOT}-*.md` — any prior run for this company
  (different expected date, or initial vs gate). Use the most recent as
  context for "what did we conclude before; has the picture changed."

**Do not read** the full `notes/` or `library/`. Pre-IPO is scoped to
the offering question plus the public peers used as comp anchors.

### Step 2: Targeted Research (Exa searches)

**Search tool:** Use `web_search_exa`. Fall back to `WebSearch` if Exa
MCP is unavailable.

**Initial mode — 4 searches:**
1. `"{Company} IPO S-1 highlights {year}"` — surfaces analysis pieces
   covering the offering thesis. Often catches reporters' angles the
   dossier doesn't.
2. `"{Company} IPO roadshow demand cornerstone"` — anchor investor
   commitments, oversubscription chatter, lead-investor signals.
3. `"{sector} IPO {year} performance day 1 day 30"` — regime check.
   Recent IPOs in the same lane: did they pop, hold, fade? This is
   half the trade.
4. `"{Company} competitors valuation comparable"` — public-company
   comp set for the valuation section (P/S, EV/Sales, growth rate
   comparisons).

**Gate mode — adds 2 searches (5 total):**
5. `"{Company} IPO pricing announcement"` — final price, range
   movement (above / at / below indicated range). The single biggest
   day-1 signal.
6. `"{Company} IPO oversubscription demand"` — late demand reads,
   any IFR / Bloomberg leaks of book multiples.

**Batching:** keep parallel tool blocks ≤5 (per the project's
parallel-cap memory). Run searches sequentially or in groups of ≤5;
don't dispatch all in one block alongside file reads.

**For all searches:** capture the URL of the strongest result for
citation in the report. Don't fabricate; if a search returns nothing
useful (real risk for pre-IPO names), say so and move on.

### Step 3: Build the Report

Use the template at `references/pre-ipo-template.md`. Same actionable-
above-rule layout as pre-earnings and deep-dive.

**Write sequence matters:** analyze the reference sections first (you
need the facts), then write the actionable sections last (you need the
analysis to write the verdict).

---

**Actionable (top of file, above the rule):**

**3a. Snapshot** — compact table: proposed ticker / company / expected
date / indicated range / lead UW tier / sector / thesis fit / cornerstone
investors named / lockup expiry / quiet-period end / dossier age / last
pre-ipo run if any.

**3b. Verdict** — one of `SKIP` / `WATCH FOR PRICING` / `SUBSCRIBE IF
ELIGIBLE` / `WATCH FOR OPEN-AND-FLIP` / `WATCH FOR D30 ENTRY` /
`WATCH FOR LOCKUP DIP` / `BUILD VIA TRANCHES`. One sentence on why; one
sentence on what would change it (the failure mode that flips the verdict
to `SKIP` or to a different shape).

**3c. Pre-Commit Plan** — 2–5 lines. Concrete conditional orders or
watch levels keyed to the verdict. Examples:
- For `SUBSCRIBE IF ELIGIBLE`: "Place IPO Access request through Robinhood
  by {date}. Sizing: {N% of portfolio} if filled. If not filled, fall
  through to {next-best verdict}."
- For `WATCH FOR OPEN-AND-FLIP`: "If priced at high end / above range,
  monitor pre-market indication. Buy at $X if first print is <{X% over
  IPO price}; abort if indication is >{Y%}. Sell into $Z or by EOD-{N}."
- For `WATCH FOR D30 ENTRY`: "Set price alert at $X for ~{date + 25 TD}.
  Re-evaluate with fresh deep-dive once trading starts."
- For `BUILD VIA TRANCHES`: "Tranche 1 at $X (initial position); Tranche 2
  at $Y (post-quiet-period); Tranche 3 at $Z (post-lockup). Total
  target: {N% portfolio}."

**3d. Trade-Shape Decision Matrix** — table with each of the four
non-SKIP shapes, and for each: does it apply here, what's the supporting
signal, what's the disqualifier. The verdict in 3b is the row that
"applies cleanly"; the matrix shows the work.

**3e. Gate Update** — populated in gate mode only. Blank/omitted in
initial mode.

---

**Reference (bottom of file, below the rule):**

**3f. What the company does** — 1 paragraph from `overview.md`, plain
English. No marketing-speak.

**3g. Thesis fit** — does the company fit the AI infrastructure /
power-constrained / wait-for-deal lens? Cite the relevant library files.
If the thesis fit fails (the calendar's "Thesis Fit" was misjudged), say
so explicitly — that often flips the verdict to `SKIP`.

**3h. The S-1 essentials** — table:
- Revenue (last full year + most recent stub)
- Revenue growth rate YoY
- Gross margin
- GAAP profit/loss
- Cash burn rate (if loss-making) and cash runway post-IPO
- Customer concentration (top-10 customer %)
- Use of proceeds (growth investment / debt paydown / cash-out)
- Dual-class structure (yes/no, vote ratio if yes)

**3i. Quality of the offering** — narrative:
- Underwriter tier (Tier 1: GS / MS / JPM / BofA / Citi / WFC; Tier 2:
  the rest). Lead bookrunner matters most.
- Cornerstone / anchor investors named in the prospectus or roadshow
  reporting (Fidelity, T. Rowe, Tiger, Coatue, Sequoia, etc.).
- Insider/VC selling at IPO: primary (new shares from company) vs.
  secondary (existing shareholders cashing out). Heavy secondary at IPO
  is a tell.
- Lockup terms (typical 180 days; sometimes shorter for hot deals).

**3j. Comp regime check** — last 3–5 IPOs in the same sector in the
past 6–12 months. Table:
| Ticker | IPO Date | IPO Price | Day-1 Close | Day-30 Close | Today | Day-1 Pop % | D30 vs IPO % | Today vs IPO % |
This is the regime tell. **If the regime is bad (last 3 in sector are
underwater vs IPO price), open-and-flip is structurally unfavorable
regardless of fit.**

**3k. Comp valuation** — at the indicated price range, compute
implied market cap / EV / P-S vs. 2–3 nearest public peers (from the
deep-dive files read in Step 1). Is it priced at peer multiples,
premium, or discount?

**3l. Lockup & quiet-period calendar** — three dates:
- Expected pricing: {Expected Date}
- Quiet period ends: ~25 trading days after pricing (analyst
  initiations launch — often a volatility event)
- Lockup expires: ~180 calendar days after pricing (insider/VC
  selling pressure)

**3m. Risks & red flags** — distilled from `risks.md`, with the
emphasis on items that would flip the verdict. Examples: customer
concentration > 30%, dual-class with founder controlling >50%,
GAAP loss expanding YoY, secondary share % > 30% of offering,
litigation overhang.

**3n. Council pass — three lenses** — short, one paragraph each:
- **Contrarian:** what's the strongest case this IPO breaks issue
  or fades after day 1?
- **Bull:** what's the strongest case it pops and holds?
- **First-Principles:** strip the IPO frame entirely — if this were
  already public at the indicated price, would it be a buy?

**3o. Open questions** — 3–5 specific items that, if answered between
now and the gate run, would flip or sharpen the verdict. Examples:
"Will any cornerstone investors be confirmed in the 424A?" "Will the
range be raised, held, or cut?" "Will Anthropic / OpenAI announce a
partnership in the pre-IPO window?"

**3p. Proposed Watchlist Updates** *(only if the IPO graduates to a
holding plan — i.e., verdict is `BUILD VIA TRANCHES`, `WATCH FOR D30
ENTRY`, or `WATCH FOR LOCKUP DIP`)* — appended at the bottom. Same
format as the `stock-deep-dive` and `pre-earnings` blocks. After the
file is written, Step 5b (below) runs the shared apply script to
write the proposals directly into `vault/watchlist.md`'s
`## Planned Tranches` table. The block in this file is the audit trail.

Scoping rules — pre-IPO proposals are date-anchored to either the
post-IPO trade shape:

- For `BUILD VIA TRANCHES`: emit `Add:` lines for the planned
  tranches with `Conditional GTC` order type. Note column should
  cite the trade-shape (e.g., `tranche 1 of 3 — initial position
  post-IPO`). Expiries: anchor to `expected_ipo_date + 60 days`
  (gives time for the post-IPO trading to settle and for the
  user to fold in a fresh deep-dive).
- For `WATCH FOR D30 ENTRY`: emit a single `Add:` line with
  `Alert` order type at the post-quiet-period entry price.
  Expiry: `expected_ipo_date + 50 days`.
- For `WATCH FOR LOCKUP DIP`: emit a `Conditional GTC` line at
  the lockup-window entry price. Expiry: `expected_ipo_date +
  210 days`.
- Do **not** emit Buy Below / Trim Above (Price Trigger) lines —
  those are deep-dive's authority for established public stocks
  and don't apply pre-IPO.

For `SUBSCRIBE IF ELIGIBLE`, `WATCH FOR OPEN-AND-FLIP`, and `SKIP`,
write `No changes proposed.` — these verdicts don't generate durable
watchlist entries.

### Step 4: Gate-Mode Specifics *(gate mode only)*

Gate runs read the initial file first and compute a delta:

- **Pricing delta:** announced price vs. indicated range (above / at
  high end / mid / low end / below). The single most important data
  point in the gate run.
- **Range movement:** was the range upsized, held, or cut between
  the initial run and pricing?
- **Anchor delta:** any cornerstone investors confirmed since initial?
- **Regime delta:** any new sector IPO data points (a peer that
  priced this week, day-1 pop)?
- **Robinhood mechanics check:** is the IPO listed on RH IPO Access?
  This affects whether the SUBSCRIBE verdict is even achievable.
- **News delta:** max 3 bullet items. Single Exa search:
  `"{Company} IPO last 7 days"`.

The gate file re-emits the verdict (now collapsed — no more
`WATCH FOR PRICING` option) and a single-line **Final order** that
the user is placing today. For `SKIP`, the final order is "no
participation, remove from active watch."

### Step 5: Write & Surface

Write the file to `vault/reports/pre-ipo/`. Create the folder if
absent.

**Update `vault/ipo-calendar.md` for this row** using the Edit tool —
two cells:

1. **`Skill Run`** → set to `initial YYYY-MM-DD` or `gate YYYY-MM-DD`
   (today's date).
2. **`Expected Date`** → sync from the dossier's `_meta.md`
   `expected_ipo_date:` field if it's more specific than the calendar's
   current value. Specifically:
   - If calendar is `TBD` and dossier has a date → write the dossier's date.
   - If calendar has a date and dossier has the same or different date →
     write the dossier's date (dossier is the authoritative source —
     it was pulled from the S-1 filing).
   - If both have a date, recompute the calendar's `Status` column too
     using the legend in `ipo-calendar.md` (`30+ days out` / `this month`
     / `this week` / etc.) so news-analyst's daily reminder is grounded
     in the dossier-anchored date.
   - If dossier's `expected_ipo_date_confidence` is `range-only`, leave
     the calendar `TBD` — don't fake precision.

If the row doesn't exist (defensive — Step 0 already gated), don't try
to add it.

If the dossier was just auto-built in Step 0c, this same sync applies —
the freshly-written `_meta.md` is the source.

After writing, print the **Verdict + Pre-Commit Plan** sections to
chat verbatim. Do not duplicate other sections to chat — the user
can open the file for the rest.

**Do not delete prior pre-ipo files.** Each run is its own event;
quarterly-review reads the history for calibration (was the trade-
shape call right? Did the regime read hold up?).

### Step 5b: Apply Watchlist Updates *(graduating verdicts only)*

If the verdict is `BUILD VIA TRANCHES`, `WATCH FOR D30 ENTRY`, or
`WATCH FOR LOCKUP DIP`, run the shared apply script after Step 5
writes the file:

```bash
python .claude/scripts/apply_watchlist_updates.py vault/reports/pre-ipo/{ROOT}-EXPECTEDDATE-{initial|gate}.md
```

Pre-IPO tranches sit in `vault/watchlist.md` → `## Planned Tranches`
with long expiries (60–210 days) and `Conditional GTC` order type;
the gating condition (post-IPO trading window, lockup dip, etc.)
lives in the row's `Note` column.

Skip this step for `SUBSCRIBE IF ELIGIBLE`, `WATCH FOR OPEN-AND-FLIP`,
and `SKIP` — those verdicts emit `No changes proposed.` and the script
is a no-op anyway.

---

## Constraints

- **Require the calendar row.** Step 0b is a hard gate. Don't try to
  build the row inline — that's the user's manual entry or
  vault-curator's Friday job. (The calendar row signals user intent
  to track this IPO; pre-ipo doesn't surface candidates itself.)
- **Auto-build the dossier if missing.** Step 0c is a soft gate — pre-ipo
  invokes `company-dossier` in pre-IPO mode inline when the dossier is
  absent or stale. The user's `pre-ipo` call is the consumer signal that
  justifies the build. (This differs from `pre-earnings`, which hard-gates
  on dossier — public-company dossiers are heavier and the user typically
  wants explicit control over that EDGAR pull. Pre-IPO dossiers are
  lighter — S-1 only, no quarterly history, no Form 4 stack — so the
  cost/benefit flips toward auto-build.)
- **No deep-dive verdicts.** Pre-IPO does not produce HOLD/ADD/REDUCE/
  WATCH. Those are the deep-dive's output, and they require live price
  data that doesn't exist pre-IPO. The trade-shape verdict above is
  the only verdict pre-ipo emits.
- **No hallucinated numbers.** Every figure must come from the dossier,
  a search result, or a vault file. If unavailable, write "N/A" or
  "not yet disclosed." S-1 figures are typically several months old —
  cite the as-of date.
- **Stay neutral on trade shape.** The skill evaluates each shape on
  the specific facts. It does not have a default preference for
  open-and-flip vs. d30-entry vs. building. The user picks.
- **Be honest about regime.** If the comp regime check shows the
  sector's last 3 IPOs are underwater, the report says so even if
  the thesis fit is high — that's the regime tell, and burying it
  would defeat the point.
- **Scoped reads.** Read the selective dossier files (Step 1) +
  narrow vault files only. Don't re-read the whole vault.
- **Pre-commit, not predict.** The verdict is a conditional plan,
  not a forecast. The plan tells the user what conditions to watch
  and what to do when they fire.
- **Gate is not a re-run.** If you catch yourself re-doing the
  trade-shape matrix from scratch in a gate run, stop — the initial
  file already has it. Gate's job is *delta*: pricing, regime, anchors,
  news; does the verdict still hold; what's the one order I'm placing.
- **Watchlist writes go through Step 5b's apply script.** Pre-IPO emits
  the `Proposed Watchlist Updates` block in its report (audit trail) and
  then runs `apply_watchlist_updates.py` for graduating verdicts. Do not
  edit `watchlist.md` or `price-triggers.md` by hand from this skill. For
  `ipo-calendar.md`, only update the `Skill Run` cell (Step 5);
  `vault-curator` is the single content writer for status/date/range.

---

## Example invocations

- `"pre-ipo VLT"` → auto-detect mode from `Expected Date` in calendar
- `"pre-ipo VoltaGrid"` → company-name fallback when ticker is `TBD`
- `"run pre-ipo on VoltaGrid"` → same
- `"pre-ipo VLT gate"` → force gate mode (runs initial first if absent)
- `"pre-ipo VLT initial"` → force initial (even if <2 TD out)

---

## Interactions with other skills

- **`company-dossier` (pre-IPO mode)** is a hard dependency. If the
  dossier is missing, pre-ipo flags and stops. If the dossier is
  >30 days stale and there's been a known S-1/A amendment, pre-ipo
  flags and recommends a refresh before continuing.
- **`stock-deep-dive`** is the next skill to run *after* the IPO is
  trading. Pre-ipo's `BUILD VIA TRANCHES` verdict expects a fresh
  deep-dive once price history exists (typically T+30 onward). The
  pre-ipo file's tranche plan is the seed; the deep-dive refines
  the levels.
- **`pre-earnings`** is the skill to run for the company's first
  earnings print — which is the next big catalyst after lockup
  expiry. Once the dossier flips to public-company mode (10-Q on
  file), pre-earnings becomes the active workflow.
- **`news-analyst`** reads `vault/ipo-calendar.md` daily (Step 1e)
  and surfaces a one-liner reminder when an IPO is within 7 trading
  days. The reminder cites the most recent pre-ipo file if one
  exists.
- **`vault-curator`** writes/updates `vault/ipo-calendar.md` rows
  on Fridays. Pre-ipo's runs flip the `Skill Run` column on those
  rows (Step 5) but don't add or remove rows themselves.
- **`weekly-review`** runs housekeeping on `vault/watchlist.md`
  (expired-tranche cleanup, stale-row pruning). Pre-IPO writes its
  proposed tranches directly via Step 5b's apply script — same pattern
  as `stock-deep-dive` and `pre-earnings`.
- **`quarterly-review`** reads `vault/reports/pre-ipo/` during
  calibration: was the trade-shape call right (did SUBSCRIBE-eligible
  IPOs that we passed on actually pop)? Did the regime read hold up?
  This is why pre-ipo files are not deleted after the print.
