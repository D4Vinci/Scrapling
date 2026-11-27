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

    def test_relocate_accepts_selector_when_called_on_subclass(self):
        """`relocate()` on a `Selector` subclass (like the fetchers' `Response`) must accept a
        plain `Selector` as the element, not only an instance of the receiver's own class."""

        class Page(Selector):
            pass

        html = "<html><body><div><h1>Title</h1><p>Body text</p></div></body></html>"
        heading = Selector(html).css("h1")[0]

        # Used to raise `KeyError: 'tag'` because the element was never converted to a dict.
        relocated = Page(html).relocate(heading, selector_type=True)

        assert len(relocated) == 1
        assert relocated[0].tag == "h1"
        assert relocated[0].text == "Title"

        # The reverse direction (plain receiver, subclass element) keeps working.
        relocated = Selector(html).relocate(Page(html).css("h1")[0], selector_type=True)
        assert relocated[0].text == "Title"
