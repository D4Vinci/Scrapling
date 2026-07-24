from base64 import b64encode, b64decode
from pathlib import Path

import orjson
import anyio
from anyio import Path as AsyncPath

from scrapling.core.utils import log
from scrapling.core._types import Dict, Optional, Any, Tuple
from scrapling.engines.toolbelt.custom import Response


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

            # Browser-engine cookies are cached as a JSON array (see `put`) and come back
            # as a `list`; restore the `tuple` shape `Response` expects. Static-engine
            # cookies are cached as a JSON object and come back as a `dict` already.
            cached_cookies = data["cookies"]
            cookies: Tuple[Dict[str, str], ...] | Dict[str, str] = (
                tuple(cached_cookies) if isinstance(cached_cookies, list) else cached_cookies
            )

            return Response(
                url=data["url"],
                content=b64decode(data["content"]),
                status=data["status"],
                reason=data["reason"],
                encoding=data["encoding"],
                cookies=cookies,
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
                    # Browser-engine responses store cookies as a `tuple` of full cookie
                    # dicts; static-engine responses store a flat `dict`. Preserve whichever
                    # shape it is instead of collapsing non-dict cookies to `{}`, which was
                    # silently dropping every cookie from browser-engine responses.
                    "cookies": list(response.cookies)
                    if isinstance(response.cookies, tuple)
                    else dict(response.cookies),
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
