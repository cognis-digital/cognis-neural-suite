"""Shared fixtures and canned network payloads for the livesearch test suite.

No test in this suite touches the real network: every test that would trigger
an HTTP request monkeypatches ``livesearch._get`` to return canned bytes, so the
suite is fully offline, deterministic, and safe to run in CI.
"""

from __future__ import annotations

import pytest

RSS_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>Example News</title>
  <item>
    <title>Rare earth export curbs tighten &amp; ripple</title>
    <link>https://example.com/a</link>
    <pubDate>Wed, 15 Jul 2026 12:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Second story</title>
    <link>https://example.com/b</link>
    <pubDate>Tue, 14 Jul 2026 09:30:00 +0000</pubDate>
  </item>
  <item>
    <title>Ancient archived story</title>
    <link>https://example.com/old</link>
    <pubDate>Mon, 01 Jan 2001 00:00:00 GMT</pubDate>
  </item>
</channel></rss>
"""

ATOM_SAMPLE = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Source</title>
  <entry>
    <title>Atom entry one</title>
    <link href="https://atom.example/1"/>
    <updated>2026-07-13T08:00:00Z</updated>
  </entry>
  <entry>
    <title>Atom entry two</title>
    <link href="https://atom.example/2"/>
    <published>2026-07-12T08:00:00+02:00</published>
  </entry>
</feed>
"""

DDG_SAMPLE = (
    b'<html><body>'
    b'<a rel="nofollow" class="result__a" '
    b'href="/l/?uddg=https%3A%2F%2Freal.example%2Fpage&rut=x">'
    b'Real <b>Result</b> Title</a>'
    b'<a rel="nofollow" class="result__a" '
    b'href="https://direct.example/no-redirect">Direct Title</a>'
    b'</body></html>'
)

MALFORMED_XML = b"<rss><channel><item><title>oops"


@pytest.fixture
def fake_get(monkeypatch):
    """Install a fake ``_get`` and return a controller to script responses.

    Usage::

        def test_x(fake_get):
            fake_get.set(RSS_SAMPLE)          # every fetch returns this
            ...
        def test_y(fake_get):
            fake_get.route({url: payload})    # per-URL responses
    """
    import livesearch

    class Controller:
        def __init__(self):
            self.payload = b""
            self.routes = {}
            self.calls = []

        def set(self, payload: bytes):
            self.payload = payload

        def route(self, mapping: dict):
            self.routes = mapping

        def _get(self, url, *args, **kwargs):
            self.calls.append(url)
            for key, val in self.routes.items():
                if key in url:
                    if isinstance(val, Exception):
                        raise val
                    return val
            if isinstance(self.payload, Exception):
                raise self.payload
            return self.payload

    ctrl = Controller()
    monkeypatch.setattr(livesearch, "_get", ctrl._get)
    return ctrl
