import asyncio

import pytest

from scrapling import Selector


class TestParserAdaptive:
    def test_element_relocation(self):
        """Test relocating element after structure change"""
        original_html = """
                <div class="container">
                    <section class="products">
                        <article class="product" id="p1">
                            <h3>Product 1</h3>
                            <p class="description">Description 1</p>
                        </article>
                        <article class="product" id="p2">
                            <h3>Product 2</h3>
                            <p class="description">Description 2</p>
                        </article>
                    </section>
                </div>
                """
        changed_html = """
                <div class="new-container">
                    <div class="product-wrapper">
                        <section class="products">
                            <article class="product new-class" data-id="p1">
                                <div class="product-info">
                                    <h3>Product 1</h3>
                                    <p class="new-description">Description 1</p>
                                </div>
                            </article>
                            <article class="product new-class" data-id="p2">
                                <div class="product-info">
                                    <h3>Product 2</h3>
                                    <p class="new-description">Description 2</p>
                                </div>
                            </article>
                        </section>
                    </div>
                </div>
                """

        old_page = Selector(original_html, url="example.com", adaptive=True)
        new_page = Selector(changed_html, url="example.com", adaptive=True)

        # 'p1' was used as ID and now it's not and all the path elements have changes
        # Also at the same time testing `adaptive` vs combined selectors
        _ = old_page.css("#p1, #p2", auto_save=True)[0]
        relocated = new_page.css("#p1", adaptive=True)

        assert relocated is not None
        assert relocated[0].attrib["data-id"] == "p1"
        assert relocated[0].has_class("new-class")
        assert relocated[0].css(".new-description")[0].text == "Description 1"

    def test_relocation_auto_save_no_match_above_threshold(self):
        """Adaptive relocation with `auto_save=True` must not crash when no element
        clears the `percentage` threshold (relocate() returns an empty list)."""
        original_html = """
                <div class="container">
                    <article class="product" id="target">
                        <h3>Widget</h3>
                        <p class="desc">A widget</p>
                    </article>
                </div>
                """
        # Unrelated structure so nothing can match a high threshold
        changed_html = "<html><body><span>totally unrelated content</span></body></html>"

        old_page = Selector(original_html, url="example.com", adaptive=True)
        new_page = Selector(changed_html, url="example.com", adaptive=True)

        old_page.css("#target", identifier="target", auto_save=True)

        # Before the fix this raised `IndexError: list index out of range` because the
        # guard checked `elements is not None` but relocate() returns [] (never None).
        result = new_page.css("#target", identifier="target", adaptive=True, auto_save=True, percentage=95)
        assert list(result) == []

    @pytest.mark.asyncio
    async def test_element_relocation_async(self):
        """Test relocating element after structure change in async mode"""
        original_html = """
                <div class="container">
                    <section class="products">
                        <article class="product" id="p1">
                            <h3>Product 1</h3>
                            <p class="description">Description 1</p>
                        </article>
                        <article class="product" id="p2">
                            <h3>Product 2</h3>
                            <p class="description">Description 2</p>
                        </article>
                    </section>
                </div>
                """
        changed_html = """
                <div class="new-container">
                    <div class="product-wrapper">
                        <section class="products">
                            <article class="product new-class" data-id="p1">
                                <div class="product-info">
                                    <h3>Product 1</h3>
                                    <p class="new-description">Description 1</p>
                                </div>
                            </article>
                            <article class="product new-class" data-id="p2">
                                <div class="product-info">
                                    <h3>Product 2</h3>
                                    <p class="new-description">Description 2</p>
                                </div>
                            </article>
                        </section>
                    </div>
                </div>
                """

        # Simulate async operation
        await asyncio.sleep(0.1)  # Minimal async operation

        old_page = Selector(original_html, url="example.com", adaptive=True)
        new_page = Selector(changed_html, url="example.com", adaptive=True)

        # 'p1' was used as ID and now it's not and all the path elements have changes
        # Also at the same time testing `adaptive` vs combined selectors
        _ = old_page.css("#p1, #p2", auto_save=True)[0]
        relocated = new_page.css("#p1", adaptive=True)

        assert relocated is not None
        assert relocated[0].attrib["data-id"] == "p1"
        assert relocated[0].has_class("new-class")
        assert relocated[0].css(".new-description")[0].text == "Description 1"


class TestAdaptiveTextFloor:
    """The opt-in text floor of `relocate`, and the default behaviour it leaves alone"""

    @staticmethod
    def page(names, cls="product", tclass="ptitle"):
        return (
            "<html><body>"
            + "".join(
                f'<div class="{cls}"><span class="{tclass}">{name}</span><span class="price">$9.99</span></div>'
                for name in names
            )
            + "</body></html>"
        )

    @staticmethod
    def gone_page(count):
        return (
            "<html><body>"
            + "".join(
                '<div class="item-x"><span class="x">n/a</span><span class="price">$9.99</span></div>'
                for _ in range(count)
            )
            + "</body></html>"
        )

    NAMES = [f"Widget-{i:02d}" for i in range(1, 13)]

    def test_returns_nothing_when_the_saved_target_is_gone(self):
        """A removed target yields no elements instead of the closest unrelated ones"""
        url = "https://shop.example.com/text-floor-gone"
        Selector(self.page(self.NAMES), url=url, adaptive=True).css(".product .ptitle", auto_save=True)

        found = Selector(self.gone_page(len(self.NAMES)), url=url, adaptive=True).css(
            ".product .ptitle", adaptive=True, min_text_similarity=0.2
        )

        assert len(found) == 0

    def test_keeps_the_match_when_the_title_was_renamed(self):
        """A text edit the caller accepts is not rejected by the floor"""
        url = "https://shop.example.com/text-floor-renamed"
        Selector(self.page(self.NAMES), url=url, adaptive=True).css(".product .ptitle", auto_save=True)

        renamed = self.page([f"Widget-{i:02d} (2026)" for i in range(1, 13)])
        found = Selector(renamed, url=url, adaptive=True).css(
            ".product .ptitle", adaptive=True, min_text_similarity=0.2
        )

        assert len(found) == 12
        assert found[0].text.strip() == "Widget-01 (2026)"

    def test_keeps_the_match_when_only_the_price_changed(self):
        """A price edit leaves the title element where it was"""
        url = "https://shop.example.com/text-floor-price"
        Selector(self.page(self.NAMES), url=url, adaptive=True).css(".product .ptitle", auto_save=True)

        repriced = self.page(self.NAMES).replace("$9.99", "$12.50")
        found = Selector(repriced, url=url, adaptive=True).css(
            ".product .ptitle", adaptive=True, min_text_similarity=0.2
        )

        assert len(found) == 12
        assert found[0].text.strip() == "Widget-01"

    def test_a_ratio_outside_zero_and_one_is_refused(self):
        """A floor above 1 filters every candidate, which reads as a removed target"""
        url = "https://shop.example.com/text-floor-range"
        Selector(self.page(self.NAMES), url=url, adaptive=True).css(".product .ptitle", auto_save=True)

        for ratio in (1.5, -0.1):
            with pytest.raises(ValueError):
                Selector(self.gone_page(len(self.NAMES)), url=url, adaptive=True).css(
                    ".product .ptitle", adaptive=True, min_text_similarity=ratio
                )

    def test_default_behaviour_is_unchanged(self):
        """Without the floor the structural score alone decides, and `percentage` stays the only threshold"""
        url = "https://shop.example.com/text-floor-default"
        Selector(self.page(self.NAMES), url=url, adaptive=True).css(".product .ptitle", auto_save=True)

        found = Selector(self.gone_page(len(self.NAMES)), url=url, adaptive=True).css(".product .ptitle", adaptive=True)

        assert len(found) == len(self.NAMES)
        assert found[0].attrib["class"] == "price"
