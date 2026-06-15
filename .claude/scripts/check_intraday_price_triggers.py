#!/usr/bin/env python3
"""
Intraday price-trigger worker. Runs on a 15-min GitHub Actions cron during
US market hours, checks watchlist + broader price triggers and planned
tranches against current prices via the existing daily checker, and pushes
mobile notifications for newly-fired levels via Pushover.

Outputs:
- Pushover push notification — the live alert.
- Append to vault/reports/intraday-alerts/YYYY-MM-DD.md — the persistent
  record. Committed back to main by the GH Actions workflow.

State (avoid re-alerting the same fire on every 15-min tick):
- A small JSON file at .intraday-state/YYYY-MM-DD.json keyed by date,
  listing the (type:ticker:direction) ids that have already been alerted
  today. Persisted between GH Actions runs via actions/cache. Resets
  naturally at the date boundary (next day → new file → empty list).

Trigger sources (the underlying checker handles parsing):
- vault/watchlist.md (Tier 1/2 holdings — full sev-3 weight)
- vault/price-triggers.md (broader universe — lighter)
- watchlist.md ## Planned Tranches (active staged orders)

Required env:
- PUSHOVER_TOKEN — application API token from pushover.net
- PUSHOVER_USER — user/group key from pushover.net dashboard

Usage:
    python .claude/scripts/check_intraday_price_triggers.py
    python .claude/scripts/check_intraday_price_triggers.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHECK_SCRIPT = REPO_ROOT / ".claude/skills/news-analyst/scripts/check_price_triggers.py"
POSITIONS_SCRIPT = REPO_ROOT / ".claude/scripts/get_positions.py"
WATCHLIST = REPO_ROOT / "vault/watchlist.md"
BROADER = REPO_ROOT / "vault/price-triggers.md"

TRIM_STATUSES = {"FIRED_TRIM", "FIRED_TRANCHE_TRIM"}

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

FIRED_STATUSES = {
    "FIRED_BUY",
    "FIRED_TRIM",
    "FIRED_TRANCHE_BUY",
    "FIRED_TRANCHE_TRIM",
}


class PushoverError(RuntimeError):
    pass


def send_pushover(title: str, message: str, priority: int = 0) -> None:
    """POST a notification to Pushover. Raises PushoverError on failure."""
    token = os.environ.get("PUSHOVER_TOKEN")
    user = os.environ.get("PUSHOVER_USER")
    if not token or not user:
        raise PushoverError("PUSHOVER_TOKEN and PUSHOVER_USER must be set")

    # Pushover caps: title 250 chars, message 1024 chars.
    title = title[:250]
    message = message[:1024]

    data = urllib.parse.urlencode({
        "token": token,
        "user": user,
        "title": title,
        "message": message,
        "priority": str(priority),
    }).encode("utf-8")

    req = urllib.request.Request(PUSHOVER_URL, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            payload = json.loads(body) if body else {}
            if payload.get("status") != 1:
                raise PushoverError(f"non-success response: {body}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise PushoverError(f"HTTP {e.code}: {err_body}") from e
    except urllib.error.URLError as e:
        raise PushoverError(f"URL error: {e}") from e


def run_checker(watchlist_path: Path, label: str) -> dict:
    cmd = [
        sys.executable,
        str(CHECK_SCRIPT),
        "--watchlist",
        str(watchlist_path),
        "--label",
        label,
    ]
    # Retry on transient subprocess failures (Stooq hiccups, network blips).
    # Without retries, a single bad request kills the whole 15-min tick;
    # with them, we ride out brief outages and still alert on persistent
    # failures (the next */15 cron will re-fire either way).
    import time
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            out = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
            return json.loads(out)
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < 2:
                time.sleep(2 ** attempt)  # 1s, 2s
    raise RuntimeError(f"run_checker failed after 3 attempts: {last_err}") from last_err


def load_shares_held() -> dict[str, float]:
    """Return {ticker: shares_held} from the trade log. Trim triggers for tickers
    with zero shares held are stale (position closed, watchlist row not yet
    cleaned up) and should be suppressed. Buy triggers are unaffected — the
    user may not hold yet.

    Failure mode: if get_positions.py errors or returns malformed JSON, log
    to stderr and return empty dict. Empty dict means no suppression — the
    intraday worker reverts to its old behavior, which is the safe fallback.
    """
    if not POSITIONS_SCRIPT.exists():
        return {}
    try:
        out = subprocess.check_output(
            [sys.executable, str(POSITIONS_SCRIPT), "--format", "json", "--no-prices"],
            cwd=str(REPO_ROOT),
            text=True,
            timeout=30,
        )
        data = json.loads(out)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as e:
        print(f"position lookup failed, skipping suppression: {e}", file=sys.stderr)
        return {}
    return {p["ticker"]: float(p.get("shares_held", 0)) for p in data.get("positions", [])}


def suppress_stale_trims(fired: list[dict], shares_held: dict[str, float]) -> tuple[list[dict], list[dict]]:
    """Split fired rows into (kept, suppressed). A trim trigger is suppressed
    when shares_held for its ticker is zero (or the ticker has no trade-log
    entry at all — same signal: not held). Buy triggers always pass through.

    Empty shares_held dict (position lookup failed) → no suppression."""
    if not shares_held:
        return fired, []
    kept, suppressed = [], []
    for row in fired:
        if row["status"] in TRIM_STATUSES and shares_held.get(row["ticker"], 0) <= 0:
            suppressed.append(row)
        else:
            kept.append(row)
    return kept, suppressed


def fire_id(row: dict) -> str:
    """Stable id for state-tracking. Includes the trigger level (and tranche
    expiry) so two same-direction rows for the same ticker — e.g. NVDA buy
    @245 and NVDA buy @235 — get separate state entries. Without level in
    the id, the second fire would be suppressed by the first day's alert."""
    if row["type"] == "trigger":
        direction = "buy" if row["status"] == "FIRED_BUY" else "trim"
        level = row.get("buy_below") if direction == "buy" else row.get("trim_above")
        suffix = f"{level}"
    else:
        direction = "buy" if row["status"] == "FIRED_TRANCHE_BUY" else "trim"
        suffix = f"{row.get('at_price')}:{row.get('expires') or ''}"
    return f"{row['type']}:{row['ticker']}:{direction}:{row.get('label', '')}:{suffix}"


def _direction_of(row: dict) -> str:
    return "buy" if "BUY" in row["status"] else "trim"


def _level_of(row: dict) -> float | None:
    if row["type"] == "trigger":
        return row.get("buy_below") if _direction_of(row) == "buy" else row.get("trim_above")
    return row.get("at_price")


def collapse_key(row: dict) -> tuple[str, str, float | None]:
    """Group key: same ticker + direction + level. A watchlist Trim-Above row
    and a Planned-Tranche trim row pointing at the same price (e.g., DLR
    trim ≥ $230 + DLR tranche trim 1 sh @ $230) produce two near-identical
    alerts; collapsing on this key folds them into one display row. Distinct
    levels (DLR trim 230 vs 270) remain separate alerts."""
    lvl = _level_of(row)
    return (row["ticker"], _direction_of(row), round(lvl, 2) if lvl is not None else None)


def collapse_fires(fires: list[dict]) -> list[dict]:
    """Merge same-ticker / same-direction / same-level fires into one
    display row. Watchlist trigger is preferred as the primary (carries the
    long-horizon framing); concurrent tranche fires attach as
    `_collapsed_peers` so format_message_body / format_log_lines can render
    them as sub-lines (the tranche's order/size/expiry).

    State (alerted ids) still tracks each fire individually — only the
    display is collapsed, so a re-fire of either row alone tomorrow still
    suppresses correctly."""
    groups: dict[tuple, list[dict]] = {}
    order: list[tuple] = []
    for r in fires:
        k = collapse_key(r)
        if k not in groups:
            order.append(k)
        groups.setdefault(k, []).append(r)
    out: list[dict] = []
    for k in order:
        rows = groups[k]
        if len(rows) == 1:
            out.append(rows[0])
            continue
        primary = next((r for r in rows if r["type"] == "trigger"), rows[0])
        peers = [r for r in rows if r is not primary]
        merged = dict(primary)
        merged["_collapsed_peers"] = peers
        out.append(merged)
    return out


def _peer_summary(peer: dict) -> str:
    """One-line description of a collapsed-peer row, used as a sub-bullet
    under the primary fire's line."""
    if peer["type"] == "tranche":
        bits: list[str] = []
        if peer.get("size"):
            bits.append(str(peer["size"]))
        if peer.get("order"):
            bits.append(peer["order"])
        if peer.get("expires"):
            bits.append(f"expires {peer['expires']}")
        detail = ", ".join(bits) if bits else "tranche fire"
        return f"also: tranche {detail}"
    return f"also: {peer.get('label', 'other source')} trigger"


def fire_label(row: dict) -> str:
    """Human-readable: 'NVDA buy @ $42.00'. Adds an intraday-touch suffix
    when the row fired on day low/high rather than the current tick price."""
    if row["type"] == "trigger":
        if row["status"] == "FIRED_BUY":
            base = f"{row['ticker']} buy ≤ ${row['buy_below']:.2f}"
        else:
            base = f"{row['ticker']} trim ≥ ${row['trim_above']:.2f}"
    elif row["status"] == "FIRED_TRANCHE_BUY":
        base = f"{row['ticker']} tranche buy ≤ ${row['at_price']:.2f} ({row['size']})"
    else:
        base = f"{row['ticker']} tranche trim ≥ ${row['at_price']:.2f} ({row['size']})"
    if row.get("triggered_by") == "intraday":
        base += " [intraday touch]"
    return base


def intraday_context(row: dict) -> str | None:
    """Return a one-line context string for an intraday-touch fire, or None
    when the trigger fired on the current tick price (and so needs no extra
    explanation)."""
    if row.get("triggered_by") != "intraday":
        return None
    is_buy_side = row["status"] in ("FIRED_BUY", "FIRED_TRANCHE_BUY")
    extreme = row.get("day_low") if is_buy_side else row.get("day_high")
    word = "low" if is_buy_side else "high"
    direction = "rebounded" if is_buy_side else "pulled back"
    if extreme is None:
        return f"price has {direction}; trigger touched intraday but not at this tick"
    return f"day {word} ${extreme:.2f} crossed the level; price now ${row['current_price']:.2f} ({direction})"


def build_title(new_fires: list[dict]) -> str:
    if len(new_fires) == 1:
        r = new_fires[0]
        action = "trim" if "TRIM" in r["status"] else "buy"
        return f"{r['ticker']} hit {action} trigger @ ${r['current_price']:.2f}"
    return f"{len(new_fires)} intraday triggers fired"


def format_message_body(new_fires: list[dict], stamp: str) -> str:
    lines = [stamp, ""]
    for r in new_fires:
        lines.append(f"— {fire_label(r)}  (now ${r['current_price']:.2f}, {r['price_source']})")
        ctx = intraday_context(r)
        if ctx:
            lines.append(f"  {ctx}")
        for peer in r.get("_collapsed_peers", []):
            lines.append(f"  + {_peer_summary(peer)}")
        details = []
        if r.get("type") == "tranche" and r.get("order"):
            details.append(f"order: {r['order']}")
        if r.get("funded_by"):
            details.append(f"funded by {r['funded_by']}")
        if r.get("prefer_over"):
            details.append(f"prefer over {', '.join(r['prefer_over'])}")
        if r.get("deferred_due_to"):
            details.append(f"DEFERRED — {', '.join(r['deferred_due_to'])} ranked higher")
        if details:
            lines.append("  " + " · ".join(details))
        if r.get("note"):
            lines.append(f"  {r['note']}")
    return "\n".join(lines).rstrip()


def format_log_lines(new_fires: list[dict], stamp_short: str) -> str:
    lines = [f"## {stamp_short}", ""]
    for r in new_fires:
        prefix = "[tranche]" if r["type"] == "tranche" else f"[{r['label']}]"
        lines.append(f"- {prefix} **{fire_label(r)}** — current ${r['current_price']:.2f} ({r['price_source']})")
        ctx = intraday_context(r)
        if ctx:
            lines.append(f"  - {ctx}")
        for peer in r.get("_collapsed_peers", []):
            lines.append(f"  - {_peer_summary(peer)}")
        if r.get("type") == "tranche" and r.get("order"):
            lines.append(f"  - Order: {r['order']}")
        if r.get("funded_by"):
            lines.append(f"  - Funded by: {r['funded_by']}")
        if r.get("prefer_over"):
            lines.append(f"  - Prefer over: {', '.join(r['prefer_over'])}")
        if r.get("deferred_due_to"):
            lines.append(f"  - **Deferred** — {', '.join(r['deferred_due_to'])} ranked higher today")
        if r.get("note"):
            lines.append(f"  - {r['note']}")
    lines.append("")
    return "\n".join(lines)


def send_system_alert(reason: str, stamp: str, dry_run: bool) -> None:
    """One-off failure push when prices can't be fetched at all."""
    title = "Intraday worker: price fetch failure"
    body = (
        f"{stamp}\n\n"
        f"Reason: {reason}\n\n"
        "If this persists, check Stooq availability and the GH Actions log."
    )
    if dry_run:
        print(f"[DRY RUN] would push system alert: {reason}")
        return
    try:
        send_pushover(title=title, message=body, priority=0)
    except PushoverError as e:
        print(f"system alert push failed: {e}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=".intraday-state")
    ap.add_argument("--vault-dir", default="vault/reports/intraday-alerts")
    ap.add_argument("--dry-run", action="store_true", help="Skip push, state write, and vault log write.")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    today_iso = now.date().isoformat()
    stamp_short = now.strftime("%H:%M UTC")
    stamp = f"{today_iso} {stamp_short}"

    summaries = []
    if WATCHLIST.exists():
        summaries.append(run_checker(WATCHLIST, "watchlist"))
    if BROADER.exists():
        summaries.append(run_checker(BROADER, "broader"))

    results = [row for s in summaries for row in s["results"]]
    total = len(results)
    errors = [r for r in results if r["status"] == "ERROR"]
    fired = [r for r in results if r["status"] in FIRED_STATUSES]

    # Fail loudly if every row errored — likely Stooq blocked / outage.
    if total > 0 and len(errors) == total:
        diagnostic = next(
            (s.get("diagnostic") for s in summaries if s.get("diagnostic")),
            "all rows errored, no diagnostic",
        )
        print(f"all {total} rows errored: {diagnostic}", file=sys.stderr)
        # Use a state flag so we don't push this every 15 min — once per day.
        state_dir = Path(args.state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        flag = state_dir / f"{today_iso}-fetch-fail.flag"
        if not flag.exists():
            send_system_alert(diagnostic, stamp, args.dry_run)
            if not args.dry_run:
                flag.write_text(stamp)
        return 1

    if not fired:
        print(f"checked {total} rows, 0 fired.")
        return 0

    # Suppress trim fires for tickers with zero shares held (the trade log is
    # the source of truth — a trim trigger on a closed position is a stale row
    # the user forgot to clean up, not an actionable alert).
    shares_held = load_shares_held()
    fired, stale_trims = suppress_stale_trims(fired, shares_held)
    for r in stale_trims:
        print(f"suppressed stale trim trigger: {r['ticker']} (0 shares held)", file=sys.stderr)
    if not fired:
        print(f"checked {total} rows, all fires were stale trims (no position held).")
        return 0

    state_dir = Path(args.state_dir)
    state_path = state_dir / f"{today_iso}.json"
    already: set[str] = set()
    if state_path.exists():
        try:
            already = set(json.loads(state_path.read_text(encoding="utf-8")).get("alerted", []))
        except (OSError, json.JSONDecodeError):
            pass

    new_fires = [r for r in fired if fire_id(r) not in already]
    if not new_fires:
        print(f"checked {total} rows, {len(fired)} fired, all already alerted today.")
        return 0

    # Collapse same-ticker / same-direction / same-level fires for display
    # (e.g., watchlist Trim 230 + planned-tranche Trim @ 230). State still
    # tracks the originals individually via `new_fires` below.
    display_fires = collapse_fires(new_fires)
    if len(display_fires) < len(new_fires):
        print(f"collapsed {len(new_fires)} fires into {len(display_fires)} display rows.")

    title = build_title(display_fires)
    message = format_message_body(display_fires, stamp)

    if args.dry_run:
        print(f"[DRY RUN] would push: {title}")
        print("---")
        print(message)
        return 0

    try:
        send_pushover(title=title, message=message, priority=1)
        print(f"pushed: {title}")
    except PushoverError as e:
        print(f"pushover send failed: {e}", file=sys.stderr)
        return 1

    vault_log = Path(args.vault_dir) / f"{today_iso}.md"
    vault_log.parent.mkdir(parents=True, exist_ok=True)
    if not vault_log.exists():
        vault_log.write_text(
            f"# Intraday Price Triggers — {today_iso}\n\n"
            "Auto-generated by `.claude/scripts/check_intraday_price_triggers.py`. "
            "One block per 15-min tick that produced a new fire. "
            "Not investment advice.\n\n",
            encoding="utf-8",
        )
    with vault_log.open("a", encoding="utf-8") as f:
        f.write(format_log_lines(display_fires, stamp_short))

    state_dir.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"date": today_iso, "alerted": sorted(already | {fire_id(r) for r in new_fires})}, indent=2),
        encoding="utf-8",
    )
    print(f"alerted on {len(new_fires)} new fire(s); logged to {vault_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
