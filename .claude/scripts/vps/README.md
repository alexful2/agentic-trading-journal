# VPS scaffolding (optional)

> **Optional integration.** This is *one* way to run the skills unattended — on a
> small Linux VPS via systemd timers. You can use cron or the GitHub Actions
> workflows in `.github/workflows/` instead, or just run the skills interactively
> and **delete this directory entirely.** Nothing here is required.

These scripts are meant to be deployed to a server (e.g. a ~$5/mo Linux VPS) under
an install path like `/opt/trading-journal/`. They're tracked in the repo so
changes are reviewable; the server is the runtime. All paths/users below are
placeholders — set your own.

## Files that ship here

### `daily-news.sh`
Systemd-triggered daily-report runner. The report model is switchable by
environment variable instead of editing the wrapper:

```bash
DAILY_NEWS_AGENT=claude   # run the news-analyst via Claude Code
DAILY_NEWS_AGENT=codex    # or via Codex (GPT) — optional
```

Both branches share the same prompt, repo-lock handling, commit/push step, and
(optional) email pipeline. If Codex is configured but missing/failing, the wrapper
falls back to Claude so the report still ships.

After the daily commit, the push can trigger
`.github/workflows/publish-dashboard-pages.yml` to regenerate the public Pages
dashboard (also optional — delete the workflow if you don't publish one).

### `news-read.sh` + `news-read@.service`
Auto-triggered by `check_intraday_news.py` when a sev-4 alert fires on a Tier-1
ticker. Runs a short "what just happened?" news read and pushes a 3-line verdict
(Pushover). It is **alert-shaped, not order-shaped** — distinct from the
`stock-deep-dive` skill and the `pre-trade` gate.

```
news worker sev-4 (Tier-1)
  → push headline alert (T+0)
  → systemctl start news-read@<INSTANCE>.service
      → news-read.sh reads /tmp/news-read/<INSTANCE>.env
      → claude --print "news-read on $TICKER"   (T+1–3 min)
      → push 3-line verdict
```

**Why a transient templated unit (not a `Popen` detach).** systemd's default
`KillMode=control-group` kills the whole cgroup when a `Type=oneshot` parent
exits — so a child detached from the worker's process group gets killed mid-run.
Running each invocation as its own transient unit gives it an independent cgroup.
(Kept here because it's a non-obvious gotcha worth documenting.)

## Deploy (generic)

Copy from the git checkout — **don't `scp` from a Windows workstation**, CRLF line
endings break the shebang (`status 203/EXEC`):

```bash
ssh youruser@YOUR_VPS_HOST 'cd /opt/trading-journal/trading-journal && git pull \
    && sudo cp .claude/scripts/vps/daily-news.sh  /opt/trading-journal/scripts/ \
    && sudo cp .claude/scripts/vps/news-read.sh   /opt/trading-journal/scripts/ \
    && sudo chmod +x /opt/trading-journal/scripts/*.sh \
    && sudo cp .claude/scripts/vps/news-read@.service /etc/systemd/system/ \
    && sudo systemctl daemon-reload'
```

Then create matching `.timer` units for the schedule you want (see the
`.github/workflows/*.yml` `OnCalendar`-equivalent cron lines for reference
timings), and `systemctl enable --now` them.

## Configuration

- **Secrets** come from an `EnvironmentFile` (e.g. `/opt/trading-journal/secrets.env`,
  mode 600) — `CLAUDE_CODE_OAUTH_TOKEN`, and optionally `RESEND_API_KEY`,
  `PUSHOVER_*`, etc. **Never commit this file.**
- The `news-read@.service` unit has a placeholder `User=` — set it to the account
  the worker runs as. That account needs write access to the log dir and (for the
  auto-trigger) permission to `systemctl start` the transient unit.

## Kill switches

1. `--no-news-read` flag on `check_intraday_news.py` — per-run skip.
2. `INTRADAY_NEWS_READ_DISABLED=1` env var — disable globally.
3. `sudo systemctl mask news-read@.service` — make the spawn a no-op.

## Logs

- Wrapper runs: `${INTRADAY_NEWS_READ_LOG_DIR:-/var/log/trading-journal}/news-read-TICKER-*.log`
- Unit journal: `sudo journalctl -u 'news-read@*.service' --since '1 hour ago'`
