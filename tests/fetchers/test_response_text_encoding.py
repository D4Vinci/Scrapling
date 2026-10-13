import pytest

from scrapling.engines.toolbelt.custom import Response


@pytest.mark.parametrize("encoding", ["utf-8", "iso-8859-1", "windows-1252", "utf-16"])
def test_unicode_response_content_uses_selected_encoding(encoding):
    content = "<html><body><p>café</p></body></html>"
    response = Response("https://example.test/", content, 200, "OK", {}, {}, {}, encoding=encoding)
    assert response.css("p::text").get() == "café"
    assert response.body == content.encode(encoding)
    assert response.encoding == encoding


def test_byte_response_preserves_original_body():
    content = b"<p>caf\xe9</p>"
    response = Response("https://example.test/", content, 200, "OK", {}, {}, {}, encoding="iso-8859-1")
    assert response.css("p::text").get() == "café"
    assert response.body == content
