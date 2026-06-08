#!/usr/bin/env python3
"""
Fetch pre-earnings setup data via yfinance.

Outputs JSON with:
- Next earnings date + trading days until print
- Consensus EPS + revenue estimates for the upcoming quarter
- EPS revisions trend (up/down in last 7d / 30d)
- Last 8 quarters beat/miss history: reported EPS, consensus, surprise %, 1-day price reaction
- Guidance trajectory summary (beat magnitude trend)

Install dependency: pip install yfinance
Usage: python get_earnings_setup.py --ticker VRT [--output FILE]
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone, timedelta

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print(
        "ERROR: yfinance / pandas not installed.\nRun: pip install yfinance pandas",
        file=sys.stderr,
    )
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


def _trading_days_between(d1, d2):
    """Rough count of US trading days (weekdays only, no holiday calendar)."""
    if d1 is None or d2 is None:
        return None
    if d1 > d2:
        d1, d2 = d2, d1
    days = pd.bdate_range(d1, d2)
    return max(0, len(days) - 1)


def _next_earnings(t):
    """Return (date_obj, trading_days_until) — both None if unknown."""
    today = datetime.now(timezone.utc).date()
    try:
        cal = t.calendar
        if isinstance(cal, dict) and "Earnings Date" in cal:
            ed = cal["Earnings Date"]
            first = ed[0] if isinstance(ed, list) and ed else ed
            if first is not None:
                d = first.date() if hasattr(first, "date") else first
                return d, _trading_days_between(today, d)

        ed = t.earnings_dates
        if ed is not None and not ed.empty:
            now = datetime.now(timezone.utc)
            future = ed[ed.index > now]
            if not future.empty:
                d = min(future.index)
                d = d.date() if hasattr(d, "date") else d
                return d, _trading_days_between(today, d)
    except Exception as e:
        print(f"  WARNING [next-earnings]: {e}", file=sys.stderr)

    return None, None


def _consensus_estimates(t):
    """Fetch forward consensus EPS + revenue for current quarter.

    yfinance's get_earnings_estimate() returns rows indexed by period: 0q, +1q, 0y, +1y.
    0q = current quarter (the one about to be reported).
    """
    result = {
        "eps": {"currentQ": None, "nextQ": None, "currentY": None},
        "revenue": {"currentQ": None, "nextQ": None, "currentY": None},
        "revisions": {
            "eps_up_7d": None,
            "eps_down_7d": None,
            "eps_up_30d": None,
            "eps_down_30d": None,
        },
        "analystCount": None,
    }

    try:
        eps_est = t.get_earnings_estimate()
        if eps_est is not None and not eps_est.empty:
            for period_key, dest_key in [("0q", "currentQ"), ("+1q", "nextQ"), ("0y", "currentY")]:
                if period_key in eps_est.index:
                    row = eps_est.loc[period_key]
                    result["eps"][dest_key] = {
                        "avg": _clean(row.get("avg")),
                        "low": _clean(row.get("low")),
                        "high": _clean(row.get("high")),
                        "yearAgoEps": _clean(row.get("yearAgoEps")),
                        "numberOfAnalysts": _clean(row.get("numberOfAnalysts")),
                        "growth": _clean(row.get("growth")),
                    }
                    if dest_key == "currentQ" and result["analystCount"] is None:
                        result["analystCount"] = _clean(row.get("numberOfAnalysts"))
    except Exception as e:
        print(f"  WARNING [eps-estimate]: {e}", file=sys.stderr)

    try:
        rev_est = t.get_revenue_estimate()
        if rev_est is not None and not rev_est.empty:
            for period_key, dest_key in [("0q", "currentQ"), ("+1q", "nextQ"), ("0y", "currentY")]:
                if period_key in rev_est.index:
                    row = rev_est.loc[period_key]
                    result["revenue"][dest_key] = {
                        "avg": _clean(row.get("avg")),
                        "low": _clean(row.get("low")),
                        "high": _clean(row.get("high")),
                        "yearAgoRevenue": _clean(row.get("yearAgoRevenue")),
                        "numberOfAnalysts": _clean(row.get("numberOfAnalysts")),
                        "growth": _clean(row.get("growth")),
                    }
    except Exception as e:
        print(f"  WARNING [revenue-estimate]: {e}", file=sys.stderr)

    try:
        rev = t.get_eps_revisions()
        if rev is not None and not rev.empty and "0q" in rev.index:
            row = rev.loc["0q"]
            result["revisions"] = {
                "eps_up_7d": _clean(row.get("upLast7days")),
                "eps_down_7d": _clean(row.get("downLast7days")),
                "eps_up_30d": _clean(row.get("upLast30days")),
                "eps_down_30d": _clean(row.get("downLast30days")),
            }
    except Exception as e:
        print(f"  WARNING [eps-revisions]: {e}", file=sys.stderr)

    return result


def _beat_miss_history(t, num_quarters=8):
    """Last N quarters: consensus EPS, reported EPS, surprise %, 1-day price reaction."""
    result = []
    now = datetime.now(timezone.utc)

    try:
        ed = t.earnings_dates
        if ed is None or ed.empty:
            return result

        past = ed[ed.index < now].head(num_quarters)
        if past.empty:
            return result

        earliest = past.index.min() - timedelta(days=10)
        latest = past.index.max() + timedelta(days=10)
        try:
            hist = t.history(start=earliest, end=latest, auto_adjust=False)
        except Exception:
            hist = pd.DataFrame()

        for idx, row in past.iterrows():
            date_str = str(idx.date()) if hasattr(idx, "date") else str(idx)[:10]
            reported = _clean(row.get("Reported EPS"))
            estimate = _clean(row.get("EPS Estimate"))
            surprise = _clean(row.get("Surprise(%)"))

            reaction_pct = None
            if not hist.empty:
                try:
                    tz = hist.index.tz
                    idx_aware = idx.tz_convert(tz) if tz is not None and idx.tz is not None else idx
                    on_or_before = hist.index[hist.index <= idx_aware]
                    on_or_after = hist.index[hist.index >= idx_aware]

                    if len(on_or_before) > 0 and len(on_or_after) > 0:
                        prior_close_idx = on_or_before[-1]
                        # If earnings was intraday, prior_close_idx may equal idx.
                        # Back up one day to get the pre-print close.
                        if len(on_or_before) >= 2:
                            prior_close_idx = on_or_before[-2]

                        after_candidates = hist.index[hist.index > prior_close_idx]
                        if len(after_candidates) > 0:
                            after_idx = after_candidates[0]
                            prior_close = float(hist.loc[prior_close_idx, "Close"])
                            after_close = float(hist.loc[after_idx, "Close"])
                            if prior_close > 0:
                                reaction_pct = round(((after_close - prior_close) / prior_close) * 100, 2)
                except Exception:
                    pass

            result.append({
                "date": date_str,
                "epsEstimate": estimate,
                "epsReported": reported,
                "surprisePct": surprise,
                "reactionPct": reaction_pct,
            })
    except Exception as e:
        print(f"  WARNING [beat-miss-history]: {e}", file=sys.stderr)

    return result


def _guidance_trajectory(history):
    """Summarize whether beats are accelerating, decelerating, or steady.

    Looks at the last 4 quarters' surprise %. Not a prediction — just a trend
    description.
    """
    if len(history) < 3:
        return None
    recent = [h.get("surprisePct") for h in history[:4] if h.get("surprisePct") is not None]
    if len(recent) < 3:
        return None
    # history[0] is most recent
    newest = recent[0]
    oldest = recent[-1]
    avg = sum(recent) / len(recent)
    trend = "steady"
    if len(recent) >= 3:
        # Check monotonic decel: each subsequent newer quarter's surprise is smaller in absolute value
        abs_vals = [abs(v) for v in recent]
        if all(abs_vals[i] <= abs_vals[i + 1] for i in range(len(abs_vals) - 1)):
            trend = "decelerating (beat magnitude shrinking)"
        elif all(abs_vals[i] >= abs_vals[i + 1] for i in range(len(abs_vals) - 1)):
            trend = "accelerating (beat magnitude growing)"
    return {
        "avgSurprisePct": round(avg, 2),
        "newestSurprisePct": round(newest, 2) if newest is not None else None,
        "oldestInWindowSurprisePct": round(oldest, 2) if oldest is not None else None,
        "trend": trend,
        "quartersUsed": len(recent),
    }


def summarize(data):
    print(f"\n--- {data['ticker']} Pre-Earnings Setup ---", file=sys.stderr)
    ne = data.get("nextEarnings") or {}
    print(f"  Next earnings:      {ne.get('date', 'N/A')}  ({ne.get('tradingDaysUntil', 'N/A')} trading days)", file=sys.stderr)

    est = data.get("consensusEstimates") or {}
    eps_cq = (est.get("eps") or {}).get("currentQ") or {}
    rev_cq = (est.get("revenue") or {}).get("currentQ") or {}
    print(f"  Consensus EPS (Q):  {eps_cq.get('avg', 'N/A')}  (n={eps_cq.get('numberOfAnalysts', 'N/A')}, growth {eps_cq.get('growth', 'N/A')})", file=sys.stderr)
    print(f"  Consensus Rev (Q):  {rev_cq.get('avg', 'N/A')}  (growth {rev_cq.get('growth', 'N/A')})", file=sys.stderr)

    rev = est.get("revisions") or {}
    print(f"  EPS revisions 30d:  up {rev.get('eps_up_30d', 'N/A')} / down {rev.get('eps_down_30d', 'N/A')}", file=sys.stderr)

    traj = data.get("guidanceTrajectory")
    if traj:
        print(f"  Trajectory:         {traj.get('trend')} (avg {traj.get('avgSurprisePct')}% over last {traj.get('quartersUsed')}Q)", file=sys.stderr)

    hist = data.get("beatMissHistory") or []
    print(f"  Beat/miss quarters loaded: {len(hist)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Pre-earnings setup via yfinance")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--output")
    parser.add_argument("--quarters", type=int, default=8)
    args = parser.parse_args()

    ticker = args.ticker.upper()
    print(f"Fetching pre-earnings setup for {ticker}...", file=sys.stderr)

    t = yf.Ticker(ticker)

    try:
        _ = t.info
    except Exception as e:
        print(f"ERROR: Could not fetch {ticker}: {e}", file=sys.stderr)
        sys.exit(1)

    ne_date, ne_days = _next_earnings(t)
    estimates = _consensus_estimates(t)
    history = _beat_miss_history(t, num_quarters=args.quarters)
    trajectory = _guidance_trajectory(history)

    data = {
        "ticker": ticker,
        "generated_at": datetime.now().isoformat(),
        "nextEarnings": {
            "date": str(ne_date) if ne_date else None,
            "tradingDaysUntil": ne_days,
        },
        "consensusEstimates": estimates,
        "beatMissHistory": history,
        "guidanceTrajectory": trajectory,
    }

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
