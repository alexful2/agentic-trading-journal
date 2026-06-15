#!/usr/bin/env python3
"""
Aggregate open positions from markdown trade-log files.

Walks the trade-log folder under the vault (default vault/trades/, with
automatic fallback to vault/!Journalit/ for Journalit users), parses YAML
frontmatter, and aggregates per-instrument: total shares held (entries minus
exits), entry-weighted average cost, realized P&L from partial exits, and
(optionally) unrealized P&L computed against current Stooq prices.

The trade-file schema (one file per trade) is plain markdown frontmatter:

    ---
    type: trade
    instrument: NVDA
    direction: long
    tradeStatus: OPEN          # OPEN until fully exited, then CLOSED
    entries:                   # one item per buy (tranches welcome)
      - { size: 50, price: 118.40, time: 2026-05-12T14:32:00 }
    exits:                     # one item per sell
      - { size: 25, price: 131.20, time: 2026-06-09T18:45:00 }
    ---

This format is compatible with the Journalit Obsidian plugin's export, so you
can write the files by hand, via the `log-trade` skill, or with Journalit —
whatever you prefer. Journalit is optional; nothing here requires it.

A trade is included if BOTH:
  - tradeStatus is "OPEN"
  - shares_held > 0 (sum of entry sizes minus sum of exit sizes)

Multiple OPEN trade files for the same instrument are aggregated into one
position row (shares and cost basis pooled).

Usage:
    python get_positions.py                          # all open positions, with prices
    python get_positions.py --ticker NVDA            # one ticker only
    python get_positions.py --no-prices              # skip Stooq calls (faster)
    python get_positions.py --format markdown        # human-readable table
    python get_positions.py --vault vault            # custom vault path
    python get_positions.py --trades-dir !Journalit  # force a specific folder
"""

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Sibling import — _stooq.py provides the canonical Stooq fetcher.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _stooq import fetch_close as _fetch_price_stooq  # noqa: E402


def _parse_frontmatter(text):
    """Parse YAML-ish frontmatter at the top of a markdown file. Returns a
    dict, or None if no frontmatter block is found.

    Handles flat key:value, list-of-dicts (entries:/exits:), and quoted
    strings. Sufficient for Journalit's regular schema; not a general YAML
    parser."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    body = m.group(1)
    out = {}
    cur_list_key = None
    cur_list_item = None
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        # List-item start: "  - key: value"
        m_item = re.match(r"^(\s*)-\s+([A-Za-z_][\w]*)\s*:\s*(.*)$", line)
        if m_item:
            indent, k, v = m_item.group(1), m_item.group(2), m_item.group(3)
            if cur_list_key is None:
                continue
            cur_list_item = {k: _coerce_yaml_scalar(v)}
            out[cur_list_key].append(cur_list_item)
            continue
        # Continuation of current list item: "    key: value"
        m_cont = re.match(r"^(\s+)([A-Za-z_][\w]*)\s*:\s*(.*)$", line)
        if m_cont and cur_list_item is not None and len(m_cont.group(1)) > 2:
            k, v = m_cont.group(2), m_cont.group(3)
            cur_list_item[k] = _coerce_yaml_scalar(v)
            continue
        # Top-level key: "key: value" or "key:" (start of list)
        m_top = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", line)
        if m_top:
            k, v = m_top.group(1), m_top.group(2)
            if v == "":
                # Could be start of a list or empty value; assume list until proven otherwise
                out[k] = []
                cur_list_key = k
                cur_list_item = None
            else:
                out[k] = _coerce_yaml_scalar(v)
                cur_list_key = None
                cur_list_item = None
            continue
    return out


def _coerce_yaml_scalar(s):
    s = s.strip()
    if s == "":
        return ""
    # Inline empty containers (Journalit emits `images: []`, `tags: []`).
    if s == "[]":
        return []
    if s == "{}":
        return {}
    # Strip surrounding quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    # Bools
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    # Null
    if s.lower() in ("null", "~"):
        return None
    # Numbers
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        pass
    return s


def _resolve_trades_dir(vault_root, trades_dir=None):
    """Return the folder to scan for trade files, or None if none exists.

    If trades_dir is given, use it verbatim. Otherwise prefer the neutral
    `trades/` folder, falling back to `!Journalit/` for Journalit users."""
    if trades_dir:
        d = vault_root / trades_dir
        return d if d.exists() else None
    for candidate in ("trades", "!Journalit"):
        d = vault_root / candidate
        if d.exists():
            return d
    return None


def _scan_trades(vault_root, trades_dir=None):
    """Yield (path, frontmatter_dict) for every trade file in the trade-log
    folder. Skips files without parseable frontmatter or without type=trade."""
    root = _resolve_trades_dir(vault_root, trades_dir)
    if root is None:
        return
    for path in root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = _parse_frontmatter(text)
        if not fm or fm.get("type") != "trade":
            continue
        yield path, fm


def _aggregate_position(trades_for_ticker):
    """Given a list of trade frontmatter dicts (all same instrument),
    return an aggregate position dict, or None if shares_held is 0 / no
    OPEN trades."""
    total_entry_size = 0.0
    weighted_entry_cost = 0.0
    total_exit_size = 0.0
    realized_pnl = 0.0
    earliest_entry = None
    latest_exit = None
    open_files = []
    direction = None

    for fm in trades_for_ticker:
        if fm.get("tradeStatus") != "OPEN":
            continue
        entries = fm.get("entries") or []
        exits = fm.get("exits") or []
        if not entries:
            continue
        # Use entries to compute size + weighted cost.
        for e in entries:
            sz = _to_float(e.get("size"))
            pr = _to_float(e.get("price"))
            if sz is None or pr is None:
                continue
            total_entry_size += sz
            weighted_entry_cost += sz * pr
            t = _to_dt(e.get("time"))
            if t and (earliest_entry is None or t < earliest_entry):
                earliest_entry = t
        for x in exits:
            sz = _to_float(x.get("size"))
            pr = _to_float(x.get("price"))
            if sz is None or pr is None:
                continue
            total_exit_size += sz
            t = _to_dt(x.get("time"))
            if t and (latest_exit is None or t > latest_exit):
                latest_exit = t
        if direction is None:
            direction = fm.get("direction")
        open_files.append(fm.get("_path", ""))

    shares_held = total_entry_size - total_exit_size
    if shares_held <= 0 or total_entry_size <= 0:
        return None

    avg_cost = weighted_entry_cost / total_entry_size

    # Realized P&L on the exited portion uses the entry-weighted avg cost.
    # Per-exit price * size minus avg_cost * size.
    if total_exit_size > 0:
        # Recompute: realized = sum(exit.price * exit.size) - avg_cost * total_exit_size
        gross_exit = 0.0
        for fm in trades_for_ticker:
            if fm.get("tradeStatus") != "OPEN":
                continue
            for x in (fm.get("exits") or []):
                sz = _to_float(x.get("size"))
                pr = _to_float(x.get("price"))
                if sz is None or pr is None:
                    continue
                gross_exit += sz * pr
        realized_pnl = gross_exit - (avg_cost * total_exit_size)

    return {
        "shares_held": round(shares_held, 4),
        "avg_cost": round(avg_cost, 4),
        "total_entered": round(total_entry_size, 4),
        "total_exited": round(total_exit_size, 4),
        "realized_pnl": round(realized_pnl, 2),
        "first_entry_date": earliest_entry.date().isoformat() if earliest_entry else None,
        "last_exit_date": latest_exit.date().isoformat() if latest_exit else None,
        "direction": direction or "long",
        "open_trade_files": len(open_files),
    }


def _to_float(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def _to_dt(v):
    if not v:
        return None
    s = str(v)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default="vault", help="Vault root (default: vault)")
    parser.add_argument("--trades-dir", default=None,
                        help="Trade-log folder under the vault. Default: auto "
                             "(prefers trades/, falls back to !Journalit/).")
    parser.add_argument("--ticker", default=None, help="Filter to one ticker (case-insensitive)")
    parser.add_argument("--no-prices", action="store_true", help="Skip Stooq price fetches")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    vault_root = Path(args.vault)
    if not vault_root.exists():
        print(f"ERROR: vault root not found: {vault_root}", file=sys.stderr)
        sys.exit(1)

    by_ticker = {}
    for path, fm in _scan_trades(vault_root, args.trades_dir):
        instrument = (fm.get("instrument") or "").upper().strip()
        if not instrument:
            continue
        if args.ticker and instrument != args.ticker.upper():
            continue
        fm["_path"] = str(path)
        by_ticker.setdefault(instrument, []).append(fm)

    rows = []
    for ticker in sorted(by_ticker.keys()):
        agg = _aggregate_position(by_ticker[ticker])
        if not agg:
            continue
        row = {"ticker": ticker, **agg}
        if not args.no_prices:
            price, err = _fetch_price_stooq(ticker)
            if price is not None:
                row["current_price"] = round(price, 2)
                cost_basis = agg["avg_cost"] * agg["shares_held"]
                current_value = price * agg["shares_held"]
                row["unrealized_pnl"] = round(current_value - cost_basis, 2)
                row["unrealized_pct"] = round(((price / agg["avg_cost"]) - 1) * 100, 2)
                row["total_pnl"] = round(agg["realized_pnl"] + (current_value - cost_basis), 2)
                row["price_source"] = "stooq"
            else:
                row["current_price"] = None
                row["price_error"] = err.get("kind") if err else "unknown"
        rows.append(row)

    if args.format == "json":
        print(json.dumps({"as_of": datetime.now().isoformat(timespec="seconds"), "positions": rows}, indent=2))
    else:
        if not rows:
            print("No open positions found.")
            return
        print(f"# Open positions (as of {datetime.now().date().isoformat()})\n")
        if "current_price" in rows[0]:
            print("| Ticker | Shares | Avg cost | Current | Unrealized | Realized | First entry |")
            print("|---|---|---|---|---|---|---|")
            for r in rows:
                cur = f"${r['current_price']:.2f}" if r.get("current_price") is not None else "—"
                un = f"{r['unrealized_pct']:+.1f}% (${r['unrealized_pnl']:+.0f})" if r.get("unrealized_pnl") is not None else "—"
                rl = f"${r['realized_pnl']:+.0f}" if r["realized_pnl"] else "—"
                print(f"| {r['ticker']} | {r['shares_held']:.0f} | ${r['avg_cost']:.2f} | {cur} | {un} | {rl} | {r['first_entry_date'] or '—'} |")
        else:
            print("| Ticker | Shares | Avg cost | Realized | First entry |")
            print("|---|---|---|---|---|")
            for r in rows:
                rl = f"${r['realized_pnl']:+.0f}" if r["realized_pnl"] else "—"
                print(f"| {r['ticker']} | {r['shares_held']:.0f} | ${r['avg_cost']:.2f} | {rl} | {r['first_entry_date'] or '—'} |")


if __name__ == "__main__":
    main()
