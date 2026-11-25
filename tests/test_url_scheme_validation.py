from scrapling.parser import Selector
from scrapling.spiders.links import LinkExtractor


class TestLinkExtractorSchemeValidation:
    def test_file_scheme_is_rejected(self):
        html = '<html><body><a href="file:///etc/passwd">local</a></body></html>'
        page = Selector(content=html, url="https://example.com/")
        extractor = LinkExtractor()

        urls = extractor.extract(page)
        assert len(urls) == 0
        assert not any(url.startswith("file://") for url in urls)

    def test_mixed_schemes(self):
        html = (
            "<html><body>"
            '<a href="file:///etc/passwd">bad</a>'
            '<a href="http://example.com/page">http</a>'
            '<a href="https://example.com/good">good</a>'
            "</body></html>"
        )
        page = Selector(content=html, url="https://example.com/")
        extractor = LinkExtractor()

        urls = extractor.extract(page)
        assert urls == ["http://example.com/page", "https://example.com/good"]
        assert not any(url.startswith("file://") for url in urls)
