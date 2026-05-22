"""Map Scrapy's ``Response`` to Scrapling's unified :class:`~scrapling.engines.toolbelt.custom.Response`."""

from __future__ import annotations

from copy import copy
from http.client import responses as http_responses
from typing import Any

from scrapling.core._types import Dict
from scrapling.engines.toolbelt.custom import Response

try:
    from scrapy.http import Response as ScrapyResponse
except ImportError as exc:  # pragma: no cover - optional dependency
    raise ImportError('Scrapy is required for this module. Install with: pip install "scrapling[scrapy]"') from exc


def _scrapy_headers_to_str_dict(headers: Any) -> Dict[str, str]:
    """Normalize Scrapy :class:`~scrapy.http.headers.Headers` to ``dict[str, str]``."""
    if headers is None:
        return {}
    if hasattr(headers, "to_unicode_dict"):
        return dict(headers.to_unicode_dict())
    return {}


def _http_reason(status: int, response: ScrapyResponse) -> str:
    phrase = getattr(response, "phrase", None)
    if isinstance(phrase, str) and phrase:
        return phrase
    return http_responses.get(status, "") or ""


def scrapling_response_from_scrapy(response: ScrapyResponse, **selector_kwargs: Any) -> Response:
    """Build a Scrapling :class:`~scrapling.engines.toolbelt.custom.Response` from a Scrapy response.

    Scrapy's built-in ``response.css`` / ``response.xpath`` (parsel) are unchanged. Use the returned
    object for Scrapling selection (including adaptive parsing) alongside Scrapy.

    :param response: Any Scrapy :class:`~scrapy.http.Response` (typically :class:`~scrapy.http.TextResponse`).
    :param selector_kwargs: Forwarded to :class:`~scrapling.parser.Selector` (e.g. ``adaptive=True``,
        ``storage_args={...}``, ``keep_comments``, ``adaptive_domain``).
    :return: A Scrapling ``Response`` (``Selector`` subclass) with HTTP metadata populated from Scrapy.

    .. note::

        This parses the body again with lxml as Scrapling's tree. Scrapy may already have a parsel
        tree in memory, so very large HTML means extra CPU and RAM unless you avoid parsel on that page.
    """
    url = response.url
    body: bytes = response.body or b""
    encoding: str = getattr(response, "encoding", None) or "utf-8"
    status = int(response.status)

    resp_headers = _scrapy_headers_to_str_dict(response.headers)

    req = getattr(response, "request", None)
    request_headers = _scrapy_headers_to_str_dict(req.headers) if req is not None else {}
    method = getattr(req, "method", "GET") if req is not None else "GET"

    cookies: Dict[str, str] | tuple[Dict[str, str], ...] = {}

    meta_src = getattr(response, "meta", None)
    meta_copy = copy(meta_src) if isinstance(meta_src, dict) else {}

    return Response(
        url=url,
        content=body,
        status=status,
        reason=_http_reason(status, response),
        cookies=cookies,
        headers=resp_headers,
        request_headers=request_headers,
        encoding=encoding,
        method=method,
        history=[],
        meta=meta_copy,
        **selector_kwargs,
    )
