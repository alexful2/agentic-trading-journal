#!/usr/bin/env python3
"""
Monte Carlo sensitivity for the deep-dive Implied Expectations block.

Takes a valuation MODEL plus sourced low/base/high ranges for its inputs, samples
the inputs (triangular by default), propagates each draw through the model to an
implied per-share value, and reports:
  - the percentile distribution of implied price,
  - the BREAK-EVEN PROBABILITY = P(implied price >= today's market price),
  - per-variable sensitivity (|Pearson r| of input vs. output) -> the crux variable.

This is SENSITIVITY ANALYSIS, not prediction. It does not forecast price; it asks
"across the plausible range of the assumptions, how often does today's price look
justified, and which assumption drives the answer?" Every input range must be
sourced (analyst low/mean/high, guidance band, historical vol) -- garbage ranges
give a garbage distribution. There is no training and no fitting; output is
deterministic given --seed. The break-even probability is the honest substitute
for typing a made-up P(bull): you never assert a probability, the sourced ranges
produce one. (Pairs with C8 - Kelly Criterion: no fake-precise probabilities.)

Models (each declares the input names it needs; any input may be supplied as a
fixed constant instead of a {low, base, high} range, and vice-versa):

  unit-econ    implied_price = (capacity_mw * utilization * rev_per_mw
                                * ebitda_margin * ev_ebitda_mult - net_debt) / shares_out
               rev_per_mw is annual $ revenue per MW. To pass EBITDA-per-MW
               directly, set ebitda_margin = 1.

  reverse-dcf  implied_price = [ sum_{t=1..years} fcf0_ps*(1+growth)^t / (1+discount)^t
                                 + terminal ]
               terminal = fcf_year_N*(1+terminal_growth)/(discount-terminal_growth)
                          / (1+discount)^years      (Gordon terminal, discounted back)
               fcf0_ps is trailing free cash flow PER SHARE. Draws where
               discount <= terminal_growth are skipped and counted.

  multiple     implied_price = (metric * exit_multiple - net_debt) / shares_out
               metric = a forward $ driver (revenue, EBITDA, earnings). For an
               equity multiple (P/E, P/S) set net_debt = 0 and metric = the
               equity driver; for an EV multiple pass net_debt and an EV driver.

Spec via --spec-file <path> or --spec '<json>':
  {
    "model": "unit-econ",
    "market_price": 63.54,
    "draws": 20000,
    "seed": 42,
    "variables": {
       "capacity_mw":    {"low": 0.75, "base": 1.0,   "high": 1.4},
       "rev_per_mw":     {"low": 3.0e6, "base": 3.6e6, "high": 4.2e6, "dist": "triangular"},
       "ebitda_margin":  {"low": 0.45, "base": 0.55,  "high": 0.65},
       "ev_ebitda_mult": {"low": 10,   "base": 14,    "high": 20}
    },
    "constants": { "utilization": 0.9, "shares_out": 270000000, "net_debt": -200000000 }
  }

Per-variable "dist": "triangular" (default), "uniform", or "normal"
(mean = base, sd = (high - low) / 4, so low..high spans ~+/-2 sd).

Usage:
  python monte_carlo_valuation.py --spec-file iren_spec.json
  python monte_carlo_valuation.py --spec '{...}' --format human
"""

import argparse
import json
import math
import random
import sys


MODELS = ("unit-econ", "reverse-dcf", "multiple")
PCTILES = (5, 10, 25, 50, 75, 90, 95)


class SpecError(Exception):
    pass


def _need(resolved, name, model):
    if name not in resolved:
        raise SpecError(f"model '{model}' needs input '{name}' (as a variable range or a constant)")
    return resolved[name]


def _model_unit_econ(r):
    ev = (_need(r, "capacity_mw", "unit-econ") * r.get("utilization", 1.0)
          * _need(r, "rev_per_mw", "unit-econ") * _need(r, "ebitda_margin", "unit-econ")
          * _need(r, "ev_ebitda_mult", "unit-econ"))
    equity = ev - r.get("net_debt", 0.0)
    shares = _need(r, "shares_out", "unit-econ")
    if shares <= 0:
        raise SpecError("shares_out must be > 0")
    return equity / shares


def _model_reverse_dcf(r):
    g = _need(r, "growth", "reverse-dcf")
    disc = _need(r, "discount", "reverse-dcf")
    tg = r.get("terminal_growth", 0.025)
    years = int(r.get("years", 10))
    fcf0 = _need(r, "fcf0_ps", "reverse-dcf")
    if disc <= tg:
        return None  # degenerate terminal — skip this draw
    pv = 0.0
    fcf = fcf0
    for t in range(1, years + 1):
        fcf = fcf0 * (1 + g) ** t
        pv += fcf / (1 + disc) ** t
    terminal = fcf * (1 + tg) / (disc - tg) / (1 + disc) ** years
    return pv + terminal


def _model_multiple(r):
    shares = _need(r, "shares_out", "multiple")
    if shares <= 0:
        raise SpecError("shares_out must be > 0")
    equity = _need(r, "metric", "multiple") * _need(r, "exit_multiple", "multiple") - r.get("net_debt", 0.0)
    return equity / shares


_MODEL_FNS = {"unit-econ": _model_unit_econ, "reverse-dcf": _model_reverse_dcf, "multiple": _model_multiple}


def _sample(rng, spec):
    low, base, high = spec["low"], spec["base"], spec["high"]
    if low > high:
        low, high = high, low
    dist = spec.get("dist", "triangular")
    if low == high:
        return low
    if dist == "uniform":
        return rng.uniform(low, high)
    if dist == "normal":
        sd = (high - low) / 4.0
        return rng.gauss(base, sd)
    return rng.triangular(low, high, base)  # triangular default


def _percentile(sorted_vals, pct):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    rank = pct / 100.0 * (len(sorted_vals) - 1)
    lo = int(math.floor(rank))
    hi = int(math.ceil(rank))
    if lo == hi:
        return sorted_vals[lo]
    frac = rank - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def _pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / math.sqrt(sxx * syy)


def run(spec):
    model = spec.get("model")
    if model not in MODELS:
        raise SpecError(f"model must be one of {MODELS}, got {model!r}")
    market_price = spec.get("market_price")
    if not (isinstance(market_price, (int, float)) and math.isfinite(market_price) and market_price > 0):
        raise SpecError("spec needs 'market_price' > 0")
    draws = int(spec.get("draws", 20000))
    if draws < 1:
        raise SpecError("'draws' must be >= 1")
    seed = int(spec.get("seed", 42))
    variables = spec.get("variables", {}) or {}
    constants = spec.get("constants", {}) or {}
    if not variables:
        raise SpecError("spec needs at least one entry in 'variables' (else there is nothing to sample)")
    for name, vs in variables.items():
        for k in ("low", "base", "high"):
            if k not in vs:
                raise SpecError(f"variable '{name}' missing '{k}'")
        lo, ba, hi = vs["low"], vs["base"], vs["high"]
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (lo, ba, hi)):
            raise SpecError(f"variable '{name}' has a non-finite low/base/high")
        if not (lo <= ba <= hi):
            raise SpecError(f"variable '{name}' needs low <= base <= high (got {lo}/{ba}/{hi})")
        dist = vs.get("dist", "triangular")
        if dist not in ("triangular", "uniform", "normal"):
            raise SpecError(f"variable '{name}' has unknown dist '{dist}' (use triangular|uniform|normal)")

    rng = random.Random(seed)
    fn = _MODEL_FNS[model]
    outputs = []
    sampled = {name: [] for name in variables}
    skipped = 0
    for _ in range(draws):
        draw = dict(constants)
        for name, vs in variables.items():
            draw[name] = _sample(rng, vs)
        val = fn(draw)
        if val is None or not math.isfinite(val):
            skipped += 1
            continue
        outputs.append(val)
        for name in variables:
            sampled[name].append(draw[name])

    if not outputs:
        raise SpecError("every draw was skipped (degenerate spec — check discount vs terminal_growth, or ranges)")

    sorted_out = sorted(outputs)
    pcts = {f"p{p}": _percentile(sorted_out, p) for p in PCTILES}
    mean = sum(outputs) / len(outputs)
    be_prob = sum(1 for o in outputs if o >= market_price) / len(outputs)

    sens = []
    for name in variables:
        r = _pearson(sampled[name], outputs)
        sens.append({"variable": name, "corr": round(r, 4), "abs_corr": round(abs(r), 4)})
    sens.sort(key=lambda d: -d["abs_corr"])

    return {
        "model": model,
        "market_price": market_price,
        "draws_requested": draws,
        "draws_used": len(outputs),
        "draws_skipped": skipped,
        "seed": seed,
        "implied_price": {
            **{k: (round(v, 4) if v is not None else None) for k, v in pcts.items()},
            "mean": round(mean, 4),
        },
        "break_even_probability": round(be_prob, 4),
        "sensitivity": sens,
        "crux_variable": sens[0]["variable"] if sens else None,
    }


def _fmt_money(x):
    if x is None:
        return "N/A"
    return f"${x:,.2f}"


def _human(res):
    ip = res["implied_price"]
    lines = []
    lines.append(f"Monte Carlo — model={res['model']}  draws={res['draws_used']}/{res['draws_requested']}"
                 + (f" (skipped {res['draws_skipped']})" if res["draws_skipped"] else "")
                 + f"  seed={res['seed']}")
    lines.append(f"Market price: {_fmt_money(res['market_price'])}")
    lines.append("")
    lines.append("Implied price distribution:")
    lines.append(f"  p5  {_fmt_money(ip['p5']):>14}   p25 {_fmt_money(ip['p25']):>14}   p50 {_fmt_money(ip['p50']):>14}")
    lines.append(f"  p75 {_fmt_money(ip['p75']):>14}   p90 {_fmt_money(ip['p90']):>14}   p95 {_fmt_money(ip['p95']):>14}")
    lines.append(f"  mean {_fmt_money(ip['mean'])}")
    lines.append("")
    lines.append(f"BREAK-EVEN PROBABILITY (implied >= price): {res['break_even_probability'] * 100:.1f}%")
    lines.append("(p50/mean are distribution percentiles — NOT a fair-value price target.)")
    lines.append(f"CRUX VARIABLE: {res['crux_variable']}")
    lines.append("Sensitivity (|Pearson r| of input vs implied price):")
    for s in res["sensitivity"]:
        bar = "#" * int(round(s["abs_corr"] * 30))
        lines.append(f"  {s['variable']:<18} {s['corr']:+.3f}  {bar}")
    lines.append("")
    lines.append("Sensitivity analysis, not a forecast. Input ranges must be sourced.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--spec", help="Inline JSON spec")
    g.add_argument("--spec-file", help="Path to a JSON spec file")
    parser.add_argument("--format", choices=("json", "human"), default="json")
    args = parser.parse_args()

    try:
        if args.spec_file:
            with open(args.spec_file, encoding="utf-8") as fh:
                spec = json.load(fh)
        else:
            spec = json.loads(args.spec)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: could not read spec: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        res = run(spec)
    except SpecError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.format == "human":
        print(_human(res))
    else:
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
