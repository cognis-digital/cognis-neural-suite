# Usage — `livesearch`

`livesearch` is a keyless, dependency-free live web-search and feed-ingestion
module. It can be used as a library (import the functions) or as a CLI
(`python -m livesearch` / the `livesearch` console script installed by `pip`).

All producers return a **uniform item**:

```json
{
  "title":     "Rare earth export curbs tighten",
  "link":      "https://example.com/story",
  "published": "2026-07-15T12:00:00Z",   // ISO-8601 UTC, or "" if undated
  "source":    "google-news",             // backend or feed title
  "query":     "rare earth"               // set for searches, "" for feeds
}
```

## Install

```bash
pip install -e .            # from the repo root; adds the `livesearch` script
pip install -e ".[dev]"     # + pytest & ruff for development
```

Requires Python 3.10+ and nothing else at runtime.

## Library API

| Function | Purpose |
|---|---|
| `web_search(query, when="7d", limit=50)` | Live web search via Google News RSS (keyless). Stamps `query`/`source`. |
| `fetch_feed(url, limit=50, source="")` | Parse an RSS 2.0 or Atom feed into items. Returns `[]` on network/parse error. |
| `ddg_search(query, limit=25)` | Keyless search by scraping DuckDuckGo's HTML endpoint (fallback). |
| `harvest(sources, since_days=14, per_source=30, min_year=2026)` | Run a mixed list of feed URLs and `{"query": ...}` dicts; keep recent, de-dupe by link, sort newest-first. |
| `google_news_rss(query, when, lang, country)` | Build the Google News RSS search URL (keyless search backend). |

### Output & filtering helpers

| Function | Purpose |
|---|---|
| `to_json(items, indent=2)` | Pretty JSON array (UTF-8, non-ASCII preserved). |
| `to_ndjson(items)` | Newline-delimited JSON — one object per line, ideal for `jq -c` and log pipelines. |
| `to_csv(items)` | CSV with a fixed header row in `FIELDS` order. |
| `render(items, fmt)` | Render as `plain` / `json` / `ndjson` / `csv`. |
| `filter_items(items, match=None, source=None)` | Keep items whose title/link match a regex and/or whose source contains a substring. |
| `dedupe(items)` | De-duplicate by `link`, preserving first-seen order. |
| `load_sources(path)` | Parse a sources file into a `harvest`-ready list. |

### Example

```python
from livesearch import harvest, filter_items, to_csv

items = harvest([
    {"query": "rare earth export", "when": "7d"},
    "https://feeds.example.com/markets.rss",
], since_days=7)

china = filter_items(items, match="china|beijing", source="google-news")
print(to_csv(china))
```

## CLI

```
python -m livesearch [query] [options]
```

| Option | Description |
|---|---|
| `query` | Search query (Google News RSS backend). |
| `--feed URL` | Fetch/parse an RSS/Atom feed instead of searching. |
| `--ddg` | Use the DuckDuckGo HTML scrape backend for `query`. |
| `--harvest FILE` | Run `harvest()` over a sources file (one feed URL or `q: query` per line). |
| `--since-days N` | With `--harvest`: keep items newer than N days (default 14). |
| `--when W` | Recency bound for search (`1h`, `1d`, `7d`, …; default `7d`). |
| `--limit N` | Max items per source (default 25). |
| `--match REGEX` | Keep only items whose title/link match the regex (case-insensitive). |
| `--source TEXT` | Keep only items whose source contains this text. |
| `--format FMT` | `plain` (default), `json`, `ndjson`, or `csv`. |
| `--json` | Shortcut for `--format json` (backward-compatible). |

### Sources file format (`--harvest`)

One entry per line; blank lines and `#` comments are ignored.

```text
# feeds are fetched as-is
https://feeds.example.com/markets.rss

# 'q:' (or 'query:') lines become live web searches
q: rare earth export controls

# a plain keyword line is also treated as a search query
lithium supply chain
```

See [`examples/sources.txt`](../examples/sources.txt) for a runnable sample.

### CLI examples

```bash
# Latest week, plain human-readable
python -m livesearch "critical minerals" --when 7d

# CSV, filtered to China-related gallium stories in the last day
python -m livesearch "critical minerals" --when 1d --match "gallium|china" --format csv

# NDJSON harvest across a file of feeds + queries, last 7 days
python -m livesearch --harvest examples/sources.txt --since-days 7 --format ndjson | jq -c .

# Parse a single feed as JSON
python -m livesearch --feed https://feeds.example.com/markets.rss --json
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success (zero or more items printed). |
| `2` | Usage error — no query/`--feed`/`--harvest`, or an invalid `--match` regex. |
