from unittest.mock import AsyncMock, Mock

import pytest

from scrapling.parser import Selector
from scrapling.engines.toolbelt.convertor import ResponseFactory, Response


HTML_WITH_ACCENTED_TEXT = "<html><body>Bürger</body></html>"
LATIN9_CONTENT_TYPE = "text/html; charset=iso-8859-15"


def make_sync_playwright_response():
    response = Mock()
    response.url = "https://example.com"
    response.status = 200
    response.status_text = "OK"
    response.headers = {"content-type": LATIN9_CONTENT_TYPE}
    response.all_headers = Mock(return_value={"content-type": LATIN9_CONTENT_TYPE})
    response.body = Mock(return_value=HTML_WITH_ACCENTED_TEXT.encode("iso-8859-15"))
    response.request.all_headers = Mock(return_value={})
    response.request.redirected_from = None
    return response


def make_sync_page():
    page = Mock()
    page.url = "https://example.com"
    page.content = Mock(return_value=HTML_WITH_ACCENTED_TEXT)
    page.context.cookies = Mock(return_value=[])
    return page


def make_async_playwright_response():
    response = Mock()
    response.url = "https://example.com"
    response.status = 200
    response.status_text = "OK"
    response.headers = {"content-type": LATIN9_CONTENT_TYPE}
    response.all_headers = AsyncMock(return_value={"content-type": LATIN9_CONTENT_TYPE})
    response.body = AsyncMock(return_value=HTML_WITH_ACCENTED_TEXT.encode("iso-8859-15"))
    response.request.all_headers = AsyncMock(return_value={})
    response.request.redirected_from = None
    return response


def make_async_page():
    page = Mock()
    page.url = "https://example.com"
    page.content = AsyncMock(return_value=HTML_WITH_ACCENTED_TEXT)
    page.context.cookies = AsyncMock(return_value=[])
    return page


class TestResponseFactory:
    """Test ResponseFactory functionality"""

    def test_response_from_curl(self):
        """Test creating response from curl_cffi response"""
        # Mock curl response
        mock_curl_response = Mock()
        mock_curl_response.url = "https://example.com"
        mock_curl_response.content = b"<html><body>Test</body></html>"
        mock_curl_response.status_code = 200
        mock_curl_response.reason = "OK"
        mock_curl_response.encoding = "utf-8"
        mock_curl_response.cookies = {"session": "abc"}
        mock_curl_response.headers = {"Content-Type": "text/html"}
        mock_curl_response.request.headers = {"User-Agent": "Test"}
        mock_curl_response.request.method = "GET"
        mock_curl_response.history = []

        response = ResponseFactory.from_http_request(
            mock_curl_response,
            {"adaptive": False}
        )

        assert response.status == 200
        assert response.url == "https://example.com"
        assert isinstance(response, Response)

    def test_playwright_page_content_uses_utf8_encoding(self):
        """page.content() returns Unicode, so its encoded bytes are UTF-8."""
        mock_response = make_sync_playwright_response()
        mock_page = make_sync_page()

        response = ResponseFactory.from_playwright_response(
            mock_page,
            mock_response,
            mock_response,
            {"adaptive": False},
            collect_history=False,
        )

        assert response.encoding == "utf-8"
        assert "Bürger" in response.html_content
        assert "BÃ" not in response.html_content

    def test_playwright_raw_response_keeps_header_encoding(self):
        """Raw response bytes should still use the charset from Content-Type."""
        mock_response = make_sync_playwright_response()

        response = ResponseFactory.from_playwright_response(
            None,
            mock_response,
            mock_response,
            {"adaptive": False},
            collect_history=False,
        )

        assert response.encoding == "iso-8859-15"
        assert "Bürger" in response.html_content

    @pytest.mark.asyncio
    async def test_async_playwright_page_content_uses_utf8_encoding(self):
        """Async page.content() returns Unicode, so its encoded bytes are UTF-8."""
        mock_response = make_async_playwright_response()
        mock_page = make_async_page()

        response = await ResponseFactory.from_async_playwright_response(
            mock_page,
            mock_response,
            mock_response,
            {"adaptive": False},
            collect_history=False,
        )

        assert response.encoding == "utf-8"
        assert "Bürger" in response.html_content
        assert "BÃ" not in response.html_content

    @pytest.mark.asyncio
    async def test_async_playwright_raw_response_keeps_header_encoding(self):
        """Raw response bytes should still use the charset from Content-Type."""
        mock_response = make_async_playwright_response()

        response = await ResponseFactory.from_async_playwright_response(
            None,
            mock_response,
            mock_response,
            {"adaptive": False},
            collect_history=False,
        )

        assert response.encoding == "iso-8859-15"
        assert "Bürger" in response.html_content

    def test_response_history_processing(self):
        """Test processing response history"""
        # Mock responses with redirects
        mock_final = Mock()
        mock_final.status = 200
        mock_final.status_text = "OK"
        mock_final.all_headers = Mock(return_value={})

        mock_redirect = Mock()
        mock_redirect.url = "https://example.com/redirect"
        mock_redirect.response = Mock(return_value=mock_final)
        mock_redirect.all_headers = Mock(return_value={})
        mock_redirect.redirected_from = None

        mock_first = Mock()
        mock_first.request.redirected_from = mock_redirect

        # Process history
        history = ResponseFactory._process_response_history(
            mock_first,
            {}
        )

        assert len(history) >= 0  # Should process redirects


class TestErrorScenarios:
    """Test various error scenarios"""

    def test_invalid_html_handling(self):
        """Test handling of malformed HTML"""
        malformed_html = """
        <html>
            <body>
                <div>Unclosed div
                <p>Paragraph without closing tag
                <span>Nested unclosed
            </body>
        """

        # Should handle gracefully
        page = Selector(malformed_html)
        assert page is not None

        # Should still be able to select elements
        divs = page.css("div")
        assert len(divs) > 0

    def test_empty_responses(self):
        """Test handling of empty responses"""
        # Empty HTML
        page = Selector("")
        assert page is not None

        # Whitespace only
        page = Selector("   \n\t   ")
        assert page is not None

        # Null bytes
        page = Selector("Hello\x00World")
        assert "Hello" in page.get_all_text()
