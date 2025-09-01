import pytest
import json

from scrapling import Selector
from scrapling.core.custom_types import AttributesHandler


class TestAttributesHandler:
    """Test AttributesHandler functionality"""

    @pytest.fixture
    def sample_html(self):
        return """
        <html>
            <body>
                <div id="main" 
                     class="container active" 
                     data-config='{"theme": "dark", "version": 2.5}'
                     data-items='[1, 2, 3, 4, 5]'
                     data-invalid-json='{"broken: json}'
                     title="Main Container"
                     style="color: red; background: blue;"
                     data-empty=""
                     data-number="42"
                     data-bool="true"
                     data-url="https://example.com/page?param=value"
                     custom-attr="custom-value"
                     data-nested='{"user": {"name": "John", "age": 30}}'
                     data-encoded="&lt;div&gt;HTML&lt;/div&gt;"
                     onclick="handleClick()"
                     data-null="null"
                     data-undefined="undefined">
                    Content
                </div>
                <input type="text" 
                       name="username" 
                       value="test@example.com" 
                       placeholder="Enter email"
                       required
                       disabled>
                <img src="/images/photo.jpg" 
                     alt="Photo" 
                     width="100" 
                     height="100"
                     loading="lazy">
            </body>
        </html>
        """

    @pytest.fixture
    def attributes(self, sample_html):
        page = Selector(sample_html)
        element = page.css("#main")[0]
        return element.attrib

    def test_basic_attribute_access(self, attributes):
        """Test basic attribute access"""
        # Dict-like access
        assert attributes["id"] == "main"
        assert attributes["class"] == "container active"
        assert attributes["title"] == "Main Container"

        # Key existence
        assert "id" in attributes
        assert "nonexistent" not in attributes

        # Get with default
        assert attributes.get("id") == "main"
        assert attributes.get("nonexistent") is None
        assert attributes.get("nonexistent", "default") == "default"

    def test_iteration_methods(self, attributes):
        """Test iteration over attributes"""
        # Keys
        keys = list(attributes.keys())
        assert "id" in keys
        assert "class" in keys
        assert "data-config" in keys

        # Values
        values = list(attributes.values())
        assert "main" in values
        assert "container active" in values

        # Items
        items = dict(attributes.items())
        assert items["id"] == "main"
        assert items["class"] == "container active"

        # Length
        assert len(attributes) > 0

    def test_json_parsing(self, attributes):
        """Test JSON parsing from attributes"""
        # Valid JSON object
        config = attributes["data-config"].json()
        assert config["theme"] == "dark"
        assert config["version"] == 2.5

        # Valid JSON array
        items = attributes["data-items"].json()
        assert items == [1, 2, 3, 4, 5]

        # Nested JSON
        nested = attributes["data-nested"].json()
        assert nested["user"]["name"] == "John"
        assert nested["user"]["age"] == 30

        # JSON null
        assert attributes["data-null"].json() is None

    def test_json_error_handling(self, attributes):
        """Test JSON parsing error handling"""
        # Invalid JSON should raise error or return None
        with pytest.raises((json.JSONDecodeError, AttributeError)):
            attributes["data-invalid-json"].json()

        # Non-existent attribute
        with pytest.raises(KeyError):
            attributes["nonexistent"].json()

    def test_json_string_property(self, attributes):
        """Test json_string property"""
        # Should return JSON representation of all attributes
        json_string = attributes.json_string
        assert isinstance(json_string, bytes)

        # Parse it back
        parsed = json.loads(json_string)
        assert parsed["id"] == "main"
        assert parsed["class"] == "container active"

    def test_search_values(self, attributes):
        """Test search_values method"""
        # Exact match
        results = list(attributes.search_values("main", partial=False))
        assert len(results) == 1
        assert "id" in results[0]

        # Partial match
        results = list(attributes.search_values("container", partial=True))
        assert len(results) >= 1
        found_keys = []
        for result in results:
            found_keys.extend(result.keys())
        assert "class" in found_keys or "title" in found_keys

        # Case sensitivity
        results = list(attributes.search_values("MAIN", partial=False))
        assert len(results) == 0  # Should be case-sensitive by default

        # Multiple matches
        results = list(attributes.search_values("2", partial=True))
        assert len(results) > 1  # Should find multiple attributes

        # No matches
        results = list(attributes.search_values("nonexistent", partial=False))
        assert len(results) == 0

    def test_special_attribute_types(self, sample_html):
        """Test handling of special attribute types"""
        page = Selector(sample_html)

        # Boolean attributes
        input_elem = page.css("input")[0]
        assert "required" in input_elem.attrib
        assert "disabled" in input_elem.attrib

        # Empty attributes
        main_elem = page.css("#main")[0]
        assert main_elem.attrib["data-empty"] == ""

        # Numeric string attributes
        assert main_elem.attrib["data-number"] == "42"
        assert main_elem.attrib["data-bool"] == "true"

    def test_attribute_modification(self, sample_html):
        """Test that AttributesHandler is read-only (if applicable)"""
        page = Selector(sample_html)
        element = page.css("#main")[0]
        attrs = element.attrib

        # Test if attributes can be modified
        # This behavior depends on implementation
        original_id = attrs["id"]
        try:
            attrs["id"] = "new-id"
            # If modification is allowed
            assert attrs["id"] == "new-id"
            # Reset
            attrs["id"] = original_id
        except (TypeError, AttributeError):
            # If modification is not allowed (read-only)
            assert attrs["id"] == original_id

    def test_string_representation(self, attributes):
        """Test string representations"""
        # __str__
        str_repr = str(attributes)
        assert isinstance(str_repr, str)
        assert "id" in str_repr or "main" in str_repr

        # __repr__
        repr_str = repr(attributes)
        assert isinstance(repr_str, str)

    def test_edge_cases(self, sample_html):
        """Test edge cases and special scenarios"""
        page = Selector(sample_html)

        # Element with no attributes
        page_with_no_attrs = Selector("<div>Content</div>")
        elem = page_with_no_attrs.css("div")[0]
        assert len(elem.attrib) == 0
        assert list(elem.attrib.keys()) == []
        assert elem.attrib.get("any") is None

        # Element with encoded content
        main_elem = page.css("#main")[0]
        encoded = main_elem.attrib["data-encoded"]
        assert "<" in encoded  # Should decode it

        # Style attribute parsing
        style = main_elem.attrib["style"]
        assert "color: red" in style
        assert "background: blue" in style

    def test_url_attribute(self, attributes):
        """Test URL attributes"""
        url = attributes["data-url"]
        assert url == "https://example.com/page?param=value"

        # Could test URL joining if AttributesHandler supports it
        # based on the parent element's base URL

    def test_comparison_operations(self, sample_html):
        """Test comparison operations if supported"""
        page = Selector(sample_html)
        elem1 = page.css("#main")[0]
        elem2 = page.css("input")[0]

        # Different elements should have different attributes
        assert elem1.attrib != elem2.attrib

        # The same element should have equal attributes
        elem1_again = page.css("#main")[0]
        assert elem1.attrib == elem1_again.attrib

    def test_complex_search_patterns(self, attributes):
        """Test complex search patterns"""
        # Search for JSON-containing attributes
        json_attrs = []
        for key, value in attributes.items():
            try:
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    json.loads(value)
                    json_attrs.append(key)
            except:
                pass

        assert "data-config" in json_attrs
        assert "data-items" in json_attrs
        assert "data-nested" in json_attrs

    def test_attribute_filtering(self, attributes):
        """Test filtering attributes by patterns"""
        # Get all data-* attributes
        data_attrs = {k: v for k, v in attributes.items() if k.startswith("data-")}
        assert len(data_attrs) > 5
        assert "data-config" in data_attrs
        assert "data-items" in data_attrs

        # Get all event handler attributes
        event_attrs = {k: v for k, v in attributes.items() if k.startswith("on")}
        assert "onclick" in event_attrs

    def test_performance_with_many_attributes(self):
        """Test performance with elements having many attributes"""
        # Create an element with many attributes
        attrs_list = [f'data-attr{i}="value{i}"' for i in range(100)]
        html = f'<div id="test" {" ".join(attrs_list)}>Content</div>'

        page = Selector(html)
        element = page.css("#test")[0]
        attribs = element.attrib

        # Should handle many attributes efficiently
        assert len(attribs) == 101  # id + 100 data attributes

        # Search should still work efficiently
        results = list(attribs.search_values("value50", partial=False))
        assert len(results) == 1

    def test_unicode_attributes(self):
        """Test handling of Unicode in attributes"""
        html = """
        <div id="unicode-test"
             data-emoji="😀🎉"
             data-chinese="你好世界"
             data-arabic="مرحبا بالعالم"
             data-special="café naïve">
        </div>
        """

        page = Selector(html)
        attrs = page.css("#unicode-test")[0].attrib

        assert attrs["data-emoji"] == "😀🎉"
        assert attrs["data-chinese"] == "你好世界"
        assert attrs["data-arabic"] == "مرحبا بالعالم"
        assert attrs["data-special"] == "café naïve"

        # Search with Unicode
        results = list(attrs.search_values("你好", partial=True))
        assert len(results) == 1

    def test_malformed_attributes(self):
        """Test handling of malformed attributes"""
        # Various malformed HTML scenarios
        test_cases = [
            '<div id="test" class=>Content</div>',  # Empty attribute value
            '<div id="test" class>Content</div>',  # No attribute value
            '<div id="test" data-"invalid"="value">Content</div>',  # Invalid attribute name
            '<div id=test class=no-quotes>Content</div>',  # Unquoted values
        ]

        for html in test_cases:
            try:
                page = Selector(html)
                if page.css("div"):
                    attrs = page.css("div")[0].attrib
                    # Should handle gracefully without crashing
                    assert isinstance(attrs, AttributesHandler)
            except:
                # Some malformed HTML might not parse at all
                pass
