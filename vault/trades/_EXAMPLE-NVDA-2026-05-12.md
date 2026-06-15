---
type: trade
instrument: NVDA
direction: long
tradeStatus: OPEN
entries:
  - size: 50
    price: 118.40
    time: 2026-05-12T14:32:00
  - size: 25
    price: 112.10
    time: 2026-05-28T15:01:00
exits:
  - size: 25
    price: 131.20
    time: 2026-06-09T18:45:00
tags: []
images: []
---

EXAMPLE / TEMPLATE — not a real position. Delete this file (or keep it as a
reference) once you start logging your own trades.

This shows the trade-log schema that `get_positions.py` reads. One file per
trade. The parser only looks at the frontmatter; the body is free notes.

Field notes:

- `type: trade` and `tradeStatus: OPEN` are the filters — the parser ignores
  any file that isn't a `type: trade`, and only counts `OPEN` trades toward
  open positions.
- `entries` / `exits` are lists. Add a tranche by appending an item to
  `entries`; trim by appending to `exits`. shares_held = sum(entries.size) −
  sum(exits.size), avg cost is entry-weighted, realized P&L is booked on the
  exited portion against that avg cost.
- Flip `tradeStatus: CLOSED` once the position is fully exited (shares_held
  hits 0). Closed trades drop out of the open-position roster.
- `time` accepts `YYYY-MM-DDTHH:MM:SS`, `YYYY-MM-DDTHH:MM`, or `YYYY-MM-DD`.
- `tags` / `images` are optional (kept here for Journalit-export parity).

You don't need to edit this by hand: in a Claude Code session, just say
"I bought 50 NVDA at 118.40" and the `log-trade` skill writes/updates the
right file for you. This format is also what the Journalit Obsidian plugin
exports, so Journalit users can keep using it — point the parser at the
`!Journalit/` folder via `--trades-dir !Journalit`.
