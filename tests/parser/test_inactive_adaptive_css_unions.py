"""Enabling adaptive support must not change ordinary CSS union semantics."""

from unittest.mock import Mock

import pytest

from scrapling import Selector
from scrapling.core.storage import StorageSystemMixin


@pytest.mark.parametrize("query", [".second, p", "p, .second", ".second, .first"])
def test_css_union_is_unique_and_in_document_order(query: str) -> None:
    """Overlapping and reversed groups still produce each DOM node once."""
    page = Selector(
        '<div><p class="first">One</p><p class="second">Two</p></div>',
        adaptive=True,
        _storage=Mock(spec=StorageSystemMixin),
    )

    assert page.css(query).getall() == [
        '<p class="first">One</p>',
        '<p class="second">Two</p>',
    ]


def test_css_text_union_keeps_distinct_nodes_in_document_order() -> None:
    """The same union contract applies to text-node selectors."""
    page = Selector(
        '<div><p class="first">One</p><p class="second">Two</p></div>',
        adaptive=True,
        _storage=Mock(spec=StorageSystemMixin),
    )

    assert page.css(".second::text, p::text").getall() == ["One", "Two"]
