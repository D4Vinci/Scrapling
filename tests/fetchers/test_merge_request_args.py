"""Tests for _merge_request_args to ensure browser-only kwargs are excluded.

Regression tests for https://github.com/D4Vinci/Scrapling/issues/247
and https://github.com/D4Vinci/Scrapling/issues/336
"""

import pytest

from curl_cffi import CurlFollow

from scrapling.engines.static import FetcherClient


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


class TestMergeRequestArgsResolvesFollowRedirects:
    """Verify that Scrapling's string ``follow_redirects`` modes are resolved
    to a value ``curl_cffi`` accepts before being forwarded as
    ``allow_redirects`` (fixes #336).

    ``curl_cffi`` consumes ``allow_redirects`` via ``int(allow_redirects)``
    for anything that is not a ``CurlFollow`` member (only the literal
    ``"safe"`` is special-cased). Forwarding a raw string such as ``"all"``
    therefore raises ``ValueError: invalid literal for int()``, which broke
    every ``Fetcher.get()`` call when ``follow_redirects`` defaulted to the
    string ``"safe"``.
    """

    def _build_args(self, **extra_kwargs):
        """Helper: instantiate a FetcherClient and call _merge_request_args."""
        client = FetcherClient()
        return client._merge_request_args(url="https://example.com", **extra_kwargs)

    def test_default_follow_redirects_resolved(self):
        """The default (``"safe"``) must not leak through as a raw string."""
        args = self._build_args()
        allow_redirects = args["allow_redirects"]
        assert not isinstance(allow_redirects, str)
        # Whatever it resolves to must be int()-able the way curl_cffi expects.
        int(allow_redirects)

    @pytest.mark.parametrize("mode", ["safe", "all", "obeycode", "firstonly"])
    def test_string_modes_resolved_to_curlfollow(self, mode):
        """Every FollowRedirects literal must map to a curl_cffi-acceptable
        value (a CurlFollow member or a bool), never a raw string."""
        args = self._build_args(follow_redirects=mode)
        allow_redirects = args["allow_redirects"]
        assert isinstance(allow_redirects, (CurlFollow, bool))
        # curl_cffi does int(allow_redirects); confirm this does not raise.
        int(allow_redirects)

    @pytest.mark.parametrize("value", [True, False])
    def test_bool_modes_passed_through(self, value):
        """Explicit boolean values are already curl_cffi-acceptable and must
        be preserved as-is."""
        args = self._build_args(follow_redirects=value)
        assert args["allow_redirects"] is value
