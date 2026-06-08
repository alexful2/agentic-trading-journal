#!/usr/bin/env python3
"""
Apply a `## Proposed Watchlist Updates` block from a deep-dive, pre-earnings,
or pre-ipo file directly to `vault/watchlist.md`.

Replaces the old propose-via-block / weekly-review-promotes pattern. With
Pushover notifications wired into intraday triggers, trigger freshness now
matters more than the consolidation loop's batching benefit — a Saturday
pre-earnings shouldn't sit unpromoted until Friday while the user is acting
on its tranches all week.

Idempotent: re-applying the same block is a no-op apart from refreshing
`Last Reviewed` to today (harmless). Each call updates rows by upsert, not
append-only.

Usage:
    python apply_watchlist_updates.py PATH_TO_FILE
                                      [--watchlist vault/watchlist.md]
                                      [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

WATCHLIST_DEFAULT = "vault/watchlist.md"


def parse_proposal_block(md_text: str) -> dict | None:
    """Return {'price_trigger': dict|None, 'add_tranches': list, 'remove_tranches': list}
    or None if there's no actionable proposal in the file."""
    block_match = re.search(
        r"^## Proposed Watchlist Updates\s*\n(.*?)(?=^## |\Z)",
        md_text,
        re.MULTILINE | re.DOTALL,
    )
    if not block_match:
        return None
    body = block_match.group(1)

    proposal: dict = {"price_trigger": None, "add_tranches": [], "remove_tranches": []}

    pt_match = re.search(
        r"### Price Trigger\s*\n(.*?)(?=^###|\Z)", body, re.MULTILINE | re.DOTALL
    )
    if pt_match:
        pt_body = pt_match.group(1)
        if "No changes proposed." not in pt_body:
            pt: dict = {}
            for line in pt_body.splitlines():
                m = re.match(r"^\s*-\s+\*\*([^:]+):\*\*\s*(.+?)$", line)
                if not m:
                    continue
                key = m.group(1).strip().lower().replace(" ", "_").replace("-", "_")
                val = m.group(2).strip()
                # Strip trailing italic notes like *(deep-dive owns long-horizon...)*
                val = re.sub(r"\s*\*\(.*?\)\*\s*$", "", val).strip()
                pt[key] = val
            if pt.get("ticker"):
                proposal["price_trigger"] = pt

    tr_match = re.search(
        r"### Planned Tranches\s*\n(.*?)(?=^###|\Z)", body, re.MULTILINE | re.DOTALL
    )
    if tr_match:
        for line in tr_match.group(1).splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            line = line.lstrip("-").strip()
            if line.startswith("Add:"):
                parsed = parse_tranche_line(line[len("Add:") :].strip())
                if parsed:
                    proposal["add_tranches"].append(parsed)
            elif line.startswith("Remove:"):
                parsed = parse_tranche_line(line[len("Remove:") :].strip())
                if parsed:
                    proposal["remove_tranches"].append(parsed)

    if not (
        proposal["price_trigger"]
        or proposal["add_tranches"]
        or proposal["remove_tranches"]
    ):
        return None
    return proposal


def parse_tranche_line(line: str) -> dict | None:
    """Parse `TICKER | {Buy|Trim} | size | @price | expires YYYY-MM-DD | order=X | note...`"""
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 4:
        return None
    out: dict = {"ticker": parts[0].upper(), "raw": line, "note": ""}
    action_raw = parts[1].lower()
    if action_raw not in ("buy", "trim"):
        return None
    out["action"] = "Buy" if action_raw == "buy" else "Trim"
    out["size"] = parts[2]
    price_raw = parts[3].lstrip("@").strip().replace("$", "").replace(",", "")
    if price_raw.lower() == "market":
        out["at_price"] = None  # event-driven, not table-eligible
    else:
        try:
            out["at_price"] = float(price_raw)
        except ValueError:
            out["at_price"] = None
    out["expires"] = ""
    # None means "proposal didn't specify" — apply_tranches preserves the
    # existing row's order in that case, and only defaults to Alert for
    # genuinely new rows. Older proposal blocks (pre-Order column) lack
    # order= entirely; treating them as a request to downgrade matched
    # rows to Alert silently broke Conditional GTC rows.
    out["order"] = None
    notes: list[str] = []
    for p in parts[4:]:
        m = re.match(r"^expires\s+(\d{4}-\d{2}-\d{2})$", p, re.IGNORECASE)
        if m:
            out["expires"] = m.group(1)
            continue
        m = re.match(r"^order\s*=\s*(.+)$", p, re.IGNORECASE)
        if m:
            out["order"] = m.group(1).strip()
            continue
        if p:
            notes.append(p)
    out["note"] = " ".join(notes).strip()
    return out


def _parse_price(s: str) -> float | None:
    s = (s or "").replace("$", "").replace(",", "").strip()
    if s in ("", "—", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _split_table(section: str) -> tuple[list[str], int, list[str]]:
    """Return (lines, header_idx, header_cells_lowercased)."""
    lines = section.splitlines(keepends=True)
    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "Ticker" in line.split("|")[1] if line.count("|") >= 2 else False:
            header_idx = i
            break
    if header_idx < 0:
        # Fallback: any header row that mentions Ticker
        for i, line in enumerate(lines):
            if line.strip().startswith("|") and "Ticker" in line:
                header_idx = i
                break
    header_cells = []
    if header_idx >= 0:
        header_cells = [
            c.strip().lower() for c in lines[header_idx].strip().strip("|").split("|")
        ]
    return lines, header_idx, header_cells


def _format_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |\n"


def upsert_price_trigger(
    watchlist_text: str, pt: dict, today_iso: str
) -> tuple[str, str]:
    confidence = (pt.get("confidence") or "med").lower()
    ticker = pt["ticker"].upper()
    if confidence == "low":
        return watchlist_text, f"price-trigger {ticker}: skipped (confidence=low)"

    section_re = re.compile(
        r"(^## Price Triggers\s*\n.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    section_match = section_re.search(watchlist_text)
    if not section_match:
        return watchlist_text, f"price-trigger {ticker}: section not found"

    section = section_match.group(1)
    lines, header_idx, header_cells = _split_table(section)
    if header_idx < 0:
        return watchlist_text, f"price-trigger {ticker}: header not found"

    header_map = {h: i for i, h in enumerate(header_cells)}
    last_reviewed_idx = header_map.get("last reviewed")

    # Find target row
    target_idx = -1
    for i in range(header_idx + 2, len(lines)):
        line = lines[i].strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0].upper() == ticker:
            target_idx = i
            break

    if target_idx >= 0:
        cells = [c.strip() for c in lines[target_idx].strip().strip("|").split("|")]
    else:
        cells = ["—"] * len(header_cells)

    while len(cells) < len(header_cells):
        cells.append("—")
    cells[0] = ticker

    field_to_header = {
        "buy_below": "buy below",
        "trim_above": "trim above",
        "funded_by": "funded-by",
        "prefer_over": "prefer-over",
        "note": "note",
    }
    any_changed = False
    for field, hkey in field_to_header.items():
        col_idx = header_map.get(hkey)
        if col_idx is None or field not in pt:
            continue
        val = pt[field].strip()
        # Sentinel "unchanged" may be followed by a parenthetical annotation
        # (the italic *(...)* form is already stripped at parse time, but a
        # plain "(...)" is not). Match the sentinel as a prefix so both work.
        if re.match(r"^unchanged\s*(\(|$)", val, re.IGNORECASE):
            continue
        if field in ("buy_below", "trim_above"):
            # Price columns: strip trailing plain parenthetical annotation,
            # then refuse to write unparseable values (defends against
            # template drift dumping prose into a numeric cell).
            val = re.sub(r"\s*\(.*?\)\s*$", "", val).strip()
            if val not in ("", "—") and _parse_price(val) is None:
                continue
        if val in ("", "—"):
            cells[col_idx] = "—"
        else:
            cells[col_idx] = val
        any_changed = True

    # Bump Last Reviewed when there's a real change OR when this is a deep-dive
    # confirm (no change but explicit). The skill caller decides whether to
    # call us; if it called, we treat it as a re-confirm and bump the date.
    if last_reviewed_idx is not None:
        cells[last_reviewed_idx] = today_iso

    new_line = _format_row(cells)
    if target_idx >= 0:
        lines[target_idx] = new_line
        action = "updated" if any_changed else "re-confirmed"
    else:
        # No existing row + nothing actually changed (all-unchanged proposal,
        # e.g. a pre-earnings whose price-trigger section explicitly defers
        # to the deep-dive levels) → skip the insert. Otherwise we'd pollute
        # the table with a row of all em-dashes that the trigger parser
        # silently ignores anyway.
        if not any_changed:
            return watchlist_text, f"price-trigger {ticker}: skipped (no row exists and proposal is all-unchanged)"
        last_data = header_idx + 1
        for i in range(header_idx + 2, len(lines)):
            if lines[i].strip().startswith("|"):
                last_data = i
        lines.insert(last_data + 1, new_line)
        action = "inserted"

    new_section = "".join(lines)
    return watchlist_text.replace(section, new_section, 1), f"price-trigger {ticker}: {action}"


def apply_tranches(
    watchlist_text: str,
    add_list: list[dict],
    remove_list: list[dict],
    today_iso: str,
) -> tuple[str, list[str]]:
    summaries: list[str] = []
    section_re = re.compile(
        r"(^## Planned Tranches\s*\n.*?)(?=^## |\Z|^---\s*\n\s*\*Last updated)",
        re.MULTILINE | re.DOTALL,
    )
    section_match = section_re.search(watchlist_text)
    if not section_match:
        section_re = re.compile(
            r"(^## Planned Tranches\s*\n.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
        )
        section_match = section_re.search(watchlist_text)
    if not section_match:
        return watchlist_text, ["tranches: section not found"]

    section = section_match.group(1)
    lines, header_idx, header_cells = _split_table(section)
    if header_idx < 0:
        return watchlist_text, ["tranches: header not found"]
    header_map = {h: i for i, h in enumerate(header_cells)}

    def _row_match(cells: list[str], tr: dict, match_expires: bool) -> bool:
        if cells[0].upper() != tr["ticker"]:
            return False
        if cells[header_map.get("action", 1)].lower() != tr["action"].lower():
            return False
        existing_price = _parse_price(cells[header_map.get("at price", 3)])
        if existing_price is None or tr.get("at_price") is None:
            return False
        if abs(existing_price - tr["at_price"]) > 0.01:
            return False
        if match_expires and "expires" in header_map:
            existing_exp = cells[header_map["expires"]].strip()
            if existing_exp != tr.get("expires", ""):
                return False
        return True

    # Apply removes first (by Ticker + Action + At Price; ignore Expires)
    for tr in remove_list:
        if tr.get("at_price") is None:
            summaries.append(
                f"tranche-remove skipped (no parseable price): {tr.get('ticker')} {tr.get('raw', '')[:60]}"
            )
            continue
        removed = False
        for i in range(header_idx + 2, len(lines)):
            if not lines[i].strip().startswith("|"):
                continue
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if _row_match(cells, tr, match_expires=False):
                lines[i] = ""
                removed = True
                summaries.append(
                    f"tranche-remove: {tr['ticker']} {tr['action']} @ ${tr['at_price']:g}"
                )
                break
        if not removed:
            summaries.append(
                f"tranche-remove target not found: {tr['ticker']} {tr['action']} @ ${tr['at_price']:g}"
            )
    lines = [l for l in lines if l != ""]

    # Apply adds — upsert (Ticker + Action + At Price + Expires)
    new_rows: list[str] = []
    for tr in add_list:
        if tr.get("at_price") is None:
            summaries.append(
                f"tranche-add skipped (event-driven or unparseable price): "
                f"{tr.get('ticker')} {tr.get('raw', '')[:60]}"
            )
            continue
        row_cells = ["—"] * len(header_cells)
        row_cells[header_map.get("ticker", 0)] = tr.get("ticker", "")
        if "action" in header_map:
            row_cells[header_map["action"]] = tr.get("action", "")
        if "size" in header_map:
            row_cells[header_map["size"]] = tr.get("size", "")
        if "at price" in header_map:
            row_cells[header_map["at price"]] = f"{tr['at_price']:g}"
        if "expires" in header_map:
            row_cells[header_map["expires"]] = tr.get("expires", "")
        if "order" in header_map:
            # None here means proposal didn't specify; default for new rows
            # is Alert. Matched rows preserve the existing order (patched in
            # below once we've found the match).
            row_cells[header_map["order"]] = tr.get("order") or "Alert"
        if "note" in header_map:
            row_cells[header_map["note"]] = tr.get("note", "")

        is_dup = False
        for i in range(header_idx + 2, len(lines)):
            if not lines[i].strip().startswith("|"):
                continue
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if _row_match(cells, tr, match_expires=True):
                # Preserve fields the proposal didn't override.
                if tr.get("order") is None and "order" in header_map:
                    order_idx = header_map["order"]
                    if order_idx < len(cells):
                        row_cells[order_idx] = cells[order_idx]
                lines[i] = _format_row(row_cells)
                is_dup = True
                summaries.append(
                    f"tranche-update (existing row): {tr['ticker']} {tr['action']} @ ${tr['at_price']:g} expires {tr.get('expires')}"
                )
                break
        if not is_dup:
            new_rows.append(_format_row(row_cells))
            summaries.append(
                f"tranche-add: {tr['ticker']} {tr['action']} @ ${tr['at_price']:g} expires {tr.get('expires')}"
            )

    if new_rows:
        last_data = header_idx + 1
        for i in range(header_idx + 2, len(lines)):
            if lines[i].strip().startswith("|"):
                last_data = i
        lines = lines[: last_data + 1] + new_rows + lines[last_data + 1 :]

    return watchlist_text.replace(section, "".join(lines), 1), summaries


def update_last_updated(text: str, today_iso: str) -> str:
    return re.sub(
        r"\*Last updated:\s*\d{4}-\d{2}-\d{2}\s*\*",
        f"*Last updated: {today_iso}*",
        text,
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_file")
    p.add_argument("--watchlist", default=WATCHLIST_DEFAULT)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    src = Path(args.source_file)
    wl = Path(args.watchlist)
    if not src.exists():
        print(f"ERROR: source file not found: {src}", file=sys.stderr)
        return 2
    if not wl.exists():
        print(f"ERROR: watchlist not found: {wl}", file=sys.stderr)
        return 2

    src_text = src.read_text(encoding="utf-8")
    proposal = parse_proposal_block(src_text)
    if proposal is None:
        print(f"No actionable proposal block in {src.name} — nothing to apply.")
        return 0

    today_iso = date.today().isoformat()
    wl_text = wl.read_text(encoding="utf-8")
    new_text = wl_text
    summaries: list[str] = []

    if proposal["price_trigger"]:
        new_text, summary = upsert_price_trigger(new_text, proposal["price_trigger"], today_iso)
        summaries.append(summary)

    if proposal["add_tranches"] or proposal["remove_tranches"]:
        new_text, tr_summaries = apply_tranches(
            new_text, proposal["add_tranches"], proposal["remove_tranches"], today_iso
        )
        summaries.extend(tr_summaries)

    if new_text != wl_text:
        new_text = update_last_updated(new_text, today_iso)

    if args.dry_run:
        print(f"[DRY RUN] would apply from {src.name}:")
        for s in summaries:
            print(f"  - {s}")
        return 0

    if new_text == wl_text:
        print(f"No effective changes from {src.name}.")
    else:
        wl.write_text(new_text, encoding="utf-8")
        print(f"Applied {src.name} → {wl}:")
    for s in summaries:
        print(f"  - {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
