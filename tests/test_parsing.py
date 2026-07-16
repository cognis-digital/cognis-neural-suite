"""Tests for URL building, date parsing, and feed parsing (RSS + Atom)."""

from __future__ import annotations

import urllib.parse
from datetime import datetime, timezone

from conftest import ATOM_SAMPLE, MALFORMED_XML, RSS_SAMPLE

import livesearch


class TestGoogleNewsUrl:
    def test_encodes_query_and_when(self):
        url = livesearch.google_news_rss("iran oil sanctions", when="7d")
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        assert parsed.netloc == "news.google.com"
        assert parsed.path == "/rss/search"
        assert qs["q"] == ["iran oil sanctions when:7d"]
        assert qs["hl"] == ["en-US"]
        assert qs["gl"] == ["US"]
        assert qs["ceid"] == ["US:en"]

    def test_when_empty_omits_clause(self):
        url = livesearch.google_news_rss("btc", when="")
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        assert qs["q"] == ["btc"]

    def test_lang_country_override(self):
        url = livesearch.google_news_rss("wahl", when="1d", lang="de", country="DE")
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        assert qs["hl"] == ["de-DE"]
        assert qs["gl"] == ["DE"]

    def test_special_chars_are_percent_encoded(self):
        url = livesearch.google_news_rss("a & b/c", when="")
        assert " " not in url
        assert "&q=" not in url  # the ampersand in the query must be encoded, not a separator


class TestParseDt:
    def test_none_and_blank(self):
        assert livesearch._parse_dt(None) is None
        assert livesearch._parse_dt("") is None
        assert livesearch._parse_dt("   ") is None

    def test_rfc822(self):
        dt = livesearch._parse_dt("Wed, 15 Jul 2026 12:00:00 GMT")
        assert dt == datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)

    def test_iso8601_z(self):
        dt = livesearch._parse_dt("2026-07-13T08:00:00Z")
        assert dt == datetime(2026, 7, 13, 8, 0, tzinfo=timezone.utc)

    def test_iso8601_offset(self):
        dt = livesearch._parse_dt("2026-07-12T08:00:00+02:00")
        assert dt.utcoffset().total_seconds() == 2 * 3600

    def test_naive_iso_gets_utc(self):
        dt = livesearch._parse_dt("2026-07-12T08:00:00")
        assert dt.tzinfo == timezone.utc

    def test_garbage_returns_none(self):
        assert livesearch._parse_dt("not a date at all") is None


class TestTag:
    def test_strips_namespace(self):
        from xml.etree import ElementTree as ET
        el = ET.fromstring('<entry xmlns="http://www.w3.org/2005/Atom"/>')
        assert livesearch._tag(el) == "entry"

    def test_plain_tag(self):
        from xml.etree import ElementTree as ET
        assert livesearch._tag(ET.fromstring("<item/>")) == "item"


class TestFetchFeedRss:
    def test_parses_items(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        items = livesearch.fetch_feed("https://x/feed")
        assert len(items) == 3
        first = items[0]
        assert first["title"] == "Rare earth export curbs tighten & ripple"  # entities unescaped
        assert first["link"] == "https://example.com/a"
        assert first["published"] == "2026-07-15T12:00:00Z"

    def test_source_defaults_to_feed_title(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        items = livesearch.fetch_feed("https://x/feed")
        assert items[0]["source"] == "Example News"

    def test_explicit_source_overrides(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        items = livesearch.fetch_feed("https://x/feed", source="mine")
        assert all(it["source"] == "mine" for it in items)

    def test_limit_caps_items(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        items = livesearch.fetch_feed("https://x/feed", limit=1)
        assert len(items) == 1

    def test_all_fields_present(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        for it in livesearch.fetch_feed("https://x/feed"):
            assert set(it) == set(livesearch.FIELDS)


class TestFetchFeedAtom:
    def test_parses_atom_link_href_and_dates(self, fake_get):
        fake_get.set(ATOM_SAMPLE)
        items = livesearch.fetch_feed("https://x/atom")
        assert len(items) == 2
        assert items[0]["link"] == "https://atom.example/1"
        assert items[0]["published"] == "2026-07-13T08:00:00Z"
        # +02:00 published normalized to UTC
        assert items[1]["published"] == "2026-07-12T06:00:00Z"


class TestFetchFeedErrors:
    def test_malformed_xml_returns_empty(self, fake_get):
        fake_get.set(MALFORMED_XML)
        assert livesearch.fetch_feed("https://x/bad") == []

    def test_network_error_returns_empty(self, fake_get):
        fake_get.set(OSError("boom"))
        assert livesearch.fetch_feed("https://x/down") == []
