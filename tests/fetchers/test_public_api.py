from importlib import import_module
from importlib.machinery import ModuleSpec
from json import dumps
from pathlib import Path

import pytest

from scrapling.engines.toolbelt import fingerprints


@pytest.mark.parametrize("module", ["scrapling", "scrapling.fetchers"])
@pytest.mark.parametrize("name", ["DynamicFetcher", "DynamicSession", "AsyncDynamicSession", "PlayWrightFetcher"])
def test_dynamic_imports_are_removed(module: str, name: str) -> None:
    package = import_module(module)
    assert name not in package.__all__
    with pytest.raises(ImportError):
        exec(f"from {module} import {name}")


@pytest.mark.parametrize("module", ["scrapling.fetchers.chrome", "scrapling.engines._browsers._controllers"])
def test_dynamic_modules_are_removed(module: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        import_module(module)


@pytest.mark.parametrize("browser_mode", [True, "chrome"])
def test_browser_version_uses_patchright_when_playwright_is_installed(
    browser_mode: bool | str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    packages: dict[str, ModuleSpec] = {}
    looked_up: list[str] = []
    for name, version in (("patchright", "998.0.0.0"), ("playwright", "999.0.0.0")):
        directory = tmp_path / name
        bundle = directory / "driver" / "package"
        bundle.mkdir(parents=True)
        (bundle / "browsers.json").write_text(dumps({"browsers": [{"name": "chromium", "browserVersion": version}]}))
        packages[name] = ModuleSpec(name, None, origin=str(directory / "__init__.py"))

    def find_spec(name: str) -> ModuleSpec:
        looked_up.append(name)
        return packages[name]

    monkeypatch.setattr(fingerprints, "find_spec", find_spec)
    monkeypatch.setattr(fingerprints, "get_os_name", lambda: "macos")
    fingerprints.driven_browser_version.cache_clear()
    try:
        assert fingerprints.driven_browser_version() == 998
        assert "Chrome/998.0.0.0" in fingerprints.generate_headers(browser_mode=browser_mode)["User-Agent"]
        assert looked_up == ["patchright"]
    finally:
        fingerprints.driven_browser_version.cache_clear()
