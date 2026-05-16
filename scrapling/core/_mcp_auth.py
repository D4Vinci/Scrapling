# -*- coding: utf-8 -*-
"""Request-level Bearer token verification for the HTTP MCP transport.

FastMCP's ``streamable-http`` transport accepts a ``TokenVerifier`` whose
``verify_token`` coroutine is invoked by the bundled ``BearerAuthBackend``
for every incoming request that carries an ``Authorization: Bearer <...>``
header. ``RequireAuthMiddleware`` rejects requests that arrive without a
verified user with HTTP 401. We plug a static, constant-time verifier in
front of that machinery so the value of ``SCRAPLING_MCP_TOKEN`` is checked
on every request rather than only at process startup.
"""
from __future__ import annotations

import hmac
from typing import Optional


def _to_bytes(value: str) -> Optional[bytes]:
    if not isinstance(value, str):
        return None
    try:
        return value.encode("utf-8")
    except UnicodeEncodeError:  # pragma: no cover - defensive
        return None


class StaticBearerTokenVerifier:
    """Verifier that accepts exactly one shared-secret bearer token.

    The expected token is captured at construction time. Comparison is done
    with :func:`hmac.compare_digest` to avoid leaking information through
    timing side channels.
    """

    def __init__(self, expected_token: str):
        token = (expected_token or "").strip()
        if not token:
            raise ValueError("StaticBearerTokenVerifier requires a non-empty token.")
        self._expected = token.encode("utf-8")
        self._client_id = "scrapling-mcp"

    async def verify_token(self, token: str):
        """Return an :class:`AccessToken` on a match, ``None`` otherwise.

        The MCP ``BearerAuthBackend`` treats ``None`` as an authentication
        failure, which is then turned into a 401 by ``RequireAuthMiddleware``.
        """
        from mcp.server.auth.provider import AccessToken

        candidate = _to_bytes(token)
        if candidate is None:
            return None
        # Constant-time comparison; lengths may differ but compare_digest
        # handles that without an early-exit length branch.
        if not hmac.compare_digest(self._expected, candidate):
            return None
        return AccessToken(
            token=token,
            client_id=self._client_id,
            scopes=[],
            expires_at=None,
        )


def build_http_auth(token: str, port: int):
    """Build the ``(auth_settings, verifier)`` pair for FastMCP HTTP mode.

    ``AuthSettings`` requires ``issuer_url`` and ``resource_server_url``.
    They are only used as identifiers in protected-resource metadata; we
    synthesize them from the bind port so the operator does not have to
    configure an OAuth issuer for what is, semantically, a static shared
    secret deployment.
    """
    from mcp.server.auth.settings import AuthSettings
    from pydantic import AnyHttpUrl

    base_url = AnyHttpUrl(f"http://127.0.0.1:{int(port)}")
    settings = AuthSettings(
        issuer_url=base_url,
        resource_server_url=base_url,
        required_scopes=[],
    )
    return settings, StaticBearerTokenVerifier(token)
