#!/usr/bin/env python3
"""Build vault/DASHBOARD.md — single-pane summary of the trading vault.

Pure file-reads, no network, no LLM. Designed to run after each
daily-news.service / intraday-*.service tick (cheap; <1s). Output is
markdown with Obsidian-flavored callouts and tables, intended to be
opened in Obsidian as a homepage.

Inputs (read-only):
  vault/watchlist.md
  vault/price-triggers.md
  vault/ipo-calendar.md
  vault/reports/daily/YYYY-MM-DD.md           (latest 1-2)
  vault/reports/intraday-alerts/YYYY-MM-DD.md (today + yesterday — fired triggers)
  vault/reports/intraday-alerts/news-YYYY-MM-DD.md (today + yesterday — sev>=4 PUSH)
  vault/reports/pre-earnings/*.md
  vault/reports/pre-ipo/*.md
  vault/deep-dives/*.md                        (most recent per ticker for verdict)

Output:
  vault/DASHBOARD.md (overwritten on every run)
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "vault"
OUT = VAULT / "DASHBOARD.md"

NOW = datetime.now().astimezone()
TODAY = NOW.date()
RECENT_FILES_HOURS = 48
CRITICAL_NEWS_HOURS = 24


# ---------- table parsing ----------

def find_section(text: str, heading: str) -> str:
    """Return the body of `## heading` (or `### heading`) up to the next
    heading at the same-or-shallower depth. Empty string if not found."""
    pattern = re.compile(
        rf"^(#{{1,6}})\s+{re.escape(heading)}\s*$", re.MULTILINE
    )
    m = pattern.search(text)
    if not m:
        return ""
    depth = len(m.group(1))
    start = m.end()
    end_pat = re.compile(rf"^#{{1,{depth}}}\s+\S", re.MULTILINE)
    m2 = end_pat.search(text, pos=start)
    return text[start : m2.start()] if m2 else text[start:]


def parse_md_table(body: str) -> list[dict[str, str]]:
    """Parse the first markdown pipe-table in `body` into dicts."""
    lines = [ln.rstrip() for ln in body.splitlines()]
    rows: list[list[str]] = []
    in_table = False
    for ln in lines:
        if ln.lstrip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows.append(cells)
            in_table = True
        elif in_table:
            break
    if len(rows) < 2:
        return []
    header = rows[0]
    # row 1 is the |---|---| separator; data starts at index 2
    data = rows[2:]
    return [dict(zip(header, r)) for r in data if len(r) == len(header)]


# ---------- watchlist / triggers / tranches ----------

@dataclass
class TriggerRow:
    ticker: str
    buy_below: str
    trim_above: str
    funded_by: str
    prefer_over: str
    last_reviewed: str
    note: str
    source: str = ""


@dataclass
class TrancheRow:
    ticker: str
    action: str
    size: str
    at_price: str
    expires: str
    order: str
    note: str


def load_watchlist():
    text = (VAULT / "watchlist.md").read_text(encoding="utf-8")
    tier1 = parse_md_table(find_section(text, "Tier 1 — Core Holdings"))
    tier2 = parse_md_table(find_section(text, "Tier 2 — Active Watchlist"))
    tier3 = parse_md_table(find_section(text, "Tier 3 — Peripheral Interest"))
    triggers_raw = parse_md_table(find_section(text, "Price Triggers"))
    tranches_raw = parse_md_table(find_section(text, "Planned Tranches"))

    triggers = [
        TriggerRow(
            ticker=r.get("Ticker", ""),
            buy_below=r.get("Buy Below", ""),
            trim_above=r.get("Trim Above", ""),
            funded_by=r.get("Funded-by", ""),
            prefer_over=r.get("Prefer-over", ""),
            last_reviewed=r.get("Last Reviewed", ""),
            note=r.get("Note", ""),
        )
        for r in triggers_raw
    ]
    tranches = [
        TrancheRow(
            ticker=r.get("Ticker", ""),
            action=r.get("Action", ""),
            size=r.get("Size", ""),
            at_price=r.get("At Price", ""),
            expires=r.get("Expires", ""),
            order=r.get("Order", ""),
            note=r.get("Note", ""),
        )
        for r in tranches_raw
    ]
    return tier1, tier2, tier3, triggers, tranches


def load_broader_triggers() -> list[TriggerRow]:
    text = (VAULT / "price-triggers.md").read_text(encoding="utf-8")
    rows = parse_md_table(find_section(text, "Price Triggers"))
    return [
        TriggerRow(
            ticker=r.get("Ticker", ""),
            buy_below=r.get("Buy Below", ""),
            trim_above=r.get("Trim Above", ""),
            funded_by=r.get("Funded-by", ""),
            prefer_over=r.get("Prefer-over", ""),
            last_reviewed=r.get("Last Reviewed", ""),
            note=r.get("Note", ""),
            source=r.get("Source", ""),
        )
        for r in rows
    ]


def is_stale(last_reviewed: str, days: int = 30) -> bool:
    try:
        d = datetime.strptime(last_reviewed.strip(), "%Y-%m-%d").date()
    except ValueError:
        return False
    return (TODAY - d).days > days


def is_expired(expires: str) -> bool:
    try:
        d = datetime.strptime(expires.strip(), "%Y-%m-%d").date()
    except ValueError:
        return False
    return d < TODAY


# ---------- IPO calendar ----------

def load_ipo_calendar() -> list[dict[str, str]]:
    text = (VAULT / "ipo-calendar.md").read_text(encoding="utf-8")
    return parse_md_table(find_section(text, "Calendar"))


# ---------- daily report ----------

@dataclass
class DailyItem:
    title: str
    action: str  # one-line action snippet


def latest_daily_report() -> tuple[Path | None, str]:
    daily_dir = VAULT / "reports" / "daily"
    if not daily_dir.exists():
        return None, ""
    files = sorted(
        [p for p in daily_dir.glob("*.md") if re.match(r"\d{4}-\d{2}-\d{2}\.md", p.name)],
        reverse=True,
    )
    if not files:
        return None, ""
    p = files[0]
    return p, p.read_text(encoding="utf-8")


def parse_daily_items(text: str) -> list[DailyItem]:
    """Extract `### {Title}` items and the line under `**Action:**`."""
    items: list[DailyItem] = []
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)
    for blk in blocks[1:]:
        title_line, _, rest = blk.partition("\n")
        title = title_line.strip()
        # stop at next thematic-break section header
        rest = rest.split("\n## ", 1)[0]
        action = ""
        for ln in rest.splitlines():
            if ln.strip().lower().startswith("- **action:**"):
                action = ln.split("**", 2)[-1].lstrip(":").strip()
                action = re.sub(r"\*\*", "", action).strip()
                break
        items.append(DailyItem(title=title, action=action))
    return items


def _bullets(body: str) -> list[str]:
    out = []
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith("- ") or s.startswith("* "):
            out.append(s[2:].strip())
    return out


def parse_active_earnings(text: str) -> list[str]:
    return _bullets(find_section(text, "Active Earnings Windows"))


def parse_active_ipos(text: str) -> list[str]:
    return _bullets(find_section(text, "Active IPO Windows"))


def parse_verdict_drift(text: str) -> list[str]:
    return _bullets(find_section(text, "Verdict Drift"))


def parse_broader_fires(text: str) -> list[str]:
    return _bullets(find_section(text, "Broader Price Triggers"))


# ---------- intraday alerts ----------

@dataclass
class IntradayNewsItem:
    ticker: str
    sev: int
    push: bool
    kind: str
    headline: str
    url: str
    timestamp: str  # source feed timestamp, ISO


_HEAD_RE = re.compile(
    r"^-\s*\[(?P<tkr>[^\]]+)\]\s*"  # [TICKER]
    r"(?:\*\*)?sev\s*(?P<sev>\d+)"  # sev N (optional **)
    r"(?:\s*[—-]\s*PUSH)?"  # optional — PUSH
    r"(?:\*\*)?"  # optional closing **
    r"(?:\s*[—-]\s*(?P<rest>.*))?$"  # optional — rest
)


def parse_intraday_news(path: Path) -> list[IntradayNewsItem]:
    """Block layout in news-YYYY-MM-DD.md:
        - [TICKER] **sev 4 — PUSH** — kind descriptors here
          - Headline goes here
          - https://url
          - via source · 2026-05-07T20:42:09+00:00
    Continuation lines start with two spaces + `- `.
    """
    if not path.exists():
        return []
    items: list[IntradayNewsItem] = []
    block: list[str] = []

    def flush():
        if not block:
            return
        head = block[0]
        m = _HEAD_RE.match(head)
        if not m:
            return
        sev_n = int(m.group("sev"))
        push = "PUSH" in head
        rest = (m.group("rest") or "").strip(" *")
        kind = rest if rest else "—"
        # continuation lines (already stripped to start with "- ")
        cont = [
            ln[2:].strip() for ln in block[1:] if ln.startswith("- ")
        ]
        headline = ""
        url = ""
        ts = ""
        for c in cont:
            if c.startswith("http"):
                url = c
            elif " · " in c and re.search(r"\d{4}-\d{2}-\d{2}", c):
                ts = c.split(" · ", 1)[-1].strip()
            elif not headline:
                headline = c
        items.append(
            IntradayNewsItem(
                ticker=m.group("tkr").strip(),
                sev=sev_n,
                push=push,
                kind=kind,
                headline=headline,
                url=url,
                timestamp=ts,
            )
        )

    for raw in path.read_text(encoding="utf-8").splitlines():
        ln = raw.rstrip()
        stripped = ln.strip()
        if stripped.startswith("- [") and "sev" in stripped.lower():
            flush()
            block = [stripped]
        elif block and (ln.startswith("  - ") or ln.startswith("    - ")):
            block.append(ln.strip())
        elif stripped == "" or stripped.startswith("##") or stripped.startswith("#"):
            flush()
            block = []
    flush()
    return items


def _ts_to_dt(ts: str) -> datetime | None:
    """Parse ISO-ish timestamps from the intraday news feed."""
    if not ts:
        return None
    s = ts.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # try without timezone
        try:
            return datetime.fromisoformat(s.split("+")[0]).replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def recent_intraday_news(hours: int = CRITICAL_NEWS_HOURS) -> list[IntradayNewsItem]:
    """Read today's + yesterday's intraday news files; dedupe by URL/timestamp;
    return items whose source timestamp is within `hours` of now (or no ts)."""
    seen: set[tuple[str, str, str]] = set()  # (ticker, url, ts)
    out: list[IntradayNewsItem] = []
    cutoff = NOW - timedelta(hours=hours)
    for off in (0, 1):
        d = TODAY - timedelta(days=off)
        p = VAULT / "reports" / "intraday-alerts" / f"news-{d.isoformat()}.md"
        for n in parse_intraday_news(p):
            key = (n.ticker, n.url, n.timestamp)
            if key in seen:
                continue
            seen.add(key)
            dt = _ts_to_dt(n.timestamp)
            if dt is not None and dt < cutoff:
                continue
            out.append(n)
    out.sort(key=lambda x: (-x.sev, x.ticker))
    return out


def parse_intraday_triggers(path: Path) -> list[str]:
    """Returns one-line summaries of fires from intraday-alerts/YYYY-MM-DD.md."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    fires: list[str] = []
    for ln in text.splitlines():
        if ln.startswith("- ["):
            fires.append(ln.strip("- ").strip())
    return fires


def recent_intraday_triggers() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []  # (date, line)
    for off in (0, 1):
        d = TODAY - timedelta(days=off)
        p = VAULT / "reports" / "intraday-alerts" / f"{d.isoformat()}.md"
        for line in parse_intraday_triggers(p):
            out.append((d.isoformat(), line))
    return out


# ---------- pre-earnings / pre-ipo (upcoming) ----------

def upcoming_pre_earnings() -> list[tuple[str, str, Path]]:
    """Return (ticker, print_date, path) sorted by print date asc, future only."""
    pe_dir = VAULT / "reports" / "pre-earnings"
    if not pe_dir.exists():
        return []
    pat = re.compile(r"^([A-Z\.]+)-(\d{4}-\d{2}-\d{2})-(initial|gate)\.md$")
    seen: dict[tuple[str, str], Path] = {}
    for p in pe_dir.glob("*.md"):
        m = pat.match(p.name)
        if not m:
            continue
        tkr, dt, mode = m.groups()
        try:
            d = datetime.strptime(dt, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < TODAY:
            continue
        # prefer gate file over initial when both exist
        key = (tkr, dt)
        if key not in seen or mode == "gate":
            seen[key] = p
    return sorted(((t, d, p) for (t, d), p in seen.items()), key=lambda x: x[1])


def upcoming_pre_ipo() -> list[tuple[str, str, Path]]:
    pi_dir = VAULT / "reports" / "pre-ipo"
    if not pi_dir.exists():
        return []
    pat = re.compile(r"^([A-Z0-9_\.]+)-(\d{4}-\d{2}-\d{2})-(initial|gate)\.md$")
    seen: dict[tuple[str, str], Path] = {}
    for p in pi_dir.glob("*.md"):
        m = pat.match(p.name)
        if not m:
            continue
        slug, dt, mode = m.groups()
        try:
            d = datetime.strptime(dt, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < TODAY:
            continue
        key = (slug, dt)
        if key not in seen or mode == "gate":
            seen[key] = p
    return sorted(((s, d, p) for (s, d), p in seen.items()), key=lambda x: x[1])


# ---------- deep-dives ----------

def latest_deep_dive_per_ticker() -> dict[str, tuple[str, Path]]:
    """Return {ticker: (date_str, path)} for most-recent single-ticker deep dive."""
    dd = VAULT / "deep-dives"
    if not dd.exists():
        return {}
    pat = re.compile(r"^([A-Z\.]+)-(\d{4}-\d{2}-\d{2})\.md$")
    out: dict[str, tuple[str, Path]] = {}
    for p in dd.glob("*.md"):
        m = pat.match(p.name)
        if not m:
            continue
        tkr, dt = m.groups()
        prev = out.get(tkr)
        if prev is None or dt > prev[0]:
            out[tkr] = (dt, p)
    return out


VERDICT_PAT = re.compile(
    r"^\s*[*-]?\s*\*?\*?(?:Verdict|Final\s+Verdict|verdict)\*?\*?\s*[:—-]\s*\*?\*?(?P<v>HOLD|ADD|REDUCE|WATCH|TRIM|BUY|EXIT)\*?\*?",
    re.IGNORECASE | re.MULTILINE,
)


def extract_verdict(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    # search first 200 lines (verdict normally at top or in summary)
    head = "\n".join(text.splitlines()[:400])
    m = VERDICT_PAT.search(head)
    return m.group("v").upper() if m else ""


# ---------- recent files ----------

def recent_files(hours: int = RECENT_FILES_HOURS) -> list[tuple[datetime, Path]]:
    cutoff_ts = NOW.timestamp() - hours * 3600
    out: list[tuple[datetime, Path]] = []
    skip_dirs = {".obsidian", ".trash", "Files"}
    for p in VAULT.rglob("*.md"):
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.name == "DASHBOARD.md":
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime >= cutoff_ts:
            out.append((datetime.fromtimestamp(mtime).astimezone(), p))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


# ---------- formatters ----------

def fmt_wikilink(name: str) -> str:
    return f"[[{name}]]"


def render_dashboard() -> str:
    tier1, tier2, tier3, triggers, tranches = load_watchlist()
    broader = load_broader_triggers()
    ipos = load_ipo_calendar()
    daily_path, daily_text = latest_daily_report()
    daily_items = parse_daily_items(daily_text) if daily_text else []
    earnings_lines = parse_active_earnings(daily_text) if daily_text else []
    ipo_lines = parse_active_ipos(daily_text) if daily_text else []
    drift_lines = parse_verdict_drift(daily_text) if daily_text else []
    broader_fires = parse_broader_fires(daily_text) if daily_text else []
    news_items = recent_intraday_news()
    fired = recent_intraday_triggers()
    pe = upcoming_pre_earnings()
    pi = upcoming_pre_ipo()
    deep_dives = latest_deep_dive_per_ticker()
    rfiles = recent_files()

    out: list[str] = []

    # ----- frontmatter -----
    out.append("---")
    out.append("type: dashboard")
    out.append(f"last_updated: {NOW.isoformat(timespec='seconds')}")
    out.append("---")
    out.append("")
    out.append("# Trading Dashboard")
    out.append("")
    out.append(
        f"> **Last updated:** {NOW:%Y-%m-%d %H:%M %Z} · "
        f"**Today:** {NOW:%A, %B %-d %Y}"
        if sys.platform != "win32"
        else f"> **Last updated:** {NOW:%Y-%m-%d %H:%M %Z} · "
        f"**Today:** {NOW:%A, %B %#d %Y}"
    )
    out.append(">")
    out.append(
        "> Auto-built by `.claude/scripts/build_dashboard.py`. "
        "Rebuilds after each daily / intraday run. "
        "Source files (watchlist, triggers, daily reports) are authoritative — "
        "this file is a view."
    )
    out.append("")

    # ----- TODAY (priority surface) -----
    today_blocks: list[str] = []

    # Active earnings within 5 TD (carry from daily report's section)
    if earnings_lines:
        today_blocks.append("**Active earnings windows:**")
        for ln in earnings_lines:
            today_blocks.append(f"- {ln}")
        today_blocks.append("")

    # Active IPOs (≤7 TD)
    if ipo_lines:
        today_blocks.append("**Active IPO windows:**")
        for ln in ipo_lines:
            today_blocks.append(f"- {ln}")
        today_blocks.append("")

    # sev-4 PUSH news in last 24h
    push_items = [
        n for n in news_items if n.push and n.sev >= 4
    ]
    if push_items:
        today_blocks.append("**Sev-4 PUSH alerts (last 24h):**")
        for n in push_items[:10]:
            head = (n.headline or n.kind or "—").rstrip(".")
            if len(head) > 130:
                head = head[:127] + "..."
            link = f" [→]({n.url})" if n.url else ""
            dt = _ts_to_dt(n.timestamp)
            ts = dt.strftime("%m-%d %H:%M") if dt else ""
            ts_str = f" *({ts} UTC)*" if ts else ""
            today_blocks.append(f"- **[{n.ticker}]** {n.kind} — {head}{link}{ts_str}")
        today_blocks.append("")

    # Fires today
    today_iso = TODAY.isoformat()
    fires_today = [(d, ln) for d, ln in fired if d == today_iso]
    if fires_today:
        today_blocks.append("**Triggers fired today:**")
        for _, ln in fires_today:
            today_blocks.append(f"- {ln}")
        today_blocks.append("")

    # Tranches expiring in the next 7 days (silent killer otherwise)
    soon_expiring = []
    for tr in tranches:
        try:
            d = datetime.strptime(tr.expires.strip(), "%Y-%m-%d").date()
        except ValueError:
            continue
        days_left = (d - TODAY).days
        if 0 <= days_left <= 7:
            soon_expiring.append((days_left, tr))
    if soon_expiring:
        soon_expiring.sort(key=lambda x: x[0])
        today_blocks.append("**Tranches expiring in ≤7 days:**")
        for days_left, tr in soon_expiring:
            today_blocks.append(
                f"- **{tr.ticker}** {tr.action} {tr.size} @ {tr.at_price} — "
                f"expires {tr.expires} (T-{days_left}d)"
            )
        today_blocks.append("")

    # Broader-trigger fires (from latest daily)
    if broader_fires:
        today_blocks.append("**Broader trigger fires (latest daily):**")
        for ln in broader_fires:
            short = ln if len(ln) <= 200 else ln[:197] + "..."
            today_blocks.append(f"- {short}")
        today_blocks.append("")

    if today_blocks:
        out.append("## Today")
        out.append("")
        out.append("> [!important] Must-attend")
        for ln in today_blocks:
            out.append(f"> {ln}" if ln else ">")
        out.append("")
    else:
        out.append("## Today")
        out.append("")
        out.append("> [!note] No active earnings/IPO/sev-4 events surfaced today.")
        out.append("")

    # ----- DAILY ALERT HEADLINES -----
    if daily_items and daily_path:
        out.append(f"## Latest Daily Alert — {daily_path.stem}")
        out.append("")
        out.append(f"Source: {fmt_wikilink(daily_path.stem)}")
        out.append("")
        for it in daily_items:
            title = re.sub(r"^[^\w]*", "", it.title).strip()
            out.append(f"- **{title}**")
            if it.action and it.action.lower() != "none":
                out.append(f"  - _Action:_ {it.action}")
        out.append("")

    # ----- VERDICT DRIFT -----
    if drift_lines:
        out.append("## Verdict Drift (from latest daily)")
        out.append("")
        for ln in drift_lines:
            short = ln if len(ln) <= 220 else ln[:217] + "..."
            out.append(f"- {short}")
        out.append("")

    # ----- WATCHLIST -----
    out.append("## Watchlist")
    out.append("")
    out.append("### Tier 1 — Core Holdings")
    out.append("")
    out.append("| Ticker | Company | Latest Verdict | Most Recent Deep Dive |")
    out.append("| --- | --- | --- | --- |")
    for r in tier1:
        tkr = r.get("Ticker", "")
        co = r.get("Company", "")
        dd = deep_dives.get(tkr)
        if dd:
            verdict = extract_verdict(dd[1]) or "—"
            link = fmt_wikilink(dd[1].stem)
            verdict_cell = f"{verdict} ({dd[0]})"
        else:
            verdict_cell, link = "—", "—"
        out.append(f"| {tkr} | {co} | {verdict_cell} | {link} |")
    out.append("")
    out.append("### Tier 2 — Active Watchlist")
    out.append("")
    out.append("| Ticker | Company | Latest Verdict | Most Recent Deep Dive |")
    out.append("| --- | --- | --- | --- |")
    for r in tier2:
        tkr = r.get("Ticker", "")
        co = r.get("Company", "")
        dd = deep_dives.get(tkr)
        if dd:
            verdict = extract_verdict(dd[1]) or "—"
            link = fmt_wikilink(dd[1].stem)
            verdict_cell = f"{verdict} ({dd[0]})"
        else:
            verdict_cell, link = "—", "—"
        out.append(f"| {tkr} | {co} | {verdict_cell} | {link} |")
    out.append("")
    if tier3:
        out.append("### Tier 3 — Peripheral Interest")
        out.append("")
        t3_str = ", ".join(r.get("Ticker", "") for r in tier3)
        out.append(f"_{t3_str}_")
        out.append("")

    # ----- WATCHLIST PRICE TRIGGERS -----
    out.append("## Price Triggers — Watchlist")
    out.append("")
    out.append("| Ticker | Buy ≤ | Trim ≥ | Funded-by | Reviewed | Status | Note |")
    out.append("| --- | --- | --- | --- | --- | --- | --- |")
    for t in triggers:
        status = "STALE" if is_stale(t.last_reviewed) else "live"
        note = (t.note or "").replace("|", "\\|")
        if len(note) > 80:
            note = note[:77] + "..."
        out.append(
            f"| {t.ticker} | {t.buy_below} | {t.trim_above} | {t.funded_by} | "
            f"{t.last_reviewed} | {status} | {note} |"
        )
    out.append("")

    # ----- PLANNED TRANCHES -----
    active_tranches = [tr for tr in tranches if not is_expired(tr.expires)]
    expired_tranches = [tr for tr in tranches if is_expired(tr.expires)]
    out.append("## Planned Tranches — Active")
    out.append("")
    if active_tranches:
        out.append("| Ticker | Action | Size | At Price | Expires | Order | Note |")
        out.append("| --- | --- | --- | --- | --- | --- | --- |")
        for tr in active_tranches:
            note = (tr.note or "").replace("|", "\\|")
            if len(note) > 70:
                note = note[:67] + "..."
            out.append(
                f"| {tr.ticker} | {tr.action} | {tr.size} | {tr.at_price} | "
                f"{tr.expires} | {tr.order} | {note} |"
            )
        out.append("")
    else:
        out.append("_No active tranches._")
        out.append("")
    if expired_tranches:
        out.append(
            f"_({len(expired_tranches)} expired tranche(s) hidden — pruned by weekly-review.)_"
        )
        out.append("")

    # ----- BROADER TRIGGERS -----
    if broader:
        live_broader = [b for b in broader if not is_stale(b.last_reviewed)]
        stale_broader = [b for b in broader if is_stale(b.last_reviewed)]
        out.append("## Broader Price Triggers (non-watchlist)")
        out.append("")
        if live_broader:
            out.append("| Ticker | Buy ≤ | Trim ≥ | Funded-by | Reviewed | Source |")
            out.append("| --- | --- | --- | --- | --- | --- |")
            for t in live_broader:
                src = t.source if t.source.startswith("[[") else (t.source or "—")
                out.append(
                    f"| {t.ticker} | {t.buy_below} | {t.trim_above} | "
                    f"{t.funded_by} | {t.last_reviewed} | {src} |"
                )
            out.append("")
        if stale_broader:
            stale_tickers = ", ".join(b.ticker for b in stale_broader)
            out.append(f"_Stale (>30d): {stale_tickers}_")
            out.append("")

    # ----- IPO CALENDAR -----
    if ipos:
        out.append("## IPO Calendar")
        out.append("")
        # Group by status
        by_status: dict[str, list[dict]] = defaultdict(list)
        for r in ipos:
            by_status[r.get("Status", "")].append(r)
        order = [
            "priced",
            "this week",
            "this month",
            "trading",
            "quiet-period",
            "lockup-soon",
            "30+ days out",
            "pulled",
        ]
        for status in order:
            rows = by_status.get(status, [])
            if not rows:
                continue
            out.append(f"### {status}")
            out.append("")
            out.append("| Ticker | Company | Expected | Sector | Fit | Skill Run |")
            out.append("| --- | --- | --- | --- | --- | --- |")
            for r in rows:
                out.append(
                    f"| {r.get('Ticker', '')} | {r.get('Company', '')} | "
                    f"{r.get('Expected Date', '')} | {r.get('Sector', '')} | "
                    f"{r.get('Thesis Fit', '')} | {r.get('Skill Run', '')} |"
                )
            out.append("")

    # ----- UPCOMING SCHEDULED EVENTS (from filenames) -----
    if pe or pi:
        out.append("## Upcoming Scheduled Events")
        out.append("")
        if pe:
            out.append("**Pre-earnings plans on file:**")
            for tkr, dt, p in pe[:10]:
                td = (datetime.strptime(dt, "%Y-%m-%d").date() - TODAY).days
                td_str = "today" if td == 0 else f"T-{td}d" if td > 0 else f"T+{-td}d"
                out.append(f"- **{tkr}** print {dt} ({td_str}) — {fmt_wikilink(p.stem)}")
            out.append("")
        if pi:
            out.append("**Pre-IPO plans on file:**")
            for slug, dt, p in pi[:10]:
                td = (datetime.strptime(dt, "%Y-%m-%d").date() - TODAY).days
                td_str = "today" if td == 0 else f"T-{td}d" if td > 0 else f"T+{-td}d"
                out.append(f"- **{slug}** expected {dt} ({td_str}) — {fmt_wikilink(p.stem)}")
            out.append("")

    # ----- RECENT CRITICAL NEWS (last 24h, sev≥3) -----
    sev3plus = [n for n in news_items if n.sev >= 3]
    if sev3plus:
        out.append("## Recent News (last ~24h)")
        out.append("")
        # by ticker
        by_tkr: dict[str, list[IntradayNewsItem]] = defaultdict(list)
        for n in sev3plus:
            by_tkr[n.ticker].append(n)
        for tkr in sorted(by_tkr.keys()):
            items = by_tkr[tkr]
            items.sort(key=lambda x: (-x.sev, x.timestamp), reverse=False)
            count4 = sum(1 for i in items if i.sev >= 4)
            count3 = sum(1 for i in items if i.sev == 3)
            badge = []
            if count4:
                badge.append(f"**{count4} sev-4**")
            if count3:
                badge.append(f"{count3} sev-3")
            out.append(f"- **[{tkr}]** ({', '.join(badge)})")
            for it in items[:5]:
                # SEC filings: kind ("Form 4 (insider)") and headline ("4 - Statement of...")
                # are duplicative; show kind only and link to the index.
                is_sec = bool(re.match(r"^(Form |10-Q|10-K|8-K|144|S-1|DEF |424)", it.kind))
                if is_sec:
                    label = it.kind
                else:
                    head = (it.headline or it.kind or "—").rstrip(".")
                    if len(head) > 100:
                        head = head[:97] + "..."
                    label = f"{it.kind} — {head}"
                link = f" [→]({it.url})" if it.url else ""
                out.append(f"  - sev {it.sev} · {label}{link}")
        out.append("")

    # ----- RECENT FILES -----
    if rfiles:
        out.append(f"## Recent Files (last {RECENT_FILES_HOURS}h)")
        out.append("")
        # group by top-level folder under vault/
        by_folder: dict[str, list[tuple[datetime, Path]]] = defaultdict(list)
        for ts, p in rfiles:
            try:
                rel = p.relative_to(VAULT)
            except ValueError:
                continue
            top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
            by_folder[top].append((ts, p))
        for folder in sorted(by_folder.keys()):
            files = by_folder[folder][:8]
            out.append(f"**{folder}/**")
            for ts, p in files:
                rel = p.relative_to(VAULT)
                out.append(
                    f"- `{ts:%m-%d %H:%M}` {fmt_wikilink(p.stem)} "
                    f"<sub>`{rel.as_posix()}`</sub>"
                )
            extra = len(by_folder[folder]) - len(files)
            if extra > 0:
                out.append(f"- _+{extra} more_")
            out.append("")

    # ----- QUICK COMMANDS -----
    out.append("## Quick Commands")
    out.append("")
    out.append("- `deep dive TICKER` — full research run")
    out.append("- `pre-earnings TICKER gate` — T-1 / day-of earnings gate")
    out.append("- `pre-ipo TICKER gate` — day-of-pricing IPO gate")
    out.append("- `run weekly review` — Friday macro synthesis")
    out.append("- `build company dossier for TICKER` — SEC-sourced reference")
    out.append("")

    out.append("---")
    out.append("")
    out.append(
        "*Not investment advice. This file is auto-generated; edit the underlying "
        "vault files (watchlist, triggers, etc.), not this dashboard.*"
    )
    out.append("")
    return "\n".join(out)


def main() -> int:
    text = render_dashboard()
    OUT.write_text(text, encoding="utf-8")
    sys.stdout.write(f"wrote {OUT.relative_to(ROOT)} ({len(text)} chars)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
