from base64 import b64encode, b64decode
from pathlib import Path

import orjson
import anyio
from anyio import Path as AsyncPath

from scrapling.core.utils import log
from scrapling.core._types import Dict, Optional, Any
from scrapling.engines.toolbelt.custom import Response


def _serialize_cookies(cookies: Any) -> Any:
    """Return a JSON-serializable form of ``Response.cookies``.

    Static-engine responses carry a flat ``dict``; browser-engine responses
    carry a tuple of full cookie dicts. Both shapes are preserved as-is so the
    replayed response is identical to the original.
    """
    if isinstance(cookies, dict):
        return dict(cookies)
    if isinstance(cookies, (tuple, list)):
        return [dict(cookie) for cookie in cookies]
    return {}


def _deserialize_cookies(cookies: Any) -> Any:
    """Restore the original ``Response.cookies`` shape written by ``_serialize_cookies``."""
    return tuple(cookies) if isinstance(cookies, list) else cookies


class ResponseCacheManager:
    """Caches HTTP responses to disk for replay during spider development."""

    def __init__(self, cache_dir: str | Path):
        self._cache_dir = AsyncPath(cache_dir)

    def _cache_path(self, fingerprint: bytes) -> AsyncPath:
        return self._cache_dir / f"{fingerprint.hex()}.json"

    async def get(self, fingerprint: bytes) -> Optional[Response]:
        path = self._cache_path(fingerprint)
        if not await path.exists():
            return None

        try:
            async with await anyio.open_file(path, "rb") as f:
                data: Dict[str, Any] = orjson.loads(await f.read())

            return Response(
                url=data["url"],
                content=b64decode(data["content"]),
                status=data["status"],
                reason=data["reason"],
                encoding=data["encoding"],
                cookies=_deserialize_cookies(data["cookies"]),
                headers=data["headers"],
                request_headers=data["request_headers"],
                method=data["method"],
            )
        except Exception as e:
            log.warning(f"Failed to read cached response for {fingerprint.hex()}: {e}")
            return None

    async def put(self, fingerprint: bytes, response: Response, method: str = "GET") -> None:
        await self._cache_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self._cache_path(fingerprint).with_suffix(".tmp")

        try:
            serialized = orjson.dumps(
                {
                    "url": response.url,
                    "content": b64encode(response.body).decode("ascii"),
                    "status": response.status,
                    "reason": response.reason,
                    "encoding": response.encoding,
                    "cookies": _serialize_cookies(response.cookies),
                    "headers": dict(response.headers),
                    "request_headers": dict(response.request_headers),
                    "method": method,
                }
            )
            async with await anyio.open_file(temp_path, "wb") as f:
                await f.write(serialized)

            await temp_path.replace(self._cache_path(fingerprint))
        except Exception as e:
            if await temp_path.exists():
                await temp_path.unlink()
            log.warning(f"Failed to cache response for {fingerprint.hex()}: {e}")

    async def clear(self) -> None:
        if not await self._cache_dir.exists():
            return
        async for entry in self._cache_dir.iterdir():
            if entry.suffix == ".json":
                await entry.unlink()
        log.info(f"Cleared response cache at {self._cache_dir}")
