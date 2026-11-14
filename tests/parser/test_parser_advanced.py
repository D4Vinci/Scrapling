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

    def test_comment_handling(self, complex_html):
        """Test handling of comments"""
        page = Selector(complex_html, keep_comments=True)
        content = page.html_content
        assert "Comment" in content

        page = Selector(complex_html, keep_comments=False)
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
        assert isinstance(texts[0], Selector)
        assert isinstance(texts[0].get(), TextHandler)

        # ::attr() pseudo-element
        attrs = page.css("div::attr(class)")
        assert "container" in attrs.getall()

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

    def test_get_all_text_preserves_interleaved_text_nodes(self):
        """Test get_all_text preserves interleaved text nodes"""
        html = """
        <html>
        <body>
            <main>
                string1
                <b>string2</b>
                string3
                <div>
                    <span>string4</span>
                </div>
                string5
                <script>ignored</script>
                string6
                <style>ignored</style>
                string7
            </main>
        </body>
        </html>
        """

        page = Selector(html, adaptive=False)
        node = page.css("main")[0]

        assert node.get_all_text("\n", strip=True) == "string1\nstring2\nstring3\nstring4\nstring5\nstring6\nstring7"

    def test_get_all_text_keeps_text_after_comment(self):
        """Tail text following a comment or PI node must still be collected"""
        html = "<div>before<!-- c -->after<p>x</p></div>"
        assert Selector(html, keep_comments=True).get_all_text() == "before\nafter\nx"

    def test_get_all_text_deep_nesting(self):
        """Deeply nested trees collect every visible text node and skip ignored subtrees"""
        depth = 500
        html = "<div>" + "".join(f"<span>t{i}" for i in range(depth)) + "leaf" + "</span>" * depth + "end</div>"
        text = Selector(html).get_all_text(strip=True)
        assert text.startswith("t0\nt1\n")
        assert "leaf" in text and text.endswith("end")
        assert text.count("\n") == depth

        ignored = "<div>keep<script>" + "<b>x</b>" * depth + "</script>done</div>"
        assert Selector(ignored).get_all_text(strip=True) == "keep\ndone"


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

    def test_text_handler_regex_check_match(self):
        """Test TextHandler.re() with check_match=True returns bool"""
        text = TextHandler("Price: $10.99")
        assert text.re(r"\$[\d.]+", check_match=True) is True
        assert text.re(r"no-match-pattern", check_match=True) is False

    def test_text_handler_regex_replace_entities_false(self):
        """Test TextHandler.re() with replace_entities=False preserves entities"""
        text = TextHandler("Hello &amp; World")
        results = text.re(r"&amp;", replace_entities=False)
        assert len(results) == 1
        assert results[0] == "&amp;"

    def test_text_handler_regex_with_groups(self):
        """Test TextHandler.re() with capture groups flattens results"""
        text = TextHandler("name=Alice age=30 name=Bob age=25")
        results = text.re(r"name=(\w+) age=(\d+)")
        assert len(results) == 4
        assert "Alice" in results
        assert "30" in results

    def test_text_handler_re_first_with_default(self):
        """Test TextHandler.re_first() returns default when no match"""
        text = TextHandler("no numbers here")
        result = text.re_first(r"\d+", default="N/A")
        assert result == "N/A"

    def test_text_handler_re_first_returns_first_match(self):
        """Test TextHandler.re_first() returns first match"""
        text = TextHandler("a1 b2 c3")
        result = text.re_first(r"\d")
        assert result == "1"
        assert isinstance(result, TextHandler)

    def test_text_handler_clean_with_entities(self):
        """Test TextHandler.clean() with remove_entities=True"""
        text = TextHandler("Hello\t&amp;\nWorld")
        cleaned = text.clean(remove_entities=True)
        assert "&amp;" not in cleaned
        assert "&" in cleaned
        assert "\t" not in cleaned
        assert "\n" not in cleaned

    def test_text_handler_clean_without_entities(self):
        """Test TextHandler.clean() preserves entities by default"""
        text = TextHandler("Hello\t&amp;\nWorld")
        cleaned = text.clean(remove_entities=False)
        assert "&amp;" in cleaned

    def test_text_handler_json_valid(self):
        """Test TextHandler.json() with valid JSON"""
        text = TextHandler('{"key": "value", "num": 42}')
        data = text.json()
        assert data["key"] == "value"
        assert data["num"] == 42

    def test_text_handler_json_invalid(self):
        """Test TextHandler.json() raises on invalid JSON"""
        text = TextHandler("not json")
        with pytest.raises(Exception):
            text.json()

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

    def test_text_handlers_re(self):
        """Test TextHandlers.re() flattens results across all elements"""
        handlers = TextHandlers([
            TextHandler("a1 b2"),
            TextHandler("c3 d4"),
        ])
        results = handlers.re(r"[a-z]\d")
        assert isinstance(results, TextHandlers)
        assert len(results) == 4
        assert results[0] == "a1"
        assert results[3] == "d4"

    def test_text_handlers_re_empty(self):
        """Test TextHandlers.re() on empty list"""
        handlers = TextHandlers([])
        results = handlers.re(r"\d+")
        assert isinstance(results, TextHandlers)
        assert len(results) == 0

    def test_text_handlers_re_no_matches(self):
        """Test TextHandlers.re() when no element matches"""
        handlers = TextHandlers([TextHandler("abc"), TextHandler("def")])
        results = handlers.re(r"\d+")
        assert len(results) == 0

    def test_text_handlers_extract(self):
        """Test TextHandlers.extract() returns self"""
        handlers = TextHandlers([TextHandler("a"), TextHandler("b")])
        assert handlers.extract() is handlers
        assert handlers.getall() is handlers


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


class TestBaseHrefResolution:
    """Relative URLs must resolve against the document's first <base href>."""

    def test_absolute_base(self):
        page = Selector(
            '<html><head><base href="https://cdn.example/assets/"></head><body></body></html>',
            url="https://example.com/posts/1",
        )
        assert page.urljoin("img.png") == "https://cdn.example/assets/img.png"
        assert page.urljoin("/root") == "https://cdn.example/root"

    def test_relative_base_resolves_against_document(self):
        page = Selector(
            '<base href="../static/">',
            url="https://example.com/a/b/page",
        )
        assert page.urljoin("app.js") == "https://example.com/a/static/app.js"

    def test_root_relative_and_protocol_relative_base(self):
        root_relative = Selector('<base href="/assets/">', url="https://example.com/deep/page")
        assert root_relative.urljoin("x.css") == "https://example.com/assets/x.css"

        protocol_relative = Selector('<base href="//cdn.example/v1/">', url="https://example.com/")
        assert protocol_relative.urljoin("x.css") == "https://cdn.example/v1/x.css"

    def test_empty_and_whitespace_base_fall_back_to_document_url(self):
        for href in ("", "   "):
            page = Selector(f'<base href="{href}">', url="https://example.com/dir/page")
            assert page.urljoin("x") == "https://example.com/dir/x"

    def test_first_base_with_href_wins(self):
        page = Selector(
            '<base target="_blank"><base href="https://first.example/"><base href="https://second.example/">',
            url="https://example.com/",
        )
        assert page.urljoin("a") == "https://first.example/a"

    def test_invalid_and_script_bases_are_ignored(self):
        for href in ("http://[broken", "javascript:alert(1)", "data:text/html,x"):
            page = Selector(f'<base href="{href}">', url="https://example.com/dir/page")
            assert page.urljoin("x") == "https://example.com/dir/x"

    def test_absolute_links_are_unaffected(self):
        page = Selector('<base href="https://cdn.example/">', url="https://example.com/")
        assert page.urljoin("https://other.example/abs") == "https://other.example/abs"

    def test_descendant_selectors_use_document_base(self):
        page = Selector(
            '<html><head><base href="https://cdn.example/"></head><body><a href="x">x</a></body></html>',
            url="https://example.com/page",
        )
        link = page.css("a")[0]
        assert link.urljoin("x") == "https://cdn.example/x"

    def test_documents_with_same_url_do_not_share_a_base(self):
        first = Selector('<base href="https://one.example/">', url="https://example.com/")
        second = Selector('<base href="https://two.example/">', url="https://example.com/")
        assert first.urljoin("a") == "https://one.example/a"
        assert second.urljoin("a") == "https://two.example/a"

    def test_no_base_keeps_existing_behaviour(self):
        page = Selector("<html></html>", url="https://example.com/page")
        assert page.urljoin("relative") == "https://example.com/relative"
        assert page.urljoin("/absolute") == "https://example.com/absolute"

    def test_base_works_without_document_url(self):
        page = Selector('<base href="https://cdn.example/a/">')
        assert page.urljoin("x") == "https://cdn.example/a/x"

    def test_template_base_is_not_document_content(self):
        page = Selector(
            '<html><head><template><base href="https://wrong.example/"></template>'
            '<base href="https://right.example/"></head></html>',
            url="https://example.com/page",
        )
        assert page.urljoin("x") == "https://right.example/x"

        only_template = Selector(
            '<template><base href="https://wrong.example/"></template>',
            url="https://example.com/dir/page",
        )
        assert only_template.urljoin("x") == "https://example.com/dir/x"

    def test_invalid_port_falls_back_to_document_url(self):
        page = Selector('<base href="http://cdn.example:99999/">', url="https://example.com/dir/page")
        assert page.urljoin("x") == "https://example.com/dir/x"

    def test_special_scheme_without_slashes_follows_whatwg(self):
        # Different scheme from the document: absolute URL.
        page = Selector('<base href="http:cdn.example/assets/">', url="https://example.com/dir/page")
        assert page.urljoin("x") == "http://cdn.example/assets/x"

        # Same scheme as the document: relative reference, not a new origin.
        same = Selector('<base href="https:cdn.example/assets/">', url="https://example.com/dir/page")
        assert same.urljoin("x") == "https://example.com/dir/cdn.example/assets/x"

        # One slash and backslashes count as slashes for special schemes.
        one_slash = Selector('<base href="http:/cdn.example/assets/">', url="https://example.com/dir/page")
        assert one_slash.urljoin("x") == "http://cdn.example/assets/x"

        backslashes = Selector('<base href="http:\\cdn.example\\assets\\">', url="https://example.com/dir/page")
        assert backslashes.urljoin("x") == "http://cdn.example/assets/x"

        # Extra slashes still introduce the authority for special schemes.
        triple = Selector('<base href="https:///cdn.example/assets/">', url="https://example.com/dir/page")
        assert triple.urljoin("x") == "https://cdn.example/assets/x"

        many_backslashes = Selector('<base href="https:\\\\\\cdn.example\\\\assets\\\\">', url="https://example.com/dir/page")
        assert many_backslashes.urljoin("x") == "https://cdn.example/assets/x"

        # file: is special too; backslashes become path separators.
        file_url = Selector('<base href="file:\\cdn.example\\assets\\">', url="https://example.com/dir/page")
        assert file_url.urljoin("x") == "file:///cdn.example/assets/x"

        # UNC form keeps its host.
        unc = Selector('<base href="file://server/share/">', url="https://example.com/dir/page")
        assert unc.urljoin("x") == "file://server/share/x"

        # A special scheme without a host cannot become a base.
        no_host = Selector('<base href="http:">', url="https://example.com/dir/page")
        assert no_host.urljoin("x") == "https://example.com/dir/x"

    def test_nbsp_is_not_html_whitespace(self):
        page = Selector('<base href="\u00a0https://cdn.example/a/\u00a0">', url="https://example.com/dir/page")
        joined = page.urljoin("x")
        assert joined.startswith("https://example.com/dir/")
        assert "cdn.example" in joined

    def test_base_scan_happens_once_per_document(self, monkeypatch):
        page = Selector(
            '<base href="https://cdn.example/"><a href="1">1</a><a href="2">2</a>',
            url="https://example.com/",
        )
        calls = []
        original = Selector._document_root

        def counting(selector):
            calls.append(1)
            return original(selector)

        monkeypatch.setattr(Selector, "_document_root", counting)
        links = page.css("a")
        assert links[0].urljoin("x") == "https://cdn.example/x"
        assert links[1].urljoin("y") == "https://cdn.example/y"
        assert len(calls) == 1
