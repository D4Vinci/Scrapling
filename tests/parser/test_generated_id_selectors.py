"""Generated selectors must round-trip valid HTML IDs containing punctuation."""

import pytest
from lxml.html import Element

from scrapling import Selector


IDENTIFIERS = [
    "product:42",
    "123item",
    "sale.item",
    "quote'item",
    "both'\"quotes",
    "a\\b",
    "end\\",
    "a\\\\b",
    "a\\'\"b",
    "a b",
    "a\nb",
    "-",
    "--a",
    "é",
    "🦊",
]


@pytest.mark.parametrize("identifier", IDENTIFIERS)
@pytest.mark.parametrize("full_path", [False, True])
def test_generated_css_id_selector_round_trip(identifier: str, full_path: bool) -> None:
    """CSS punctuation and leading digits in an ID are data, not syntax."""
    root = Element("html")
    body = Element("body")
    root.append(body)
    target = Element("p", id=identifier)
    body.append(target)
    page = Selector(root=root)
    selected = page.css("p").first

    generated = selected.generate_full_css_selector if full_path else selected.generate_css_selector

    assert [element._root for element in page.css(generated)] == [target]


@pytest.mark.parametrize("identifier", IDENTIFIERS)
@pytest.mark.parametrize("full_path", [False, True])
def test_generated_xpath_id_selector_round_trip(identifier: str, full_path: bool) -> None:
    """XPath ID predicates must quote values rather than interpolate syntax."""
    root = Element("html")
    body = Element("body")
    root.append(body)
    target = Element("p", id=identifier)
    body.append(target)
    page = Selector(root=root)
    selected = page.css("p").first

    generated = selected.generate_full_xpath_selector if full_path else selected.generate_xpath_selector

    assert [element._root for element in page.xpath(generated)] == [target]
