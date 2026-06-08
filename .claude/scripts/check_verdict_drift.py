#!/usr/bin/env python3
"""
Check whether deep-dive verdicts have drifted vs. current price.

Reads vault/deep-dives/_verdicts.md, takes the most recent row per ticker,
filters to verdicts within the last N days (default 60 — older verdicts are
stale enough that drift isn't actionable), fetches current Stooq price, and
emits any row where |drift| ≥ threshold (default 10%).

The daily news-analyst run consumes the JSON output and renders a
"## Verdict Drift" section above macro awareness when there are hits.

Usage:
    python check_verdict_drift.py                          # JSON to stdout
    python check_verdict_drift.py --threshold 15           # 15% drift
    python check_verdict_drift.py --window-days 30         # 30-day window
    python check_verdict_drift.py --output drift.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Sibling import — _stooq.py provides the canonical Stooq fetcher.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _stooq import fetch_close as _fetch_price_stooq  # noqa: E402

try:
    from zoneinfo import ZoneInfo
    _PT = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001 — ImportError on Py<3.9, ZoneInfoNotFoundError on Windows w/o tzdata
    _PT = None


DEFAULT_WINDOW_DAYS = 60
DEFAULT_THRESHOLD_PCT = 10.0


def _today_pt():
    """Today's date in Pacific time. Workflows run on UTC runners; near
    midnight PT, `date.today()` would be one day ahead of the user's
    actual day. Falls back to UTC if zoneinfo/tzdata isn't available."""
    if _PT is not None:
        return datetime.now(_PT).date()
    return datetime.now(timezone.utc).date()


def _parse_ledger(path):
    """Parse the verdict ledger table. Returns list of dicts:
    {date, ticker, verdict, price_at_verdict, file}.
    Skips rows missing a parseable price."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if line.startswith("| Date") or re.match(r"^\|\s*-+", line):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        date_str, ticker, verdict, price_str, file_str = parts[:5]
        try:
            verdict_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        price = None
        m = re.search(r"\$?([\d,]+\.?\d*)", price_str)
        if m:
            try:
                price = float(m.group(1).replace(",", ""))
            except ValueError:
                pass
        if price is None:
            continue
        rows.append({
            "date": verdict_date.isoformat(),
            "ticker": ticker.upper(),
            "verdict": verdict.upper(),
            "price_at_verdict": price,
            "file": _strip_wikilink(file_str),
        })
    return rows


def _strip_wikilink(s):
    # Ledger pointers may be [[wikilinks]] (legacy) or `backticks` (current —
    # backticks avoid Obsidian phantom notes when the deep-dive file is later
    # auto-deleted). Strip either; return as-is otherwise.
    m = re.match(r"\[\[(.+?)\]\]", s)
    if m:
        return m.group(1)
    m = re.match(r"`(.+?)`", s)
    if m:
        return m.group(1)
    return s


def _most_recent_per_ticker(rows):
    """Keep one row per ticker — the latest by date."""
    by_ticker = {}
    for r in rows:
        existing = by_ticker.get(r["ticker"])
        if existing is None or r["date"] > existing["date"]:
            by_ticker[r["ticker"]] = r
    return list(by_ticker.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default="vault")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD_PCT,
                        help=f"Minimum |drift| %% to surface (default: {DEFAULT_THRESHOLD_PCT})")
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS,
                        help=f"Only consider verdicts within last N days (default: {DEFAULT_WINDOW_DAYS})")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    args = parser.parse_args()

    vault_root = Path(args.vault)
    ledger_path = vault_root / "deep-dives" / "_verdicts.md"

    rows = _parse_ledger(ledger_path)
    latest = _most_recent_per_ticker(rows)
    today = _today_pt()
    cutoff = today.toordinal() - args.window_days

    drifts = []
    skipped_old = 0
    errors = []
    for r in latest:
        verdict_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
        age_days = (today - verdict_date).days
        if verdict_date.toordinal() < cutoff:
            skipped_old += 1
            continue
        price, err = _fetch_price_stooq(r["ticker"])
        if price is None:
            errors.append({"ticker": r["ticker"], "error": err})
            continue
        drift_pct = ((price / r["price_at_verdict"]) - 1) * 100
        if abs(drift_pct) >= args.threshold:
            drifts.append({
                "ticker": r["ticker"],
                "verdict": r["verdict"],
                "verdict_date": r["date"],
                "age_days": age_days,
                "price_at_verdict": r["price_at_verdict"],
                "current_price": round(price, 2),
                "drift_pct": round(drift_pct, 1),
                "direction": "up" if drift_pct > 0 else "down",
                "deep_dive_file": r["file"],
            })

    drifts.sort(key=lambda d: -abs(d["drift_pct"]))

    summary = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "ledger_path": str(ledger_path),
        "ledger_rows": len(rows),
        "tickers_in_window": len(latest) - skipped_old,
        "skipped_stale_verdicts": skipped_old,
        "threshold_pct": args.threshold,
        "window_days": args.window_days,
        "drifts": drifts,
        "errors": errors,
    }
    out = json.dumps(summary, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
