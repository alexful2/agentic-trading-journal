# Suggestion Template

Output path: `vault/suggestions/wiki-YYYY-WW.md`

---

```markdown
---
date: {{YYYY-MM-DD}}
week: {{YYYY-WW}}
type: vault-curation
status: pending
library_files_read: {{count}}
notes_files_read: {{count}}
web_searches_run: {{count}}
suggestions_count: {{count}}
---

<!--
Status field — flip this manually when you've reviewed the file:
  pending     — items still need triage (default for new files)
  handled     — promoted/acted on; curator should stop re-flagging
  dismissed   — reviewed and rejected; don't re-suggest
  superseded  — a newer wiki-YYYY-WW.md carries forward what's still relevant
Curator skips files where status != pending when looking at carry-forward.
-->


# Weekly Vault Curation — Week of {{Month DD, YYYY}}

> Suggestions only — nothing is written automatically.
> **A checked `- [x]` box means: "I want this done OR it's already been done."**
>
> **Optional:** under any checked box you can indent one or more bullets
> with item-specific instructions for the implementation agent. Example:
> ```
> - [x] **Promote to** `library/foo.md`
>     - Keep under 80 lines, lead with the cohort-fragility ranking, skip the macro stats
> ```
> No nested bullet = use the default action on the checkbox line.
>
> Run an agent with: "Go through `vault/vault-suggestions/wiki-{{YYYY-WW}}.md`
> and implement everything I've checked. For each checked item: first read
> any nested bullets under it as item-specific instructions; then verify
> whether the action has already been done — if so, skip it (and leave a
> one-line note in the file). Otherwise, do it. Make all files relatively
> concise." Unticked items are ignored entirely.
>
> Macro context used for this run: `[[weekly-review: {{YYYY-WW}}]]` (or
> "no weekly-review found this week" if absent).

---

## Part 1: Library Suggestions

### New Concepts Worth Adding

<!-- Sourced from web radar. Only include if genuinely novel vs. current library/. -->

#### {{Concept Title}}
- [ ] **Promote to** `library/{{suggested-kebab-case-filename}}.md`
    - 

**Source:** {{essay/post title — Author — Publication — Date}}
**Why it's new:** {{1 sentence. What does this add that isn't already in library/?}}
**Synthesis:** {{2 sentences max distilling the idea + how it connects to existing worldview.}}

<!-- Repeat #### blocks back-to-back; NO `---` between items in the same section. -->
<!-- If nothing found: "No standout material surfaced this week." -->

---

### Implicit Beliefs Worth Articulating

<!-- Patterns found across notes/ that recur but aren't written down in library/. -->

#### {{Belief / Pattern Title}}
- [ ] **Promote to** `library/{{suggested-kebab-case-filename}}.md`
    - 

**Seen in:** {{[[note-file-1]], [[note-file-2]], ...}}
**Draft principle:** {{2-3 sentences max. A draft of how this could read as a
library principle, not a description.}}

<!-- Repeat for each. If nothing recurring found: skip this section. -->

---

### Possibly Stale Library Entries

<!-- Library files that may need updating given recent notes or this week's macro picture. -->

#### [[{{library-filename}}]]
- [ ] **Update entry** — {{specific thing to change in 1 short clause}}
    - 

{{Why it might be stale. 1-2 sentences. Name the specific thing that's changed.}}

<!-- Repeat for each. If nothing stale: skip this section. -->

---

### Trade Consolidation Candidates

<!-- Notes in notes/ that reference closed Journalit trades. -->

#### [[{{note-filename}}]]
- [ ] **Write arc to** `library/{{ticker}}-trade-arc.md`
    - 

**Journalit trade:** {{TICKER-DDMMYY-T1}} — `tradeStatus: CLOSED`
**Notes involved:** {{list all related note files by date}}
**Suggested arc:**
- Entry ({{date}}): {{thesis at entry}}
- During hold: {{key updates / pivots}}
- Exit ({{date}}): {{why sold, outcome}}
- Lesson: {{one durable takeaway}}

<!-- If no closed trades with open notes: skip this section. -->

---

## Part 2: Opportunity Radar

> Stocks not on the watchlist that surfaced from this week's thesis screener.
> Research prompts, not buy signals. Not investment advice.

### Wait-for-Deal Candidates

<!-- Companies fitting the wait-for-deal thesis. -->

#### {{Company Name}} ({{TICKER or "pre-IPO"}})
- [ ] **Run** `deep-dive {{TICKER}}`  *(or: add to watchlist Tier 3 / build dossier)*
    - 

**What they do:** {{one sentence — specific product/service.}}
**Why they fit:** {{why an AI lab would want this — compute lane, energy type, scale.}}
**Deal readiness:** {{existing relationships, lab customers, or capacity hints.}}
**Source:** {{search result or article URL}}

<!-- Repeat for each candidate. Max 3. If nothing fits: "No candidates this week." -->

---

### IPO Radar

<!-- Upcoming IPOs in AI compute / energy / infrastructure. -->

#### {{Company Name}} ({{TICKER or "pre-IPO"}})
- [ ] **Add to [[ipo-calendar]]** *(or: build pre-IPO dossier)*
    - 

{{Expected window + one to three sentences on what they do, why relevant, key facts. Source link.}}

<!-- Repeat for each. If nothing found: "No relevant IPOs on radar this week." -->

---

## Vault Health

### Coverage Gaps

#### {{Gap title}}
- [ ] **{{Concrete action}}** — {{target filename or "none, demote/watch"}}
    - 

{{1-2 sentences: what's missing, why it's a gap now.}}

<!-- Repeat for each. Or skip if "None identified." -->

---

### Notes Needing Attention

#### [[{{note-filename}}]]
- [ ] **{{Concrete action}}** — {{e.g. "Mark superseded with pointer to [[newer-note]]"}}
    - 

{{1-2 sentences: what's incomplete / contradicting / superseded.}}

<!-- Repeat for each. Or skip if "None identified." -->

---

*Generated: {{timestamp}}*
```

## Rules

1. **Wikilinks:** Use `[[filename]]` when referencing vault files.
2. **Checkbox per recommendation.** Every actionable suggestion gets one
   `- [ ]` line naming the concrete action and target file path. No
   checkbox = not actionable / context only.
   **Semantics:** A checked `- [x]` means *"I want this done OR it's
   already been done."* The implementation agent must verify state per
   item before acting — if the target already exists, skip with a note
   rather than overwrite. Unticked = ignored.
   **Empty placeholder:** seed a `    - ` (4-space indent + dash + space)
   line directly under every checkbox. This gives the user a ready
   indent point to type item-specific instructions if they decide to
   tick the box. If they leave it empty, the implementation agent
   ignores it.
   **Nested-bullet override:** when the user fills in that placeholder
   (or adds more), the implementation agent reads any non-empty
   indented bullets following a `[x]` line as item-specific instructions
   that override or refine the default action (length, framing, what to
   emphasize/skip, file path override).
3. **Layout: heading-style for every suggestion, no `---` between items
   within a section.** Each suggestion gets its own `#### {{Title}}`
   heading, then the `- [ ]` checkbox + placeholder, then a body
   paragraph. Repeat blocks back-to-back. `---` horizontal rules ONLY
   appear between `###` category sections (and at `##` Part boundaries),
   never between items inside the same category. This keeps the
   placeholder visually adjacent to its checkbox.
4. **Suggestions only.** Frame as "worth considering," not directives.
5. **Sources required.** Every web radar suggestion must have a real source.
6. **Brevity.** Keep each suggestion to ~3-5 lines of body text after the
   checkbox. The whole file should read in under 5 minutes. No multi-paragraph
   syntheses — if it can't fit in 2-3 sentences, it's a deep-dive, not a
   suggestion.
7. **Honest null state.** If nothing compelling surfaced, say so clearly.
   A short honest report beats a padded one.
