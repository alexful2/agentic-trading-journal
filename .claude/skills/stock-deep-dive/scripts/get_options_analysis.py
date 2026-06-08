#!/usr/bin/env python3
"""
get_options_analysis.py — Evaluates whether buying calls makes sense over shares.

Takes the JSON output of get_historical_patterns.py and current options chain
data to determine if the math works: does the pattern's avg return clear the
breakeven at a reasonable strike/expiry, given current IV levels?

Three conditions must ALL pass:
  1. Best entry pattern win rate >= 60%
  2. ATM implied vol <= 1.5x 30-day realized vol  (options not expensive)
  3. Pattern avg return clears breakeven for some OTM call at target expiry

Outputs conditions_met: true/false with full data. Silent omission is the
intended behavior when conditions_met is false — don't mention calls at all.

Usage:
    python get_options_analysis.py --ticker NVDA --pattern-file patterns.json
    python get_options_analysis.py --ticker NVDA --pattern-file patterns.json --output opts.json
    python get_options_analysis.py --ticker NVDA --pattern-file patterns.json --format json
"""

import argparse
import json
import math
import sys
from datetime import datetime

try:
    import numpy as np
    import yfinance as yf
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}\nRun: pip install yfinance numpy", file=sys.stderr)
    sys.exit(1)


# ─── Thresholds ───────────────────────────────────────────────────────────────

MIN_WIN_RATE    = 60.0   # Win rate must be >= 60% (0-100 scale to match pattern JSON)
MAX_IV_RATIO    = 1.50   # ATM IV must be <= 1.5x realized vol
MIN_EXPIRY_DAYS = 45     # Don't look at options closer than 45 days out
MAX_EXPIRY_DAYS = 270    # Don't go beyond ~9 months
EXPIRY_BUFFER   = 2.0    # Target expiry = pattern_horizon_calendar_days * this
TRADING_TO_CAL  = 1.4    # Approx trading-day to calendar-day multiplier
OTM_TARGETS     = [0.05, 0.07, 0.10, 0.12, 0.15]  # Scanned least-to-most OTM


def log(msg):
    print(msg, file=sys.stderr)


# ─── Pattern parsing ──────────────────────────────────────────────────────────

def get_best_pattern(pattern_json):
    """
    Extract the best-performing pattern from get_historical_patterns.py JSON.

    JSON structure (from that script):
      {
        "current_price": float,
        "pct_below_52wh": float | null,
        "gain_vs_20d": float | null,
        "presets": [
          { "label": "Preset 1 — Dip Buyer", "stats": {"+21d": {...}, "+42d": {...}, "+63d": {...}},
            "avg_max_drawdown": float, "worst_max_drawdown": float, "valid_instances": int },
          { "label": "Preset 2 — Extended Run", ... },
          { "label": "Preset 3 — Pre-Earnings Entry",
            "stats": {"entry_to_earn+5d": {...}, "earnings_day_move": {...}}, ... }
        ]
      }
    Stats blocks: { "win_rate": float (0-100), "avg_return": float (%), "best": %, "worst": %, "n": int }
    Presets missing "stats" key had insufficient historical instances — skip them.
    """
    presets = pattern_json.get("presets", [])
    pct_below = pattern_json.get("pct_below_52wh")
    gain_20d  = pattern_json.get("gain_vs_20d")

    best = None
    best_wr = 0.0

    for i, preset in enumerate(presets):
        if "stats" not in preset:
            continue  # insufficient data

        stats = preset["stats"]
        instances = preset.get("valid_instances", 0)
        worst_dd  = preset.get("worst_max_drawdown", -99.0)
        avg_dd    = preset.get("avg_max_drawdown", -20.0)

        if i < 2:
            # Dip Buyer (0) or Extended Run (1) — prefer 42d horizon
            for hkey in ["+42d", "+63d", "+21d"]:
                if hkey not in stats:
                    continue
                s = stats[hkey]
                wr      = s.get("win_rate", 0.0)
                avg_ret = s.get("avg_return", 0.0)
                h_days  = int(hkey.strip("+d"))
                h_cal   = int(h_days * TRADING_TO_CAL)

                # Determine if this preset is currently active
                if i == 0:
                    active = pct_below is not None and 15.0 <= pct_below <= 30.0
                else:
                    active = gain_20d is not None and gain_20d > 20.0

                if wr > best_wr:
                    best_wr = wr
                    best = {
                        "name": preset["label"],
                        "win_rate": wr,
                        "avg_return_pct": avg_ret,
                        "horizon_key": hkey,
                        "horizon_trading_days": h_days,
                        "horizon_calendar_days": h_cal,
                        "instances": instances,
                        "worst_drawdown_pct": worst_dd,
                        "avg_drawdown_pct": avg_dd,
                        "is_active_today": active,
                    }
                break  # only best horizon per preset

        else:
            # Pre-Earnings (2) — use entry_to_earn+5d horizon (~15 trading / 21 cal days)
            if "entry_to_earn+5d" not in stats:
                continue
            s  = stats["entry_to_earn+5d"]
            wr = s.get("win_rate", 0.0)
            avg_ret = s.get("avg_return", 0.0)

            if wr > best_wr:
                best_wr = wr
                best = {
                    "name": preset["label"],
                    "win_rate": wr,
                    "avg_return_pct": avg_ret,
                    "horizon_key": "entry_to_earn+5d",
                    "horizon_trading_days": 15,
                    "horizon_calendar_days": 21,
                    "instances": instances,
                    "worst_drawdown_pct": worst_dd,
                    "avg_drawdown_pct": avg_dd,
                    "is_active_today": False,  # can't infer pre-earnings window from JSON alone
                }

    return best


# ─── Realized volatility ──────────────────────────────────────────────────────

def get_realized_vol_30d(ticker_obj):
    """Annualized 30-day realized vol from daily log returns via yfinance."""
    try:
        hist = ticker_obj.history(period="3mo")
        if len(hist) < 31:
            return None
        closes = hist["Close"].tail(31)
        log_returns = np.log(closes / closes.shift(1)).dropna()
        return round(float(log_returns.std() * math.sqrt(252)), 4)
    except Exception as e:
        log(f"Warning: realized vol calc failed: {e}")
        return None


# ─── Options chain ────────────────────────────────────────────────────────────

def fetch_options_chain(ticker_obj, current_price, target_days):
    """
    Fetch calls chain for the expiry closest to target_days.
    Returns (atm_iv, calls_df, expiry_str, actual_expiry_days) or four Nones.
    """
    try:
        available = ticker_obj.options
        if not available:
            log("No listed options for this ticker.")
            return None, None, None, None

        today = datetime.today()
        best_expiry, best_diff = None, float("inf")

        for exp_str in available:
            exp_dt   = datetime.strptime(exp_str, "%Y-%m-%d")
            days_out = (exp_dt - today).days
            if not (MIN_EXPIRY_DAYS <= days_out <= MAX_EXPIRY_DAYS):
                continue
            diff = abs(days_out - target_days)
            if diff < best_diff:
                best_diff, best_expiry = diff, exp_str

        if not best_expiry:
            log(f"No expiry found in {MIN_EXPIRY_DAYS}–{MAX_EXPIRY_DAYS} day window.")
            return None, None, None, None

        chain    = ticker_obj.option_chain(best_expiry)
        calls    = chain.calls.copy()
        exp_days = (datetime.strptime(best_expiry, "%Y-%m-%d") - today).days

        if calls.empty:
            log("Empty calls chain.")
            return None, None, None, None

        # ATM IV: implied vol of call closest to spot
        calls["_dist"] = abs(calls["strike"] - current_price)
        atm_row = calls.loc[calls["_dist"].idxmin()]
        iv_val  = atm_row.get("impliedVolatility")
        atm_iv  = float(iv_val) if iv_val and float(iv_val) > 0 else None

        log(f"Selected expiry: {best_expiry} ({exp_days}d)")
        if atm_iv:
            log(f"ATM IV: {atm_iv:.1%}")

        return atm_iv, calls, best_expiry, exp_days

    except Exception as e:
        log(f"Error fetching options chain: {e}")
        return None, None, None, None


# ─── Strike selection ─────────────────────────────────────────────────────────

def find_best_strike(calls, current_price, expiry_str, expiry_days, avg_pattern_return_pct):
    """
    Scan OTM% targets from least OTM (cheapest breakeven %) to most OTM.
    Return the first strike whose breakeven the pattern's avg return clears.
    Returns a data dict, or None if nothing clears.
    """
    for otm_pct in OTM_TARGETS:
        target_strike = current_price * (1 + otm_pct)

        calls["_d"] = abs(calls["strike"] - target_strike)
        row = calls.loc[calls["_d"].idxmin()]

        strike = float(row["strike"])
        bid    = float(row.get("bid",       0) or 0)
        ask    = float(row.get("ask",       0) or 0)
        last   = float(row.get("lastPrice", 0) or 0)

        premium = (bid + ask) / 2 if bid > 0 and ask > 0 else last
        if premium <= 0.01:
            continue

        actual_otm_pct = (strike - current_price) / current_price * 100
        breakeven_price = strike + premium
        breakeven_pct   = (breakeven_price - current_price) / current_price * 100

        implied_target       = current_price * (1 + avg_pattern_return_pct / 100)
        intrinsic_at_avg     = max(0.0, implied_target - strike)
        option_profit_at_avg = intrinsic_at_avg - premium
        option_return_pct    = option_profit_at_avg / premium * 100

        iv_val    = row.get("impliedVolatility")
        delta_val = row.get("delta")
        strike_iv = float(iv_val)    if iv_val    and float(iv_val)    > 0 else None
        delta     = float(delta_val) if delta_val is not None               else None

        log(f"  ${strike:.0f} ({actual_otm_pct:.1f}% OTM): "
            f"prem ${premium:.2f}, bkevn {breakeven_pct:.1f}% "
            f"vs pattern avg {avg_pattern_return_pct:.1f}%")

        if avg_pattern_return_pct > breakeven_pct:
            return {
                "strike":                   round(strike, 2),
                "actual_otm_pct":           round(actual_otm_pct, 1),
                "expiry":                   expiry_str,
                "expiry_days":              expiry_days,
                "premium":                  round(premium, 2),
                "breakeven_price":          round(breakeven_price, 2),
                "breakeven_pct":            round(breakeven_pct, 1),
                "leverage_ratio":           round(current_price / premium, 1),
                "delta":                    round(delta, 2) if delta is not None else None,
                "strike_iv":                round(strike_iv, 4) if strike_iv else None,
                "implied_target_price":     round(implied_target, 2),
                "option_return_at_avg_pct": round(option_return_pct, 1),
            }

    return None


# ─── IV label ─────────────────────────────────────────────────────────────────

def classify_iv_ratio(r):
    if   r < 0.85: return "cheap — IV below recent realized vol"
    elif r < 1.10: return "fair"
    elif r < 1.35: return "slightly elevated"
    elif r < 1.50: return "elevated"
    else:          return "expensive"


# ─── Main ─────────────────────────────────────────────────────────────────────

def _fail(reason, detail, filter_results=None):
    return {
        "conditions_met": False,
        "fail_reason":    reason,
        "fail_detail":    detail,
        "filter_results": filter_results or {},
        "recommendation": None,
    }


def analyze(ticker_symbol, pattern_json):
    log(f"\n=== Options Analysis: {ticker_symbol} ===")

    yf_ticker = yf.Ticker(ticker_symbol)

    try:
        current_price = float(yf_ticker.fast_info.last_price)
    except Exception:
        log("ERROR: Could not fetch current price.")
        sys.exit(1)
    log(f"Current price: ${current_price:.2f}")

    # ── Filter 1: pattern win rate ─────────────────────────────────────────
    best = get_best_pattern(pattern_json)
    if not best:
        return _fail("no_valid_pattern",
                     "No entry pattern has sufficient history (≥4 instances required).")

    log(f"Best pattern: {best['name']}  |  {best['win_rate']:.0f}% win rate  |  "
        f"avg {best['avg_return_pct']:+.1f}% ({best['horizon_key']})")

    if best["win_rate"] < MIN_WIN_RATE:
        return _fail("win_rate_too_low",
                     f"Best pattern win rate {best['win_rate']:.0f}% < {MIN_WIN_RATE:.0f}% minimum.",
                     {"win_rate": best["win_rate"], "win_rate_pass": False})

    # ── Realized vol + target expiry ───────────────────────────────────────
    realized_vol = get_realized_vol_30d(yf_ticker)
    log(f"30d realized vol: {realized_vol:.1%}" if realized_vol else "30d realized vol: unavailable")

    target_days = max(60, int(best["horizon_calendar_days"] * EXPIRY_BUFFER))
    log(f"Target expiry: ~{target_days} calendar days")

    # ── Fetch options chain ────────────────────────────────────────────────
    atm_iv, calls_df, expiry_str, expiry_days = fetch_options_chain(
        yf_ticker, current_price, target_days
    )
    if calls_df is None:
        return _fail("no_options_data",
                     "Could not fetch options chain — ticker may not have listed options.")

    # ── Filter 2: IV ratio ─────────────────────────────────────────────────
    iv_ratio = iv_label = None
    iv_pass  = True

    if atm_iv and realized_vol:
        iv_ratio = round(atm_iv / realized_vol, 2)
        iv_label = classify_iv_ratio(iv_ratio)
        iv_pass  = iv_ratio <= MAX_IV_RATIO
        log(f"IV ratio: {iv_ratio:.2f} ({iv_label})")

        if not iv_pass:
            return _fail("iv_too_expensive",
                         f"IV ratio {iv_ratio:.2f} > {MAX_IV_RATIO} — options too expensive right now.",
                         {"win_rate": best["win_rate"], "win_rate_pass": True,
                          "iv_ratio": iv_ratio, "iv_label": iv_label, "iv_pass": False})
    else:
        log("IV ratio: skipped (data unavailable — proceeding without IV filter)")

    # ── Filter 3 + strike selection ────────────────────────────────────────
    log(f"\nScanning strikes ({expiry_str}):")
    strike = find_best_strike(
        calls_df, current_price, expiry_str, expiry_days, best["avg_return_pct"]
    )
    if not strike:
        return _fail("return_doesnt_clear_breakeven",
                     f"Pattern avg +{best['avg_return_pct']:.1f}% doesn't clear breakeven "
                     f"for any scanned strike at {expiry_str}.",
                     {"win_rate": best["win_rate"], "win_rate_pass": True,
                      "iv_ratio": iv_ratio, "iv_label": iv_label, "iv_pass": iv_pass,
                      "breakeven_pass": False})

    # ── All conditions met ─────────────────────────────────────────────────
    buffer_ratio = round(expiry_days / best["horizon_calendar_days"], 1)

    return {
        "conditions_met": True,
        "fail_reason":    None,
        "filter_results": {
            "win_rate":      best["win_rate"], "win_rate_pass": True,
            "iv_ratio":      iv_ratio,         "iv_label":      iv_label,
            "iv_pass":       iv_pass,          "breakeven_pass": True,
        },
        "recommendation": {
            "current_price":               round(current_price, 2),
            "pattern_name":                best["name"],
            "pattern_win_rate_pct":        best["win_rate"],
            "pattern_avg_return_pct":      best["avg_return_pct"],
            "pattern_horizon":             best["horizon_key"],
            "pattern_horizon_calendar_days": best["horizon_calendar_days"],
            "pattern_instances":           best["instances"],
            "pattern_worst_drawdown_pct":  best["worst_drawdown_pct"],
            "pattern_avg_drawdown_pct":    best["avg_drawdown_pct"],
            "pattern_is_active_today":     best["is_active_today"],
            "atm_iv":                      round(atm_iv, 4) if atm_iv else None,
            "realized_vol_30d":            realized_vol,
            "iv_ratio":                    iv_ratio,
            "iv_label":                    iv_label,
            "expiry_buffer_ratio":         buffer_ratio,
            **strike,
        },
    }


# ─── Text output ──────────────────────────────────────────────────────────────

def format_text(result, ticker):
    lines = [f"=== Options Analysis: {ticker} ===", ""]

    if not result["conditions_met"]:
        lines += [
            "STATUS: CONDITIONS NOT MET — calls not recommended over shares",
            f"Reason: {result.get('fail_detail', result['fail_reason'])}",
        ]
        fr = result.get("filter_results", {})
        if "win_rate" in fr:
            lines.append(f"  Win rate: {fr['win_rate']:.0f}%  "
                         f"({'pass' if fr.get('win_rate_pass') else 'FAIL — below 60% threshold'})")
        if fr.get("iv_ratio") is not None:
            lines.append(f"  IV ratio: {fr['iv_ratio']:.2f} ({fr.get('iv_label', '')})  "
                         f"({'pass' if fr.get('iv_pass') else 'FAIL — too expensive'})")
        if "breakeven_pass" in fr:
            lines.append(f"  Breakeven clearance: "
                         f"{'pass' if fr['breakeven_pass'] else 'FAIL — pattern avg below breakeven'}")
        return "\n".join(lines)

    r = result["recommendation"]
    lines += [
        "STATUS: CONDITIONS MET",
        "",
        f"Entry pattern:  {r['pattern_name']}",
        f"  Win rate:     {r['pattern_win_rate_pct']:.0f}%  ({r['pattern_instances']} historical instances)",
        f"  Avg return:   +{r['pattern_avg_return_pct']:.1f}%  ({r['pattern_horizon']} / "
        f"~{r['pattern_horizon_calendar_days']} calendar days)",
        f"  Active today: {'Yes' if r['pattern_is_active_today'] else 'No'}",
        "",
        f"Recommended call ({ticker}, ${r['current_price']:.2f}):",
        f"  Strike:       ${r['strike']:.2f}  ({r['actual_otm_pct']:.1f}% OTM)",
        f"  Expiry:       {r['expiry']}  ({r['expiry_days']}d / {r['expiry_buffer_ratio']:.1f}x pattern buffer)",
        f"  Premium:      ${r['premium']:.2f}  →  breakeven ${r['breakeven_price']:.2f}  (+{r['breakeven_pct']:.1f}%)",
        f"  Pattern avg:  +{r['pattern_avg_return_pct']:.1f}%  →  implied target ${r['implied_target_price']:.2f}",
        f"  Return @ avg: ~{r['option_return_at_avg_pct']:.0f}%  (vs +{r['pattern_avg_return_pct']:.1f}% on shares)",
        f"  Leverage:     {r['leverage_ratio']:.1f}x  (stock price / premium)",
    ]
    if r.get("delta") is not None:
        lines.append(f"  Delta:        {r['delta']:.2f}")
    if r.get("iv_ratio") is not None:
        lines.append(f"  IV ratio:     {r['iv_ratio']:.2f}  ({r['iv_label']})")
    lines += [
        "",
        "Risk comparison:",
        f"  Max loss (calls):     100% of premium  (${r['premium']:.2f}/share)",
        f"  Avg drawdown (shares): {r['pattern_avg_drawdown_pct']:.1f}%",
        f"  Worst drawdown (shares): {r['pattern_worst_drawdown_pct']:.1f}%",
        "",
        "Sizing: max 1-2% of portfolio given 100% total-loss risk on options.",
    ]
    return "\n".join(lines)


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate calls vs shares using historical pattern data and live options chain"
    )
    parser.add_argument("--ticker",       required=True, help="Ticker symbol e.g. NVDA")
    parser.add_argument("--pattern-file", required=True,
                        help="Path to JSON output from get_historical_patterns.py (--format json)")
    parser.add_argument("--output",  help="Write JSON result to this file path")
    parser.add_argument("--format",  choices=["text", "json", "both"], default="both",
                        help="Output format (default: both)")
    args = parser.parse_args()

    ticker = args.ticker.upper()

    try:
        with open(args.pattern_file, "r", encoding="utf-8") as f:
            pattern_json = json.load(f)
    except Exception as e:
        log(f"ERROR: Could not load --pattern-file '{args.pattern_file}': {e}")
        sys.exit(1)

    result = analyze(ticker, pattern_json)

    if args.format in ("text", "both"):
        print(format_text(result, ticker))

    if args.format in ("json", "both"):
        json_out = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_out)
            log(f"JSON written to {args.output}")
        elif args.format == "json":
            print(json_out)
        else:
            log(f"\nJSON:\n{json_out}")


if __name__ == "__main__":
    main()
