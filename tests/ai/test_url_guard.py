import socket

import pytest

from scrapling.core._url_guard import (
    UnsafeURLError,
    require_http_token,
    validate_url,
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Each test starts with no MCP env vars set."""
    for var in ("SCRAPLING_MCP_ALLOW_LOCAL", "SCRAPLING_MCP_ALLOWLIST", "SCRAPLING_MCP_TOKEN"):
        monkeypatch.delenv(var, raising=False)
    yield


def _addrinfo_for(*addresses):
    """Build a socket.getaddrinfo-style return value for the given IPs."""

    def _fake(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (addr, 0)) for addr in addresses]

    return _fake


class TestSchemeRules:
    def test_rejects_file_scheme(self):
        with pytest.raises(UnsafeURLError):
            validate_url("file:///etc/passwd")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(UnsafeURLError):
            validate_url("ftp://example.com/foo")

    def test_rejects_gopher_scheme(self):
        with pytest.raises(UnsafeURLError):
            validate_url("gopher://example.com/")

    def test_rejects_data_scheme(self):
        with pytest.raises(UnsafeURLError):
            validate_url("data:text/html,<script>alert(1)</script>")

    def test_rejects_empty_url(self):
        with pytest.raises(UnsafeURLError):
            validate_url("")

    def test_rejects_url_without_host(self):
        with pytest.raises(UnsafeURLError):
            validate_url("http://")


class TestIPLiteralRules:
    def test_rejects_loopback_127(self):
        with pytest.raises(UnsafeURLError, match="loopback"):
            validate_url("http://127.0.0.1/")

    def test_rejects_loopback_localhost_via_dns(self, monkeypatch):
        # localhost is a hostname; resolution should yield 127.0.0.1
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("127.0.0.1"))
        with pytest.raises(UnsafeURLError, match="loopback"):
            validate_url("http://localhost/")

    def test_rejects_link_local_metadata(self):
        with pytest.raises(UnsafeURLError, match="link-local"):
            validate_url("http://169.254.169.254/latest/meta-data/")

    def test_rejects_private_10(self):
        with pytest.raises(UnsafeURLError, match="private"):
            validate_url("http://10.0.0.1/")

    def test_rejects_private_192_168(self):
        with pytest.raises(UnsafeURLError, match="private"):
            validate_url("http://192.168.1.1/")

    def test_rejects_private_172_16(self):
        with pytest.raises(UnsafeURLError, match="private"):
            validate_url("http://172.16.0.1/")

    def test_rejects_unspecified(self):
        with pytest.raises(UnsafeURLError):
            validate_url("http://0.0.0.0/")

    def test_rejects_ipv6_loopback(self):
        with pytest.raises(UnsafeURLError, match="loopback"):
            validate_url("http://[::1]/")

    def test_rejects_ipv6_link_local(self):
        with pytest.raises(UnsafeURLError, match="link-local"):
            validate_url("http://[fe80::1]/")


class TestDNSResolution:
    def test_rejects_when_dns_resolves_to_private_ip(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("10.0.0.42"))
        with pytest.raises(UnsafeURLError, match="private"):
            validate_url("http://example.com/")

    def test_accepts_when_dns_resolves_to_public_ip(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34"))
        validate_url("http://example.com/")  # no exception

    def test_rejects_when_dns_fails(self, monkeypatch):
        def _raise(*a, **kw):
            raise socket.gaierror(-2, "Name or service not known")

        monkeypatch.setattr(socket, "getaddrinfo", _raise)
        with pytest.raises(UnsafeURLError, match="could not be resolved"):
            validate_url("http://this-host-does-not-resolve.invalid/")

    def test_rejects_when_any_resolved_address_is_private(self, monkeypatch):
        # Multi-A record where one entry is public and another is private.
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34", "10.0.0.5"))
        with pytest.raises(UnsafeURLError, match="private"):
            validate_url("http://example.com/")


class TestAllowlist:
    def test_allowlist_rejects_other_domain(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34"))
        monkeypatch.setenv("SCRAPLING_MCP_ALLOWLIST", "internal.example")
        with pytest.raises(UnsafeURLError, match="allowlist"):
            validate_url("http://example.com/")

    def test_allowlist_accepts_exact_match(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34"))
        monkeypatch.setenv("SCRAPLING_MCP_ALLOWLIST", "example.com")
        validate_url("http://example.com/")

    def test_allowlist_accepts_subdomain(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34"))
        monkeypatch.setenv("SCRAPLING_MCP_ALLOWLIST", "example.com")
        validate_url("http://api.example.com/v1")

    def test_allowlist_does_not_match_partial_suffix(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34"))
        monkeypatch.setenv("SCRAPLING_MCP_ALLOWLIST", "example.com")
        with pytest.raises(UnsafeURLError, match="allowlist"):
            validate_url("http://notexample.com/")

    def test_allowlist_with_multiple_entries(self, monkeypatch):
        monkeypatch.setattr(socket, "getaddrinfo", _addrinfo_for("93.184.216.34"))
        monkeypatch.setenv("SCRAPLING_MCP_ALLOWLIST", "foo.test, example.com , bar.test")
        validate_url("http://example.com/")


class TestAllowLocalEscapeHatch:
    def test_env_var_bypasses_ip_blocks(self, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_ALLOW_LOCAL", "1")
        validate_url("http://127.0.0.1/")
        validate_url("http://10.0.0.1/")

    def test_explicit_param_bypasses_ip_blocks(self):
        validate_url("http://127.0.0.1/", allow_local=True)

    def test_allow_local_still_enforces_scheme(self, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_ALLOW_LOCAL", "1")
        with pytest.raises(UnsafeURLError):
            validate_url("file:///etc/passwd")

    def test_allow_local_still_enforces_allowlist(self, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_ALLOW_LOCAL", "1")
        monkeypatch.setenv("SCRAPLING_MCP_ALLOWLIST", "internal.test")
        with pytest.raises(UnsafeURLError, match="allowlist"):
            validate_url("http://127.0.0.1/")


class TestRequireHttpToken:
    def test_raises_when_token_missing(self):
        with pytest.raises(UnsafeURLError, match="SCRAPLING_MCP_TOKEN"):
            require_http_token()

    def test_returns_token_when_set(self, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "secret-value")
        assert require_http_token() == "secret-value"

    def test_raises_when_token_blank(self, monkeypatch):
        monkeypatch.setenv("SCRAPLING_MCP_TOKEN", "   ")
        with pytest.raises(UnsafeURLError):
            require_http_token()
