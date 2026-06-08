"""
send_brief.py

Sends the daily trading-journal email via Resend's HTTPS API. Replaces the
prior Gmail-MCP `create_draft` flow because:
  - Gmail MCP only creates drafts, never inbox-delivered sends.
  - Gmail MCP does not support attachments.
  - SMTP is port-blocked in Claude Routine environments.

Resend is HTTPS-based (port 443), supports attachments as base64, and the
free tier covers a daily brief comfortably.

Environment:
    RESEND_API_KEY must be set. In local runs it comes from
    .claude/settings.json's `env` block; in scheduled runs it comes from
    the routine's environment configuration.

Usage (CLI):
    python send_brief.py \\
        --subject "NVDA's GTC day" \\
        --preview "Gap-up exits the deep-dive add window" \\
        --html-file brief.html \\
        --text-file brief.txt \\
        --attachment news-visual/briefing.pdf

Usage (import):
    from send_brief import send
    send(
        subject="...",
        html_body="<html>...</html>",
        text_body="...",
        attachments=[Path("news-visual/briefing.pdf")],
    )
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


RESEND_ENDPOINT = "https://api.resend.com/emails"
DEFAULT_FROM = os.environ.get("RESEND_FROM") or "Trading Journal <onboarding@resend.dev>"
DEFAULT_TO = os.environ.get("RESEND_TO") or "you@example.com"


class SendError(RuntimeError):
    pass


def _encode_attachment(path: Path) -> dict:
    if not path.exists():
        raise SendError(f"Attachment not found: {path}")
    data = path.read_bytes()
    suffix = path.suffix.lower()
    content_type = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(suffix, "application/octet-stream")
    return {
        "filename": path.name,
        "content": base64.b64encode(data).decode("ascii"),
        "content_type": content_type,
    }


def send(
    subject: str,
    html_body: str,
    text_body: str | None = None,
    attachments: Iterable[Path] | None = None,
    to: str | Iterable[str] = DEFAULT_TO,
    sender: str = DEFAULT_FROM,
) -> str:
    """POST to Resend. Returns the Resend message id on success."""
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    if not api_key:
        raise SendError(
            "RESEND_API_KEY is not set. Add it to .claude/settings.json "
            "env block (local) or the routine env (scheduled)."
        )

    to_list = [to] if isinstance(to, str) else list(to)
    payload: dict = {
        "from": sender,
        "to": to_list,
        "subject": subject,
        "html": html_body,
    }
    if text_body:
        payload["text"] = text_body
    if attachments:
        payload["attachments"] = [_encode_attachment(Path(p)) for p in attachments]

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Cloudflare at Resend's edge rejects requests without a UA
            # (bare urllib default is refused with 403 / error code 1010).
            "User-Agent": "trading-journal/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )

    # Retry up to 3 times on transient failure (5xx, network error,
    # unparseable body) with exponential backoff: 2s, 4s, 8s. 4xx is a hard
    # fail — retrying won't fix auth or request-shape bugs. Bumped from 1
    # retry on 2026-04-26 after Resend's "DNS cache overflow" 503 outage
    # took down the daily brief — 1 retry wasn't enough to ride it out.
    max_attempts = 4
    resp_body = None
    last_transient_error = None
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read().decode("utf-8")
            json.loads(resp_body)  # validate parse succeeds before breaking out
            break
        except urllib.error.HTTPError as e:
            if 500 <= e.code < 600 and attempt < max_attempts - 1:
                detail = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
                last_transient_error = f"Resend HTTP {e.code}: {detail[:200]}"
                backoff = 2 ** (attempt + 1)
                print(f"send_brief: {last_transient_error}; retrying in {backoff}s (attempt {attempt + 2}/{max_attempts})", file=sys.stderr)
                time.sleep(backoff)
                continue
            detail = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
            raise SendError(f"Resend HTTP {e.code}: {detail}") from None
        except urllib.error.URLError as e:
            if attempt < max_attempts - 1:
                last_transient_error = f"Network error: {e.reason}"
                backoff = 2 ** (attempt + 1)
                print(f"send_brief: {last_transient_error}; retrying in {backoff}s (attempt {attempt + 2}/{max_attempts})", file=sys.stderr)
                time.sleep(backoff)
                continue
            raise SendError(f"Network error reaching Resend: {e.reason}") from None
        except json.JSONDecodeError:
            if attempt < max_attempts - 1:
                last_transient_error = "Unparseable body"
                backoff = 2 ** (attempt + 1)
                print(f"send_brief: {last_transient_error}; retrying in {backoff}s (attempt {attempt + 2}/{max_attempts})", file=sys.stderr)
                time.sleep(backoff)
                continue
            raise SendError(f"Unparseable Resend response: {resp_body}") from None

    if last_transient_error:
        print(f"send_brief: recovered from transient {last_transient_error} on retry", file=sys.stderr)

    parsed = json.loads(resp_body)
    msg_id = parsed.get("id")
    if not msg_id:
        raise SendError(f"Resend returned no id: {parsed}")
    return msg_id


def _read_file_arg(path_str: str | None) -> str | None:
    if not path_str:
        return None
    return Path(path_str).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Send daily brief via Resend.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--html-file", required=True, help="Path to HTML body file.")
    parser.add_argument("--text-file", default=None, help="Path to plain-text body file (optional).")
    parser.add_argument(
        "--attachment",
        action="append",
        default=[],
        help="Path to an attachment file (repeatable).",
    )
    parser.add_argument("--to", default=DEFAULT_TO)
    parser.add_argument("--from", dest="sender", default=DEFAULT_FROM)
    args = parser.parse_args()

    html_body = _read_file_arg(args.html_file)
    text_body = _read_file_arg(args.text_file)

    try:
        msg_id = send(
            subject=args.subject,
            html_body=html_body,
            text_body=text_body,
            attachments=[Path(a) for a in args.attachment],
            to=args.to,
            sender=args.sender,
        )
    except SendError as e:
        print(f"[send_brief] failed: {e}", file=sys.stderr)
        return 1

    print(f"[send_brief] sent id={msg_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
