#!/usr/bin/env python3
"""
Compute the options-implied 1-day earnings move vs. historical realized moves.

Uses yfinance to pull the options chain for the first expiry on or after the
upcoming earnings date, takes the ATM straddle premium, and divides by spot.
Then compares to the distribution of |1-day| moves from the last N earnings
prints.

Output JSON:
- currentSpot
- nextEarningsDate
- expiryUsed (first expiry on/after earnings date)
- atmStrike
- straddlePremium (call mid + put mid)
- impliedMovePct  (straddle / spot)
- historicalRealized: { count, mean, median, max, moves: [...] }
- richness: "rich" | "fair" | "cheap" — implied vs. historical median
    rich  = implied > 1.25 × historical median
    cheap = implied < 0.80 × historical median
    fair  = in between

Install dependency: pip install yfinance
Usage: python get_implied_move.py --ticker VRT [--output FILE]
"""

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("ERROR: yfinance / pandas not installed.", file=sys.stderr)
    sys.exit(1)


def _clean(val):
    if val is None:
        return None
    try:
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
    except TypeError:
        pass
    return val


def _mid(row):
    bid = row.get("bid")
    ask = row.get("ask")
    last = row.get("lastPrice")
    if bid and ask and bid > 0 and ask > 0:
        return (bid + ask) / 2
    return last


def _nearest_expiry_after(expiries, earnings_date):
    """First options expiry on or after the earnings date."""
    if not expiries or earnings_date is None:
        return None
    parsed = []
    for e in expiries:
        try:
            parsed.append(datetime.strptime(e, "%Y-%m-%d").date())
        except Exception:
            continue
    parsed = sorted(parsed)
    for d in parsed:
        if d >= earnings_date:
            return d.strftime("%Y-%m-%d")
    return parsed[-1].strftime("%Y-%m-%d") if parsed else None


def _atm_strike(strikes, spot):
    if not strikes or spot is None:
        return None
    return min(strikes, key=lambda s: abs(s - spot))


def _get_spot(t):
    try:
        fi = t.fast_info
        p = fi.last_price
        if p:
            return float(p)
    except Exception:
        pass
    try:
        info = t.info
        for k in ("currentPrice", "regularMarketPrice", "previousClose"):
            if info.get(k):
                return float(info[k])
    except Exception:
        pass
    return None


def _next_earnings_date(t):
    try:
        cal = t.calendar
        if isinstance(cal, dict) and "Earnings Date" in cal:
            ed = cal["Earnings Date"]
            first = ed[0] if isinstance(ed, list) and ed else ed
            if first is not None:
                return first.date() if hasattr(first, "date") else first
        now = datetime.now(timezone.utc)
        ed = t.earnings_dates
        if ed is not None and not ed.empty:
            future = ed[ed.index > now]
            if not future.empty:
                d = min(future.index)
                return d.date() if hasattr(d, "date") else d
    except Exception as e:
        print(f"  WARNING [next-earnings]: {e}", file=sys.stderr)
    return None


def _historical_realized_moves(t, num_quarters=8):
    """Absolute % moves on the first trading day after each of the last N prints."""
    moves = []
    now = datetime.now(timezone.utc)
    try:
        ed = t.earnings_dates
        if ed is None or ed.empty:
            return moves

        past = ed[ed.index < now].head(num_quarters)
        if past.empty:
            return moves

        start = past.index.min() - timedelta(days=10)
        end = past.index.max() + timedelta(days=10)
        hist = t.history(start=start, end=end, auto_adjust=False)
        if hist.empty:
            return moves

        for idx in past.index:
            try:
                tz = hist.index.tz
                idx_aware = idx.tz_convert(tz) if tz is not None and idx.tz is not None else idx
                on_or_before = hist.index[hist.index <= idx_aware]
                on_or_after = hist.index[hist.index > idx_aware]
                if len(on_or_before) < 1 or len(on_or_after) < 1:
                    continue
                prior_close_idx = on_or_before[-1]
                if len(on_or_before) >= 2:
                    prior_close_idx = on_or_before[-2]
                after_candidates = hist.index[hist.index > prior_close_idx]
                if len(after_candidates) < 1:
                    continue
                after_idx = after_candidates[0]
                prior_close = float(hist.loc[prior_close_idx, "Close"])
                after_close = float(hist.loc[after_idx, "Close"])
                if prior_close > 0:
                    move_pct = abs((after_close - prior_close) / prior_close) * 100
                    moves.append({
                        "date": str(idx.date()) if hasattr(idx, "date") else str(idx)[:10],
                        "absMovePct": round(move_pct, 2),
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"  WARNING [realized-moves]: {e}", file=sys.stderr)
    return moves


def _classify_richness(implied_pct, realized_median_pct):
    if implied_pct is None or realized_median_pct is None or realized_median_pct == 0:
        return None
    ratio = implied_pct / realized_median_pct
    if ratio > 1.25:
        return "rich"
    if ratio < 0.80:
        return "cheap"
    return "fair"


def summarize(data):
    print(f"\n--- {data['ticker']} Implied Move ---", file=sys.stderr)
    print(f"  Spot:              ${data.get('currentSpot', 'N/A')}", file=sys.stderr)
    print(f"  Earnings:          {data.get('nextEarningsDate', 'N/A')}", file=sys.stderr)
    print(f"  Expiry used:       {data.get('expiryUsed', 'N/A')}", file=sys.stderr)
    print(f"  ATM strike:        {data.get('atmStrike', 'N/A')}", file=sys.stderr)
    print(f"  Straddle premium:  ${data.get('straddlePremium', 'N/A')}", file=sys.stderr)
    print(f"  Implied move:      {data.get('impliedMovePct', 'N/A')}%", file=sys.stderr)
    hr = data.get("historicalRealized") or {}
    print(f"  Realized (median): {hr.get('median', 'N/A')}%  (n={hr.get('count', 0)})", file=sys.stderr)
    print(f"  Richness:          {data.get('richness', 'N/A')}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--output")
    parser.add_argument("--quarters", type=int, default=8)
    args = parser.parse_args()

    ticker = args.ticker.upper()
    print(f"Fetching options-implied move for {ticker}...", file=sys.stderr)

    t = yf.Ticker(ticker)

    spot = _get_spot(t)
    earnings_date = _next_earnings_date(t)

    data = {
        "ticker": ticker,
        "generated_at": datetime.now().isoformat(),
        "currentSpot": round(spot, 2) if spot else None,
        "nextEarningsDate": str(earnings_date) if earnings_date else None,
        "expiryUsed": None,
        "atmStrike": None,
        "straddlePremium": None,
        "impliedMovePct": None,
        "historicalRealized": None,
        "richness": None,
        "notes": [],
    }

    if spot is None:
        data["notes"].append("Could not determine spot price.")
    if earnings_date is None:
        data["notes"].append("Could not determine next earnings date.")

    # Options chain
    try:
        expiries = list(t.options) if hasattr(t, "options") else []
        if not expiries:
            data["notes"].append("No options expiries available (illiquid or unlisted).")
        elif earnings_date is not None:
            expiry = _nearest_expiry_after(expiries, earnings_date)
            data["expiryUsed"] = expiry
            if expiry:
                chain = t.option_chain(expiry)
                calls = chain.calls
                puts = chain.puts
                if calls is not None and puts is not None and not calls.empty and not puts.empty:
                    strikes = sorted(set(calls["strike"].tolist()) & set(puts["strike"].tolist()))
                    atm = _atm_strike(strikes, spot) if spot else None
                    data["atmStrike"] = float(atm) if atm is not None else None

                    if atm is not None and spot is not None:
                        call_row = calls[calls["strike"] == atm].iloc[0].to_dict()
                        put_row = puts[puts["strike"] == atm].iloc[0].to_dict()
                        call_mid = _mid(call_row)
                        put_mid = _mid(put_row)
                        if call_mid is not None and put_mid is not None:
                            straddle = float(call_mid) + float(put_mid)
                            data["straddlePremium"] = round(straddle, 2)
                            data["impliedMovePct"] = round((straddle / spot) * 100, 2)
    except Exception as e:
        print(f"  WARNING [options-chain]: {e}", file=sys.stderr)
        data["notes"].append(f"Options chain fetch failed: {e}")

    # Historical realized
    moves = _historical_realized_moves(t, num_quarters=args.quarters)
    if moves:
        abs_moves = [m["absMovePct"] for m in moves if m["absMovePct"] is not None]
        if abs_moves:
            median = statistics.median(abs_moves)
            data["historicalRealized"] = {
                "count": len(abs_moves),
                "mean": round(sum(abs_moves) / len(abs_moves), 2),
                "median": round(median, 2),
                "max": round(max(abs_moves), 2),
                "moves": moves,
            }
            data["richness"] = _classify_richness(data["impliedMovePct"], median)

    summarize(data)
    output = json.dumps(data, indent=2, default=str)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nOutput written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
