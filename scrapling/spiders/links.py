"""Pure URL discovery primitive"""

import re
from urllib.parse import urlsplit

from w3lib.html import strip_html5_whitespace
from w3lib.url import canonicalize_url, safe_url_string

from scrapling.core._types import (
    TYPE_CHECKING,
    Iterable,
    Callable,
    List,
    Optional,
    Pattern,
    Set,
    Tuple,
    Union,
    Any,
)
from scrapling.core.utils import log

if TYPE_CHECKING:
    from scrapling.engines.toolbelt.custom import Response


__all__ = ["LinkExtractor"]
valid_schemas = {"http", "https", "file"}


IGNORED_EXTENSIONS = {
    # archives
    "7z",
    "7zip",
    "bz2",
    "rar",
    "tar",
    "tar.gz",
    "xz",
    "zip",
    # images
    "mng",
    "pct",
    "bmp",
    "gif",
    "jpg",
    "jpeg",
    "png",
    "pst",
    "psp",
    "tif",
    "tiff",
    "ai",
    "drw",
    "dxf",
    "eps",
    "ps",
    "svg",
    "cdr",
    "ico",
    "webp",
    # audio
    "mp3",
    "wma",
    "ogg",
    "wav",
    "ra",
    "aac",
    "mid",
    "au",
    "aiff",
    # video
    "3gp",
    "asf",
    "asx",
    "avi",
    "mov",
    "mp4",
    "mpg",
    "qt",
    "rm",
    "swf",
    "wmv",
    "m4a",
    "m4v",
    "flv",
    "webm",
    # office suites
    "xls",
    "xlsm",
    "xlsx",
    "xltm",
    "xltx",
    "potm",
    "potx",
    "ppt",
    "pptm",
    "pptx",
    "pps",
    "doc",
    "docb",
    "docm",
    "docx",
    "dotm",
    "dotx",
    "odt",
    "ods",
    "odg",
    "odp",
    # other
    "css",
    "pdf",
    "exe",
    "bin",
    "rss",
    "dmg",
    "iso",
    "apk",
    "jar",
    "sh",
    "rb",
    "js",
    "hta",
    "bat",
    "cpl",
    "msi",
    "msp",
    "py",
}


PatternInput = Iterable[Union[str, Pattern[str]]]
StrOrIterable = Union[str, Iterable[str]]


def _to_str_tuple(value: StrOrIterable) -> Tuple[str, ...]:
    if not value:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _compile_patterns(patterns: Union[str, Pattern[str], PatternInput, None]) -> Tuple[Pattern[str], ...]:
    if not patterns:
        return ()
    if isinstance(patterns, (str, re.Pattern)):
        patterns = (patterns,)
    return tuple(p if isinstance(p, re.Pattern) else re.compile(p) for p in patterns)


def _url_extension(url: str) -> str:
    extensions = _url_extensions(url)
    return extensions[0] if extensions else ""


def _url_extensions(url: str) -> Tuple[str, ...]:
    path = urlsplit(url).path
    _, _, last = path.rpartition("/")
    if "." not in last:
        return ()
    parts = last.lower().split(".")
    return tuple(".".join(parts[i:]) for i in range(1, len(parts)) if parts[i])


def _filler(x):
    return x


class LinkExtractor:
    """Extracts and filters URLs from a `Response` (or a single URL via `matches`).

    All matching is regex-based; allow/deny patterns can be plain strings (compiled
    with `re.compile`) or pre-compiled `re.Pattern` objects, individually or as an
    iterable.

    :param allow: Regex pattern(s) URLs must match to be kept. String, compiled `re.Pattern`,
        or an iterable of either. Empty means match all.
    :param deny: Regex pattern(s) URLs must NOT match. Takes precedence over `allow`.
    :param allow_domains: Domain(s) to keep. Matches the exact host or any subdomain
        (e.g. `"example.com"` matches `"api.example.com"`). String or iterable.
    :param deny_domains: Domain(s) to exclude. Same matching rules as `allow_domains`.
    :param restrict_css: CSS selectors to scope DOM extraction to. Empty means whole page.
    :param restrict_xpath: XPath selectors to scope DOM extraction to. Empty means whole page.
    :param tags: Element tags to look for links in. Default ("a", "area").
    :param attrs: Attributes on those tags to read URLs from. Default ("href",).
    :param canonicalize: Canonicalize URLs (sort query params, normalize path). Default True.
    :param strip: Strip whitespace from extracted URLs. Default True.
    :param keep_fragment: Preserve the URL fragment when canonicalizing. Default False.
    :param deny_extensions: File extensions to drop. Default `IGNORED_EXTENSIONS`.
    :param process: A function to do a process on the values extracted before using them. Return None to drop any value.
    """

    def __init__(
        self,
        allow: Union[str, Pattern[str], PatternInput] = (),
        deny: Union[str, Pattern[str], PatternInput] = (),
        allow_domains: StrOrIterable = (),
        deny_domains: StrOrIterable = (),
        restrict_css: StrOrIterable = (),
        restrict_xpath: StrOrIterable = (),
        tags: Iterable[str] = ("a", "area"),
        attrs: Iterable[str] = ("href",),
        canonicalize: bool = True,
        strip: bool = True,
        keep_fragment: bool = False,
        deny_extensions: Optional[Iterable[str]] = None,
        process: Callable[[Any], Any] | None = None,
    ) -> None:
        self.allow: Tuple[Pattern[str], ...] = _compile_patterns(allow)
        self.deny: Tuple[Pattern[str], ...] = _compile_patterns(deny)
        self.allow_domains: Tuple[str, ...] = tuple(d.lower() for d in _to_str_tuple(allow_domains))
        self.deny_domains: Tuple[str, ...] = tuple(d.lower() for d in _to_str_tuple(deny_domains))
        self.restrict_css: Tuple[str, ...] = _to_str_tuple(restrict_css)
        self.restrict_xpath: Tuple[str, ...] = _to_str_tuple(restrict_xpath)
        self.tags: Tuple[str, ...] = tuple(tags)
        self.attrs: Tuple[str, ...] = tuple(attrs)
        self.canonicalize = canonicalize
        self.strip = strip
        self.keep_fragment = keep_fragment
        self.deny_extensions: Set[str] = set(
            (ext.lower().lstrip(".") for ext in deny_extensions) if deny_extensions is not None else IGNORED_EXTENSIONS
        )
        self.process: Callable[[Any], Any] = process if callable(process) else _filler

    def extract(self, response: "Response") -> List[str]:
        """Return absolute, filtered, deduped URLs from `response`."""
        scopes: List[Any] = []
        if self.restrict_xpath:
            for xp in self.restrict_xpath:
                scopes.extend(response.xpath(xp))
        if self.restrict_css:
            for cs in self.restrict_css:
                scopes.extend(response.css(cs))
        if not scopes:
            scopes = [response]

        out: List[str] = []
        search_selector = "| ".join([f".//{tag}/@{attr}" for tag in self.tags for attr in self.attrs])
        for scope in scopes:
            for url in scope._root.xpath(search_selector):
                if not url:
                    continue
                url = str(url)
                if self.strip:
                    url = strip_html5_whitespace(url)
                    if not url:
                        continue
                url = str(response.urljoin(url))
                url = self.process(url)
                if not url:
                    continue

                if self.canonicalize:
                    url = canonicalize_url(url, keep_fragments=self.keep_fragment)

                try:
                    url = safe_url_string(url, encoding=response.encoding)
                except ValueError:
                    log.debug(f"Skipping the extraction of bad URL {url!r}")
                    continue

                if not self._url_passes(url):
                    continue

                out.append(url)

        # Switching to dict for deduplication instead of Set will keep the insertion order of the links.
        return list(dict.fromkeys(out))

    def matches(self, url: str) -> bool:
        """URL-only filter (no response extraction).

        Applies allow/deny/allow_domains/deny_domains/deny_extensions to a single URL.
        Used by `SitemapSpider` to dispatch sitemap URLs through `CrawlRule`s without
        needing a `Response`.
        """
        if self.canonicalize:
            url = canonicalize_url(url, keep_fragments=self.keep_fragment)
        return self._url_passes(url)

    def _url_passes(self, url: str) -> bool:
        if url.split("://", 1)[0] not in valid_schemas:
            return False

        if self.deny_extensions and any(ext in self.deny_extensions for ext in _url_extensions(url)):
            return False

        if self.allow and not any(p.search(url) for p in self.allow):
            return False
        if self.deny and any(p.search(url) for p in self.deny):
            return False

        if self.allow_domains or self.deny_domains:
            host = (urlsplit(url).hostname or "").lower()
            if self.allow_domains and not any(host == d or host.endswith("." + d) for d in self.allow_domains):
                return False
            if self.deny_domains and any(host == d or host.endswith("." + d) for d in self.deny_domains):
                return False
        return True
