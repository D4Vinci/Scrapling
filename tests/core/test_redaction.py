from scrapling.core.utils.redaction import redact_headers, redact_mapping, redact_proxy, redact_url_userinfo


def test_redact_url_userinfo_removes_credentials():
    assert redact_url_userinfo("http://user:pass@example.com:8080/a") == "http://***@example.com:8080/a"


def test_redact_proxy_supports_url_and_mapping_forms():
    assert redact_proxy("http://user:pass@proxy.local:8080") == "http://***@proxy.local:8080"
    assert redact_proxy({"http": "http://u:p@proxy:8080", "https": "http://proxy:8080"}) == {
        "http": "http://***@proxy:8080",
        "https": "http://proxy:8080",
    }
    assert redact_proxy({"server": "http://proxy:8080", "username": "u", "password": "p"}) == {
        "server": "http://proxy:8080",
        "username": "***",
        "password": "***",
    }


def test_redact_headers_and_nested_mapping():
    headers = redact_headers({"Authorization": "Bearer secret", "X-Trace": "abc", "Cookie": "sid=secret"})
    assert headers == {"Authorization": "***", "X-Trace": "abc", "Cookie": "***"}

    nested = redact_mapping({"proxy": "http://u:p@proxy:8080", "headers": {"X-Api-Key": "secret", "Accept": "*/*"}})
    assert nested["proxy"] == "http://***@proxy:8080"
    assert nested["headers"]["X-Api-Key"] == "***"
    assert nested["headers"]["Accept"] == "*/*"
