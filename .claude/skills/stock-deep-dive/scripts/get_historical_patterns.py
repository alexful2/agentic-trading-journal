#!/usr/bin/env python3
"""
Analyze historical entry patterns for a stock via yfinance (Yahoo Finance).
No API key required.

Install dependency: pip install yfinance

Runs three entry-condition presets against historical price data and measures
forward returns at +21/+42/+63 trading day horizons.

Usage:
    python get_historical_patterns.py --ticker NVDA
    python get_historical_patterns.py --ticker NVDA --years 4

"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print(
        "ERROR: yfinance is not installed.\n"
        "Run: pip install yfinance",
        file=sys.stderr,
    )
    sys.exit(1)


COOLDOWN_DAYS = 20   # min trading days between counted instances of same preset
MIN_SAMPLES = 4      # minimum instances required before reporting stats


# ---------------------------------------------------------------------------
# Data fetchers
# ---------------------------------------------------------------------------

def fetch_price_history(ticker, years=5):
    """
    Fetch daily OHLCV history via yfinance.
    Returns list of dicts sorted ascending by date:
      [{"date": "YYYY-MM-DD", "open": x, "high": x, "low": x, "close": x}, ...]
    """
    t = yf.Ticker(ticker.upper())
    hist = t.history(period=f"{years}y")

    if hist is None or hist.empty:
        return []

    result = []
    for date_idx, row in hist.iterrows():
        close = row["Close"]
        if close is None or close != close:  # NaN check
            continue
        date_str = str(date_idx.date()) if hasattr(date_idx, "date") else str(date_idx)[:10]
        result.append({
            "date": date_str,
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(close),
            "volume": int(row["Volume"]) if row["Volume"] == row["Volume"] else 0,
        })

    result.sort(key=lambda x: x["date"])
    return result


def fetch_earnings_dates(ticker):
    """
    Fetch historical earnings release dates via yfinance.
    Returns sorted list of date strings ["YYYY-MM-DD", ...] for past dates only.
    """
    t = yf.Ticker(ticker.upper())
    try:
        ed = t.earnings_dates
        if ed is None or ed.empty:
            return []
        now = datetime.now(timezone.utc)
        past = ed[ed.index < now]
        dates = sorted({
            str(d.date()) if hasattr(d, "date") else str(d)[:10]
            for d in past.index
        })
        return dates
    except Exception as e:
        print(f"  WARNING [earnings-dates]: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def rolling_max(prices, window):
    """Rolling maximum close over the last `window` trading days (inclusive)."""
    closes = [p["close"] for p in prices]
    result = []
    for i in range(len(closes)):
        start = max(0, i - window + 1)
        result.append(max(closes[start : i + 1]))
    return result


def with_cooldown(indices):
    """
    De-overlap a sorted list of condition-matching indices so that consecutive
    picks are at least COOLDOWN_DAYS apart.
    """
    picked = []
    last = -(COOLDOWN_DAYS + 1)
    for i in indices:
        if i - last >= COOLDOWN_DAYS:
            picked.append(i)
            last = i
    return picked


def forward_returns(prices, entry_idx, horizons):
    """
    Measure percent returns from the close at entry_idx at each trading-day horizon.
    Also returns the max intra-period drawdown.

    Returns:
        rets    — dict {horizon: pct_return}
        max_dd  — float, worst drawdown from entry through the longest horizon
    """
    entry_price = prices[entry_idx]["close"]
    n = len(prices)
    max_h = max(horizons)
    end = min(entry_idx + max_h + 1, n)

    rets = {}
    min_price = entry_price
    for offset in range(1, end - entry_idx):
        fp = prices[entry_idx + offset]["close"]
        if fp < min_price:
            min_price = fp
        if offset in horizons:
            rets[offset] = ((fp - entry_price) / entry_price) * 100.0

    max_dd = ((min_price - entry_price) / entry_price) * 100.0
    return rets, max_dd


def stats_block(returns_list):
    """Compute summary stats from a list of floats."""
    if not returns_list:
        return None
    n = len(returns_list)
    return {
        "win_rate": round(sum(1 for r in returns_list if r > 0) / n * 100, 1),
        "avg_return": round(sum(returns_list) / n, 1),
        "best": round(max(returns_list), 1),
        "worst": round(min(returns_list), 1),
        "n": n,
    }


# ---------------------------------------------------------------------------
# Level Context: ATR, moving averages, recent swing lows
# ---------------------------------------------------------------------------

def compute_level_context(prices):
    """
    Reference numbers for the Step 4 price ladder cross-check.

    Emits:
      - atr_20d: Average True Range over the last 20 trading days. Used to
        express ladder levels in vol-adjusted units ("Buy Below is -1.3 ATR").
      - sma_50d / sma_200d: Simple moving averages. Other participants watch
        these, so a ladder level sitting right at one of them is notable.
      - recent_swing_lows: Local minima in the last ~6 months where close was
        strictly lower than neighbors within a 5-day window. Up to 3 most
        recent, reverse-chronological. Natural support shelves.

    Returns None if there isn't enough history.
    """
    if len(prices) < 21:
        return None

    # ATR(20) — Wilder's true range averaged over the last 20 days.
    trs = []
    start = len(prices) - 20
    for i in range(start, len(prices)):
        h, l = prices[i]["high"], prices[i]["low"]
        if i == 0:
            tr = h - l
        else:
            prev_c = prices[i - 1]["close"]
            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        trs.append(tr)
    atr_20 = sum(trs) / len(trs) if trs else None

    sma_50 = (
        sum(p["close"] for p in prices[-50:]) / 50 if len(prices) >= 50 else None
    )
    sma_200 = (
        sum(p["close"] for p in prices[-200:]) / 200 if len(prices) >= 200 else None
    )

    # Swing lows: strict local minima in a ±5-day window, within last ~126 TD.
    N = 5
    lookback = min(126, len(prices) - N - 1)
    swing_lows = []
    search_start = max(N, len(prices) - lookback)
    for i in range(search_start, len(prices) - N):
        center = prices[i]["close"]
        left_min = min(p["close"] for p in prices[i - N:i])
        right_min = min(p["close"] for p in prices[i + 1:i + 1 + N])
        if center < left_min and center < right_min:
            swing_lows.append({"date": prices[i]["date"], "price": round(center, 2)})
    swing_lows.sort(key=lambda x: x["date"], reverse=True)
    swing_lows = swing_lows[:3]

    current_price = prices[-1]["close"]
    return {
        "current_price": round(current_price, 2),
        "atr_20d": round(atr_20, 2) if atr_20 is not None else None,
        "atr_20d_pct_of_price": (
            round(atr_20 / current_price * 100, 2)
            if atr_20 and current_price else None
        ),
        "sma_50d": round(sma_50, 2) if sma_50 is not None else None,
        "sma_200d": round(sma_200, 2) if sma_200 is not None else None,
        "recent_swing_lows": swing_lows,
    }


# ---------------------------------------------------------------------------
# Preset 1: Dip Buyer
# ---------------------------------------------------------------------------

def preset_dip_buyer(prices, roll_max):
    """
    Condition: price is 15–30% below its rolling 52-week high.
    Entry on first day in the zone; cooldown after.
    """
    HORIZONS = (21, 42, 63)
    LOOKBACK = 252

    eligible = [
        i for i in range(LOOKBACK, len(prices))
        if roll_max[i] > 0 and
        15.0 <= ((roll_max[i] - prices[i]["close"]) / roll_max[i]) * 100 <= 30.0
    ]
    instances = with_cooldown(eligible)
    valid = [i for i in instances if i + max(HORIZONS) < len(prices)]

    result = {
        "label": "Preset 1 — Dip Buyer",
        "condition": "Price 15–30% below rolling 52-week high",
        "total_instances": len(instances),
        "valid_instances": len(valid),
    }

    if len(valid) < MIN_SAMPLES:
        result["note"] = (
            f"Only {len(valid)} instances with full forward data — "
            "insufficient for reliable statistics."
        )
        return result

    by_horizon = defaultdict(list)
    drawdowns = []
    for idx in valid:
        rets, dd = forward_returns(prices, idx, HORIZONS)
        for h, r in rets.items():
            by_horizon[h].append(r)
        drawdowns.append(dd)

    result["stats"] = {f"+{h}d": stats_block(by_horizon[h]) for h in HORIZONS}
    result["avg_max_drawdown"] = round(sum(drawdowns) / len(drawdowns), 1)
    result["worst_max_drawdown"] = round(min(drawdowns), 1)
    return result


# ---------------------------------------------------------------------------
# Preset 2: Extended Run (Don't Chase)
# ---------------------------------------------------------------------------

def preset_extended_run(prices):
    """
    Condition: price is >20% above where it was 20 trading days ago.
    Entry on first eligible day; cooldown after.
    """
    HORIZONS = (21, 42, 63)
    LOOKBACK = 20

    eligible = [
        i for i in range(LOOKBACK, len(prices))
        if prices[i - LOOKBACK]["close"] > 0 and
        ((prices[i]["close"] - prices[i - LOOKBACK]["close"])
         / prices[i - LOOKBACK]["close"]) * 100 > 20.0
    ]
    instances = with_cooldown(eligible)
    valid = [i for i in instances if i + max(HORIZONS) < len(prices)]

    result = {
        "label": "Preset 2 — Extended Run",
        "condition": "Price >20% above its level 20 trading days ago",
        "total_instances": len(instances),
        "valid_instances": len(valid),
    }

    if len(valid) < MIN_SAMPLES:
        result["note"] = (
            f"Only {len(valid)} instances with full forward data — "
            "insufficient for reliable statistics."
        )
        return result

    by_horizon = defaultdict(list)
    drawdowns = []
    for idx in valid:
        rets, dd = forward_returns(prices, idx, HORIZONS)
        for h, r in rets.items():
            by_horizon[h].append(r)
        drawdowns.append(dd)

    result["stats"] = {f"+{h}d": stats_block(by_horizon[h]) for h in HORIZONS}
    result["avg_max_drawdown"] = round(sum(drawdowns) / len(drawdowns), 1)
    result["worst_max_drawdown"] = round(min(drawdowns), 1)
    return result


# ---------------------------------------------------------------------------
# Preset 3: Pre-Earnings Entry
# ---------------------------------------------------------------------------

def preset_pre_earnings(prices, earnings_dates):
    """
    Entry: 10 trading days before each historical earnings release.
    Outcome: measured from entry through earnings day + 5 trading days.
    Also reports the earnings-day move in isolation.
    """
    if not earnings_dates:
        return {
            "label": "Preset 3 — Pre-Earnings Entry",
            "condition": "Entry 10 trading days before earnings; outcome through earnings + 5 days",
            "total_instances": 0,
            "valid_instances": 0,
            "note": "No historical earnings dates found.",
        }

    from datetime import timedelta
    date_to_idx = {p["date"]: i for i, p in enumerate(prices)}

    instances = []
    for earn_str in earnings_dates:
        earn_idx = None
        for offset in range(5):
            candidate = (
                datetime.strptime(earn_str, "%Y-%m-%d") + timedelta(days=offset)
            ).strftime("%Y-%m-%d")
            if candidate in date_to_idx:
                earn_idx = date_to_idx[candidate]
                break
        if earn_idx is None or earn_idx < 10:
            continue
        instances.append((earn_idx - 10, earn_idx))

    FORWARD = 5
    valid = [(e, x) for e, x in instances if x + FORWARD < len(prices)]

    result = {
        "label": "Preset 3 — Pre-Earnings Entry",
        "condition": "Entry 10 trading days before earnings; outcome through earnings + 5 days",
        "total_instances": len(instances),
        "valid_instances": len(valid),
    }

    if len(valid) < MIN_SAMPLES:
        result["note"] = (
            f"Only {len(valid)} instances with full forward data — "
            "insufficient for reliable statistics."
        )
        return result

    full_rets = []
    earn_day_rets = []
    drawdowns = []

    for entry_idx, earn_idx in valid:
        ep = prices[entry_idx]["close"]
        outcome = prices[earn_idx + FORWARD]["close"]
        full_rets.append(((outcome - ep) / ep) * 100.0)

        if earn_idx > 0:
            pre = prices[earn_idx - 1]["close"]
            earn_close = prices[earn_idx]["close"]
            earn_day_rets.append(((earn_close - pre) / pre) * 100.0)

        window = [prices[j]["close"] for j in range(entry_idx, earn_idx + FORWARD + 1)]
        drawdowns.append(((min(window) - ep) / ep) * 100.0)

    result["stats"] = {"entry_to_earn+5d": stats_block(full_rets)}
    if earn_day_rets:
        result["stats"]["earnings_day_move"] = stats_block(earn_day_rets)

    result["avg_max_drawdown"] = round(sum(drawdowns) / len(drawdowns), 1)
    result["worst_max_drawdown"] = round(min(drawdowns), 1)
    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_text(ticker, presets, current_price, pct_below_52wh, gain_vs_20d, level_context=None):
    lines = []
    lines.append(f"=== Historical Entry Pattern Analysis: {ticker} ===")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Current price: ${current_price:.2f}")

    if pct_below_52wh is not None:
        flag = ""
        if 15.0 <= pct_below_52wh <= 30.0:
            flag = "  <-- CURRENTLY IN DIP BUYER ZONE"
        elif pct_below_52wh > 30.0:
            flag = "  <-- BELOW DIP BUYER ZONE (deeper than 30%)"
        lines.append(f"% below 52-week high: {pct_below_52wh:.1f}%{flag}")

    if gain_vs_20d is not None:
        flag = "  <-- CURRENTLY IN EXTENDED RUN ZONE" if gain_vs_20d > 20.0 else ""
        lines.append(f"Gain vs. 20 trading days ago: {gain_vs_20d:+.1f}%{flag}")

    if level_context:
        lines.append("")
        lines.append("--- Level Context ---")
        atr = level_context.get("atr_20d")
        atr_pct = level_context.get("atr_20d_pct_of_price")
        if atr is not None:
            pct_part = f"  ({atr_pct}% of price)" if atr_pct is not None else ""
            lines.append(f"ATR(20d): ${atr:.2f}{pct_part}")
        sma_50 = level_context.get("sma_50d")
        sma_200 = level_context.get("sma_200d")
        if sma_50 is not None:
            lines.append(f"50 DMA:   ${sma_50:.2f}")
        if sma_200 is not None:
            lines.append(f"200 DMA:  ${sma_200:.2f}")
        swings = level_context.get("recent_swing_lows") or []
        if swings:
            pretty = ", ".join(f"${s['price']:.2f} ({s['date']})" for s in swings)
            lines.append(f"Recent swing lows: {pretty}")

    lines.append("")

    for p in presets:
        lines.append(f"--- {p['label']} ---")
        lines.append(f"Condition: {p['condition']}")
        lines.append(
            f"Historical instances: {p['total_instances']} total, "
            f"{p['valid_instances']} with full forward data"
        )

        if "note" in p:
            lines.append(f"NOTE: {p['note']}")
            lines.append("")
            continue

        for horizon_key, s in p.get("stats", {}).items():
            lines.append(
                f"  {horizon_key}: win rate {s['win_rate']}%, "
                f"avg {s['avg_return']:+.1f}%  "
                f"(best {s['best']:+.1f}%, worst {s['worst']:+.1f}%, n={s['n']})"
            )

        if "avg_max_drawdown" in p:
            lines.append(
                f"  Avg max drawdown during period: {p['avg_max_drawdown']:+.1f}%  "
                f"(worst case: {p['worst_max_drawdown']:+.1f}%)"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze historical entry patterns via yfinance"
    )
    parser.add_argument("--ticker", required=True, help="Ticker symbol (e.g. NVDA)")
    parser.add_argument("--years", type=int, default=5, help="Years of history (default 5)")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )
    args = parser.parse_args()

    ticker = args.ticker.upper()

    print(f"Fetching {args.years}-year price history for {ticker} via yfinance...", file=sys.stderr)
    prices = fetch_price_history(ticker, args.years)

    if not prices or len(prices) < 60:
        print(
            f"ERROR: Insufficient price history for {ticker} "
            f"(got {len(prices)} trading days, need at least 60).",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"  {len(prices)} trading days loaded ({prices[0]['date']} → {prices[-1]['date']}).", file=sys.stderr)

    print("Fetching historical earnings dates...", file=sys.stderr)
    earnings_dates = fetch_earnings_dates(ticker)
    print(f"  {len(earnings_dates)} earnings dates found.", file=sys.stderr)

    roll_max = rolling_max(prices, 252)

    current_price = prices[-1]["close"]
    curr_52wh = roll_max[-1]
    pct_below_52wh = ((curr_52wh - current_price) / curr_52wh) * 100.0 if curr_52wh else None
    price_20d_ago = prices[-21]["close"] if len(prices) > 21 else None
    gain_vs_20d = (
        ((current_price - price_20d_ago) / price_20d_ago) * 100.0
        if price_20d_ago else None
    )

    print("Running preset analysis...", file=sys.stderr)
    p1 = preset_dip_buyer(prices, roll_max)
    p2 = preset_extended_run(prices)
    p3 = preset_pre_earnings(prices, earnings_dates)
    presets = [p1, p2, p3]

    level_context = compute_level_context(prices)

    if args.format == "json":
        out = json.dumps(
            {
                "ticker": ticker,
                "generated_at": datetime.now().isoformat(),
                "current_price": current_price,
                "pct_below_52wh": round(pct_below_52wh, 1) if pct_below_52wh is not None else None,
                "gain_vs_20d": round(gain_vs_20d, 1) if gain_vs_20d is not None else None,
                "levelContext": level_context,
                "presets": presets,
            },
            indent=2,
        )
    else:
        out = format_text(ticker, presets, current_price, pct_below_52wh, gain_vs_20d, level_context)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
