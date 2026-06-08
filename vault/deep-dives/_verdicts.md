# Deep-dive verdict ledger

> Not investment advice.

Append-only log of deep-dive verdicts. Row per single-ticker deep-dive at the moment it was written.
Comparison files are not logged here. Used by `check_verdict_drift.py` (daily) and `quarterly-review` (calibration).

`Break-even P` = the Implied Expectations break-even probability (Step 4c) at verdict time — captured here because deep-dive files are auto-deleted when superseded. `—` when the dive named no quantifiable break-even. Feeds a future calibration pass once enough verdicts resolve (not yet — n too small). `--bootstrap` rebuilds from deep-dive files and resets this column to `—`.

Maintained by `.claude/scripts/log_verdict.py`. To rebuild: `python .claude/scripts/log_verdict.py --bootstrap`.

| Date | Ticker | Verdict | Price at verdict | Deep-dive file | Break-even P |
| --- | --- | --- | --- | --- | --- |
| 2026-04-14 | AMZN | HOLD | $249.02 | `AMZN-2026-04-14` |
| 2026-04-24 | APLD | WATCH | $34.98 | `APLD-2026-04-24` |
| 2026-04-14 | BE | WATCH | $219.03 | `BE-2026-04-14` |
| 2026-04-20 | CIFR | WATCH | $19.18 | `CIFR-2026-04-20` |
| 2026-04-22 | CORZ | WATCH | $21.45 | `CORZ-2026-04-22` |
| 2026-04-22 | CRWV | WATCH | $124.25 | `CRWV-2026-04-22` |
| 2026-04-24 | EOSE | WATCH | $7.67 | `EOSE-2026-04-24` |
| 2026-04-15 | HNGE | HOLD | $41.47 | `HNGE-2026-04-15` |
| 2026-04-18 | IREN | WATCH | $48.12 | `IREN-2026-04-18` |
| 2026-04-20 | NBIS | WATCH | $158.59 | `NBIS-2026-04-20` |
| 2026-04-23 | RIVN | WATCH | $17.13 | `RIVN-2026-04-23` |
| 2026-04-23 | RKLB | WATCH | $84.60 | `RKLB-2026-04-23` |
| 2026-04-26 | TWST | WATCH | $60.94 | `TWST-2026-04-26` |
| 2026-04-26 | TEM | WATCH | $52.12 | `TEM-2026-04-26` |
| 2026-04-28 | LITE | WATCH | $797.07 | `LITE-2026-04-28` |
| 2026-04-29 | IREN | ADD | $42.55 | `IREN-2026-04-29` |
| 2026-04-29 | AMZN | HOLD | $252.00 | `AMZN-2026-04-29` |
| 2026-04-30 | SNDK | WATCH | $1096.51 | `SNDK-2026-04-30` |
| 2026-04-30 | NBIS | ADD | $138.23 | `NBIS-2026-04-30` |
| 2026-04-30 | INTC | WATCH | $94.48 | `INTC-2026-04-30` |
| 2026-05-02 | IREN | ADD | $45.66 | `IREN-2026-05-02` |
| 2026-05-03 | HNGE | HOLD | $45.43 | `HNGE-2026-05-03` |
| 2026-05-03 | BE | WATCH | $290.52 | `BE-2026-05-03` |
| 2026-05-07 | CORZ | WATCH | $22.36 | `CORZ-2026-05-07` |
| 2026-05-07 | IREN | HOLD | $56.85 | `IREN-2026-05-07` |
| 2026-05-07 | APLD | WATCH | $41.53 | `APLD-2026-05-07` |
| 2026-05-10 | AMZN | HOLD | $272.68 | `AMZN-2026-05-10` |
| 2026-05-11 | HNGE | HOLD | $54.74 | `HNGE-2026-05-12` |
| 2026-05-12 | CRWV | ADD | $102.94 | `CRWV-2026-05-12` |
| 2026-05-13 | TEM | WATCH | $46.23 | `TEM-2026-05-13` |
| 2026-05-13 | NBIS | HOLD | $208.34 | `NBIS-2026-05-13` |
| 2026-05-14 | CBRS | WATCH | $340.50 | `CBRS-2026-05-14` |
| 2026-05-15 | TWST | ADD | $48.43 | `TWST-2026-05-15` |
| 2026-05-15 | VIVO | WATCH | $4.54 | `VIVO-2026-05-15` |
| 2026-05-18 | IREN | HOLD | $49.14 | `IREN-2026-05-18` |
| 2026-05-19 | TE | WATCH | $6.88 | `TE-2026-05-19` |
| 2026-05-19 | EOSE | WATCH | $6.88 | `EOSE-2026-05-19` |
| 2026-05-19 | DGXX | WATCH | $7.72 | `DGXX-2026-05-19` |
| 2026-05-19 | HNGE | HOLD | $54.96 | `HNGE-2026-05-19` |
| 2026-05-19 | RKLB | WATCH | $127.31 | `RKLB-2026-05-19` |
| 2026-05-19 | APLD | WATCH | $36.62 | `APLD-2026-05-19` |
| 2026-05-30 | BE | WATCH | $285.00 | `BE-2026-05-30` |
| 2026-05-30 | AMZN | HOLD | $270.64 | `AMZN-2026-05-30` |
| 2026-05-30 | CORZ | WATCH | $26.85 | `CORZ-2026-05-30` |
| 2026-05-31 | IREN | HOLD | $63.54 | `IREN-2026-05-31` |
| 2026-05-31 | MARA | WATCH | $14.38 | `MARA-2026-05-31` |
| 2026-05-31 | NBIS | HOLD | $231.09 | `NBIS-2026-05-31` |
| 2026-06-05 | NBIS | ADD | $227.76 | `NBIS-2026-06-05` |
| 2026-06-06 | CRWV | HOLD | $100.39 | `CRWV-2026-06-06` |
| 2026-06-07 | IREN | HOLD | $54.35 | `IREN-2026-06-07` | 73% |
