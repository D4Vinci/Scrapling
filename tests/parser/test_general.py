import pickle
import time

import pytest
from cssselect import SelectorError, SelectorSyntaxError

from scrapling import Adaptor


@pytest.fixture
def html_content():
    return '''
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


@pytest.fixture
def page(html_content):
    return Adaptor(html_content, auto_match=False)


# CSS Selector Tests
class TestCSSSelectors:
    def test_basic_product_selection(self, page):
        """Test selecting all product elements"""
        elements = page.css('main #products .product-list article.product')
        assert len(elements) == 3

    def test_in_stock_product_selection(self, page):
        """Test selecting in-stock products"""
        in_stock_products = page.css(
            'main #products .product-list article.product:not(:contains("Out of stock"))')
        assert len(in_stock_products) == 2


# XPath Selector Tests
class TestXPathSelectors:
    def test_high_rating_reviews(self, page):
        """Test selecting reviews with high ratings"""
        reviews = page.xpath(
            '//section[@id="reviews"]//div[contains(@class, "review") and @data-rating >= 4]'
        )
        assert len(reviews) == 2

    def test_high_priced_products(self, page):
        """Test selecting products above a certain price"""
        high_priced_products = page.xpath(
            '//article[contains(@class, "product")]'
            '[number(translate(substring-after(.//span[@class="price"], "$"), ",", "")) > 15]'
        )
        assert len(high_priced_products) == 2


# Text Matching Tests
class TestTextMatching:
    def test_regex_multiple_matches(self, page):
        """Test finding multiple matches with regex"""
        stock_info = page.find_by_regex(r'In stock: \d+', first_match=False)
        assert len(stock_info) == 2

    def test_regex_first_match(self, page):
        """Test finding the first match with regex"""
        stock_info = page.find_by_regex(r'In stock: \d+', first_match=True, case_sensitive=True)
        assert stock_info.text == 'In stock: 5'

    def test_partial_text_match(self, page):
        """Test finding elements with partial text match"""
        stock_info = page.find_by_text(r'In stock:', partial=True, first_match=False)
        assert len(stock_info) == 2

    def test_exact_text_match(self, page):
        """Test finding elements with exact text match"""
        out_of_stock = page.find_by_text('Out of stock', partial=False, first_match=False)
        assert len(out_of_stock) == 1


# Similar Elements Tests
class TestSimilarElements:
    def test_finding_similar_products(self, page):
        """Test finding similar product elements"""
        first_product = page.css_first('.product')
        similar_products = first_product.find_similar()
        assert len(similar_products) == 2

    def test_finding_similar_reviews(self, page):
        """Test finding similar review elements with additional filtering"""
        first_review = page.find('div', class_='review')
        similar_high_rated_reviews = [
            review
            for review in first_review.find_similar()
            if int(review.attrib.get('data-rating', 0)) >= 4
        ]
        assert len(similar_high_rated_reviews) == 1


# Error Handling Tests
class TestErrorHandling:
    def test_invalid_adaptor_initialization(self):
        """Test various invalid Adaptor initializations"""
        # No arguments
        with pytest.raises(ValueError):
            _ = Adaptor(auto_match=False)

        # Invalid argument types
        with pytest.raises(TypeError):
            _ = Adaptor(root="ayo", auto_match=False)

        with pytest.raises(TypeError):
            _ = Adaptor(text=1, auto_match=False)

        with pytest.raises(TypeError):
            _ = Adaptor(body=1, auto_match=False)

    def test_invalid_storage(self, page, html_content):
        """Test invalid storage parameter"""
        with pytest.raises(ValueError):
            _ = Adaptor(html_content, storage=object, auto_match=True)

    def test_bad_selectors(self, page):
        """Test handling of invalid selectors"""
        with pytest.raises((SelectorError, SelectorSyntaxError)):
            page.css('4 ayo')

        with pytest.raises((SelectorError, SelectorSyntaxError)):
            page.xpath('4 ayo')


# Pickling and Object Representation Tests
class TestPicklingAndRepresentation:
    def test_unpickleable_objects(self, page):
        """Test that Adaptor objects cannot be pickled"""
        table = page.css('.product-list')[0]
        with pytest.raises(TypeError):
            pickle.dumps(table)

        with pytest.raises(TypeError):
            pickle.dumps(table[0])

    def test_string_representations(self, page):
        """Test custom string representations of objects"""
        table = page.css('.product-list')[0]
        assert issubclass(type(table.__str__()), str)
        assert issubclass(type(table.__repr__()), str)
        assert issubclass(type(table.attrib.__str__()), str)
        assert issubclass(type(table.attrib.__repr__()), str)


# Navigation and Traversal Tests
class TestElementNavigation:
    def test_basic_navigation_properties(self, page):
        """Test basic navigation properties of elements"""
        table = page.css('.product-list')[0]
        assert table.path is not None
        assert table.html_content != ''
        assert table.prettify() != ''

    def test_parent_and_sibling_navigation(self, page):
        """Test parent and sibling navigation"""
        table = page.css('.product-list')[0]
        parent = table.parent
        assert parent.attrib['id'] == 'products'

        parent_siblings = parent.siblings
        assert len(parent_siblings) == 1

    def test_child_navigation(self, page):
        """Test child navigation"""
        table = page.css('.product-list')[0]
        children = table.children
        assert len(children) == 3

    def test_next_and_previous_navigation(self, page):
        """Test next and previous element navigation"""
        child = page.css('.product-list')[0].find({'data-id': "1"})
        next_element = child.next
        assert next_element.attrib['data-id'] == '2'

        prev_element = next_element.previous
        assert prev_element.tag == child.tag

    def test_ancestor_finding(self, page):
        """Test finding ancestors of elements"""
        all_prices = page.css('.price')
        products_with_prices = [
            price.find_ancestor(lambda p: p.has_class('product'))
            for price in all_prices
        ]
        assert len(products_with_prices) == 3


# JSON and Attribute Tests
class TestJSONAndAttributes:
    def test_json_conversion(self, page):
        """Test converting content to JSON"""
        script_content = page.css('#page-data::text')[0]
        assert issubclass(type(script_content.sort()), str)
        page_data = script_content.json()
        assert page_data['totalProducts'] == 3
        assert 'lastUpdated' in page_data

    def test_attribute_operations(self, page):
        """Test various attribute-related operations"""
        # Product ID extraction
        products = page.css('.product')
        product_ids = [product.attrib['data-id'] for product in products]
        assert product_ids == ['1', '2', '3']
        assert 'data-id' in products[0].attrib

        # Review rating calculations
        reviews = page.css('.review')
        review_ratings = [int(review.attrib['data-rating']) for review in reviews]
        assert sum(review_ratings) / len(review_ratings) == 4.5

        # Attribute searching
        key_value = list(products[0].attrib.search_values('1', partial=False))
        assert list(key_value[0].keys()) == ['data-id']

        key_value = list(products[0].attrib.search_values('1', partial=True))
        assert list(key_value[0].keys()) == ['data-id']

        # JSON attribute conversion
        attr_json = page.css_first('#products').attrib['schema'].json()
        assert attr_json == {'jsonable': 'data'}
        assert isinstance(page.css('#products')[0].attrib.json_string, bytes)


# Performance Test
def test_large_html_parsing_performance():
    """Test parsing and selecting performance on large HTML"""
    large_html = '<html><body>' + '<div class="item">' * 5000 + '</div>' * 5000 + '</body></html>'

    start_time = time.time()
    parsed = Adaptor(large_html, auto_match=False)
    elements = parsed.css('.item')
    end_time = time.time()

    assert len(elements) == 5000
    # Converting 5000 elements to a class and doing operations on them will take time
    # Based on my tests with 100 runs, 1 loop each Scrapling (given the extra work/features) takes 10.4ms on average
    assert end_time - start_time < 0.5  # Locally I test on 0.1 but on GitHub actions with browsers and threading sometimes closing adds fractions of seconds


# Selector Generation Test
def test_selectors_generation(page):
    """Try to create selectors for all elements in the page"""

    def _traverse(element: Adaptor):
        assert isinstance(element.generate_css_selector, str)
        assert isinstance(element.generate_xpath_selector, str)
        for branch in element.children:
            _traverse(branch)

    _traverse(page)


# Miscellaneous Tests
def test_getting_all_text(page):
    """Test getting all text from the page"""
    assert page.get_all_text() != ''


def test_regex_on_text(page):
    """Test regex operations on text"""
    element = page.css('[data-id="1"] .price')[0]
    match = element.re_first(r'[\.\d]+')
    assert match == '10.99'
    match = element.text.re(r'(\d+)', replace_entities=False)
    assert len(match) == 2
