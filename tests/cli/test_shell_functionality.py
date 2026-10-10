import pytest
from unittest.mock import patch, MagicMock

from scrapling.parser import Selector
from scrapling.core._types import cast, extraction_types
from scrapling.core.shell import CustomShell, CurlParser, Convertor


class TestCurlParser:
    """Test curl command parsing"""

    @pytest.fixture
    def parser(self):
        return CurlParser()

    def test_basic_curl_parse(self, parser):
        """Test parsing basic curl commands"""
        # Simple GET
        curl_cmd = "curl https://example.com"
        request = parser.parse(curl_cmd)

        assert request.url == "https://example.com"
        assert request.method == "get"
        assert request.data is None

    def test_curl_with_headers(self, parser):
        """Test parsing curl with headers"""
        curl_cmd = '''curl https://example.com \
            -H "User-Agent: Mozilla/5.0" \
            -H "Accept: application/json"'''

        request = parser.parse(curl_cmd)

        assert request.headers["User-Agent"] == "Mozilla/5.0"
        assert request.headers["Accept"] == "application/json"

    def test_curl_with_data(self, parser):
        """Test parsing curl with data"""
        # Form data
        curl_cmd = 'curl https://example.com -X POST -d "key=value&foo=bar"'
        request = parser.parse(curl_cmd)

        assert request.method == "post"
        assert request.data == "key=value&foo=bar"

        # JSON data
        curl_cmd = """curl https://example.com -X POST --data-raw '{"key": "value"}'"""
        request = parser.parse(curl_cmd)

        assert request.json_data == {"key": "value"}

    def test_curl_with_cookies(self, parser):
        """Test parsing curl with cookies"""
        curl_cmd = '''curl https://example.com \
            -H "Cookie: session=abc123; user=john" \
            -b "extra=cookie"'''

        request = parser.parse(curl_cmd)

        assert request.cookies["session"] == "abc123"
        assert request.cookies["user"] == "john"
        assert request.cookies["extra"] == "cookie"

    def test_curl_with_proxy(self, parser):
        """Test parsing curl with proxy"""
        curl_cmd = "curl https://example.com -x http://proxy:8080 -U user:pass"
        request = parser.parse(curl_cmd)

        assert "http://user:pass@proxy:8080" in request.proxy["http"]

    def test_curl2fetcher(self, parser):
        """Test converting curl to fetcher request"""
        with patch("scrapling.fetchers.Fetcher.get") as mock_get:
            mock_response = MagicMock()
            mock_get.return_value = mock_response

            curl_cmd = "curl https://example.com"
            _ = parser.convert2fetcher(curl_cmd)

            mock_get.assert_called_once()

    def test_invalid_curl_commands(self, parser):
        """Test handling invalid curl commands"""
        # Invalid format
        with pytest.raises(AttributeError):
            parser.parse("not a curl command")


class TestConvertor:
    """Test content conversion functionality"""

    @pytest.fixture
    def sample_html(self):
        return """
        <html>
            <body>
                <div class="content">
                    <h1>Title</h1>
                    <p>Some text content</p>
                </div>
            </body>
        </html>
        """

    def test_extract_markdown(self, sample_html):
        """Test extracting content as Markdown"""
        page = Selector(sample_html)
        content = list(Convertor._extract_content(page, "markdown"))

        assert len(content) > 0
        assert "Title\n=====" in content[0]  # Markdown conversion

    def test_extract_html(self, sample_html):
        """Test extracting content as HTML"""
        page = Selector(sample_html)
        content = list(Convertor._extract_content(page, "html"))

        assert len(content) > 0
        assert "<h1>Title</h1>" in content[0]

    def test_extract_text(self, sample_html):
        """Test extracting content as plain text"""
        page = Selector(sample_html)
        content = list(Convertor._extract_content(page, "text"))

        assert len(content) > 0
        assert "Title" in content[0]
        assert "Some text content" in content[0]

    def test_extract_with_selector(self, sample_html):
        """Test extracting with CSS selector"""
        page = Selector(sample_html)
        content = list(Convertor._extract_content(page, "text", css_selector=".content"))

        assert len(content) > 0

    def test_write_to_file(self, sample_html, tmp_path):
        """Test writing content to files"""
        page = Selector(sample_html)

        # Test markdown
        md_file = tmp_path / "output.md"
        Convertor.write_content_to_file(page, str(md_file))
        assert md_file.exists()

        # Test HTML
        html_file = tmp_path / "output.html"
        Convertor.write_content_to_file(page, str(html_file))
        assert html_file.exists()

        # Test text
        txt_file = tmp_path / "output.txt"
        Convertor.write_content_to_file(page, str(txt_file))
        assert txt_file.exists()

    @pytest.mark.parametrize("encoding", ["iso-8859-1", "windows-1252"])
    @pytest.mark.parametrize("extension", ["md", "txt"])
    def test_write_text_outputs_as_utf8(self, encoding, extension, tmp_path):
        """Test that md/txt output does not depend on the page charset"""
        page = Selector("<html><body><p>Caf&eacute; &mdash; &#x4E2D;</p></body></html>", encoding=encoding)

        out_file = tmp_path / f"output.{extension}"
        Convertor.write_content_to_file(page, str(out_file))

        assert out_file.read_bytes().decode("utf-8").strip() == "Café — 中"

    def test_write_html_keeps_page_encoding(self, tmp_path):
        """Test that html output is still written with the page encoding"""
        page = Selector("<html><body><p>Caf&eacute;</p></body></html>", encoding="iso-8859-1")

        out_file = tmp_path / "output.html"
        Convertor.write_content_to_file(page, str(out_file))

        assert "Caf\xe9".encode("iso-8859-1") in out_file.read_bytes()

    def test_write_utf8_page_is_unchanged(self, tmp_path):
        """Test that md/txt output of a UTF-8 page is written as UTF-8"""
        page = Selector("<html><body><p>Café — 中</p></body></html>")

        for extension in ("md", "txt"):
            out_file = tmp_path / f"output.{extension}"
            Convertor.write_content_to_file(page, str(out_file))
            assert out_file.read_bytes().decode("utf-8").strip() == "Café — 中"

    def test_failed_conversion_keeps_existing_file(self, sample_html, tmp_path):
        """Test that a failing conversion does not truncate the output file"""
        page = Selector(sample_html)
        out_file = tmp_path / "output.md"
        out_file.write_text("previous content", encoding="utf-8")

        with patch.object(Convertor, "_extract_content", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                Convertor.write_content_to_file(page, str(out_file))
        assert out_file.read_text(encoding="utf-8") == "previous content"

        missing_file = tmp_path / "missing.txt"
        with patch.object(Convertor, "_extract_content", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                Convertor.write_content_to_file(page, str(missing_file))
        assert not missing_file.exists()

    def test_invalid_operations(self, sample_html):
        """Test error handling in convertor"""
        page = Selector(sample_html)

        # Invalid extraction type
        with pytest.raises(ValueError):
            list(Convertor._extract_content(page, cast(extraction_types, "invalid")))

        # Invalid filename
        with pytest.raises(ValueError):
            Convertor.write_content_to_file(page, "")

        # Unknown file extension
        with pytest.raises(ValueError):
            Convertor.write_content_to_file(page, "output.xyz")


class TestCustomShell:
    """Test interactive shell functionality"""

    def test_shell_initialization(self):
        """Test shell initialization"""
        shell = CustomShell(code="", log_level="debug")

        assert shell.log_level == 10  # DEBUG level
        assert shell.page is None
        assert len(shell.pages) == 0

    def test_shell_namespace(self):
        """Test shell namespace creation"""
        shell = CustomShell(code="")
        namespace = shell.get_namespace()

        # Check all expected functions/classes are available
        assert "get" in namespace
        assert "post" in namespace
        assert "Fetcher" in namespace
        assert "StealthyFetcher" in namespace
        assert "view" in namespace
        assert "uncurl" in namespace
