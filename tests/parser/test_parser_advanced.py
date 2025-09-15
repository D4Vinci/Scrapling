import re
import pytest
from unittest.mock import Mock

from scrapling import Selector, Selectors
from scrapling.core.custom_types import TextHandler, TextHandlers
from scrapling.core.storage import SQLiteStorageSystem


class TestSelectorAdvancedFeatures:
    """Test advanced Selector features like adaptive matching"""

    def test_adaptive_initialization_with_storage(self):
        """Test adaptive initialization with custom storage"""
        html = "<html><body><p>Test</p></body></html>"

        # Use the actual SQLiteStorageSystem for this test
        selector = Selector(
            content=html,
            adaptive=True,
            storage=SQLiteStorageSystem,
            storage_args={"storage_file": ":memory:", "url": "https://example.com"}
        )

        assert selector._Selector__adaptive_enabled is True
        assert selector._storage is not None

    def test_adaptive_initialization_with_default_storage_args(self):
        """Test adaptive initialization with default storage args"""
        html = "<html><body><p>Test</p></body></html>"
        url = "https://example.com"

        # Test that adaptive mode uses default storage when no explicit args provided
        selector = Selector(
            content=html,
            url=url,
            adaptive=True
        )

        # Should create storage with default args
        assert selector._storage is not None

    def test_adaptive_with_existing_storage(self):
        """Test adaptive initialization with existing storage object"""
        html = "<html><body><p>Test</p></body></html>"

        mock_storage = Mock()

        selector = Selector(
            content=html,
            adaptive=True,
            _storage=mock_storage
        )

        assert selector._storage is mock_storage


class TestAdvancedSelectors:
    """Test advanced selector functionality"""

    @pytest.fixture
    def complex_html(self):
        return """
        <html>
            <body>
                <div class="container" data-test='{"key": "value"}'>
                    <p>First paragraph</p>
                    <!-- Comment -->
                    <p>Second paragraph</p>
                    <![CDATA[Some CDATA content]]>
                    <div class="nested">
                        <span id="special">Special content</span>
                        <span>Regular content</span>
                    </div>
                    <table>
                        <tr><td>Cell 1</td><td>Cell 2</td></tr>
                        <tr><td>Cell 3</td><td>Cell 4</td></tr>
                    </table>
                </div>
            </body>
        </html>
        """

    def test_comment_and_cdata_handling(self, complex_html):
        """Test handling of comments and CDATA"""
        # With comments/CDATA kept
        page = Selector(
            complex_html,
            keep_comments=True,
            keep_cdata=True
        )
        content = page.body
        assert "Comment" in content
        assert "CDATA" in content

        # Without comments/CDATA
        page = Selector(
            complex_html,
            keep_comments=False,
            keep_cdata=False
        )
        content = page.html_content
        assert "Comment" not in content

    def test_advanced_xpath_variables(self, complex_html):
        """Test XPath with variables"""
        page = Selector(complex_html)

        # Using XPath variables
        cells = page.xpath(
            "//td[text()=$cell_text]",
            cell_text="Cell 1"
        )
        assert len(cells) == 1
        assert cells[0].text == "Cell 1"

    def test_pseudo_elements(self, complex_html):
        """Test CSS pseudo-elements"""
        page = Selector(complex_html)

        # ::text pseudo-element
        texts = page.css("p::text")
        assert len(texts) == 2
        assert isinstance(texts[0], TextHandler)

        # ::attr() pseudo-element
        attrs = page.css("div::attr(class)")
        assert "container" in attrs

    def test_complex_attribute_operations(self, complex_html):
        """Test complex attribute handling"""
        page = Selector(complex_html)
        container = page.css(".container")[0]

        # JSON in attributes
        data = container.attrib["data-test"].json()
        assert data["key"] == "value"

        # Attribute searching
        matches = list(container.attrib.search_values("container"))
        assert len(matches) == 1

    def test_url_joining(self):
        """Test URL joining functionality"""
        page = Selector("<html></html>", url="https://example.com/page")

        # Relative URL
        assert page.urljoin("../other") == "https://example.com/other"
        assert page.urljoin("/absolute") == "https://example.com/absolute"
        assert page.urljoin("relative") == "https://example.com/relative"

    def test_find_operations_edge_cases(self, complex_html):
        """Test edge cases in find operations"""
        page = Selector(complex_html)

        # Multiple argument types
        _ = page.find_all(
            "span",
            ["div"],
            {"class": "nested"},
            lambda e: e.text != ""
        )

        # Regex pattern matching
        pattern = re.compile(r"Cell \d+")
        cells = page.find_all(pattern)
        assert len(cells) == 4

    def test_text_operations_edge_cases(self, complex_html):
        """Test text operation edge cases"""
        page = Selector(complex_html)

        # get_all_text with a custom separator
        text = page.get_all_text(separator=" | ", strip=True)
        assert " | " in text

        # Ignore specific tags
        text = page.get_all_text(ignore_tags=("table",))
        assert "Cell" not in text

        # With empty values
        text = page.get_all_text(valid_values=False)
        assert text != ""


class TestTextHandlerAdvanced:
    """Test advanced TextHandler functionality"""

    def test_text_handler_operations(self):
        """Test various TextHandler operations"""
        text = TextHandler("  Hello World  ")

        # All string methods should return TextHandler
        assert isinstance(text.strip(), TextHandler)
        assert isinstance(text.upper(), TextHandler)
        assert isinstance(text.lower(), TextHandler)
        assert isinstance(text.replace("World", "Python"), TextHandler)

        # Custom methods
        assert text.clean() == "Hello World"

        # Sorting
        text2 = TextHandler("dcba")
        assert text2.sort() == "abcd"

    def test_text_handler_regex(self):
        """Test regex operations on TextHandler"""
        text = TextHandler("Price: $10.99, Sale: $8.99")

        # Basic regex
        prices = text.re(r"\$[\d.]+")
        assert len(prices) == 2
        assert prices[0] == "$10.99"

        # Case insensitive
        text2 = TextHandler("HELLO hello HeLLo")
        matches = text2.re(r"hello", case_sensitive=False)
        assert len(matches) == 3

        # Clean match
        text3 = TextHandler(" He  l  lo  ")
        matches = text3.re(r"He l lo", clean_match=True, case_sensitive=False)
        assert len(matches) == 1

    def test_text_handlers_operations(self):
        """Test TextHandlers list operations"""
        handlers = TextHandlers([
            TextHandler("First"),
            TextHandler("Second"),
            TextHandler("Third")
        ])

        # Slicing should return TextHandlers
        assert isinstance(handlers[0:2], TextHandlers)

        # Get methods
        assert handlers.get() == "First"
        assert handlers.get("default") == "First"
        assert TextHandlers([]).get("default") == "default"


class TestSelectorsAdvanced:
    """Test advanced Selectors functionality"""

    def test_selectors_filtering(self):
        """Test filtering operations on Selectors"""
        html = """
        <div>
            <p class="highlight">Important</p>
            <p>Regular</p>
            <p class="highlight">Also important</p>
        </div>
        """
        page = Selector(html)
        paragraphs = page.css("p")

        # Filter by class
        highlighted = paragraphs.filter(lambda p: p.has_class("highlight"))
        assert len(highlighted) == 2

        # Search for a specific element
        found = paragraphs.search(lambda p: p.text == "Regular")
        assert found is not None
        assert found.text == "Regular"

    def test_selectors_properties(self):
        """Test Selectors properties"""
        html = "<div><p>1</p><p>2</p><p>3</p></div>"
        page = Selector(html)
        paragraphs = page.css("p")

        assert paragraphs.first.text == "1"
        assert paragraphs.last.text == "3"
        assert paragraphs.length == 3
