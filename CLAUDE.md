# Agentic Trading Journal

## Project Purpose

A personal investment research and journaling system built as Claude Code
skills. The agents read an Obsidian vault for context, gather market news,
and write severity-scored reports, deep-dive research, and periodic reviews
back into the vault.

This file is the always-loaded system context. Keep it **lean** — priors and
conventions only. The vault (`notes/`, `library/`) is the real source of truth;
every skill pays for this file's tokens on every run, so it should not duplicate
what the vault already records.

> This is a generalized reference implementation. The shipped `vault/` is a
> lightly-anonymized snapshot of a real working vault — replace it with your own.
> Nothing here is investment advice.

## The Vault

Path: `./vault/` (relative to project root — always use this path).

```
vault/
├── notes/          # Per-stock theses, decisions, rationale, lessons learned.
│                   # Timestamped — newer files supersede older ones on the same topic.
├── library/        # Reference material: principles, frameworks, worldview.
│   └── research/    # Empirical-priors catalog: finance findings as decision priors.
│                   # Consumed selectively by deep-dive; not bulk-read by the daily alert.
├── reports/
│   ├── daily/      # OUTPUT: Daily news alerts (news-analyst)
│   ├── weekly/     # OUTPUT: Weekly macro reviews (weekly-review)
│   ├── pre-earnings/ # OUTPUT: Pre-earnings action plans (pre-earnings)
│   └── quarterly/  # OUTPUT: Quarterly calibration + echo audit (quarterly-review)
├── deep-dives/     # OUTPUT: On-demand stock deep dives + _verdicts.md ledger
├── vault-suggestions/ # OUTPUT: Weekly vault-curator suggestions (human review)
├── companies/      # Per-ticker SEC-sourced dossiers + mosaic execution research
├── watchlist.md    # Tiered stock list + watchlist price triggers + planned tranches
├── price-triggers.md # Broader-universe price triggers (non-watchlist names)
├── tripwires.md    # Thesis falsification ledger — pre-registered invalidation conditions
└── ipo-calendar.md # Date-anchored IPO reminder layer
```

Position tracking is whatever you keep in the vault — these skills can parse a
`!Journalit/`-style folder of YAML-frontmatter trade files via
`.claude/scripts/get_positions.py` if present, but that's optional. Adapt the
parser to your own bookkeeping.

## How to Load Context

### Phase 1 — Understand the portfolio

1. **Read `vault/watchlist.md`** for the tiered stock list — what's held,
   what's watched, and how deeply to research each. Tier definitions are in
   the file.
2. **Confirm open positions** from your position-tracking source if available.
3. **Read `vault/notes/`** to understand the thesis per position, how past
   decisions played out, and any recurring patterns in the decision-making.
4. **Read `vault/library/`** (except `library/research/`, which is read
   *selectively* by deep-dive) for principles, frameworks, and worldview.

### Phase 2 — Gather news (tiered search)

Search depth scales with tier to keep token usage low while covering
high-conviction positions thoroughly.

- **Tier 1 — Core holdings (always):** one dedicated search per ticker for
  ticker news + company news. Full severity analysis every run.
- **Tier 2 — Active watchlist (rotation):** one search per ticker; rotate if
  there are more than ~4 (alternate halves day to day).
- **Tier 3 — Peripheral (passive):** no dedicated searches; scored only if they
  surface in the broad searches.
- **Broad searches (every run):** general market, plus a handful keyed to your
  thesis themes and the macro backdrop (rates, policy, your sector).

Target ~10–15 searches per run.

### Phase 3 — Score and write

Score each item with the framework in
`.claude/skills/news-analyst/references/scoring-framework.md`. **Only severity
≥ 3 items are surfaced** — sev 1–2 are dropped as noise (not filed in an
appendix). Each surfaced item gets one action line: `run deep-dive TICKER`,
`watch for [condition]`, or `none`. Write to
`vault/reports/daily/YYYY-MM-DD.md` using the report template.

## Investment Perspective (baseline — EDIT THIS)

> This section is the personalization hook. It holds *priors only* — a brief
> statement of how **you** invest, so the agents reason in your frame. Keep it
> short; the vault always wins on conflict. Replace the neutral examples below
> with your own. The richer your `notes/` and `library/` get, the less this
> section needs to say.

- **Style.** State your actual style in a sentence — e.g. long-term,
  conviction-based stock-picking vs. systematic/diversified; concentrated vs.
  broad; the time horizon you size for.
- **Thesis themes.** Name the one or two themes you actually have an edge or
  conviction in. The agents use these to weight news and seed broad searches.
- **Known biases — push back on these, don't mirror them.** List your own
  recurring mistakes (chasing, loss aversion, anchoring to stale targets) so
  the agents argue against them rather than reinforce them. This is one of the
  most valuable things to write here.
- **Frameworks to apply by name.** If you keep named decision frameworks in
  `library/`, list them here so skills invoke them (e.g.
  `[[Opportunity-cost lens]]`).

The shipped `vault/library/` includes a few example frameworks and an
empirical-priors catalog to show the pattern — keep, edit, or delete them.

## Skills

| Skill | When to use | Output |
|-------|-------------|--------|
| `news-analyst` | Daily alert — severity ≥3 portfolio-relevant news + macro awareness | `vault/reports/daily/` |
| `weekly-review` | Weekly macro synthesis — themes, thesis pressure-test, what shifted | `vault/reports/weekly/` |
| `stock-deep-dive` | Deep analysis of one stock, or a head-to-head comparison of two | `vault/deep-dives/` |
| `vault-curator` | Weekly vault health — stale beliefs, library gaps, opportunity radar | `vault/vault-suggestions/` |
| `pre-trade` | Quick pre-order context check (`pre-trade TICKER`) | console |
| `pre-earnings` | Pre-earnings scenario ladder + implied move + pre-commit orders | `vault/reports/pre-earnings/` |
| `pre-ipo` | Pre-IPO trade-shape decision for an upcoming offering | `vault/reports/pre-ipo/` |
| `quarterly-review` | Quarterly calibration vs. closed trades + echo-chamber audit | `vault/reports/quarterly/` |
| `economic-calendar-fetcher` | Upcoming economic events (FOMC, CPI, GDP, …) | console |
| `company-dossier` | SEC-sourced per-ticker reference dossier (8 files) | `vault/companies/TICKER/` |
| `company-projects` | Mosaic execution-tracking vs. management's claimed schedule | `vault/companies/TICKER/projects.md` |
| `execution-thesis` | 1–12 month "what are they actually doing?" hypotheses | `vault/companies/TICKER/execution-thesis.md` |
| `execution-audit` | Adversarial audit of an execution-thesis (ideally on a different model) | `vault/companies/TICKER/execution-audit.md` |

### Stock deep dive — notes

The deep dive reads the vault broadly before analyzing a stock, then produces:
fundamentals (live via yfinance, no key), a historical entry-pattern backtest, a
conditional options-vs-shares check, thesis validation, a **Portfolio Fit &
Timing** section, a **Blank-Slate Reframe** (forget current holdings — would you
buy from scratch, and how much?), an **Implied Expectations** thesis-math check
(what does today's price require you to believe?), a **Conviction Check**, a
3-advisor council (Contrarian / Bull / First-Principles), and a verdict
(HOLD / ADD / REDUCE / WATCH). It writes falsification thresholds into
`tripwires.md`.

The deep dive's **Conviction Check** pressure-tests the position against the
strongest version of your own long-term thesis — would a high-conviction holder
of that thesis buy this name at today's price, or wait for a dip? The point is
to separate "good company" from "good entry," and to stop a broad secular thesis
from auto-justifying any price. No persona file needed.

### The calibration loop

- **Tripwires** (`vault/tripwires.md`) — pre-registered, measurable thesis
  invalidation conditions per holding. Written by deep-dive + manually; checked
  daily (news-driven) and weekly (systematic). A trip → run a deep-dive. Pure
  price levels stay in the price-trigger tables, not here.
- **Trade-close arcs** — fill in `vault/templates/trade-close-template.md` when
  a position closes; save to `library/`. Feeds the quarterly calibration pass.
- **Quarterly review** — grades past verdicts against outcomes and audits the
  system's own output for framing drift.

## Web Search

Skills are written to prefer `web_search_exa` (Exa MCP — neural/semantic search,
strong on financial content). It is **optional**: if you don't connect Exa, use
Claude Code's built-in web search instead — the skills degrade gracefully.

## Important Rules

- **Not investment advice.** Every report and deep dive must say so.
- **Don't hallucinate news.** Only report items found via search, with source
  and date.
- **Don't hallucinate numbers.** Every figure in a deep dive must come from the
  data scripts. If a data point is unavailable, write `N/A`.
- **Be honest about uncertainty.** If a score or verdict could go either way,
  say so — but still commit to a recommendation.
- **Report against your own book.** If news is bearish for a theme you're long,
  report it honestly. The system's job is to argue back, not cheerlead.
- **Infer patterns from the notes.** If the notes show a tendency to hold
  through dips, or a type of trade that went badly, factor it into advice.
- **Temporal reasoning: newer notes supersede older ones.** Notes are
  timestamped; the most recent file on a topic is authoritative. Never cite a
  stale target or plan as the current view if a newer note revised it. Flag
  conflicts explicitly.
- **Don't create unsolicited files.** Write only to the locations below; folders
  not yet on disk are created on first write by the relevant skill.

### Writable locations

- `vault/reports/{daily,weekly,quarterly,pre-earnings,pre-ipo}/` — skill outputs
- `vault/deep-dives/` — stock deep dives + `_verdicts.md` ledger
- `vault/vault-suggestions/` — curator output (human review)
- `vault/watchlist.md` — price-trigger + planned-tranche tables, via
  `.claude/scripts/apply_watchlist_updates.py` (tier rosters stay manual)
- `vault/price-triggers.md` — broader-universe triggers (deep-dive auto-upserts
  for non-watchlist tickers)
- `vault/tripwires.md` — falsification ledger
- `vault/ipo-calendar.md` — IPO reminder layer
- `vault/companies/TICKER/` — per-ticker dossier + mosaic research (one file per
  type, never overlapping across skills)
- `vault/library/` — only when explicitly asked (e.g. promoting a suggestion or
  adding a trade-close arc)

## Automation (optional)

The skills run fine interactively. To run them unattended, this repo ships
**optional** scaffolding you can wire up or delete — see the README's "Optional
integrations" table. In short:

- **Scheduling** — example systemd units in `.claude/scripts/vps/` and
  equivalent GitHub Actions workflows in `.github/workflows/`. Pick one
  scheduler (systemd, cron, or Actions) or none.
- **Email briefs** — `news-visual/` renders the daily report and sends it via
  Resend.
- **Intraday push** — pure-Python pollers in `.claude/scripts/` push price/news
  alerts via Pushover.

All credentials are read from environment variables or a gitignored
`.claude/settings.local.json`. **No secrets live in this repo.** Set your own
before enabling any integration. SEC EDGAR requests need a real contact email in
their `User-Agent` (search for `you@example.com`).
