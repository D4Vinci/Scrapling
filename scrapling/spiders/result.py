import csv
import re
from pathlib import Path
from dataclasses import dataclass, field
from xml.etree.ElementTree import (  # nosec B405 - we only serialize items, nothing here parses XML
    Element,
    ElementTree,
    SubElement,
    indent as indent_tree,
)

import orjson

from scrapling.core.utils import log
from scrapling.core._types import Any, Iterable, Iterator, Dict, List, Optional, Tuple, Union

# Anything outside these ranges can't be represented in XML, and scraped pages are full of control characters
_XML_FORBIDDEN_CHARS = re.compile(r"[^\x09\x0a\x0d\x20-퟿-�\U00010000-\U0010ffff]")
_XML_FORBIDDEN_TAG_CHARS = re.compile(r"[^\w.-]", re.UNICODE)


def _stringify(value: Any) -> str:
    """Turn an item's value into text, serializing containers to JSON so no data is silently dropped."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return orjson.dumps(value, option=orjson.OPT_SERIALIZE_NUMPY).decode()
    return str(value)


def _xml_tag(key: Any) -> str:
    """Turn an item's key into a usable XML tag name."""
    tag = _XML_FORBIDDEN_TAG_CHARS.sub("_", str(key))
    return tag if tag and (tag[0].isalpha() or tag[0] == "_") else f"_{tag}"


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

    def to_csv(self, path: Union[str, Path], *, fields: Optional[Iterable[str]] = None, delimiter: str = ","):
        """Export items to a CSV file.

        Items that don't share the same keys are still written, with the missing cells left empty, and any value
        that isn't a scalar (a nested dictionary or a list) is written as JSON.

        :param path: Path to the output file
        :param fields: The columns to write, defaulting to every key found in the items, in the order they appeared
        :param delimiter: The character separating the columns
        """
        columns = list(fields) if fields is not None else list({key: None for item in self for key in item})

        file = Path(path)
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, delimiter=delimiter, extrasaction="ignore")
            writer.writeheader()
            for item in self:
                writer.writerow({column: _stringify(item.get(column)) for column in columns})

        log.info("Saved %d items to %s", len(self), path)

    def to_xml(self, path: Union[str, Path], *, root_tag: str = "items", item_tag: str = "item", indent: bool = True):
        """Export items to an XML file.

        Each item becomes an element whose children are named after the item's keys. Keys that aren't valid XML
        names are rewritten and keep the original in a `name` attribute, and any value that isn't a scalar
        (a nested dictionary or a list) is written as JSON.

        :param path: Path to the output file
        :param root_tag: The name of the element wrapping all the items
        :param item_tag: The name of the element wrapping every item
        :param indent: Pretty-print the file instead of writing it on a single line
        """
        root = Element(root_tag)
        for item in self:
            element = SubElement(root, item_tag)
            for key, value in item.items():
                tag = _xml_tag(key)
                child = SubElement(element, tag)
                if tag != str(key):
                    child.set("name", _XML_FORBIDDEN_CHARS.sub("", str(key)))
                child.text = _XML_FORBIDDEN_CHARS.sub("", _stringify(value))

        tree = ElementTree(root)
        if indent:
            indent_tree(tree, space="  ")

        file = Path(path)
        file.parent.mkdir(parents=True, exist_ok=True)
        tree.write(file, encoding="utf-8", xml_declaration=True)
        log.info("Saved %d items to %s", len(self), path)


@dataclass
class CrawlStats:
    """Statistics for a crawl run."""

    requests_count: int = 0
    concurrent_requests: int = 0
    concurrent_requests_per_domain: int = 0
    failed_requests_count: int = 0
    offsite_requests_count: int = 0
    robots_disallowed_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    response_bytes: int = 0
    items_scraped: int = 0
    items_dropped: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    download_delay: float = 0.0
    autothrottle_enabled: bool = False
    blocked_requests_count: int = 0
    autothrottle_delays: Dict = field(default_factory=dict)
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
            "autothrottle_enabled": self.autothrottle_enabled,
            "autothrottle_delays": {domain: round(delay, 2) for domain, delay in self.autothrottle_delays.items()},
            "concurrent_requests": self.concurrent_requests,
            "concurrent_requests_per_domain": self.concurrent_requests_per_domain,
            "requests_count": self.requests_count,
            "requests_per_second": round(self.requests_per_second, 2),
            "sessions_requests_count": self.sessions_requests_count,
            "failed_requests_count": self.failed_requests_count,
            "offsite_requests_count": self.offsite_requests_count,
            "robots_disallowed_count": self.robots_disallowed_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
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
