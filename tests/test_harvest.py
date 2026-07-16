"""Tests for harvest(): recency filtering, de-dupe, min-year, sorting, mixed sources."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import livesearch


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@pytest.fixture
def patched_feed(monkeypatch):
    """Replace fetch_feed/web_search with deterministic in-memory producers."""
    now = datetime.now(timezone.utc)
    store = {
        "https://feed/a": [
            {"title": "fresh a", "link": "https://a/1", "published": _iso(now - timedelta(days=1)),
             "source": "A", "query": ""},
            {"title": "stale a", "link": "https://a/old", "published": _iso(now - timedelta(days=40)),
             "source": "A", "query": ""},
        ],
        "https://feed/b": [
            {"title": "fresh b", "link": "https://b/1", "published": _iso(now - timedelta(days=2)),
             "source": "B", "query": ""},
            {"title": "dup of a", "link": "https://a/1", "published": _iso(now - timedelta(days=1)),
             "source": "B", "query": ""},
            {"title": "no date", "link": "https://b/nodate", "published": "",
             "source": "B", "query": ""},
        ],
    }

    def fake_fetch(url, limit=50, source=""):
        return [dict(x) for x in store.get(url, [])][:limit]

    def fake_search(query, when="7d", limit=50):
        out = [dict(x) for x in store.get("https://feed/a", [])]
        for it in out:
            it["query"] = query
        return out[:limit]

    monkeypatch.setattr(livesearch, "fetch_feed", fake_fetch)
    monkeypatch.setattr(livesearch, "web_search", fake_search)
    return store


class TestHarvest:
    def test_dedupes_by_link(self, patched_feed):
        out = livesearch.harvest(["https://feed/a", "https://feed/b"], since_days=14)
        links = [it["link"] for it in out]
        assert links.count("https://a/1") == 1

    def test_drops_items_older_than_since_days(self, patched_feed):
        out = livesearch.harvest(["https://feed/a"], since_days=14)
        assert "https://a/old" not in {it["link"] for it in out}

    def test_keeps_undated_items(self, patched_feed):
        out = livesearch.harvest(["https://feed/b"], since_days=14)
        assert "https://b/nodate" in {it["link"] for it in out}

    def test_query_source_dict(self, patched_feed):
        out = livesearch.harvest([{"query": "gold"}], since_days=14)
        assert out
        assert all(it["query"] == "gold" for it in out)

    def test_url_dict_source(self, patched_feed):
        out = livesearch.harvest([{"url": "https://feed/a", "source": "custom"}], since_days=14)
        assert {it["link"] for it in out} == {"https://a/1"}

    def test_unknown_dict_skipped(self, patched_feed):
        out = livesearch.harvest([{"nonsense": 1}, "https://feed/a"], since_days=14)
        assert out  # the good source still produced items

    def test_sorted_newest_first(self, patched_feed):
        out = livesearch.harvest(["https://feed/a", "https://feed/b"], since_days=14)
        published = [it["published"] for it in out if it["published"]]
        assert published == sorted(published, reverse=True)

    def test_min_year_filter(self, monkeypatch):
        def fake_fetch(url, limit=50, source=""):
            return [{"title": "ancient", "link": "https://x/ancient",
                     "published": "2001-01-01T00:00:00Z", "source": "x", "query": ""}]
        monkeypatch.setattr(livesearch, "fetch_feed", fake_fetch)
        out = livesearch.harvest(["https://x"], since_days=0, min_year=2026)
        assert out == []

    def test_since_days_zero_disables_cutoff(self, patched_feed):
        # since_days=0 => no recency cutoff, but min_year (default 2026) still applies
        out = livesearch.harvest(["https://feed/a"], since_days=0)
        assert "https://a/old" in {it["link"] for it in out}
