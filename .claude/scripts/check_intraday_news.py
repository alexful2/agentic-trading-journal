#!/usr/bin/env python3
"""
Intraday news worker. Polls Google News RSS + SEC EDGAR atom for Tier 1+2
tickers from watchlist.md, severity-scores headlines/filings via deterministic
keyword rules, pushes Pushover for sev>=4, logs sev>=3 to vault.

Modeled on .claude/scripts/check_intraday_price_triggers.py — same state-file
pattern, same Pushover envelope, same cache shape. No LLM call per poll.

Sources:
- Alpaca News REST API — Benzinga-sourced, wire-direct headlines for all
  Tier 1+2 tickers in a single batch request. Requires ALPACA_API_KEY +
  ALPACA_API_SECRET env. Free tier with brokerage account; 900 headlines/day cap.
- SEC EDGAR atom (per ticker) — material filings (8-K, 10-K, 10-Q, 4, 144).
  CIK pulled from vault/companies/TICKER/_meta.md if present; else skipped.
- 8-K filings get a follow-up fetch of the index page to extract Item codes
  (2.02 = earnings, 5.02 = exec change, etc.) so routing/labels can reflect
  what the filing is actually about, not just "8-K filing".
- Federal Reserve press-release RSS — FOMC statements, rate decisions,
  minutes, Powell speeches, Beige Book. Items use ticker=_MACRO. No
  per-ticker keying. Disable with --no-macro.

Severity (deterministic keyword/regex):
- sev 4 (push):  8-K with material item (1.01/5.02/8.01/etc.), halt, guidance
                 change, M&A, FDA decision, SEC/DOJ probe, executive
                 resignation, chapter 11, breach
- sev 3 (log):   8-K earnings release / Reg FD only, 10-K/Q, Form 4 (insider),
                 analyst u/d, generic earnings
- sev <=2:       dropped silently

Time cutoff: items <24h old only. Dedup state resets at date boundary,
so without this every ticker's last few days of news would re-push on
the first run of a new day.

State (avoid re-alerting):
- .intraday-state/news-YYYY-MM-DD.json — two layers:
  - `alerted`: list of (ticker:source:item-hash) ids already alerted
    today. Today + yesterday loaded so date-boundary doesn't re-fire.
  - `cooldowns`: list of {ticker, category, ts} for sev-4 fires in the
    last CATEGORY_COOLDOWN_HOURS. Loaded across the last
    COOLDOWN_STATE_DAYS daily files. Catches same-event re-fires that
    surface from a different source (Benzinga vs Yahoo) with a fresh
    item_id but the same (ticker, category).
- A duplicate-suppression layer also runs at push time: when sev-4
  triggers news-read for a real ticker, the worker's initial Pushover
  is skipped — the news-read summary covers it. Pseudo-tickers
  (`_MACRO`, `_FILER_*`) and any news-read trigger failure still
  produce a worker push.

Required env:
- PUSHOVER_TOKEN — application API token from pushover.net
- PUSHOVER_USER — user/group key from pushover.net dashboard
- ALPACA_API_KEY — Alpaca Trading API key ID (paper account is fine)
- ALPACA_API_SECRET — Alpaca Trading API secret

Usage:
    python .claude/scripts/check_intraday_news.py
    python .claude/scripts/check_intraday_news.py --dry-run
    python .claude/scripts/check_intraday_news.py --ticker NVDA --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WATCHLIST = REPO_ROOT / "vault/watchlist.md"
COMPANIES_DIR = REPO_ROOT / "vault/companies"

PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
USER_AGENT = "trading-journal-intraday-news you@example.com"
HTTP_TIMEOUT = 20
INTER_REQUEST_DELAY = 0.3
LOOKBACK_HOURS = 24

# (ticker, category) cooldown — if the same ticker+category sev-4 fired in
# the last N hours, demote the re-fire to sev-3 (log only, no push, no
# news-read). Catches the case where the same underlying event (e.g., an
# acquisition announcement) surfaces from multiple sources or as a
# next-day editorial follow-up with a different headline + different ID.
# Window scans the last 3 daily state files; bump COOLDOWN_STATE_DAYS if
# this constant exceeds 72.
CATEGORY_COOLDOWN_HOURS = 72
COOLDOWN_STATE_DAYS = 3

ALPACA_NEWS_URL = "https://data.alpaca.markets/v1beta1/news"
EDGAR_TEMPLATE = (
    "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}"
    "&type=&dateb=&owner=include&count=10&output=atom"
)
FED_PRESS_URL = "https://www.federalreserve.gov/feeds/press_all.xml"
MACRO_TICKER = "_MACRO"

# Yahoo Finance per-ticker headline RSS. Aggregator across MotleyFool,
# Investing.com, Zacks, Schaeffer's, etc. — broader catch surface than
# Alpaca/Benzinga for mid-cap names that wire services cover thinly
# (VRT, DLR, GEV). Endpoint is undocumented and Yahoo has retired Finance
# APIs before, so treat as best-effort: fetch failure logs to stderr and
# returns [], the rest of the pipeline still runs.
YAHOO_NEWS_URL = "https://finance.yahoo.com/rss/headline?s={ticker}"

# Company-name aliases for the title-mention gate in classify_wire.
# Yahoo tags articles by ticker via its aggregator, but a ticker tag alone
# doesn't mean the article is about that company — could be a peer mention
# or a sector roundup. For sev-4 push, the title (or first 200 chars of
# description) must contain the ticker or an alias. Lowercased on use.
# Fallback if a ticker isn't here: just the ticker symbol itself.
# Example watchlist — replace with your own tickers and aliases.
COMPANY_ALIASES: dict[str, list[str]] = {
    "NVDA":  ["nvda", "nvidia"],
    "VRT":   ["vrt", "vertiv"],
    "DLR":   ["dlr", "digital realty"],
    "GEV":   ["gev", "ge vernova"],
    "CEG":   ["ceg", "constellation energy", "constellation"],
    "AMD":   ["amd", "advanced micro devices"],
    "GOOGL": ["googl", "google", "alphabet"],
    "MSFT":  ["msft", "microsoft"],
}

# Non-ticker EDGAR filers we want to watch — typically hedge funds whose
# 13F / 13D / 13G disclosures move our names. Each entry uses a pseudo-ticker
# (prefix `_FILER_`) so the dedup state, alert formatting, and Tier-1 deep-
# dive gate all keep working. Add an entry by hand; no vault file backs this.
#
# To find a CIK: EDGAR full-text search →
#   https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=<name>&type=13F
# Or the JSON API → https://data.sec.gov/submissions/CIK<10-digit-cik>.json
WATCHED_FILERS: list[dict] = [
    # Add an entry by hand, e.g.:
    #   {"pseudo_ticker": "_FILER_EXAMPLE", "label": "Example LP", "cik": "0001234567"},
]


# ---- Severity rules -----------------------------------------------------

# (regex, category). First match wins per category bucket. Case-insensitive.
SEV4_PATTERNS = [
    (r"\btrading\s+halt(s|ed)?\b", "trading halt"),
    (r"\bhalt(s|ed|ing)?\s+trading\b", "trading halt"),
    (r"\b(withdraws?|withdrew|cuts?|raises?|raised|lowers?|lowered|reduces?|reduced)\s+"
     r"(its\s+|the\s+|fy\s*\d{0,4}\s+)?(forecast|guidance|outlook)\b", "guidance change"),
    (r"\b(guidance|forecast|outlook)\s+(cut|raised|lowered|withdrawn|reduced)\b", "guidance change"),
    (r"\bpreliminary\s+(financial\s+)?results\b", "preliminary results"),
    (r"\b(earnings|profit)\s+warning\b", "earnings warning"),
    (r"\bto\s+(acquire|buy out)\b", "M&A — acquirer"),
    (r"\bagree(s|d)?\s+to\s+(be\s+)?(acquire(d)?|merge)\b", "M&A"),
    (r"\b(acquisition|merger)\s+agreement\b", "M&A"),
    (r"\btender\s+offer\b", "tender offer"),
    (r"\bgoing\s+private\b", "going private"),
    (r"\b(fda|food and drug)\s+(approves?|approval|rejects?|rejection|denies)\b", "FDA decision"),
    (r"\bcomplete\s+response\s+letter\b", "FDA CRL"),
    (r"\b(sec|doj|justice department|ftc)\s+"
     r"(investigat(ion|ing|es?)|prob(e|ing|es?)|charges?|sues?|sued|lawsuit)\b", "regulatory probe"),
    (r"\bsubpoena(s|ed)?\b", "subpoena"),
    (r"\bfile(s|d)?\s+for\s+chapter\s+11\b", "bankruptcy"),
    (r"\bgoing\s+concern\b", "going concern"),
    (r"\b(ceo|cfo|coo|chief\s+\w+\s+officer)\s+"
     r"(resign(s|ed|ation)?|stepp(ed|ing)\s+down|fired|terminated|departs?|departure)\b", "executive departure"),
    (r"\b(data\s+breach|ransomware|cyberattack)\b", "cyber incident"),
    (r"\b(major|massive)\s+(recall|product\s+recall)\b", "product recall"),
]

SEV3_PATTERNS = [
    (r"\binsider\s+(buy(ing)?|sell(ing|s)?|purchase)\b", "insider activity"),
    (r"\b(upgrades?|downgrades?|upgraded|downgraded)\b", "analyst rating"),
    (r"\b(beat(s|en)?|miss(es|ed)?)\s+(estimates?|expectations?|consensus)\b", "earnings result"),
    (r"\bquarterly\s+results?\b", "earnings"),
    (r"\bprice\s+target\s+(raised|cut|lowered|increased|reduced)\b", "PT change"),
]

MACRO_SEV4_PATTERNS = [
    (r"\bfomc\s+statement\b", "FOMC statement"),
    (r"\bfederal\s+open\s+market\s+committee\b", "FOMC"),
    (r"\bfederal\s+funds\s+rate\b", "Fed funds rate decision"),
    (r"\bminutes\s+of\s+the\s+federal\s+open\s+market\s+committee\b", "FOMC minutes"),
    (r"\bsummary\s+of\s+economic\s+projections\b", "FOMC SEP / dot plot"),
    (r"\bemergency\s+(rate|action|measure)\b", "Fed emergency action"),
]

MACRO_SEV3_PATTERNS = [
    (r"\bspeech\s+by\b", "Fed speech"),
    (r"\bremarks\s+by\b", "Fed remarks"),
    (r"\bstatement\s+by\b", "Fed statement"),
    (r"\bbeige\s+book\b", "Beige Book"),
    (r"\bstress\s+test\b", "Fed stress test"),
    (r"\btestimony\s+by\b", "Fed Congressional testimony"),
]

# ---- Wire / aggregator (Yahoo) severity rules --------------------------
#
# Tuned for verbose aggregator headlines: "Power Supplier VRT Closes $3
# Billion Convertible Notes Offering to Fuel AI Transformation" — wouldn't
# match any of the SEV4_PATTERNS above (no "halt", "guidance change",
# "agrees to acquire") but is exactly the kind of capital-action news we
# want to surface.

# Listicles, ranked-stock posts, "should you buy", peer-comparison
# clickbait, generic price-move headlines. Reused on every wire item.
WIRE_DROP_PATTERNS = [
    r"\bbetter\s+(stock|datacenter|ai)\b",
    r"\b\w+\s+vs\.?\s+\w+\b",
    r"\bshould\s+you\s+(buy|sell|hold)\b",
    r"\b\d+\s+stocks?\s+to\s+(buy|watch|consider|own)\b",
    r"\bbest\s+stocks?\s+for\b",
    r"\bjim\s+cramer\b",
    r"\bprice\s+(prediction|forecast)\b",
    r"\b(buy|sell|hold)\?\s*$",   # title ends in "Buy, Sell, or Hold?"
    r"\binvestor\s+letter\b",
    r"\bweekly\s+(wrap|review|recap|roundup)\b",
    r"\bdaily\s+(brief|wrap|roundup)\b",
    r"\bmarket\s+(roundup|recap)\b",
    r"\bearnings\s+call\s+(summary|highlights?)\b",  # transcript recaps, not news
]

# Generic price-action headlines are usually noise, but only drop them after
# material event rules get first pass.
WIRE_PRICE_ACTION_DROP_PATTERNS = [
    r"\bwhy\s+\w+\s+(shares?|stock)\s+(moved|jumped|sank|fell|rose|surged)\b",
    r"\b(stock|shares?)\s+(rises?|rose|falls?|fell|jumps?|drops?|surges?|plunges?|soars?|sinks?)\b",
]

# Sev-4 push patterns. Each is (regex, category-label). Material capital
# actions, named-party partnerships, sell-side action with explicit verb,
# guidance change, regulatory shock, executive departure. Order matters:
# first match wins per item.
WIRE_SEV4_PATTERNS = [
    # Capital actions
    (r"\bconvertible\s+(notes?|bonds?|debentures?)\b", "capital raise — convertibles"),
    (r"\bsecondary\s+offering\b", "capital raise — secondary"),
    (r"\bprivate\s+placement\b", "capital raise — private placement"),
    (r"\b(at-the-market|atm)\s+(offering|program)\b", "capital raise — ATM"),
    (r"\bshelf\s+registration\b", "capital raise — shelf"),
    (r"\b(senior|subordinated|term)\s+(notes?|loan|credit\s+facility)\b", "debt facility"),
    (r"\bcredit\s+(facility|agreement)\b", "debt facility"),
    (r"\braises?\s+\$\s*\d+\s*(million|billion|m|b)\b", "capital raise"),
    (r"\bbuyback\s+(authorization|program)\b", "buyback"),
    (r"\bshare\s+repurchase\s+(authorization|program)\b", "buyback"),
    # Partnerships / contracts / customer wins / capacity
    (r"\bstrategic\s+(partnership|investment|agreement)\b", "strategic partnership"),
    (r"\bmaster\s+services\s+agreement\b", "master services agreement"),
    (r"\b(signed|signs)\s+(an?\s+)?(agreement|contract|deal|mou)\s+with\b", "agreement signed"),
    (r"\bcontract\s+award\b", "contract award"),
    (r"\b(named|selected|chose[n]?)\s+(as\s+)?(preferred\s+)?partner\b", "partner selected"),
    (r"\b\d+\s*(mw|gw|mwh|gwh)\s+(deal|contract|agreement|deployment|capacity|site|campus)\b",
        "MW/GW capacity event"),
    (r"\b(energized|commissioning|commissioned)\b.*\b(substation|site|campus|facility|data\s+center)\b",
        "site energization"),
    (r"\bground\s*break(ing)?\b.*\b(data\s+center|campus|facility)\b", "groundbreaking"),
    (r"\b(acquires?|acquir(ed|ing))\b", "M&A — acquirer"),
    (r"\bagree(s|d)?\s+to\s+(be\s+)?acquire(d)?\b", "M&A"),
    (r"\b(merger|acquisition)\s+agreement\b", "M&A"),
    # Sell-side action (explicit verb required, not just "covers" or "watches")
    (r"\binitiates?\s+coverage\s+(on|of|at)\b", "sell-side initiation"),
    (r"\b(raises?|raised|lifts?|lifted)\s+(price\s+)?target\b", "price target raised"),
    (r"\bprice\s+target\s+(raised|cut|lowered|increased|reduced|lifted)\b", "PT change"),
    (r"\bupgrades?\s+(to|at)\s+(buy|overweight|outperform|strong\s+buy)\b", "upgrade"),
    (r"\bdowngrades?\s+(to|at)\s+(sell|underweight|underperform)\b", "downgrade"),
    # Guidance / earnings revisions
    (r"\braises?\s+(full[-\s]?year|fy|guidance|outlook|forecast)\b", "guidance raised"),
    (r"\b(lowers?|cuts?|reduces?)\s+(full[-\s]?year|fy|guidance|outlook|forecast)\b", "guidance cut"),
    (r"\b(beats?|beat)\s+(and|&)\s+raise[sd]?\b", "beats and raises"),
    (r"\bwithdraws?\s+(guidance|outlook|forecast)\b", "guidance withdrawn"),
    (r"\bpreliminary\s+(financial\s+)?results\b", "preliminary results"),
    (r"\b(earnings|profit)\s+warning\b", "earnings warning"),
    # Regulatory / legal / executive
    (r"\b(sec|doj|justice\s+department|ftc)\s+"
     r"(investigat(ion|ing|es?)|prob(e|ing|es?)|charges?|sues?|sued|lawsuit)\b", "regulatory probe"),
    (r"\bsubpoena(s|ed)?\b", "subpoena"),
    (r"\b(trading\s+halt(s|ed)?|halt(s|ed|ing)?\s+trading)\b", "trading halt"),
    (r"\bfile(s|d)?\s+for\s+chapter\s+11\b", "bankruptcy"),
    (r"\bgoing\s+concern\b", "going concern"),
    (r"\b(ceo|cfo|coo|chief\s+\w+\s+officer|president)\s+"
     r"(resign(s|ed|ation)?|stepp(ed|ing)\s+down|fired|terminated|departs?|departure)\b",
        "executive departure"),
    (r"\b(fda|food\s+and\s+drug)\s+(approves?|approval|rejects?|rejection|denies)\b", "FDA decision"),
    (r"\bcomplete\s+response\s+letter\b", "FDA CRL"),
    (r"\b(data\s+breach|ransomware|cyberattack)\b", "cyber incident"),
]

# Sev-3 log patterns. Insider activity, generic earnings beats/misses, less
# decisive sell-side ("covers" not "initiates"), analyst commentary.
WIRE_SEV3_PATTERNS = [
    (r"\binsider\s+(buy(ing)?|sell(ing|s)?|purchase)\b", "insider activity"),
    (r"\b(beat(s|en)?|miss(es|ed)?)\s+(estimates?|expectations?|consensus)\b", "earnings result"),
    (r"\bquarterly\s+results?\b", "earnings"),
    (r"\b(analyst|sell-side)\s+(commentary|note|view)\b", "analyst commentary"),
    (r"\bvaluation\b", "valuation discussion"),
]

DROP_PATTERNS = [
    r"\b\d+\s+stocks?\s+to\s+(buy|watch|consider|own)\b",
    r"\bshould\s+you\s+(buy|sell)\b",
    r"\bbest\s+stocks?\s+for\b",
    r"\bjim\s+cramer\b",
    r"\bmotley\s+fool\b",
    r"\b(stock|shares?)\s+(rises?|rose|falls?|fell|jumps?|drops?|surges?|plunges?)\b",
    r"\bprice\s+(prediction|forecast)\b",
]

# Severities for SEC filings appearing in a company's own ticker feed.
# Routine passive-holder disclosures (13G/A, Form 144, Form 4 amendments)
# dominate the feed but rarely move prices — Vanguard/BlackRock churn,
# 10b5-1-scheduled proposed sales, transaction corrections — so they're
# dropped to sev 0 here. Activist stakes (13D) stay sev 4. Clustered Form
# 144s (3+ insiders in the same 24h batch) get bumped back to sev 3 via
# the mark_form144_clusters pre-pass.
EDGAR_FILING_SEV_TICKER = {
    "8-K":   (4, "8-K filing"),
    "8-K/A": (4, "8-K amendment"),
    "10-K":  (3, "10-K filing"),
    "10-K/A":(3, "10-K amendment"),
    "10-Q":  (3, "10-Q filing"),
    "10-Q/A":(3, "10-Q amendment"),
    "4":     (3, "Form 4 (insider)"),
    "4/A":   (0, "Form 4 amendment"),       # dropped — usually correction
    "144":   (0, "Form 144"),                # dropped — proposed, not actual; see cluster pre-pass
    "S-1":   (3, "S-1 filing"),
    "424B4": (3, "424B4 prospectus"),
    # Activist (13D) — rare and meaningful, push.
    "SCHEDULE 13D":   (4, "Schedule 13D (>5% active stake)"),
    "SCHEDULE 13D/A": (4, "Schedule 13D amendment"),
    "SC 13D":         (4, "Schedule 13D (>5% active stake)"),
    "SC 13D/A":       (4, "Schedule 13D amendment"),
    # Passive (13G) — Vanguard/BlackRock/Fidelity reporting churn on the
    # ticker feed. Drop here; the WATCHED_FILERS path below keeps these
    # sev-4 when filed by a tracked investor.
    "SCHEDULE 13G":   (0, "Schedule 13G (>5% passive stake)"),
    "SCHEDULE 13G/A": (0, "Schedule 13G amendment"),
    "SC 13G":         (0, "Schedule 13G (>5% passive stake)"),
    "SC 13G/A":       (0, "Schedule 13G amendment"),
    # 13F-HR should never appear on an operating-company ticker feed; defensive.
    "13F-HR":         (0, "13F holdings disclosure"),
    "13F-HR/A":       (0, "13F amendment"),
}

# Severities for SEC filings on a tracked-filer feed (WATCHED_FILERS path,
# pseudo-ticker `_FILER_*`). Here the filer IS the signal — a hedge fund's
# 13F/13D/13G changes tell us about position moves — so these stay sev 4.
EDGAR_FILING_SEV_FILER = {
    "13F-HR":         (4, "13F holdings disclosure"),
    "13F-HR/A":       (4, "13F amendment"),
    "SCHEDULE 13D":   (4, "Schedule 13D (>5% active stake)"),
    "SCHEDULE 13D/A": (4, "Schedule 13D amendment"),
    "SCHEDULE 13G":   (4, "Schedule 13G (>5% passive stake)"),
    "SCHEDULE 13G/A": (4, "Schedule 13G amendment"),
    "SC 13D":         (4, "Schedule 13D (>5% active stake)"),
    "SC 13D/A":       (4, "Schedule 13D amendment"),
    "SC 13G":         (4, "Schedule 13G (>5% passive stake)"),
    "SC 13G/A":       (4, "Schedule 13G amendment"),
    # Filer-side 4/144 (e.g. fund officer transactions) is exotic; log if seen.
    "4":   (3, "Form 4 (filer insider)"),
    "4/A": (3, "Form 4 amendment (filer)"),
    "144": (3, "Form 144 (filer)"),
    # Operating-company filings on a hedge fund's atom feed shouldn't happen,
    # but if EDGAR ever surfaces one we want it logged, not silently dropped.
    "8-K":   (3, "8-K (filer)"),
    "8-K/A": (3, "8-K/A (filer)"),
    "10-K":  (3, "10-K (filer)"),
    "10-Q":  (3, "10-Q (filer)"),
}

# 8-K Item code -> (severity, human-readable label). Routing intent:
# scheduled / housekeeping items log only (sev 3); surprise / material items
# push (sev 4). Item 9.01 (financial statements & exhibits) is omitted —
# always paired with another item; never a standalone signal.
EIGHT_K_ITEM_INFO: dict[str, tuple[int, str]] = {
    "1.01": (4, "material agreement"),
    "1.02": (4, "agreement terminated"),
    "1.03": (4, "bankruptcy"),
    "1.04": (3, "mine safety"),
    "1.05": (4, "cybersecurity incident"),
    "2.01": (4, "acquisition/disposition"),
    "2.02": (3, "earnings release"),
    "2.03": (3, "new debt obligation"),
    "2.04": (4, "debt acceleration"),
    "2.05": (4, "exit/disposal costs"),
    "2.06": (4, "material impairment"),
    "3.01": (4, "delisting notice"),
    "3.02": (3, "unregistered equity sale"),
    "3.03": (3, "rights modification"),
    "4.01": (3, "auditor change"),
    "4.02": (4, "financial restatement"),
    "5.01": (4, "change of control"),
    "5.02": (4, "exec/director change"),
    "5.03": (3, "bylaw amendment"),
    "5.04": (3, "401k blackout"),
    "5.05": (3, "ethics code amendment"),
    "5.06": (4, "shell company status change"),
    "5.07": (0, "shareholder vote results"),  # housekeeping; no signal
    "5.08": (3, "shareholder nominations"),
    "7.01": (3, "Reg FD disclosure"),
    "8.01": (4, "other material event"),
}


def classify_headline(text: str) -> tuple[int, str]:
    lower = text.lower()
    for pat in DROP_PATTERNS:
        if re.search(pat, lower):
            return (0, "drop")
    for pat, cat in SEV4_PATTERNS:
        if re.search(pat, lower):
            return (4, cat)
    for pat, cat in SEV3_PATTERNS:
        if re.search(pat, lower):
            return (3, cat)
    return (0, "")


def classify_wire(title: str, description: str, ticker: str) -> tuple[int, str]:
    """Score a Yahoo/aggregator wire item.

    Three-stage gate:
      Stage 1 (relevance):  watched ticker or company alias must appear in
                            title OR first 200 chars of description. Yahoo's
                            per-ticker URL alone isn't enough — items tagged
                            with our ticker can still be peer-mention pieces
                            (e.g., "Better Datacenter Stock: VRT or DLR?"
                            appears in both feeds but is primary to neither).
      Stage 2 (severity):   hard drop > sev4.
      Stage 3 (noise):      price-action-only drop > sev3.

    For sev-4 push we require the alias-in-title gate to pass. If only the
    ticker tag is present but no alias in the headline body, we cap at
    sev-3 (log) so peer-mentions don't push to phone.
    """
    text = f"{title} {description[:200]}".lower()
    for pat in WIRE_DROP_PATTERNS:
        if re.search(pat, text):
            return (0, "drop")
    aliases = COMPANY_ALIASES.get(ticker, [ticker.lower()])
    title_lower = title.lower()
    # Title-mention gate. Word-boundary match so a short ticker that collides
    # with a common English word (e.g. a 2-letter symbol) doesn't over-fire.
    has_title_alias = any(
        re.search(rf"\b{re.escape(a)}\b", title_lower) for a in aliases
    )
    for pat, cat in WIRE_SEV4_PATTERNS:
        if re.search(pat, text):
            if has_title_alias:
                return (4, cat)
            # Material pattern matched but ticker not named in title —
            # could be a peer mention. Log but don't push.
            return (3, f"{cat} (peer-mention)")
    for pat in WIRE_PRICE_ACTION_DROP_PATTERNS:
        if re.search(pat, text):
            return (0, "drop")
    for pat, cat in WIRE_SEV3_PATTERNS:
        if re.search(pat, text):
            return (3, cat)
    return (0, "")


def classify_macro(text: str) -> tuple[int, str]:
    """Score a Federal Reserve press-release title. Tighter ruleset than the
    ticker-news headline classifier — Fed titles are formulaic and we want
    to push only the truly market-moving events (FOMC, rate decisions,
    minutes, SEP). Speeches and testimony log as sev-3."""
    lower = text.lower()
    for pat, cat in MACRO_SEV4_PATTERNS:
        if re.search(pat, lower):
            return (4, cat)
    for pat, cat in MACRO_SEV3_PATTERNS:
        if re.search(pat, lower):
            return (3, cat)
    return (0, "")


# ---- Watchlist parsing -------------------------------------------------

TIER_HEADER_RE = re.compile(r"^## Tier (\d+)\b", re.MULTILINE)
TABLE_TICKER_RE = re.compile(r"^\|\s*([A-Z][A-Z0-9]{0,5})\s*\|", re.MULTILINE)


def _parse_tier_map(path: Path) -> dict[str, list[str]]:
    """Parse the watchlist into {tier_num: [tickers]}. Internal helper."""
    out: dict[str, list[str]] = {}
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8")
    parts = TIER_HEADER_RE.split(text)
    # split returns: [pre, "1", body1, "2", body2, "3", body3, ...]
    for i in range(1, len(parts), 2):
        tier_num = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        seen, tickers = set(), []
        for m in TABLE_TICKER_RE.finditer(body):
            t = m.group(1)
            if t not in seen:
                seen.add(t)
                tickers.append(t)
        out[tier_num] = tickers
    return out


def load_active_tickers(path: Path = WATCHLIST) -> list[str]:
    """Parse Tier 1 + Tier 2 ticker tables. Tier 3 is intentionally skipped
    (peripheral interest — covered passively by daily news, not intraday)."""
    tier_map = _parse_tier_map(path)
    seen, out = set(), []
    for tier in ("1", "2"):
        for t in tier_map.get(tier, []):
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def load_tier1_tickers(path: Path = WATCHLIST) -> set[str]:
    """Tier 1 only. Retained for callers that still want a Tier-1 set;
    no longer used to gate news-read (that now fires for any real ticker
    on sev-4, including Tier 2)."""
    return set(_parse_tier_map(path).get("1", []))


def is_real_ticker(ticker: str) -> bool:
    """True for operating-company tickers. Pseudo-tickers used for non-ticker
    EDGAR feeds (`_MACRO`, `_FILER_*`) all start with `_` and don't have a
    thesis note or watchlist row, so they shouldn't trigger news-read."""
    return bool(ticker) and not ticker.startswith("_")


def load_cik(ticker: str) -> str | None:
    meta = COMPANIES_DIR / ticker / "_meta.md"
    if not meta.exists():
        return None
    text = meta.read_text(encoding="utf-8")
    m = re.search(r"\*\*CIK:\*\*\s*(\d+)", text)
    if not m:
        return None
    return m.group(1).zfill(10)


# ---- HTTP / time -------------------------------------------------------

def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return resp.read()


def parse_dt_loose(s: str) -> datetime | None:
    """Parse atom (ISO-8601) or RSS (RFC-822) timestamps. Returns aware dt."""
    if not s:
        return None
    s = s.strip()
    try:
        s2 = s[:-1] + "+00:00" if s.endswith("Z") else s
        return datetime.fromisoformat(s2)
    except ValueError:
        pass
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        pass
    return None


# ---- Source: Alpaca News REST -----------------------------------------

def fetch_alpaca_news(tickers: list[str], cutoff: datetime) -> list[dict]:
    """Single batch request for all watched tickers. Alpaca's symbols= param
    accepts comma-separated, so 7 tickers = 1 HTTP call.

    Each article carries a `symbols` list — articles sometimes cross-tag
    multiple tickers (e.g. "NVDA and GOOGL on AI capex"). We attribute the
    article to each watched ticker that appears, generating one item per
    (article, watched-ticker) pair. Dedup state distinguishes by ticker so
    cross-tagged articles can fire for multiple tickers if material.

    Failure mode: missing env vars or auth error → log and return []. EDGAR
    still runs in the main pipeline, so we degrade rather than fail.
    """
    api_key = os.environ.get("ALPACA_API_KEY")
    api_secret = os.environ.get("ALPACA_API_SECRET")
    if not api_key or not api_secret:
        print("ALPACA_API_KEY/SECRET not set; skipping Alpaca news fetch", file=sys.stderr)
        return []
    if not tickers:
        return []

    start_iso = cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    # Alpaca's hard max is 50 (request limit=200 returns HTTP 400).
    # NVDA+GOOGL alone can hit ~40 items in a 24h batch, so mid-cap items
    # are at risk of clipping on busy days. Real fix is pagination via
    # next_page_token or per-ticker calls; tracked separately.
    params = urllib.parse.urlencode({
        "symbols": ",".join(tickers),
        "start": start_iso,
        "limit": "50",
        "sort": "desc",
    })
    url = f"{ALPACA_NEWS_URL}?{params}"
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "User-Agent": USER_AGENT,
    })
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        print(f"alpaca news HTTP {e.code}: {body}", file=sys.stderr)
        return []
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"alpaca news fetch failed: {e}", file=sys.stderr)
        return []

    watched = set(tickers)
    items: list[dict] = []
    for article in payload.get("news", []):
        title = (article.get("headline") or "").strip()
        if not title:
            continue
        created = parse_dt_loose(article.get("created_at") or article.get("updated_at") or "")
        if created and created < cutoff:
            continue
        article_id = str(article.get("id", ""))
        if not article_id:
            continue
        for ticker in article.get("symbols", []):
            if ticker not in watched:
                continue
            items.append({
                "ticker": ticker,
                "source": "alpaca",
                "item_id": article_id,
                "title": title,
                "link": (article.get("url") or "").strip(),
                "pub": created.isoformat() if created else "",
                "publisher": (article.get("source") or "").strip(),
            })
    return items


# ---- Source: SEC EDGAR atom -------------------------------------------

ATOM_NS = "{http://www.w3.org/2005/Atom}"


def fetch_edgar(ticker: str, cik: str, cutoff: datetime) -> list[dict]:
    url = EDGAR_TEMPLATE.format(cik=cik)
    try:
        data = http_get(url)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"edgar fetch failed for {ticker} CIK {cik}: {e}", file=sys.stderr)
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        print(f"edgar parse failed for {ticker}: {e}", file=sys.stderr)
        return []
    items: list[dict] = []
    for entry in root.findall(f"{ATOM_NS}entry"):
        title = (entry.findtext(f"{ATOM_NS}title") or "").strip()
        if not title:
            continue
        updated = parse_dt_loose(entry.findtext(f"{ATOM_NS}updated") or "")
        if updated and updated < cutoff:
            continue
        link_el = entry.find(f"{ATOM_NS}link")
        link = link_el.attrib.get("href", "") if link_el is not None else ""
        entry_id = (entry.findtext(f"{ATOM_NS}id") or link or title).strip()
        # Title format examples:
        #   "8-K - VERTIV HOLDINGS CO (0001674101) (Filer)"
        #   "13F-HR  - Quarterly report filed by..."
        #   "SCHEDULE 13D/A [Amend]  - General Statement of Acquisition..."
        # Strategy: take everything up to the " - " separator, then strip any
        # trailing "[Amend]"-style annotation. The old regex used a [A-Z0-9/-]
        # character class which stopped at the space inside "SCHEDULE 13D",
        # so 13D/G filings silently scored as filing_type="" (sev 0, dropped).
        m = re.match(r"^(.+?)\s+-\s+", title)
        filing_type_raw = m.group(1).strip() if m else ""
        filing_type = re.sub(r"\s*\[[^\]]*\]\s*$", "", filing_type_raw).strip()
        items.append({
            "ticker": ticker,
            "source": "edgar",
            "item_id": hashlib.sha1(entry_id.encode()).hexdigest()[:12],
            "title": title,
            "link": link,
            "pub": updated.isoformat() if updated else "",
            "filing_type": filing_type,
        })
    return items


def fetch_fed_press(cutoff: datetime) -> list[dict]:
    """Federal Reserve press releases (RSS). Catches FOMC statements,
    rate decisions, minutes, Powell speeches. No per-ticker keying — every
    item uses ticker=MACRO_TICKER so dedup state works the same way.

    Failure mode: fetch/parse error → log to stderr and return []. The rest
    of the pipeline still runs; we just miss macro for this tick.
    """
    try:
        data = http_get(FED_PRESS_URL)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"fed press fetch failed: {e}", file=sys.stderr)
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        print(f"fed press parse failed: {e}", file=sys.stderr)
        return []
    items: list[dict] = []
    # RSS 2.0: rss > channel > item*. iter("item") tolerates either depth.
    for entry in root.iter("item"):
        title = (entry.findtext("title") or "").strip()
        if not title:
            continue
        pub = parse_dt_loose(entry.findtext("pubDate") or "")
        if pub and pub < cutoff:
            continue
        link = (entry.findtext("link") or "").strip()
        guid = (entry.findtext("guid") or link or title).strip()
        items.append({
            "ticker": MACRO_TICKER,
            "source": "fed",
            "item_id": hashlib.sha1(guid.encode()).hexdigest()[:12],
            "title": title,
            "link": link,
            "pub": pub.isoformat() if pub else "",
            "publisher": "Federal Reserve",
        })
    return items


def fetch_yahoo_news(tickers: list[str], cutoff: datetime) -> list[dict]:
    """Per-ticker Yahoo Finance headline RSS. One HTTP per ticker, mirrors
    the EDGAR per-ticker pattern. Returns items with source='yahoo'.

    Yahoo's feed is undocumented; treat fetch failures as soft — log to
    stderr and skip the ticker. If the entire fetch returns 0 items across
    all tickers, that's likely a Yahoo-side outage; main() should log a
    warning but not crash.
    """
    items: list[dict] = []
    for ticker in tickers:
        if ticker.startswith("_"):  # skip pseudo-tickers
            continue
        url = YAHOO_NEWS_URL.format(ticker=urllib.parse.quote(ticker))
        try:
            data = http_get(url)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"yahoo fetch failed for {ticker}: {e}", file=sys.stderr)
            continue
        try:
            text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data
            if "<rss" in text:
                text = text[text.find("<rss"):]
            root = ET.fromstring(text)
        except (ET.ParseError, UnicodeDecodeError, AttributeError) as e:
            print(f"yahoo parse failed for {ticker}: {e}", file=sys.stderr)
            continue
        for entry in root.iter("item"):
            title = (entry.findtext("title") or "").strip()
            if not title:
                continue
            pub = parse_dt_loose(entry.findtext("pubDate") or "")
            if pub and pub < cutoff:
                continue
            link = (entry.findtext("link") or "").strip()
            guid = (entry.findtext("guid") or link or title).strip()
            desc = (entry.findtext("description") or "").strip()
            # Strip HTML tags from description; Yahoo wraps in CDATA + html.
            desc_clean = re.sub(r"<[^>]+>", " ", desc)
            desc_clean = re.sub(r"\s+", " ", desc_clean).strip()
            items.append({
                "ticker": ticker,
                "source": "yahoo",
                "item_id": hashlib.sha1(guid.encode()).hexdigest()[:12],
                "title": title,
                "description": desc_clean[:500],   # cap to keep state small
                "link": link,
                "pub": pub.isoformat() if pub else "",
                "publisher": "yahoo",
            })
        time.sleep(INTER_REQUEST_DELAY)
    return items


def fetch_8k_items(index_url: str) -> list[str]:
    """Fetch a filing index page and extract 8-K Item codes (e.g. '2.02').

    Returns codes in the order they appear on the page, deduped. Empty list
    on fetch failure or parse miss — caller falls back to the generic 8-K
    label so a transient HTTP failure doesn't silently drop a real filing.
    """
    if not index_url:
        return []
    try:
        data = http_get(index_url)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"8-K index fetch failed for {index_url}: {e}", file=sys.stderr)
        return []
    text = data.decode("utf-8", errors="replace")
    seen, out = set(), []
    for c in re.findall(r"Item\s+(\d+\.\d+)", text):
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def score_8k(item: dict) -> tuple[int, str]:
    """Severity for an 8-K based on its parsed Item codes.

    Drops 9.01 (always-paired exhibit list). Picks the item with the highest
    severity; ties go to whichever is listed first on the index page. If no
    codes are available (fetch failed or page changed format), fall back to
    the generic sev-4 label so we don't lose the filing.
    """
    codes = [c for c in item.get("items", []) if c != "9.01"]
    if not codes:
        return (4, "8-K filing")
    best_sev, best_code, best_label = -1, "", "other material event"
    for code in codes:
        sev, label = EIGHT_K_ITEM_INFO.get(code, (4, "other material event"))
        if sev > best_sev:
            best_sev, best_code, best_label = sev, code, label
    return (best_sev, f"8-K — {best_label} (Item {best_code})")


# ---- Pushover ---------------------------------------------------------

NEWS_READ_ENV_DIR = Path("/tmp/news-read")


def trigger_news_read(ticker: str, category: str, title: str, link: str = "") -> bool:
    """Spawn a transient news-read systemd unit for a sev-4 alert on any
    real ticker (Tier 1 or Tier 2; pseudo-tickers excluded upstream).

    Each invocation starts an instance of news-read@<INSTANCE>.service via
    `sudo systemctl start --no-block`. The transient unit gets its own
    cgroup, so it survives this worker's intraday-news.service exit.
    (Previous Popen-detach approach was killed by systemd cgroup-kill on
    parent oneshot exit — see vault/notes for the 2026-05-14 incident.)

    Args are passed via /tmp/news-read/<INSTANCE>.env (sourced by the
    wrapper script). The unit's ExecStopPost line cleans up the env file;
    this function also cleans up best-effort if the start call itself
    fails (in which case ExecStopPost won't run).

    Failure mode: env-file write fails or systemctl errors → log to
    stderr, return False. The Pushover alert has already fired, so the
    user still got the headline ping; we just skip the auto-follow-up.
    """
    import subprocess  # local import — only used on this code path
    instance = f"{ticker}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    try:
        NEWS_READ_ENV_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"news-read env dir create failed: {e}", file=sys.stderr)
        return False
    env_file = NEWS_READ_ENV_DIR / f"{instance}.env"

    def _shellquote(s: str) -> str:
        # Single-quote and escape internal single quotes. The wrapper
        # script sources this file via `. file`, so values must be
        # shell-safe.
        return "'" + (s or "").replace("'", "'\\''") + "'"

    try:
        env_file.write_text(
            f"TICKER={_shellquote(ticker)}\n"
            f"CATEGORY={_shellquote(category)}\n"
            f"HEADLINE={_shellquote(title)}\n"
            f"URL={_shellquote(link)}\n",
            encoding="utf-8",
        )
    except OSError as e:
        print(f"news-read env file write failed for {ticker}: {e}", file=sys.stderr)
        return False

    unit = f"news-read@{instance}.service"
    try:
        subprocess.run(
            ["sudo", "-n", "systemctl", "start", "--no-block", unit],
            check=True, timeout=5,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"news-read spawn failed for {ticker}: {e}", file=sys.stderr)
        # Best-effort cleanup; ExecStopPost won't run if start failed.
        try:
            env_file.unlink()
        except OSError:
            pass
        return False
    return True


class PushoverError(RuntimeError):
    pass


def send_pushover(title: str, message: str, priority: int = 1) -> None:
    token = os.environ.get("PUSHOVER_TOKEN")
    user = os.environ.get("PUSHOVER_USER")
    if not token or not user:
        raise PushoverError("PUSHOVER_TOKEN and PUSHOVER_USER must be set")
    title = title[:250]
    message = message[:1024]
    body = urllib.parse.urlencode({
        "token": token, "user": user,
        "title": title, "message": message,
        "priority": str(priority),
    }).encode("utf-8")
    req = urllib.request.Request(PUSHOVER_URL, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            payload = json.loads(data) if data else {}
            if payload.get("status") != 1:
                raise PushoverError(f"non-success: {data}")
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise PushoverError(f"HTTP {e.code}: {err}") from e
    except urllib.error.URLError as e:
        raise PushoverError(str(e)) from e


# ---- Pipeline ---------------------------------------------------------

FORM144_CLUSTER_THRESHOLD = 3


def mark_form144_clusters(items: list[dict]) -> None:
    """Tag Form 144 filings whose ticker has 3+ Form 144s in the same batch.
    A single insider filing a 10b5-1 proposed-sale notice is noise; a cluster
    of 3+ insiders within the same 24h window is a coordinated-sell signal
    worth surfacing. Mutates items in place (adds `cluster_member: True`).
    The 24h EDGAR lookback ensures the cluster window matches the batch."""
    counts: dict[str, int] = {}
    for it in items:
        if it.get("source") == "edgar" and it.get("filing_type") == "144" \
                and not it["ticker"].startswith("_FILER_"):
            counts[it["ticker"]] = counts.get(it["ticker"], 0) + 1
    clustered = {t for t, n in counts.items() if n >= FORM144_CLUSTER_THRESHOLD}
    for it in items:
        if it.get("filing_type") == "144" and it["ticker"] in clustered:
            it["cluster_member"] = True


def score_item(item: dict) -> tuple[int, str]:
    if item["source"] == "edgar":
        ft = item.get("filing_type", "")
        is_filer = item["ticker"].startswith("_FILER_")
        if ft in ("8-K", "8-K/A") and not is_filer:
            return score_8k(item)
        if is_filer:
            return EDGAR_FILING_SEV_FILER.get(ft, (0, ""))
        if ft == "144" and item.get("cluster_member"):
            return (3, f"Form 144 cluster ({FORM144_CLUSTER_THRESHOLD}+ insiders, 24h)")
        return EDGAR_FILING_SEV_TICKER.get(ft, (0, ""))
    if item["source"] == "fed":
        return classify_macro(item["title"])
    if item["source"] == "yahoo":
        return classify_wire(item["title"], item.get("description", ""), item["ticker"])
    return classify_headline(item["title"])


def _normalize_title(title: str) -> str:
    """Normalize a headline for content-hash dedup across tickers.
    Lowercase, strip punctuation, collapse whitespace. Aggregators like
    Yahoo cross-tag the same article with multiple tickers; we want to
    surface ONE alert with a multi-ticker label rather than fire twice."""
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def dedup_by_content(items: list[dict]) -> list[dict]:
    """Collapse same-content items across tickers for wire-aggregator
    sources. Mutates the surviving item to have a `tickers` list of all
    tickers the article was tagged with. Preserves per-ticker `ticker`
    field on the survivor (set to the first ticker seen) for state-key
    backward compatibility. Non-wire sources pass through untouched.
    """
    by_hash: dict[str, dict] = {}
    out: list[dict] = []
    for it in items:
        if it.get("source") != "yahoo":
            out.append(it)
            continue
        key = _normalize_title(it.get("title", ""))
        if not key:
            out.append(it)
            continue
        if key in by_hash:
            existing = by_hash[key]
            tickers = existing.setdefault("tickers", [existing["ticker"]])
            if it["ticker"] not in tickers:
                tickers.append(it["ticker"])
            continue
        by_hash[key] = it
        out.append(it)
    return out


def fire_id(item: dict) -> str:
    return f"{item['ticker']}:{item['source']}:{item['item_id']}"


def display_ticker(it: dict) -> str:
    """Render the ticker label for push/log: friendly name for pseudo-tickers
    like `_FILER_SA_LP` (→ "SA LP"), comma-joined list for cross-tagged wire
    items (VRT,DLR), raw ticker otherwise."""
    if it.get("display_name"):
        return it["display_name"]
    tickers = it.get("tickers")
    if tickers and len(tickers) > 1:
        return ",".join(tickers)
    return it["ticker"]


def format_push_body(items: list[dict], stamp: str) -> str:
    lines = [stamp, ""]
    for it in items:
        lines.append(f"[{display_ticker(it)}] {it['category']}")
        lines.append(f"  {it['title'][:160]}")
        if it.get("publisher"):
            lines.append(f"  via {it['publisher']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_log_block(items: list[dict], stamp_short: str) -> str:
    lines = [f"## {stamp_short}", ""]
    for it in items:
        sev_marker = "**sev 4 — PUSH**" if it["severity"] >= 4 else "sev 3"
        lines.append(f"- [{display_ticker(it)}] {sev_marker} — {it['category']}")
        lines.append(f"  - {it['title']}")
        if it.get("link"):
            lines.append(f"  - {it['link']}")
        meta_bits = []
        if it.get("publisher"):
            meta_bits.append(f"via {it['publisher']}")
        if it.get("filing_type"):
            meta_bits.append(f"filing {it['filing_type']}")
        if it.get("pub"):
            meta_bits.append(it["pub"])
        if meta_bits:
            lines.append(f"  - {' · '.join(meta_bits)}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", default=".intraday-state")
    ap.add_argument("--vault-dir", default="vault/reports/intraday-alerts")
    ap.add_argument("--dry-run", action="store_true",
                    help="Skip push, vault log write, state write.")
    ap.add_argument("--ticker", action="append",
                    help="Override watchlist tickers (repeatable, for testing).")
    ap.add_argument("--lookback-hours", type=int, default=LOOKBACK_HOURS,
                    help=f"Reject feed items older than this. Default {LOOKBACK_HOURS}.")
    ap.add_argument("--no-macro", action="store_true",
                    help="Skip the Federal Reserve macro feed (testing).")
    ap.add_argument("--no-filers", action="store_true",
                    help="Skip the WATCHED_FILERS EDGAR feeds (testing).")
    ap.add_argument("--no-yahoo", action="store_true",
                    help="Skip the Yahoo Finance per-ticker RSS source.")
    ap.add_argument("--no-news-read", "--no-deep-dive", action="store_true",
                    dest="no_news_read",
                    help="Don't auto-trigger news-read on sev-4 for real "
                         "tickers (Tier 1 + Tier 2). "
                         "(--no-deep-dive kept as a deprecated alias.)")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=args.lookback_hours)
    today_iso = now.date().isoformat()
    stamp_short = now.strftime("%H:%M UTC")
    stamp = f"{today_iso} {stamp_short}"

    tickers = args.ticker or load_active_tickers()
    if not tickers:
        print("no Tier 1/2 tickers found; nothing to do.", file=sys.stderr)
        return 0
    print(f"checking {len(tickers)} tickers: {', '.join(tickers)}")

    raw_items: list[dict] = []
    raw_items.extend(fetch_alpaca_news(tickers, cutoff))
    time.sleep(INTER_REQUEST_DELAY)
    if not args.no_macro:
        raw_items.extend(fetch_fed_press(cutoff))
        time.sleep(INTER_REQUEST_DELAY)
    for t in tickers:
        cik = load_cik(t)
        if cik:
            raw_items.extend(fetch_edgar(t, cik, cutoff))
            time.sleep(INTER_REQUEST_DELAY)

    # Watched non-ticker filers (e.g. hedge funds whose 13F moves our names).
    # Each pseudo-ticker behaves like _MACRO — same dedup, same routing — but
    # is excluded from the news-read trigger by is_real_ticker (pseudo-tickers
    # start with `_` and have no thesis note or watchlist row to read).
    if not args.no_filers:
        for f in WATCHED_FILERS:
            filer_items = fetch_edgar(f["pseudo_ticker"], f["cik"], cutoff)
            for it in filer_items:
                it["display_name"] = f["label"]
            raw_items.extend(filer_items)
            time.sleep(INTER_REQUEST_DELAY)

    # Yahoo Finance per-ticker headline RSS. Aggregator across MotleyFool,
    # Investing.com, Zacks, etc. Fills the small/mid-cap coverage gap that
    # Alpaca/Benzinga has on names like VRT, DLR, GEV. Undocumented endpoint,
    # so a fetch failure here is non-fatal — log and continue.
    yahoo_count = 0
    if not args.no_yahoo:
        yahoo_items = fetch_yahoo_news(tickers, cutoff)
        yahoo_count = len(yahoo_items)
        raw_items.extend(yahoo_items)
        if yahoo_count == 0:
            print("warning: yahoo returned 0 items across all tickers — "
                  "feed may be down", file=sys.stderr)

    # Cross-ticker content-hash dedup for wire/aggregator items. Same article
    # tagged with multiple tickers (e.g. "Better Datacenter Stock: VRT or
    # DLR?") collapses to one item with a multi-ticker label.
    raw_items = dedup_by_content(raw_items)

    # Enrich 8-K filings with their Item codes so severity routing knows
    # whether it's an earnings release (log only), an exec change (push),
    # an M&A item (push), etc. One extra HTTP per 8-K — rare event, cheap.
    for it in raw_items:
        if it.get("source") == "edgar" and it.get("filing_type") in ("8-K", "8-K/A"):
            codes = fetch_8k_items(it.get("link", ""))
            if codes:
                it["items"] = codes
            time.sleep(INTER_REQUEST_DELAY)

    mark_form144_clusters(raw_items)

    scored: list[dict] = []
    for it in raw_items:
        sev, cat = score_item(it)
        if sev < 3:
            continue
        it["severity"] = sev
        it["category"] = cat
        scored.append(it)
    print(f"fetched {len(raw_items)} items, {len(scored)} sev>=3 after scoring.")

    state_dir = Path(args.state_dir)
    state_path = state_dir / f"news-{today_iso}.json"
    # Load today's AND yesterday's state to prevent bleed-over. At the UTC
    # date boundary a fresh empty state file is created, but the 24h lookback
    # still pulls prior-afternoon filings — without yesterday's state, every
    # sev-4 from late yesterday re-fires at ~10:00 UTC this morning.
    yesterday_iso = (now.date() - timedelta(days=1)).isoformat()
    already: set[str] = set()
    for sp in (state_path, state_dir / f"news-{yesterday_iso}.json"):
        if sp.exists():
            try:
                already |= set(json.loads(sp.read_text(encoding="utf-8")).get("alerted", []))
            except (OSError, json.JSONDecodeError):
                pass

    # Load the (ticker, category) cooldown set from the last COOLDOWN_STATE_DAYS
    # of state files. Catches the same underlying event re-surfacing from a
    # different source (Benzinga vs Yahoo) or as a next-day editorial follow-up
    # with a different headline — both routes produce fresh fire_ids that
    # the alerted-set dedup misses.
    cooldown_cutoff = now - timedelta(hours=CATEGORY_COOLDOWN_HOURS)
    cooldowns: dict[tuple[str, str], datetime] = {}
    for days_back in range(COOLDOWN_STATE_DAYS):
        sp = state_dir / f"news-{(now.date() - timedelta(days=days_back)).isoformat()}.json"
        if not sp.exists():
            continue
        try:
            data = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for entry in data.get("cooldowns", []):
            ts = parse_dt_loose(entry.get("ts", ""))
            if not ts or ts < cooldown_cutoff:
                continue
            key = (entry.get("ticker", ""), entry.get("category", ""))
            if not key[0] or not key[1]:
                continue
            if key not in cooldowns or ts > cooldowns[key]:
                cooldowns[key] = ts

    new_items = [it for it in scored if fire_id(it) not in already]
    if not new_items:
        print(f"no new items after dedup (already alerted today: {len(already)}).")
        return 0

    new_items.sort(key=lambda x: (-x["severity"], x["ticker"]))

    # Apply (ticker, category) cooldown: demote in-cooldown sev-4 items to
    # sev-3 so they still log to the vault but don't push and don't trigger
    # news-read. The original category is preserved with a "(cooldown)" tail
    # so the vault log shows why this didn't escalate.
    cooled_count = 0
    for it in new_items:
        if it["severity"] < 4:
            continue
        key = (it["ticker"], it["category"])
        if key in cooldowns:
            it["severity"] = 3
            it["category"] = f"{it['category']} (cooldown)"
            cooled_count += 1
    if cooled_count:
        print(f"demoted {cooled_count} sev-4 item(s) by 72h (ticker, category) cooldown.")

    push_items = [it for it in new_items if it["severity"] >= 4]
    triggered: set[str] = set()  # news-read tickers; also used for state write

    if push_items:
        # Step 1: trigger news-read FIRST, then build the worker push from
        # whatever news-read didn't claim. This avoids the duplicate-ping
        # problem (one ping from the worker + one from news-read covering
        # the same ticker). Pseudo-tickers (_MACRO, _FILER_*) never get
        # news-read, so they always fall through to the worker push.
        news_read_disabled = (
            args.no_news_read
            or os.environ.get("INTRADAY_NEWS_READ_DISABLED") == "1"
            # Deprecated alias — keeps existing kill-switch envs working.
            or os.environ.get("INTRADAY_DEEP_DIVE_DISABLED") == "1"
        )
        if not news_read_disabled:
            for it in push_items:
                t = it["ticker"]
                if not is_real_ticker(t) or t in triggered:
                    continue
                if args.dry_run:
                    print(f"[DRY RUN] would trigger news-read for {t} "
                          f"({it['category']})")
                    triggered.add(t)
                elif trigger_news_read(
                    t, it["category"], it["title"], it.get("link", ""),
                ):
                    triggered.add(t)
            if triggered and not args.dry_run:
                print(f"triggered news-read: {', '.join(sorted(triggered))}")

        # Step 2: worker push covers ONLY items news-read didn't take.
        # If news-read claimed every push item, the worker stays silent —
        # the user gets one rich news-read ping per ticker instead of two
        # pings (immediate headline + delayed analysis).
        worker_push_items = [it for it in push_items if it["ticker"] not in triggered]

        if worker_push_items:
            if len(worker_push_items) == 1:
                wi = worker_push_items[0]
                push_title = f"[{display_ticker(wi)}] {wi['category']}"
            else:
                push_title = f"{len(worker_push_items)} critical news items"
            push_body = format_push_body(worker_push_items, stamp)
            if args.dry_run:
                print(f"[DRY RUN] would push: {push_title}")
                print("---")
                print(push_body)
                print("---")
            else:
                try:
                    send_pushover(title=push_title, message=push_body, priority=1)
                    print(f"pushed: {push_title}")
                except PushoverError as e:
                    print(f"pushover send failed: {e}", file=sys.stderr)
                    return 1
        elif push_items:
            print(f"worker push suppressed: news-read covers all "
                  f"{len(push_items)} sev-4 item(s).")
    else:
        print(f"{len(new_items)} sev-3 items, no sev-4 push.")

    if args.dry_run:
        print(f"[DRY RUN] would log {len(new_items)} items, would mark {len(new_items)} new ids.")
        for it in new_items:
            print(f"  - sev{it['severity']} [{it['ticker']}] {it['category']}: {it['title'][:120]}")
        return 0

    vault_log = Path(args.vault_dir) / f"news-{today_iso}.md"
    vault_log.parent.mkdir(parents=True, exist_ok=True)
    if not vault_log.exists():
        vault_log.write_text(
            f"# Intraday News Alerts — {today_iso}\n\n"
            "Auto-generated by `.claude/scripts/check_intraday_news.py`. "
            "One block per 20-min tick that produced new sev>=3 items. "
            "Sev-4 items also push to Pushover. Not investment advice.\n\n",
            encoding="utf-8",
        )
    with vault_log.open("a", encoding="utf-8") as f:
        f.write(format_log_block(new_items, stamp_short))

    state_dir.mkdir(parents=True, exist_ok=True)

    # Carry forward today's existing cooldown entries (a prior tick this
    # same day may have already written some) and append fresh entries for
    # any sev-4 fire we actually triggered this run. "Triggered" means
    # either news-read fired for the ticker OR the worker pushed it —
    # in both cases the user got an alert and the cooldown should start.
    existing_cooldowns: list[dict] = []
    if state_path.exists():
        try:
            existing = json.loads(state_path.read_text(encoding="utf-8"))
            existing_cooldowns = existing.get("cooldowns", [])
        except (OSError, json.JSONDecodeError):
            pass

    # Prune today's existing cooldown list to entries still within the
    # window — keeps the state file bounded across many ticks.
    existing_cooldowns = [
        c for c in existing_cooldowns
        if (parse_dt_loose(c.get("ts", "")) or datetime.min.replace(tzinfo=timezone.utc)) >= cooldown_cutoff
    ]

    now_iso = now.isoformat()
    fresh_cooldowns: list[dict] = []
    # Record cooldown entries for every sev-4 that fired this run — both
    # the ones news-read claimed and the ones the worker pushed. Either
    # path means the user got an alert, so the 72h cooldown should start.
    # (Dry-run returns above before reaching this branch.)
    for it in push_items:
        if it.get("severity", 0) < 4:
            continue
        fresh_cooldowns.append({
            "ticker": it["ticker"],
            "category": it["category"],
            "ts": now_iso,
        })

    state_path.write_text(
        json.dumps({
            "date": today_iso,
            "alerted": sorted(already | {fire_id(it) for it in new_items}),
            "cooldowns": existing_cooldowns + fresh_cooldowns,
        }, indent=2),
        encoding="utf-8",
    )
    print(f"logged {len(new_items)} items to {vault_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
