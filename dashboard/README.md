# Trading Journal Dashboard

Static, read-only dashboard generated from the vault's canonical Markdown and
JSON files. The output is a single `index.html`, so it can be opened locally or
published as a GitHub Pages site from a separate public repo.

## Public Output Rule

Treat `dashboard/index.html` as public internet output. Do not add secrets,
API keys, tokens, OAuth details, private account identifiers, email addresses,
or other obviously sensitive personal data to the dashboard data model or UI.
If a future field is useful but sensitive, keep it in the private vault/report
and link or summarize it without exposing the sensitive value.

## Refresh Locally

Run from the repo root:

```powershell
python dashboard\generate_dashboard.py
```

Then open `dashboard/index.html` in a browser.

## Publish To GitHub Pages

Recommended shape: create a separate public repo just for the dashboard, then
copy these files into that repo root:

- `dashboard/index.html`
- `dashboard/.nojekyll`

In the new repo, enable Pages from `Settings -> Pages -> Deploy from a branch`,
using the root of `main`. The generated HTML embeds the dashboard data, so the
published repo does not need the private vault files.

After the separate Pages repo exists, publish with:

```powershell
python dashboard\deploy_pages.py
```

By default this expects the Pages checkout at `..\trading-dashboard`. Override
with:

```powershell
python dashboard\deploy_pages.py --pages-repo C:\path\to\trading-dashboard
```

The deploy script regenerates `dashboard/index.html`, scans for obvious
sensitive strings, copies `index.html` and `.nojekyll` into the Pages repo,
commits, and pushes. GitHub Pages redeploys automatically after that push.

## Automatic Publish

`.github/workflows/publish-dashboard-pages.yml` runs on every push to `main`.
That covers VPS daily, weekly, intraday, and local commits once they land in
the private repo. The workflow regenerates the dashboard, runs the same
sensitive-output guard, clones the public Pages repo, and pushes only
`index.html` and `.nojekyll`.

One-time setup: create a fine-grained GitHub token with `Contents: Read and
write` access only to `your-username/trading-dashboard`, then add it to the
private `trading-journal` repo as an Actions secret:

```text
DASHBOARD_PAGES_TOKEN
```

There is also a direct VPS fallback in `/opt/trading-journal/scripts/daily-news.sh`.
If `/opt/trading-journal/trading-dashboard` exists, the wrapper can publish from
there after the daily-news run. Default VPS Pages checkout:

```text
/opt/trading-journal/trading-dashboard
```

If that checkout does not exist, the daily job logs a skip and still succeeds.
Set `DASHBOARD_PAGES_DEPLOY_DISABLED=1` in `/opt/trading-journal/secrets.env` to
turn off direct VPS deploys without editing the wrapper.

## Inputs

- `vault/watchlist.md`
- `vault/price-triggers.md`
- `vault/ipo-calendar.md`
- `vault/deep-dives/_verdicts.md`
- `vault/reports/intraday-alerts/news-*.md`
- `vault/reports/daily/*.md`
- `trigger_results_watchlist.json`
- `trigger_results_broader.json`
- `upcoming_earnings.json`
- `verdict_drift.json`

Trigger result JSON is used only when it is newer than the source trigger
tables. If it is stale, the dashboard shows current trigger definitions and
surfaces a freshness warning.
