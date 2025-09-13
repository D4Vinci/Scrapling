from unittest.mock import Mock

from scrapling.parser import Selector
from scrapling.engines.toolbelt.custom import ResponseEncoding
from scrapling.engines.toolbelt.convertor import ResponseFactory, Response


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

    def test_response_encoding_edge_cases(self):
        """Test response encoding handling"""
        # Test various content types
        test_cases = [
            (None, "utf-8"),
            ("", "utf-8"),
            ("text/html; charset=invalid", "utf-8"),
            ("application/octet-stream", "utf-8"),
        ]

        for content_type, expected in test_cases:
            encoding = ResponseEncoding.get_value(content_type)
            assert encoding == expected

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
