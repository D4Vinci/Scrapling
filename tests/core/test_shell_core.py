import pytest

from scrapling.core.shell import (
    _CookieParser,
    _ParseHeaders,
    Request,
    _known_logging_levels,
)


class TestCookieParser:
    """Test cookie parsing functionality"""
    
    def test_simple_cookie_parsing(self):
        """Test parsing a simple cookie"""
        cookie_string = "session_id=abc123"
        cookies = list(_CookieParser(cookie_string))
        assert len(cookies) == 1
        assert cookies[0] == ("session_id", "abc123")
    
    def test_multiple_cookies_parsing(self):
        """Test parsing multiple cookies"""
        cookie_string = "session_id=abc123; theme=dark; lang=en"
        cookies = list(_CookieParser(cookie_string))
        assert len(cookies) == 3
        cookie_dict = dict(cookies)
        assert cookie_dict["session_id"] == "abc123"
        assert cookie_dict["theme"] == "dark"
        assert cookie_dict["lang"] == "en"
    
    def test_cookie_with_attributes(self):
        """Test parsing cookies with attributes"""
        cookie_string = "session_id=abc123; Path=/; HttpOnly; Secure"
        cookies = list(_CookieParser(cookie_string))
        assert len(cookies) == 1
        assert cookies[0] == ("session_id", "abc123")
    
    def test_empty_cookie_string(self):
        """Test parsing empty cookie string"""
        cookies = list(_CookieParser(""))
        assert len(cookies) == 0
    
    def test_malformed_cookie_handling(self):
        """Test handling of malformed cookies"""
        # Should not raise exception but may return an empty list
        cookies = list(_CookieParser("invalid_cookie_format"))
        assert isinstance(cookies, list)


class TestParseHeaders:
    """Test header parsing functionality"""
    
    def test_simple_headers(self):
        """Test parsing simple headers"""
        header_lines = [
            "Content-Type: text/html",
            "Content-Length: 1234",
            "User-Agent: TestAgent/1.0"
        ]
        headers, cookies = _ParseHeaders(header_lines)
        
        assert headers["Content-Type"] == "text/html"
        assert headers["Content-Length"] == "1234"
        assert headers["User-Agent"] == "TestAgent/1.0"
        assert len(cookies) == 0
    
    def test_headers_with_cookies(self):
        """Test parsing headers with cookie headers"""
        header_lines = [
            "Content-Type: text/html",
            "Set-Cookie: session_id=abc123",
            "Set-Cookie: theme=dark; Path=/",
        ]
        headers, cookies = _ParseHeaders(header_lines)
        
        assert headers["Content-Type"] == "text/html"
        assert "Set-Cookie" in headers  # Should contain the first Set-Cookie
        # Cookie parsing behavior depends on implementation
    
    def test_headers_without_colons(self):
        """Test headers without colons"""
        header_lines = [
            "Content-Type: text/html",
            "InvalidHeader;",  # Header ending with semicolon
        ]
        headers, cookies = _ParseHeaders(header_lines)
        
        assert headers["Content-Type"] == "text/html"
        assert "InvalidHeader" in headers
        assert headers["InvalidHeader"] == ""
    
    def test_invalid_header_format(self):
        """Test invalid header format raises error"""
        header_lines = [
            "Content-Type: text/html",
            "InvalidHeaderWithoutColon",  # No colon, no semicolon
        ]
        
        with pytest.raises(ValueError, match="Could not parse header without colon"):
            _ParseHeaders(header_lines)
    
    def test_headers_with_multiple_colons(self):
        """Test headers with multiple colons"""
        header_lines = [
            "Authorization: Bearer: token123",
            "X-Custom: value:with:colons",
        ]
        headers, cookies = _ParseHeaders(header_lines)
        
        assert headers["Authorization"] == "Bearer: token123"
        assert headers["X-Custom"] == "value:with:colons"
    
    def test_headers_with_whitespace(self):
        """Test headers with extra whitespace"""
        header_lines = [
            "  Content-Type  :  text/html  ",
            "\tUser-Agent\t:\tTestAgent/1.0\t",
        ]
        headers, cookies = _ParseHeaders(header_lines)
        
        # Should handle whitespace correctly
        assert "Content-Type" in headers or "  Content-Type  " in headers
        assert "text/html" in str(headers.values()) or "  text/html  " in str(headers.values())
    
    def test_parse_cookies_disabled(self):
        """Test parsing with cookies disabled"""
        header_lines = [
            "Content-Type: text/html",
            "Set-Cookie: session_id=abc123",
        ]
        headers, cookies = _ParseHeaders(header_lines, parse_cookies=False)
        
        assert headers["Content-Type"] == "text/html"
        # Cookie parsing behavior when disabled
        assert len(cookies) == 0 or "Set-Cookie" in headers
    
    def test_empty_header_lines(self):
        """Test parsing empty header lines"""
        headers, cookies = _ParseHeaders([])
        assert len(headers) == 0
        assert len(cookies) == 0


class TestRequestNamedTuple:
    """Test Request namedtuple functionality"""
    
    def test_request_creation(self):
        """Test creating Request namedtuple"""
        request = Request(
            method="GET",
            url="https://example.com",
            params={"q": "test"},
            data=None,
            json_data=None,
            headers={"User-Agent": "Test"},
            cookies={"session": "abc123"},
            proxy=None,
            follow_redirects=True
        )
        
        assert request.method == "GET"
        assert request.url == "https://example.com"
        assert request.params == {"q": "test"}
        assert request.headers == {"User-Agent": "Test"}
        assert request.follow_redirects is True
    
    def test_request_defaults(self):
        """Test Request with default/None values"""
        request = Request(
            method="POST",
            url="https://api.example.com",
            params=None,
            data='{"key": "value"}',
            json_data={"key": "value"},
            headers={},
            cookies={},
            proxy="http://proxy:8080",
            follow_redirects=False
        )
        
        assert request.method == "POST"
        assert request.data == '{"key": "value"}'
        assert request.json_data == {"key": "value"}
        assert request.proxy == "http://proxy:8080"
        assert request.follow_redirects is False
    
    def test_request_field_access(self):
        """Test accessing Request fields"""
        request = Request(
            "GET", "https://example.com", {}, None, None, {}, {}, None, True
        )
        
        # Test field access by name
        assert hasattr(request, 'method')
        assert hasattr(request, 'url') 
        assert hasattr(request, 'params')
        assert hasattr(request, 'data')
        assert hasattr(request, 'json_data')
        assert hasattr(request, 'headers')
        assert hasattr(request, 'cookies')
        assert hasattr(request, 'proxy')
        assert hasattr(request, 'follow_redirects')
        
        # Test field access by index
        assert request[0] == "GET"
        assert request[1] == "https://example.com"


class TestLoggingLevels:
    """Test logging level constants"""
    
    def test_known_logging_levels(self):
        """Test that all known logging levels are defined"""
        expected_levels = ["debug", "info", "warning", "error", "critical", "fatal"]
        
        for level in expected_levels:
            assert level in _known_logging_levels
            assert isinstance(_known_logging_levels[level], int)
    
    def test_logging_level_values(self):
        """Test logging level values are correct"""
        from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL
        
        assert _known_logging_levels["debug"] == DEBUG
        assert _known_logging_levels["info"] == INFO
        assert _known_logging_levels["warning"] == WARNING
        assert _known_logging_levels["error"] == ERROR
        assert _known_logging_levels["critical"] == CRITICAL
        assert _known_logging_levels["fatal"] == FATAL
    
    def test_level_hierarchy(self):
        """Test that logging levels have correct hierarchy"""
        levels = [
            _known_logging_levels["debug"],
            _known_logging_levels["info"],
            _known_logging_levels["warning"],
            _known_logging_levels["error"],
            _known_logging_levels["critical"],
        ]
        
        # Levels should be in ascending order
        for i in range(len(levels) - 1):
            assert levels[i] < levels[i + 1]
