import pytest
from pathlib import Path

from scrapling.engines._browsers._validators import (
    validate,
    StealthConfig,
    PlaywrightConfig,
    validate_fetch,
    _is_invalid_file_path,
)


class TestValidators:
    """Test configuration validators"""

    def test_playwright_config_valid(self):
        """Test valid PlaywrightConfig"""
        params = {
            "max_pages": 2,
            "headless": True,
            "timeout": 30000,
            "proxy": "http://proxy.example.com:8080"
        }

        config = validate(params, PlaywrightConfig)

        assert config.max_pages == 2
        assert config.headless is True
        assert config.timeout == 30000
        assert isinstance(config.proxy, dict)

    def test_playwright_config_invalid_max_pages(self):
        """Test PlaywrightConfig with invalid max_pages"""
        params = {"max_pages": 0}

        with pytest.raises(TypeError):
            validate(params, PlaywrightConfig)

        params = {"max_pages": 51}

        with pytest.raises(TypeError):
            validate(params, PlaywrightConfig)

    def test_playwright_config_invalid_timeout(self):
        """Test PlaywrightConfig with an invalid timeout"""
        params = {"timeout": -1}

        with pytest.raises(TypeError):
            validate(params, PlaywrightConfig)

    def test_playwright_config_invalid_cdp_url(self):
        """Test PlaywrightConfig with invalid CDP URL"""
        params = {"cdp_url": "invalid-url"}

        with pytest.raises(TypeError):
            validate(params, PlaywrightConfig)

    def test_stealth_config_valid(self):
        """Test valid StealthConfig"""
        params = {
            "max_pages": 1,
            "headless": True,
            "solve_cloudflare": False,
            "timeout": 30000
        }

        config = validate(params, StealthConfig)

        assert config.max_pages == 1
        assert config.headless is True
        assert config.solve_cloudflare is False
        assert config.timeout == 30000

    def test_stealth_config_cloudflare_timeout(self):
        """Test StealthConfig timeout adjustment for Cloudflare"""
        params = {
            "solve_cloudflare": True,
            "timeout": 10000  # Less than the required 60,000
        }

        config = validate(params, StealthConfig)

        assert config.timeout == 60000  # Should be increased

    def test_playwright_config_blocked_domains(self):
        """Test PlaywrightConfig with blocked_domains"""
        params = {"blocked_domains": {"ads.example.com", "tracker.io"}}

        config = validate(params, PlaywrightConfig)

        assert config.blocked_domains == {"ads.example.com", "tracker.io"}

    def test_playwright_config_blocked_domains_default_none(self):
        """Test PlaywrightConfig blocked_domains defaults to None"""
        config = validate({}, PlaywrightConfig)

        assert config.blocked_domains is None

    def test_stealth_config_blocked_domains(self):
        """Test StealthConfig inherits blocked_domains"""
        params = {"blocked_domains": {"ads.example.com"}}

        config = validate(params, StealthConfig)

        assert config.blocked_domains == {"ads.example.com"}


class TestValidatorRegressionCoverage:
    def test_file_path_validation_is_not_stale_cached(self, tmp_path):
        path = tmp_path / "init.js"
        missing_msg = _is_invalid_file_path(str(path))
        assert missing_msg
        path.write_text("// init", encoding="utf-8")
        assert _is_invalid_file_path(str(path)) is False

    def test_validate_fetch_merges_session_defaults_and_overrides(self):
        class Session:
            _config = validate({"timeout": 1000, "wait": 0, "network_idle": False}, PlaywrightConfig)

        params = validate_fetch({"timeout": 2000, "network_idle": True}, Session(), PlaywrightConfig)
        assert params.timeout == 2000
        assert params.network_idle is True
        assert params.wait == 0

    def test_stealth_proxy_auto_enables_webrtc_protections(self):
        config = validate({"proxy": "http://proxy.example:8080"}, StealthConfig)
        assert config.block_webrtc is True
        assert config.dns_over_https is True

    def test_stealth_explicit_webrtc_override_is_preserved(self):
        config = validate({"proxy": "http://proxy.example:8080", "block_webrtc": False}, StealthConfig)
        assert config.block_webrtc is False
