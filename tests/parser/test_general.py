
import pickle
import unittest
from scrapling import Adaptor
from cssselect import SelectorError, SelectorSyntaxError


class TestParser(unittest.TestCase):
    def setUp(self):
        self.html = '''
        <html>
        <head>
            <title>Complex Web Page</title>
            <style>
                .hidden { display: none; }
            </style>
        </head>
        <body>
            <header>
                <nav>
                    <ul>
                        <li><a href="#home">Home</a></li>
                        <li><a href="#about">About</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </nav>
            </header>
            <main>
                <section id="products" schema='{"jsonable": "data"}'>
                    <h2>Products</h2>
                    <div class="product-list">
                        <article class="product" data-id="1">
                            <h3>Product 1</h3>
                            <p class="description">This is product 1</p>
                            <span class="price">$10.99</span>
                            <div class="hidden stock">In stock: 5</div>
                        </article>
                        <article class="product" data-id="2">
                            <h3>Product 2</h3>
                            <p class="description">This is product 2</p>
                            <span class="price">$20.99</span>
                            <div class="hidden stock">In stock: 3</div>
                        </article>
                        <article class="product" data-id="3">
                            <h3>Product 3</h3>
                            <p class="description">This is product 3</p>
                            <span class="price">$15.99</span>
                            <div class="hidden stock">Out of stock</div>
                        </article>
                    </div>
                </section>
                <section id="reviews">
                    <h2>Customer Reviews</h2>
                    <div class="review-list">
                        <div class="review" data-rating="5">
                            <p class="review-text">Great product!</p>
                            <span class="reviewer">John Doe</span>
                        </div>
                        <div class="review" data-rating="4">
                            <p class="review-text">Good value for money.</p>
                            <span class="reviewer">Jane Smith</span>
                        </div>
                    </div>
                </section>
            </main>
            <footer>
                <p>&copy; 2024 Our Company</p>
            </footer>
            <script id="page-data" type="application/json">
                {"lastUpdated": "2024-09-22T10:30:00Z", "totalProducts": 3}
            </script>
        </body>
        </html>
        '''
        self.page = Adaptor(self.html, auto_match=False, debug=False)

    def test_css_selector(self):
        """Test Selecting elements with complex CSS selectors"""
        elements = self.page.css('main #products .product-list article.product')
        self.assertEqual(len(elements), 3)

        in_stock_products = self.page.css(
            'main #products .product-list article.product:not(:contains("Out of stock"))')
        self.assertEqual(len(in_stock_products), 2)

    def test_xpath_selector(self):
        """Test Selecting elements with Complex XPath selectors"""
        reviews = self.page.xpath(
            '//section[@id="reviews"]//div[contains(@class, "review") and @data-rating >= 4]'
        )
        self.assertEqual(len(reviews), 2)

        high_priced_products = self.page.xpath(
            '//article[contains(@class, "product")]'
            '[number(translate(substring-after(.//span[@class="price"], "$"), ",", "")) > 15]'
        )
        self.assertEqual(len(high_priced_products), 2)

    def test_find_by_text(self):
        """Test Selecting elements with Text matching"""
        stock_info = self.page.find_by_regex(r'In stock: \d+', first_match=False)
        self.assertEqual(len(stock_info), 2)

        stock_info = self.page.find_by_regex(r'In stock: \d+', first_match=True, case_sensitive=True)
        self.assertEqual(stock_info.text, 'In stock: 5')

        stock_info = self.page.find_by_text(r'In stock:', partial=True, first_match=False)
        self.assertEqual(len(stock_info), 2)

        out_of_stock = self.page.find_by_text('Out of stock', partial=False, first_match=False)
        self.assertEqual(len(out_of_stock), 1)

    def test_find_similar_elements(self):
        """Test Finding similar elements of an element"""
        first_product = self.page.css_first('.product')
        similar_products = first_product.find_similar()
        self.assertEqual(len(similar_products), 2)

        first_review = self.page.find('div', class_='review')
        similar_high_rated_reviews = [
            review
            for review in first_review.find_similar()
            if int(review.attrib.get('data-rating', 0)) >= 4
        ]
        self.assertEqual(len(similar_high_rated_reviews), 1)

    def test_expected_errors(self):
        """Test errors that should raised if it does"""
        with self.assertRaises(ValueError):
            _ = Adaptor(auto_match=False)

        with self.assertRaises(TypeError):
            _ = Adaptor(root="ayo", auto_match=False)

        with self.assertRaises(TypeError):
            _ = Adaptor(text=1, auto_match=False)

        with self.assertRaises(TypeError):
            _ = Adaptor(body=1, auto_match=False)

        with self.assertRaises(ValueError):
            _ = Adaptor(self.html, storage=object, auto_match=True)

    def test_pickleable(self):
        """Test that objects aren't pickleable"""
        table = self.page.css('.product-list')[0]
        with self.assertRaises(TypeError):  # Adaptors
            pickle.dumps(table)

        with self.assertRaises(TypeError):  # Adaptor
            pickle.dumps(table[0])

    def test_overridden(self):
        """Test overridden functions"""
        table = self.page.css('.product-list')[0]
        self.assertTrue(issubclass(type(table.__str__()), str))
        self.assertTrue(issubclass(type(table.__repr__()), str))
        self.assertTrue(issubclass(type(table.attrib.__str__()), str))
        self.assertTrue(issubclass(type(table.attrib.__repr__()), str))

    def test_bad_selector(self):
        """Test object can handle bad selector"""
        with self.assertRaises((SelectorError, SelectorSyntaxError,)):
            self.page.css('4 ayo')

        with self.assertRaises((SelectorError, SelectorSyntaxError,)):
            self.page.xpath('4 ayo')

    def test_selectors_generation(self):
        """Try to create selectors for all elements in the page"""
        def _traverse(element: Adaptor):
            self.assertTrue(type(element.generate_css_selector) is str)
            self.assertTrue(type(element.generate_xpath_selector) is str)
            for branch in element.children:
                _traverse(branch)

        _traverse(self.page)

    def test_getting_all_text(self):
        """Test getting all text"""
        self.assertNotEqual(self.page.get_all_text(), '')

    def test_element_navigation(self):
        """Test moving in the page from selected element"""
        table = self.page.css('.product-list')[0]

        self.assertIsNot(table.path, [])
        self.assertNotEqual(table.html_content, '')
        self.assertNotEqual(table.prettify(), '')

        parent = table.parent
        self.assertEqual(parent.attrib['id'], 'products')

        children = table.children
        self.assertEqual(len(children), 3)

        parent_siblings = parent.siblings
        self.assertEqual(len(parent_siblings), 1)

        child = table.find({'data-id': "1"})
        next_element = child.next
        self.assertEqual(next_element.attrib['data-id'], '2')

        prev_element = next_element.previous
        self.assertEqual(prev_element.tag, child.tag)

        all_prices = self.page.css('.price')
        products_with_prices = [
            price.find_ancestor(lambda p: p.has_class('product'))
            for price in all_prices
        ]
        self.assertEqual(len(products_with_prices), 3)

    def test_empty_return(self):
        """Test cases where functions shouldn't have results"""
        test_html = """
        <html>
            <span id="a"><a></a><!--comment--></span>
            <span id="b"><!--comment--><a></a></span>
        </html>"""
        soup = Adaptor(test_html, auto_match=False, keep_comments=False)
        html_tag = soup.css('html')[0]
        self.assertEqual(html_tag.path, [])
        self.assertEqual(html_tag.siblings, [])
        self.assertEqual(html_tag.parent, None)
        self.assertEqual(html_tag.find_ancestor(lambda e: e), None)

        self.assertEqual(soup.css('#a a')[0].next, None)
        self.assertEqual(soup.css('#b a')[0].previous, None)

    def test_text_to_json(self):
        """Test converting text to json"""
        script_content = self.page.css('#page-data::text')[0]
        self.assertTrue(issubclass(type(script_content.sort()), str))
        page_data = script_content.json()
        self.assertEqual(page_data['totalProducts'], 3)
        self.assertTrue('lastUpdated' in page_data)

    def test_regex_on_text(self):
        """Test doing regex on a selected text"""
        element = self.page.css('[data-id="1"] .price')[0]
        match = element.re_first(r'[\.\d]+')
        self.assertEqual(match, '10.99')
        match = element.text.re(r'(\d+)', replace_entities=False)
        self.assertEqual(len(match), 2)

    def test_attribute_operations(self):
        """Test operations on elements attributes"""
        products = self.page.css('.product')
        product_ids = [product.attrib['data-id'] for product in products]
        self.assertEqual(product_ids, ['1', '2', '3'])
        self.assertTrue('data-id' in products[0].attrib)

        reviews = self.page.css('.review')
        review_ratings = [int(review.attrib['data-rating']) for review in reviews]
        self.assertEqual(sum(review_ratings) / len(review_ratings), 4.5)

        key_value = list(products[0].attrib.search_values('1', partial=False))
        self.assertEqual(list(key_value[0].keys()), ['data-id'])

        key_value = list(products[0].attrib.search_values('1', partial=True))
        self.assertEqual(list(key_value[0].keys()), ['data-id'])

        attr_json = self.page.css_first('#products').attrib['schema'].json()
        self.assertEqual(attr_json, {'jsonable': 'data'})
        self.assertEqual(type(self.page.css('#products')[0].attrib.json_string), bytes)

    def test_performance(self):
        """Test parsing and selecting speed"""
        import time
        large_html = '<html><body>' + '<div class="item">' * 5000 + '</div>' * 5000 + '</body></html>'

        start_time = time.time()
        parsed = Adaptor(large_html, auto_match=False, debug=False)
        elements = parsed.css('.item')
        end_time = time.time()

        self.assertEqual(len(elements), 5000)
        # Converting 5000 elements to a class and doing operations on them will take time
        # Based on my tests with 100 runs, 1 loop each Scrapling (given the extra work/features) takes 10.4ms on average
        self.assertLess(end_time - start_time, 0.5)  # Locally I test on 0.1 but on GitHub actions with browsers and threading sometimes closing adds fractions of seconds


# Use `coverage run -m unittest --verbose tests/test_parser_functions.py` instead for the coverage report
# if __name__ == '__main__':
#     unittest.main(verbosity=2)
