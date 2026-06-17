#!/usr/bin/env python3
"""
Forward-mark deep-dive verdicts with their realized outcome.

The verdict ledger (`vault/deep-dives/_verdicts.md`, maintained by
`log_verdict.py`) records each deep-dive's call and the price at verdict time,
but never looks back to see how the call did. This script closes that loop: for
every verdict old enough to have a +21d / +60d outcome, it fetches the Stooq
close near that date and stores the raw forward return. The deep-dive skill then
renders a small calibration block (`--render`) at the moment it forms a NEW
verdict — the same diachronic, "fate of your own past output at the site of
judgment" pattern as the daily Verdict Drift section.

Scoring is direction-aware at RENDER time, not storage time: the JSON stores the
neutral long return; `favorable()` applies the verdict's direction (ADD/BUY want
up, REDUCE/TRIM/EXIT/SELL want down; HOLD/WATCH make no directional bet and are
not graded). This keeps the stored data interpretation-free.

Honest-uncertainty note baked into the render: until ~20 graded verdicts have
resolved, this is DESCRIPTIVE, not calibrated — a readout, never a correction
loop. The block says so.

State: vault/deep-dives/_verdict_scores.json (atomic writes). Idempotent — only
fills marks that have come due and aren't already set. Raw history grows with the
ledger (small; quarterly-review reads it); only the render is capped.

Modelled on the bounded-artifact discipline of story_ledger.py / log_verdict.py.

CLI:
  python .claude/scripts/score_verdicts.py                 # fill due marks
  python .claude/scripts/score_verdicts.py --render        # markdown block for the deep-dive
  python .claude/scripts/score_verdicts.py --rebuild       # recompute every mark from scratch
  python .claude/scripts/score_verdicts.py --today 2026-07-01   # override today (testing)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Sibling imports — reuse the ledger parser and PT-aware today from the drift checker.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_verdict_drift import _parse_ledger, _today_pt  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
DEFAULT_VAULT = REPO / "vault"

HORIZONS = [("ret_21d", 21), ("ret_60d", 60)]   # field name -> calendar-day offset
GRADED_UP = {"ADD", "BUY"}
GRADED_DOWN = {"REDUCE", "TRIM", "EXIT", "SELL"}
RENDER_CAP = 10                 # most recent graded+resolved verdicts shown in the block
CALIBRATED_AFTER = 20           # graded-n below this -> labelled descriptive, not calibrated
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
TIMEOUT_SEC = 12


# ---------------------------------------------------------------- io helpers

def _scores_path(vault_root: Path) -> Path:
    return vault_root / "deep-dives" / "_verdict_scores.json"


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    data = json.loads(raw)   # corrupt JSON raises — better than silently wiping marks
    return data if isinstance(data, dict) else {}


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# ---------------------------------------------------------------- yahoo history

# Yahoo's chart API is key-less and returns a clean daily date->close series — the
# same source the deep-dive's yfinance scripts use. Stooq is NOT usable here: its
# quote endpoint gives only the latest close, and its history CSV endpoint is behind
# a JavaScript proof-of-work bot-wall (verified from the VPS, 2026-06-16). We prefer
# curl_cffi (browser impersonation — installed in the VPS venv) and fall back to a
# plain urllib request with a desktop UA for local one-off runs.

def _http_get_json(url: str) -> dict | None:
    try:
        from curl_cffi import requests as _cr  # type: ignore
        r = _cr.get(url, impersonate="chrome", timeout=TIMEOUT_SEC)
        return r.json() if r.status_code == 200 else None
    except ImportError:
        pass
    except Exception:  # noqa: BLE001 — any curl_cffi/network error -> fall through / give up
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            if resp.status != 200:
                return None
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None


def _unix(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def _fetch_history(ticker: str, d1: date, d2: date) -> dict[str, float] | None:
    """Daily closes for [d1, d2] as {YYYY-MM-DD: close}, or None on any failure
    (caller leaves the marks unscored and retries next run)."""
    url = (f"{YAHOO_CHART_URL}{ticker.upper()}"
           f"?period1={_unix(d1)}&period2={_unix(d2 + timedelta(days=2))}&interval=1d")
    payload = _http_get_json(url)
    try:
        res = payload["chart"]["result"][0]
        stamps = res["timestamp"]
        closes = res["indicators"]["quote"][0]["close"]
    except (TypeError, KeyError, IndexError):
        return None
    out: dict[str, float] = {}
    for ts, close in zip(stamps, closes):
        if close is None:
            continue
        out[datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()] = float(close)
    return out or None


def _close_on_or_before(history: dict[str, float], target: date) -> float | None:
    """Latest available close on/before target (handles weekends/holidays)."""
    best_d, best_close = None, None
    for d_iso, close in history.items():
        if d_iso <= target.isoformat() and (best_d is None or d_iso > best_d):
            best_d, best_close = d_iso, close
    return best_close


# ---------------------------------------------------------------- scoring

def _key(row: dict) -> str:
    return f"{row['date']}|{row['ticker']}|{row['file']}"


def score(vault_root: Path, today: date, rebuild: bool = False) -> dict:
    """Fill any due, unscored forward marks. Returns the scores dict."""
    rows = _parse_ledger(vault_root / "deep-dives" / "_verdicts.md")
    path = _scores_path(vault_root)
    scores = {} if rebuild else _load(path)

    # Group rows that still need at least one mark, by ticker, to batch fetches.
    need_by_ticker: dict[str, list] = {}
    for row in rows:
        key = _key(row)
        entry = scores.get(key, {})
        pending = [(field, date.fromisoformat(row["date"]) + timedelta(days=days))
                   for field, days in HORIZONS
                   if today >= date.fromisoformat(row["date"]) + timedelta(days=days)
                   and entry.get(field) is None]
        if pending:
            need_by_ticker.setdefault(row["ticker"], []).append((row, pending))

    changed = False
    for ticker, items in need_by_ticker.items():
        earliest = min(date.fromisoformat(r["date"]) for r, _ in items)
        history = _fetch_history(ticker, earliest - timedelta(days=5), today)
        if history is None:
            print(f"WARN: no Stooq history for {ticker}; leaving unscored, will retry",
                  file=sys.stderr)
            continue
        for row, pending in items:
            key = _key(row)
            entry = scores.setdefault(key, {
                "date": row["date"], "ticker": ticker,
                "verdict": row["verdict"], "price_at_verdict": row["price_at_verdict"],
            })
            p0 = row["price_at_verdict"]
            for field, target in pending:
                p_then = _close_on_or_before(history, target)
                if p_then is None or not p0:
                    continue
                entry[field] = round((p_then - p0) / p0, 4)   # raw long return
                changed = True

    if changed or rebuild:
        _save(path, scores)
    return scores


# ---------------------------------------------------------------- render

def favorable(verdict: str, ret: float) -> bool | None:
    """Did the return go the verdict's way? None for non-directional calls."""
    v = verdict.upper()
    if v in GRADED_UP:
        return ret > 0
    if v in GRADED_DOWN:
        return ret < 0
    return None


def _signed(verdict: str, ret: float) -> float:
    """Return expressed so positive = the call was right (for averaging)."""
    return -ret if verdict.upper() in GRADED_DOWN else ret


def render(vault_root: Path, today: date) -> str:
    scores = _load(_scores_path(vault_root))
    graded = [e for e in scores.values()
              if favorable(e.get("verdict", ""), 0.0) is not None
              and e.get("ret_21d") is not None]
    graded.sort(key=lambda e: e["date"], reverse=True)
    shown = graded[:RENDER_CAP]
    if not shown:
        return ("**Verdict calibration:** no graded verdicts have resolved to +21d yet "
                "(WATCH/HOLD calls aren't graded). Evidence, never a command.")

    def bucket(label: str, members: set[str]) -> str | None:
        es = [e for e in shown if e["verdict"].upper() in members]
        if not es:
            return None
        fav = sum(1 for e in es if favorable(e["verdict"], e["ret_21d"]))
        avg = sum(_signed(e["verdict"], e["ret_21d"]) for e in es) / len(es)
        return f"{label} {fav}/{len(es)} favorable @+21d (avg {avg * 100:+.1f}%)"

    parts = [b for b in (bucket("ADD", GRADED_UP), bucket("REDUCE", GRADED_DOWN)) if b]
    total_graded = len([e for e in scores.values()
                        if favorable(e.get("verdict", ""), 0.0) is not None
                        and e.get("ret_21d") is not None])
    tag = ("" if total_graded >= CALIBRATED_AFTER
           else f" _(descriptive only — {total_graded}/{CALIBRATED_AFTER} graded "
                f"verdicts resolved; not yet calibrated)_")
    return ("**Verdict calibration (resolved, graded; last "
            f"{len(shown)}):** {' · '.join(parts)}.{tag} Evidence, never a command.")


# ---------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--render", action="store_true", help="print the calibration block")
    ap.add_argument("--rebuild", action="store_true", help="recompute every mark from scratch")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--today", default=None, help="override today (YYYY-MM-DD) for testing")
    args = ap.parse_args()

    vault_root = Path(args.vault)
    today = date.fromisoformat(args.today) if args.today else _today_pt()

    if args.render:
        print(render(vault_root, today))
        return 0

    scores = score(vault_root, today, rebuild=args.rebuild)
    graded = sum(1 for e in scores.values()
                 if favorable(e.get("verdict", ""), 0.0) is not None
                 and e.get("ret_21d") is not None)
    print(f"scored: {len(scores)} verdicts tracked, {graded} graded+resolved @+21d")
    return 0


if __name__ == "__main__":
    sys.exit(main())
