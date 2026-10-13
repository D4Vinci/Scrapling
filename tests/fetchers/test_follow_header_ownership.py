from types import MappingProxyType

import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders import Request


def response():
    result = Response("https://example.test/source", "<p>source</p>", 200, "OK", {}, {}, {})
    result.request = Request(result.url)
    return result


@pytest.mark.parametrize("key", ["headers", "extra_headers"])
def test_follow_does_not_mutate_explicit_header_dictionary(key):
    original = {"X-Shared": "caller", "referer": "https://previous.test/"}
    copied = dict(original)
    followed = response().follow("/next", **{key: original})
    assert original == copied
    assert followed._session_kwargs[key]["referer"] == "https://example.test/source"
    followed._session_kwargs[key]["X-Shared"] = "child"
    assert original == copied


@pytest.mark.parametrize("key", ["headers", "extra_headers"])
@pytest.mark.parametrize("headers", [None, MappingProxyType({"X-Shared": "caller"})])
def test_follow_copies_optional_and_read_only_headers(key, headers):
    followed = response().follow("/next", **{key: headers})
    assert followed._session_kwargs[key]["referer"] == "https://example.test/source"


def test_follow_without_referer_keeps_explicit_headers_unchanged():
    headers = {"referer": "https://caller.test/"}
    followed = response().follow("/next", referer_flow=False, headers=headers)
    assert followed._session_kwargs["headers"] == headers
    assert headers == {"referer": "https://caller.test/"}
