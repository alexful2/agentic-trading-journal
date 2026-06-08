"""
Shared Stooq quote fetcher used by sibling scripts in .claude/scripts/.

Why Stooq: no API key, no rate limit, covers US tickers — works in remote
runners where Yahoo Finance is blocked and FMP's free plan rejects most
tickers with HTTP 402.

Note: news-analyst/scripts/check_price_triggers.py keeps its own richer
_fetch_price_stooq that returns intraday high/low (needed for the
missed-run / intraday-touch check). It's intentionally not consolidated
here — it's invoked as a subprocess and benefits from being standalone.
"""

import math
import urllib.error
import urllib.parse
import urllib.request


STOOQ_QUOTE_URL = "https://stooq.com/q/l/"
DEFAULT_TIMEOUT_SEC = 10


def fetch_close(ticker, timeout_sec=DEFAULT_TIMEOUT_SEC):
    """Fetch the latest close price from Stooq for a US ticker.

    Returns (price: float, error: None) on success or (None, error_dict)
    on failure, where error_dict has shape {"kind": str, "detail": str}.
    """
    params = {"s": f"{ticker.lower()}.us", "f": "sd2t2ohlcv", "h": "", "e": "csv"}
    url = f"{STOOQ_QUOTE_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8").strip()
            if resp.status != 200:
                return None, {"kind": "stooq_http_error", "detail": f"status={resp.status}"}
    except urllib.error.HTTPError as e:
        return None, {"kind": "stooq_http_error", "detail": f"status={e.code}"}
    except urllib.error.URLError as e:
        return None, {"kind": "stooq_network_error", "detail": str(e.reason)[:120]}
    except (TimeoutError, OSError) as e:
        return None, {"kind": "stooq_network_error", "detail": type(e).__name__}

    lines = body.splitlines()
    if len(lines) < 2:
        return None, {"kind": "stooq_parse_error", "detail": body[:80]}
    cols = lines[1].split(",")
    if len(cols) < 7 or cols[1].strip().upper() in {"N/D", ""} or cols[6].strip().upper() in {"N/D", ""}:
        return None, {"kind": "stooq_unknown_ticker", "detail": lines[1][:80]}
    try:
        price = float(cols[6])
    except ValueError:
        return None, {"kind": "stooq_parse_error", "detail": cols[6]}
    if math.isnan(price) or math.isinf(price):
        return None, {"kind": "stooq_parse_error", "detail": cols[6]}
    return price, None
