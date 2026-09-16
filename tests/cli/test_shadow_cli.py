from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from scrapling.cli import main
from scrapling.parser import Selector


@pytest.mark.parametrize(("command", "fetcher"), [("fetch", "DynamicFetcher"), ("stealthy-fetch", "StealthyFetcher")])
@pytest.mark.parametrize(
    ("flags", "enabled"), [([], False), (["--pierce-shadow"], True), (["--no-pierce-shadow"], False)]
)
def test_shadow_option_reaches_fetcher(
    tmp_path: Path, command: str, fetcher: str, flags: list[str], enabled: bool
) -> None:
    output = tmp_path / "page.txt"
    with patch(f"scrapling.fetchers.{fetcher}.fetch", return_value=Selector("<p>Content</p>")) as fetch:
        result = CliRunner().invoke(main, ["extract", command, "https://example.com", str(output), *flags])
    assert result.exit_code == 0, result.output
    assert fetch.call_args.kwargs["pierce_shadow"] is enabled
    assert output.read_text() == "Content"


@pytest.mark.parametrize("command", ["fetch", "stealthy-fetch"])
def test_shadow_option_in_browser_help(command: str) -> None:
    result = CliRunner().invoke(main, ["extract", command, "--help"])
    assert result.exit_code == 0
    assert "--pierce-shadow / --no-pierce-shadow" in result.output


@pytest.mark.parametrize("command", ["get", "post", "put", "delete"])
def test_shadow_option_not_in_http_help(command: str) -> None:
    result = CliRunner().invoke(main, ["extract", command, "--help"])
    assert result.exit_code == 0
    assert "pierce-shadow" not in result.output
