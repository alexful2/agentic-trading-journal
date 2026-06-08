Status: #library
Tags: #framework #earnings #sizing

---

# Pre-Earnings Cross-Print Playbook

A per-print plan handles one earnings event at a time. When two or more portfolio-relevant prints fall within ~5 trading days, the plans need cross-coordination: cash is shared, earlier prints carry information about later same-cohort prints, and attention spills over. This playbook layers on top of the per-print plans; it does not replace them.

**When this applies:** ≥2 portfolio-relevant prints within 5 trading days — especially when two of them share a thesis (same-cohort) and a third is independent.

## Three coordination axes

**1. Cash allocation across prints.** Before any print fires, identify the total dry powder earmarked for "earnings adds this week." Cap the first print's add at ≤50% of that bucket, the second at ≤50% of what's left, and so on. The bias is to leave room for the *last* print to be larger if the cohort signal has firmed by then. The wrong move is pre-committing the full bucket to print 1 and being out of cash if print 3 turns into the actual layup.

**2. Same-cohort information flow.** When two prints share a thesis, the earlier print is data about the later one's setup:
- *Earlier same-cohort positive (beat + raise + upgrades):* confirm the later add at planned size; consider upsizing within the bucket cap if the cohort read is unusually strong.
- *Earlier same-cohort negative (miss, guide-down, or beat-but-stock-down on something thesis-relevant):* reduce the later add by ≥50%, or skip. This is [[macro-cohort-confirmation]] firing — the cohort signal trumps the single-name plan.
- *Earlier same-cohort mixed (beat but soft guidance, or beat-and-raise but stock down on something idiosyncratic):* hold the later add at planned size; don't upsize, don't skip.

The fresh data is the read on cohort-level demand and the cohort-level multiple, not just one company's quarter.

**3. Sequencing for same-day or hours-apart prints.** If two prints fall the same day (or one AM and one AH), neither informs the other in a usable way — by the time you process the first, the second is already pricing. Treat them as independent and rely on the per-print plans. Don't try to "wait and see how the first one trades" intraday; orders set ahead of time execute regardless.

## Operational checklist (run every week with ≥2 prints in 5 TD)

1. List all portfolio-relevant prints in the next 5 trading days.
2. Group them by cohort. Note same-cohort dependencies and ordering.
3. Produce the per-print plan for each (scenario ladder, options-implied move, pre-commit orders).
4. Layer this playbook on top: allocate the earnings-week cash bucket and cap each print's add as a fraction; mark which prints inform which; pre-write the if/then for negative-print scenarios on each later same-cohort print.
5. After each print fires, before the next same-cohort print, re-derive the planned add given the earlier print's *market reaction*, not just headline beat/miss. A beat that closes -4% reads cohort-negative; a small miss that closes +3% reads cohort-positive.

## What this playbook is *not*

- Not a substitute for the per-print plan, which produces the scenario ladder, the options-implied move check, and the GTC orders. This file is the cross-print layer.
- Not a model. It's a coordination checklist. The judgment call ("is this cohort-positive enough to upsize?") still happens against full context, not from a formula.

---
# References
- [[catalyst-payoff-shape-sizing]] — per-print sizing geometry
- [[macro-cohort-confirmation]] — the cohort-confirmation gate that drives axis 2
- [[extended-with-vs-without-catalyst]] — for how to read a stock's reaction to its *own* print before the next same-cohort print
