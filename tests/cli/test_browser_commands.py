from inspect import Parameter, signature
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from click.testing import CliRunner

from scrapling import cli
from scrapling.core.shell import CustomShell
from scrapling.core._shell_signatures import Signatures_map
from scrapling.engines._browsers._types import StealthSession
from scrapling.fetchers import StealthyFetcher
from scrapling.parser import Selector


@pytest.mark.parametrize(
    ("flags", "options"),
    [
        ([], {"block_webrtc": False, "solve_cloudflare": False, "allow_webgl": True, "hide_canvas": False}),
        (
            ["--block-webrtc", "--solve-cloudflare", "--block-webgl", "--hide-canvas"],
            {"block_webrtc": True, "solve_cloudflare": True, "allow_webgl": False, "hide_canvas": True},
        ),
        (
            ["--allow-webrtc", "--no-solve-cloudflare", "--allow-webgl", "--show-canvas"],
            {"block_webrtc": False, "solve_cloudflare": False, "allow_webgl": True, "hide_canvas": False},
        ),
    ],
)
def test_fetch_stealth_options(tmp_path: Path, flags: list[str], options: dict[str, bool]) -> None:
    with patch.object(StealthyFetcher, "fetch", return_value=Selector("<p>Content</p>")) as fetch:
        result = CliRunner().invoke(
            cli.main, ["extract", "fetch", "https://example.com", str(tmp_path / "page.txt"), *flags]
        )
    assert result.exit_code == 0, result.output
    assert options.items() <= fetch.call_args.kwargs.items()


def test_fetch_common_options(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SCRAPLING_EXECUTABLE_PATH", raising=False)
    output = tmp_path / "page.txt"
    with patch.object(StealthyFetcher, "fetch", return_value=Selector("<p>Content</p><b>Other</b>")) as fetch:
        result = CliRunner().invoke(
            cli.main,
            [
                "extract",
                "fetch",
                "https://example.com",
                str(output),
                "--no-headless",
                "--disable-resources",
                "--network-idle",
                "--pierce-shadow",
                "--timeout",
                "60000",
                "--wait",
                "50",
                "--css-selector",
                "p",
                "--wait-selector",
                "p",
                "--locale",
                "en-GB",
                "--real-chrome",
                "--proxy",
                "http://localhost:8080",
                "--extra-headers",
                "X-Test: value",
                "--executable-path",
                "/opt/chromium",
                "--dns-over-https",
                "--block-ads",
            ],
        )
    assert result.exit_code == 0, result.output
    fetch.assert_called_once_with(
        "https://example.com",
        headless=False,
        disable_resources=True,
        network_idle=True,
        pierce_shadow=True,
        timeout=60000,
        wait=50,
        wait_selector="p",
        locale="en-GB",
        real_chrome=True,
        proxy="http://localhost:8080",
        extra_headers={"X-Test": "value"},
        executable_path="/opt/chromium",
        dns_over_https=True,
        block_ads=True,
        block_webrtc=False,
        solve_cloudflare=False,
        allow_webgl=True,
        hide_canvas=False,
    )
    assert output.read_text() == "Content"


def test_browser_command_help_and_removed_command() -> None:
    runner = CliRunner()
    result = runner.invoke(cli.main, ["extract", "fetch", "--help"])
    assert result.exit_code == 0
    assert "StealthyFetcher" in result.output
    for option in ("--block-webrtc", "--solve-cloudflare", "--allow-webgl", "--hide-canvas"):
        assert option in result.output
    result = runner.invoke(cli.main, ["extract", "stealthy-fetch", "--help"])
    assert result.exit_code == 2
    assert "No such command 'stealthy-fetch'" in result.output
    assert not hasattr(cli, "stealthy_fetch")


@pytest.mark.parametrize(("installed", "force"), [(False, False), (True, False), (True, True), (False, True)])
def test_install_playwright_keeps_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, installed: bool, force: bool
) -> None:
    marker = tmp_path / ".scrapling_dependencies_installed"
    if installed:
        marker.touch()
    monkeypatch.setattr(cli, "__PACKAGE_DIR__", tmp_path)
    with patch("scrapling.cli.check_output") as execute, patch("tld.utils.update_tld_names") as update:
        result = CliRunner().invoke(cli.main, ["install", *(["--force"] if force else [])])
    assert result.exit_code == 0, result.output
    assert marker.exists()
    if force or not installed:
        assert execute.call_args_list == [
            call([cli.python_executable, "-m", "playwright", "install", "chromium"], shell=False),
            call([cli.python_executable, "-m", "playwright", "install-deps", "chromium"], shell=False),
        ]
        update.assert_called_once_with(fail_silently=True)
        assert "Installing browsers" in result.output
    else:
        execute.assert_not_called()
        update.assert_not_called()
        assert result.output.strip() == "The dependencies are already installed"


def test_shell_fetch_namespace_and_completion() -> None:
    shell = CustomShell(code="")
    namespace = shell.get_namespace()
    assert namespace["StealthyFetcher"] is StealthyFetcher
    assert {"StealthySession", "AsyncStealthySession", "fetch"} <= namespace.keys()
    assert (
        not {"DynamicFetcher", "DynamicSession", "AsyncDynamicSession", "PlayWrightFetcher", "stealthy_fetch"}
        & namespace.keys()
    )
    parameters = signature(namespace["fetch"]).parameters
    assert set(parameters) == {"url", *StealthSession.__annotations__}
    assert all(parameters[name].kind is Parameter.KEYWORD_ONLY for name in StealthSession.__annotations__)
    assert Signatures_map["fetch"] == StealthSession.__annotations__
    assert "stealthy_fetch" not in Signatures_map
    assert "Shortcut for `StealthyFetcher.fetch`" in shell.banner()
    assert "Dynamic" not in shell.banner()
    assert "stealthy_fetch" not in shell.banner()


def test_shell_fetch_updates_page_history() -> None:
    pages = [Selector(f"<p>{index}</p>") for index in range(7)]
    shell = CustomShell(code="")
    shell.shell = MagicMock(user_ns={})
    with patch.object(StealthyFetcher, "fetch", side_effect=pages) as fetch:
        namespace = shell.get_namespace()
        for page in pages:
            assert namespace["fetch"]("https://example.com", solve_cloudflare=True) is page
    assert fetch.call_count == len(pages)
    fetch.assert_called_with("https://example.com", solve_cloudflare=True)
    assert shell.page is pages[-1]
    assert shell.pages == pages[-5:]
    assert shell.shell.user_ns == {"page": pages[-1], "response": pages[-1], "pages": pages[-5:]}
