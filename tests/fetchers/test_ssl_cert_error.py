import pytest
from scrapling.engines.toolbelt.proxy_rotation import is_ssl_verification_error
from curl_cffi.curl import CurlError


@pytest.mark.parametrize(
    "msg",
    [
        "curl: (60) SSL certificate problem: certificate has expired",
        "curl: (60) SSL certificate problem: certificate verify failed",
        "curl: (60) peer certificate cannot be authenticated with given CA certificates",
    ],
)
def test_is_ssl_verification_error_true(msg):
    assert is_ssl_verification_error(CurlError(msg)) is True


@pytest.mark.parametrize(
    "msg",
    [
        "curl: (7) Failed to connect",
        "curl: (28) Connection timed out",
        "connection refused",
    ],
)
def test_is_ssl_verification_error_false(msg):
    assert is_ssl_verification_error(CurlError(msg)) is False
