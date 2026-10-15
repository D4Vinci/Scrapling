"""Generic spider templates that build on the `Spider` base."""

from dataclasses import dataclass

from scrapling.spiders.links import LinkExtractor
from scrapling.spiders.request import Request
from scrapling.spiders.spider import Spider
from scrapling.core._types import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Union,
)

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


__all__ = ["CrawlRule", "CrawlSpider"]


ParseCallback = Callable[
    ["Response"],
    AsyncGenerator[Union[Dict[str, Any], Request, None], None],
]
ProcessRequestFn = Callable[[Request, "Response"], Request]


@dataclass
class CrawlRule:
    """Rule for `CrawlSpider`: extract links from a response and dispatch them.

    :param link_extractor: `LinkExtractor` that produces URLs from each response.
    :param callback: Bound method on the spider to call for each matched URL.
        Falls back to the spider's default ``parse()`` by default.
    :param priority: Override the priority of the requests that will be dispatched.
    :param process_request: Optional bound method to mutate each `Request` before
        it is yielded. Signature: ``(request, response) -> request``. Use it to
        add headers, change priority, or filter requests.
    """

    link_extractor: LinkExtractor
    callback: Optional[ParseCallback] = None
    priority: Optional[int] = None
    process_request: Optional[ProcessRequestFn] = None


class CrawlSpider(Spider):
    """A generic spider that can extract and follow links automatically based on crawl rules.

    Override `rules()` to return a list of `CrawlRule`s.

    You can start from it and override it as needed for more custom functionality, or just implement your own spider.
    """

    crawl_strategy: Literal["bfs", "dfs"] = "bfs"

    def rules(self) -> List[CrawlRule]:
        """Override to define link-following rules."""
        return []

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        for rule in self.rules():
            for url in rule.link_extractor.extract(response):
                req = response.follow(url, callback=rule.callback)
                if rule.priority is not None:
                    req.priority = rule.priority
                if rule.process_request is not None:
                    req = rule.process_request(req, response)
                yield req
