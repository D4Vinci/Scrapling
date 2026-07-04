"""Tests for `LinkExtractor`."""

import re

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.links import IGNORED_EXTENSIONS, LinkExtractor


def _make_response(html: str, url: str = "https://example.com/page") -> Response:
    """Build a minimal Response wrapping the given HTML."""
    return Response(
        url=url,
        content=html,
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )


HTML_BASIC = """
<html><body>
  <a href="/posts/1">post 1</a>
  <a href="/posts/2">post 2</a>
  <a href="https://other.com/page">external</a>
  <a href="/about">about</a>
  <a href="mailto:x@example.com">mail</a>
  <a href="javascript:alert(1)">js</a>
  <a href="/file.pdf">pdf</a>
  <area href="/area-link">area</area>
  <link rel="stylesheet" href="/style.css">
</body></html>
"""


class TestExtractBasic:
    def test_default_extracts_a_and_area_with_href(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor().extract(resp)
        # mailto/javascript filtered (non-http scheme), .pdf filtered (deny_extensions)
        # link[rel=stylesheet] not in default tags
        assert "https://example.com/posts/1" in urls
        assert "https://example.com/posts/2" in urls
        assert "https://example.com/about" in urls
        assert "https://example.com/area-link" in urls
        assert "https://other.com/page" in urls
        assert all(not u.startswith("mailto:") for u in urls)
        assert all(not u.startswith("javascript:") for u in urls)
        assert not any(u.endswith(".pdf") for u in urls)
        assert not any(u.endswith(".css") for u in urls)

    def test_relative_urls_become_absolute_via_urljoin(self):
        resp = _make_response('<a href="foo/bar">x</a>', url="https://example.com/sub/")
        assert LinkExtractor().extract(resp) == ["https://example.com/sub/foo/bar"]

    def test_empty_allow_means_match_all(self):
        resp = _make_response('<a href="/anything">x</a><a href="/else">y</a>')
        out = LinkExtractor().extract(resp)
        assert len(out) == 2


class TestAllowDeny:
    def test_allow_regex_filters_in(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor(allow=r"/posts/").extract(resp)
        assert urls == ["https://example.com/posts/1", "https://example.com/posts/2"]

    def test_deny_regex_filters_out(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor(deny=r"/posts/").extract(resp)
        assert "https://example.com/posts/1" not in urls
        assert "https://example.com/about" in urls

    def test_deny_overrides_allow(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor(allow=r"/posts/", deny=r"/posts/2").extract(resp)
        assert urls == ["https://example.com/posts/1"]

    def test_compiled_pattern_accepted(self):
        resp = _make_response(HTML_BASIC)
        pat = re.compile(r"/posts/\d+$")
        urls = LinkExtractor(allow=pat).extract(resp)
        assert len(urls) == 2

    def test_iterable_of_patterns(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor(allow=[r"/posts/", r"/about"]).extract(resp)
        assert "https://example.com/posts/1" in urls
        assert "https://example.com/about" in urls


class TestDomains:
    def test_allow_domains_keeps_only_matching(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor(allow_domains="example.com").extract(resp)
        assert all("example.com" in u for u in urls)
        assert "https://other.com/page" not in urls

    def test_allow_domains_matches_subdomains(self):
        html = '<a href="https://api.example.com/x">a</a><a href="https://other.com/y">b</a>'
        resp = _make_response(html)
        urls = LinkExtractor(allow_domains="example.com").extract(resp)
        assert urls == ["https://api.example.com/x"]

    def test_deny_domains_filters_out(self):
        resp = _make_response(HTML_BASIC)
        urls = LinkExtractor(deny_domains="other.com").extract(resp)
        assert "https://other.com/page" not in urls
        assert "https://example.com/posts/1" in urls


class TestRestrict:
    def test_restrict_css_scopes_extraction(self):
        html = """
        <html><body>
            <nav><a href="/nav-link">n</a></nav>
            <main><a href="/main-link">m</a></main>
        </body></html>
        """
        resp = _make_response(html)
        urls = LinkExtractor(restrict_css="main").extract(resp)
        assert urls == ["https://example.com/main-link"]

    def test_restrict_xpath_scopes_extraction(self):
        html = """
        <html><body>
            <div id="header"><a href="/h">h</a></div>
            <div id="content"><a href="/c">c</a></div>
        </body></html>
        """
        resp = _make_response(html)
        urls = LinkExtractor(restrict_xpath='//div[@id="content"]').extract(resp)
        assert urls == ["https://example.com/c"]


class TestTagsAttrs:
    def test_custom_tags_and_attrs_for_stylesheets(self):
        html = '<link rel="stylesheet" href="/style.css"><a href="/page">p</a>'
        resp = _make_response(html)
        # Override deny_extensions to allow .css through, and pick up <link href>
        urls = LinkExtractor(tags=("link",), attrs=("href",), deny_extensions=()).extract(resp)
        assert urls == ["https://example.com/style.css"]


class TestCanonicalization:
    def test_query_params_sorted(self):
        resp = _make_response('<a href="/x?b=2&a=1">x</a>')
        urls = LinkExtractor().extract(resp)
        assert urls == ["https://example.com/x?a=1&b=2"]

    def test_fragment_dropped_by_default(self):
        resp = _make_response('<a href="/x#section">x</a>')
        urls = LinkExtractor().extract(resp)
        assert urls == ["https://example.com/x"]

    def test_keep_fragment_preserves_it(self):
        resp = _make_response('<a href="/x#section">x</a>')
        urls = LinkExtractor(keep_fragment=True).extract(resp)
        assert urls == ["https://example.com/x#section"]

    def test_canonicalize_off_leaves_url_unchanged(self):
        resp = _make_response('<a href="/x?b=2&a=1#f">x</a>')
        urls = LinkExtractor(canonicalize=False).extract(resp)
        assert urls == ["https://example.com/x?b=2&a=1#f"]


class TestDedup:
    def test_unique_drops_duplicates(self):
        html = '<a href="/x">a</a><a href="/x">b</a><a href="/x?">c</a>'
        resp = _make_response(html)
        urls = LinkExtractor().extract(resp)
        # canonicalize collapses /x and /x? together
        assert urls == ["https://example.com/x"]


class TestExtensions:
    def test_default_deny_extensions_drops_pdf_zip_images(self):
        html = '<a href="/a.pdf">pdf</a><a href="/b.zip">zip</a><a href="/c.png">png</a><a href="/d">ok</a>'
        resp = _make_response(html)
        urls = LinkExtractor().extract(resp)
        assert urls == ["https://example.com/d"]

    def test_default_deny_extensions_drops_compound_archive(self):
        html = '<a href="/dataset.tar.gz">archive</a><a href="/d">ok</a>'
        resp = _make_response(html)
        urls = LinkExtractor().extract(resp)
        assert urls == ["https://example.com/d"]

    def test_custom_deny_extensions_overrides_default(self):
        html = '<a href="/a.pdf">pdf</a><a href="/b.zip">zip</a>'
        resp = _make_response(html)
        urls = LinkExtractor(deny_extensions={"zip"}).extract(resp)
        # .pdf now allowed because we replaced the set
        assert urls == ["https://example.com/a.pdf"]

    def test_custom_deny_extensions_honors_compound_extension(self):
        ex = LinkExtractor(deny_extensions={"tar.gz"})
        assert ex.matches("https://example.com/dataset.tar.gz") is False
        assert ex.matches("https://example.com/dataset.gz") is True

    def test_empty_deny_extensions_allows_everything(self):
        html = '<a href="/a.pdf">pdf</a>'
        resp = _make_response(html)
        urls = LinkExtractor(deny_extensions=()).extract(resp)
        assert urls == ["https://example.com/a.pdf"]


class TestStrip:
    def test_strip_removes_whitespace(self):
        resp = _make_response('<a href="  /spaced  ">x</a>')
        urls = LinkExtractor().extract(resp)
        assert urls == ["https://example.com/spaced"]


class TestMatches:
    def test_matches_honors_allow(self):
        ex = LinkExtractor(allow=r"/posts/")
        assert ex.matches("https://example.com/posts/1") is True
        assert ex.matches("https://example.com/about") is False

    def test_matches_honors_deny(self):
        ex = LinkExtractor(deny=r"/admin")
        assert ex.matches("https://example.com/admin/x") is False
        assert ex.matches("https://example.com/posts/1") is True

    def test_matches_honors_allow_domains(self):
        ex = LinkExtractor(allow_domains="example.com")
        assert ex.matches("https://api.example.com/x") is True
        assert ex.matches("https://other.com/x") is False

    def test_matches_honors_deny_extensions(self):
        ex = LinkExtractor()
        assert ex.matches("https://example.com/file.pdf") is False
        assert ex.matches("https://example.com/page") is True

    def test_matches_rejects_non_http_schemes(self):
        ex = LinkExtractor()
        assert ex.matches("mailto:x@example.com") is False
        assert ex.matches("javascript:void(0)") is False
        assert ex.matches("ftp://example.com/x") is False

    def test_matches_canonicalizes_before_checking(self):
        ex = LinkExtractor(allow=r"a=1&b=2$")
        # the URL has params in the wrong order; canonicalize sorts them
        assert ex.matches("https://example.com/x?b=2&a=1") is True


class TestIgnoredExtensions:
    def test_constant_includes_common_binary_types(self):
        for ext in ("pdf", "zip", "png", "mp4", "exe"):
            assert ext in IGNORED_EXTENSIONS
