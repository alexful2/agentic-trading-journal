#!/bin/bash
# daily-news.sh - scheduled daily news report runner.
#
# Deployed on the VPS as /opt/trading-journal/scripts/daily-news.sh.
# Model switch:
#   DAILY_NEWS_AGENT=codex   # default
#   DAILY_NEWS_AGENT=claude  # fallback / comparison

set -euo pipefail

# Common helpers: PATH, secrets, venv, log/timestamp helpers, repo_lockfile,
# git_pull_clean, commit_and_push.
# shellcheck disable=SC1091
. /opt/trading-journal/scripts/_common.sh

REPO="${TRADING_JOURNAL_REPO:-/opt/trading-journal/trading-journal}"
AGENT="${DAILY_NEWS_AGENT:-codex}"
PROMPT="${DAILY_NEWS_PROMPT:-Run the daily news analysis for today. Read AGENTS.md, CLAUDE.md, and .claude/skills/news-analyst/SKILL.md, then follow the news-analyst workflow exactly.}"

run_claude_agent() {
    log "daily-news agent=claude"
    DAILY_NEWS_FOOTER_MODEL="${DAILY_NEWS_FOOTER_MODEL:-Claude Opus 4.7}" \
        claude --print --dangerously-skip-permissions "$PROMPT"
}

run_daily_news_agent() {
    case "$AGENT" in
        codex)
            local model reasoning footer_model
            model="${DAILY_NEWS_CODEX_MODEL:-gpt-5.5}"
            reasoning="${DAILY_NEWS_CODEX_REASONING:-high}"
            footer_model="${DAILY_NEWS_FOOTER_MODEL:-Codex ${model} (${reasoning} reasoning)}"

            if ! command -v codex >/dev/null 2>&1; then
                log "codex CLI missing"
                if [ "${DAILY_NEWS_CODEX_FALLBACK_TO_CLAUDE:-1}" = "1" ]; then
                    log "falling back to claude"
                    run_claude_agent
                    return
                fi
                exit 127
            fi

            log "daily-news agent=codex model=$model reasoning=$reasoning"
            if ! DAILY_NEWS_FOOTER_MODEL="$footer_model" \
                codex exec \
                    --cd "$REPO" \
                    --model "$model" \
                    -c "model_reasoning_effort=\"$reasoning\"" \
                    --dangerously-bypass-approvals-and-sandbox \
                    --search \
                    "$PROMPT"; then
                log "codex daily-news run failed"
                if [ "${DAILY_NEWS_CODEX_FALLBACK_TO_CLAUDE:-1}" = "1" ]; then
                    log "falling back to claude"
                    run_claude_agent
                    return
                fi
                exit 1
            fi
            ;;
        claude)
            run_claude_agent
            ;;
        *)
            log "unknown DAILY_NEWS_AGENT=$AGENT; expected codex or claude"
            exit 2
            ;;
    esac
}

publish_dashboard_pages() {
    if [ "${DASHBOARD_PAGES_DEPLOY_DISABLED:-0}" = "1" ]; then
        log "dashboard pages deploy disabled"
        return
    fi

    local pages_repo
    pages_repo="${DASHBOARD_PAGES_REPO:-/opt/trading-journal/trading-dashboard}"
    if [ ! -d "$pages_repo/.git" ]; then
        log "dashboard pages repo missing at $pages_repo; skip public deploy"
        return
    fi

    log "dashboard pages deploy start"
    if ! python dashboard/deploy_pages.py --skip-generate --pages-repo "$pages_repo"; then
        log "dashboard pages deploy failed"
        return
    fi
    log "dashboard pages deploy done"
}

LOCK="$(repo_lockfile "$REPO")"

# Phase 1: sync repo while locked.
(
    flock -x -w 1800 9 || { log "lock timeout during pull phase"; exit 1; }
    log "daily-news start"
    git_pull_clean "$REPO"
) 9>"$LOCK"

# Phase 2: run the LLM unlocked so intraday jobs do not stall behind a long
# news-analysis turn. The model branch is the only intended difference here.
cd "$REPO"
run_daily_news_agent

# Phase 3: commit and push the report / related deterministic outputs.
(
    flock -x -w 1800 9 || { log "lock timeout during commit phase"; exit 1; }
    cd "$REPO"
    if [ "${DASHBOARD_PAGES_DEPLOY_DISABLED:-0}" != "1" ]; then
        log "dashboard regenerate"
        python dashboard/generate_dashboard.py
    fi
    commit_and_push "daily report: $(date -u +%Y-%m-%d)" \
        vault/reports/daily \
        vault/watchlist.md \
        vault/price-triggers.md \
        vault/companies \
        vault/deep-dives \
        vault/ipo-calendar.md \
        dashboard/index.html \
        dashboard/.nojekyll
    log "daily-news done"
) 9>"$LOCK"

# Public GitHub Pages deploy is intentionally after the private repo commit.
# It uses the committed dashboard/index.html and should not dirty this repo.
publish_dashboard_pages
