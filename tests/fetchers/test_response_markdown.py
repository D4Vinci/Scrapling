"""Tests for the public `Response.markdown()` method."""

import sys

import pytest

from scrapling.engines.toolbelt.custom import Response

HTML = """
<html>
  <head><title>Docs Home</title><style>.hint { color: red; }</style></head>
  <body>
    <h1>Title</h1>
    <p>Visible content.</p>
    <p style="display:none">hidden instructions</p>
    <script>console.log("noise")</script>
    <div class="a">First</div>
    <div class="a">Second</div>
  </body>
</html>
"""


def _make_response(url: str = "https://example.com/") -> Response:
    return Response(
        url=url,
        content=HTML,
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )


class TestResponseMarkdown:
    def test_returns_plain_string_with_markdown(self):
        md = _make_response().markdown()
        assert type(md) is str
        assert "Title\n=====" in md
        assert "Visible content." in md
        assert "Docs Home" in md

    def test_sanitization_is_always_applied(self):
        """Scripts, styles, and hidden elements are stripped even without main_content_only"""
        md = _make_response().markdown()
        assert "hidden instructions" not in md
        assert "console.log" not in md
        assert ".hint" not in md

    def test_main_content_only_scopes_to_body(self):
        md = _make_response().markdown(main_content_only=True)
        assert "Docs Home" not in md
        assert "Visible content." in md

    def test_css_selector_concatenates_all_matches(self):
        md = _make_response().markdown(css_selector=".a")
        assert "First" in md
        assert "Second" in md
        assert "Visible content." not in md

    def test_missing_markdownify_raises_friendly_error(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "markdownify", None)
        with pytest.raises(ModuleNotFoundError, match=r"scrapling\[rag\]"):
            _make_response().markdown()
