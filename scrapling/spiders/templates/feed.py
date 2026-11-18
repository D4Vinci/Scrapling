"""Feed template spiders for XML, CSV, and JSON feeds."""

from copy import deepcopy
from csv import DictReader
from io import StringIO

from orjson import JSONDecodeError, loads

from lxml import etree
from lxml.etree import _Element

from scrapling.core._types import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)
from scrapling.spiders.request import Request
from scrapling.spiders.spider import Spider
from scrapling.spiders.templates._utils import _decompress

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


__all__ = ["XMLFeedSpider", "CSVFeedSpider", "JSONFeedSpider"]


class XMLFeedSpider(Spider):
    """A Spider that iterates over the nodes of an XML feed (RSS, Atom, product feeds, etc.).

    Override `parse_node()` to process each node matching `itertag`. Gzipped feeds are decompressed automatically.

    Each node is passed as a namespace-stripped `lxml` element, so `node.findtext("title")` and case-sensitive
    `node.xpath(...)` work on any feed without namespace maps.

    :cvar itertag: Name of the node to iterate over. A plain name ("item") matches regardless of namespace;
        a prefixed name ("media:content") matches only the namespace the prefix maps to in `namespaces`.
    :cvar namespaces: Tuple of `(prefix, uri)` pairs defining the prefixes usable in `itertag`.
    """

    itertag: str = "item"
    namespaces: Tuple[Tuple[str, str], ...] = ()

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Iterate over the feed's `itertag` nodes and dispatch each one to `parse_node`."""
        content_type = response.headers.get("content-type") if response.headers else None
        try:
            body = _decompress(response.body, content_type)
        except OSError as e:
            self.logger.warning(f"Failed to decompress feed: {e}")
            return

        try:
            root = etree.fromstring(body)
        except etree.XMLSyntaxError as e:
            self.logger.warning(f"Failed to parse XML feed from {response.url}: {e}")
            return

        for node in self._iter_nodes(root):
            async for result in self.parse_node(response, node):
                yield result

    async def parse_node(
        self, response: "Response", node: _Element
    ) -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Override to process one feed node; `node` is a namespace-stripped `lxml` element."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse_node() method")
        yield  # Make this a generator for type checkers

    def _wanted_tag(self) -> Tuple[Optional[str], str]:
        """Resolve `itertag` into a `(namespace uri or None, localname)` pair."""
        prefix, _, name = self.itertag.rpartition(":")
        if not prefix:
            return None, name
        uri = dict(self.namespaces).get(prefix)
        if not uri:
            raise ValueError(f"`itertag` prefix {prefix!r} is not defined in `namespaces`")
        return uri, name

    def _iter_nodes(self, root: _Element) -> Iterator[_Element]:
        uri, name = self._wanted_tag()
        for el in root.iter():
            if isinstance(el.tag, str):
                qname = etree.QName(el.tag)
                if qname.localname == name and (uri is None or qname.namespace == uri):
                    yield self._strip_namespaces(el)

    @staticmethod
    def _strip_namespaces(node: _Element) -> _Element:
        """Return a copy of `node` with namespaces removed from every tag and attribute."""
        node = deepcopy(node)
        for el in node.iter():
            if isinstance(el.tag, str):
                el.tag = etree.QName(el.tag).localname
            for key in list(el.attrib):
                if isinstance(key, str) and key.startswith("{"):
                    el.attrib[etree.QName(key).localname] = el.attrib.pop(key)
        etree.cleanup_namespaces(node)
        return node


class CSVFeedSpider(Spider):
    """A Spider that iterates over the rows of a CSV feed.

    Override `parse_row()` to process each row as a dictionary. Gzipped feeds are decompressed automatically.

    :cvar delimiter: The character separating fields.
    :cvar quotechar: The character enclosing fields that contain special characters.
    :cvar headers: The column names. When left unset, the first row of the feed is used as the header.
    """

    delimiter: str = ","
    quotechar: str = '"'
    headers: Optional[List[str]] = None

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Read the feed's rows and dispatch each one to `parse_row`."""
        content_type = response.headers.get("content-type") if response.headers else None
        try:
            body = _decompress(response.body, content_type)
        except OSError as e:
            self.logger.warning(f"Failed to decompress feed: {e}")
            return

        # Spreadsheet exports often start with a BOM, which would otherwise end up in the first column name
        text = body.decode(response.encoding or "utf-8", errors="replace").removeprefix("\N{BYTE ORDER MARK}")
        reader = DictReader(
            StringIO(text, newline=""), fieldnames=self.headers, delimiter=self.delimiter, quotechar=self.quotechar
        )
        for row in reader:
            async for result in self.parse_row(response, dict(row)):
                yield result

    async def parse_row(
        self, response: "Response", row: Dict[str, Any]
    ) -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Override to process one feed row as a `{column: value}` dictionary."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse_row() method")
        yield  # Make this a generator for type checkers


class JSONFeedSpider(Spider):
    """A Spider that reads JSON Feed items and follows paginated feeds.

    Override `parse_item()` to process each item as a dictionary. Item fields, including custom extensions,
    are passed through unchanged. Gzipped feeds are decompressed automatically.

    :cvar follow_next: Follow the feed's `next_url` using the normal scheduler and duplicate filtering.
    """

    follow_next: bool = True

    async def parse(self, response: "Response") -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Dispatch each JSON Feed item, then schedule the next page when present."""
        content_type = response.headers.get("content-type") if response.headers else None
        try:
            feed = loads(_decompress(response.body, content_type))
        except (OSError, JSONDecodeError) as e:
            self.logger.warning(f"Failed to read JSON feed: {e}")
            return
        if not isinstance(feed, dict) or not isinstance(feed.get("items"), list):
            self.logger.warning("JSON feed must contain an items array")
            return

        for item in feed["items"]:
            if not isinstance(item, dict):
                self.logger.warning("Skipping a JSON feed item that is not an object")
                continue
            async for result in self.parse_item(response, item):
                yield result

        next_url = feed.get("next_url")
        if self.follow_next and next_url:
            if not isinstance(next_url, str):
                self.logger.warning("JSON feed next_url must be a string")
                return
            yield response.follow(next_url, callback=self.parse)

    async def parse_item(
        self, response: "Response", item: Dict[str, Any]
    ) -> AsyncGenerator[Union[Dict[str, Any], Request, None], None]:
        """Override to process a JSON Feed item or follow its article URL."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse_item() method")
        yield  # Make this a generator for type checkers
