"""
Tests for Selector.iterancestors() and Selector.find_ancestor() methods.
Target file: tests/parser/test_general.py (append to TestElementNavigation class)
"""
import pytest
from scrapling import Selector


@pytest.fixture
def nested_page():
    html = """
    <html><body>
        <div id="level1">
            <section id="level2" class="wrapper">
                <article id="level3" class="card">
                    <p id="level4"><span id="target">deep text</span></p>
                </article>
            </section>
        </div>
    </body></html>
    """
    return Selector(html, adaptive=False)


class TestAncestorNavigation:
    def test_iterancestors_returns_all_ancestors(self, nested_page):
        """iterancestors() should yield every ancestor up to <html>"""
        target = nested_page.css("#target")[0]
        ancestors = list(target.iterancestors())
        ancestor_tags = [a.tag for a in ancestors]
        assert ancestors[0].attrib.get("id") == "level4"
        # Expected order: p → article → section → div → body → html
        assert ancestor_tags[:4] == ["p", "article", "section", "div"]
        assert "body" in ancestor_tags
        assert "html" in ancestor_tags

    def test_find_ancestor_returns_first_match(self, nested_page):
        """find_ancestor() should return the closest ancestor matching the predicate"""
        target = nested_page.css("#target")[0]
        # Looking for the nearest ancestor with class "card"
        result = target.find_ancestor(lambda el: el.has_class("card"))
        assert result is not None
        assert result.attrib.get("id") == "level3"

    def test_find_ancestor_returns_none_when_not_found(self, nested_page):
        """find_ancestor() should return None if no ancestor matches"""
        target = nested_page.css("#target")[0]
        result = target.find_ancestor(lambda el: el.has_class("nonexistent-class"))
        assert result is None

    def test_iterancestors_on_text_node_is_empty(self, nested_page):
        """iterancestors() on a text node should yield nothing (not raise)"""
        text_node = nested_page.css("#target::text")[0]
        ancestors = list(text_node.iterancestors())
        assert ancestors == []

    def test_find_ancestor_on_root_element_returns_none(self, nested_page):
        """find_ancestor() on the root <html> element should return None gracefully"""
        # html element has no ancestors
        html_el = nested_page.css("html")[0]
        result = html_el.find_ancestor(lambda el: True)
        assert result is None
