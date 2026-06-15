# Agentic Trading Journal

An investment-research and journaling system, built as
[Claude Code](https://claude.com/claude-code) **skills** on top of a local
[Obsidian](https://obsidian.md) vault.

The agent reads a personal vault of theses, positions, and principles; gathers market
news; and writes severity-scored alerts, in-depth research, weekly
macro syntheses, and quarterly self-audits back into the vault. The point is to automate
and sharpen the research, not to let Claude trade entirely for you. Some skills are designed as scheduled runs (daily news reports, weekly/quarterly reviews, curator reports, intraday price triggers),
while other stuff is meant to be called manually in
Claude code (deep dives, company dossier files, etc). Nothing is a fully automated research loop, at least yet (I'm currently working off this project to make a fully autonomous trading agent).

The idea of this public repo is for others to start with
my version and build on top of it, or find some ideas/inspiration to import into your own version
of this project. 

> **This is a generalized snapshot of a system I run privately.** It's a
> portfolio / reference implementation meant to show the architecture — not a
> maintained product, and not a service with users. I port interesting pieces
> over occasionally. The vault shipped here is a lightly-anonymized snapshot of a
> real book. **Nothing in this repo is investment advice.** See [the disclaimer](#disclaimer).

---

## Why it's interesting

The individual pieces are all simple. The logic and infrastructure behind how they fit together
is the more interesting part:

- **Skills as composable agents.** Each capability — daily alert, deep dive,
  weekly review, pre-earnings, curation — is a self-contained Claude Code skill
  with its own prompt, reference docs, and Python scripts. They *compose*: the
  daily alert can trigger a deep dive; the deep dive writes falsification
  conditions; the weekly review checks them; the quarterly review grades the
  whole system's calibration.
- **Severity-gated signal, not a digest.** The daily run surfaces only
  severity ≥ 3 items, each ending in one explicit action line
  (`run deep-dive TICKER` / `watch for X` / `none`). Noise is dropped, not
  filed in an appendix.
- **A research council, not a single take.** The deep dive runs a 3-advisor
  mini-council (Contrarian / Bull / First-Principles) plus a **Blank-Slate
  Reframe** that forgets current holdings and asks "if I had only cash today,
  would I buy this — and how much?" — which catches the status-quo bias that
  "it's not a big enough position to bother" hides.
- **Falsifiable theses (a tripwire ledger).** Every holding gets
  pre-registered, *measurable* invalidation conditions. They're checked daily
  (news-driven) and weekly (systematic). A trip forces a re-evaluation — so you
  can't quietly move the goalposts after the fact.
- **A calibration loop.** The quarterly review compares past verdicts against
  the outcomes of closed trades and audits the system's own recent output for
  framing drift and echo-chamber effects — is it reasoning from new data, or
  recycling its own language?
- **Empirical priors as a first-class layer.** A small catalog distills
  peer-reviewed finance findings (arbitrage decay, post-earnings drift, Kelly
  sizing, concentration) into decision rules, each with a strict
  verify-then-stamp citation discipline.
- **Mosaic execution research.** A `company-projects` → `execution-thesis` →
  `execution-audit` chain verifies what management *actually* ships against
  public signals (filings, permits, hiring, freight) vs. what they *say* — and
  the audit step is designed to run on a *different* model for agent diversity.
- **Numbers come from scripts, not the model.** Fundamentals, options, and
  prices are pulled by Python (yfinance / Stooq / FMP). The LLM reasons over
  them but is instructed never to invent a figure — unavailable data is written
  `N/A`.
- **Local-first, human-readable memory.** State is plain markdown in an
  Obsidian vault — git-versioned, greppable, no database. The agents read and
  write the same files a human edits.

---

## How it works

```
                       ┌─────────────────────────────┐
   market news  ─────► │  Claude Code skill (agent)  │ ─────►  markdown report
   web search          │  prompt + references + .py  │         written to vault/
                       └──────────────┬──────────────┘
                                      │ reads + writes
                          ┌───────────▼───────────┐
                          │   Obsidian vault/      │   ← the shared memory layer
                          │   notes, theses,       │
                          │   positions, reports,  │
                          │   priors, tripwires    │
                          └────────────────────────┘
```

The **vault** is the memory. Skills load context from it (your theses,
principles, open positions, recent reports), do their work, and write results
back as markdown. Because everything is files, the whole system is inspectable,
diffable, and editable by hand.

A **skill** is a directory under `.claude/skills/<name>/` containing a
`SKILL.md` (the agent's instructions), optional `references/` (templates,
scoring frameworks, personas), and optional `scripts/` (deterministic Python for
data the model shouldn't guess at). You invoke one by name from a Claude Code
session in this repo.

### The skills

| Skill | What it does | Output |
|-------|--------------|--------|
| `news-analyst` | Daily severity-scored portfolio alert (≥3 only) + macro awareness | `vault/reports/daily/` |
| `stock-deep-dive` | Fundamentals deep dive — council + blank-slate reframe + verdict; single or head-to-head | `vault/deep-dives/` |
| `weekly-review` | Weekly macro synthesis, thesis pressure-test, what-shifted | `vault/reports/weekly/` |
| `quarterly-review` | Calibration vs. closed trades + echo-chamber audit | `vault/reports/quarterly/` |
| `pre-trade` | 20-second "are you sure?" context check before an order (no writes) | console |
| `pre-earnings` | Scenario ladder + implied-move + pre-commit orders for a print | `vault/reports/pre-earnings/` |
| `pre-ipo` | Trade-shape decision for an upcoming offering | `vault/reports/pre-ipo/` |
| `vault-curator` | Weekly vault health, belief articulation, opportunity radar | `vault/vault-suggestions/` |
| `company-dossier` | SEC/EDGAR-sourced per-ticker reference dossier (8 files) | `vault/companies/TICKER/` |
| `company-projects` | Mosaic execution-tracking against management's claimed schedule | `vault/companies/TICKER/projects.md` |
| `execution-thesis` | 1–12 month "what are they actually doing?" hypotheses | `vault/companies/TICKER/execution-thesis.md` |
| `execution-audit` | Adversarial audit of an execution-thesis (run on a different model) | `vault/companies/TICKER/execution-audit.md` |
| `economic-calendar-fetcher` | Upcoming macro events (FOMC, CPI, GDP, …) | console |

`CLAUDE.md` is the always-loaded system context that ties them together (vault
layout, conventions, the rules every skill obeys).

---

## Quickstart

You need [Claude Code](https://claude.com/claude-code) and Python 3.11+.

```bash
git clone https://github.com/alexful2/agentic-trading-journal
cd agentic-trading-journal
pip install -r news-visual/requirements.txt   # yfinance, requests, jinja2, ...

# open a Claude Code session in the repo, then ask for a skill by name, e.g.:
#   "run the daily news analysis"
#   "deep dive on NVDA"
#   "pre-trade NVDA"
```

Then **make the vault yours**: the `vault/` here is a real, anonymized snapshot. Replace
`vault/notes/`, `vault/watchlist.md`, and friends with your own theses and
positions. The `vault/library/` frameworks and `vault/library/research/`
empirical priors are starter content — keep, edit, or delete them. Skills read
whatever is in the vault, so the system becomes *your* journal the moment you
start writing in it.

---

## Optional integrations (scaffolding — wire up or delete)

The core system is just the skills + the vault. Everything below is plumbing I
use to run it unattended. It's left in as a **reference**: each piece is
self-contained, so wire up your own credentials or delete the directory. None of
it is required to use the skills interactively.

| Integration | Where | What it adds | To remove |
|-------------|-------|--------------|-----------|
| **Email briefs** (Resend) | `news-visual/` | Renders the daily report to HTML and emails it | delete `news-visual/`, unset `RESEND_API_KEY` |
| **Scheduled jobs** (systemd) | `.claude/scripts/vps/` | Runs skills on a timer on a Linux server | delete the dir; or use cron / GitHub Actions instead |
| **CI / cron fallback** | `.github/workflows/` | GitHub Actions versions of the scheduled jobs | delete the workflows |
| **Intraday workers** (Pushover) | `.claude/scripts/check_intraday_*.py` | Pure-Python price/news pollers → mobile push | delete the scripts |
| **Public dashboard** | `dashboard/` | Renders vault state to a static HTML page for GitHub Pages | delete the dir |

Every credential is read from environment variables or a gitignored
`.claude/settings.local.json` — **no secrets live in this repo.** If you enable
an integration, supply your own keys; if you fork and publish a dashboard, audit
the rendered output first (it reads from your vault).

> **Note on data sources.** SEC EDGAR requires a real contact email in the
> `User-Agent` of automated requests — search for `you@example.com` and set your
> own before running the EDGAR-backed skills (`company-dossier`, etc.).

---

## Design notes & background

A longer write-up of the thinking behind this — why a "second loop that argues
back," why falsifiable tripwires, why a calibration audit — is planned as a
companion article. _(link TBD)_

This repo is intentionally a **snapshot**, not a continuously-synced mirror of
my private vault. Treat it as a reference implementation to read, fork, and
adapt — not a dependency to track upstream.

---

## Disclaimer

**This is not investment advice.** It's a personal research and journaling
system shared as a software project. Nothing here is a recommendation to buy or
sell any security. The vault shown is one investor's real, lightly-anonymized
notes (position sizes scaled); any tickers appear to demonstrate the system, not
as positions to copy, endorsements, or forecasts. Markets carry risk of loss. Do your own research and consult a
licensed professional before making financial decisions. The author and
contributors accept no liability for any use of this software.

## License

[MIT](./LICENSE).
