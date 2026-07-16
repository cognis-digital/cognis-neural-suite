"""Tests for the search backends: web_search, ddg_search, and _get retry."""

from __future__ import annotations

import pytest
from conftest import DDG_SAMPLE, RSS_SAMPLE

import livesearch


class TestWebSearch:
    def test_stamps_query_on_items(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        items = livesearch.web_search("rare earth", when="7d")
        assert items
        assert all(it["query"] == "rare earth" for it in items)
        assert all(it["source"] == "google-news" for it in items)

    def test_hits_google_news_endpoint(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        livesearch.web_search("btc halving")
        assert any("news.google.com" in u for u in fake_get.calls)

    def test_limit_forwarded(self, fake_get):
        fake_get.set(RSS_SAMPLE)
        assert len(livesearch.web_search("x", limit=2)) == 2


class TestDdgSearch:
    def test_extracts_redirect_target(self, fake_get):
        fake_get.set(DDG_SAMPLE)
        items = livesearch.ddg_search("anything")
        assert items[0]["link"] == "https://real.example/page"
        assert items[0]["title"] == "Real Result Title"  # inner tags stripped
        assert items[0]["source"] == "duckduckgo"
        assert items[0]["query"] == "anything"

    def test_direct_href_when_no_uddg(self, fake_get):
        fake_get.set(DDG_SAMPLE)
        items = livesearch.ddg_search("anything")
        assert items[1]["link"] == "https://direct.example/no-redirect"

    def test_limit(self, fake_get):
        fake_get.set(DDG_SAMPLE)
        assert len(livesearch.ddg_search("q", limit=1)) == 1

    def test_network_error_returns_empty(self, fake_get):
        fake_get.set(OSError("down"))
        assert livesearch.ddg_search("q") == []


class TestGetRetry:
    def test_succeeds_first_try_no_sleep(self, monkeypatch):
        calls = {"n": 0}

        def fake_urlopen(req, timeout=None):
            calls["n"] += 1

            class R:
                def __enter__(self_):
                    return self_

                def __exit__(self_, *a):
                    return False

                def read(self_):
                    return b"ok"

            return R()

        slept = []
        monkeypatch.setattr(livesearch.urllib.request, "urlopen", fake_urlopen)
        monkeypatch.setattr(livesearch.time, "sleep", lambda s: slept.append(s))
        assert livesearch._get("https://x") == b"ok"
        assert calls["n"] == 1
        assert slept == []

    def test_retries_then_succeeds(self, monkeypatch):
        calls = {"n": 0}

        def flaky_urlopen(req, timeout=None):
            calls["n"] += 1
            if calls["n"] < 3:
                raise OSError("transient")

            class R:
                def __enter__(self_):
                    return self_

                def __exit__(self_, *a):
                    return False

                def read(self_):
                    return b"finally"

            return R()

        slept = []
        monkeypatch.setattr(livesearch.urllib.request, "urlopen", flaky_urlopen)
        monkeypatch.setattr(livesearch.time, "sleep", lambda s: slept.append(s))
        assert livesearch._get("https://x", retries=2, backoff=0.1) == b"finally"
        assert calls["n"] == 3
        assert slept == [0.1, 0.2]  # exponential backoff

    def test_reraises_after_exhausting_retries(self, monkeypatch):
        def always_fail(req, timeout=None):
            raise OSError("nope")

        monkeypatch.setattr(livesearch.urllib.request, "urlopen", always_fail)
        monkeypatch.setattr(livesearch.time, "sleep", lambda s: None)
        with pytest.raises(OSError):
            livesearch._get("https://x", retries=1)
