from scrapling import Selector


class TestJsonLdExtraction:
    """Test suite for JSON-LD and Schema.org extraction and normalization."""

    def test_single_json_ld_object(self):
        """Test single JSON-LD object is extracted cleanly."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Wireless Headphones",
                "price": "99.99"
            }
            </script>
        </head>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 1
        assert schemas[0]["@type"] == "Product"
        assert schemas[0]["name"] == "Wireless Headphones"
        assert schemas[0]["price"] == "99.99"

    def test_multiple_script_tags(self):
        """Test multiple script tags across the document are extracted in order."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "Organization", "name": "AudioCorp"}
            </script>
        </head>
        <body>
            <script type="application/ld+json">
            {"@context": "https://schema.org", "@type": "Product", "name": "Headphones"}
            </script>
        </body>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 2
        assert schemas[0]["@type"] == "Organization"
        assert schemas[1]["@type"] == "Product"

    def test_json_array_of_objects(self):
        """Test JSON-LD containing an array of objects is unpacked into top-level entries."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            [
                {"@context": "https://schema.org", "@type": "BreadcrumbList"},
                {"@context": "https://schema.org", "@type": "Product", "name": "Item"}
            ]
            </script>
        </head>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 2
        assert schemas[0]["@type"] == "BreadcrumbList"
        assert schemas[1]["@type"] == "Product"

    def test_top_level_graph_wrapper(self):
        """Test top-level @graph unwraps nodes and propagates parent @context."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@graph": [
                    {"@type": "Organization", "@id": "#corp"},
                    {"@type": "WebSite", "@id": "#site"}
                ]
            }
            </script>
        </head>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 2
        assert schemas[0]["@type"] == "Organization"
        assert schemas[0]["@context"] == "https://schema.org"
        assert schemas[0]["@id"] == "#corp"
        assert schemas[1]["@type"] == "WebSite"
        assert schemas[1]["@context"] == "https://schema.org"

    def test_graph_node_retains_own_context(self):
        """Test a node inside @graph with its own @context is not overwritten."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@graph": [
                    {"@context": "https://example.com/custom", "@type": "CustomEntity"}
                ]
            }
            </script>
        </head>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 1
        assert schemas[0]["@context"] == "https://example.com/custom"

    def test_nested_properties_preserved_intact(self):
        """Test inner properties (like offers inside Product) are NOT destructively flattened."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Shoes",
                "offers": {
                    "@type": "Offer",
                    "price": "49.99",
                    "seller": {"@type": "Organization", "name": "ShoeStore"}
                }
            }
            </script>
        </head>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 1
        product = schemas[0]
        assert product["@type"] == "Product"
        assert isinstance(product["offers"], dict)
        assert product["offers"]["@type"] == "Offer"
        assert product["offers"]["seller"]["name"] == "ShoeStore"

    def test_type_as_string_matching(self):
        """Test find_schema with standard string @type."""
        html = """
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": "Article", "headline": "Test"}
        </script>
        """
        page = Selector(html)
        article = page.find_schema("Article")
        assert article is not None
        assert article["headline"] == "Test"
        assert page.find_schema("Product") is None

    def test_type_as_list_matching(self):
        """Test find_schema matches when @type is an array of types."""
        html = """
        <script type="application/ld+json">
        {"@context": "https://schema.org", "@type": ["Restaurant", "LocalBusiness"], "name": "Bistro"}
        </script>
        """
        page = Selector(html)
        assert page.find_schema("Restaurant") is not None
        assert page.find_schema("Restaurant")["name"] == "Bistro"
        assert page.find_schema("LocalBusiness") is not None
        assert page.find_schema("Hotel") is None

    def test_schema_org_uri_normalization(self):
        """Test matching against full schema.org URIs (https and http)."""
        html = """
        <script type="application/ld+json">
        {"@type": "https://schema.org/Product", "name": "Item 1"}
        </script>
        <script type="application/ld+json">
        {"@type": "http://schema.org/Recipe", "name": "Cake"}
        </script>
        """
        page = Selector(html)
        assert page.find_schema("Product") is not None
        assert page.find_schema("Product")["name"] == "Item 1"
        assert page.find_schema("Recipe") is not None
        assert page.find_schema("Recipe")["name"] == "Cake"
        # User query can also be a full URI
        assert page.find_schema("https://schema.org/Product")["name"] == "Item 1"

    def test_case_insensitive_matching(self):
        """Test schema type matching is case-insensitive."""
        html = """
        <script type="application/ld+json">
        {"@type": "Product", "name": "Gadget"}
        </script>
        """
        page = Selector(html)
        assert page.find_schema("product") is not None
        assert page.find_schema("PRODUCT") is not None
        assert page.find_schema("pRoDuCt")["name"] == "Gadget"

    def test_mixed_valid_and_invalid_scripts(self):
        """Test invalid JSON is skipped gracefully with debug log while valid is parsed."""
        html = """
        <html>
        <head>
            <script type="application/ld+json">
            {INVALID JSON HERE, NOT VALID
            </script>
            <script type="application/ld+json">
            {"@type": "Book", "title": "Good Book"}
            </script>
        </head>
        </html>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 1
        assert schemas[0]["@type"] == "Book"
        assert schemas[0]["title"] == "Good Book"

    def test_empty_script_tag(self):
        """Test empty script tag returns empty list without error."""
        html = '<script type="application/ld+json"></script>'
        page = Selector(html)
        assert page.json_ld == []

    def test_whitespace_only_script_tag(self):
        """Test whitespace-only script tag returns empty list without error."""
        html = '<script type="application/ld+json">   \n\t  \n </script>'
        page = Selector(html)
        assert page.json_ld == []

    def test_html_comment_wrapper(self):
        """Test script content wrapped in HTML comments is parsed correctly."""
        html = """
        <script type="application/ld+json">
        <!--
        {"@context": "https://schema.org", "@type": "Event", "name": "Concert"}
        -->
        </script>
        """
        page = Selector(html)
        assert len(page.json_ld) == 1
        assert page.find_schema("Event")["name"] == "Concert"

    def test_cdata_wrappers(self):
        """Test script content wrapped in CDATA blocks is parsed correctly."""
        html = """
        <script type="application/ld+json">
        //<![CDATA[
        {"@type": "Place", "name": "Paris"}
        //]]>
        </script>
        <script type="application/ld+json">
        <![CDATA[
        {"@type": "City", "name": "Rome"}
        ]]>
        </script>
        """
        page = Selector(html)
        assert len(page.json_ld) == 2
        assert page.find_schema("Place")["name"] == "Paris"
        assert page.find_schema("City")["name"] == "Rome"

    def test_non_schema_org_vocabulary(self):
        """Test non-Schema.org JSON-LD vocabularies are preserved without rejection."""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "@type": "Person",
            "name": "Alice"
        }
        </script>
        """
        page = Selector(html)
        schemas = page.json_ld
        assert len(schemas) == 1
        assert schemas[0]["@context"] == "https://www.w3.org/ns/activitystreams"
        assert schemas[0]["name"] == "Alice"
        assert page.find_schema("Person")["name"] == "Alice"

    def test_no_json_ld_present(self):
        """Test page with no JSON-LD returns empty list and None for find."""
        html = "<html><body><h1>Hello World</h1></body></html>"
        page = Selector(html)
        assert page.json_ld == []
        assert page.find_schema("Product") is None
        assert page.find_all_schemas("Product") == []
        assert page.find_schema() is None
        assert page.find_all_schemas() == []

    def test_first_match_and_find_all_behavior(self):
        """Test duplicate types: find_schema returns first match, find_all_schemas returns all."""
        html = """
        <script type="application/ld+json">
        {"@type": "Product", "name": "Product 1"}
        </script>
        <script type="application/ld+json">
        {"@type": "Product", "name": "Product 2"}
        </script>
        <script type="application/ld+json">
        {"@type": "Product", "name": "Product 3"}
        </script>
        """
        page = Selector(html)
        # find_schema returns first
        first = page.find_schema("Product")
        assert first is not None
        assert first["name"] == "Product 1"

        # find_all_schemas returns all 3 in order
        all_products = page.find_all_schemas("Product")
        assert len(all_products) == 3
        assert [p["name"] for p in all_products] == ["Product 1", "Product 2", "Product 3"]

    def test_empty_type_argument_behavior(self):
        """Test passing no type to find_schema returns first available schema."""
        html = """
        <script type="application/ld+json">
        {"@type": "First", "val": 1}
        </script>
        <script type="application/ld+json">
        {"@type": "Second", "val": 2}
        </script>
        """
        page = Selector(html)
        assert page.find_schema()["val"] == 1
        assert len(page.find_all_schemas()) == 2

    def test_script_with_parameters_in_type_attribute(self):
        """Test script tags with charset or other attributes in type."""
        html = """
        <script type="application/ld+json; charset=utf-8">
        {"@type": "NewsArticle", "headline": "Headline"}
        </script>
        """
        page = Selector(html)
        assert page.find_schema("NewsArticle")["headline"] == "Headline"
