from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import generate_dashboard


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
DEFAULT_PAGES_REPO = ROOT.parent / "trading-dashboard"
PUBLIC_FILES = ("index.html", ".nojekyll")

SENSITIVE_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:api[_-]?key|secret|password|passwd|token|oauth|private[_-]?key)\b", re.IGNORECASE),
    re.compile(r"\b(?:ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH_TOKEN|OPENAI_API_KEY|ALPACA_API_SECRET|PUSHOVER_(?:USER|TOKEN))\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def run(cmd: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git(pages_repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return run(["git", "-c", f"safe.directory={pages_repo.as_posix()}", *args], pages_repo)


def scan_public_output(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[str] = []
    for pattern in SENSITIVE_PATTERNS:
        for match in pattern.finditer(text):
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 40)
            snippet = re.sub(r"\s+", " ", text[start:end]).strip()
            findings.append(snippet)
            if len(findings) >= 10:
                return findings
    return findings


def copy_public_files(pages_repo: Path) -> None:
    for name in PUBLIC_FILES:
        src = DASHBOARD_DIR / name
        if not src.exists():
            raise FileNotFoundError(f"missing dashboard output: {src}")
        shutil.copy2(src, pages_repo / name)


def commit_and_push(pages_repo: Path, message: str, no_push: bool) -> str:
    git(pages_repo, ["add", *PUBLIC_FILES])
    status = git(pages_repo, ["status", "--porcelain", "--", *PUBLIC_FILES]).stdout.strip()
    if not status:
        return "Dashboard already up to date; no commit created."

    git(pages_repo, ["commit", "-m", message])
    if no_push:
        return "Committed dashboard update; push skipped by --no-push."

    git(pages_repo, ["push"])
    return "Committed and pushed dashboard update."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the public dashboard and publish it to the GitHub Pages repo."
    )
    parser.add_argument(
        "--pages-repo",
        default=os.environ.get("DASHBOARD_PAGES_REPO", str(DEFAULT_PAGES_REPO)),
        help="Path to the separate GitHub Pages checkout. Defaults to ../trading-dashboard.",
    )
    parser.add_argument(
        "--message",
        default=f"Update dashboard {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        help="Commit message for the Pages repo.",
    )
    parser.add_argument("--no-push", action="store_true", help="Commit locally but do not push.")
    parser.add_argument("--dry-run", action="store_true", help="Generate and scan only; do not copy or commit.")
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Use the existing dashboard/index.html instead of regenerating it first.",
    )
    parser.add_argument(
        "--allow-sensitive-match",
        action="store_true",
        help="Bypass the public-output sensitive-string guard.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pages_repo = Path(args.pages_repo).expanduser().resolve()

    if args.skip_generate:
        print("Using existing dashboard/index.html")
    else:
        print("Generating dashboard/index.html")
        generate_dashboard.render()

    findings = scan_public_output(DASHBOARD_DIR / "index.html")
    if findings and not args.allow_sensitive_match:
        print("Refusing to publish: possible sensitive text found in dashboard/index.html.", file=sys.stderr)
        for item in findings:
            print(f"- {item}", file=sys.stderr)
        print("Remove the source text or rerun with --allow-sensitive-match after manual review.", file=sys.stderr)
        return 2

    if args.dry_run:
        print("Dry run passed; no files copied or committed.")
        return 0

    if not (pages_repo / ".git").exists():
        print(f"Pages repo is not a git checkout: {pages_repo}", file=sys.stderr)
        return 2

    copy_public_files(pages_repo)
    print(commit_and_push(pages_repo, args.message, args.no_push))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
