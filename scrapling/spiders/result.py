from pathlib import Path
from dataclasses import dataclass, field

import orjson

from scrapling.core.utils import log
from scrapling.core._types import Any, Iterator, Dict, List, Tuple, Union


class ItemList(list):
    """A list of scraped items with export capabilities."""

    def to_json(self, path: Union[str, Path], *, indent: bool = False):
        """Export items to a JSON file.

        :param path: Path to the output file
        :param indent: Pretty-print with 2-space indentation (slightly slower)
        """
        options = orjson.OPT_SERIALIZE_NUMPY
        if indent:
            options |= orjson.OPT_INDENT_2

        file = Path(path)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(orjson.dumps(list(self), option=options))
        log.info("Saved %d items to %s", len(self), path)

    def to_jsonl(self, path: Union[str, Path]):
        """Export items as JSON Lines (one JSON object per line).

        :param path: Path to the output file
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            for item in self:
                f.write(orjson.dumps(item, option=orjson.OPT_SERIALIZE_NUMPY))
                f.write(b"\n")
        log.info("Saved %d items to %s", len(self), path)


@dataclass
class CrawlStats:
    """Statistics for a crawl run."""

    requests_count: int = 0
    concurrent_requests: int = 0
    concurrent_requests_per_domain: int = 0
    failed_requests_count: int = 0
    offsite_requests_count: int = 0
    response_bytes: int = 0
    items_scraped: int = 0
    items_dropped: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    download_delay: float = 0.0
    blocked_requests_count: int = 0
    custom_stats: Dict = field(default_factory=dict)
    response_status_count: Dict = field(default_factory=dict)
    domains_response_bytes: Dict = field(default_factory=dict)
    sessions_requests_count: Dict = field(default_factory=dict)
    proxies: List[str | Dict | Tuple] = field(default_factory=list)
    log_levels_counter: Dict = field(default_factory=dict)

    @property
    def elapsed_seconds(self) -> float:
        return self.end_time - self.start_time

    @property
    def requests_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return 0.0
        return self.requests_count / self.elapsed_seconds

    def increment_status(self, status: int) -> None:
        self.response_status_count[f"status_{status}"] = self.response_status_count.get(f"status_{status}", 0) + 1

    def increment_response_bytes(self, domain: str, count: int) -> None:
        self.response_bytes += count
        self.domains_response_bytes[domain] = self.domains_response_bytes.get(domain, 0) + count

    def increment_requests_count(self, sid: str) -> None:
        self.requests_count += 1
        self.sessions_requests_count[sid] = self.sessions_requests_count.get(sid, 0) + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "items_scraped": self.items_scraped,
            "items_dropped": self.items_dropped,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "download_delay": round(self.download_delay, 2),
            "concurrent_requests": self.concurrent_requests,
            "concurrent_requests_per_domain": self.concurrent_requests_per_domain,
            "requests_count": self.requests_count,
            "requests_per_second": round(self.requests_per_second, 2),
            "sessions_requests_count": self.sessions_requests_count,
            "failed_requests_count": self.failed_requests_count,
            "offsite_requests_count": self.offsite_requests_count,
            "blocked_requests_count": self.blocked_requests_count,
            "response_status_count": self.response_status_count,
            "response_bytes": self.response_bytes,
            "domains_response_bytes": self.domains_response_bytes,
            "proxies": self.proxies,
            "custom_stats": self.custom_stats,
            "log_count": self.log_levels_counter,
        }


@dataclass
class CrawlResult:
    """Complete result from a spider run."""

    stats: CrawlStats
    items: ItemList
    paused: bool = False

    @property
    def completed(self) -> bool:
        """True if the crawl completed normally (not paused)."""
        return not self.paused

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.items)
