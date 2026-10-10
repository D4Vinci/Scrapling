"""Tests for _merge_request_args to ensure browser-only kwargs are excluded.

Regression tests for https://github.com/D4Vinci/Scrapling/issues/247
"""

import pytest

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


class TestMergeRequestArgsEncodesDataAndParams:
    """Verify that dict `data` and `params` reach curl_cffi in the form the
    `requests` convention expects: lists become repeated keys and None values
    are dropped."""

    def _build_args(self, **extra_kwargs):
        client = FetcherClient()
        return client._merge_request_args(url="https://example.com", **extra_kwargs)

    def test_data_list_becomes_repeated_keys(self):
        args = self._build_args(data={"tags": ["a", "b"]})
        assert args["data"] == "tags=a&tags=b"

    def test_data_int_list_becomes_repeated_keys(self):
        args = self._build_args(data={"ids": [1, 2]})
        assert args["data"] == "ids=1&ids=2"

    def test_data_tuple_and_set_values_are_expanded(self):
        args = self._build_args(data={"t": ("a", "b"), "s": {"x"}})
        assert args["data"] == "t=a&t=b&s=x"

    def test_data_none_value_is_dropped(self):
        args = self._build_args(data={"opt": None, "q": "x"})
        assert args["data"] == "q=x"

    def test_data_scalars_are_unchanged(self):
        args = self._build_args(data={"a": "1", "b": 2, "c": "x y"})
        assert args["data"] == "a=1&b=2&c=x+y"

    def test_data_dict_keeps_form_content_type(self):
        args = self._build_args(data={"tags": ["a", "b"]})
        assert args["headers"]["Content-Type"] == "application/x-www-form-urlencoded"

    def test_data_dict_keeps_caller_content_type(self):
        args = self._build_args(data={"a": "1"}, headers={"content-type": "text/plain"})
        assert args["headers"]["content-type"] == "text/plain"
        assert "Content-Type" not in args["headers"]

    def test_params_none_value_is_dropped(self):
        args = self._build_args(params={"page": None, "q": "x"})
        assert args["params"] == {"q": "x"}

    def test_params_list_is_unchanged(self):
        args = self._build_args(params={"tag": ["a", "b"]})
        assert args["params"] == {"tag": ["a", "b"]}

    def test_non_dict_data_is_untouched(self):
        pairs = [("tags", ["a", "b"]), ("opt", None)]
        assert self._build_args(data="a=1&b=2")["data"] == "a=1&b=2"
        assert self._build_args(data=b"raw")["data"] == b"raw"
        assert self._build_args(data=pairs)["data"] is pairs
        assert "Content-Type" not in self._build_args(data="a=1")["headers"]

    def test_non_dict_params_is_untouched(self):
        pairs = [("page", None), ("q", "x")]
        assert self._build_args(params=pairs)["params"] is pairs

    def test_dict_data_with_multipart_stays_a_dict(self):
        """curl_cffi adds the items of a dict `data` to a `multipart` body, so it must not become a string."""
        mime = object()
        args = self._build_args(data={"a": "1"}, multipart=mime)
        assert args["data"] == {"a": "1"}
        assert args["multipart"] is mime
        assert "Content-Type" not in args["headers"]
