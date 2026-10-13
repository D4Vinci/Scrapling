"""Text searches should normalize the query and candidate consistently."""

import pytest

from scrapling import Selector


@pytest.mark.parametrize("query", ["  Hello   World  ", "Hello\n\tWorld"])
@pytest.mark.parametrize("partial", [False, True])
def test_clean_match_normalizes_query(query: str, partial: bool) -> None:
    """Copied multiline text should find the same element as a clean query."""
    page = Selector("<div><p>Hello World</p><p>Other</p></div>")

    match = page.find_by_text(query, clean_match=True, partial=partial)

    assert match.tag == "p"
    assert match.text == "Hello World"


def test_literal_match_keeps_query_whitespace() -> None:
    """Opting out of normalization still requires literal whitespace."""
    page = Selector("<div><p>Hello World</p><p>Hello  World</p></div>")

    assert page.find_by_text("Hello  World", clean_match=False).text == "Hello  World"
    assert page.find_by_text(" Hello World ", clean_match=False, first_match=False) == []
