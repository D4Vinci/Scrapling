from dataclasses import dataclass, field

from scrapling.core._types import Any, Iterator, Dict, List, Tuple


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
    items: list[dict[str, Any]]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.items)
