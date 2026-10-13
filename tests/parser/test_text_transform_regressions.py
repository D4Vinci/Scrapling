"""String transformations must preserve the documented extraction API."""

import pytest

from scrapling import TextHandler


@pytest.mark.parametrize(
    ("method", "value"),
    [
        ("removeprefix", "Hello "),
        ("removesuffix", "World"),
        ("removeprefix", "absent"),
        ("removesuffix", "absent"),
    ],
)
def test_string_transform_keeps_extraction_methods(method: str, value: str) -> None:
    """Compare values with Python strings, then use the returned regex API."""
    source = "Hello World"
    result = getattr(TextHandler(source), method)(value)

    assert result == getattr(source, method)(value)
    assert isinstance(result, TextHandler)
    assert result.re(r"\S+", replace_entities=False) == result.split()
