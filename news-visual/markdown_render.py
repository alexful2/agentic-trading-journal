"""
markdown_render.py

Inline-only markdown converters used by build_and_send.py.

Two surfaces:
- md_to_html(text): inline markdown → safe inline HTML (for email bodies).
  Handles `**bold**`, `*italic*`, `` `code` ``, `[label](url)`, `[[ref|display]]`
  and `[[ref]]` wikilinks. HTML-escapes text content but not markup.
- md_to_plain(text): strip all markdown → plain text (for PDF
  briefing-data.js values that the PDF template HTML-escapes itself).

Both strip wikilinks the same way: `[[A|B]]` → `B`; `[[A]]` → `A` unless `A`
looks like a trading-journal filename reference (YYYY-MM-DD prefix/suffix or
TICKER-YYYY-MM-DD), in which case the wikilink is omitted entirely.
"""

from __future__ import annotations

import html
import re


WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|([^\[\]]+))?\]\]")
LINK_RE = re.compile(r"\[([^\[\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.DOTALL)
CODE_RE = re.compile(r"`([^`]+)`")

# Deep-dive / note filename patterns: TICKER-YYYY-MM-DD, YYYY-MM-DD TICKER, YYYY-MM-DD
FILENAME_REF_RE = re.compile(
    r"^(?:[A-Z]{2,6}-)?\d{4}-\d{2}-\d{2}(?:\s+[A-Z]{2,6}.*)?$"
)


def _is_filename_ref(ref: str) -> bool:
    return bool(FILENAME_REF_RE.match(ref.strip()))


def _strip_wikilinks(text: str, omit_filename_refs: bool = True) -> str:
    """Replace wikilinks with their display text. If omit_filename_refs is
    True, plain `[[YYYY-MM-DD ...]]` refs are dropped entirely since they
    reference internal notes and mean nothing to an external reader."""
    def repl(m: re.Match) -> str:
        ref, display = m.group(1), m.group(2)
        if display:
            return display
        if omit_filename_refs and _is_filename_ref(ref):
            return ""
        return ref
    out = WIKILINK_RE.sub(repl, text)
    # collapse doubled spaces and space-before-punct introduced by omission
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([,.;:)])", r"\1", out)
    return out.strip()


def md_to_html(
    text: str,
    link_style: str = "color: #1a73e8; text-decoration: none;",
    omit_filename_wikilinks: bool = False,
) -> str:
    """Convert inline markdown to inline HTML for email bodies. Wikilinks
    become plain display text (brackets stripped). Filename-style wikilinks
    are stripped-to-text by default (show the display), not omitted, since
    email readers can still make sense of "2026-04-20 NVDA thesis" as
    context. Set omit_filename_wikilinks=True for the PDF path."""
    if not text:
        return ""
    # Wikilinks first — they're internal, strip before anything else.
    text = _strip_wikilinks(text, omit_filename_refs=omit_filename_wikilinks)

    # Extract [label](url) links before HTML-escaping so URLs survive.
    placeholders: list[str] = []
    def link_sub(m: re.Match) -> str:
        label = html.escape(m.group(1), quote=True)
        url = html.escape(m.group(2), quote=True)
        ph = f"\x00L{len(placeholders)}\x00"
        placeholders.append(
            f'<a href="{url}" target="_blank" rel="noopener" style="{link_style}">{label}</a>'
        )
        return ph
    text = LINK_RE.sub(link_sub, text)

    # HTML-escape remaining text content.
    text = html.escape(text, quote=False)

    # Restore links.
    for i, tag in enumerate(placeholders):
        text = text.replace(f"\x00L{i}\x00", tag)

    # Inline formatting (bold/italic/code). Operates on the escaped string,
    # so we match literal ** and * which escape() left untouched.
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    text = CODE_RE.sub(r"<code>\1</code>", text)

    return text


def md_to_plain(text: str, omit_filename_wikilinks: bool = False) -> str:
    """Strip all inline markdown → plain text. Used for both the email
    plain-text fallback (default: keep filename-ref display text) and the
    PDF briefingData values (pass `omit_filename_wikilinks=True` to drop
    internal note refs entirely for a tighter card layout)."""
    if not text:
        return ""
    text = _strip_wikilinks(text, omit_filename_refs=omit_filename_wikilinks)
    # [label](url) → label
    text = LINK_RE.sub(r"\1", text)
    # **bold** → bold; *italic* → italic; `code` → code
    text = BOLD_RE.sub(r"\1", text)
    text = ITALIC_RE.sub(r"\1", text)
    text = CODE_RE.sub(r"\1", text)
    return text.strip()


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "html"
    sample = sys.stdin.read()
    if mode == "plain":
        print(md_to_plain(sample))
    else:
        print(md_to_html(sample))
