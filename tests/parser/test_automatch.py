import asyncio

import pytest

from scrapling import Adaptor


class TestParserAutoMatch:
    def test_element_relocation(self):
        """Test relocating element after structure change"""
        original_html = '''
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
                '''
        changed_html = '''
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
                '''

        old_page = Adaptor(original_html, url='example.com', auto_match=True)
        new_page = Adaptor(changed_html, url='example.com', auto_match=True)

        # 'p1' was used as ID and now it's not and all the path elements have changes
        # Also at the same time testing auto-match vs combined selectors
        _ = old_page.css('#p1, #p2', auto_save=True)[0]
        relocated = new_page.css('#p1', auto_match=True)

        assert relocated is not None
        assert relocated[0].attrib['data-id'] == 'p1'
        assert relocated[0].has_class('new-class')
        assert relocated[0].css('.new-description')[0].text == 'Description 1'

    @pytest.mark.asyncio
    async def test_element_relocation_async(self):
        """Test relocating element after structure change in async mode"""
        original_html = '''
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
                '''
        changed_html = '''
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
                '''

        # Simulate async operation
        await asyncio.sleep(0.1)  # Minimal async operation

        old_page = Adaptor(original_html, url='example.com', auto_match=True)
        new_page = Adaptor(changed_html, url='example.com', auto_match=True)

        # 'p1' was used as ID and now it's not and all the path elements have changes
        # Also at the same time testing auto-match vs combined selectors
        _ = old_page.css('#p1, #p2', auto_save=True)[0]
        relocated = new_page.css('#p1', auto_match=True)

        assert relocated is not None
        assert relocated[0].attrib['data-id'] == 'p1'
        assert relocated[0].has_class('new-class')
        assert relocated[0].css('.new-description')[0].text == 'Description 1'
