# Quant tools — the Implied Expectations layer

Shared helpers for the deep-dive **Implied Expectations** block (Step 4c) and its
relatives. The whole layer is a **verifier**: it states what today's price requires
you to believe and what would prove it wrong. It never originates a thesis, never
emits a fair-value price target, and never invents a probability.

Three pieces: one script (Monte Carlo), one ledger field (break-even P), and one
inline method (Bayesian posture). A calibration *report* is deliberately **not**
built yet — see the bottom.

---

## 1. `monte_carlo_valuation.py` — break-even probability + crux variable

**What it does.** Takes a valuation model plus *sourced* low/base/high ranges for
its inputs, samples them (triangular by default), propagates each draw to an
implied per-share value, and reports the distribution, the **break-even
probability** = P(implied ≥ today's price), and a per-variable sensitivity
ranking whose top entry is the **crux variable**.

**Why it exists.** It's the honest substitute for typing a made-up P(bull). You
never assert a probability — the sourced ranges produce one by simulation. It's
*sensitivity analysis, not prediction*: no training, no fitting, deterministic
given `--seed`. Pairs with [[C8 - Kelly Criterion and Position Sizing]] (no
fake-precise probabilities) and can't overfit the way a trained price model would
([[C1 - Publication & Arbitrage Decay]], [[C2 - Replication Crisis in Factor Anomalies]]).

**Models** (`unit-econ`, `reverse-dcf`, `multiple`) — see the script docstring for
formulas. Any input can be a sampled `{low, base, high}` range or a fixed
`constant`.

**Use in a deep dive (Step 4c):**
1. Pick the archetype equation. Source low/base/high for each uncertain input from
   *this run's* numbers — analyst low/mean/high, guidance band, historical vol,
   the fundamentals script, the dossier. **Garbage ranges → garbage distribution.**
2. Run it:
   ```bash
   python .claude/scripts/monte_carlo_valuation.py --spec-file spec.json --format human
   ```
3. Cite the break-even probability, the p25–p75 band, and the crux variable in the
   Implied Expectations block. Report the **break-even probability**, not the p50
   as a "fair value" — the point estimate is the false-precision trap.

**Discipline:** ranges must be sourced; keep `seed` fixed so the number is
reproducible/auditable; if you can't source ranges, skip the MC and reason the
break-even qualitatively. The crux variable should match the one the prose names.

---

## 2. `Break-even P` — verdict-ledger column

`log_verdict.py` takes an optional `--breakeven-prob 0.XX` that records the Step 4c
break-even probability in `vault/deep-dives/_verdicts.md`.

```bash
python .claude/scripts/log_verdict.py --ticker NVDA --verdict ADD --price 63.54 \
    --file NVDA-2026-06-07.md --breakeven-prob 0.45
```

It lives in the **ledger** (not just the deep-dive file) because deep-dive files
are auto-deleted when superseded — the ledger is the only durable home for the
prediction. Appended as the last column so `check_verdict_drift.py`'s `parts[:5]`
indexing is unaffected. `—` when the dive named no quantifiable break-even.

This is the **rail** for eventual self-calibration: a prediction logged at decision
time, whose outcome accrues later. Nothing reads it yet.

---

## 3. Bayesian posture — an inline method, *not* a script

For execution-thesis schedule confidence (and any "is the claimed milestone real?"
question), reason as a structured confidence update — but do it **inline**, and
report an **ordinal posture**, not a precise percent:

- **Prior:** management's claimed schedule is on track (a coarse prior, e.g. "lean
  yes").
- **Update directionally by signal tier:** an independent Tier-A confirmation
  raises confidence; a company-only Tier-B claim raises it a little; a Tier-A/B
  contradiction lowers it; an *expected* signal that's missing lowers it.
- **Report posture:** On Schedule / Likely On Schedule / Unknown / Likely Behind /
  Behind — plus the 1–2 signals that moved it most.

**Why no calculator.** A script that multiplies guessed likelihood ratios into a
"posterior 73%" manufactures exactly the false precision this layer exists to
avoid — the LRs are themselves vibes. The value is the *explicit, consistent
direction and magnitude* of the update, not a decimal. Keep it as a reasoning
frame; if a number ever helps, write it as a posture band, not a point estimate.

---

## Calibration — deferred on purpose

No `calibration_report.py` yet. With only a handful of resolved verdicts, a
calibrator would output "insufficient data" — the premature-calibration-loop the
vault's own discipline warns against (skip calibration loops until drift is real).
Build it once ~30 single-ticker verdicts have resolved (price moved enough, or the
trade closed with a `library/TICKER - YYYY-MM-DD Close.md` arc). It will read the
`Break-even P` column + realized outcomes and live inside `quarterly-review`, which
already owns the calibration pass.
