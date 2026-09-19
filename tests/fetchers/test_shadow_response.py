from unittest.mock import AsyncMock, Mock

import pytest

from scrapling.core._types import Any
from scrapling.engines.toolbelt.convertor import ResponseFactory


def _response(async_mode: bool, content_type: str) -> Any:
    method = AsyncMock if async_mode else Mock
    response = Mock(url="https://example.com", status=200, status_text="OK")
    response.headers = {"content-type": content_type}
    response.all_headers = method(return_value=response.headers)
    response.body = method(return_value=b"B\xfcrger")
    response.request.all_headers = method(return_value={})
    response.request.redirected_from = None
    return response


def _page(async_mode: bool) -> Any:
    method = AsyncMock if async_mode else Mock
    page = Mock(url="https://example.com")
    page.content = method(return_value="<html><body>Bürger</body></html>")
    page.evaluate = method(return_value=None)
    page.context.cookies = method(return_value=[])
    return page


@pytest.mark.parametrize("error", [None, RuntimeError("Shadow extraction failed")])
def test_shadow_falls_back_to_page_content(error: Exception | None, caplog: pytest.LogCaptureFixture) -> None:
    page = _page(False)
    page.evaluate.side_effect = error
    raw = _response(False, "text/html; charset=iso-8859-15")
    response = ResponseFactory.from_playwright_response(page, raw, None, {}, pierce_shadow=True)
    assert response.body == "<html><body>Bürger</body></html>".encode()
    assert response.encoding == "utf-8"
    page.content.assert_called_once()
    page.evaluate.assert_called_once()
    if error:
        assert any(record.levelno >= 30 and "shadow" in record.message.lower() for record in caplog.records)


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [None, RuntimeError("Shadow extraction failed")])
async def test_async_shadow_falls_back_to_page_content(
    error: Exception | None, caplog: pytest.LogCaptureFixture
) -> None:
    page = _page(True)
    page.evaluate.side_effect = error
    raw = _response(True, "text/html; charset=iso-8859-15")
    response = await ResponseFactory.from_async_playwright_response(page, raw, None, {}, pierce_shadow=True)
    assert response.body == "<html><body>Bürger</body></html>".encode()
    assert response.encoding == "utf-8"
    page.content.assert_awaited_once()
    page.evaluate.assert_awaited_once()
    if error:
        assert any(record.levelno >= 30 and "shadow" in record.message.lower() for record in caplog.records)


def test_shadow_snapshot_string_preserves_response_data() -> None:
    page = _page(False)
    content = '<html><body><p id="host"><shadow-root><div>Bürger</div></shadow-root></p></body></html>'
    page.evaluate.return_value = content
    raw = _response(False, "text/html; charset=iso-8859-15")
    response = ResponseFactory.from_playwright_response(
        page, raw, None, {}, meta={"source": "test"}, pierce_shadow=True
    )
    assert response.body == content.encode()
    assert response.css("#host > shadow-root > div::text").get() == "Bürger"
    assert response.encoding == "utf-8"
    assert response.meta == {"source": "test"}
    assert response.status == 200 and response.url == page.url and response.headers == raw.headers
    page.content.assert_not_called()
    page.evaluate.assert_called_once()


@pytest.mark.asyncio
async def test_async_shadow_snapshot_string_preserves_response_data() -> None:
    page = _page(True)
    content = '<html><body><p id="host"><shadow-root><div>Bürger</div></shadow-root></p></body></html>'
    page.evaluate.return_value = content
    raw = _response(True, "text/html; charset=iso-8859-15")
    response = await ResponseFactory.from_async_playwright_response(
        page, raw, None, {}, meta={"source": "test"}, pierce_shadow=True
    )
    assert response.body == content.encode()
    assert response.css("#host > shadow-root > div::text").get() == "Bürger"
    assert response.encoding == "utf-8"
    assert response.meta == {"source": "test"}
    assert response.status == 200 and response.url == page.url and response.headers == raw.headers
    page.content.assert_not_awaited()
    page.evaluate.assert_awaited_once()


@pytest.mark.parametrize("has_page", [False, True])
def test_shadow_keeps_raw_body_without_html_page(has_page: bool) -> None:
    page = _page(False)
    raw = _response(False, "text/plain; charset=iso-8859-15" if has_page else "text/html; charset=iso-8859-15")
    response = ResponseFactory.from_playwright_response(page if has_page else None, raw, None, {}, pierce_shadow=True)
    assert response.body == b"B\xfcrger"
    assert response.encoding == "iso-8859-15"
    page.evaluate.assert_not_called()
    page.content.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("has_page", [False, True])
async def test_async_shadow_keeps_raw_body_without_html_page(has_page: bool) -> None:
    page = _page(True)
    raw = _response(True, "text/plain; charset=iso-8859-15" if has_page else "text/html; charset=iso-8859-15")
    response = await ResponseFactory.from_async_playwright_response(
        page if has_page else None, raw, None, {}, pierce_shadow=True
    )
    assert response.body == b"B\xfcrger"
    assert response.encoding == "iso-8859-15"
    page.evaluate.assert_not_awaited()
    page.content.assert_not_awaited()
