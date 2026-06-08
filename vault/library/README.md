# library/

This is the reference layer of the vault: principles, decision frameworks, and
worldview. Skills read it during context-loading to reason in *your* frame, and
the deep dive reads `research/` selectively.

**What ships here is example content.** The framework files below are
depersonalized examples — they show the *form* of a written-down decision rule
that the skills can apply by name. Keep the ones that fit how you actually think,
edit them, and write your own. The system gets sharper the more of your real
reasoning lives here.

## Example frameworks

| File | What it captures |
|------|------------------|
| `Opportunity-cost lens.md` | Holding = re-buying at today's price; partial rotations beat all-or-nothing. |
| `extended-with-vs-without-catalyst.md` | "Extended" is two different signals — repricing vs. FOMO — and only the business change tells them apart. |
| `catalyst-payoff-shape-sizing.md` | Size into a catalyst by its payoff *shape*, not the direction you hope it moves. |
| `macro-cohort-confirmation.md` | Idiosyncratic weakness is information; cohort weakness is liquidity. Add only on the second. |
| `Wait-for-deal thesis.md` | A worked example of a *sector-level* thesis written down for the skills to apply. |
| `ai-infra-thesis-kill-switches.md` | The three numerical thresholds that would actually break the AI-infra cycle — vs. noise. |
| `ai-capex-payback-window.md` | The capex ROIC J-curve: FCF compression is the *expected* shape, not a thesis break. Size to the payback horizon. |
| `orchestration-vs-substrate.md` | Where the AI margin lives — physical substrate vs. the intelligence layer — and who's hedged across both. |
| `agentic-ai-compute-mix.md` | Agentic workloads shift the compute *mix* toward CPU without eating GPU demand — first-party ARM silicon is the tell. |
| `ouroboros-economy-circular-financing.md` | AI dollars circulate intra-cohort; ranks which names are most fragile if external revenue lags. |
| `permitting-as-binding-constraint.md` | Political consent can't be bought — pre-permitted footprints earn a scarcity premium; the macro still gets built. |
| `AI Energy Thesis.md` | Power is the binding constraint; on-site generation (BTM gas now, SMRs later) has durable pricing power. |
| `warrant-conditionality-equity-announcements.md` | Announced "equity injections" are mostly option value — size off committed cash, read the signal separately. |
| `pre-earnings-cross-print-playbook.md` | Coordinating cash, cohort-information flow, and sequencing when ≥2 prints land in ~5 trading days. |
| `Nvidia - AI Cycle Durability and GPU Economics.md` | A labeled *example* of a single-name thesis — mechanical claim, confirm/break conditions, dated refresh. |

## `research/` — empirical-priors catalog

A small catalog (C1–C15) distilling peer-reviewed finance findings into decision
priors, each with a strict verify-then-stamp citation discipline. See
[`research/README.md`](./research/README.md) for what it is and how to grow your
own.

## How skills use this folder

- `news-analyst`, `weekly-review`, `stock-deep-dive` load the frameworks as
  context and can apply named ones (`[[Opportunity-cost lens]]`).
- `stock-deep-dive` pulls relevant `research/` priors into its reasoning.
- `vault-curator` flags implicit beliefs in your `notes/` that are worth
  promoting into a framework here, and flags stale entries for review.
- Filled-in trade-close arcs also live here (`TICKER - YYYY-MM-DD Close.md`),
  read by `quarterly-review` for calibration.
