#!/usr/bin/env python3
"""
Score a pre-earnings run against the realized post-print move.

Reads the Scenario Ladder from a pre-earnings gate (or initial) file,
fetches close prices on the print date and N trading days later,
identifies which scenario row contained the realized price, and emits
JSON. Used by quarterly-review's calibration pass.

Usage:
    python .claude/scripts/score_print.py --ticker VRT --print-date 2026-05-05
    python .claude/scripts/score_print.py --ticker VRT --print-date 2026-05-05 --horizon 5

Output: JSON to stdout. Exit 0 on success (including future-print case
where realized move is not yet available); exit 1 on hard failures
(missing source file, parse failure, price-fetch error).

Price source: Yahoo Finance v8 chart API (unkeyed, historical OHLC).
quarterly-review is manual-only, so the yfinance-blocked-in-routines
constraint doesn't apply here.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
PRE_EARNINGS_DIR = Path("vault/reports/pre-earnings")


def _fetch_history(ticker, start, end):
    """Return list of (date, close) tuples from Yahoo, oldest first."""
    p1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
    p2 = int(datetime(end.year, end.month, end.day, tzinfo=timezone.utc).timestamp()) + 86400
    url = f"{YAHOO_CHART_URL}{ticker.upper()}?period1={p1}&period2={p2}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result = (data.get("chart") or {}).get("result") or []
    if not result:
        return []
    res = result[0]
    timestamps = res.get("timestamp") or []
    quote = (res.get("indicators") or {}).get("quote") or [{}]
    closes = quote[0].get("close") or []
    rows = []
    for t, c in zip(timestamps, closes):
        if c is None:
            continue
        d = datetime.fromtimestamp(t, tz=timezone.utc).date()
        rows.append((d, float(c)))
    return sorted(rows)


def _find_pre_earnings_file(ticker, print_date):
    """Return all on-disk files for this print, preferred (gate) first.

    Gate files lock in orders T-1/day-of and often carry only a Pre-Commit
    Plan, deferring the Scenario Ladder to the initial file. So the caller
    parses the ladder from the preferred file but falls back to the next
    file when the preferred one has no ladder. Returns a list of
    (path, mode) tuples, gate before initial.
    """
    base = PRE_EARNINGS_DIR / f"{ticker.upper()}-{print_date}"
    found = []
    for suffix in ("gate", "initial"):
        p = Path(f"{base}-{suffix}.md")
        if p.exists():
            found.append((p, suffix))
    return found


def _parse_scenario_ladder(text):
    """Return list of {scenario, probability_pct, price_low, price_high, action}."""
    m = re.search(
        r"##\s*Scenario Ladder\b(.+?)(?=^##\s|\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not m:
        return []
    section = m.group(1)

    rows = []
    header_seen = False
    in_table = False
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if in_table:
                break
            continue
        if not header_seen and "Scenario" in line and "Prob" in line:
            header_seen = True
            continue
        if not header_seen:
            continue
        if re.match(r"^\|\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?\s*$", line):
            in_table = True
            continue
        if not in_table:
            continue

        parts = line.strip("|").split("|")
        if len(parts) < 6:
            continue
        cols = [p.strip() for p in parts[:5]] + ["|".join(parts[5:]).strip()]

        scenario_name = _extract_scenario_name(cols[0])
        prob = _extract_int_pct(cols[1])
        low, high = _extract_price_range(cols[2])
        action = cols[5]
        if scenario_name and prob is not None and low is not None:
            rows.append({
                "scenario": scenario_name,
                "probability_pct": prob,
                "price_low": low,
                "price_high": high,
                "action": action,
            })
    return rows


def _extract_scenario_name(s):
    m = re.search(r"\*\*([^*]+?)\*\*", s)
    if m:
        return m.group(1).strip()
    return re.split(r"\s*\(", re.sub(r"\*+", "", s), 1)[0].strip() or None


def _extract_int_pct(s):
    m = re.search(r"(\d+)\s*%", s)
    return int(m.group(1)) if m else None


def _extract_price_range(s):
    m = re.search(
        r"\$?\s*(\d+(?:\.\d+)?)\s*(?:[–—\-]|to)\s*\$?\s*(\d+(?:\.\d+)?)",
        s,
    )
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def _walk_to_trading_day(rows, anchor_date, offset):
    """Return (date, close) at trading-day offset from the first row on/after anchor_date."""
    idx = next((i for i, (d, _) in enumerate(rows) if d >= anchor_date), None)
    if idx is None:
        return None, None
    target_idx = idx + offset
    if target_idx >= len(rows):
        return None, None
    return rows[target_idx]


def _match_scenario(price, scenarios):
    """Return (matched_or_None, boundary_miss, closest)."""
    for s in scenarios:
        if s["price_low"] <= price <= s["price_high"]:
            return s, False, s
    if not scenarios:
        return None, True, None
    closest = min(
        scenarios,
        key=lambda s: abs(price - (s["price_low"] + s["price_high"]) / 2),
    )
    return None, True, closest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--print-date", required=True, help="YYYY-MM-DD")
    ap.add_argument(
        "--horizon",
        type=int,
        default=5,
        help="Trading days post-print to measure realized move (default 5).",
    )
    args = ap.parse_args()

    ticker = args.ticker.upper()
    try:
        print_date = datetime.strptime(args.print_date, "%Y-%m-%d").date()
    except ValueError:
        json.dump({"error": "invalid --print-date, expect YYYY-MM-DD"}, sys.stdout)
        sys.exit(1)

    out = {
        "ticker": ticker,
        "print_date": args.print_date,
        "horizon_trading_days": args.horizon,
    }

    candidates = _find_pre_earnings_file(ticker, args.print_date)
    if not candidates:
        out["error"] = (
            f"no pre-earnings file at "
            f"{PRE_EARNINGS_DIR}/{ticker}-{args.print_date}-{{gate,initial}}.md"
        )
        json.dump(out, sys.stdout, indent=2)
        sys.exit(1)

    # Parse the ladder from the preferred (gate) file; if it carries no
    # ladder (gate files often defer it to the initial file), fall back.
    scenarios = []
    src_path, mode = candidates[0]
    for cand_path, cand_mode in candidates:
        parsed = _parse_scenario_ladder(cand_path.read_text(encoding="utf-8"))
        if parsed:
            scenarios, src_path, mode = parsed, cand_path, cand_mode
            break
    out["source_file"] = str(src_path).replace("\\", "/")
    out["source_mode"] = mode
    if mode != candidates[0][1]:
        out["ladder_fallback"] = (
            f"preferred '{candidates[0][1]}' file had no Scenario Ladder; "
            f"scored against '{mode}' file"
        )
    out["scenarios"] = scenarios
    if not scenarios:
        out["error"] = (
            "could not parse Scenario Ladder table from any pre-earnings "
            f"file for {ticker} {args.print_date}"
        )
        json.dump(out, sys.stdout, indent=2)
        sys.exit(1)

    # Need horizon trading days after print_date; pad calendar window generously.
    end_date = print_date + timedelta(days=args.horizon * 2 + 7)
    today = datetime.now(timezone.utc).date()
    if end_date > today:
        out["realized_move_pct"] = None
        out["matched_scenario"] = None
        out["note"] = (
            f"horizon end ({end_date}) is in the future; "
            "realized move not yet available"
        )
        json.dump(out, sys.stdout, indent=2)
        sys.exit(0)

    try:
        rows = _fetch_history(ticker, print_date, end_date + timedelta(days=3))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        out["error"] = f"yahoo fetch failed: {type(e).__name__}: {e}"
        json.dump(out, sys.stdout, indent=2)
        sys.exit(1)

    if not rows:
        out["error"] = f"yahoo returned no rows for {ticker} {print_date}–{end_date}"
        json.dump(out, sys.stdout, indent=2)
        sys.exit(1)

    anchor_date, anchor_close = _walk_to_trading_day(rows, print_date, 0)
    target_date, target_close = _walk_to_trading_day(rows, print_date, args.horizon)
    if anchor_close is None or target_close is None:
        out["error"] = "insufficient trading days in Yahoo result"
        json.dump(out, sys.stdout, indent=2)
        sys.exit(1)

    out["spot_at_print_close"] = anchor_close
    out["spot_at_horizon_close"] = target_close
    out["anchor_trading_date"] = anchor_date.isoformat()
    out["horizon_trading_date"] = target_date.isoformat()
    out["realized_move_pct"] = round((target_close / anchor_close - 1) * 100, 2)

    matched, boundary_miss, closest = _match_scenario(target_close, scenarios)
    out["matched_scenario"] = matched
    out["boundary_miss"] = boundary_miss
    if boundary_miss:
        out["closest_scenario"] = closest

    out["did_plan_execute"] = "unverified"

    json.dump(out, sys.stdout, indent=2)
    sys.exit(0)


if __name__ == "__main__":
    main()
