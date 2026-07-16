"""livesearch — real-time web-search & feed ingestion for Cognis monitoring tools.

Drop this module into any monitoring/OSINT repo to give it a *live* source of
current items, with no API keys and no third-party dependencies (standard library
only: urllib + xml.etree). Everything is fetched at call time, so the data is always
as current as the web — the design goal is real-time monitoring, not static lists.

Three ways in, all returning a uniform list of dated items
``{"title","link","published","source","query"}``:

* ``web_search(query, when="7d")`` — Google News RSS as a keyless search backend
  (always reflects the live web; ``when`` bounds recency: "1d"/"7d"/"1h"...).
* ``fetch_feed(url)``             — parse any RSS 2.0 / Atom feed.
* ``ddg_search(query)``          — DuckDuckGo HTML scrape fallback (no feed needed).

``harvest(sources, since_days=...)`` runs a mixed list of queries + feed URLs,
keeps only recent items, de-dupes by link, and sorts newest-first.

Output helpers turn any item list into the format you need for downstream tools:
``to_json`` / ``to_ndjson`` / ``to_csv``. ``filter_items`` narrows a list by a
title/link regex or by source, and ``load_sources`` reads a mixed sources file
(one feed URL or ``q: query`` per line) for batch ``harvest`` runs.

CLI:
    python -m livesearch "iran oil sanctions" --when 7d --json
    python -m livesearch "rare earth export" --format csv --match "china|beijing"
    python -m livesearch --harvest sources.txt --since-days 7 --format ndjson
"""

from __future__ import annotations

import csv
import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

USER_AGENT = "Mozilla/5.0 (compatible; CognisLiveSearch/1.0; +https://cognis.digital)"
TIMEOUT = 20

#: Uniform ordering of the item fields every producer emits.
FIELDS = ("title", "link", "published", "source", "query")


def _get(url: str, retries: int = 2, backoff: float = 0.5) -> bytes:
    """Fetch ``url`` as bytes with a bounded exponential-backoff retry.

    A single successful request behaves exactly as a plain GET. Transient
    network errors (``URLError``/``OSError``) are retried up to ``retries``
    additional times, sleeping ``backoff * 2**attempt`` seconds between tries;
    the final failure is re-raised so callers keep their existing error paths.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    attempt = 0
    while True:
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # nosec - read-only GET
                return r.read()
        except OSError:
            if attempt >= retries:
                raise
            time.sleep(backoff * (2 ** attempt))
            attempt += 1


def google_news_rss(query: str, when: str = "7d",
                    lang: str = "en", country: str = "US") -> str:
    """Build a Google News RSS search URL — a keyless, always-current search feed."""
    q = query if not when else f"{query} when:{when}"
    qs = urllib.parse.urlencode({"q": q, "hl": f"{lang}-{country}",
                                 "gl": country, "ceid": f"{country}:{lang}"})
    return f"https://news.google.com/rss/search?{qs}"


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        return parsedate_to_datetime(value)  # RFC-822 (RSS pubDate)
    except (TypeError, ValueError):
        pass
    try:  # ISO-8601 (Atom updated/published)
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _tag(el) -> str:
    return el.tag.split("}", 1)[-1]  # strip namespace


def fetch_feed(url: str, limit: int = 50, source: str = "") -> list[dict]:
    """Parse an RSS 2.0 or Atom feed into uniform dated items."""
    try:
        root = ET.fromstring(_get(url))
    except (ET.ParseError, OSError):
        return []
    items: list[dict] = []
    # RSS: channel/item ; Atom: feed/entry
    nodes = [e for e in root.iter() if _tag(e) in ("item", "entry")]
    feed_title = ""
    for e in root.iter():
        if _tag(e) == "title":
            feed_title = (e.text or "").strip()
            break
    for node in nodes[:limit]:
        title = link = pub = ""
        for ch in node:
            t = _tag(ch)
            if t == "title":
                title = (ch.text or "").strip()
            elif t == "link":
                link = (ch.get("href") or ch.text or "").strip()
            elif t in ("pubDate", "published", "updated", "date"):
                pub = (ch.text or "").strip()
        dt = _parse_dt(pub)
        items.append({
            "title": html.unescape(title),
            "link": link,
            "published": dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if dt else "",
            "source": source or feed_title or urllib.parse.urlparse(url).netloc,
            "query": "",
        })
    return items


def web_search(query: str, when: str = "7d", limit: int = 50) -> list[dict]:
    """Live web search via Google News RSS (keyless, real-time)."""
    items = fetch_feed(google_news_rss(query, when=when), limit=limit, source="google-news")
    for it in items:
        it["query"] = query
    return items


_DDG_RE = re.compile(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>', re.S)


def ddg_search(query: str, limit: int = 25) -> list[dict]:
    """Fallback keyless web search by scraping DuckDuckGo's HTML endpoint."""
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    try:
        body = _get(url).decode("utf-8", "replace")
    except OSError:
        return []
    out = []
    for href, raw in _DDG_RE.findall(body)[:limit]:
        # DDG wraps targets in a redirect; pull the real uddg= param when present
        m = re.search(r"uddg=([^&]+)", href)
        link = urllib.parse.unquote(m.group(1)) if m else href
        title = html.unescape(re.sub("<.*?>", "", raw)).strip()
        out.append({"title": title, "link": link, "published": "",
                    "source": "duckduckgo", "query": query})
    return out


def harvest(sources: list, since_days: int = 14, per_source: int = 30,
            min_year: int = 2026) -> list[dict]:
    """Run a mixed list of feed URLs and {'query':...} dicts; keep recent, de-dupe.

    `sources` items may be: a feed URL str, or a dict with either ``url`` (feed) or
    ``query`` (live web search, optional ``when``). Only items newer than
    `since_days` (or with no date) and not older than `min_year` are kept.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days) \
        if since_days else None
    seen: set[str] = set()
    out: list[dict] = []
    for s in sources:
        if isinstance(s, str):
            items = fetch_feed(s, limit=per_source)
        elif "query" in s:
            items = web_search(s["query"], when=s.get("when", "7d"), limit=per_source)
        elif "url" in s:
            items = fetch_feed(s["url"], limit=per_source, source=s.get("source", ""))
        else:
            continue
        for it in items:
            if not it["link"] or it["link"] in seen:
                continue
            dt = _parse_dt(it["published"]) if it["published"] else None
            if dt:
                if dt.year < min_year:
                    continue
                if cutoff and dt < cutoff:
                    continue
            seen.add(it["link"])
            out.append(it)
    out.sort(key=lambda x: x["published"] or "", reverse=True)
    return out


# --------------------------------------------------------------------------- #
# Output / filtering / source-loading helpers (importable, no network)         #
# --------------------------------------------------------------------------- #

def to_json(items: list[dict], indent: int = 2) -> str:
    """Serialize items as a pretty JSON array (UTF-8 safe, key order stable)."""
    return json.dumps(items, indent=indent, ensure_ascii=False)


def to_ndjson(items: Iterable[dict]) -> str:
    """Serialize items as newline-delimited JSON — one object per line.

    NDJSON streams cleanly into log pipelines and tools like ``jq -c``.
    """
    return "\n".join(json.dumps(it, ensure_ascii=False) for it in items)


def to_csv(items: Iterable[dict]) -> str:
    """Serialize items as CSV with a fixed header row (``FIELDS`` order)."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(FIELDS), extrasaction="ignore",
                       lineterminator="\n")
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k, "") for k in FIELDS})
    return buf.getvalue().rstrip("\n")


def filter_items(items: Iterable[dict], match: str | None = None,
                 source: str | None = None) -> list[dict]:
    """Return items whose title/link match ``match`` (regex, case-insensitive)
    and/or whose ``source`` contains ``source`` (case-insensitive substring).

    A ``None`` filter is a no-op, so ``filter_items(items)`` returns a copy.
    Raises ``re.error`` if ``match`` is not a valid regular expression.
    """
    rx = re.compile(match, re.IGNORECASE) if match else None
    src = source.lower() if source else None
    out: list[dict] = []
    for it in items:
        if rx and not (rx.search(it.get("title", "")) or rx.search(it.get("link", ""))):
            continue
        if src and src not in (it.get("source", "") or "").lower():
            continue
        out.append(it)
    return out


def dedupe(items: Iterable[dict]) -> list[dict]:
    """De-duplicate items by ``link``, preserving first-seen order."""
    seen: set[str] = set()
    out: list[dict] = []
    for it in items:
        link = it.get("link", "")
        if link and link in seen:
            continue
        if link:
            seen.add(link)
        out.append(it)
    return out


def load_sources(path: str) -> list:
    """Parse a sources file into a ``harvest``-ready list.

    One entry per line. Blank lines and ``#`` comments are ignored. A line
    beginning ``q:`` (or ``query:``) becomes a live web-search ``{"query": ...}``;
    anything starting ``http`` is treated as a feed URL; any other text is also
    treated as a search query (so a plain keyword line just works).
    """
    sources: list = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            low = line.lower()
            if low.startswith("q:") or low.startswith("query:"):
                sources.append({"query": line.split(":", 1)[1].strip()})
            elif low.startswith("http://") or low.startswith("https://"):
                sources.append(line)
            else:
                sources.append({"query": line})
    return sources


def render(items: list[dict], fmt: str = "plain") -> str:
    """Render an item list in one of: ``plain`` / ``json`` / ``ndjson`` / ``csv``."""
    if fmt == "json":
        return to_json(items)
    if fmt == "ndjson":
        return to_ndjson(items)
    if fmt == "csv":
        return to_csv(items)
    lines = []
    for it in items:
        when = (it.get("published") or "")[:10]
        lines.append(f"[{when:<10}] {it.get('source',''):<16} {it.get('title','')}"
                     f"\n            {it.get('link','')}")
    return "\n".join(lines)


def _cli(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="livesearch",
                                description="keyless real-time web-search / feed ingestion")
    p.add_argument("query", nargs="?", help="search query (Google News RSS)")
    p.add_argument("--feed", help="fetch an RSS/Atom feed URL instead of searching")
    p.add_argument("--ddg", action="store_true", help="use DuckDuckGo HTML scrape")
    p.add_argument("--harvest", metavar="FILE",
                   help="run harvest() over a sources file (one feed URL or 'q: query' per line)")
    p.add_argument("--since-days", type=int, default=14,
                   help="with --harvest: keep items newer than N days (default 14)")
    p.add_argument("--when", default="7d", help="recency bound for search (e.g. 1d, 7d, 1h)")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--match", help="keep only items whose title/link match this regex")
    p.add_argument("--source", help="keep only items whose source contains this text")
    p.add_argument("--format", choices=["plain", "json", "ndjson", "csv"],
                   help="output format (default: plain; --json is a shortcut for json)")
    p.add_argument("--json", action="store_true", help="shortcut for --format json")
    a = p.parse_args(argv)
    if a.harvest:
        items = harvest(load_sources(a.harvest), since_days=a.since_days, per_source=a.limit)
    elif a.feed:
        items = fetch_feed(a.feed, limit=a.limit)
    elif a.ddg and a.query:
        items = ddg_search(a.query, limit=a.limit)
    elif a.query:
        items = web_search(a.query, when=a.when, limit=a.limit)
    else:
        p.error("give a query, --feed URL, or --harvest FILE")
        return 2
    if a.match or a.source:
        try:
            items = filter_items(items, match=a.match, source=a.source)
        except re.error as exc:
            p.error(f"invalid --match regex: {exc}")
            return 2
    fmt = a.format or ("json" if a.json else "plain")
    print(render(items, fmt))
    return 0


def _entry() -> None:
    """Console-script entry point (see ``[project.scripts]`` in pyproject)."""
    raise SystemExit(_cli(sys.argv[1:]))


if __name__ == "__main__":
    _entry()
