from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from scrapling.cli import main
from scrapling.parser import Selector


@pytest.mark.parametrize(
    ("extension", "expected"),
    [("md", "First\n\nSecond"), ("txt", "FirstSecond"), ("html", "<p>First</p><p></p><p>Second</p>")],
)
def test_cli_preserves_selected_blocks(tmp_path: Path, extension: str, expected: str) -> None:
    page = Selector("<html><body><p>First</p><p></p><p>Second</p></body></html>")
    output = tmp_path / f"output.{extension}"
    with patch("scrapling.fetchers.Fetcher.get", return_value=page):
        result = CliRunner().invoke(main, ["extract", "get", "https://example.com", str(output), "-s", "p"])
    assert result.exit_code == 0, result.output
    assert output.read_text(encoding="utf-8") == expected
