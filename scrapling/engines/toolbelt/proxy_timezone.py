"""
Resolve a browser timezone from a proxy for stealth.

The browser ``timezone_id`` should match the proxy/VPN exit location so
websites cannot detect automation through a timezone mismatch. This module
provides a small, opt-in, failure-safe resolver with caching:

1. Explicit ``proxy_timezone_map`` (deterministic, no network).
2. Custom ``timezone_resolver`` callable (for user providers/tests).
3. Built-in auto lookup via ``ip-api.com`` (direct host lookup, cached).
4. Fallback to the session ``timezone_id`` (current behavior).
"""

import json
from hashlib import sha256
from threading import Lock
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from scrapling.core._types import Callable, Dict, Optional, ProxyType
from scrapling.core.utils import log


TimezoneResolver = Callable[[ProxyType], Optional[str]]

_cache: Dict[str, Optional[str]] = {}
_cache_lock = Lock()


def clear_proxy_timezone_cache() -> None:
    """Clear the in-memory proxy to timezone cache (mainly for tests)."""
    with _cache_lock:
        _cache.clear()


def proxy_key(proxy: ProxyType) -> str:
    """Generate a stable cache key for a proxy."""
    if isinstance(proxy, str):
        return proxy
    server = proxy.get("server", "") if isinstance(proxy, dict) else ""
    username = proxy.get("username", "") if isinstance(proxy, dict) else ""
    return f"{server}|{username}"


def _redact(proxy: ProxyType) -> str:
    """Return a credentials-free description of a proxy for logging."""
    host = extract_proxy_host(proxy)
    return host or "proxy"


def extract_proxy_host(proxy: ProxyType) -> str:
    """Extract the hostname from a proxy URL string or Playwright dict."""
    server = ""
    if isinstance(proxy, str):
        server = proxy
    elif isinstance(proxy, dict):
        server = proxy.get("server", "")
    if not server:
        return ""
    if "://" not in server:
        server = f"http://{server}"
    try:
        return urlparse(server).hostname or ""
    except ValueError:
        return ""


def fetch_timezone_for_host(host: str, timeout: float = 3.0) -> Optional[str]:
    """Look up the IANA timezone for an IP/host via ip-api.com.

    :param host: Proxy hostname or exit IP.
    :param timeout: HTTP timeout in seconds.
    :return: Timezone like ``Europe/Berlin`` or ``None`` on any failure.
    """
    if not host:
        return None
    url = f"http://ip-api.com/json/{host}?fields=status,timezone,query"
    try:
        request = Request(url, headers={"Accept": "application/json"})
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - fixed ip-api.com endpoint, host is user config
            payload = json.loads(response.read().decode("utf-8", "replace"))
        if payload.get("status") == "success" and payload.get("timezone"):
            timezone = str(payload["timezone"])
            return timezone or None
        return None
    except Exception as e:  # Never break crawling on geo lookup failure
        log.debug(f"Timezone auto-lookup failed for host '{host}': {e}")
        return None


def resolve_proxy_timezone(
    proxy: ProxyType,
    fallback: Optional[str] = None,
    proxy_timezone_map: Optional[Dict[str, str]] = None,
    timezone_resolver: Optional[TimezoneResolver] = None,
    auto_match_timezone: bool = False,
    timeout: float = 3.0,
) -> Optional[str]:
    """Resolve the timezone for a proxy with caching and safe fallbacks.

    Priority: explicit map -> custom resolver -> auto lookup -> fallback.

    :param proxy: Proxy URL string or Playwright-style dict.
    :param fallback: Session-level ``timezone_id`` to use when unresolved.
    :param proxy_timezone_map: Optional explicit mapping keyed by proxy key
        (see :func:`proxy_key`) or by proxy hostname.
    :param timezone_resolver: Optional callable ``(proxy) -> timezone|None``.
    :param auto_match_timezone: Enable built-in ip-api.com lookup.
    :param timeout: Lookup timeout in seconds for the built-in provider.
    :return: IANA timezone string or the fallback.
    """
    key = proxy_key(proxy)
    cache_key = sha256(proxy_key(proxy).encode("utf-8", "replace")).hexdigest()
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key] or fallback

    resolved: Optional[str] = None

    if proxy_timezone_map:
        host = extract_proxy_host(proxy)
        resolved = proxy_timezone_map.get(key) or (proxy_timezone_map.get(host) if host else None)

    if resolved is None and timezone_resolver is not None:
        try:
            resolved = timezone_resolver(proxy)
        except Exception as e:
            log.debug(f"Custom timezone resolver failed for proxy '{_redact(proxy)}': {e}")
            resolved = None

    if resolved is None and auto_match_timezone:
        host = extract_proxy_host(proxy)
        resolved = fetch_timezone_for_host(host, timeout=timeout) if host else None

    with _cache_lock:
        _cache[cache_key] = resolved

    return resolved or fallback
