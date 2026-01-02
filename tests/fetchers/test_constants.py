from scrapling.engines.constants import (
    DEFAULT_DISABLED_RESOURCES,
    DEFAULT_STEALTH_FLAGS,
    HARMFUL_DEFAULT_ARGS,
    DEFAULT_FLAGS,
)


class TestConstants:
    """Test constant values"""

    def test_default_disabled_resources(self):
        """Test default disabled resources"""
        assert "image" in DEFAULT_DISABLED_RESOURCES
        assert "font" in DEFAULT_DISABLED_RESOURCES
        assert "stylesheet" in DEFAULT_DISABLED_RESOURCES
        assert "media" in DEFAULT_DISABLED_RESOURCES

    def test_harmful_default_args(self):
        """Test harmful default arguments"""
        assert "--enable-automation" in HARMFUL_DEFAULT_ARGS
        assert "--disable-popup-blocking" in HARMFUL_DEFAULT_ARGS

    def test_flags(self):
        """Test default stealth flags"""
        assert "--no-pings" in DEFAULT_FLAGS
        # assert "--incognito" in DEFAULT_STEALTH_FLAGS
        assert "--disable-blink-features=AutomationControlled" in DEFAULT_STEALTH_FLAGS
