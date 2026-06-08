#!/usr/bin/env python3
"""
Check watchlist price triggers against current prices.

Parses the `## Price Triggers` table in vault/watchlist.md, fetches current
prices, and emits JSON with one entry per trigger.

Price sources (tried in order, first success wins):
  1. Stooq CSV quote (https://stooq.com/q/l/). No API key, no rate limit,
     covers all US tickers. This is the primary path — works everywhere,
     including the remote-trigger environment where Yahoo Finance is blocked
     and where FMP's free plan rejects most tickers with HTTP 402.
  2. FMP (/stable/quote) if FMP_API_KEY is set. Only useful for tickers
     included in whatever FMP plan the key has access to; mega-caps on
     the free plan, everything on paid plans. Tried after Stooq so we
     get real-time FMP data when available but don't depend on it.
  3. yfinance — last-resort local fallback. Blocked in remote routines.

Statuses (triggers):
  FIRED_BUY  — current price <= buy_below threshold
  FIRED_TRIM — current price >= trim_above threshold
  ARMED      — within 3% of a trigger (not fired)
  IDLE       — no trigger crossed
  STALE      — last_reviewed > 30 days ago (triggers do not fire when stale)
  ERROR      — price fetch failed

Statuses (tranches, if a `## Planned Tranches` table is present):
  FIRED_TRANCHE_BUY  — action=Buy, current price <= at_price, not expired
  FIRED_TRANCHE_TRIM — action=Trim, current price >= at_price, not expired
  ARMED              — within 3% of at_price (not fired)
  IDLE               — at_price not crossed
  EXPIRED            — expires date is in the past (suppressed from firing,
                       surfaced for housekeeping/cleanup)
  ERROR              — price fetch failed

Each output row carries a `type` field of "trigger" or "tranche" so the
downstream consumer (news-analyst) can render them appropriately.

Capital-collision detection (triggers only):
  Each trigger row may declare a `prefer-over` list naming other tickers
  that should be funded after this one when both fire the same day. After
  classification, any row with FIRED_BUY that appears in another FIRED_BUY
  row's prefer_over list gets `deferred_due_to: [preferred_ticker, …]`
  populated. This does NOT change `status` — the trigger still fires — but
  the annotation flows into the daily alert so the reader sees "DLR fired
  but VRT is preferred, defer DLR" without having to re-read the
  deep-dive.

  SCOPE: Collision detection is scoped to rows parsed by a single
  invocation of this script. The daily pipeline runs the script twice
  (once per source file), so cross-file Prefer-over entries — e.g. a
  watchlist row preferring over a broader-file ticker — are silently
  dropped. Keep Prefer-over rankings within the same source file. If
  cross-file ranking becomes necessary, extend --watchlist to nargs='+'
  and parse a merged row set before calling detect_capital_collisions.

Usage:
    python check_price_triggers.py [--watchlist PATH] [--label LABEL] [--output FILE]

Default watchlist path is vault/watchlist.md relative to the current working
directory (i.e. repo root). The same script is used for the broader-stock
file at vault/price-triggers.md by passing --watchlist vault/price-triggers.md
--label broader. The label is attached to every result row so downstream
consumers (e.g. news-analyst) can route watchlist vs. broader fires to
different report sections.
"""

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


STALE_DAYS = 30
ARMED_PCT = 3.0
FMP_QUOTE_URL = "https://financialmodelingprep.com/stable/quote"
STOOQ_QUOTE_URL = "https://stooq.com/q/l/"
HTTP_TIMEOUT_SEC = 10


def parse_triggers_table(md_text):
    """Find the ## Price Triggers section and parse rows into dicts.

    Supports both the legacy 5-column layout
    (Ticker | Buy Below | Trim Above | Last Reviewed | Note [| Source])
    and the current 7-column layout with Funded-by / Prefer-over inserted
    between Trim Above and Last Reviewed:
    (Ticker | Buy Below | Trim Above | Funded-by | Prefer-over | Last Reviewed | Note [| Source]).

    Column identification is header-driven so the same parser handles both
    vault/watchlist.md (no Source column) and vault/price-triggers.md (has
    Source column) regardless of Funded-by / Prefer-over presence.
    """
    match = re.search(
        r"^## Price Triggers\s*\n(.*?)(?=^## |\Z)",
        md_text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []

    header_map = None  # column name (lowercased) → index
    rows = []
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Separator row (| --- | --- | ...)
        if re.match(r"^\|\s*-+", line):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        # Header row — capture column positions, then skip.
        if parts[0].lower() == "ticker":
            header_map = {p.lower(): i for i, p in enumerate(parts)}
            continue
        if header_map is None:
            # No header seen yet; fall back to legacy positional parse.
            header_map = {
                "ticker": 0,
                "buy below": 1,
                "trim above": 2,
                "last reviewed": 3,
                "note": 4,
            }

        def col(name):
            idx = header_map.get(name)
            if idx is None or idx >= len(parts):
                return ""
            return parts[idx]

        ticker = col("ticker").upper()
        buy_below = _parse_price(col("buy below"))
        trim_above = _parse_price(col("trim above"))
        last_reviewed = _parse_date(col("last reviewed"))
        funded_by = _parse_optional_text(col("funded-by"))
        prefer_over = _parse_ticker_list(col("prefer-over"))
        note = col("note")

        if not ticker or (buy_below is None and trim_above is None):
            continue

        rows.append(
            {
                "ticker": ticker,
                "buy_below": buy_below,
                "trim_above": trim_above,
                "last_reviewed": last_reviewed.isoformat() if last_reviewed else None,
                "funded_by": funded_by,
                "prefer_over": prefer_over,
                "note": note,
            }
        )
    return rows


def parse_tranches_table(md_text):
    """Find the ## Planned Tranches section and parse rows into dicts.

    Expected columns: Ticker | Action | Size | At Price | Expires | Order | Note.
    The Order column was added 2026-04 — legacy rows without it parse with an
    empty `order` field. Action must be "Buy" or "Trim" (case-insensitive).
    Rows with missing ticker, unknown action, or unparseable at_price are skipped.
    """
    match = re.search(
        r"^## Planned Tranches\s*\n(.*?)(?=^## |\Z)",
        md_text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []

    rows = []
    header_map = None  # column name (lowercased) → index, header-driven path
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+", line):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        if parts[0].lower() == "ticker":
            header_map = {p.lower(): i for i, p in enumerate(parts)}
            continue

        if header_map:
            def col(name, default=""):
                idx = header_map.get(name)
                if idx is None or idx >= len(parts):
                    return default
                return parts[idx]
            ticker = col("ticker").upper()
            action_raw = col("action").strip().lower()
            size = col("size")
            at_price = _parse_price(col("at price"))
            expires = _parse_date(col("expires"))
            order = col("order")
            note = col("note")
        else:
            # No header seen yet; legacy positional parse.
            ticker = parts[0].upper()
            action_raw = parts[1].strip().lower()
            size = parts[2]
            at_price = _parse_price(parts[3])
            expires = _parse_date(parts[4])
            order = ""
            note = parts[5] if len(parts) > 5 else ""

        if action_raw not in ("buy", "trim"):
            continue
        action = "Buy" if action_raw == "buy" else "Trim"

        if not ticker or at_price is None:
            continue

        rows.append(
            {
                "ticker": ticker,
                "action": action,
                "size": size,
                "at_price": at_price,
                "expires": expires.isoformat() if expires else None,
                "order": order,
                "note": note,
            }
        )
    return rows


def _parse_price(s):
    s = s.replace("$", "").replace(",", "").strip()
    if s in ("", "—", "-", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_date(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_optional_text(s):
    """Return None for empty / em-dash / hyphen cells; otherwise the stripped
    text. Used for soft-optional free-text columns like Funded-by."""
    s = (s or "").strip()
    if s in ("", "—", "-", "N/A"):
        return None
    return s


def _parse_ticker_list(s):
    """Parse a comma-separated ticker list into a list of uppercased tickers.
    Returns [] for empty / em-dash cells."""
    s = (s or "").strip()
    if s in ("", "—", "-", "N/A"):
        return []
    return [t.strip().upper() for t in s.split(",") if t.strip()]


def _coerce_price(value):
    if value is None:
        return None
    try:
        price = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(price) or math.isinf(price):
        return None
    return price


def _fetch_price_stooq(ticker):
    """Fetch current price + intraday high/low from Stooq's CSV quote endpoint.
    Returns (quote, error_dict) where quote is a dict with keys 'close', 'high',
    'low' (high/low may be None if Stooq omits them, e.g. on illiquid names).
    No API key, no rate limit, covers US tickers (append `.US` to the symbol).

    The high/low are needed for the missed-run check: when the cron fires
    sparsely (GH Actions free tier doesn't guarantee every */15 slot), the
    current price at tick time may have already rebounded past a trigger that
    DID get touched intraday. Using the day's range catches those misses."""
    params = {"s": f"{ticker.lower()}.us", "f": "sd2t2ohlcv", "h": "", "e": "csv"}
    url = f"{STOOQ_QUOTE_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SEC) as resp:
            body = resp.read().decode("utf-8").strip()
            if resp.status != 200:
                return None, {"kind": "stooq_http_error", "detail": f"status={resp.status}"}
    except urllib.error.HTTPError as e:
        return None, {"kind": "stooq_http_error", "detail": f"status={e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return None, {"kind": "stooq_network_error", "detail": f"{type(e.reason).__name__}: {e.reason}"}
    except (TimeoutError, OSError) as e:
        return None, {"kind": "stooq_network_error", "detail": f"{type(e).__name__}: {e}"}

    lines = body.splitlines()
    if len(lines) < 2:
        return None, {"kind": "stooq_parse_error", "detail": f"fewer than 2 CSV lines: {body[:120]!r}"}
    # Data row: Symbol,Date,Time,Open,High,Low,Close,Volume
    cols = lines[1].split(",")
    if len(cols) < 7:
        return None, {"kind": "stooq_parse_error", "detail": f"row has {len(cols)} columns: {lines[1][:120]!r}"}
    # Stooq returns 'N/D' for unknown tickers / no data.
    if cols[1].strip().upper() in {"N/D", ""} or cols[6].strip().upper() in {"N/D", ""}:
        return None, {"kind": "stooq_unknown_ticker", "detail": f"no data row: {lines[1][:120]!r}"}
    close = _coerce_price(cols[6])
    if close is None:
        return None, {"kind": "stooq_parse_error", "detail": f"close not parseable: {cols[6]!r}"}
    high = _coerce_price(cols[4])
    low = _coerce_price(cols[5])
    return {"close": close, "high": high, "low": low}, None


def _fetch_price_fmp(ticker, api_key):
    """Fetch current price from FMP /stable/quote. Returns (quote, error_dict)
    where quote is a dict with 'close' / 'high' / 'low' (high/low may be None
    if FMP doesn't include the day-range fields for that plan/ticker)."""
    params = {"symbol": ticker, "apikey": api_key}
    url = f"{FMP_QUOTE_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SEC) as resp:
            body = resp.read().decode("utf-8")
            if resp.status != 200:
                return None, {"kind": "fmp_http_error", "detail": f"status={resp.status}"}
            data = json.loads(body)
    except urllib.error.HTTPError as e:
        msg = ""
        try:
            msg = e.read().decode("utf-8")[:200]
        except Exception:
            pass
        return None, {"kind": "fmp_http_error", "detail": f"status={e.code}: {e.reason}; body={msg}"}
    except urllib.error.URLError as e:
        return None, {"kind": "fmp_network_error", "detail": f"{type(e.reason).__name__}: {e.reason}"}
    except (TimeoutError, OSError) as e:
        return None, {"kind": "fmp_network_error", "detail": f"{type(e).__name__}: {e}"}
    except ValueError as e:
        return None, {"kind": "fmp_parse_error", "detail": f"json decode: {e}"}

    if isinstance(data, dict) and data.get("Error Message"):
        return None, {"kind": "fmp_api_error", "detail": str(data.get("Error Message"))[:200]}
    if not isinstance(data, list) or not data:
        return None, {"kind": "fmp_parse_error", "detail": f"unexpected payload shape: {type(data).__name__}"}
    row = data[0]
    if not isinstance(row, dict):
        return None, {"kind": "fmp_parse_error", "detail": "first result is not an object"}
    price = _coerce_price(row.get("price")) or _coerce_price(row.get("previousClose"))
    if price is None:
        return None, {"kind": "fmp_parse_error", "detail": f"no price or previousClose in row; keys={sorted(row.keys())[:8]}"}
    high = _coerce_price(row.get("dayHigh"))
    low = _coerce_price(row.get("dayLow"))
    return {"close": price, "high": high, "low": low}, None


def _fetch_price_yfinance(ticker):
    """Fallback using yfinance. Returns (quote, error_dict) where quote is a
    dict with 'close'/'high'/'low' (high/low best-effort)."""
    try:
        import yfinance as yf
    except ImportError as e:
        return None, {"kind": "yfinance_missing", "detail": str(e)}
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        price = _coerce_price(fi.last_price if fi else None)
        if price is None:
            return None, {"kind": "yfinance_no_price", "detail": "fast_info returned no last_price (host likely blocked)"}
        high = _coerce_price(getattr(fi, "day_high", None)) if fi else None
        low = _coerce_price(getattr(fi, "day_low", None)) if fi else None
        return {"close": price, "high": high, "low": low}, None
    except Exception as e:
        return None, {"kind": "yfinance_runtime_error", "detail": f"{type(e).__name__}: {e}"}


def fetch_price(ticker, api_key):
    """Return (quote, source, error_dict).

    quote is a dict {'close', 'high', 'low'} (high/low may be None depending
    on the source) on success, or None on failure. Tries Stooq first
    (universal coverage, no key), then FMP if the key is set and the plan
    covers the ticker, then yfinance as a last-resort local fallback.
    source is the name of the path that succeeded, or "" on total failure.
    """
    errors: dict = {}

    quote, err = _fetch_price_stooq(ticker)
    if quote is not None:
        return quote, "stooq", None
    errors["stooq"] = err

    if api_key:
        quote, err = _fetch_price_fmp(ticker, api_key)
        if quote is not None:
            return quote, "fmp", None
        errors["fmp"] = err
    else:
        errors["fmp"] = {"kind": "no_api_key", "detail": "FMP_API_KEY not set"}

    quote, err = _fetch_price_yfinance(ticker)
    if quote is not None:
        return quote, "yfinance", None
    errors["yfinance"] = err

    return None, "", errors


def classify(trigger, price_info, today, label):
    quote, source, err = price_info
    price = quote["close"] if quote else None
    day_high = quote.get("high") if quote else None
    day_low = quote.get("low") if quote else None
    result = {
        "ticker": trigger["ticker"],
        "type": "trigger",
        "label": label,
        "current_price": round(price, 2) if price is not None else None,
        "day_high": round(day_high, 2) if day_high is not None else None,
        "day_low": round(day_low, 2) if day_low is not None else None,
        "price_source": source,
        "buy_below": trigger["buy_below"],
        "trim_above": trigger["trim_above"],
        "last_reviewed": trigger["last_reviewed"],
        "days_since_review": None,
        "funded_by": trigger.get("funded_by"),
        "prefer_over": trigger.get("prefer_over", []),
        "deferred_due_to": [],  # filled in later by detect_capital_collisions
        "note": trigger["note"],
        "status": None,
        "triggered_by": None,  # "current" or "intraday" on FIRED_BUY/FIRED_TRIM
        "message": None,
        "error": err,
    }

    if price is None:
        result["status"] = "ERROR"
        # Surface the most informative error path to the top.
        err = err or {}
        fmp_err = err.get("fmp") or {}
        yf_err = err.get("yfinance") or {}
        kind = fmp_err.get("kind") or yf_err.get("kind") or "unknown"
        detail = fmp_err.get("detail") or yf_err.get("detail") or ""
        result["message"] = f"Price fetch failed ({kind}): {detail}" if detail else f"Price fetch failed ({kind})"
        return result

    if trigger["last_reviewed"]:
        reviewed = datetime.fromisoformat(trigger["last_reviewed"]).date()
        age = (today - reviewed).days
        result["days_since_review"] = age
        if age > STALE_DAYS:
            result["status"] = "STALE"
            result["message"] = (
                f"Last reviewed {age} days ago — trigger suppressed until re-confirmed"
            )
            return result

    # Buy fires on current price OR an intraday touch the cron may have missed.
    # Current takes priority so a still-below-trigger row reads naturally.
    buy_below = trigger["buy_below"]
    if buy_below is not None:
        if price <= buy_below:
            result["status"] = "FIRED_BUY"
            result["triggered_by"] = "current"
            result["message"] = f"Price ${price:.2f} <= buy trigger ${buy_below:.2f}"
            return result
        if day_low is not None and day_low <= buy_below:
            result["status"] = "FIRED_BUY"
            result["triggered_by"] = "intraday"
            result["message"] = (
                f"Day low ${day_low:.2f} <= buy trigger ${buy_below:.2f} "
                f"(price now ${price:.2f}, rebounded)"
            )
            return result

    trim_above = trigger["trim_above"]
    if trim_above is not None:
        if price >= trim_above:
            result["status"] = "FIRED_TRIM"
            result["triggered_by"] = "current"
            result["message"] = f"Price ${price:.2f} >= trim trigger ${trim_above:.2f}"
            return result
        if day_high is not None and day_high >= trim_above:
            result["status"] = "FIRED_TRIM"
            result["triggered_by"] = "intraday"
            result["message"] = (
                f"Day high ${day_high:.2f} >= trim trigger ${trim_above:.2f} "
                f"(price now ${price:.2f}, pulled back)"
            )
            return result

    armed = []
    if buy_below is not None:
        pct_above = ((price - buy_below) / buy_below) * 100
        if 0 < pct_above <= ARMED_PCT:
            armed.append(f"{pct_above:.1f}% above buy trigger")
    if trim_above is not None:
        pct_below = ((trim_above - price) / trim_above) * 100
        if 0 < pct_below <= ARMED_PCT:
            armed.append(f"{pct_below:.1f}% below trim trigger")
    if armed:
        result["status"] = "ARMED"
        result["message"] = "; ".join(armed)
        return result

    result["status"] = "IDLE"
    return result


def classify_tranche(tranche, price_info, today, label):
    quote, source, err = price_info
    price = quote["close"] if quote else None
    day_high = quote.get("high") if quote else None
    day_low = quote.get("low") if quote else None
    result = {
        "ticker": tranche["ticker"],
        "type": "tranche",
        "label": label,
        "current_price": round(price, 2) if price is not None else None,
        "day_high": round(day_high, 2) if day_high is not None else None,
        "day_low": round(day_low, 2) if day_low is not None else None,
        "price_source": source,
        "action": tranche["action"],
        "size": tranche["size"],
        "at_price": tranche["at_price"],
        "expires": tranche["expires"],
        "order": tranche.get("order", ""),
        "note": tranche["note"],
        "status": None,
        "triggered_by": None,
        "message": None,
        "error": err,
    }

    if tranche["expires"]:
        expires_date = datetime.fromisoformat(tranche["expires"]).date()
        if expires_date < today:
            result["status"] = "EXPIRED"
            result["message"] = (
                f"Expired {(today - expires_date).days} days ago — cleanup candidate"
            )
            return result

    if price is None:
        result["status"] = "ERROR"
        err = err or {}
        fmp_err = err.get("fmp") or {}
        yf_err = err.get("yfinance") or {}
        kind = fmp_err.get("kind") or yf_err.get("kind") or "unknown"
        detail = fmp_err.get("detail") or yf_err.get("detail") or ""
        result["message"] = f"Price fetch failed ({kind}): {detail}" if detail else f"Price fetch failed ({kind})"
        return result

    at_price = tranche["at_price"]
    action = tranche["action"]

    if action == "Buy":
        if price <= at_price:
            result["status"] = "FIRED_TRANCHE_BUY"
            result["triggered_by"] = "current"
            result["message"] = (
                f"Price ${price:.2f} <= tranche buy @ ${at_price:.2f} ({tranche['size']})"
            )
            return result
        if day_low is not None and day_low <= at_price:
            result["status"] = "FIRED_TRANCHE_BUY"
            result["triggered_by"] = "intraday"
            result["message"] = (
                f"Day low ${day_low:.2f} <= tranche buy @ ${at_price:.2f} ({tranche['size']}) "
                f"— price now ${price:.2f}, rebounded"
            )
            return result
    else:  # Trim
        if price >= at_price:
            result["status"] = "FIRED_TRANCHE_TRIM"
            result["triggered_by"] = "current"
            result["message"] = (
                f"Price ${price:.2f} >= tranche trim @ ${at_price:.2f} ({tranche['size']})"
            )
            return result
        if day_high is not None and day_high >= at_price:
            result["status"] = "FIRED_TRANCHE_TRIM"
            result["triggered_by"] = "intraday"
            result["message"] = (
                f"Day high ${day_high:.2f} >= tranche trim @ ${at_price:.2f} ({tranche['size']}) "
                f"— price now ${price:.2f}, pulled back"
            )
            return result

    if action == "Buy":
        pct_above = ((price - at_price) / at_price) * 100
        if 0 < pct_above <= ARMED_PCT:
            result["status"] = "ARMED"
            result["message"] = f"{pct_above:.1f}% above tranche buy level"
            return result
    else:
        pct_below = ((at_price - price) / at_price) * 100
        if 0 < pct_below <= ARMED_PCT:
            result["status"] = "ARMED"
            result["message"] = f"{pct_below:.1f}% below tranche trim level"
            return result

    result["status"] = "IDLE"
    return result


def detect_capital_collisions(trigger_results):
    """Mutate trigger rows in-place: for each FIRED_BUY row, if its ticker
    appears in another FIRED_BUY row's prefer_over list, annotate the deferred
    row with `deferred_due_to` = [list of preferred tickers]. Scope is limited
    to the rows passed in — see module docstring: the daily pipeline invokes
    this script once per source file, so cross-file Prefer-over relationships
    are not detected. Keep Prefer-over lists within the same file."""
    fired_buys = [r for r in trigger_results if r.get("status") == "FIRED_BUY"]
    fired_by_ticker = {r["ticker"]: r for r in fired_buys}
    for preferred in fired_buys:
        for deferred_ticker in preferred.get("prefer_over") or []:
            deferred = fired_by_ticker.get(deferred_ticker)
            if deferred is None:
                continue
            if preferred["ticker"] not in deferred["deferred_due_to"]:
                deferred["deferred_due_to"].append(preferred["ticker"])


def _summarize_errors(results, api_key_present):
    """Distill per-row errors into a single human-readable diagnostic for the
    top-level summary. Returns None when there are no errors."""
    error_rows = [r for r in results if r["status"] == "ERROR"]
    if not error_rows:
        return None

    # Count by kind — prefer the most common failure mode as the headline.
    # We care about the Stooq path first (it's primary). Summarise by the
    # Stooq-side error kind; if Stooq succeeded but some other path was
    # asked for explicitly, we'd still have an error_rows list empty, so
    # we never get here.
    kind_counts: dict = {}
    sample_detail = ""
    for r in error_rows:
        err = r.get("error") or {}
        stooq_err = err.get("stooq") or {}
        kind = stooq_err.get("kind") or "unknown"
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        if not sample_detail and stooq_err.get("detail"):
            sample_detail = stooq_err["detail"]

    top_kind = max(kind_counts.items(), key=lambda kv: kv[1])[0]
    n_err = len(error_rows)

    if top_kind == "stooq_network_error":
        return (
            f"{n_err}/{len(results)} rows errored: couldn't reach stooq.com "
            f"(sample: {sample_detail!r}). Host may be blocked in this environment — "
            "if this happens in a routine, allowlist stooq.com or add an alternative source."
        )
    if top_kind == "stooq_http_error":
        return (
            f"{n_err}/{len(results)} rows errored: Stooq returned an HTTP error "
            f"(sample: {sample_detail!r})."
        )
    if top_kind == "stooq_unknown_ticker":
        return (
            f"{n_err}/{len(results)} rows errored: Stooq has no data for the ticker(s) "
            f"(sample: {sample_detail!r}). Check the ticker symbol and append conventions."
        )
    if top_kind == "stooq_parse_error":
        return (
            f"{n_err}/{len(results)} rows errored: Stooq response didn't parse "
            f"(sample: {sample_detail!r}). API shape may have changed."
        )
    return f"{n_err}/{len(results)} rows errored with kind={top_kind!r} (sample: {sample_detail!r})"


def _healthcheck():
    """Quick end-to-end probe. Fetches NVDA once and reports which path worked.
    Exits 0 on success, 1 on failure. Writes one line to stdout for logs."""
    api_key = os.environ.get("FMP_API_KEY")
    quote, source, err = fetch_price("NVDA", api_key)
    if quote is not None:
        price = quote["close"]
        high = quote.get("high")
        low = quote.get("low")
        range_str = f" range=${low:.2f}-${high:.2f}" if (high is not None and low is not None) else ""
        print(f"OK price_source={source} NVDA=${price:.2f}{range_str} api_key_present={bool(api_key)}")
        return 0
    err = err or {}
    fmp_err = err.get("fmp") or {}
    yf_err = err.get("yfinance") or {}
    print(
        f"FAIL api_key_present={bool(api_key)} "
        f"fmp_kind={fmp_err.get('kind')!r} fmp_detail={fmp_err.get('detail')!r} "
        f"yf_kind={yf_err.get('kind')!r} yf_detail={yf_err.get('detail')!r}"
    )
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--watchlist",
        default="vault/watchlist.md",
        help="Path to markdown file containing a `## Price Triggers` table "
        "(default: vault/watchlist.md)",
    )
    parser.add_argument(
        "--label",
        default="watchlist",
        help="Label attached to each result row so downstream consumers can "
        "distinguish sources (e.g. 'watchlist' vs. 'broader'). "
        "Default: watchlist",
    )
    parser.add_argument(
        "--output", help="Write JSON to this file instead of stdout"
    )
    parser.add_argument(
        "--healthcheck",
        action="store_true",
        help="Probe price fetch with a known-good ticker and exit 0/1. Use at "
        "the start of a routine run to surface env/network issues early.",
    )
    args = parser.parse_args()

    if args.healthcheck:
        sys.exit(_healthcheck())

    path = Path(args.watchlist)
    if not path.exists():
        print(f"ERROR: watchlist not found: {path}", file=sys.stderr)
        sys.exit(1)

    md_text = path.read_text(encoding="utf-8")
    triggers = parse_triggers_table(md_text)
    tranches = parse_tranches_table(md_text)
    today = datetime.now().date()

    api_key = os.environ.get("FMP_API_KEY")

    # Fetch each unique ticker once — tranches can repeat tickers that also
    # appear in the triggers table.
    price_cache = {}

    def _price(ticker):
        if ticker not in price_cache:
            price_cache[ticker] = fetch_price(ticker, api_key)
        return price_cache[ticker]

    trigger_results = [classify(t, _price(t["ticker"]), today, args.label) for t in triggers]
    detect_capital_collisions(trigger_results)
    tranche_results = [classify_tranche(t, _price(t["ticker"]), today, args.label) for t in tranches]
    results = trigger_results + tranche_results

    fired_statuses = ("FIRED_BUY", "FIRED_TRIM", "FIRED_TRANCHE_BUY", "FIRED_TRANCHE_TRIM")

    # Top-level diagnostic — distilled from per-row errors so the report
    # housekeeping line can cite the real cause instead of guessing.
    diagnostic = _summarize_errors(results, api_key_present=bool(api_key))

    # Sources actually used this run (set of strings).
    sources_used = sorted({r.get("price_source") for r in results if r.get("price_source")})

    summary = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "watchlist_path": str(path),
        "label": args.label,
        "api_key_present": bool(api_key),
        "price_sources_used": sources_used,
        "diagnostic": diagnostic,
        "total": len(results),
        "fired": sum(1 for r in results if r["status"] in fired_statuses),
        "fired_tranches": sum(1 for r in tranche_results if r["status"] in fired_statuses),
        "armed": sum(1 for r in results if r["status"] == "ARMED"),
        "stale": sum(1 for r in trigger_results if r["status"] == "STALE"),
        "expired_tranches": sum(1 for r in tranche_results if r["status"] == "EXPIRED"),
        "errors": sum(1 for r in results if r["status"] == "ERROR"),
        "results": results,
    }

    output = json.dumps(summary, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
