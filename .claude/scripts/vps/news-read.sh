#!/bin/bash
# news-read.sh — auto-spawned via news-read@.service when check_intraday_news.py
# scores a sev-4 alert on a real ticker (any Tier). Produces a brief 3-line
# "what just happened?" summary and pushes it to Pushover.
#
# Distinct from the stock-deep-dive skill (which runs scripts + 3-advisor
# council + writes a full file). This is alert-shaped — "what just happened?".
# Memory: [[feedback_auto_trigger_news_shape]].
#
# Architecture:
# - Spawned as its own templated systemd unit (news-read@<instance>.service)
#   so it survives the parent intraday-news.service exit. Previous Popen
#   approach was killed by systemd cgroup-kill when the parent oneshot
#   service deactivated; the transient-unit pattern gives each invocation
#   its own cgroup.
# - Args arrive via /tmp/news-read/<instance>.env, sourced at script start.
#   The .service unit's ExecStopPost cleans up the env file.
# - Per-ticker flock prevents duplicate runs when two consecutive 20-min
#   ticks both catch a sev-4 on the same name.
# - Repo flock + git_pull_simple in Phase 1 (matches the intraday-worker
#   pattern from [[vps_lock_architecture]] — concurrent dirty tree is
#   expected since another job's Phase 2 may be running).
# - Phase 2 (the Claude call) runs UNLOCKED — news-read is read-only, so
#   no Phase 3 commit/push is needed.
#
# Args:
#   $1 = instance name (e.g. NVDA-20260514T202049Z)
#         resolves env file at /tmp/news-read/<instance>.env containing:
#           TICKER=<...>
#           CATEGORY=<...>     (e.g. "8-K — material agreement (Item 1.01)")
#           HEADLINE=<...>     (filing-type description or wire headline)
#           URL=<...>          (link to filing/article, used by WebFetch)
#
# Deploy (from a workstation with SSH access to the VPS):
#   scp .claude/scripts/vps/news-read.sh youruser@YOUR_VPS_HOST:/tmp/
#   ssh youruser@YOUR_VPS_HOST 'sudo mv /tmp/news-read.sh /opt/trading-journal/scripts/ \
#       && sudo chmod +x /opt/trading-journal/scripts/news-read.sh'
#   scp .claude/scripts/vps/news-read@.service youruser@YOUR_VPS_HOST:/tmp/
#   ssh youruser@YOUR_VPS_HOST 'sudo mv /tmp/news-read@.service /etc/systemd/system/ \
#       && sudo systemctl daemon-reload'
#
# First-time setup (creates the log dir owned by the worker user):
#   ssh youruser@YOUR_VPS_HOST 'sudo mkdir -p /var/log/trading-journal \
#       && sudo chown youruser:youruser /var/log/trading-journal'
#
# Smoke test on VPS:
#   sudo mkdir -p /tmp/news-read && sudo chown youruser:youruser /tmp/news-read
#   cat >/tmp/news-read/SMOKE.env <<'EOF'
#   TICKER='NVDA'
#   CATEGORY='smoke test'
#   HEADLINE='SmokeTest'
#   URL=''
#   EOF
#   sudo systemctl start news-read@SMOKE.service
#   tail -f /var/log/trading-journal/news-read-NVDA-*.log

set -euo pipefail

INSTANCE="${1:?instance name required}"

ENV_FILE="/tmp/news-read/${INSTANCE}.env"
if [ ! -r "$ENV_FILE" ]; then
    echo "news-read.sh: env file missing or unreadable: $ENV_FILE" >&2
    exit 2
fi
# shellcheck disable=SC1090
set -a
. "$ENV_FILE"
set +a

TICKER="${TICKER:?TICKER required in env file}"
CATEGORY="${CATEGORY:-}"
HEADLINE="${HEADLINE:-}"
URL="${URL:-}"

# Common helpers: PATH, secrets (PUSHOVER_*, CLAUDE_CODE_OAUTH_TOKEN, etc.),
# venv activation, log/timestamp helpers, repo_lockfile, git_pull_simple.
# shellcheck disable=SC1091
. /opt/trading-journal/scripts/_common.sh

REPO="${TRADING_JOURNAL_REPO:-/opt/trading-journal/trading-journal}"
LOG_DIR="${INTRADAY_NEWS_READ_LOG_DIR:-/var/log/trading-journal}"
# /tmp/trading-journal-locks chosen over /run/trading-journal so the wrapper runs
# under non-root users without a systemd-tmpfiles.d entry. Locks are
# inherently ephemeral (process-lifetime), so /tmp's auto-cleanup is fine.
LOCK_DIR="${INTRADAY_NEWS_READ_LOCK_DIR:-/tmp/trading-journal-locks}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/news-read-${TICKER}-${TS}.log"

mkdir -p "$LOG_DIR" "$LOCK_DIR"

# Redirect all subsequent stdout/stderr to the log file. systemd's journal
# capture sees only what runs before this exec; everything after lives in
# the log file. This mirrors the prior news-deep-dive.sh design.
exec >> "$LOG_FILE" 2>&1

log "news-read start: ticker=$TICKER instance=$INSTANCE category=${CATEGORY:-<none>}"

# Per-ticker single-flight: if a news-read is already running for this
# name (e.g., previous tick still in flight), exit silently. Distinct
# from the repo lock — multiple tickers can run in parallel.
exec 8>"$LOCK_DIR/news-read-${TICKER}.lock"
if ! flock -n 8; then
    log "another news-read in flight for $TICKER; skipping"
    exit 0
fi

# Phase 1: git pull, repo-locked. git_pull_simple (not _clean) because
# this wrapper may fire concurrently with another job's LLM Phase 2 —
# dirty tracked files are expected and should ride out the pull via
# autostash, not be committed as wip-recovery.
REPO_LOCK="$(repo_lockfile "$REPO")"
( flock -x -w 60 9 || { log "repo lock timeout during pull-phase"; exit 1; }
  git_pull_simple "$REPO" || log "git_pull_simple failed; continuing with local tree"
) 9>"$REPO_LOCK"

# Phase 2: the Claude call. UNLOCKED — multi-minute. news-read is read-only,
# so no Phase 3 commit/push needed.
cd "$REPO"

# News-read prompt. Shape: "what just happened?", not "are you sure?".
# Distinct from stock-deep-dive (which runs scripts + 3-advisor council).
# Goal is a
# 30-60s read that surfaces (a) what the news actually says, (b) direction
# and magnitude of impact, (c) whether an order action is warranted now.
#
# The substance line MUST contain real content from the filing/article —
# headline + category alone is a fail, since the user already saw both
# in the first Pushover ping. If WebFetch can't pull useful content, say
# so explicitly so the user knows the substance line is degraded.
PROMPT="Quick news-read on $TICKER. Auto-triggered by the intraday news worker — 'what just happened?' mode, not a buy/sell decision moment.

Trigger:
  category: ${CATEGORY:-<none>}
  headline: ${HEADLINE:-<none>}
  url:      ${URL:-<none>}

Do these fast, in order:
1. If the URL is set and looks like SEC EDGAR or a wire story, WebFetch it — read enough to know the specific number / counterparty / contract / item that matters, not just the headline. For an 8-K, fetch the index page AND the actual exhibit to extract the substance.
2. Skim the most recent thesis note for $TICKER in vault/notes/ (60-second skim, not a deep read) so you can frame impact against the held thesis.
3. Check the watchlist row for $TICKER in vault/watchlist.md for current trigger geometry — knowing the buy/trim levels lets you judge whether action is genuinely needed.

Output exactly 3 short phone-friendly lines. No headers, no markdown, no tables, no preamble.

(1) substance — 1-2 sentences describing what the filing/article ACTUALLY says: the specific number, counterparty, contract, item code with its plain-English meaning, or finding. NOT the category label. NOT 'an 8-K current report'. If WebFetch failed or returned nothing useful, lead with 'Could not fetch — reasoning from headline:' and then summarize what the headline alone implies.

(2) impact — direction (POSITIVE / NEGATIVE / NEUTRAL / AMBIGUOUS) and magnitude (small / moderate / large), with a one-clause why tied to the thesis. Magnitude = expected stock impact, not headline drama. Example: 'NEGATIVE, moderate — guidance cut narrows the FY revenue range below consensus, which directly contradicts the growth-acceleration thesis.'

(3) action — NONE / WATCH / ADJUST-LADDER / ESCALATE-TO-DEEP-DIVE, with a one-clause why. Decision rule: ESCALATE-TO-DEEP-DIVE only if an order action is warranted in the next hour (thesis just broke OR price is already moving past a tranche level). ADJUST-LADDER if the existing buy/trim geometry no longer fits. WATCH if it changes the picture but no order today. NONE if zero action.

Be specific. No file writes. No scripts."

log "prompt prepared, calling claude"
echo "PROMPT: $PROMPT"
echo "---"

VERDICT="$(claude --print --dangerously-skip-permissions "$PROMPT" 2>&1 || true)"
echo "$VERDICT"
echo "---"

if [ -z "$VERDICT" ]; then
    VERDICT="(empty verdict — see $LOG_FILE for details)"
fi

TITLE="[$TICKER] news read"
# Strip ANSI escape codes; tail the most informative bottom of the response
# (Pushover caps at 1024 chars).
BODY="$(printf '%s' "$VERDICT" \
    | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' \
    | tail -c 950)"

if [ -n "${PUSHOVER_TOKEN:-}" ] && [ -n "${PUSHOVER_USER:-}" ]; then
    curl -sS \
        --form-string "token=$PUSHOVER_TOKEN" \
        --form-string "user=$PUSHOVER_USER" \
        --form-string "title=$TITLE" \
        --form-string "message=$BODY" \
        --form-string "priority=1" \
        https://api.pushover.net/1/messages.json || \
        log "pushover send failed"
else
    log "PUSHOVER_TOKEN/USER missing; skipping push"
fi

log "news-read complete for $TICKER"
