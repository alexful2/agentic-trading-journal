from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
OUT = Path(__file__).resolve().parent / "index.html"
RECENT_HOURS = 72


@dataclass
class Table:
    headers: list[str]
    rows: list[dict[str, str]]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def clean(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    value = value.replace("[[", "").replace("]]", "")
    value = re.sub(r"\s+", " ", value)
    return value


def strip_md(value: str) -> str:
    value = clean(value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    return value.replace("`", "").strip()


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def extract_section(markdown: str, heading: str, level: int = 2) -> str:
    marker = "#" * level
    pattern = re.compile(rf"^{marker}\s+{re.escape(heading)}[^\n]*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(rf"^{marker}\s+", markdown[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(markdown)
    return markdown[start:end]


def parse_first_table(markdown: str) -> Table:
    lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return Table([], [])

    def split(line: str) -> list[str]:
        return [clean(cell) for cell in line.strip("|").split("|")]

    headers = split(lines[0])
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = split(line)
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        rows.append(dict(zip(headers, cells[: len(headers)])))
    return Table(headers, rows)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}


def rel_path(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def file_stamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def relative_age(ts: float, now_ts: float) -> str:
    minutes = max(0, int((now_ts - ts) // 60))
    if minutes < 60:
        return f"{minutes}m ago" if minutes else "just now"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def latest_existing(paths: list[Path]) -> Path | None:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: path.stat().st_mtime)


def collect_watchlist() -> dict[str, list[dict[str, str]]]:
    text = read_text(VAULT / "watchlist.md")
    tiers: dict[str, list[dict[str, str]]] = {}
    for heading, key in [
        ("Tier 1", "Core"),
        ("Tier 2", "Active"),
        ("Tier 3", "Peripheral"),
    ]:
        match = re.search(rf"^##\s+{re.escape(heading)}.*$", text, re.MULTILINE)
        if not match:
            tiers[key] = []
            continue
        start = match.start()
        next_match = re.search(r"^##\s+", text[match.end() :], re.MULTILINE)
        section = text[start : match.end() + next_match.start()] if next_match else text[start:]
        tiers[key] = parse_first_table(section).rows
    return tiers


def collect_triggers() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any], dict[str, Any]]:
    watchlist_text = read_text(VAULT / "watchlist.md")
    broader_text = read_text(VAULT / "price-triggers.md")
    watchlist = parse_first_table(extract_section(watchlist_text, "Price Triggers")).rows
    tranches = parse_first_table(extract_section(watchlist_text, "Planned Tranches")).rows
    broader = parse_first_table(extract_section(broader_text, "Price Triggers")).rows
    for row in watchlist:
        row["Scope"] = "watchlist"
    for row in broader:
        row["Scope"] = "broader"
    return (
        watchlist + broader,
        tranches,
        load_json(ROOT / "trigger_results_watchlist.json"),
        load_json(ROOT / "trigger_results_broader.json"),
    )


def collect_ipo() -> list[dict[str, str]]:
    rows = parse_first_table(extract_section(read_text(VAULT / "ipo-calendar.md"), "Calendar")).rows
    status_rank = {
        "priced": 0,
        "trading": 1,
        "this week": 2,
        "this month": 3,
        "quiet-period": 4,
        "lockup-soon": 5,
        "30+ days out": 6,
    }
    return sorted(rows, key=lambda row: (status_rank.get(row.get("Status", ""), 9), row.get("Expected Date", "")))


def collect_earnings() -> list[dict[str, Any]]:
    rows = load_json(ROOT / "upcoming_earnings.json").get("upcoming", [])
    return sorted(rows, key=lambda row: row.get("calendar_days_until", 999))


def collect_verdicts() -> list[dict[str, str]]:
    table = parse_first_table(read_text(VAULT / "deep-dives" / "_verdicts.md"))
    rows = table.rows
    return sorted(rows, key=lambda row: row.get("Date", ""), reverse=True)


def collect_verdict_drift() -> list[dict[str, Any]]:
    payload = load_json(ROOT / "verdict_drift.json")
    return sorted(payload.get("drifts", []), key=lambda row: abs(float(row.get("drift_pct", 0))), reverse=True)


def collect_recent_files() -> list[dict[str, str]]:
    now_ts = datetime.now().timestamp()
    cutoff = now_ts - RECENT_HOURS * 3600
    recent = []
    for path in VAULT.rglob("*"):
        if not path.is_file():
            continue
        stat = path.stat()
        changed = max(stat.st_ctime, stat.st_mtime)
        if changed < cutoff:
            continue
        recent.append(
            {
                "path": rel_path(path),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "age": relative_age(changed, now_ts),
                "kind": path.parts[-2] if len(path.parts) > 1 else "vault",
            }
        )
    return sorted(recent, key=lambda item: item["modified"], reverse=True)[:24]


def collect_intraday_news() -> list[dict[str, str]]:
    alert_dir = VAULT / "reports" / "intraday-alerts"
    files = sorted(alert_dir.glob("news-*.md"), key=lambda path: path.stat().st_mtime, reverse=True)[:6]
    events: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for path in files:
        for raw in read_text(path).splitlines():
            line = raw.rstrip()
            if line.startswith("- ["):
                match = re.match(r"- \[([^\]]+)\]\s+(.*)", line)
                if not match:
                    current = None
                    continue
                ticker, meta = match.groups()
                sev_match = re.search(r"sev\s+(\d)", meta, re.IGNORECASE)
                severity = int(sev_match.group(1)) if sev_match else 0
                if severity < 3:
                    current = None
                    continue
                current = {
                    "ticker": ticker,
                    "severity": f"sev {severity}",
                    "meta": strip_md(meta),
                    "title": "",
                    "source": path.name,
                }
                events.append(current)
            elif current and line.startswith("  - ") and not current["title"]:
                detail = strip_md(line[4:])
                if detail and not detail.startswith("http"):
                    current["title"] = detail

    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for event in events:
        if not event["title"]:
            continue
        key = (event["ticker"], event["severity"], event["meta"])
        grouped.setdefault(key, {**event, "titles": [], "count": 0})
        grouped[key]["count"] += 1
        if event["title"] not in grouped[key]["titles"]:
            grouped[key]["titles"].append(event["title"])

    summarized: list[dict[str, str]] = []
    for event in grouped.values():
        title = "; ".join(event["titles"][:2])
        if event["count"] > 2:
            title = f"{title}; +{event['count'] - 2} more"
        summarized.append(
            {
                "ticker": event["ticker"],
                "severity": event["severity"],
                "meta": event["meta"],
                "title": title,
                "source": event["source"],
                "count": str(event["count"]),
            }
        )
    return sorted(summarized, key=lambda item: (item["severity"], item["ticker"]), reverse=True)[:12]


def collect_daily_actions() -> list[dict[str, str]]:
    daily_dir = VAULT / "reports" / "daily"
    files = [path for path in daily_dir.rglob("*.md") if "pdf" not in path.parts]
    files = sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:4]
    actions: list[dict[str, str]] = []
    active_heading = ""
    for path in files:
        for raw in read_text(path).splitlines():
            line = raw.strip()
            if line.startswith("## "):
                active_heading = strip_md(line.lstrip("# "))
            if "**Action:**" in line:
                action = strip_md(line.split("**Action:**", 1)[1].strip())
                actions.append({"action": action, "context": active_heading, "source": rel_path(path)})
            elif line.startswith("- **") and ("consider" in line.lower() or "re-evaluate" in line.lower()):
                actions.append({"action": strip_md(line.lstrip("- ")), "context": active_heading, "source": rel_path(path)})
            if len(actions) >= 10:
                return actions
    return actions


def build_focus_queue(
    news: list[dict[str, str]],
    actions: list[dict[str, str]],
    trigger_rows: list[dict[str, str]],
    tranches: list[dict[str, str]],
    ipo: list[dict[str, str]],
    earnings: list[dict[str, Any]],
    verdict_drift: list[dict[str, Any]],
) -> list[dict[str, str]]:
    queue: list[dict[str, str]] = []
    for action in actions[:3]:
        queue.append(
            {
                "type": "Daily action",
                "ticker": re.search(r"\b[A-Z]{2,6}\b", action["action"]).group(0) if re.search(r"\b[A-Z]{2,6}\b", action["action"]) else "ACTION",
                "title": action["action"],
                "detail": f"{action['context']} - {action['source']}",
                "priority": "high",
            }
        )
    for item in news[:3]:
        queue.append(
            {
                "type": item["severity"],
                "ticker": item["ticker"],
                "title": item["title"],
                "detail": f"{item['meta']} - {item['source']}",
                "priority": "high" if "4" in item["severity"] else "medium",
            }
        )
    today = date.today()
    for row in tranches:
        expires = parse_date(row.get("Expires"))
        if expires and 0 <= (expires - today).days <= 21:
            queue.append(
                {
                    "type": f"{row.get('Action', 'Tranche')} tranche",
                    "ticker": row.get("Ticker", ""),
                    "title": f"{row.get('Size', '')} at {row.get('At Price', '')}",
                    "detail": f"Expires {row.get('Expires')} - {row.get('Order')} - {row.get('Note', '')}",
                    "priority": "medium",
                }
            )
    for row in earnings[:3]:
        queue.append(
            {
                "type": "Earnings",
                "ticker": row.get("ticker", ""),
                "title": f"Print {row.get('print_date', '')}",
                "detail": "prepped" if row.get("has_pre_earnings_file") else "needs pre-earnings run",
                "priority": "medium" if row.get("has_pre_earnings_file") else "high",
            }
        )
    for row in ipo[:3]:
        if row.get("Status") in {"priced", "this week", "this month"}:
            queue.append(
                {
                    "type": "IPO",
                    "ticker": row.get("Ticker", "IPO"),
                    "title": f"{row.get('Company', '')} - {row.get('Expected Date', '')}",
                    "detail": f"{row.get('Status', '')} - {row.get('Thesis Fit', '')}",
                    "priority": "medium",
                }
            )
    for row in verdict_drift[:4]:
        queue.append(
            {
                "type": "Verdict drift",
                "ticker": row.get("ticker", ""),
                "title": f"{row.get('drift_pct', '')}% since {row.get('verdict', '')}",
                "detail": f"{row.get('deep_dive_file', '')} - {row.get('age_days', '')}d old",
                "priority": "medium",
            }
        )
    return queue[:14]


def build_position_cards(
    watchlist: dict[str, list[dict[str, str]]],
    triggers: list[dict[str, str]],
    tranches: list[dict[str, str]],
    verdicts: list[dict[str, str]],
) -> list[dict[str, str]]:
    latest_verdict: dict[str, dict[str, str]] = {}
    for row in verdicts:
        latest_verdict.setdefault(row.get("Ticker", ""), row)
    trigger_by_ticker: dict[str, list[dict[str, str]]] = {}
    tranche_by_ticker: dict[str, list[dict[str, str]]] = {}
    for row in triggers:
        trigger_by_ticker.setdefault(row.get("Ticker", ""), []).append(row)
    for row in tranches:
        tranche_by_ticker.setdefault(row.get("Ticker", ""), []).append(row)

    cards: list[dict[str, str]] = []
    for tier, rows in watchlist.items():
        for row in rows:
            ticker = row.get("Ticker", "")
            triggers_for_name = trigger_by_ticker.get(ticker, [])
            tranches_for_name = tranche_by_ticker.get(ticker, [])
            verdict = latest_verdict.get(ticker, {})
            cards.append(
                {
                    "ticker": ticker,
                    "company": row.get("Company", ""),
                    "tier": tier,
                    "thesis": row.get("Why I Own It (brief)") or row.get("Why I'm Watching") or row.get("Loose Interest", ""),
                    "verdict": verdict.get("Verdict", "unrated"),
                    "verdictDate": verdict.get("Date", ""),
                    "priceAtVerdict": verdict.get("Price at verdict", ""),
                    "buy": next((item.get("Buy Below", "") for item in triggers_for_name if item.get("Buy Below") not in {"", "---", "\u2014"}), ""),
                    "trim": next((item.get("Trim Above", "") for item in triggers_for_name if item.get("Trim Above") not in {"", "---", "\u2014"}), ""),
                    "tranches": str(len(tranches_for_name)),
                }
            )
    return cards


def as_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def render() -> None:
    watchlist = collect_watchlist()
    triggers, tranches, watch_state, broader_state = collect_triggers()
    ipo = collect_ipo()
    earnings = collect_earnings()
    verdicts = collect_verdicts()
    verdict_drift = collect_verdict_drift()
    recent_files = collect_recent_files()
    news = collect_intraday_news()
    daily_actions = collect_daily_actions()

    watch_checked = parse_dt(watch_state.get("checked_at"))
    broader_checked = parse_dt(broader_state.get("checked_at"))
    watch_fresh = bool(watch_checked and watch_checked.timestamp() >= (VAULT / "watchlist.md").stat().st_mtime)
    broader_fresh = bool(broader_checked and broader_checked.timestamp() >= (VAULT / "price-triggers.md").stat().st_mtime)

    source_paths = [
        VAULT / "watchlist.md",
        VAULT / "price-triggers.md",
        VAULT / "ipo-calendar.md",
        VAULT / "deep-dives" / "_verdicts.md",
        latest_existing(list((VAULT / "reports" / "intraday-alerts").glob("news-*.md"))),
        latest_existing([path for path in (VAULT / "reports" / "daily").rglob("*.md") if "pdf" not in path.parts]),
    ]
    source_stamps = [
        {"path": rel_path(path), "updated": file_stamp(path)}
        for path in source_paths
        if path is not None and path.exists()
    ]

    data = {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "recentHours": RECENT_HOURS,
        "watchlist": watchlist,
        "positions": build_position_cards(watchlist, triggers, tranches, verdicts),
        "triggers": triggers,
        "tranches": tranches,
        "watchState": watch_state,
        "broaderState": broader_state,
        "triggerSnapshotsFresh": {"watchlist": watch_fresh, "broader": broader_fresh},
        "ipo": ipo,
        "earnings": earnings,
        "verdicts": verdicts[:12],
        "verdictDrift": verdict_drift,
        "recentFiles": recent_files,
        "news": news,
        "dailyActions": daily_actions,
        "focusQueue": build_focus_queue(news, daily_actions, triggers, tranches, ipo, earnings, verdict_drift),
        "sourceStamps": source_stamps,
    }
    OUT.write_text(HTML_TEMPLATE.replace("__DASHBOARD_DATA__", as_json(data)), encoding="utf-8")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trading Journal Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f6f3;
      --surface: #ffffff;
      --surface-soft: #f9faf7;
      --ink: #171916;
      --muted: #626b64;
      --faint: #8b948d;
      --line: #dfe5de;
      --line-strong: #c7d0c9;
      --accent: #1f6f55;
      --accent-2: #315f91;
      --warn: #9b6b12;
      --danger: #a64038;
      --good: #277343;
      --charcoal: #243029;
      --shadow: 0 16px 46px rgba(28, 36, 30, .08);
      --radius: 8px;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 15px;
    }
    * { box-sizing: border-box; }
    html { background: var(--bg); }
    body { margin: 0; min-width: 320px; color: var(--ink); background: radial-gradient(circle at top left, rgba(31,111,85,.10), transparent 28rem), var(--bg); }
    button, input { font: inherit; }
    .shell { width: min(1740px, calc(100% - 28px)); margin: 0 auto; padding: 18px 0 34px; }
    .hero {
      min-height: 176px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(340px, 460px);
      gap: 18px;
      align-items: end;
      padding: 20px 0 18px;
    }
    .kicker { color: var(--accent); font-size: 12px; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
    h1 { margin: 7px 0 0; font-size: clamp(32px, 4vw, 54px); line-height: .98; letter-spacing: 0; }
    .subtitle { max-width: 760px; margin-top: 11px; color: var(--muted); font-size: 15px; line-height: 1.45; }
    .toolbar { display: grid; gap: 10px; justify-items: end; }
    .search {
      width: min(460px, 100%);
      height: 42px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255,255,255,.9);
      padding: 0 13px;
      color: var(--ink);
      box-shadow: var(--shadow);
    }
    .tabs { display: flex; gap: 7px; justify-content: flex-end; flex-wrap: wrap; }
    .tab {
      height: 34px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255,255,255,.78);
      color: var(--charcoal);
      padding: 0 11px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 800;
    }
    .tab.active { background: var(--charcoal); border-color: var(--charcoal); color: #fff; }
    .metrics { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
    .metric {
      min-height: 96px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(180deg, #fff, #fbfcfa);
      box-shadow: var(--shadow);
      padding: 13px;
      position: relative;
      overflow: hidden;
    }
    .metric:before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px; background: var(--stripe, var(--accent)); }
    .metric strong { display: block; font-size: 28px; line-height: 1; letter-spacing: 0; }
    .metric span { display: block; margin-top: 8px; color: var(--muted); font-size: 12px; font-weight: 850; letter-spacing: .05em; text-transform: uppercase; }
    .metric small { display: block; margin-top: 7px; color: var(--faint); line-height: 1.25; }
    .layout { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(360px, .85fr); gap: 14px; align-items: start; }
    .main { display: grid; grid-template-columns: minmax(0, 1fr) minmax(340px, .82fr); gap: 14px; }
    .side { display: grid; gap: 14px; }
    .wide { grid-column: 1 / -1; }
    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel-head {
      min-height: 50px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #fff, var(--surface-soft));
    }
    h2 { margin: 0; font-size: 14px; letter-spacing: 0; }
    .count { color: var(--muted); font-size: 12px; white-space: nowrap; }
    .panel-body { padding: 12px; }
    .stack { display: grid; gap: 9px; }
    .card {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #fff;
      padding: 11px;
      transition: border-color .14s ease, box-shadow .14s ease, transform .14s ease;
    }
    .card:hover { border-color: var(--line-strong); box-shadow: 0 11px 26px rgba(28,36,30,.07); transform: translateY(-1px); }
    .card.featured { background: linear-gradient(135deg, #26332d, #35473d); color: #fff; border-color: #26332d; }
    .card.featured .muted, .card.featured .detail { color: rgba(255,255,255,.72); }
    .row { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
    .ticker { font-size: 13px; font-weight: 900; letter-spacing: .05em; }
    .title { margin-top: 6px; font-size: 14px; font-weight: 850; line-height: 1.28; }
    .detail { margin-top: 6px; color: var(--muted); font-size: 12px; line-height: 1.38; }
    .muted { color: var(--muted); font-size: 12px; }
    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 22px;
      max-width: 100%;
      border-radius: 999px;
      padding: 2px 8px;
      background: #eef2ef;
      color: #3e4942;
      font-size: 11px;
      font-weight: 850;
      line-height: 1.15;
      white-space: nowrap;
    }
    .pill.high, .pill.red { background: #f8e7e5; color: var(--danger); }
    .pill.medium, .pill.gold { background: #fbefd9; color: var(--warn); }
    .pill.green { background: #e6f2eb; color: var(--good); }
    .pill.blue { background: #e7eff7; color: var(--accent-2); }
    .positions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 9px; }
    .position-card { min-height: 164px; display: grid; align-content: start; gap: 8px; }
    .level-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; margin-top: 2px; }
    .level { border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface-soft); padding: 7px; min-width: 0; }
    .level span { display: block; color: var(--faint); font-size: 10px; font-weight: 850; letter-spacing: .06em; text-transform: uppercase; }
    .level strong { display: block; margin-top: 4px; font-size: 13px; overflow-wrap: anywhere; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { padding: 8px 9px; border-bottom: 1px solid var(--line); color: var(--faint); text-align: left; font-size: 11px; font-weight: 850; letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }
    td { padding: 9px; border-bottom: 1px solid var(--line); vertical-align: top; }
    tr:last-child td { border-bottom: 0; }
    tbody tr:hover { background: #fbfcfa; }
    .table-wrap { overflow-x: auto; }
    .clamp { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
    .source { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; color: var(--muted); font-size: 12px; }
    .source span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .notice { border-left: 4px solid var(--warn); border-radius: var(--radius); background: #fff9ed; color: #4f3b15; padding: 10px 11px; font-size: 13px; line-height: 1.38; }
    .empty { color: var(--muted); font-size: 13px; padding: 8px 2px; }
    .hidden { display: none !important; }
    @media (max-width: 1320px) {
      .layout, .main { grid-template-columns: 1fr; }
      .metrics { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .positions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 760px) {
      .shell { width: min(100% - 18px, 1740px); padding-top: 10px; }
      .hero { grid-template-columns: 1fr; min-height: 0; padding-top: 10px; }
      .toolbar { justify-items: stretch; }
      .tabs { justify-content: flex-start; overflow-x: auto; flex-wrap: nowrap; padding-bottom: 2px; }
      .tab { flex: 0 0 auto; }
      .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .metric { min-height: 86px; }
      .positions { grid-template-columns: 1fr; }
      .level-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      th:nth-child(n+5), td:nth-child(n+5) { display: none; }
      .panel-body { padding: 10px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div>
        <div class="kicker">Trading Journal</div>
        <h1>Decision dashboard</h1>
        <div class="subtitle" id="subtitle"></div>
      </div>
      <div class="toolbar">
        <input class="search" id="search" type="search" placeholder="Filter ticker, event, source, note">
        <div class="tabs" role="tablist">
          <button class="tab active" data-view="all">All</button>
          <button class="tab" data-view="action">Action</button>
          <button class="tab" data-view="portfolio">Portfolio</button>
          <button class="tab" data-view="calendar">Calendar</button>
          <button class="tab" data-view="research">Research</button>
          <button class="tab" data-view="system">System</button>
        </div>
      </div>
    </header>

    <section class="metrics" id="metrics"></section>

    <div class="layout">
      <div class="main">
        <section class="panel wide" data-panel="action">
          <div class="panel-head"><h2>Action Queue</h2><span class="count" id="queueCount"></span></div>
          <div class="panel-body stack" id="queue"></div>
        </section>

        <section class="panel wide" data-panel="portfolio">
          <div class="panel-head"><h2>Position Map</h2><span class="count" id="positionCount"></span></div>
          <div class="panel-body positions" id="positions"></div>
        </section>

        <section class="panel" data-panel="action">
          <div class="panel-head"><h2>Trigger Radar</h2><span class="count" id="triggerCount"></span></div>
          <div class="panel-body" id="triggers"></div>
        </section>

        <section class="panel" data-panel="calendar">
          <div class="panel-head"><h2>Planned Tranches</h2><span class="count" id="trancheCount"></span></div>
          <div class="panel-body" id="tranches"></div>
        </section>
      </div>

      <aside class="side">
        <section class="panel" data-panel="calendar">
          <div class="panel-head"><h2>Event Calendar</h2><span class="count" id="eventCount"></span></div>
          <div class="panel-body" id="events"></div>
        </section>

        <section class="panel" data-panel="research">
          <div class="panel-head"><h2>Latest Verdicts</h2><span class="count" id="verdictCount"></span></div>
          <div class="panel-body" id="verdicts"></div>
        </section>

        <section class="panel" data-panel="research">
          <div class="panel-head"><h2>Recent Vault Activity</h2><span class="count" id="fileCount"></span></div>
          <div class="panel-body" id="files"></div>
        </section>

        <section class="panel" data-panel="system">
          <div class="panel-head"><h2>System Freshness</h2><span class="count">inputs</span></div>
          <div class="panel-body stack" id="system"></div>
        </section>
      </aside>
    </div>
  </main>

  <script>
    const data = __DASHBOARD_DATA__;
    const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
    const rowText = row => Object.values(row || {}).join(" ").toLowerCase();
    const nonEmpty = value => value && !["-", "--", "---", "\u2014", "TBD"].includes(String(value).trim());
    const money = value => {
      const text = String(value ?? "").trim();
      if (!nonEmpty(text)) return "-";
      return /^-?\d+(\.\d+)?$/.test(text) ? `$${esc(text)}` : esc(text);
    };
    const clamp = value => `<div class="clamp">${esc(value || "")}</div>`;
    let view = "all";
    let query = "";

    const flatWatch = Object.values(data.watchlist).flat();
    const freshResults = [
      ...(data.triggerSnapshotsFresh.watchlist ? (data.watchState.results || []) : []),
      ...(data.triggerSnapshotsFresh.broader ? (data.broaderState.results || []) : [])
    ];
    const firedCount = freshResults.filter(row => String(row.status || "").startsWith("FIRED")).length;

    function visibleRows(rows) {
      return rows.filter(row => !query || rowText(row).includes(query));
    }
    function tagClass(value) {
      const text = String(value || "").toLowerCase();
      if (text.includes("high") || text.includes("sev 4") || text.includes("fired") || text.includes("needs")) return "high";
      if (text.includes("medium") || text.includes("alert") || text.includes("this week") || text.includes("drift")) return "medium";
      if (text.includes("hold") || text.includes("add") || text.includes("prepped")) return "green";
      if (text.includes("ipo") || text.includes("watch") || text.includes("30+")) return "blue";
      return "";
    }
    function table(headers, rows, cells) {
      if (!rows.length) return `<div class="empty">No matching rows.</div>`;
      return `<div class="table-wrap"><table><thead><tr>${headers.map(h => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${cells(row).join("")}</tr>`).join("")}</tbody></table></div>`;
    }
    function applyPanelVisibility() {
      document.querySelectorAll("[data-panel]").forEach(panel => {
        panel.classList.toggle("hidden", view !== "all" && panel.dataset.panel !== view);
      });
    }

    function render() {
      const queueRows = visibleRows(data.focusQueue);
      const positionRows = visibleRows(data.positions);
      const triggerRows = visibleRows(freshResults.length ? freshResults : data.triggers.map(row => ({...row, status: "set"}))).slice(0, 18);
      const trancheRows = visibleRows(data.tranches).slice(0, 18);
      const eventRows = visibleRows([
        ...data.earnings.map(row => ({kind: "Earnings", ticker: row.ticker, date: row.print_date, status: row.has_pre_earnings_file ? "prepped" : "needs prep", detail: row.pre_earnings_file || `${row.calendar_days_until} calendar days`})),
        ...data.ipo.map(row => ({kind: "IPO", ticker: row.Ticker, date: row["Expected Date"], status: row.Status, detail: `${row.Company} - ${row["Thesis Fit"]}`}))
      ]).slice(0, 14);
      const verdictRows = visibleRows(data.verdicts).slice(0, 12);
      const fileRows = visibleRows(data.recentFiles).slice(0, 18);

      document.getElementById("subtitle").textContent = `Generated ${data.generatedAt}. Built from canonical vault files with stale trigger snapshots fenced off instead of silently reused.`;
      document.getElementById("metrics").innerHTML = [
        ["Queue", queueRows.length, "Items needing attention", "var(--danger)"],
        ["Core", data.watchlist.Core?.length || 0, "Owned Tier 1 names", "var(--accent)"],
        ["Triggers", data.triggers.length, firedCount ? `${firedCount} fresh fired` : "Set levels", "var(--warn)"],
        ["Tranches", data.tranches.length, "Explicit staged plans", "var(--accent-2)"],
        ["Events", data.earnings.length + data.ipo.length, "Earnings and IPOs", "var(--charcoal)"],
        ["Files", data.recentFiles.length, `Changed in ${data.recentHours}h`, "#6d756f"],
      ].map(([label, value, detail, color]) => `<article class="metric" style="--stripe:${color}"><strong>${value}</strong><span>${esc(label)}</span><small>${esc(detail)}</small></article>`).join("");

      document.getElementById("queueCount").textContent = `${queueRows.length} shown`;
      document.getElementById("queue").innerHTML = queueRows.length ? queueRows.map((row, index) => `
        <article class="card ${index === 0 ? "featured" : ""}">
          <div class="row"><span class="ticker">${esc(row.ticker)}</span><span class="pill ${tagClass(row.priority || row.type)}">${esc(row.type)}</span></div>
          <div class="title">${esc(row.title)}</div>
          <div class="detail">${esc(row.detail)}</div>
        </article>`).join("") : `<div class="empty">No matching action items.</div>`;

      document.getElementById("positionCount").textContent = `${positionRows.length} shown`;
      document.getElementById("positions").innerHTML = positionRows.length ? positionRows.map(row => `
        <article class="card position-card">
          <div class="row"><span class="ticker">${esc(row.ticker)}</span><span class="pill ${tagClass(row.verdict)}">${esc(row.verdict)}</span></div>
          <div class="title">${esc(row.company)}</div>
          <div class="detail">${esc(row.thesis)}</div>
          <div class="level-grid">
            <div class="level"><span>Buy</span><strong>${money(row.buy)}</strong></div>
            <div class="level"><span>Trim</span><strong>${money(row.trim)}</strong></div>
            <div class="level"><span>Plans</span><strong>${esc(row.tranches)}</strong></div>
          </div>
          <div class="muted">${esc(row.tier)} - verdict ${esc(row.verdictDate || "unlogged")} ${row.priceAtVerdict ? `at ${esc(row.priceAtVerdict)}` : ""}</div>
        </article>`).join("") : `<div class="empty">No matching positions.</div>`;

      document.getElementById("triggerCount").textContent = freshResults.length ? "fresh snapshot" : "definitions";
      document.getElementById("triggers").innerHTML = table(["Ticker", "State", "Buy", "Trim", "Reviewed", "Note"], triggerRows, row => [
        `<td><strong>${esc(row.ticker || row.Ticker)}</strong><br><span class="muted">${esc(row.label || row.Scope || "")}</span></td>`,
        `<td><span class="pill ${tagClass(row.status)}">${esc(row.status)}</span></td>`,
        `<td>${money(row.buy_below ?? row["Buy Below"])}</td>`,
        `<td>${money(row.trim_above ?? row["Trim Above"])}</td>`,
        `<td>${esc(row.last_reviewed ?? row["Last Reviewed"] ?? "")}</td>`,
        `<td>${clamp(row.note ?? row.Note)}</td>`
      ]);

      document.getElementById("trancheCount").textContent = `${trancheRows.length} shown`;
      document.getElementById("tranches").innerHTML = table(["Ticker", "Action", "Size", "At", "Expires", "Order", "Note"], trancheRows, row => [
        `<td><strong>${esc(row.Ticker)}</strong></td>`,
        `<td><span class="pill ${tagClass(row.Action)}">${esc(row.Action)}</span></td>`,
        `<td>${esc(row.Size)}</td>`,
        `<td>${money(row["At Price"])}</td>`,
        `<td>${esc(row.Expires)}</td>`,
        `<td>${esc(row.Order)}</td>`,
        `<td>${clamp(row.Note)}</td>`
      ]);

      document.getElementById("eventCount").textContent = `${eventRows.length} shown`;
      document.getElementById("events").innerHTML = table(["Name", "Date", "Status", "Detail"], eventRows, row => [
        `<td><strong>${esc(row.ticker)}</strong><br><span class="muted">${esc(row.kind)}</span></td>`,
        `<td>${esc(row.date)}</td>`,
        `<td><span class="pill ${tagClass(row.status)}">${esc(row.status)}</span></td>`,
        `<td>${clamp(row.detail)}</td>`
      ]);

      document.getElementById("verdictCount").textContent = `${verdictRows.length} recent`;
      document.getElementById("verdicts").innerHTML = table(["Ticker", "Verdict", "Date", "Price"], verdictRows, row => [
        `<td><strong>${esc(row.Ticker)}</strong></td>`,
        `<td><span class="pill ${tagClass(row.Verdict)}">${esc(row.Verdict)}</span></td>`,
        `<td>${esc(row.Date)}</td>`,
        `<td>${esc(row["Price at verdict"])}</td>`
      ]);

      document.getElementById("fileCount").textContent = `last ${data.recentHours}h`;
      document.getElementById("files").innerHTML = table(["File", "Modified", "Age"], fileRows, row => [
        `<td>${esc(row.path)}</td>`,
        `<td>${esc(row.modified)}</td>`,
        `<td><span class="pill">${esc(row.age)}</span></td>`
      ]);

      const notices = [];
      if (!data.triggerSnapshotsFresh.watchlist) notices.push("Watchlist trigger snapshot is older than vault/watchlist.md, so the dashboard is showing trigger definitions rather than stale fired-state rows.");
      if (!data.triggerSnapshotsFresh.broader) notices.push("Broader trigger snapshot is older than vault/price-triggers.md, so opportunistic trigger state is treated as informational only.");
      document.getElementById("system").innerHTML = [
        ...notices.map(text => `<div class="notice">${esc(text)}</div>`),
        ...data.sourceStamps.map(row => `<div class="source"><span>${esc(row.path)}</span><strong>${esc(row.updated)}</strong></div>`)
      ].join("");
      applyPanelVisibility();
    }

    document.querySelectorAll(".tab").forEach(button => {
      button.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(tab => tab.classList.toggle("active", tab === button));
        view = button.dataset.view;
        applyPanelVisibility();
      });
    });
    document.getElementById("search").addEventListener("input", event => {
      query = event.target.value.trim().toLowerCase();
      render();
    });
    render();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    render()
