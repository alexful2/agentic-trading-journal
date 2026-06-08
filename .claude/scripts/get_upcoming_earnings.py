#!/usr/bin/env python3
"""
List upcoming earnings prints for watchlist tickers.

Reads `vault/companies/TICKER/_meta.md` for a structured `next_earnings:`
line, computes trading-day distance, and notes whether a pre-earnings
file already exists for that print. Output drives the daily report's
"Active Earnings Windows" section.

The `next_earnings:` line in `_meta.md` is the authoritative date. Format:
    next_earnings: 2026-05-05  (or `next_earnings: 2026-05-05 (estimated)` — the parens are ignored)

Tickers must appear in `vault/watchlist.md` (any tier) to qualify.
The check is silent for tickers with no dossier or no `next_earnings:` line.

Usage:
    python get_upcoming_earnings.py                  # JSON to stdout
    python get_upcoming_earnings.py --window-days 14 # custom window (default: 14)
    python get_upcoming_earnings.py --output upcoming.json
"""

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    _PT = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001 — ImportError on Py<3.9, ZoneInfoNotFoundError on Windows w/o tzdata
    _PT = None


DEFAULT_WINDOW_TRADING_DAYS = 14


def _today_pt():
    """Today's date in Pacific time. Workflows run on UTC runners; near
    midnight PT, `date.today()` would be one day ahead of the user's
    actual day. Falls back to UTC if zoneinfo/tzdata isn't available."""
    if _PT is not None:
        return datetime.now(_PT).date()
    return datetime.now(timezone.utc).date()


def _trading_days_between(start, end):
    """Count weekday days from start (exclusive) to end (inclusive). Negative
    if end is before start. Doesn't account for US holidays — close enough
    for a 2-week look-ahead, and erring on the high side is harmless here."""
    if end < start:
        return -_trading_days_between(end, start)
    days = 0
    cur = start
    while cur < end:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            days += 1
    return days


def _parse_watchlist_tickers(path):
    """Return set of all tickers in the watchlist (T1 + T2 + T3)."""
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    tickers = set()
    in_table = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and re.search(r"\|\s*Ticker\s*\|", s, re.IGNORECASE):
            in_table = True
            continue
        if not s.startswith("|"):
            in_table = False
            continue
        if in_table and re.match(r"^\|\s*-+", s):
            continue
        if in_table:
            parts = [p.strip() for p in s.strip("|").split("|")]
            if not parts:
                continue
            tk = parts[0].upper()
            # Filter to plausible tickers (alphabetic, ≤6 chars).
            if re.match(r"^[A-Z]{1,6}$", tk):
                tickers.add(tk)
    return tickers


def _parse_next_earnings(meta_path):
    """Return (date, raw_value) for the `next_earnings:` line in _meta.md, or
    (None, None) if not present or unparseable."""
    if not meta_path.exists():
        return None, None
    text = meta_path.read_text(encoding="utf-8")
    # Match either bare-key (`next_earnings: 2026-05-05`) or bolded
    # (`**Next earnings:** 2026-05-05`). Take the first hit.
    m = re.search(
        r"^(?:next_earnings|\*\*Next earnings\*\*)\s*:\s*([\d\-]+)",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    if not m:
        return None, None
    raw = m.group(1).strip()
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date(), raw
    except ValueError:
        return None, raw


def _find_pre_earnings_file(reports_dir, ticker, print_date):
    """Look for a pre-earnings file for this ticker+date. Prefer -gate over
    -initial when both exist. Returns (filename_without_ext, mode) or (None, None)."""
    if not reports_dir.exists():
        return None, None
    base = f"{ticker}-{print_date.isoformat()}"
    gate = reports_dir / f"{base}-gate.md"
    initial = reports_dir / f"{base}-initial.md"
    if gate.exists():
        return f"{base}-gate", "gate"
    if initial.exists():
        return f"{base}-initial", "initial"
    return None, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default="vault")
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_TRADING_DAYS,
                        help=f"Surface prints within next N trading days (default: {DEFAULT_WINDOW_TRADING_DAYS})")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    args = parser.parse_args()

    vault_root = Path(args.vault)
    watchlist_path = vault_root / "watchlist.md"
    companies_dir = vault_root / "companies"
    pre_earnings_dir = vault_root / "reports" / "pre-earnings"

    tickers = _parse_watchlist_tickers(watchlist_path)
    today = _today_pt()

    upcoming = []
    no_dossier = []
    no_field = []
    for ticker in sorted(tickers):
        meta_path = companies_dir / ticker / "_meta.md"
        if not meta_path.exists():
            no_dossier.append(ticker)
            continue
        print_date, raw = _parse_next_earnings(meta_path)
        if print_date is None:
            no_field.append(ticker)
            continue
        td = _trading_days_between(today, print_date)
        if td < 0 or td > args.window_days:
            continue
        pe_file, pe_mode = _find_pre_earnings_file(pre_earnings_dir, ticker, print_date)
        upcoming.append({
            "ticker": ticker,
            "print_date": print_date.isoformat(),
            "trading_days_until": td,
            "calendar_days_until": (print_date - today).days,
            "has_pre_earnings_file": pe_file is not None,
            "pre_earnings_file": pe_file,
            "pre_earnings_mode": pe_mode,
        })

    upcoming.sort(key=lambda u: u["trading_days_until"])

    summary = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "today": today.isoformat(),
        "window_days": args.window_days,
        "watchlist_tickers": sorted(tickers),
        "upcoming": upcoming,
        "tickers_without_dossier": no_dossier,
        "tickers_without_next_earnings_field": no_field,
    }
    out = json.dumps(summary, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
