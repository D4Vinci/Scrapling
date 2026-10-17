import pytest

from scrapling import Selector


@pytest.mark.parametrize("selection", ["css", "xpath"])
@pytest.mark.parametrize("full_path", [False, True])
@pytest.mark.parametrize(
    "html, target_css, expected_css, expected_xpath",
    [
        pytest.param(
            "<section><p>A</p><p>B</p></section>",
            "p:first-of-type",
            "body > section > p:nth-of-type(1)",
            "//body/section/p[1]",
            id="first-sibling",
        ),
        pytest.param(
            "<section><p>A</p><p>B</p></section>",
            "p:nth-of-type(2)",
            "body > section > p:nth-of-type(2)",
            "//body/section/p[2]",
            id="second-sibling",
        ),
        pytest.param(
            "<section><p>A</p></section><section><p>B</p></section>",
            "section:first-of-type > p",
            "body > section:nth-of-type(1) > p",
            "//body/section[1]/p",
            id="first-ancestor",
        ),
        pytest.param(
            "<section><p>A</p></section><section><p>B</p></section>",
            "section:nth-of-type(2) > p",
            "body > section:nth-of-type(2) > p",
            "//body/section[2]/p",
            id="second-ancestor",
        ),
        pytest.param(
            "<section><span>before</span><p>A</p><em>between</em><p>B</p></section>",
            "p:first-of-type",
            "body > section > p:nth-of-type(1)",
            "//body/section/p[1]",
            id="first-sibling-mixed-tags",
        ),
        pytest.param(
            "<section><span>before</span><p>A</p><em>between</em><p>B</p></section>",
            "p:nth-of-type(2)",
            "body > section > p:nth-of-type(2)",
            "//body/section/p[2]",
            id="second-sibling-mixed-tags",
        ),
        pytest.param(
            "<section><span>before</span><p>A</p><em>after</em></section>",
            "p",
            "body > section > p",
            "//body/section/p",
            id="unique-tag",
        ),
        pytest.param(
            "<section><p>A</p><p>B</p></section><section><p>C</p></section>",
            "section:first-of-type > p:first-of-type",
            "body > section:nth-of-type(1) > p:nth-of-type(1)",
            "//body/section[1]/p[1]",
            id="first-sibling-and-ancestor",
        ),
    ],
)
def test_generated_selectors_round_trip(html, target_css, expected_css, expected_xpath, selection, full_path):
    """Generated paths uniquely select the original element at every level."""
    page = Selector(f"<html><body>{html}</body></html>")
    target = page.css(target_css).first
    property_name = f"generate_{'full_' if full_path else ''}{selection}_selector"

    generated = getattr(target, property_name)
    assert generated == (expected_css if selection == "css" else expected_xpath)
    matches = getattr(page, selection)(generated)
    assert len(matches) == 1
    assert matches.first._root is target._root


@pytest.mark.parametrize("selection", ["css", "xpath"])
@pytest.mark.parametrize("full_path", [False, True])
@pytest.mark.parametrize("target_css", ["#target", "#target > p:first-of-type"])
def test_generated_selectors_keep_id_shortcuts(selection, full_path, target_css):
    """IDs still terminate short paths and remain present once in full paths."""
    page = Selector('<html><body><section id="target"><p>A</p><p>B</p></section><section>C</section></body></html>')
    target = page.css(target_css).first
    property_name = f"generate_{'full_' if full_path else ''}{selection}_selector"

    if selection == "css":
        expected = "body > #target" if full_path else "#target"
        if target.tag == "p":
            expected += " > p:nth-of-type(1)"
    else:
        expected = "//body/*[@id='target']" if full_path else "//*[@id='target']"
        if target.tag == "p":
            expected += "/p[1]"

    generated = getattr(target, property_name)
    assert generated == expected
    matches = getattr(page, selection)(generated)
    assert len(matches) == 1
    assert matches.first._root is target._root
