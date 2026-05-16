# -*- coding: utf-8 -*-
"""Internal URL guard used by the MCP server tools.

Refuses non-HTTP schemes and SSRF-prone targets (loopback, private,
link-local, multicast, reserved, unspecified IPs). Optional allowlist
via ``SCRAPLING_MCP_ALLOWLIST``. A development escape hatch
(``SCRAPLING_MCP_ALLOW_LOCAL=1``) bypasses the IP-class checks; it is
intended only for local testing and is documented as such.
"""
from __future__ import annotations

import ipaddress
import os
import socket
from typing import FrozenSet, Iterable, Optional, Tuple
from urllib.parse import urlparse

_ALLOWED_SCHEMES = frozenset({"http", "https"})
_ALLOWLIST_ENV = "SCRAPLING_MCP_ALLOWLIST"
_ALLOW_LOCAL_ENV = "SCRAPLING_MCP_ALLOW_LOCAL"


class UnsafeURLError(ValueError):
    """Raised when a URL fails MCP safety validation."""


def _ip_block_reason(ip: ipaddress._BaseAddress) -> Optional[str]:
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link-local"
    if ip.is_multicast:
        return "multicast"
    if ip.is_unspecified:
        return "unspecified"
    if ip.is_private:
        return "private"
    if ip.is_reserved:
        return "reserved"
    return None


def _load_allowlist() -> Optional[FrozenSet[str]]:
    raw = os.environ.get(_ALLOWLIST_ENV, "").strip()
    if not raw:
        return None
    items = {h.strip().lower().lstrip(".") for h in raw.split(",") if h.strip()}
    return frozenset(items) if items else None


def _hostname_in_allowlist(hostname: str, allowlist: Iterable[str]) -> bool:
    h = hostname.lower()
    for entry in allowlist:
        if h == entry or h.endswith("." + entry):
            return True
    return False


def _allow_local() -> bool:
    return os.environ.get(_ALLOW_LOCAL_ENV, "").strip() in {"1", "true", "yes", "on"}


def _try_parse_ip(value: str) -> Optional[ipaddress._BaseAddress]:
    candidate = value
    if candidate.startswith("[") and candidate.endswith("]"):
        candidate = candidate[1:-1]
    try:
        return ipaddress.ip_address(candidate)
    except ValueError:
        return None


def _check_ip(
    ip: ipaddress._BaseAddress, hostname: str, *, original: Optional[str] = None
) -> None:
    reason = _ip_block_reason(ip)
    if reason is None:
        return
    detail = f"{hostname}" if original is None or original == hostname else f"{hostname} ({original})"
    raise UnsafeURLError(f"Host '{detail}' resolves to a {reason} address; refused.")


def validate_url(
    url: str,
    *,
    allowlist: Optional[Iterable[str]] = None,
    allow_local: Optional[bool] = None,
) -> None:
    """Validate a URL for MCP-driven outbound fetch.

    :param url: The URL to validate.
    :param allowlist: Optional iterable of allowed hostnames. If ``None``,
        the value of ``SCRAPLING_MCP_ALLOWLIST`` is used. When effectively
        empty, no allowlist is enforced.
    :param allow_local: Override for the ``SCRAPLING_MCP_ALLOW_LOCAL`` env
        var. Bypasses the IP-class blocks (still enforces scheme and
        allowlist). Intended for local development/tests only.
    :raises UnsafeURLError: on any rule violation.
    """
    if not isinstance(url, str) or not url:
        raise UnsafeURLError("URL must be a non-empty string.")

    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise UnsafeURLError(
            f"URL scheme '{scheme or '<empty>'}' is not allowed; only http/https are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise UnsafeURLError("URL must include a hostname.")

    effective_allowlist = allowlist if allowlist is not None else _load_allowlist()
    if effective_allowlist is not None and not _hostname_in_allowlist(hostname, effective_allowlist):
        raise UnsafeURLError(f"Host '{hostname}' is not in the configured allowlist.")

    bypass_ip_checks = allow_local if allow_local is not None else _allow_local()
    if bypass_ip_checks:
        return

    direct_ip = _try_parse_ip(hostname)
    if direct_ip is not None:
        _check_ip(direct_ip, hostname)
        return

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise UnsafeURLError(f"Host '{hostname}' could not be resolved: {e}")

    seen = set()
    for info in infos:
        sockaddr = info[4]
        addr = sockaddr[0]
        if addr in seen:
            continue
        seen.add(addr)
        resolved = _try_parse_ip(addr)
        if resolved is None:
            continue
        _check_ip(resolved, hostname, original=addr)


def require_http_token() -> str:
    """Return the configured HTTP MCP token or raise ``UnsafeURLError``.

    Used both as a startup gate and as the shared secret that the HTTP
    MCP transport's per-request Bearer auth (see
    :mod:`scrapling.core._mcp_auth`) compares incoming
    ``Authorization`` headers against.
    """
    token = os.environ.get("SCRAPLING_MCP_TOKEN", "").strip()
    if not token:
        raise UnsafeURLError(
            "HTTP MCP transport requires SCRAPLING_MCP_TOKEN to be set in the environment."
        )
    return token
