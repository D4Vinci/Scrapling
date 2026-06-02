from base64 import b64encode, b64decode
from pathlib import Path
import time

import orjson
import anyio
from anyio import Path as AsyncPath

from scrapling.core.utils import log
from scrapling.core._types import Dict, Optional, Any
from scrapling.engines.toolbelt.custom import Response


class ResponseCacheManager:
    """Caches HTTP responses to disk for replay during spider development."""

    def __init__(
        self,
        cache_dir: str | Path,
        ttl_seconds: Optional[float] = None,
        max_entries: Optional[int] = 4096,
        max_bytes: Optional[int] = 512 * 1024 * 1024,
    ):
        self._cache_dir = AsyncPath(cache_dir)
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._max_bytes = max_bytes

    def _cache_path(self, fingerprint: bytes) -> AsyncPath:
        return self._cache_dir / f"{fingerprint.hex()}.json"

    async def _cache_entries(self) -> list[tuple[AsyncPath, float, int]]:
        if not await self._cache_dir.exists():
            return []
        entries: list[tuple[AsyncPath, float, int]] = []
        async for entry in self._cache_dir.iterdir():
            if entry.suffix != ".json":
                continue
            try:
                stat = await entry.stat()
                entries.append((entry, stat.st_mtime, stat.st_size))
            except OSError:
                continue
        return entries

    async def _prune(self) -> None:
        entries = await self._cache_entries()
        now = time.time()
        kept: list[tuple[AsyncPath, float, int]] = []
        for path, mtime, size in entries:
            expired = self._ttl_seconds is not None and now - mtime > self._ttl_seconds
            if expired:
                try:
                    await path.unlink()
                except OSError:
                    pass
            else:
                kept.append((path, mtime, size))

        kept.sort(key=lambda item: item[1])
        total = sum(size for _, _, size in kept)
        while self._max_entries is not None and len(kept) > self._max_entries:
            path, _, size = kept.pop(0)
            total -= size
            try:
                await path.unlink()
            except OSError:
                pass
        while self._max_bytes is not None and total > self._max_bytes and kept:
            path, _, size = kept.pop(0)
            total -= size
            try:
                await path.unlink()
            except OSError:
                pass

    async def get(self, fingerprint: bytes) -> Optional[Response]:
        path = self._cache_path(fingerprint)
        if not await path.exists():
            return None

        try:
            async with await anyio.open_file(path, "rb") as f:
                data: Dict[str, Any] = orjson.loads(await f.read())
            if self._ttl_seconds is not None and time.time() - float(data.get("created_at", 0.0)) > self._ttl_seconds:
                await path.unlink()
                return None

            cookies = data.get("cookies", {})
            if isinstance(cookies, list):
                cookies = tuple(cookies)

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

    @staticmethod
    def _serialize_cookies(cookies: Any) -> Any:
        if isinstance(cookies, dict):
            return dict(cookies)
        if isinstance(cookies, (list, tuple)):
            return [dict(cookie) if isinstance(cookie, dict) else cookie for cookie in cookies]
        return {}

    async def put(self, fingerprint: bytes, response: Response, method: str = "GET") -> None:
        await self._cache_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self._cache_path(fingerprint).with_suffix(".tmp")

        try:
            serialized = orjson.dumps(
                {
                    "created_at": time.time(),
                    "url": response.url,
                    "content": b64encode(response.body).decode("ascii"),
                    "status": response.status,
                    "reason": response.reason,
                    "encoding": response.encoding,
                    "cookies": self._serialize_cookies(response.cookies),
                    "headers": dict(response.headers),
                    "request_headers": dict(response.request_headers),
                    "method": method,
                }
            )
            async with await anyio.open_file(temp_path, "wb") as f:
                await f.write(serialized)

            await temp_path.rename(self._cache_path(fingerprint))
            await self._prune()
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
