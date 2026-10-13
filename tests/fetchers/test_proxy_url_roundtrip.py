from urllib.parse import urlsplit

import pytest

from scrapling.engines._browsers._validators import PlaywrightConfig, StealthConfig
from scrapling.engines.toolbelt.navigation import construct_proxy_dict


@pytest.mark.parametrize("config_type", [PlaywrightConfig, StealthConfig])
@pytest.mark.parametrize("scheme", ["http", "https", "socks4", "socks5"])
def test_ipv6_proxy_keeps_bracketed_server(config_type, scheme):
    value = f"{scheme}://[2001:db8::1]:1080"
    config = config_type(proxy=value)
    assert config.proxy["server"] == value
    parsed = urlsplit(config.proxy["server"])
    assert parsed.hostname == "2001:db8::1"
    assert parsed.port == 1080


def test_proxy_credentials_decode_url_escapes_once():
    proxy = construct_proxy_dict("http://user%40example:p%3Ass%2521@localhost:8080")
    assert proxy == {
        "server": "http://localhost:8080",
        "username": "user@example",
        "password": "p:ss%21",
    }


def test_plain_proxy_credentials_and_hostname_are_preserved():
    assert construct_proxy_dict("http://user:pass@localhost:8080") == {
        "server": "http://localhost:8080",
        "username": "user",
        "password": "pass",
    }
