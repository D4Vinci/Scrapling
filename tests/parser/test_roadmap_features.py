import re

import pytest

from scrapling import Selector


class TestRoadmapFeatures:
    @pytest.fixture
    def roadmap_html(self):
        return """
        <html lang="en">
          <head>
            <title>Catalog</title>
            <meta name="description" content="Products page" />
            <link rel="canonical" href="/catalog" />
            <link rel="next" href="/catalog?page=3" />
            <script type="application/ld+json">
              {"@context":"https://schema.org","@type":"Product","name":"Widget"}
            </script>
            <meta property="og:title" content="Catalog OG" />
          </head>
          <body>
            <a href="/catalog?page=2" rel="next">Next</a>
            <a href="/catalog?page=4" class="pagination-next">Older Posts</a>
            <a href="/product/123-alpha" class="product-link">Alpha</a>
            <a href="/product/456-beta" class="product-link">Beta</a>
            <a href="/product/789-gamma" class="product-link">Gamma</a>
            <article itemscope itemtype="https://schema.org/Product">
              <span itemprop="name">Widget</span>
              <span itemprop="price">10</span>
            </article>
          </body>
        </html>
        """

    def test_detect_pagination_urls(self, roadmap_html):
        page = Selector(roadmap_html, url="https://example.com/catalog?page=1")
        urls = page.detect_pagination_urls()
        assert "https://example.com/catalog?page=2" in urls
        assert "https://example.com/catalog?page=3" in urls
        assert "https://example.com/catalog?page=4" in urls

    def test_detect_schemas(self, roadmap_html):
        page = Selector(roadmap_html, url="https://example.com/catalog?page=1")
        schemas = page.detect_schemas()
        sources = {item["source"] for item in schemas}
        assert "json-ld" in sources
        assert "microdata" in sources
        assert "open-graph" in sources

    def test_analyze(self, roadmap_html):
        page = Selector(roadmap_html, url="https://example.com/catalog?page=1")
        analysis = page.analyze()
        assert analysis["title"] == "Catalog"
        assert analysis["description"] == "Products page"
        assert analysis["canonical_url"] == "https://example.com/catalog"
        assert analysis["schema_count"] >= 2
        assert len(analysis["pagination_urls"]) >= 2

    def test_generate_regex_from_selectors(self, roadmap_html):
        page = Selector(roadmap_html, url="https://example.com/catalog?page=1")
        regex = page.css("a.product-link").generate_regex(attribute="href")
        assert re.search(regex, "/product/123-alpha")
        assert re.search(regex, "/product/456-beta")
        assert re.search(regex, "/product/789-gamma")

    def test_generate_regex_from_selector_helper(self, roadmap_html):
        page = Selector(roadmap_html, url="https://example.com/catalog?page=1")
        regex = page.generate_regex("a.product-link", attribute="href")
        assert re.search(regex, "/product/123-alpha")
