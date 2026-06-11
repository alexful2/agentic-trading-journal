# Quarterly Review Template

Output path: `vault/reports/quarterly/YYYY-QN.md`

---

```markdown
---
date: {{YYYY-MM-DD}}
quarter: {{YYYY-QN}}
type: quarterly-system-review
closes_analyzed: {{count}}
reports_scanned: {{count}}
{{note: partial-quarter run (…) — only when run mid-quarter; omit on
full-quarter runs}}
---

# Quarterly System Review — {{YYYY-QN}}

> This report audits the trading-journal system, not the portfolio. It
> checks whether prior verdicts and severities aligned with outcomes,
> and whether the system's framing is evolving or recycling.
{{If partial-quarter: add a second blockquote paragraph — execution
date and which inputs aren't captured yet. A later end-of-quarter
rerun overwrites this file.}}

---

## Calibration Pass

{{If no closed trades AND no pre-earnings prints AND no
execution-thesis refreshes this quarter: "No closed trades,
pre-earnings runs, or execution-thesis refreshes this quarter —
calibration pass skipped." Otherwise run the subsections that have
substrate and say plainly which ones don't.}}

### Closed trades & verdict alignment

| Ticker | Close date | Outcome | Standing verdict | Verdict date | Aligned? |
|--------|-----------|---------|-------------------|--------------|----------|
| {{TICKER}} | {{YYYY-MM-DD}} | {{win/loss/breakeven, pnl%}} | {{HOLD/ADD/REDUCE/WATCH}} | {{YYYY-MM-DD}} | {{yes/no/partial}} |

### Severity alignment

{{For each close: did sev ≥3 alerts during the trade's tenure flag the
news that actually mattered? Or did key events get under-scored, over-
scored, or missed? One bullet per close.}}

### Aggregate patterns

{{If 3+ closes: look for systematic bias, timing pattern, or structural
miss. If 1–2 closes: "One trade is not a pattern — observations only."
If 0 closes: omit this section.}}

### Pre-earnings calibration

{{Omit entire subsection if no pre-earnings files with print_date in the
quarter.}}

| Ticker | Print | Realized post-print move | Scenario matched | Ladder probability | Pre-commit action | Plan executed? |
|--------|-------|--------------------------|------------------|--------------------|--------------------|-----------------|
| {{TICKER}} | {{YYYY-MM-DD}} | {{±X.X%}} | {{scenario name}} | {{XX%}} | {{order shape}} | {{yes/no/partial/unverified}} |

**Aggregate signal:**
{{If ≥3 runs: are ladder probabilities calibrated, is the pre-commit plan
followed, did rotation-check verdicts play out? If <3 runs: "Too few
pre-earnings runs for aggregate calibration — individual rows only."}}

### Execution-thesis calibration

{{Omit entire subsection if no execution-thesis.md refreshes in the
quarter.}}

| Ticker | Refresh date | H2 this refresh | H2 prior refresh | 30/60/90 items resolved | Audit verdict |
|--------|--------------|------------------|------------------|--------------------------|----------------|
| {{TICKER}} | {{YYYY-MM-DD}} | {{cleared/not proposed/retracted}} | {{cleared/not proposed/retracted/n-a}} | {{count + 1-line note}} | {{clean/material corrections/H2 retracted/not audited}} |

**Aggregate signal:**
{{If ≥3 refreshes: H2 retraction rate (flag >30% as gate-too-lenient),
watch-list hit rate, audit recurrence pattern. If <3: "Too few
execution-thesis refreshes for aggregate calibration — individual rows
only."}}

---

## Echo-Chamber Audit

{{3–5 one-line observations from scanning the last ~90 days of daily
alerts, weekly reviews, and deep-dives. Focus on framing drift,
verdict stability, severity clustering, and self-reference.}}

- **Framing drift:** {{…}}
- **Verdict stability:** {{…}}
- **Severity clustering:** {{…}}
- **Self-reference:** {{…}}

<!-- If nothing notable: "No significant drift observed." -->

---

## Prior-Quarter Follow-Through

{{One bullet per Key Takeaway in the previous quarterly report:
**resolved** / **recurred** / **not assessable**, with a one-line
justification. Recurred-twice findings name the specific prompt,
template, or script to change. First-ever run: "No prior quarterly
report — follow-through starts next quarter."}}

- {{prior takeaway}} — {{resolved/recurred/not assessable}}: {{…}}

---

## Key Takeaways

<!-- 3–5 bullets. What should the user know? What, if anything, should
     change in how the system operates? -->

- {{…}}
- {{…}}
- {{…}}

---

*Generated: {{timestamp}}* | *Not investment advice. This is a system
review, not a portfolio review.*
```

## Rules

1. **Observations, not prescriptions.** The output flags patterns. The
   user decides whether to change the system in response.
2. **Thin inputs → thin outputs.** Do not fabricate patterns. If inputs
   are sparse, the report is short.
3. **No wikilinks to specific tickers in aggregate sections.** This is a
   system review; keep ticker-level detail in the calibration table.
4. **Writes only to `reports/quarterly/`.** Never touches `library/`,
   `notes/`, or other report folders.
