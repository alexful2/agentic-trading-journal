# Intraday News Worker — Roadmap

Living roadmap for the `check_intraday_news.py` worker (script:
`.claude/scripts/check_intraday_news.py`, workflow:
`.github/workflows/intraday-news.yml`).

The pattern across all versions: **only the input source layer changes.**
Severity scoring rules, dedup state shape, Pushover envelope, and vault
log format are stable from v1 onward.

---

## v1 — Shipped 2026-05-02 (superseded by v1.2)

- **Sources:** Google News RSS (per ticker) + SEC EDGAR atom (per CIK,
  best-effort — reads CIK from `vault/companies/TICKER/_meta.md`).
- **Cadence:** GH Actions cron `*/20 10-23 * * 1-5` (extended hours, M–F).
- **Severity:** deterministic regex/keyword rules, no LLM call per poll.
  - sev 4 → Pushover push: 8-K filing, halt, guidance change, M&A,
    FDA decision, regulatory probe, exec departure, chapter 11, breach.
  - sev 3 → vault log only: 10-K/Q, Form 4, analyst u/d, generic earnings.
  - sev ≤ 2 → dropped.
- **Tickers:** Tier 1 + Tier 2 from `vault/watchlist.md` (parsed from the
  `## Tier N` table headers).
- **Output:** Pushover push (sev 4 only) + append to
  `vault/reports/intraday-alerts/news-YYYY-MM-DD.md`.
- **Dedup:** `.intraday-state/news-YYYY-MM-DD.json` keyed by
  `{ticker}:{source}:{item_id}`.

**Known limitations of v1:**
- Google News indexes content 15–60 min after original publication, so
  ticker-news headlines lag wire feeds significantly.
- No macro coverage (Fed, BLS, geopolitical) — Tier 1+2 ticker-only.
- 8-K push fires on every 8-K including Item 2.02 earnings releases (often
  pre-announced via earnings calendar, not a true surprise).
- No automatic deep-analysis follow-up — user manually runs `pre-trade`
  or `stock-deep-dive` after a sev-4 alert.

---

## v1.2 — Shipped 2026-05-03

**What changed:** Replaced Google News with Alpaca's REST news API.
Same cron cadence, same severity rules, Benzinga-sourced wire content
in place of Google News-aggregated headlines.

- `fetch_google_news()` → `fetch_alpaca_news(tickers, cutoff)`. Single
  batch HTTP call covers all watched tickers via `symbols=` param,
  replacing N per-ticker RSS pulls.
- Auth via `APCA-API-KEY-ID` / `APCA-API-SECRET-KEY` headers; both are
  GH Actions repo secrets.
- Cross-tagged articles (article symbols includes multiple watched
  tickers) attribute to each — one item per (article, ticker) pair.
- EDGAR atom fetch unchanged.
- Failure mode preserved: if Alpaca env is missing or auth fails, log
  to stderr and return `[]` — EDGAR still runs, system degrades not
  fails.

**Smoke-test (2026-05-03 18:02 UTC, workflow_dispatch run 25286628512):**
2 items fetched in ~3s for 7 tickers, 0 sev>=3 (Sunday, low volume).
No errors. Auth clean.

**Free-tier verification:** Real-time delivery confirmed during
smoke-test (no 15-min delay artifact). Free tier with paper-trading
account is sufficient for our use; 900 headlines/day cap isn't close
to binding for 7 tickers.

---

## v1.5 — Stays-on-cron features (after v1.2 settles)

Five features, each independent. Deploy in any order. None require new
infrastructure beyond what v1/v1.2 already runs on.

### Step 0 — Bleed-over dedup fix — Shipped 2026-05-11

Pre-feature bug fix from the v1.2 5-day review (`vault/reports/intraday-alerts/v12-review-2026-05-08.md`):
state file was keyed by today's UTC date only, so the 24h lookback re-fired
every prior-afternoon item at the date rollover (~10:00 UTC). 50% of sev-4
pushes were stale duplicates.

Fix: load both today's AND yesterday's state files at startup
(`check_intraday_news.py` ~lines 552-563). ~6 lines.

### 1. Macro feed — Shipped 2026-05-11

Federal Reserve press release RSS (`FED_PRESS_URL`). Catches FOMC
statements, rate decisions, FOMC minutes, SEP/dot plot, Powell speeches,
Beige Book, stress-test results. Items use `ticker=_MACRO` so dedup state
shape is unchanged. No per-ticker keying.

- `fetch_fed_press(cutoff)` parses RSS items (title, link, pubDate, guid).
- `classify_macro(text)` — tight sev-4 gating (FOMC/rate/minutes/SEP/
  emergency); sev-3 for speeches, remarks, Beige Book, testimony, stress
  tests.
- `score_item` routes source="fed" → `classify_macro`.
- `--no-macro` CLI flag disables for testing.

BLS RSS deferred until Fed pattern produces real-world tick data
(~2 weeks).

**~80 lines of code (ended up larger than the ~50 estimate because of
the second pattern bucket + classify_macro helper).**

### 2. 8-K item parsing — Shipped 2026-05-05

When EDGAR returns an 8-K, fetch the filing index page and parse Item
codes. Routing via `EIGHT_K_ITEM_INFO` in `check_intraday_news.py`:
- Material/surprise items → push (sev 4): 1.01 material agreement, 1.03
  bankruptcy, 1.05 cybersecurity, 2.01 acquisition, 2.04 debt acceleration,
  2.06 impairment, 3.01 delisting, 4.02 restatement, 5.01 change of control,
  5.02 exec change, 5.06 shell-status change, 8.01 other.
- Scheduled/housekeeping items → log only (sev 3): 2.02 earnings release,
  2.03 new debt, 3.02/3.03 equity items, 4.01 auditor change, 5.03/5.04/5.05
  governance, 5.07 vote results, 7.01 Reg FD.
- 9.01 (financial statements/exhibits) ignored — always paired boilerplate.
- Multiple items: highest-severity wins; ties go to first listed.
- Fetch failure or unparseable page falls back to generic sev-4 "8-K filing"
  so we never silently drop a real filing.

Validated against 2026-05-05 filings: VRT (Items 2.02+7.01+9.01) routed to
log, GEV (Items 5.02+9.01) pushed as "exec/director change". Before this,
both pushed as bare "8-K filing".

### 3. Auto-trigger news-read on sev-4 — Shipped 2026-05-11; templated-unit refactor 2026-05-14

When a sev-4 fires for a Tier-1 ticker, start a transient systemd unit
`news-read@<INSTANCE>.service` that runs `claude --print` with a custom
**news-read** prompt (NOT pre-trade — pre-trade is order-shaped and the
auto-trigger moment is "what just happened?", not "are you sure?").
Output is a 3-line phone-friendly verdict: substance / thesis impact /
next-action flag (NONE | WATCH | ADJUST-LADDER | ESCALATE-TO-PRE-TRADE).
Pushes to Pushover ~30-60s after the headline alert.

Initial implementation called pre-trade directly — the smoke test showed
pre-trade gave a position-summary (correct for its shape) but didn't
actually read or summarize the news. Swapped to the news-read prompt on
2026-05-11 same-day. The wrapper script was originally named
`news-deep-dive.sh` — renamed to `news-read.sh` on 2026-05-14 because
the 3-line summary is structurally distinct from the `stock-deep-dive`
skill and the old name was a misnomer.

**Architecture diverged from the original plan.** Original said GH Actions
workflow_dispatch + `gh workflow run` — but all 7 jobs migrated to VPS
systemd timers on 2026-05-05, so this version uses a transient systemd
unit on the VPS instead. Simpler, no GH Actions dependency.

**2026-05-14 refactor — templated systemd unit replaces Popen detach.**
The original Popen-detach approach (`start_new_session=True`) was killed
by systemd's default `KillMode=control-group` when the parent
`intraday-news.service` (Type=oneshot) exited 7s later. Confirmed via
log forensics: every `news-deep-dive-VRT-*.log` since 2026-05-12 has
exactly one line (the start log) and 105 bytes, indicating the script
was terminated before reaching its first downstream log call. New
architecture: each invocation starts a transient
`news-read@<INSTANCE>.service` unit which lives in its own cgroup and
survives the parent worker's teardown.

Components:
- `load_tier1_tickers()` — parses Tier 1 only from watchlist.md
  (`_parse_tier_map` shared with `load_active_tickers`).
- `trigger_news_read(ticker, category, title, link)` — writes
  `/tmp/news-read/<INSTANCE>.env`, calls
  `sudo systemctl start --no-block news-read@<INSTANCE>.service`,
  returns immediately. `link` carries the EDGAR/wire URL to the
  wrapper's WebFetch step.
- `INTRADAY_NEWS_READ_DISABLED=1` env kill-switch
  (`INTRADAY_DEEP_DIVE_DISABLED=1` retained as alias).
- `--no-news-read` CLI flag (`--no-deep-dive` retained as alias).
- Template unit: `/etc/systemd/system/news-read@.service`. Sources the
  env file via the wrapper script. `ExecStopPost` cleans up the env
  file on exit.

Wrapper script tracked at `.claude/scripts/vps/news-read.sh` and unit
template at `.claude/scripts/vps/news-read@.service` (README at
`.claude/scripts/vps/README.md`). Wrapper sources
`/opt/trading-journal/scripts/_common.sh` for shared helpers (PATH, secrets,
venv, `git_pull_simple`, `repo_lockfile`, `log`). Per-ticker `flock`
ensures back-to-back ticks on the same name dedupe to one Claude run.

**~110 lines (script changes) + 130 lines (wrapper) + 12 lines (unit) + README.**

### 4. LLM triage backstop

Sonnet 4.6 (`claude-sonnet-4-6`) classifier on items that almost matched
a sev-4 rule but didn't. Catches "OpenAI signs deal with VRT" — clearly
material but won't match any current keyword.

Heuristic for "almost matched": item contains a Tier-1 ticker AND a
verb-rich headline AND no drop-pattern hit AND no rule match. Sonnet
returns sev 0–4 + 1-line reason. Cost: ~$0.02/call, expected ~5–10
calls/day.

**~60 lines of code.**

### 5. 24/7 coverage extension

Extend cron from `*/20 10-23 * * 1-5` to `*/20 * * * *` (every 20 min,
24/7). Catches weekend geopolitical news + Sunday-night futures-moving
events.

Trivial change once we know the noise floor. Hold until v1/v1.2 has run
for a few weeks so we can compare noise rates across hours.

**1 line of code (cron expression).**

---

## v2.0 — Real-time push architecture

**Goal:** Sub-30-second alerts from news → phone. Architectural shift
from polling to event-driven.

**Decision criterion:** only build if v1.2 data shows the 20-min cron
cadence is the actual binding constraint (i.e., wire-quality news is
arriving and we want sub-30s reaction). If 20-min Benzinga via REST is
fast enough for our discretionary trading window, **stop here.** Don't
build v2 just to build v2.

### Architecture

```
Alpaca News WebSocket (wss://stream.data.alpaca.markets/v1beta1/news)
    ↓ real-time event
Always-on ingester (Python on VPS, OR Cloudflare Worker for webhook
                    providers)
    ↓ score severity (reuses v1 keyword rules as a library)
    ↓
If sev≥4: Pushover push immediately (T+5–30s)
    ↓
GitHub repository_dispatch event with ticker + headline payload
    ↓
GH Actions workflow #2: claude -p stock-deep-dive (T+3–5min)
    ↓
Pushover verdict push
```

### Source

**Alpaca News WebSocket** — `wss://stream.data.alpaca.markets/v1beta1/news`.
Free tier with brokerage account (already provisioned in v1.2). Real-time,
Benzinga-sourced, 900 headlines/day cap.

If Alpaca's free tier turns out to be 15-min delayed (docs are ambiguous —
verify before building): pay $99/mo for Alpaca Algo Trader Plus, OR
upgrade to direct Benzinga Pro at ~$200–300/mo.

### Ingester host

Three options, ranked by complexity:

1. **Tiny VPS** (~$5/mo a small cloud instance) — Python process holds
   WebSocket open 24/7, systemd unit for auto-restart. Most flexible.
   Cleanest separation of concerns.
2. **Cloudflare Worker** (free tier) — works only for webhook-style
   providers. Alpaca is WebSocket-only so this option requires a
   different source. Skip unless we switch to Finnhub webhooks.
3. **Self-hosted GH Actions runner** — overkill, adds GH Actions runtime
   complexity, not worth it.

**Default choice: $5/mo Linux VPS with a single systemd-managed Python
service.** Reuse the v1.5 severity rules as an importable module so the
VPS just imports + classifies + pushes.

### Repository_dispatch trick

Once the VPS classifies a sev-4 event, it calls GitHub's
`repository_dispatch` API with a custom event type
(e.g. `news-sev4`). A new GH Actions workflow listens for that event
type and runs `claude -p stock-deep-dive` with the news payload as
context. Latency: ~10–30s from dispatch to workflow start.

This pattern keeps the deep-analysis stack on existing GH Actions
(reusing `CLAUDE_CODE_OAUTH_TOKEN`, the existing `claude -p` pattern,
and existing skills) — only the source-fetching layer moves to the VPS.

### Cost estimate (monthly)

- Linux VPS: $5
- Alpaca News API: $0 (free tier) or $99 (if free tier proves delayed)
- Cloudflare Worker (if used as relay): $0 (free tier)
- GitHub Actions: existing usage (deep-analysis runs are short)
- Anthropic API: existing subscription (deep-dive uses Opus via
  `CLAUDE_CODE_OAUTH_TOKEN`)

**Total: $5–104/mo depending on Alpaca tier.**

### Operational concerns

- VPS uptime monitoring: add a heartbeat ping (e.g. healthchecks.io free
  tier) so we get alerted if the WebSocket process dies.
- Reconnect logic: WebSocket disconnects happen; ingester needs
  exponential-backoff reconnect.
- State persistence across restarts: dedup state lives on local disk;
  losing it means duplicate alerts on restart. Tolerable.
- Same-network duplicate prevention: if v2 deploys but v1.2 cron is left
  running, both will alert on the same events. Disable v1.2 workflow
  when v2 ships.

---

## Open questions to resolve before each phase

**Before v1.2:**
- Does Alpaca's free tier news WebSocket/REST actually deliver real-time,
  or is it 15-min delayed like their market-data free tier? (The market-
  data 15-min delay is well-documented; news isn't explicitly stated.)
  Verify with a free account before committing.

**Before v2.0:**
- After v1.2 runs for 1–2 weeks, does the 20-min poll cadence ever bite?
  Look for: news headlines that fired EDGAR 8-Ks before any news source
  appeared in our log (means we caught the filing but missed the
  pre-filing wire push, which is exactly what v2 would fix).
- If yes, build v2. If no, stop at v1.5.

---

## What NOT to do

- **Don't run a 24/7 cron polling at high frequency.** If you want
  sub-minute alerts, switch to push (v2). Polling every 30s is the worst
  of both — high cost, still latent, source providers will rate-limit you.
- **Don't pay for Bloomberg Terminal.** $24k/yr is institutional. The
  retail-tier path is Alpaca free → Benzinga Pro ($200/mo) → Polygon
  ($199/mo) at the high end.
- **Don't add an LLM call to every poll.** Per-poll LLM calls explode
  cost. v1.5 LLM triage is gated to "almost matched a rule" items,
  expected to fire 5–10x/day.
- **Don't over-tune the severity regexes.** First-week false-positive
  noise is expected; let the actual run data drive the refinement, not
  speculation.
