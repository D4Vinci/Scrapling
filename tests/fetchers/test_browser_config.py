import importlib
import sys
from unittest.mock import call, patch


_CONFIG_MODULE = "scrapling.engines._browsers._config_tools"


def test_config_tools_import_does_not_generate_headers() -> None:
    """Importing browser configuration must not depend on header generation."""
    sys.modules.pop(_CONFIG_MODULE, None)
    try:
        with patch(
            "scrapling.engines.toolbelt.fingerprints.generate_headers",
            side_effect=ValueError("No headers based on this input can be generated."),
        ) as generate_headers:
            importlib.import_module(_CONFIG_MODULE)

        generate_headers.assert_not_called()
    finally:
        sys.modules.pop(_CONFIG_MODULE, None)


def test_default_useragent_is_generated_on_demand() -> None:
    """Default user agents should retain their modes and be cached after generation."""
    config_tools = importlib.import_module(_CONFIG_MODULE)
    config_tools.get_default_useragent.cache_clear()
    try:
        with patch.object(
            config_tools,
            "generate_headers",
            side_effect=[{"User-Agent": "chromium"}, {"User-Agent": "chrome"}],
        ) as generate_headers:
            assert config_tools.get_default_useragent(True) == "chromium"
            assert config_tools.get_default_useragent(True) == "chromium"
            assert config_tools.get_default_useragent("chrome") == "chrome"

        assert generate_headers.call_args_list == [
            call(browser_mode=True),
            call(browser_mode="chrome"),
        ]
    finally:
        config_tools.get_default_useragent.cache_clear()
