"""Tests for output helpers, filtering, dedupe, and load_sources."""

from __future__ import annotations

import csv
import io
import json

import pytest

import livesearch

ITEMS = [
    {"title": "China curbs gallium", "link": "https://x/1",
     "published": "2026-07-15T12:00:00Z", "source": "google-news", "query": "gallium"},
    {"title": "Copper rallies", "link": "https://x/2",
     "published": "2026-07-14T00:00:00Z", "source": "Reuters Metals", "query": "copper"},
    {"title": "Unicode café résumé", "link": "https://x/3",
     "published": "", "source": "duckduckgo", "query": "q"},
]


class TestToJson:
    def test_roundtrips(self):
        assert json.loads(livesearch.to_json(ITEMS)) == ITEMS

    def test_unicode_not_escaped(self):
        assert "café" in livesearch.to_json(ITEMS)


class TestToNdjson:
    def test_one_object_per_line(self):
        text = livesearch.to_ndjson(ITEMS)
        lines = text.splitlines()
        assert len(lines) == 3
        assert all(json.loads(ln) for ln in lines)
        assert json.loads(lines[0])["link"] == "https://x/1"


class TestToCsv:
    def test_header_and_rows(self):
        text = livesearch.to_csv(ITEMS)
        rows = list(csv.DictReader(io.StringIO(text)))
        assert list(rows[0].keys()) == list(livesearch.FIELDS)
        assert len(rows) == 3
        assert rows[0]["title"] == "China curbs gallium"

    def test_missing_keys_become_blank(self):
        text = livesearch.to_csv([{"title": "only title"}])
        rows = list(csv.DictReader(io.StringIO(text)))
        assert rows[0]["link"] == ""


class TestFilterItems:
    def test_none_is_copy(self):
        out = livesearch.filter_items(ITEMS)
        assert out == ITEMS and out is not ITEMS

    def test_match_regex_on_title(self):
        out = livesearch.filter_items(ITEMS, match="copper|gallium")
        assert {it["link"] for it in out} == {"https://x/1", "https://x/2"}

    def test_match_is_case_insensitive(self):
        assert len(livesearch.filter_items(ITEMS, match="CHINA")) == 1

    def test_match_on_link(self):
        assert len(livesearch.filter_items(ITEMS, match="x/3")) == 1

    def test_source_substring(self):
        out = livesearch.filter_items(ITEMS, source="reuters")
        assert [it["link"] for it in out] == ["https://x/2"]

    def test_combined_filters(self):
        out = livesearch.filter_items(ITEMS, match="curbs", source="google")
        assert [it["link"] for it in out] == ["https://x/1"]

    def test_invalid_regex_raises(self):
        with pytest.raises(__import__("re").error):
            livesearch.filter_items(ITEMS, match="(unclosed")


class TestDedupe:
    def test_preserves_first_seen_order(self):
        dupes = ITEMS + [dict(ITEMS[0])]
        out = livesearch.dedupe(dupes)
        assert len(out) == 3
        assert out[0]["link"] == "https://x/1"

    def test_blank_links_all_kept(self):
        blanks = [{"link": ""}, {"link": ""}]
        assert len(livesearch.dedupe(blanks)) == 2


class TestLoadSources:
    def test_parses_mixed(self, tmp_path):
        p = tmp_path / "sources.txt"
        p.write_text(
            "\n".join([
                "# a comment",
                "",
                "https://feeds.example.com/rss",
                "q: rare earth export",
                "query: lithium supply",
                "just some keywords",
            ]),
            encoding="utf-8",
        )
        srcs = livesearch.load_sources(str(p))
        assert srcs == [
            "https://feeds.example.com/rss",
            {"query": "rare earth export"},
            {"query": "lithium supply"},
            {"query": "just some keywords"},
        ]

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("\n# only comments\n", encoding="utf-8")
        assert livesearch.load_sources(str(p)) == []


class TestRender:
    def test_plain_contains_title_and_link(self):
        text = livesearch.render(ITEMS[:1], "plain")
        assert "China curbs gallium" in text
        assert "https://x/1" in text
        assert "2026-07-15" in text

    def test_json_format(self):
        assert json.loads(livesearch.render(ITEMS, "json")) == ITEMS

    def test_csv_format(self):
        assert livesearch.render(ITEMS, "csv").splitlines()[0] == ",".join(livesearch.FIELDS)

    def test_ndjson_format(self):
        assert len(livesearch.render(ITEMS, "ndjson").splitlines()) == 3

    def test_unknown_format_falls_back_to_plain(self):
        assert "China curbs gallium" in livesearch.render(ITEMS[:1], "weird")
