"""
parse_report.py

Parse a daily markdown report into a structured dict. The markdown is the
source of truth for content; editorial bits (subject, preheader) live in
frontmatter under the `email:` key.

Output is raw markdown strings per field. Inline markdown → HTML/plain
conversion happens in markdown_render.py so parsing stays representation-
neutral. Used by build_and_send.py.
"""

from __future__ import annotations

import re
from pathlib import Path


HEADER_RE = re.compile(r"^###\s+(🔥\s+)?(.+?)\s*$")
BULLET_RE = re.compile(r"^-\s+(.*)$")
LABELED_BULLET_RE = re.compile(r"^-\s+\*\*(.+?):\*\*\s*(.*)$")
TICKER_HEADLINE_RE = re.compile(r"^([A-Z]{2,6})\s*[—–-]\s*(.+?)\s*$")
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$")
UPDATE_SUFFIX_RE = re.compile(r"\s*\(Update[^)]*\)\s*$")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal YAML-ish frontmatter reader. Supports top-level scalars and
    one level of nesting (for `email: {subject, preheader}`). No list
    support beyond recognising `tags:` — we don't use tags downstream."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    header = text[3:end]
    body = text[end + 4:].lstrip("\n")

    fm: dict = {}
    parent: str | None = None
    for raw in header.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        # Nested key under a parent map
        if raw.startswith("  ") and parent and ":" in raw:
            key, _, val = raw.strip().partition(":")
            val = val.strip().strip('"').strip("'")
            if isinstance(fm.get(parent), dict):
                fm[parent][key.strip()] = val
            continue
        if ":" not in raw:
            parent = None
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val == "":
            fm[key] = {}
            parent = key
        else:
            fm[key] = val
            parent = None
    return fm, body


def _strip_update(headline: str) -> tuple[str, bool]:
    m = UPDATE_SUFFIX_RE.search(headline)
    if m:
        return headline[: m.start()].rstrip(), True
    return headline, False


def parse_report(path: Path) -> dict:
    """Parse a daily report markdown. Returns the structured dict consumed
    by build_and_send.py."""
    text = Path(path).read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)

    title = ""
    date_long = ""
    for line in body.splitlines():
        m = TITLE_RE.match(line)
        if m:
            title = m.group(1).strip()
            dm = re.search(r"—\s*(.+)$", title)
            if dm:
                date_long = dm.group(1).strip()
            break

    items: list[dict] = []
    macro: list[str] = []
    housekeeping: list[str] = []
    broader_triggers: list[str] = []
    active_pre_earnings: list[str] = []
    section = "preamble"
    current: dict | None = None

    def flush():
        nonlocal current
        if current is not None:
            items.append(current)
            current = None

    for raw in body.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("## "):
            flush()
            heading = stripped[3:].strip().lower()
            if heading.startswith("macro awareness"):
                section = "macro"
            elif heading.startswith("price trigger housekeeping"):
                section = "housekeeping"
            elif heading.startswith("broader price triggers"):
                section = "broader_triggers"
            elif heading.startswith("active pre-earnings windows"):
                section = "active_pre_earnings"
            else:
                section = "other"
            continue

        if stripped == "---":
            flush()
            continue

        if stripped.startswith("*Not investment advice") or stripped.startswith("*Generated"):
            flush()
            section = "footer"
            continue

        hm = HEADER_RE.match(stripped) if stripped.startswith("### ") else None
        if hm:
            flush()
            section = "items"
            fire = bool(hm.group(1))
            raw_headline = hm.group(2).strip()
            severity = 4 if fire else 3
            tm = TICKER_HEADLINE_RE.match(raw_headline)
            if tm:
                ticker = tm.group(1)
                rest = tm.group(2).strip()
            else:
                ticker = None
                rest = raw_headline
            headline, is_update = _strip_update(rest)
            current = {
                "ticker": ticker,
                "severity": severity,
                "headline": headline,
                "headline_full": raw_headline,
                "is_update": is_update,
                "source": "",
                "source_context": None,
                "why": "",
                "action": "",
                "other_bullets": [],
            }
            continue

        if section == "items" and current is not None:
            lbm = LABELED_BULLET_RE.match(stripped)
            if lbm:
                label = lbm.group(1).strip()
                content = lbm.group(2).strip()
                key = label.lower()
                if key == "source":
                    current["source"] = content
                elif key in {"source (context)", "context"}:
                    current["source_context"] = content
                elif key == "why it matters":
                    current["why"] = content
                elif key == "action":
                    current["action"] = content
                else:
                    current["other_bullets"].append((label, content))
                continue

        if section == "macro":
            bm = BULLET_RE.match(stripped)
            if bm:
                macro.append(bm.group(1).strip())
        elif section == "housekeeping":
            bm = BULLET_RE.match(stripped)
            if bm:
                housekeeping.append(bm.group(1).strip())
        elif section == "broader_triggers":
            bm = BULLET_RE.match(stripped)
            if bm:
                broader_triggers.append(bm.group(1).strip())
        elif section == "active_pre_earnings":
            bm = BULLET_RE.match(stripped)
            if bm:
                active_pre_earnings.append(bm.group(1).strip())

    flush()

    return {
        "frontmatter": fm,
        "title": title,
        "date_long": date_long,
        "items": items,
        "macro": macro,
        "housekeeping": housekeeping,
        "broader_triggers": broader_triggers,
        "active_pre_earnings": active_pre_earnings,
    }


if __name__ == "__main__":
    import json
    import sys
    p = Path(sys.argv[1])
    print(json.dumps(parse_report(p), indent=2, ensure_ascii=False))
