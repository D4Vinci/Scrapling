import pytest
from unittest.mock import MagicMock, patch, call
from scrapling.engines._browsers._validators import (
    validate,
    validate_fetch,
    _fetch_params,
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

    def test_playwright_config_pre_nav_listeners_default_none(self):
        """Test PlaywrightConfig pre_nav_listeners defaults to None"""
        config = validate({}, PlaywrightConfig)

        assert config.pre_nav_listeners is None

    def test_playwright_config_pre_nav_listeners_accepted(self):
        """Test PlaywrightConfig accepts a pre_nav_listeners dict"""
        handler = MagicMock()
        params = {"pre_nav_listeners": {"websocket": handler}}

        config = validate(params, PlaywrightConfig)

        assert config.pre_nav_listeners == {"websocket": handler}

    def test_stealth_config_pre_nav_listeners_accepted(self):
        """Test StealthConfig inherits pre_nav_listeners support"""
        handler = MagicMock()
        params = {"pre_nav_listeners": {"websocket": handler}}

        config = validate(params, StealthConfig)

        assert config.pre_nav_listeners == {"websocket": handler}

    def test_pre_nav_listeners_registered_before_goto(self):
        """Test that pre_nav_listeners are registered on the page before page.goto() is called"""
        call_order: list = []
        mock_page = MagicMock()

        def track_on(event: str, handler: object) -> None:
            call_order.append(("on", event))

        def track_goto(*args: object, **kwargs: object) -> MagicMock:
            call_order.append(("goto",))
            return MagicMock()

        mock_page.on.side_effect = track_on
        mock_page.goto.side_effect = track_goto

        ws_handler = MagicMock()
        pre_nav_listeners = {"websocket": ws_handler}

        # Simulate the registration logic used in fetch() methods
        mock_page.on("response", MagicMock())
        if pre_nav_listeners:
            for event_name, handler in pre_nav_listeners.items():
                mock_page.on(event_name, handler)
        mock_page.goto("https://example.com")

        assert call_order.index(("on", "websocket")) < call_order.index(("goto",)), (
            "pre_nav_listeners must be registered before page.goto()"
        )

    def test_pre_nav_listeners_multiple_events(self):
        """Test that multiple pre_nav_listeners are all registered before goto"""
        call_order: list = []
        mock_page = MagicMock()

        def track_on(event: str, handler: object) -> None:
            call_order.append(("on", event))

        def track_goto(*args: object, **kwargs: object) -> MagicMock:
            call_order.append(("goto",))
            return MagicMock()

        mock_page.on.side_effect = track_on
        mock_page.goto.side_effect = track_goto

        pre_nav_listeners = {"websocket": MagicMock(), "request": MagicMock()}

        mock_page.on("response", MagicMock())
        if pre_nav_listeners:
            for event_name, handler in pre_nav_listeners.items():
                mock_page.on(event_name, handler)
        mock_page.goto("https://example.com")

        goto_index = call_order.index(("goto",))
        for event in ("websocket", "request"):
            assert call_order.index(("on", event)) < goto_index, (
                f"pre_nav_listener for '{event}' must be registered before page.goto()"
            )

    def test_fetch_params_includes_pre_nav_listeners(self):
        """Test that _fetch_params dataclass includes pre_nav_listeners field"""
        from dataclasses import fields as dc_fields
        field_names = {f.name for f in dc_fields(_fetch_params)}
        assert "pre_nav_listeners" in field_names
