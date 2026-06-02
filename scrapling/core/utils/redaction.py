"""Redaction helpers for logs, metadata, caches, and checkpoints."""

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlsplit, urlunsplit
from typing import Any

_SECRET_REPLACEMENT = "***"

_SENSITIVE_HEADER_NAMES = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-api-token",
    "x-auth-token",
}

_SENSITIVE_KEY_FRAGMENTS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "auth",
    "credential",
    "cookie",
)


def is_sensitive_key(key: object) -> bool:
    """Return True when a mapping key commonly carries credentials."""
    normalized = str(key).strip().lower().replace("-", "_")
    if normalized in {name.replace("-", "_") for name in _SENSITIVE_HEADER_NAMES}:
        return True
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


def redact_url_userinfo(url: Any) -> Any:
    """Remove user:password information from a URL-like value.

    Non-string values are returned unchanged so callers can safely pass optional
    proxy values without defensive type checks.
    """
    if not isinstance(url, str) or not url:
        return url
    try:
        parsed = urlsplit(url)
    except Exception:
        return _SECRET_REPLACEMENT if "@" in url else url

    if not parsed.netloc or (parsed.username is None and parsed.password is None):
        return url

    host = parsed.hostname or ""
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    netloc = f"{_SECRET_REPLACEMENT}@{host}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def redact_headers(headers: Mapping[Any, Any] | None) -> dict[Any, Any]:
    """Return a copy of headers with credential-bearing values removed."""
    if not headers:
        return {}
    redacted: dict[Any, Any] = {}
    for key, value in dict(headers).items():
        if is_sensitive_key(key):
            redacted[key] = _SECRET_REPLACEMENT
        else:
            redacted[key] = value
    return redacted


def redact_proxy(value: Any) -> Any:
    """Redact proxy credentials from strings or proxy dictionaries.

    Supports both curl_cffi style mappings (``{"http": "http://user:pass@host"}``)
    and Playwright style mappings (``{"server": "...", "username": "...", "password": "..."}``).
    """
    if value is None:
        return None
    if isinstance(value, str):
        return redact_url_userinfo(value)
    if isinstance(value, Mapping):
        redacted: dict[Any, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in {"username", "password"} or is_sensitive_key(normalized):
                redacted[key] = _SECRET_REPLACEMENT
            elif normalized in {"server", "http", "https", "all"}:
                redacted[key] = redact_url_userinfo(item)
            elif isinstance(item, Mapping):
                redacted[key] = redact_proxy(item)
            elif isinstance(item, str):
                redacted[key] = redact_url_userinfo(item)
            else:
                redacted[key] = item
        return redacted
    return value


def redact_mapping(value: Mapping[Any, Any] | None) -> dict[Any, Any]:
    """Recursively redact a generic mapping containing headers, proxy, or auth keys."""
    if not value:
        return {}
    redacted: dict[Any, Any] = {}
    for key, item in dict(value).items():
        normalized = str(key).strip().lower().replace("-", "_")
        if normalized in {"proxy", "proxies"}:
            redacted[key] = redact_proxy(item)
        elif normalized in {"headers", "extra_headers", "request_headers"} and isinstance(item, Mapping):
            redacted[key] = redact_headers(item)
        elif is_sensitive_key(normalized):
            redacted[key] = _SECRET_REPLACEMENT
        elif isinstance(item, Mapping):
            redacted[key] = redact_mapping(item)
        elif isinstance(item, list):
            redacted[key] = [redact_mapping(v) if isinstance(v, Mapping) else v for v in item]
        elif isinstance(item, tuple):
            redacted[key] = tuple(redact_mapping(v) if isinstance(v, Mapping) else v for v in item)
        elif isinstance(item, str):
            redacted[key] = redact_url_userinfo(item)
        else:
            redacted[key] = item
    return redacted
