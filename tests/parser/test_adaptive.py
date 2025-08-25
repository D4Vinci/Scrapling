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
