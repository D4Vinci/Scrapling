import pytest
from scrapling.engines._browsers._validators import (
    validate,
    StealthConfig,
    PlaywrightConfig,
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
