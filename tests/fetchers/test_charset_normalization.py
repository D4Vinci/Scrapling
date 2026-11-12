"""Charset labels that Python accepts but libxml2/iconv rejects.

Servers keep sending Python spellings such as ``charset=euc_kr`` (underscore)
or ``shift_jis``. ``codecs`` resolves them, but the label is handed straight to
``lxml.html.HTMLParser(encoding=...)``, which only knows the IANA spelling, so
building the ``Response`` dies with ``LookupError: unknown encoding``.
"""

from typing import Optional
from unittest.mock import Mock

import pytest

from scrapling.engines.toolbelt.convertor import ResponseFactory

KOREAN_HTML = "<html><body><p>안녕하세요</p></body></html>"


def make_curl_response(*, body: bytes, charset: Optional[str], encoding: Optional[str] = None) -> Mock:
    response = Mock()
    response.url = "https://example.com/kr"
    response.content = body
    response.status_code = 200
    response.reason = "OK"
    response.encoding = charset if encoding is None else encoding
    response.cookies = {}
    response.headers = {"content-type": f"text/html; charset={charset}" if charset else "text/html"}
    response.request.headers = {"User-Agent": "Test"}
    response.request.method = "GET"
    response.history = []
    return response


def test_curl_response_with_python_only_charset_label_is_parsed():
    """A ``euc_kr`` label must not abort response construction."""
    curl_response = make_curl_response(body=KOREAN_HTML.encode("euc_kr"), charset="euc_kr")

    response = ResponseFactory.from_http_request(curl_response, {"adaptive": False})

    assert response.encoding == "euc-kr"
    assert "안녕하세요" in response.html_content


def test_curl_response_with_undecodable_charset_label_still_raises():
    """A label Python cannot resolve keeps surfacing `LookupError`, as before."""
    curl_response = make_curl_response(
        body="<html><body><p>plain</p></body></html>".encode(),
        charset="x-not-a-real-codec",
    )

    with pytest.raises(LookupError):
        ResponseFactory.from_http_request(curl_response, {"adaptive": False})


@pytest.mark.parametrize(
    "content_type,expected",
    [
        ("text/html; charset=euc_kr", "euc-kr"),
        ("text/html; charset=shift_jis", "shift-jis"),
        ("text/html; charset=UTF-8", "UTF-8"),
        ('text/html; CHARSET = "iso-8859-15"', "iso-8859-15"),
        ("text/html", "utf-8"),
    ],
)
def test_header_charset_keeps_supported_spellings_and_normalizes_python_ones(content_type, expected):
    """Only labels libxml2 cannot resolve get rewritten."""
    assert ResponseFactory._extract_encoding(content_type) == expected
