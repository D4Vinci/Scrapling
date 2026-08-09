"""Shared helpers for template spiders."""

from gzip import GzipFile
from io import BytesIO

from scrapling.core._types import Optional

__all__ = ["_decompress"]

_GZIP_MAGIC = b"\x1f\x8b"
_GUNZIP_MAX_SIZE = 64 * 1024 * 1024  # 64 MiB cap, defends against gzip bombs


def _decompress(body: bytes, content_type: Optional[str]) -> bytes:
    """Gunzip `body` when the content-type or the magic bytes say it's gzipped, capped against gzip bombs."""
    if (content_type and ("gzip" in content_type.lower())) or (body[:2] == _GZIP_MAGIC):
        out = bytearray()
        with GzipFile(fileobj=BytesIO(body)) as f:
            while chunk := f.read1(8192):
                out.extend(chunk)
                if len(out) > _GUNZIP_MAX_SIZE:
                    raise OSError(f"gzip output exceeds {_GUNZIP_MAX_SIZE} bytes")
        return bytes(out)
    return body
