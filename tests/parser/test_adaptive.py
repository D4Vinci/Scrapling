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
        result = new_page.css(
            "#target", identifier="target", adaptive=True, auto_save=True, percentage=95
        )
        assert list(result) == []

    def test_relocation_rejects_deleted_target(self):
        """A deleted target must relocate to nothing, not to structural look-alikes.

        Regression test for the adaptive matcher returning 12 wrong price spans
        (top score 69.32% on dev, 47.08% in the SoloSoft audit) after the saved
        titles were deleted from the page: the price spans share the tag, path,
        parent and siblings with the saved title, so they cleared the default
        40% threshold on structure alone. With the text anchor in place, a
        candidate sharing (almost) none of the saved text scores 0 and the
        call returns [] with a warning instead of confident garbage.
        """
        names = [f"Widget-{i:02d}" for i in range(1, 13)]
        url = "https://shop.example.com/list"

        def page(title_names, cls="product", tclass="ptitle"):
            return "<html><body>" + "".join(
                f'<div class="{cls}"><span class="{tclass}">{n}</span>'
                f'<span class="price">$9.99</span></div>'
                for n in title_names
            ) + "</body></html>"

        old_page = Selector(page(names), url=url, adaptive=True)
        assert len(old_page.css(".product .ptitle", auto_save=True)) == 12

        # Classes renamed -- the correct element must still be found.
        renamed_page = Selector(page(names, "item-x", "ttl"), url=url, adaptive=True)
        relocated = renamed_page.css(".product .ptitle", adaptive=True)
        assert len(relocated) == 1
        assert relocated[0].text == "Widget-01"

        # Titles deleted entirely -- nothing may be returned, not the prices.
        gone_html = (
            "<html><body>"
            + "".join(
                '<div class="item-x"><span class="x">n/a</span>'
                '<span class="price">$9.99</span></div>'
                for _ in names
            )
            + "</body></html>"
        )
        gone_page = Selector(gone_html, url=url, adaptive=True)
        assert list(gone_page.css(".product .ptitle", adaptive=True)) == []

    def test_relocation_finds_slightly_reworded_text(self):
        """A small text change must not veto the relocation.

        Guards the 0.2 text-ratio floor: "Widget-01" vs "Widget-01 (2026)"
        scores ~0.72, so the renamed element is still found.
        """
        names = [f"Widget-{i:02d}" for i in range(1, 13)]
        url = "https://shop.example.com/list"

        def page(title_names, cls="product", tclass="ptitle"):
            return "<html><body>" + "".join(
                f'<div class="{cls}"><span class="{tclass}">{n}</span>'
                f'<span class="price">$9.99</span></div>'
                for n in title_names
            ) + "</body></html>"

        old_page = Selector(page(names), url=url, adaptive=True)
        old_page.css(".product .ptitle", auto_save=True)

        reworded = [f"{name} (2026)" for name in names]
        new_page = Selector(page(reworded, "item-x", "ttl"), url=url, adaptive=True)
        relocated = new_page.css(".product .ptitle", adaptive=True)
        assert len(relocated) == 1
        assert relocated[0].text == "Widget-01 (2026)"

    def test_relocation_rejects_zero_overlap_reword(self):
        """A target whose identifying text was replaced wholesale must not
        relocate to the slot's new content.

        "Widget-01" vs "Zebra" shares almost no text (ratio ~0.14), so the
        text anchor vetoes the match and the call returns [] with a warning
        instead of presenting the new title as the old element.
        """
        names = [f"Widget-{i:02d}" for i in range(1, 13)]
        url = "https://shop.example.com/list"

        def page(title_names, cls="product", tclass="ptitle"):
            return "<html><body>" + "".join(
                f'<div class="{cls}"><span class="{tclass}">{n}</span>'
                f'<span class="price">$9.99</span></div>'
                for n in title_names
            ) + "</body></html>"

        old_page = Selector(page(names), url=url, adaptive=True)
        old_page.css(".product .ptitle", auto_save=True)

        new_page = Selector(page(["Zebra"] * 12, "item-x", "ttl"), url=url, adaptive=True)
        assert list(new_page.css(".product .ptitle", adaptive=True)) == []

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
