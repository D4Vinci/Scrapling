"""
Tests for Selector.find_similar() with non-default parameters.
Target file: tests/parser/test_general.py (append to TestSimilarElements class)
"""

import pytest
from scrapling import Selector


@pytest.fixture
def product_page():
    html = """
    <html><body>
        <div class="product-list">
            <div class="product" data-category="fruit" data-price="10">
                <span class="name">Apple</span>
            </div>
            <div class="product" data-category="fruit" data-price="5">
                <span class="name">Banana</span>
            </div>
            <div class="product" data-category="veggie" data-price="3">
                <span class="name">Carrot</span>
            </div>
            <!-- Structurally similar but different tag - should NOT be found -->
            <section class="product" data-category="fruit" data-price="8">
                <span class="name">Grape</span>
            </section>
        </div>
    </body></html>
    """
    return Selector(html, adaptive=False)


class TestFindSimilarAdvanced:
    def test_find_similar_default_finds_same_tag_siblings(self, product_page):
        """find_similar() with defaults should find div.product siblings, not the section"""
        first = product_page.css("div.product")[0]
        similar = first.find_similar()
        tags = [el.tag for el in similar]
        assert all(t == "div" for t in tags), "Should only return <div> elements"
        assert len(similar) == 2  # Banana and Carrot, not Grape (section)

    def test_find_similar_high_threshold_filters_more(self, product_page):
        """A higher similarity_threshold should return fewer (or equal) results"""
        first = product_page.css("div.product")[0]
        low_threshold = first.find_similar(similarity_threshold=0.1)
        high_threshold = first.find_similar(similarity_threshold=0.9)
        assert len(high_threshold) <= len(low_threshold)

    def test_find_similar_match_text_excludes_different_text(self, product_page):
        """match_text=True should factor in text content during similarity scoring"""
        first = product_page.css("div.product")[0]  # Apple
        # With match_text=True and a high threshold, "Apple" vs "Banana"/"Carrot" text
        # should reduce similarity scores - result count may drop
        with_text = first.find_similar(similarity_threshold=0.8, match_text=True)
        without_text = first.find_similar(similarity_threshold=0.8, match_text=False)
        # match_text=True is stricter when text differs, so result should be <= without_text
        assert len(with_text) <= len(without_text)

    def test_find_similar_ignore_attributes_affects_matching(self, product_page):
        """Ignoring data-price should make more elements qualify as similar"""
        first = product_page.css("div.product")[0]
        # Ignore both data-price and data-category → only class matters → all 3 divs match
        ignore_all_data = first.find_similar(
            similarity_threshold=0.2, ignore_attributes=["data-price", "data-category"]
        )
        # Ignore nothing → data-category difference (fruit vs veggie) may reduce matches
        ignore_nothing = first.find_similar(similarity_threshold=0.9, ignore_attributes=[])
        assert len(ignore_all_data) >= len(ignore_nothing)

    def test_find_similar_on_text_node_returns_empty(self, product_page):
        """find_similar() on a text node should return empty Selectors without raising"""
        text_node = product_page.css(".name::text")[0]
        result = text_node.find_similar()
        assert len(result) == 0

    def test_find_similar_attribute_count_mismatch_scoring(self):
        """The similarity denominator uses max() of both attribute counts, so candidates
        with fewer attributes don't get inflated scores and candidates with extra
        attributes stay penalized."""
        html = """
        <html><body>
            <div class="cards">
                <div class="card" data-kind="primary" data-color="red" data-size="large">Alpha</div>
                <div class="card">Beta</div>
                <div class="card" data-kind="primary" data-color="red" data-size="large" data-id="x">Gamma</div>
                <div class="card" data-kind="primary" data-color="red" data-size="large">Delta</div>
            </div>
        </body></html>
        """
        page = Selector(html, adaptive=False)
        first = page.css("div.card")[0]  # Alpha

        similar = first.find_similar(similarity_threshold=0.9, ignore_attributes=[])
        texts = {el.text for el in similar}

        # An exact attribute match must pass
        assert "Delta" in texts
        # Beta matches 1 of Alpha's 4 attributes; the old denominator counted candidate
        # attributes only, inflating it to a perfect score (1.0 / 1)
        assert "Beta" not in texts
        # Gamma's extra attribute dilutes the score (4.0 / 5) - the intentional penalty
        assert "Gamma" not in texts
