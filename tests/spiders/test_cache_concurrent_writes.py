from pathlib import Path

import anyio
import pytest

from scrapling.engines.toolbelt.custom import Response
from scrapling.spiders.cache import ResponseCacheManager


@pytest.mark.anyio
async def test_concurrent_writers_use_independent_temporary_files(tmp_path, monkeypatch, caplog):
    fingerprint = b"shared-request"
    ready = anyio.Event()
    first_ready = anyio.Event()
    paths = []
    original_replace = anyio.Path.replace

    async def synchronized_replace(source, target):
        paths.append(str(source))
        first_ready.set()
        if len(paths) == 2:
            ready.set()
        await ready.wait()
        return await original_replace(source, target)

    monkeypatch.setattr(anyio.Path, "replace", synchronized_replace)

    async def write(body):
        response = Response(
            url="https://example.com",
            content=body,
            status=200,
            reason="OK",
            encoding="utf-8",
            cookies={},
            headers={},
            request_headers={},
            method="GET",
        )
        await ResponseCacheManager(tmp_path).put(fingerprint, response)

    with anyio.fail_after(10):
        async with anyio.create_task_group() as tasks:
            tasks.start_soon(write, b"<html>first</html>")
            await first_ready.wait()
            tasks.start_soon(write, b"<html>second response</html>")

    assert "Failed to cache response" not in caplog.text
    assert len(set(paths)) == 2
    response = await ResponseCacheManager(tmp_path).get(fingerprint)
    assert response is not None
    assert response.body in (b"<html>first</html>", b"<html>second response</html>")
    assert list(Path(tmp_path).glob("*.tmp")) == []


@pytest.mark.anyio
async def test_failed_replacement_keeps_previous_response(tmp_path, monkeypatch):
    cache = ResponseCacheManager(tmp_path)
    fingerprint = b"existing-request"

    def response(body):
        return Response(
            url="https://example.com",
            content=body,
            status=200,
            reason="OK",
            encoding="utf-8",
            cookies={},
            headers={},
            request_headers={},
            method="GET",
        )

    await cache.put(fingerprint, response(b"<html>original</html>"))

    async def fail_replace(source, target):
        raise OSError("replacement unavailable")

    monkeypatch.setattr(anyio.Path, "replace", fail_replace)
    await cache.put(fingerprint, response(b"<html>replacement</html>"))
    restored = await cache.get(fingerprint)
    assert restored is not None
    assert restored.body == b"<html>original</html>"
    assert list(Path(tmp_path).glob("*.tmp")) == []
