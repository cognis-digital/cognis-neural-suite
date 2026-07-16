"""End-to-end tests for the _cli entry point (argument wiring, formats, filters)."""

from __future__ import annotations

import json

import pytest
from conftest import DDG_SAMPLE, RSS_SAMPLE

import livesearch


class TestCliSearch:
    def test_query_plain_output(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        rc = livesearch._cli(["rare earth"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Rare earth export curbs tighten & ripple" in out
        assert "https://example.com/a" in out

    def test_json_flag(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["rare earth", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert data[0]["query"] == "rare earth"

    def test_format_json_equivalent_to_json_flag(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["rare earth", "--format", "json"])
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 3

    def test_format_csv(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["x", "--format", "csv"])
        out = capsys.readouterr().out
        assert out.splitlines()[0] == ",".join(livesearch.FIELDS)

    def test_format_ndjson(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["x", "--format", "ndjson"])
        lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
        assert all(json.loads(ln) for ln in lines)


class TestCliFeedAndDdg:
    def test_feed_mode(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["--feed", "https://x/feed", "--json"])
        assert any("news.google.com" not in u for u in fake_get.calls)
        data = json.loads(capsys.readouterr().out)
        assert data[0]["link"] == "https://example.com/a"

    def test_ddg_mode(self, fake_get, capsys):
        fake_get.set(DDG_SAMPLE)
        livesearch._cli(["something", "--ddg", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert data[0]["source"] == "duckduckgo"


class TestCliFilters:
    def test_match_filter(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["x", "--match", "second", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 1
        assert data[0]["title"] == "Second story"

    def test_source_filter(self, fake_get, capsys):
        fake_get.set(RSS_SAMPLE)
        livesearch._cli(["x", "--source", "google-news", "--json"])
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 3

    def test_invalid_regex_exits_2(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        with pytest.raises(SystemExit) as ei:
            livesearch._cli(["x", "--match", "(unclosed"])
        assert ei.value.code == 2


class TestCliHarvest:
    def test_harvest_file(self, fake_get, capsys, tmp_path, monkeypatch):
        captured = {}

        def fake_harvest(sources, since_days=14, per_source=30, min_year=2026):
            captured["sources"] = sources
            captured["since_days"] = since_days
            return [{"title": "H", "link": "https://h/1", "published": "",
                     "source": "s", "query": ""}]

        monkeypatch.setattr(livesearch, "harvest", fake_harvest)
        p = tmp_path / "s.txt"
        p.write_text("https://feed.example/rss\nq: gold\n", encoding="utf-8")
        rc = livesearch._cli(["--harvest", str(p), "--since-days", "7", "--json"])
        assert rc == 0
        assert captured["since_days"] == 7
        assert captured["sources"] == ["https://feed.example/rss", {"query": "gold"}]
        data = json.loads(capsys.readouterr().out)
        assert data[0]["link"] == "https://h/1"


class TestCliErrors:
    def test_no_args_errors(self, capsys):
        with pytest.raises(SystemExit) as ei:
            livesearch._cli([])
        assert ei.value.code == 2

    def test_entry_raises_systemexit(self, monkeypatch):
        monkeypatch.setattr(livesearch.sys, "argv", ["livesearch"])
        with pytest.raises(SystemExit):
            livesearch._entry()
