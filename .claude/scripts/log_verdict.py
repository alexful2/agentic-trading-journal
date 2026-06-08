#!/usr/bin/env python3
"""
Append a row to the deep-dive verdict ledger.

The ledger lives at vault/deep-dives/_verdicts.md as a markdown table:

| Date | Ticker | Verdict | Price at verdict | Deep-dive file |

Producer: stock-deep-dive skill calls this after writing a deep-dive file,
passing the ticker, verdict, snapshot price, and the new file's name. Ledger
rows accumulate forever — quarterly-review and check_verdict_drift.py read
them. No automatic pruning.

Comparison files (TICKER_A-vs-TICKER_B-*.md) are NOT logged here — their
verdict is an allocation answer, not a per-ticker call.

Usage (one row):
    python log_verdict.py --ticker NVDA --verdict ADD --price 47.5 \
        --file NVDA-2026-04-24.md

Usage (bootstrap from existing files):
    python log_verdict.py --bootstrap                 # rebuild ledger from scratch
    python log_verdict.py --bootstrap --dry-run       # preview without writing
"""

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path


LEDGER_HEADER = """| Date | Ticker | Verdict | Price at verdict | Deep-dive file | Break-even P |
| --- | --- | --- | --- | --- | --- |
"""


def _ledger_path(vault_root):
    return vault_root / "deep-dives" / "_verdicts.md"


def _read_ledger(path):
    """Return list of row strings (no header). Creates the file with a
    header if it doesn't exist yet."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_ledger_intro() + LEDGER_HEADER, encoding="utf-8")
        return []
    text = path.read_text(encoding="utf-8")
    # Find the header line and return everything after the separator.
    rows = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Date "):
            in_table = True
            continue
        if in_table and re.match(r"^\|\s*-+", line):
            continue
        if in_table and line.startswith("|"):
            rows.append(line)
        elif in_table and not line.strip():
            # Allow blank line at end of table without breaking.
            continue
        elif in_table and not line.startswith("|"):
            in_table = False
    return rows


def _ledger_intro():
    return (
        "# Deep-dive verdict ledger\n\n"
        "Append-only log of deep-dive verdicts. Row per single-ticker deep-dive at the moment it was written.\n"
        "Comparison files are not logged here. Used by `check_verdict_drift.py` (daily) and `quarterly-review` (calibration).\n\n"
        "`Break-even P` = the Implied Expectations break-even probability (Step 4c) at verdict time — "
        "captured here because deep-dive files are auto-deleted when superseded. `—` when the dive named no "
        "quantifiable break-even. Feeds a future calibration pass once enough verdicts resolve (not yet — n too small). "
        "`--bootstrap` rebuilds from deep-dive files and resets this column to `—`.\n\n"
        "Maintained by `.claude/scripts/log_verdict.py`. To rebuild: `python .claude/scripts/log_verdict.py --bootstrap`.\n\n"
    )


def _write_ledger(path, rows):
    body = _ledger_intro() + LEDGER_HEADER + "\n".join(rows) + ("\n" if rows else "")
    path.write_text(body, encoding="utf-8")


def _row(date_str, ticker, verdict, price, fname, breakeven=None):
    price_str = f"${price:.2f}" if price is not None else "—"
    # Break-even probability from the deep-dive's Implied Expectations block
    # (Step 4c) — captured here because deep-dive files are auto-deleted when
    # superseded, so the ledger is the only durable home for the prediction.
    # Appended at the END so check_verdict_drift.py's parts[:5] indexing is
    # unaffected. "—" when the dive produced no quantifiable break-even.
    be_str = f"{breakeven * 100:.0f}%" if breakeven is not None else "—"
    # Backticked, not [[wikilinked]]: these pointers go stale when the
    # deep-dive auto-cleanup deletes superseded files, and [[dead links]]
    # render as phantom/empty notes in Obsidian. Backticks keep the
    # reference readable without creating a ghost note.
    return f"| {date_str} | {ticker.upper()} | {verdict.upper()} | {price_str} | `{fname.replace('.md', '')}` | {be_str} |"


def _row_already_logged(rows, fname):
    """Check whether a row already references this deep-dive filename.
    Used to make append idempotent (the daily auto-deep-dive chain may
    re-invoke the skill and we don't want duplicate ledger rows)."""
    base = fname.replace('.md', '')
    # Match either format so idempotency holds across the legacy [[ ]] rows
    # and the current `backtick` rows.
    return any((f"`{base}`" in r) or (f"[[{base}]]" in r) for r in rows)


def _parse_deep_dive(path):
    """Extract (date, ticker, verdict, price) from a deep-dive markdown file.
    Returns None if any field can't be parsed.

    - date / ticker / verdict: from YAML frontmatter (`date:`, `ticker:`, `verdict:`)
    - price: from the Snapshot table line `| **Price** | $X.XX (...) |`
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        return None
    fm = fm_match.group(1)

    def grab(key):
        m = re.search(rf"^{key}\s*:\s*(.+?)\s*$", fm, re.MULTILINE)
        return m.group(1).strip() if m else None

    date_str = grab("date")
    ticker = grab("ticker")
    verdict = grab("verdict")
    if not (date_str and ticker and verdict):
        return None

    price_match = re.search(r"\|\s*\*\*Price\*\*\s*\|\s*\$?([\d,]+\.?\d*)", text)
    price = None
    if price_match:
        try:
            price = float(price_match.group(1).replace(",", ""))
        except ValueError:
            price = None

    return (date_str, ticker.upper(), verdict.upper(), price)


def _bootstrap(vault_root, dry_run=False):
    deep_dives_dir = vault_root / "deep-dives"
    if not deep_dives_dir.exists():
        print(f"ERROR: {deep_dives_dir} not found", file=sys.stderr)
        return 1

    ledger_path = _ledger_path(vault_root)
    rows = []
    skipped = []
    for path in sorted(deep_dives_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        # Skip comparison files (TICKER_A-vs-TICKER_B-YYYY-MM-DD.md).
        if "-vs-" in path.stem:
            skipped.append((path.name, "comparison file"))
            continue
        parsed = _parse_deep_dive(path)
        if not parsed:
            skipped.append((path.name, "couldn't parse frontmatter or price"))
            continue
        date_str, ticker, verdict, price = parsed
        rows.append(_row(date_str, ticker, verdict, price, path.name))

    if dry_run:
        print(f"# DRY RUN — would write {len(rows)} rows to {ledger_path}\n")
        for r in rows:
            print(r)
        if skipped:
            print(f"\n# Skipped ({len(skipped)}):")
            for name, why in skipped:
                print(f"#   - {name}: {why}")
        return 0

    _write_ledger(ledger_path, rows)
    print(f"Bootstrapped {len(rows)} verdict rows to {ledger_path}", file=sys.stderr)
    if skipped:
        print(f"Skipped {len(skipped)} files:", file=sys.stderr)
        for name, why in skipped:
            print(f"  - {name}: {why}", file=sys.stderr)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default="vault")
    parser.add_argument("--ticker")
    parser.add_argument("--verdict")
    parser.add_argument("--price", type=float)
    parser.add_argument("--file", help="Deep-dive filename (e.g., NVDA-2026-04-24.md)")
    parser.add_argument("--date", help="Override date (default: today)")
    parser.add_argument("--breakeven-prob", type=float,
                        help="Break-even probability (0-1) from the deep-dive Implied Expectations block, "
                             "e.g. 0.45. Optional; recorded in the ledger so it survives deep-dive file cleanup.")
    parser.add_argument("--bootstrap", action="store_true", help="Rebuild ledger from existing deep-dive files")
    parser.add_argument("--dry-run", action="store_true", help="With --bootstrap: preview without writing")
    args = parser.parse_args()

    vault_root = Path(args.vault)
    if not vault_root.exists():
        print(f"ERROR: vault root not found: {vault_root}", file=sys.stderr)
        sys.exit(1)

    if args.bootstrap:
        sys.exit(_bootstrap(vault_root, dry_run=args.dry_run))

    if not (args.ticker and args.verdict and args.file):
        print("ERROR: --ticker, --verdict, and --file are required (or use --bootstrap)", file=sys.stderr)
        sys.exit(2)

    valid_verdicts = {"HOLD", "ADD", "REDUCE", "WATCH"}
    if args.verdict.upper() not in valid_verdicts:
        print(f"ERROR: --verdict must be one of {sorted(valid_verdicts)}", file=sys.stderr)
        sys.exit(2)

    date_str = args.date or date.today().isoformat()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"ERROR: --date must be YYYY-MM-DD, got {date_str!r}", file=sys.stderr)
        sys.exit(2)

    if args.breakeven_prob is not None and not (0.0 <= args.breakeven_prob <= 1.0):
        print(f"ERROR: --breakeven-prob must be between 0 and 1, got {args.breakeven_prob}", file=sys.stderr)
        sys.exit(2)

    ledger_path = _ledger_path(vault_root)
    rows = _read_ledger(ledger_path)
    if _row_already_logged(rows, args.file):
        print(f"Row for {args.file} already in ledger; skipping (idempotent).", file=sys.stderr)
        return

    rows.append(_row(date_str, args.ticker, args.verdict, args.price, args.file, args.breakeven_prob))
    _write_ledger(ledger_path, rows)
    be_note = f" be={args.breakeven_prob * 100:.0f}%" if args.breakeven_prob is not None else ""
    print(f"Logged: {args.ticker.upper()} {args.verdict.upper()} @ ${args.price:.2f} ({args.file}){be_note}", file=sys.stderr)


if __name__ == "__main__":
    main()
