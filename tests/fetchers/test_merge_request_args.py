"""Tests for _merge_request_args to ensure browser-only kwargs are excluded.

Regression tests for https://github.com/D4Vinci/Scrapling/issues/247
"""

import pytest

from scrapling.engines.static import FetcherClient


class TestHeadersMergeIsCaseInsensitive:
    """A per-request header replaces a session header whose name only differs by case."""

    URL = "https://example.com"

    def _merge(self, session_headers, request_headers, **extra):
        client = FetcherClient(headers=session_headers, **extra)
        return client._headers_job(self.URL, request_headers, False, True)

    def test_lowercase_request_header_replaces_session_header(self):
        headers = self._merge(
            {"User-Agent": "SessionUA/1.0", "Authorization": "Bearer SESSION"},
            {"user-agent": "RequestUA/2.0", "authorization": "Bearer REQUEST"},
        )
        assert headers == {"user-agent": "RequestUA/2.0", "authorization": "Bearer REQUEST"}

    def test_uppercase_request_header_replaces_lowercase_session_header(self):
        headers = self._merge({"x-token": "session"}, {"X-Token": "request"})
        assert headers == {"X-Token": "request"}

    def test_same_case_override_still_works(self):
        headers = self._merge({"User-Agent": "SessionUA/1.0"}, {"User-Agent": "RequestUA/2.0"})
        assert headers == {"User-Agent": "RequestUA/2.0"}

    def test_session_headers_not_overridden_are_kept_in_order(self):
        headers = self._merge(
            {"Accept": "text/html", "User-Agent": "SessionUA/1.0", "X-Trace": "1"},
            {"user-agent": "RequestUA/2.0", "X-New": "2"},
        )
        assert list(headers.items()) == [
            ("Accept", "text/html"),
            ("X-Trace", "1"),
            ("user-agent", "RequestUA/2.0"),
            ("X-New", "2"),
        ]

    def test_mixed_case_duplicates_inside_request_are_left_alone(self):
        headers = self._merge({}, {"X-Dup": "a", "x-dup": "b"})
        assert headers == {"X-Dup": "a", "x-dup": "b"}

    def test_stealth_does_not_overwrite_user_header_of_any_case(self):
        client = FetcherClient(headers={"Accept-Language": "fr"})
        headers = client._headers_job(
            self.URL, {"user-agent": "RequestUA/2.0", "REFERER": "https://a.example/"}, True, False
        )
        names = [k.lower() for k in headers]
        assert names.count("user-agent") == 1
        assert names.count("accept-language") == 1
        assert names.count("referer") == 1
        assert headers["user-agent"] == "RequestUA/2.0"
        assert headers["Accept-Language"] == "fr"
        assert headers["REFERER"] == "https://a.example/"


class TestMergeRequestArgsSkipsBrowserParams:
    """Verify that browser-only keyword arguments are stripped before
    the request dict is forwarded to curl_cffi's Session.request()."""

    def _build_args(self, **extra_kwargs):
        """Helper: instantiate a FetcherClient and call _merge_request_args."""
        client = FetcherClient()
        return client._merge_request_args(url="https://example.com", **extra_kwargs)

    def test_block_ads_excluded(self):
        """block_ads is a browser-engine param and must not leak into the
        HTTP request dict (fixes #247)."""
        args = self._build_args(block_ads=True)
        assert "block_ads" not in args

    def test_google_search_excluded(self):
        """google_search is a browser-engine param and should be stripped."""
        args = self._build_args(google_search=True)
        assert "google_search" not in args

    def test_extra_headers_excluded(self):
        """extra_headers is a browser-engine param and should be stripped."""
        args = self._build_args(extra_headers={"X-Custom": "val"})
        assert "extra_headers" not in args

    def test_url_present(self):
        """The url must always be present in the output dict."""
        args = self._build_args()
        assert args["url"] == "https://example.com"

    def test_valid_kwargs_passed_through(self):
        """Arbitrary curl_cffi-compatible kwargs should survive."""
        args = self._build_args(cookies={"session": "abc"})
        assert args.get("cookies") == {"session": "abc"}
