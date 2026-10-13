import pytest

from scrapling.engines.toolbelt import ProxyRotator
from scrapling.engines.toolbelt.proxy_timezone import (
    clear_proxy_timezone_cache,
    extract_proxy_host,
    proxy_key,
    resolve_proxy_timezone,
)


class TestProxyKey:
    def test_string_proxy_key(self):
        """A string proxy is its own cache key."""
        assert proxy_key("http://p1:8080") == "http://p1:8080"

    def test_dict_proxy_key(self):
        """A dict proxy keys on server plus username."""
        proxy = {"server": "http://p1:8080", "username": "user", "password": "pass"}
        assert proxy_key(proxy) == "http://p1:8080|user"


class TestExtractProxyHost:
    def test_string_with_auth(self):
        """Credentials and port are stripped from a proxy URL."""
        assert extract_proxy_host("http://user:pass@proxy.example.com:8080") == "proxy.example.com"

    def test_dict_server(self):
        """The host comes from the dict's server entry."""
        assert extract_proxy_host({"server": "http://10.0.0.1:8080"}) == "10.0.0.1"

    def test_empty(self):
        """Empty proxies yield an empty host."""
        assert extract_proxy_host("") == ""
        assert extract_proxy_host({}) == ""  # type: ignore[dict-item]


class TestResolveProxyTimezone:
    def setup_method(self):
        clear_proxy_timezone_cache()

    def test_fallback_when_disabled(self):
        """With no sync options, the session timezone is kept."""
        tz = resolve_proxy_timezone("http://p1:8080", fallback="UTC")
        assert tz == "UTC"

    def test_explicit_map_by_key(self):
        """A map entry keyed by the full proxy string wins."""
        proxy = "http://p1:8080"
        tz = resolve_proxy_timezone(
            proxy,
            fallback="UTC",
            proxy_timezone_map={proxy: "Europe/Berlin"},
        )
        assert tz == "Europe/Berlin"

    def test_explicit_map_by_host(self):
        """A map entry keyed by hostname matches any proxy on that host."""
        tz = resolve_proxy_timezone(
            "http://user:pass@proxy.example.com:8080",
            fallback="UTC",
            proxy_timezone_map={"proxy.example.com": "America/New_York"},
        )
        assert tz == "America/New_York"

    def test_custom_resolver(self):
        """A custom resolver callable is honored."""
        def resolver(proxy):
            return "Asia/Tokyo"

        tz = resolve_proxy_timezone(
            "http://p1:8080",
            fallback="UTC",
            timezone_resolver=resolver,
        )
        assert tz == "Asia/Tokyo"

    def test_custom_resolver_failure_falls_back(self):
        """A raising resolver falls back instead of breaking."""
        def bad_resolver(proxy):
            raise RuntimeError("boom")

        tz = resolve_proxy_timezone(
            "http://p1:8080",
            fallback="UTC",
            timezone_resolver=bad_resolver,
        )
        assert tz == "UTC"

    def test_cache_avoids_second_resolver_call(self):
        """Resolved timezones are cached per proxy."""
        calls = {"n": 0}

        def counting_resolver(proxy):
            calls["n"] += 1
            return "Europe/Paris"

        first = resolve_proxy_timezone("http://cached:8080", fallback="UTC", timezone_resolver=counting_resolver)
        second = resolve_proxy_timezone("http://cached:8080", fallback="UTC", timezone_resolver=counting_resolver)
        assert first == "Europe/Paris"
        assert second == "Europe/Paris"
        assert calls["n"] == 1


class TestBuildContextWithProxy:
    def setup_method(self):
        clear_proxy_timezone_cache()

    def test_context_syncs_timezone_from_map(self):
        """A rotation context takes the mapped timezone for its proxy."""
        pytest.importorskip("patchright")
        from scrapling.engines._browsers._base import BaseSessionMixin

        mixin = BaseSessionMixin()
        mixin._context_options = {"timezone_id": "UTC"}  # type: ignore[attr-defined]
        mixin._config = type(
            "C",
            (),
            {  # type: ignore[attr-defined]
                "timezone_id": "UTC",
                "proxy_timezone_map": {"http://p1:8080": "Europe/Berlin"},
                "timezone_resolver": None,
                "auto_match_timezone": False,
            },
        )()

        options = mixin._build_context_with_proxy("http://p1:8080")
        assert options["timezone_id"] == "Europe/Berlin"
        assert options["proxy"]["server"] == "http://p1:8080"

    def test_context_keeps_default_on_failure(self):
        """A failing resolver keeps the session timezone for the context."""
        pytest.importorskip("patchright")
        from scrapling.engines._browsers._base import BaseSessionMixin

        def bad_resolver(proxy):
            raise RuntimeError("boom")

        mixin = BaseSessionMixin()
        mixin._context_options = {"timezone_id": "UTC"}  # type: ignore[attr-defined]
        mixin._config = type(
            "C",
            (),
            {  # type: ignore[attr-defined]
                "timezone_id": "UTC",
                "proxy_timezone_map": None,
                "timezone_resolver": bad_resolver,
                "auto_match_timezone": False,
            },
        )()

        options = mixin._build_context_with_proxy("http://p1:8080")
        assert options["timezone_id"] == "UTC"


def _read_browser_timezone(session, proxy):
    """Read ``Intl`` timezone from a blank tab in a fresh rotation context.

    No navigation happens, so a dummy (unreachable) proxy is enough: context
    creation applies ``timezone_id`` before any request is made.
    """
    with session._page_generator(30000, None, False, proxy, None) as page_info:
        return page_info.page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")


def _read_context_timezone(session):
    """Read ``Intl`` timezone from the persistent context of a session."""
    page = session.context.new_page()
    try:
        return page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
    finally:
        page.close()


@pytest.mark.browser
class TestProxyTimezoneE2E:
    """End-to-end: real browser timezone with and without the feature."""

    def setup_method(self):
        clear_proxy_timezone_cache()

    def test_without_feature_timezone_mismatches_proxy(self):
        """Without syncing, the browser keeps the session timezone (UTC) even
        though the proxy exit is in Berlin -- the mismatch bots detect."""
        pytest.importorskip("patchright")
        from scrapling.fetchers import StealthySession

        proxy = "http://127.0.0.1:9"
        with StealthySession(
            timezone_id="UTC",
            proxy_rotator=ProxyRotator([proxy]),
        ) as session:
            assert _read_browser_timezone(session, proxy) == "UTC"

    def test_with_feature_timezone_matches_proxy(self):
        """With ``proxy_timezone_map``, the same proxy gets a Berlin browser."""
        pytest.importorskip("patchright")
        from scrapling.fetchers import StealthySession

        proxy = "http://127.0.0.1:9"
        with StealthySession(
            timezone_id="UTC",
            proxy_rotator=ProxyRotator([proxy]),
            proxy_timezone_map={proxy: "Europe/Berlin"},
        ) as session:
            assert _read_browser_timezone(session, proxy) == "Europe/Berlin"

    def test_without_feature_static_proxy_timezone_mismatch(self):
        """A session-level static proxy keeps the session timezone (UTC)."""
        pytest.importorskip("patchright")
        from scrapling.fetchers import StealthySession

        with StealthySession(timezone_id="UTC", proxy="http://127.0.0.1:9") as session:
            assert _read_context_timezone(session) == "UTC"

    def test_with_feature_static_proxy_timezone_matches(self):
        """A session-level static proxy is synced too (keyed by host)."""
        pytest.importorskip("patchright")
        from scrapling.fetchers import StealthySession

        with StealthySession(
            timezone_id="UTC",
            proxy="http://127.0.0.1:9",
            proxy_timezone_map={"127.0.0.1": "Europe/Berlin"},
        ) as session:
            assert _read_context_timezone(session) == "Europe/Berlin"
