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


STYLED_BUT_VISIBLE_HTML = """
<html>
  <body>
    <div style="line-height:0.9"><h2>Compact heading</h2><p>Body of the first section.</p></div>
    <p style="opacity:0.95">Almost opaque note.</p>
    <p style="font-size:0.9rem">Slightly smaller note.</p>
    <p style="width:0.5em">Narrow but visible.</p>
    <p style="min-height:0">Flexbox child.</p>
  </body>
</html>
"""

HIDDEN_HTML = """
<html>
  <body>
    <p>Visible content.</p>
    <p style="display:none">Hidden by display</p>
    <p style="display: none">Hidden by spaced display</p>
    <p style="visibility:hidden">Hidden by visibility</p>
    <p style="opacity:0">Hidden by opacity</p>
    <p style="opacity: 0">Hidden by spaced opacity</p>
    <p style="height:0px">Hidden by height</p>
    <p style="max-height:0">Hidden by max height</p>
    <p style="width:0">Hidden by width</p>
    <p style="font-size:0">Hidden by font size</p>
    <p style="display:none !important">Hidden by important</p>
    <p aria-hidden="true">Hidden by aria</p>
    <template><p>Hidden by template</p></template>
  </body>
</html>
"""


def _response_with(content: str) -> Response:
    return Response(
        url="https://example.com/",
        content=content,
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )


class TestResponseMarkdownSanitizerPrecision:
    def test_partial_zero_values_are_not_treated_as_hidden(self):
        """A style value that merely starts with a zero does not hide the element"""
        md = _response_with(STYLED_BUT_VISIBLE_HTML).markdown()
        for expected in (
            "Compact heading",
            "Body of the first section.",
            "Almost opaque note.",
            "Slightly smaller note.",
            "Narrow but visible.",
            "Flexbox child.",
        ):
            assert expected in md

    def test_truly_hidden_content_is_still_removed(self):
        md = _response_with(HIDDEN_HTML).markdown()
        assert "Visible content." in md
        for hidden in (
            "Hidden by display",
            "Hidden by spaced display",
            "Hidden by visibility",
            "Hidden by opacity",
            "Hidden by spaced opacity",
            "Hidden by height",
            "Hidden by max height",
            "Hidden by width",
            "Hidden by font size",
            "Hidden by important",
            "Hidden by aria",
            "Hidden by template",
        ):
            assert hidden not in md
