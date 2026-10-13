"""HTML attribute names need literal matching rather than XML namespace lookup."""

import pytest

from scrapling import Selector


@pytest.mark.parametrize("attribute", ["xlink:href", "wire:model", "1custom"])
def test_attr_pseudo_element_extracts_literal_html_name(attribute: str) -> None:
    """SVG/framework attributes remain ordinary names in an HTML document."""
    page = Selector(f'<div {attribute}="value"></div>')

    assert page.css(f'div::attr("{attribute}")').getall() == ["value"]


def test_attr_pseudo_element_keeps_regular_and_wildcard_extraction() -> None:
    """Literal-name handling must preserve existing extraction contracts."""
    page = Selector('<a href="/target" title="Title"></a>')

    assert page.css("a::attr(href)").getall() == ["/target"]
    assert page.css('a::attr("*")').getall() == ["/target", "Title"]
