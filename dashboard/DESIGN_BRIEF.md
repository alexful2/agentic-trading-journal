# Dashboard Design Brief

Design a polished, read-only trading command center for a personal research vault. The dashboard should feel like a quiet professional analyst workstation, not a marketing site and not an Obsidian note rendered in a browser.

Priorities:

1. Put the highest attention items first.
   - Lead with a compact market brief: critical news, active trigger state, upcoming event pressure, and recent research activity.
   - Make it obvious what deserves attention without forcing the user to read every table.

2. Organize by workflow.
   - "Action" should show critical news, price trigger radar, and planned tranches.
   - "Calendar" should show earnings and IPOs.
   - "Research" should show watchlist tiers and recent vault activity.
   - "System" should show source freshness and stale snapshot notes.

3. Keep the UI dense but calm.
   - Use restrained color for severity and status, not decoration.
   - Avoid large cards that waste space.
   - Use tables where comparison matters and compact cards where summaries matter.

4. Make read-only interactivity useful.
   - Search should filter all visible sections by ticker or keyword.
   - Tabs should change the working context without hiding essential global summary metrics.
   - Sections should display empty states cleanly.

5. Preserve trust in the data.
   - Show source freshness.
   - Make stale price-check snapshots visible as a system note instead of silently implying live state.
   - Keep canonical source files untouched; the dashboard is only a generated view.

6. Visual direction.
   - Professional trading/research desk.
   - Warm off-white canvas, ink text, restrained green/blue/gold/red status colors.
   - Clear section headers, compact metrics, strong alignment, minimal ornament.
   - Mobile must remain readable without overlapping or horizontal layout breakage.
