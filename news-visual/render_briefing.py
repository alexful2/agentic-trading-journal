"""
render_briefing.py

Renders a PDF briefing template via headless Chromium. The template loads
its data from `briefing-data.js` (written by build_and_send.py — or by
anything calling write_data()).

Called from build_and_send.py as part of the daily email pipeline. Can also
be invoked standalone for testing or when swapping templates.

Setup (one time):
    pip install -r news-visual/requirements.txt
    playwright install chromium

Usage:
    python render_briefing.py
    # swap template (any file alongside ../briefing-data.js):
    python render_briefing.py --template templates/briefing-minimal.html --out out.pdf
"""

from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys


# System-installed Chromium binaries to try before falling back to download.
# Order: explicit chromium first (smaller, no telemetry), then chrome stable,
# then snap. Most CI/sandbox Linux images have at least one of these.
SYSTEM_CHROMIUM_CANDIDATES = [
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/snap/bin/chromium",
    # Common Windows install paths (rarely used in routine env, but cheap to check):
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
SYSTEM_CHROMIUM_NAMES_ON_PATH = ["chromium-browser", "chromium", "google-chrome", "chrome"]


def write_data(data: dict, data_js_path: str = "briefing-data.js") -> None:
    """Serialize the briefing data to briefing-data.js alongside the template."""
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    content = f"window.briefingData = {payload};\n"
    Path(data_js_path).write_text(content, encoding="utf-8")


def _find_system_chromium() -> str | None:
    """Return path to a system-installed Chromium/Chrome binary, or None.
    Honors $CHROMIUM_PATH override for explicit pinning."""
    override = (Path(os.environ["CHROMIUM_PATH"]) if "CHROMIUM_PATH" in os.environ else None)
    if override and override.is_file():
        return str(override)
    for path in SYSTEM_CHROMIUM_CANDIDATES:
        if Path(path).is_file():
            return path
    for name in SYSTEM_CHROMIUM_NAMES_ON_PATH:
        found = shutil.which(name)
        if found:
            return found
    return None


def _try_install(args: list[str]) -> tuple[int, str]:
    """Run `python -m playwright install ...`. Returns (returncode, combined output)."""
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", *args],
        capture_output=True,
        text=True,
    )
    combined = (result.stdout + result.stderr).strip()
    return result.returncode, combined


def _launch_chromium(p):
    """Launch Chromium with a chain of fallbacks so PDF render survives
    whatever the runtime environment looks like.

    Fallback chain (each step only runs if the previous failed):
      1. Playwright's bundled Chromium (works locally, fails in fresh remote envs).
      2. System-installed Chromium / Chrome via executable_path. No download
         needed — works even when egress to Playwright's CDN is blocked.
      3. `playwright install --with-deps chromium` (needs sudo + network).
      4. `playwright install chromium` (no sudo, just network).

    On total failure, raises with a clear breadcrumb so build_and_send.py's
    outer except catches it and the email still sends without attachment."""
    from playwright._impl._errors import Error as PlaywrightError

    attempts: list[str] = []

    try:
        attempts.append("bundled")
        return p.chromium.launch()
    except PlaywrightError as e:
        msg = str(e).lower()
        is_missing = "executable doesn't exist" in msg or "browsertype.launch" in msg
        is_launch_fail = "failed to launch" in msg or "host system is missing dependencies" in msg
        if not (is_missing or is_launch_fail):
            raise

        # Fallback 2: system chromium. Cheapest — no network needed.
        system_path = _find_system_chromium()
        if system_path:
            try:
                attempts.append(f"system:{system_path}")
                print(f"INFO: bundled chromium unavailable; using system binary at {system_path}", file=sys.stderr)
                return p.chromium.launch(executable_path=system_path)
            except PlaywrightError as sys_err:
                print(f"INFO: system chromium failed ({sys_err}); trying install", file=sys.stderr)

        # Fallback 3: install with OS deps (sudo + network).
        attempts.append("install:--with-deps")
        rc, output = _try_install(["--with-deps", "chromium"])
        if rc == 0:
            return p.chromium.launch()
        print(f"INFO: --with-deps install failed (rc={rc}): {output[:300]}", file=sys.stderr)

        # Fallback 4: plain install (network only).
        attempts.append("install:plain")
        rc, output = _try_install(["chromium"])
        if rc == 0:
            return p.chromium.launch()

        raise RuntimeError(
            f"All Chromium fallbacks exhausted (tried: {', '.join(attempts)}). "
            f"Last install output: {output[:500]}"
        ) from e


def render_pdf(
    template_path: str = "templates/briefing-default.html",
    output_pdf_path: str = "briefing.pdf",
) -> None:
    """Render the template to a PDF sized to content height."""
    from playwright.sync_api import sync_playwright

    Path(output_pdf_path).parent.mkdir(parents=True, exist_ok=True)
    template_url = f"file://{Path(template_path).resolve()}"

    with sync_playwright() as p:
        browser = _launch_chromium(p)
        page = browser.new_page(viewport={"width": 800, "height": 1200})
        page.goto(template_url, wait_until="domcontentloaded")

        # Wait for fonts + any network-loaded resources. Swallow timeouts so a
        # slow jsdelivr response falls back to system fonts rather than crashing.
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass

        # Measure rendered height so the PDF hugs the content exactly —
        # no trailing white page, no clipping, even as daily content varies.
        content_height = page.evaluate(
            "Math.ceil(document.querySelector('.page').getBoundingClientRect().height)"
        )

        page.emulate_media(media="print")
        page.pdf(
            path=output_pdf_path,
            width="800px",
            height=f"{content_height + 40}px",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Trading Journal template to PDF.")
    parser.add_argument("--template", default="templates/briefing-default.html",
                        help="Path to the HTML template. Swap for any other "
                             "template that reads window.briefingData.")
    parser.add_argument("--out", default="briefing.pdf",
                        help="Output PDF path.")
    args = parser.parse_args()

    render_pdf(args.template, args.out)
    print(f"Wrote {args.out}")
