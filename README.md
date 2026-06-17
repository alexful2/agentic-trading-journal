# Agentic Trading Journal

An investment-research and journaling system, built as
[Claude Code](https://claude.com/claude-code) **skills** on top of a local
[Obsidian](https://obsidian.md) vault.

Claude reads a personal vault of theses, positions, and principles; gathers market
news; and writes severity-scored alerts, in-depth research, weekly
macro syntheses, and quarterly self-audits back into the vault. The point is to automate
and sharpen the research process of trading, not to let Claude trade entirely for you. Some skills are designed as scheduled runs (daily news reports, weekly/quarterly reviews, curator reports),
while other stuff is meant to be called manually in
Claude code (deep dives, company dossier files, etc). Nothing is a fully automated research loop, though you could design it to be that way. This public repo is meant to serve as a base example of an agentic trading journal that you can build on and personalize for yourself.

> **This is a generalized snapshot of a system I run privately.** It's a
> portfolio / reference implementation meant to show the architecture — not a
> maintained product, and not a service with users. I port interesting pieces
> over occasionally. The vault shipped here is a lightly-anonymized snapshot of a
> real book. **Nothing in this repo is investment advice.** See [the disclaimer](#disclaimer).

---

### The skills

| Skill | What it does | Output |
|-------|--------------|--------|
| `news-analyst` | Daily severity-scored portfolio-news alerts + macro awareness. | `vault/reports/daily/` |
| `stock-deep-dive` | In-depth research report on stock fundamentals — council + blank-slate reframe + verdict; reasons against its own past-verdict calibration | `vault/deep-dives/` |
| `weekly-review` | Weekly macro synthesis, thesis pressure-test, what-shifted | `vault/reports/weekly/` |
| `quarterly-review` | Calibration vs. closed trades + echo-chamber audit | `vault/reports/quarterly/` |
| `log-trade` | Log a fill in-session (open / add / trim / close) — no plugin needed | `vault/trades/` |
| `pre-earnings` | Scenario ladder + implied-move + pre-commit orders for a print | `vault/reports/pre-earnings/` |
| `pre-ipo` | Trade-shape decision for an upcoming offering | `vault/reports/pre-ipo/` |
| `vault-curator` | Weekly vault health, belief articulation, opportunity radar | `vault/vault-suggestions/` |
| `company-dossier` | SEC/EDGAR-sourced per-ticker reference dossier (8 files) | `vault/companies/TICKER/` |
| `company-projects` | Research a company's upcoming projects in extremely great detail to see how they're coming along. Gather oddly-specific info like job listings, permit approvals/applications, satellite readings, county land-deed records, etc. and triangulate all these data scraps into a coherent hypothesis | `vault/companies/TICKER/projects.md` |
| `execution-thesis` | 1–12 month "what are they actually doing?" hypotheses (based on company-projects) | `vault/companies/TICKER/execution-thesis.md` |
| `execution-audit` | Adversarial audit of an execution-thesis (use a different model for this for model diversity) - check the validity of hypotheses formed and audit back into execution-thesis file | `vault/companies/TICKER/execution-audit.md` |
| `economic-calendar-fetcher` | Upcoming macro events (FOMC, CPI, GDP, …) | console |

Each skill feeds into each other through a complex logic pipeline. 
`CLAUDE.md` is the always-loaded system context that ties them together (vault
layout, conventions, the rules every skill obeys).

Logic pipeline between company-dossier/projects/execution thesis is as follows: create company dossier (used generally for all sorts of things) --> company-projects (mosaic substrate) --> execution-thesis (what are they doing?) --> execution-thesis-audit (adversarial, different model) --> audit exists as its own file and folds corrections back into execution-thesis


---

## How the vault works (conventions)

The skills table tells you *what each skill produces*. What it doesn't tell you
is how the outputs become a **system** instead of a folder of disconnected
reports. These are the connective conventions — the way this vault actually
happens to work:

- **The wikilink thread is the real product.** Everything cross-references by
  `[[TICKER-YYYY-MM-DD]]`. A note threads up to a deep-dive; a daily alert flags
  a stale verdict and emits `run deep-dive X`; the new dive cites the one it
  supersedes in its footer; the weekly review cites every dive it read. The
  result is a *traceable causal chain* — you can walk note → dive → watchlist
  tranche → daily fire → weekly audit → next dive. That auditability is most of
  the point.

- **Two retention classes: ephemeral vs. permanent.** Deep-dives are
  **disposable** — superseded ones are auto-deleted, so only the latest per
  ticker survives. Notes, company dossiers, and the ledgers are **permanent**.
  That asymmetry is deliberate: tactical analysis goes stale fast and shouldn't
  accumulate; reasoning and state should.

- **State lives in append-only ledgers, not in the reports.** `_verdicts.md`,
  `tripwires.md`, and the watchlist / price-trigger tranche tables are the
  system's memory. Reports are *views*; ledgers are *state*. `_verdicts.md`
  exists precisely because deep-dives get deleted — it captures the verdict and
  break-even probability before the dive file is destroyed, so the calibration
  loop and verdict-drift detection have something durable to read.

- **Supersession is enforced three ways at once.** Filename date (newer wins) +
  an explicit `[[prior-dive]]` citation in the new file + verdict-drift flagging
  in the daily alert ("ADD stale at 24 days"). The rule "newer notes supersede
  older ones" is only trustworthy because these mechanics back it.

- **Triggers cause re-evaluation, not action.** A tripped wire or a drifted
  verdict emits `run deep-dive TICKER` — a pre-committed signal to *reassess*,
  never an auto-sell. The system argues; the human acts. That boundary is the
  whole "not letting Claude trade for you" stance, made concrete.

- **The company stack has three lifespans.** `companies/TICKER/` is the
  permanent SEC baseline; `execution-thesis` is the medium-lived mosaic layer;
  deep-dives are the ephemeral tactical layer. Keeping static reference data and
  fast-moving tactical reads in separate lifespans is what stops them colliding.

- **`library/` frameworks are cited by name as rules.** `[[macro-cohort-confirmation]]`,
  `[[C9 - Most Stocks Underperform T-Bills]]`, `[[wait-for-deal-thesis]]` — the
  library isn't reference reading, it's the decision grammar the dives reason in
  and invoke by name to justify or block a call.

- **Staleness is a first-class concept.** Price triggers expire at 30 days;
  verdicts get flagged "stale at N days"; `Last Reviewed` dates gate freshness.
  The system actively distrusts its own old outputs rather than treating them as
  standing truth.

None of this is enforced by code you have to configure — it falls out of the
filename conventions, the `[[wikilink]]` habit, and `CLAUDE.md`'s rules. Adopt as
much or as little as you like; the skills degrade gracefully if a ledger or
thread is missing.

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
`vault/notes/`, `vault/watchlist.md`, etc with your own theses and
positions. The `vault/library/` frameworks and `vault/library/research/`
empirical priors are starter/example content — keep, edit, or delete them. Skills read
whatever is in the vault, so the system becomes *your* journal the moment you
start writing in it.

### Positions

Open positions live in `vault/trades/` — one markdown file per trade (YAML
frontmatter with entries/exits and status). You don't log them by hand: tell
Claude "I bought 50 NVDA at 118.40" and the `log-trade` skill writes the file;
`get_positions.py` aggregates shares, average cost, and P&L for the other skills
to read. See
[`vault/trades/_EXAMPLE-NVDA-2026-05-12.md`](vault/trades/_EXAMPLE-NVDA-2026-05-12.md)
for the schema. Optionally, you could also use the Journalit Obsidian plugin for logging trades,
which has some nice extra functionality like visual graphs. 

---

## Optional integrations (scaffolding — wire up or delete)

The core system is just the skills + the vault. Everything below is plumbing I
use to run it unattended. It's left in as a **reference**: each piece is
self-contained, so wire up your own credentials or delete the directory. None of
it is required to use the skills interactively.

| Integration | Where | What it adds | To remove |
|-------------|-------|--------------|-----------|
| **Email briefs** (Resend) | `news-visual/` | Renders the daily report to HTML and emails it | delete `news-visual/`, unset `RESEND_API_KEY` |
| **Scheduled jobs** (systemd / cron) | `.claude/scripts/vps/` | Runs skills on a timer. Either locally, via github cronjobs, or a VPS server |  delete `.claude/scripts/vps/`|
| **CI / cron fallback** | `.github/workflows/` | GitHub Actions versions of the scheduled jobs | delete the workflows |
| **Intraday workers** (Pushover) | `.claude/scripts/check_intraday_*.py` | Pure-Python price/news pollers → mobile push (**off by default** — left as reference; the author retired these once the push channel went unused) | delete the scripts |
| **Public dashboard** | `dashboard/` | Renders vault state to a static HTML page for GitHub Pages | delete the dir |

Every credential is read from environment variables or a gitignored
`.claude/settings.local.json` — **no secrets live in this repo.** If you enable
an integration, supply your own keys; if you fork and publish a dashboard, audit
the rendered output first (it reads from your vault).

> **Note on data sources.** SEC EDGAR requires a real contact email in the
> `User-Agent` of automated requests — search for `you@example.com` and set your
> own before running the EDGAR-backed skills (`company-dossier`, etc.).

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
