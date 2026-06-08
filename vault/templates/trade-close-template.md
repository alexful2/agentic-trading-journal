# <TICKER> — Closed <YYYY-MM-DD>

Status: #trade-close
Tags: #trade #<TICKER>

Related: [[<TICKER> - <ENTRY_DATE> Buy]]

---

## Trade Summary

- **Entry:** $X.XX on YYYY-MM-DD
- **Exit:** $X.XX on YYYY-MM-DD
- **Holding period:** N days
- **P&L:** +/-X.X% (absolute: $X)
- **Position size at entry:** $X (N shares)

## Thesis Recap

**Going in:** *one-paragraph summary of the thesis from the buy note — what I believed would happen and why.*

**Deep-dive verdicts during tenure:**
- YYYY-MM-DD — VERDICT (HOLD / ADD / REDUCE / WATCH) — one-line summary
- ...

**Severity ≥4 alerts during tenure:**
- YYYY-MM-DD — one-line summary from the daily report
- ...

**What actually happened:** *one-paragraph narrative of the holding period — the arc, not a day-by-day.*

## Peer Performance

Peer basket declared at entry in [[<TICKER> - <ENTRY_DATE> Buy]]:

| Ticker | Role in basket | Return over holding period | Driving event |
|---|---|---|---|
| <TICKER> (mine) | — | +/-X.X% | — |
| <PEER1> | *why it qualifies — copied from buy note* | +/-X.X% | *one-line event that moved it most* |
| <PEER2> | *why it qualifies* | +/-X.X% | *one-line event* |
| <PEER3> | *why it qualifies* | +/-X.X% | *one-line event* |

- **Peer median return:** +/-X.X%
- **Relative performance (mine − median):** +/-X.X pp

## Attribution: Alpha vs. Beta

- **Result:** *beat / matched / lagged the peer median*
- **If beat:** *what was idiosyncratic to this name — product, contract, earnings, management, positioning?*
- **If lagged:** *what did peers have that this one didn't?*
- **Thesis check:** *did the trade work (or fail) for the reason stated in the buy note, or for unrelated reasons?*

## Calibration Notes

**System vs. reality:**
- Where did deep-dive verdicts match what actually happened? Where did they miss?
- Where did daily-alert severity scores over- or under-weight events that turned out to matter?
- Were the alerts that flagged the eventual exit condition accurate, late, or missing?

**Emotional calibration:**
- Did I follow the plan from the buy note, or did fear/FOMO drive the timing?
- Which of my known patterns showed up? (dip buyer / extended-run chaser / "give it a little more time" / FOMO re-entry / etc.)

## Lessons

- **Library implications:** *does any thesis in `vault/library/` need updating? New principle worth articulating?*
- **Process implications:** *peer basket well-chosen? Exit condition clearly stated at entry? Better buy-note fields needed?*
- **Candidate vault changes:** *flag for the next `vault-curator` run — e.g., "update [[Amazon Thesis]] to reflect X".*

---

**Not investment advice.** This is a post-mortem for calibration and learning.
