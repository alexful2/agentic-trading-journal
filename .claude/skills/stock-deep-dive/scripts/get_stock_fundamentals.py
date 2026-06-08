#!/usr/bin/env python3
"""
Fetch stock fundamentals via yfinance (Yahoo Finance).
No API key required.

Install dependency: pip install yfinance

Usage: python get_stock_fundamentals.py --ticker NVDA [--output FILE]
"""

import argparse
import json
import math
import sys
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(val):
    """Convert NaN / inf floats to None for JSON serialization."""
    if val is None:
        return None
    try:
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
    except TypeError:
        pass
    return val


def _get(d, key):
    """Safe dict get with NaN → None cleaning."""
    return _clean(d.get(key))


# ---------------------------------------------------------------------------
# Section fetchers
# ---------------------------------------------------------------------------

def _quote_and_profile(info, fast_info):
    price = year_high = year_low = market_cap = None

    if fast_info:
        try:
            price = _clean(fast_info.last_price)
            year_high = _clean(fast_info.year_high)
            year_low = _clean(fast_info.year_low)
            market_cap = _clean(fast_info.market_cap)
        except Exception:
            pass

    price = price or _get(info, "currentPrice") or _get(info, "regularMarketPrice")
    year_high = year_high or _get(info, "fiftyTwoWeekHigh")
    year_low = year_low or _get(info, "fiftyTwoWeekLow")
    market_cap = market_cap or _get(info, "marketCap")

    prev = _get(info, "previousClose") or _get(info, "regularMarketPreviousClose")
    day_chg_pct = None
    if price and prev and prev > 0:
        day_chg_pct = round(((price - prev) / prev) * 100, 2)

    quote = {
        "price": price,
        "previousClose": prev,
        "dayChangePercent": day_chg_pct,
        "volume": _get(info, "volume") or _get(info, "regularMarketVolume"),
        "averageVolume": _get(info, "averageVolume"),
        "marketCap": market_cap,
        "yearHigh": year_high,
        "yearLow": year_low,
        "beta": _get(info, "beta"),
    }

    profile = {
        "name": _get(info, "longName") or _get(info, "shortName"),
        "sector": _get(info, "sector"),
        "industry": _get(info, "industry"),
    }

    return quote, profile


def _key_metrics(info):
    return {
        "trailingPE": _get(info, "trailingPE"),
        "forwardPE": _get(info, "forwardPE"),
        "evToEbitda": _get(info, "enterpriseToEbitda"),
        "priceToSales": _get(info, "priceToSalesTrailing12Months"),
        "returnOnEquity": _get(info, "returnOnEquity"),
        "debtToEquity": _get(info, "debtToEquity"),
        "grossMargins": _get(info, "grossMargins"),
        "operatingMargins": _get(info, "operatingMargins"),
        "profitMargins": _get(info, "profitMargins"),
        "revenueGrowth": _get(info, "revenueGrowth"),
        "earningsGrowth": _get(info, "earningsGrowth"),
        "freeCashflow": _get(info, "freeCashflow"),
        "operatingCashflow": _get(info, "operatingCashflow"),
    }


def _quarterly_financials(t):
    result = []
    try:
        qf = t.quarterly_financials
        if qf is None or qf.empty:
            return result

        row_map = {
            "Total Revenue": "revenue",
            "Gross Profit": "grossProfit",
            "Operating Income": "operatingIncome",
            "Net Income": "netIncome",
            "Basic EPS": "epsBasic",
            "Diluted EPS": "epsDiluted",
        }

        for col in list(qf.columns)[:4]:
            q = {}
            q["date"] = str(col.date()) if hasattr(col, "date") else str(col)[:10]
            for src, dst in row_map.items():
                if src in qf.index:
                    raw = qf.loc[src, col]
                    q[dst] = _clean(float(raw)) if raw is not None else None
                else:
                    q[dst] = None
            result.append(q)
    except Exception as e:
        print(f"  WARNING [quarterly-financials]: {e}", file=sys.stderr)

    return result


def _earnings_history(t):
    result = []
    try:
        eh = getattr(t, "earnings_history", None)

        # Newer yfinance versions: earnings_history is a DataFrame
        if eh is not None and not getattr(eh, "empty", True):
            for idx in list(eh.index)[:4]:
                row = eh.loc[idx]
                date_str = str(idx.date()) if hasattr(idx, "date") else str(idx)[:10]
                result.append({
                    "date": date_str,
                    "epsActual": _clean(float(row.get("epsActual", float("nan")))),
                    "epsEstimate": _clean(float(row.get("epsEstimate", float("nan")))),
                    "surprisePct": _clean(float(row.get("surprisePercent", float("nan")))),
                })
        else:
            # Fallback: earnings_dates has reported vs estimated EPS
            now = datetime.now(timezone.utc)
            ed = t.earnings_dates
            if ed is not None and not ed.empty:
                past = ed[ed.index < now].head(4)
                for idx, row in past.iterrows():
                    date_str = str(idx.date()) if hasattr(idx, "date") else str(idx)[:10]
                    result.append({
                        "date": date_str,
                        "epsActual": _clean(row.get("Reported EPS")),
                        "epsEstimate": _clean(row.get("EPS Estimate")),
                        "surprisePct": _clean(row.get("Surprise(%)")),
                    })
    except Exception as e:
        print(f"  WARNING [earnings-history]: {e}", file=sys.stderr)

    return result


def _next_earnings(t):
    try:
        cal = t.calendar
        if isinstance(cal, dict) and "Earnings Date" in cal:
            ed = cal["Earnings Date"]
            first = ed[0] if isinstance(ed, list) and ed else ed
            if first is not None:
                return str(first.date()) if hasattr(first, "date") else str(first)[:10]

        # Fallback: first future date in earnings_dates index
        now = datetime.now(timezone.utc)
        ed = t.earnings_dates
        if ed is not None and not ed.empty:
            future = ed[ed.index > now]
            if not future.empty:
                d = min(future.index)
                return str(d.date()) if hasattr(d, "date") else str(d)[:10]
    except Exception as e:
        print(f"  WARNING [next-earnings]: {e}", file=sys.stderr)

    return None


def _analyst_targets(info):
    return {
        "targetMean": _get(info, "targetMeanPrice"),
        "targetMedian": _get(info, "targetMedianPrice"),
        "targetHigh": _get(info, "targetHighPrice"),
        "targetLow": _get(info, "targetLowPrice"),
        "numberOfAnalysts": _get(info, "numberOfAnalystOpinions"),
        "recommendation": _get(info, "recommendationKey"),
        "recommendationMean": _get(info, "recommendationMean"),
    }


def _fair_value_bands(info, quote, key_metrics):
    """
    Compute bear/base/bull price bands as a valuation cross-check for the
    Step 4 price ladder.

    Emits both fwd-P/E and P/S bands when the underlying data exists —
    the skill picks whichever is most meaningful for the stock in context.
    Fwd-P/E is cleanest for mature, profitable businesses. P/S is usually
    more informative for growth / pre-profit names where fwd-EPS is tiny
    or negative and produces band prices far below the trading range.

    These are reference numbers only — the ladder still comes from the
    skill's thesis reasoning. The bands let the skill audit whether each
    ladder level lives in a defensible part of the valuation range.
    """
    current_price = quote.get("price")
    fwd_eps = _get(info, "forwardEps")
    ps = key_metrics.get("priceToSales")

    fwd_pe_bands = None
    if fwd_eps is not None and fwd_eps > 0:
        fwd_pe_bands = {
            "basis": {"forwardEps": round(fwd_eps, 2)},
            "bands": {
                "bear": {"multiple": 15, "price": round(fwd_eps * 15, 2), "label": "15× fwd EPS"},
                "base": {"multiple": 20, "price": round(fwd_eps * 20, 2), "label": "20× fwd EPS"},
                "bull": {"multiple": 25, "price": round(fwd_eps * 25, 2), "label": "25× fwd EPS"},
            },
        }

    ps_bands = None
    if ps is not None and ps > 0 and current_price:
        rev_per_share = current_price / ps
        bear_mult = round(ps * 0.7, 1)
        base_mult = round(ps * 1.0, 1)
        bull_mult = round(ps * 1.4, 1)
        ps_bands = {
            "basis": {
                "revenuePerShare": round(rev_per_share, 2),
                "currentPriceToSales": round(ps, 1),
            },
            "bands": {
                "bear": {"multiple": bear_mult, "price": round(rev_per_share * bear_mult, 2), "label": f"{bear_mult}× P/S (–30% multiple)"},
                "base": {"multiple": base_mult, "price": round(rev_per_share * base_mult, 2), "label": f"{base_mult}× P/S (current)"},
                "bull": {"multiple": bull_mult, "price": round(rev_per_share * bull_mult, 2), "label": f"{bull_mult}× P/S (+40% multiple)"},
            },
        }

    # Suggest which method is likely the useful ladder anchor. Fwd-P/E is
    # meaningful when the stock trades at a normal earnings multiple (roughly
    # 8–30× fwd). Above that, the 20× base band sits well below current price
    # and is only a ladder anchor under a thesis collapse — P/S becomes the
    # more informative frame. Skill is free to override this in its reasoning.
    suggested = None
    fwd_pe = key_metrics.get("forwardPE")
    if fwd_pe_bands and fwd_pe is not None and 8 <= fwd_pe <= 30:
        suggested = "forward_pe"
    elif ps_bands:
        suggested = "price_to_sales"
    elif fwd_pe_bands:
        suggested = "forward_pe"

    if not fwd_pe_bands and not ps_bands:
        return {
            "suggested": None,
            "forwardPe": None,
            "priceToSales": None,
            "note": "Insufficient data (no positive fwd EPS or P/S available)",
        }

    return {
        "suggested": suggested,
        "forwardPe": fwd_pe_bands,
        "priceToSales": ps_bands,
        "note": None,
    }


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def summarize(data):
    q = data.get("quote") or {}
    p = data.get("profile") or {}
    m = data.get("keyMetrics") or {}
    t = data.get("analystTargets") or {}

    chg = q.get("dayChangePercent")
    chg_str = f"  ({chg:+.2f}% today)" if chg is not None else ""

    print(f"\n--- {data['ticker']} Summary ---", file=sys.stderr)
    print(f"  Company:    {p.get('name', 'N/A')}", file=sys.stderr)
    print(f"  Price:      ${q.get('price', 'N/A')}{chg_str}", file=sys.stderr)
    print(f"  52w range:  ${q.get('yearLow', 'N/A')} – ${q.get('yearHigh', 'N/A')}", file=sys.stderr)
    print(f"  Market cap: ${q.get('marketCap', 'N/A')}", file=sys.stderr)
    print(f"  P/E (TTM):  {m.get('trailingPE', 'N/A')}", file=sys.stderr)
    print(f"  Fwd P/E:    {m.get('forwardPE', 'N/A')}", file=sys.stderr)
    print(f"  EV/EBITDA:  {m.get('evToEbitda', 'N/A')}", file=sys.stderr)
    print(f"  Avg target: ${t.get('targetMean', 'N/A')}  ({t.get('recommendation', 'N/A')})", file=sys.stderr)
    print(f"  Next earn:  {data.get('nextEarningsDate', 'N/A')}", file=sys.stderr)

    qtrs = data.get("quarterlyFinancials") or []
    eps_h = data.get("earningsHistory") or []
    print(f"  Quarters loaded:  {len(qtrs)}", file=sys.stderr)
    print(f"  EPS history:      {len(eps_h)} quarters", file=sys.stderr)

    missing = [k for k, v in (data.get("keyMetrics") or {}).items() if v is None]
    if missing:
        print(f"  N/A fields: {', '.join(missing)}", file=sys.stderr)

    fv = data.get("fairValueBands") or {}
    suggested = fv.get("suggested")

    def _print_bands(label, block, is_primary):
        if not block:
            return
        b = block.get("bands", {})
        marker = " [primary]" if is_primary else ""
        print(
            f"  Fair-value ({label}){marker}:  "
            f"bear ${b.get('bear', {}).get('price', 'N/A')}  "
            f"base ${b.get('base', {}).get('price', 'N/A')}  "
            f"bull ${b.get('bull', {}).get('price', 'N/A')}",
            file=sys.stderr,
        )

    _print_bands("fwd-P/E", fv.get("forwardPe"), suggested == "forward_pe")
    _print_bands("P/S", fv.get("priceToSales"), suggested == "price_to_sales")
    if not fv.get("forwardPe") and not fv.get("priceToSales") and fv.get("note"):
        print(f"  Fair-value: N/A ({fv['note']})", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch stock fundamentals via yfinance")
    parser.add_argument("--ticker", required=True, help="Ticker symbol (e.g. NVDA)")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    args = parser.parse_args()

    ticker_str = args.ticker.upper()
    print(f"Fetching fundamentals for {ticker_str} via yfinance...", file=sys.stderr)

    t = yf.Ticker(ticker_str)

    try:
        info = t.info
    except Exception as e:
        print(f"ERROR: Could not fetch data for {ticker_str}: {e}", file=sys.stderr)
        sys.exit(1)

    # Minimal validity check
    has_price = info.get("currentPrice") or info.get("regularMarketPrice")
    has_name = info.get("longName") or info.get("shortName")
    if not has_price and not has_name:
        print(
            f"ERROR: No data returned for {ticker_str}. "
            "Check the ticker symbol and your internet connection.",
            file=sys.stderr,
        )
        sys.exit(1)

    fast_info = None
    try:
        fast_info = t.fast_info
    except Exception:
        pass

    quote, profile = _quote_and_profile(info, fast_info)
    key_metrics = _key_metrics(info)
    quarterly = _quarterly_financials(t)
    earnings_hist = _earnings_history(t)
    next_earn = _next_earnings(t)
    analyst = _analyst_targets(info)
    fair_value = _fair_value_bands(info, quote, key_metrics)

    data = {
        "ticker": ticker_str,
        "generated_at": datetime.now().isoformat(),
        "quote": quote,
        "profile": profile,
        "keyMetrics": key_metrics,
        "quarterlyFinancials": quarterly,
        "earningsHistory": earnings_hist,
        "nextEarningsDate": next_earn,
        "analystTargets": analyst,
        "fairValueBands": fair_value,
    }

    summarize(data)

    output = json.dumps(data, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nOutput written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
