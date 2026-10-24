from pathlib import Path

import orjson
import anyio
from anyio import Path as AsyncPath

from scrapling.core.utils import log
from scrapling.core._types import Any, Dict, Mapping, Optional
from scrapling.engines.toolbelt.custom import Response

# Headers that make a request conditional; a request that already sends one is left to its author
CONDITIONAL_HEADERS = frozenset({"if-none-match", "if-modified-since", "if-match", "if-unmodified-since", "if-range"})


def _get_header(headers: Mapping[str, Any], name: str) -> Optional[str]:
    """Case-insensitive header lookup, since engines don't agree on the case of header names."""
    for key, value in headers.items():
        if key.lower() == name:
            return str(value)
    return None


class ConditionalRequestManager:
    """Saves the validators (`ETag` / `Last-Modified`) of processed responses to disk, so the next run can ask the
    website whether each page changed instead of downloading it again."""

    def __init__(self, validators_dir: str | Path):
        self._validators_dir = AsyncPath(validators_dir)

    def _validators_path(self, fingerprint: bytes) -> AsyncPath:
        return self._validators_dir / f"{fingerprint.hex()}.json"

    async def get_headers(self, fingerprint: bytes) -> Dict[str, str]:
        """Return the `If-None-Match` / `If-Modified-Since` headers for a request, empty if nothing was saved for it."""
        path = self._validators_path(fingerprint)
        if not await path.exists():
            return {}

        try:
            async with await anyio.open_file(path, "rb") as f:
                data: Dict[str, Any] = orjson.loads(await f.read())
        except Exception as e:
            log.warning(f"Failed to read saved validators for {fingerprint.hex()}: {e}")
            return {}

        headers = {}
        if data.get("etag"):
            headers["If-None-Match"] = data["etag"]
        if data.get("last_modified"):
            headers["If-Modified-Since"] = data["last_modified"]
        return headers

    async def put(self, fingerprint: bytes, response: Response) -> None:
        """Save the response's validators, or drop the saved ones when the website stopped sending any."""
        path = self._validators_path(fingerprint)
        headers = response.headers or {}
        etag = _get_header(headers, "etag")
        last_modified = _get_header(headers, "last-modified")
        if not etag and not last_modified:
            if await path.exists():
                await path.unlink()
            return

        await self._validators_dir.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(".tmp")
        try:
            serialized = orjson.dumps({"url": response.url, "etag": etag, "last_modified": last_modified})
            async with await anyio.open_file(temp_path, "wb") as f:
                await f.write(serialized)

            await temp_path.replace(path)
        except Exception as e:
            if await temp_path.exists():
                await temp_path.unlink()
            log.warning(f"Failed to save validators for {fingerprint.hex()}: {e}")

    async def clear(self) -> None:
        if not await self._validators_dir.exists():
            return
        async for entry in self._validators_dir.iterdir():
            if entry.suffix == ".json":
                await entry.unlink()
        log.info(f"Cleared saved validators at {self._validators_dir}")
