"""
build_and_send.py

Turn a daily report markdown file into an email brief and send it via Resend.
This is the single deterministic step that Step 6 of the news-analyst skill
delegates to — the agent only writes the markdown and a tiny frontmatter
block (email.subject + email.preheader); this script handles transform,
render, and send.

Pipeline:
    1. Load  vault/reports/daily/$DATE.md
    2. Parse frontmatter + body  (parse_report)
    3. Convert inline markdown to HTML  (markdown_render)
    4. On Fridays, prepend Weekly Review bullets from the latest
       vault/reports/weekly/*.md
    5. Render email HTML via Jinja2  (templates/email-default.html.j2)
    6. Send via Resend  (send_brief.send)

PDF rendering is disabled by default (too expensive on the GH Actions hot
path — Playwright + Chromium install was the bulk of runtime). Pass
--with-pdf to opt in for local one-offs; the briefing template + render
code remain in this folder if you ever want to revive it.

Template swap:
    --email-template templates/email-minimal.html.j2

CLI:
    python news-visual/build_and_send.py --date 2026-04-23
    python news-visual/build_and_send.py --date 2026-04-23 --dry-run
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

# Script lives in news-visual/ — ensure local imports work regardless of
# which directory the caller runs from.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from parse_report import parse_report  # noqa: E402
from markdown_render import md_to_html, md_to_plain  # noqa: E402


LOGO_URL = "https://raw.githubusercontent.com/your-username/trading-journal-assets/main/trading-journal-logo.png"
DEFAULT_FOOTER_MODEL = os.environ.get("DAILY_NEWS_FOOTER_MODEL", "Claude Opus 4.7")
LEAD_BODY_MAX_CHARS = 520
CARD_BODY_MAX_CHARS = 320
VERDICT_MAX_CHARS = 35
MACRO_PDF_LIMIT = 8


# ────────────────────────────────────────────────────────────────────────
# Email HTML rendering
# ────────────────────────────────────────────────────────────────────────

def _render_item_sub_html(item: dict) -> str:
    """Build the <ul>...</ul> block with source / why / action bullets."""
    lines: list[str] = ["<ul>"]
    if item.get("source"):
        lines.append(f"  <li><strong>Source:</strong> {md_to_html(item['source'])}</li>")
    if item.get("source_context"):
        lines.append(f"  <li><strong>Source (context):</strong> {md_to_html(item['source_context'])}</li>")
    if item.get("why"):
        lines.append(f"  <li><strong>Why it matters:</strong> {md_to_html(item['why'])}</li>")
    if item.get("action"):
        lines.append(f"  <li><strong>Action:</strong> {md_to_html(item['action'])}</li>")
    for label, content in item.get("other_bullets", []):
        lines.append(f"  <li><strong>{md_to_html(label)}:</strong> {md_to_html(content)}</li>")
    lines.append("</ul>")
    return "\n".join(lines)


def _render_item_title_html(item: dict) -> str:
    """Build the <strong>TICKER — Headline</strong> line."""
    fire = "🔥 " if item["severity"] >= 4 else ""
    ticker = item.get("ticker")
    headline = item["headline"]
    update = " (Update)" if item.get("is_update") else ""
    if ticker:
        return f"<strong>{fire}{ticker} — {md_to_html(headline)}{update}</strong>"
    return f"<strong>{fire}{md_to_html(headline)}{update}</strong>"


def _build_email_context(parsed: dict, fm_email: dict, weekly_review: dict | None) -> dict:
    items_ctx = []
    for it in parsed["items"]:
        items_ctx.append({
            "severity": it["severity"],
            "title_html": _render_item_title_html(it),
            "sub_html": _render_item_sub_html(it),
        })

    macro_html = [md_to_html(b) for b in parsed["macro"]]
    housekeeping_html = [md_to_html(b) for b in parsed["housekeeping"]]
    broader_triggers_html = [md_to_html(b) for b in parsed.get("broader_triggers", [])]
    active_pre_earnings_html = [md_to_html(b) for b in parsed.get("active_pre_earnings", [])]

    subject = fm_email.get("subject") or _default_subject(parsed)
    preheader = fm_email.get("preheader") or _default_preheader(parsed)

    return {
        "title": parsed["title"],
        "date_long": parsed["date_long"],
        "subject": subject,
        "preheader": preheader,
        "logo_url": LOGO_URL,
        "footer_model": DEFAULT_FOOTER_MODEL,
        "weekly_review": weekly_review,
        "price_triggers": broader_triggers_html,
        "active_pre_earnings": active_pre_earnings_html,
        "items": items_ctx,
        "macro": macro_html,
        "housekeeping": housekeeping_html,
    }


def _default_subject(parsed: dict) -> str:
    items = parsed["items"]
    if not items:
        return "Quiet day — macro only"
    top = items[0]
    ticker = top.get("ticker")
    if ticker:
        return f"{ticker} update — see brief"
    return "Daily brief"


def _default_preheader(parsed: dict) -> str:
    n = len(parsed["items"])
    if n == 0:
        return "No scored items today"
    return f"{n} scored item{'s' if n != 1 else ''} today"


# ────────────────────────────────────────────────────────────────────────
# Plain-text fallback (for mail clients without HTML)
# ────────────────────────────────────────────────────────────────────────

def _render_plaintext(parsed: dict, weekly_review: dict | None) -> str:
    lines: list[str] = []
    if weekly_review:
        lines.append(f"Weekly Review — {weekly_review['header']}")
        for b in weekly_review["bullets_plain"]:
            lines.append(f"- {b}")
        lines.append("")

    if parsed.get("active_pre_earnings"):
        lines.append("Active Pre-Earnings Windows")
        for b in parsed["active_pre_earnings"]:
            lines.append(f"- {md_to_plain(b)}")
        lines.append("")

    if parsed.get("broader_triggers"):
        lines.append("Broader Price Triggers")
        for b in parsed["broader_triggers"]:
            lines.append(f"- {md_to_plain(b)}")
        lines.append("")

    for it in parsed["items"]:
        fire = "[HOT] " if it["severity"] >= 4 else ""
        ticker = it.get("ticker") or ""
        headline = md_to_plain(it["headline"])
        prefix = f"{ticker} — " if ticker else ""
        suffix = " (Update)" if it.get("is_update") else ""
        lines.append(f"{fire}{prefix}{headline}{suffix}")
        if it.get("source"):
            lines.append(f"  Source: {md_to_plain(it['source'])}")
        if it.get("source_context"):
            lines.append(f"  Source (context): {md_to_plain(it['source_context'])}")
        if it.get("why"):
            lines.append(f"  Why it matters: {md_to_plain(it['why'])}")
        if it.get("action"):
            lines.append(f"  Action: {md_to_plain(it['action'])}")
        lines.append("")

    if parsed["macro"]:
        lines.append("Macro awareness")
        for b in parsed["macro"]:
            lines.append(f"- {md_to_plain(b)}")
        lines.append("")

    if parsed["housekeeping"]:
        lines.append("Price Trigger Housekeeping")
        for b in parsed["housekeeping"]:
            lines.append(f"- {md_to_plain(b)}")
        lines.append("")

    lines.append("Not investment advice. Generated by {}.".format(DEFAULT_FOOTER_MODEL))
    return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────
# Friday Weekly Review loader
# ────────────────────────────────────────────────────────────────────────

_WEEKLY_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
_WEEKLY_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
_WEEKLY_H3_RE = re.compile(r"^###\s+(.+?)\s*$")
# A standalone bold-only line is the W17-era ticker sub-header shape:
# `**VRT (VRT)**`. Modern weeks use `### Vertiv (VRT)` instead.
_WEEKLY_BOLD_LINE_RE = re.compile(r"^\*\*([^*]+)\*\*\s*$")
_WEEKLY_BULLET_LABEL_RE = re.compile(r"^\*\*[^*]+:?\*\*\s*")
_WEEKLY_STATUS_LABEL_RE = re.compile(r"^\*\*status signal:?\*\*", re.I)
_WEEKLY_WHY_FIT_LABEL_RE = re.compile(r"^\*\*why they fit:?\*\*", re.I)


def _extract_weekly_subhead(line: str) -> str | None:
    """Return the ticker sub-header text inside Wait-for-Deal Watch if the
    line introduces a new group, else None. Handles two shapes: H3 headers
    (`### Digital Realty (DLR)`) and bold-only paragraphs (`**VRT (VRT)**`)."""
    m = _WEEKLY_H3_RE.match(line)
    if m:
        return m.group(1).strip()
    m = _WEEKLY_BOLD_LINE_RE.match(line)
    if m:
        return m.group(1).strip()
    return None


def _load_weekly_review(vault_dir: Path, run_date: dt.date) -> dict | None:
    """Load the most recent weekly-review file. Returns None on non-Friday
    or when no weekly file exists. Returns {header, bullets_html, bullets_plain}.

    Up to 7 bullets are pulled from named macro/thesis sections in document
    order. Section matching is substring-based — a header like "Thesis
    Pressure Test" still matches the "thesis pressure test" phrase, which the
    prior exact-match silently failed.

    Wait-for-Deal Watch has nested ticker sub-headers (H3 or bold). For each
    sub-header we emit ONE summary bullet with the ticker name preserved,
    preferring the "Status signal" bullet (most actionable); the multi-bullet
    'What they do / Why they fit / Status signal' block underneath would
    otherwise appear stripped of its ticker context and look duplicated."""
    if run_date.weekday() != 4:  # Monday=0, Friday=4
        return None
    weekly_dir = vault_dir / "reports" / "weekly"
    if not weekly_dir.exists():
        return None
    candidates = sorted(weekly_dir.glob("*.md"), reverse=True)
    if not candidates:
        return None

    text = candidates[0].read_text(encoding="utf-8")

    wanted_phrases = ("dominant themes", "thesis pressure test",
                      "wait-for-deal watch", "what shifted")
    wait_for_deal_phrase = "wait-for-deal watch"

    bullets: list[str] = []
    current_section = ""
    in_wait_for_deal = False
    current_subhead: str | None = None
    group_bullets: list[str] = []

    def flush_wait_for_deal_group() -> None:
        """Pick one summary bullet for the open H3 ticker group and append
        it to `bullets` with the ticker header preserved."""
        nonlocal current_subhead, group_bullets
        if current_subhead and group_bullets:
            status = next((b for b in group_bullets if _WEEKLY_STATUS_LABEL_RE.match(b)), None)
            why_fit = next((b for b in group_bullets if _WEEKLY_WHY_FIT_LABEL_RE.match(b)), None)
            chosen = status or why_fit or group_bullets[0]
            cleaned = _WEEKLY_BULLET_LABEL_RE.sub("", chosen, count=1)
            bullets.append(f"**{current_subhead}** — {cleaned}")
        current_subhead = None
        group_bullets = []

    for line in text.splitlines():
        h2 = _WEEKLY_H2_RE.match(line)
        if h2:
            if in_wait_for_deal:
                flush_wait_for_deal_group()
            current_section = h2.group(1).strip().lower()
            in_wait_for_deal = wait_for_deal_phrase in current_section
            if len(bullets) >= 7:
                break
            continue

        if in_wait_for_deal:
            subhead = _extract_weekly_subhead(line)
            if subhead:
                flush_wait_for_deal_group()
                current_subhead = subhead
                if len(bullets) >= 7:
                    break
                continue
            bm = _WEEKLY_BULLET_RE.match(line)
            if bm and current_subhead:
                group_bullets.append(bm.group(1).strip())
            continue

        if any(w in current_section for w in wanted_phrases):
            bm = _WEEKLY_BULLET_RE.match(line)
            if bm:
                bullets.append(bm.group(1).strip())
                if len(bullets) >= 7:
                    break

    if in_wait_for_deal:
        flush_wait_for_deal_group()
    bullets = bullets[:7]

    if not bullets:
        return None

    # Infer week header from filename YYYY-WW.md or use run_date.
    header = candidates[0].stem
    m = re.match(r"^(\d{4})-(\d{2})$", header)
    if m:
        header = f"Week {int(m.group(2))} of {m.group(1)}"

    return {
        "header": header,
        "bullets_html": [md_to_html(b) for b in bullets],
        "bullets_plain": [md_to_plain(b) for b in bullets],
    }


# ────────────────────────────────────────────────────────────────────────
# PDF briefingData assembly
# ────────────────────────────────────────────────────────────────────────

def _split_paragraphs(text: str, target_chars: int = LEAD_BODY_MAX_CHARS) -> list[str]:
    """Return up to 2 paragraphs from a single plain-text string. Split at
    the nearest sentence boundary near the midpoint. If the text is too
    short, returns a single-element list."""
    text = text.strip()
    if len(text) < 200:
        return [text] if text else []
    text = text[:target_chars].rsplit(". ", 1)[0] + "." if len(text) > target_chars else text
    mid = len(text) // 2
    # Search around the midpoint for a sentence boundary.
    best = -1
    for i in range(max(0, mid - 80), min(len(text), mid + 80)):
        if text[i:i+2] == ". ":
            if best < 0 or abs(i - mid) < abs(best - mid):
                best = i + 1
    if best < 0:
        return [text]
    p1 = text[:best].strip()
    p2 = text[best:].strip()
    return [p1, p2] if p1 and p2 else [text]


def _truncate_sentences(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    # Prefer the last period within the cut.
    last_period = cut.rfind(". ")
    if last_period > max_chars * 0.5:
        return cut[:last_period + 1].strip()
    return cut.rstrip() + "…"


ACTION_RULES = [
    (re.compile(r"^\s*execute tranche[:\s]+(sell|buy|trim)\s+(\S+?)\s+(\S+?)\s+at\s+(\S+)", re.I),
     lambda m: f"{m.group(1).title()} {m.group(2)} {m.group(3)} @ {m.group(4)}"),
    (re.compile(r"^\s*run\s+deep[-\s]?dive", re.I),
     lambda m: "Rerun deep dive"),
    (re.compile(r"^\s*none\s*[—-]\s*HOLD", re.I),
     lambda m: "Hold — no chase"),
    (re.compile(r"^\s*none\b", re.I),
     lambda m: "Watch — no action"),
    (re.compile(r"^\s*watch\s+for\s+(.+)", re.I),
     lambda m: f"Watch — {m.group(1)[:25]}"),
]


def _verdict_pill(action_md: str) -> str:
    plain = md_to_plain(action_md)
    for pattern, fmt in ACTION_RULES:
        m = pattern.match(plain)
        if m:
            return fmt(m)[:VERDICT_MAX_CHARS]
    return _truncate_sentences(plain, VERDICT_MAX_CHARS)


AUTO_DEEP_DIVE_VERDICT_RE = re.compile(r"\bVerdict\s+\*{0,2}(HOLD|ADD|REDUCE|WATCH)\*{0,2}", re.I)


DEEP_DIVE_LABEL_RE = re.compile(r"(auto|fresh)\s+deep-dive", re.I)


def _item_verdict_pill(item: dict) -> str:
    """Pill for the PDF lead/card. Deep-dive items replace the Action line
    with a labeled bullet in `other_bullets` whose label contains one of
    the two news-analyst forms — `Auto deep-dive` (cached/reused) or
    `🤖 Fresh deep-dive` (run today as part of this alert) — and whose
    content names the HOLD/ADD/REDUCE/WATCH verdict. Extract it. Fall back
    to the action-line pill otherwise."""
    for label, content in item.get("other_bullets", []):
        if DEEP_DIVE_LABEL_RE.search(label):
            m = AUTO_DEEP_DIVE_VERDICT_RE.search(content)
            if m:
                return m.group(1).upper()[:VERDICT_MAX_CHARS]
            return _truncate_sentences(md_to_plain(content), VERDICT_MAX_CHARS)
    return _verdict_pill(item.get("action", ""))


def _format_date_long(d: str | dt.date) -> str:
    if isinstance(d, str):
        try:
            d = dt.date.fromisoformat(d)
        except ValueError:
            return str(d)
    return d.strftime("%B %-d, %Y") if sys.platform != "win32" else d.strftime("%B %#d, %Y")


def _issue_number(vault_dir: Path) -> int:
    daily = vault_dir / "reports" / "daily"
    if not daily.exists():
        return 1
    return len([p for p in daily.glob("????-??-??.md")])


def _build_briefing_data(parsed: dict, run_date: dt.date, vault_dir: Path) -> dict | None:
    """Build the dict consumed by templates/briefing-default.html. Returns
    None when there's nothing worth rendering (zero items → skip PDF)."""
    items = parsed["items"]
    if not items:
        return None

    # Lead = first item. (Items are already in the order the agent wrote
    # them; the agent is expected to rank-order them in Step 5.)
    lead_item = items[0]
    lead_body_plain = md_to_plain(lead_item.get("why", ""), omit_filename_wikilinks=True)
    lead_paragraphs = _split_paragraphs(lead_body_plain) or [""]

    cards = []
    for it in items[1:4]:
        cards.append({
            "ticker": it.get("ticker") or "",
            "price": "",
            "priceLabel": "",
            "headline": md_to_plain(it["headline"], omit_filename_wikilinks=True),
            "body": _truncate_sentences(md_to_plain(it.get("why", ""), omit_filename_wikilinks=True), CARD_BODY_MAX_CHARS),
            "data": "",
            "source": md_to_plain(it.get("source", "").split(" — ")[0], omit_filename_wikilinks=True) if it.get("source") else "",
            "verdict": _item_verdict_pill(it),
        })

    macro_items = []
    for bullet in parsed["macro"][:MACRO_PDF_LIMIT]:
        plain = md_to_plain(bullet)
        title_split = plain.split(" — ", 1)
        if len(title_split) == 2 and len(title_split[0]) < 50:
            macro_items.append({"title": title_split[0], "body": title_split[1]})
        else:
            # Use the first ~40 chars as title.
            first_dot = plain.find(". ")
            if first_dot > 0 and first_dot < 60:
                macro_items.append({"title": plain[:first_dot], "body": plain[first_dot + 2:]})
            else:
                macro_items.append({"title": plain[:50], "body": plain[50:] if len(plain) > 50 else ""})

    return {
        "wordmark": "Trading Journal",
        "date": _format_date_long(run_date),
        "tagline": "Positions, catalysts, and macro.",
        "issue": _issue_number(vault_dir),
        "lead": {
            "ticker": lead_item.get("ticker") or "",
            "price": "",
            "priceLabel": "",
            "headline": md_to_plain(lead_item["headline"], omit_filename_wikilinks=True),
            "body": lead_paragraphs,
            "data": "",
            "source": md_to_plain(lead_item.get("source", "").split(" — ")[0], omit_filename_wikilinks=True) if lead_item.get("source") else "",
            "verdict": _item_verdict_pill(lead_item),
        },
        "cards": cards,
        "macro": macro_items,
        "footerLeft": "Personal briefing · not for distribution",
        "footerRight": None,
    }


# ────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", required=True, help="Report date YYYY-MM-DD")
    ap.add_argument("--vault-dir", default="vault",
                    help="Vault root (default: vault — relative to CWD)")
    ap.add_argument("--email-template", default=str(HERE / "templates" / "email-default.html.j2"),
                    help="Path to Jinja2 email template")
    ap.add_argument("--pdf-template", default=str(HERE / "templates" / "briefing-default.html"),
                    help="Path to HTML PDF template")
    ap.add_argument("--dry-run", action="store_true",
                    help="Render everything but skip the Resend send")
    ap.add_argument("--with-pdf", action="store_true",
                    help="Opt in to the PDF render step. Disabled by default "
                         "to keep the daily hot path lean — Playwright + "
                         "Chromium install dominated runtime on GH Actions.")
    ap.add_argument("--out-dir", default=str(HERE),
                    help="Where to write the brief.html / brief.txt inspection "
                         "artifacts (default: news-visual/). Useful for local "
                         "dry-runs into a temp dir without touching the tracked "
                         "scratch paths. briefing-data.js still lands next to "
                         "the PDF template — its path is template-relative.")
    ap.add_argument("--subject", help="Override the email subject line")
    ap.add_argument("--preheader", help="Override the inbox preheader")
    args = ap.parse_args()

    vault_dir = Path(args.vault_dir)
    report_path = vault_dir / "reports" / "daily" / f"{args.date}.md"
    if not report_path.exists():
        print(f"ERROR: report not found: {report_path}", file=sys.stderr)
        return 2

    try:
        run_date = dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"ERROR: --date must be YYYY-MM-DD (got: {args.date!r})", file=sys.stderr)
        return 2

    parsed = parse_report(report_path)
    fm_email = parsed["frontmatter"].get("email") or {}
    if args.subject:
        fm_email["subject"] = args.subject
    if args.preheader:
        fm_email["preheader"] = args.preheader

    weekly = _load_weekly_review(vault_dir, run_date)
    context = _build_email_context(parsed, fm_email, weekly)

    try:
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
    except ImportError:
        print(
            "ERROR: jinja2 is required. Install with: "
            "pip install -r news-visual/requirements.txt",
            file=sys.stderr,
        )
        return 3

    template_path = Path(args.email_template)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        undefined=StrictUndefined,
        keep_trailing_newline=False,
    )
    template = env.get_template(template_path.name)
    html_body = template.render(**context)

    text_body = _render_plaintext(parsed, weekly)

    # Write HTML + text artifacts for inspection (also the interface the old
    # pipeline used; dry-runs and log-checks expect them). Default location
    # is news-visual/, overridable via --out-dir for local dry-runs.
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "brief.html").write_text(html_body, encoding="utf-8")
    (out_dir / "brief.txt").write_text(text_body, encoding="utf-8")

    # PDF render is opt-in via --with-pdf (skipped by default and on quiet days).
    pdf_path: Path | None = None
    briefing_data = _build_briefing_data(parsed, run_date, vault_dir) if args.with_pdf else None
    if briefing_data and args.with_pdf:
        pdf_path = vault_dir / "reports" / "daily" / "pdf" / f"{args.date}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import render_briefing
            data_js = HERE / "briefing-data.js"
            render_briefing.write_data(briefing_data, data_js_path=str(data_js))
            render_briefing.render_pdf(
                template_path=args.pdf_template,
                output_pdf_path=str(pdf_path),
            )
        except Exception as e:  # Playwright/Chromium can fail in sandboxes.
            print(f"WARN: PDF render failed ({type(e).__name__}: {e}); sending without attachment", file=sys.stderr)
            pdf_path = None

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "report": str(report_path),
            "subject": context["subject"],
            "preheader": context["preheader"],
            "items": len(parsed["items"]),
            "macro_bullets": len(parsed["macro"]),
            "housekeeping_rows": len(parsed["housekeeping"]),
            "broader_triggers": len(parsed.get("broader_triggers", [])),
            "active_pre_earnings": len(parsed.get("active_pre_earnings", [])),
            "friday_weekly_review": bool(weekly),
            "html_bytes": len(html_body),
            "text_bytes": len(text_body),
            "pdf_path": str(pdf_path) if pdf_path else None,
        }, indent=2))
        return 0

    try:
        import send_brief
    except ImportError as e:
        print(f"ERROR: failed to import send_brief ({e})", file=sys.stderr)
        return 3

    attachments = [pdf_path] if pdf_path else None
    try:
        msg_id = send_brief.send(
            subject=context["subject"],
            html_body=html_body,
            text_body=text_body,
            attachments=attachments,
        )
    except Exception as e:
        print(f"ERROR: send_brief failed ({type(e).__name__}: {e})", file=sys.stderr)
        return 4

    print(f"Sent. resend_id={msg_id} pdf={'yes' if pdf_path else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
