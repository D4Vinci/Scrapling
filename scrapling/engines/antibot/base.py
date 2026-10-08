"""Shared types for the anti-bot handlers.

A handler knows one bot-protection vendor. ``detect`` recognises that vendor's challenge, captcha or block from a
:class:`Signal` (what the browser holds after a navigation); ``solve`` tries to get the page past it before a
deadline. Detection is pure: it reads the signal only, performs no I/O, and is safe to run on every response,
including ones that never touched a browser.

Rules every handler follows:

* ``detect`` never flags a content page only because it loads the vendor's sensor script or carries its cookies.
  Protected sites keep both on every page they serve, so detection needs a challenge marker, a blocking status with
  a gate-sized page, or a vendor header that is only sent on a block.
* ``solve`` never runs past ``deadline`` (a :func:`time.monotonic` value), never navigates away from the target
  origin except to the vendor's own challenge frames, and never types anything except into the vendor's widget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from html import unescape
from re import compile as re_compile
from time import monotonic
from urllib.parse import urlsplit

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Iterable, List, Literal, Optional, Protocol, Tuple

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = [
    "Kind",
    "KINDS",
    "SOLVABLE_KINDS",
    "MAX_HTML_CHARS",
    "GATE_TEXT",
    "VENDOR_MARKERS",
    "Signal",
    "Detection",
    "SolveResult",
    "Handler",
    "host_matches",
    "cookie_domain_matches",
    "visible_text",
    "remaining",
    "page_signal",
]

#: What a detection means for the caller.
#:
#: * ``device_check``: an invisible check (proof of work, fingerprint) that a real browser clears by itself.
#: * ``challenge``: an interstitial that needs the browser to run the vendor's script, maybe with one click.
#: * ``captcha``: an interactive widget (slider, press and hold, image puzzle, Turnstile/hCaptcha box).
#: * ``block``: the request was refused; solving cannot change it on this visit.
#: * ``ban``: the vendor has banned this client or IP; retrying only makes it worse.
Kind = Literal["device_check", "challenge", "captcha", "block", "ban"]
KINDS: Tuple[str, ...] = ("device_check", "challenge", "captcha", "block", "ban")
#: Kinds a handler may try to get past; ``block`` and ``ban`` are final verdicts for this visit. The session runner
#: (:mod:`scrapling.engines.antibot.runner`) still calls ``solve`` for a ``block``, so a handler with a same-origin
#: retry (Akamai's warm-up) can use it; other handlers return at once for kinds they cannot change.
SOLVABLE_KINDS = frozenset({"device_check", "challenge", "captcha"})

#: The longest DOM head a signal keeps (2 MiB of characters).
MAX_HTML_CHARS = 2 * 1024 * 1024
#: Below this many characters of visible text a page reads as a gate, not as content. Vendor block and challenge
#: pages show a sentence or two; a page that quotes a vendor's wording in an article shows far more.
GATE_TEXT = 2048

#: Lower-case strings that only appear on a vendor's challenge or block pages (not on pages that merely load the
#: vendor's sensor). Handlers use them to step aside when another vendor's challenge is on the page.
VENDOR_MARKERS: Dict[str, Tuple[str, ...]] = {
    "cloudflare": ("window._cf_chl_opt", "/cdn-cgi/challenge-platform/h/", "cf-turnstile-response", "ctype: '"),
    "datadome": ("captcha-delivery.com", "var dd={", "var dd ="),
    "perimeterx": ("px-captcha", "captcha.px-cdn.net", "captcha.px-cloud.net"),
    "akamai": ("sec-if-cpt-container", "sec-bc-tile-container", "/_sec/cp_challenge/", "/.well-known/sbsd"),
    "kasada": ("kpsdk", "/ips.js", "/149e9513-01fa-4fb0-aad4-566afd725d1b/"),
    "imperva": ("_incapsula_resource", "pardon our interruption", "incapsula incident id"),
    "aws_waf": ("gokuprops", "awswafintegration", "token.awswaf.com", "awswafcaptcha"),
}

_DROP_BLOCKS = re_compile(r"(?is)<(head|script|style|noscript|template|svg)\b[^>]*>.*?</\1\s*>")
_COMMENTS = re_compile(r"(?s)<!--.*?-->")
_TAGS = re_compile(r"(?s)<[^>]*>")
_SPACES = re_compile(r"\s+")
_TITLE = re_compile(r"(?is)<title\b[^>]*>(.*?)</title\s*>")


def visible_text(html: str) -> str:
    """Approximate the page's ``innerText``: drop head, scripts, styles and tags, unescape, collapse whitespace."""
    if not html:
        return ""
    text = _COMMENTS.sub(" ", html)
    text = _DROP_BLOCKS.sub(" ", text)
    text = _TAGS.sub(" ", text)
    return _SPACES.sub(" ", unescape(text)).strip()


def host_matches(url: str, *domains: str) -> bool:
    """True if ``url`` is http(s) and its host is one of ``domains`` or a subdomain of one.

    Matching the parsed host (not a substring of the URL) means ``https://evil.test/?x=captcha-delivery.com`` or
    ``https://captcha-delivery.com.evil.test/`` never counts as the vendor's frame.
    """
    try:
        parts = urlsplit(url or "")
        host = (parts.hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not host:
        return False
    for domain in domains:
        domain = domain.lower().strip(".")
        if host == domain or host.endswith("." + domain):
            return True
    return False


def cookie_domain_matches(host: str, cookie_domain: str) -> bool:
    """RFC 6265 domain match: would a cookie set for ``cookie_domain`` be sent to ``host``?"""
    host = (host or "").lower().rstrip(".")
    domain = (cookie_domain or "").lower().lstrip(".").rstrip(".")
    return bool(host) and bool(domain) and (host == domain or host.endswith("." + domain))


def remaining(deadline: float) -> float:
    """Seconds left before ``deadline`` (a :func:`time.monotonic` value), never negative."""
    return max(0.0, deadline - monotonic())


@dataclass
class Signal:
    """What the browser holds after a navigation; the only input of :meth:`Handler.detect`.

    :param url: The page URL after redirects.
    :param status: The main document's final HTTP status, or ``None`` when unknown (for example a re-check after a
        solve, where the page was read without its response).
    :param headers: The main document's response headers. Keys are lower-cased on construction; a list value
        (repeated header) is joined with ``", "``.
    :param cookies: Cookie names to values, for the page's own site only (cookies that would be sent to ``url``).
    :param html: The serialised DOM (or the response text), cut to :data:`MAX_HTML_CHARS` characters.
    :param frame_urls: The URLs of the page's child frames (the main frame is not included).
    """

    url: str
    status: Optional[int]
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    html: str = ""
    frame_urls: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        headers: Dict[str, str] = {}
        for key, value in (self.headers or {}).items():
            name = str(key).strip().lower()
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(v) for v in value)
            value = str(value)
            headers[name] = f"{headers[name]}, {value}" if name in headers else value
        self.headers = headers
        self.cookies = {str(k): str(v) for k, v in (self.cookies or {}).items()}
        self.html = (self.html or "")[:MAX_HTML_CHARS]
        self.frame_urls = [u for u in (self.frame_urls or ()) if isinstance(u, str) and u]
        self.url = self.url or ""
        self.status = int(self.status) if self.status is not None else None

    # -- derived views (computed once, on first use) ---------------------------------------------------------

    @cached_property
    def lower(self) -> str:
        """The HTML, lower-cased."""
        return self.html.lower()

    @cached_property
    def text(self) -> str:
        """The page's visible text (see :func:`visible_text`)."""
        return visible_text(self.html)

    @cached_property
    def title(self) -> str:
        """The first ``<title>``, unescaped, whitespace-collapsed and lower-cased (``""`` when there is none)."""
        match = _TITLE.search(self.html)
        return _SPACES.sub(" ", unescape(match.group(1))).strip().lower() if match else ""

    @cached_property
    def host(self) -> str:
        """The page URL's host, lower-cased."""
        try:
            return (urlsplit(self.url).hostname or "").lower()
        except ValueError:
            return ""

    # -- predicates -------------------------------------------------------------------------------------------

    def header(self, name: str) -> str:
        """A response header's value, stripped and lower-cased (``""`` when absent)."""
        return self.headers.get(name.lower(), "").strip().lower()

    def has(self, *needles: str) -> bool:
        """True if any of the lower-case ``needles`` occurs in the HTML."""
        lower = self.lower
        return any(n in lower for n in needles)

    def status_in(self, *codes: int, unknown: bool = False) -> bool:
        """True if the status is one of ``codes``; ``unknown`` is the answer when the status is not known."""
        return unknown if self.status is None else self.status in codes

    @property
    def is_error(self) -> bool:
        """True for a known 4xx or 5xx status."""
        return self.status is not None and self.status >= 400

    def gate(self, limit: int = GATE_TEXT) -> bool:
        """True when the page shows fewer than ``limit`` characters of visible text (a gate, not content)."""
        return len(self.text) < limit

    def has_cookie(self, *names: str) -> bool:
        """True if any of the exact cookie ``names`` is set for the page's site."""
        return any(n in self.cookies for n in names)

    def has_cookie_prefix(self, *prefixes: str) -> bool:
        """True if a cookie whose name starts with one of ``prefixes`` is set for the page's site."""
        return any(name.startswith(prefixes) for name in self.cookies)

    def frames_on(self, *domains: str) -> List[str]:
        """Child frame URLs whose host is one of ``domains`` or a subdomain of one."""
        return [u for u in self.frame_urls if host_matches(u, *domains)]

    def marked_by(self, vendor: str) -> bool:
        """True if the page carries one of ``vendor``'s challenge-page markers (:data:`VENDOR_MARKERS`)."""
        return self.has(*VENDOR_MARKERS.get(vendor, ()))

    def marked_by_other(self, vendor: str) -> bool:
        """True if the page carries another vendor's challenge-page markers."""
        return any(self.has(*marks) for name, marks in VENDOR_MARKERS.items() if name != vendor)


@dataclass
class Detection:
    """A recognised challenge, captcha or block.

    :param vendor: The vendor name (``cloudflare``, ``datadome``, ``perimeterx``, ``akamai``, ``imperva``,
        ``aws_waf`` or ``kasada``).
    :param kind: See :data:`Kind`.
    :param rule: A stable identifier of the rule that matched, such as ``dd.device``.
    :param details: Rule-specific facts for the solver (script URLs, site keys, parsed vendor objects).
    :param signal: The :class:`Signal` the detection was made from (set by
        :func:`~scrapling.engines.antibot.detect.detect`). Re-checks during a solve use its status and headers
        until a new main-frame document arrives: a page that never reloaded is still the document that was detected.
    """

    vendor: str
    kind: Kind
    rule: str
    details: Dict[str, Any] = field(default_factory=dict)
    signal: Optional[Signal] = field(default=None, repr=False, compare=False)


@dataclass
class SolveResult:
    """The outcome of :meth:`Handler.solve`.

    :param solved: True only when the vendor's challenge is gone from the page.
    :param reason: A short machine-readable reason (``solved``, ``timeout``, ``ban``, ``unsolved:<what>``...).
    :param cookies: Names of the vendor clearance cookies the solve earned or refreshed (never their values).
    :param used_solver: The captcha solver provider that was used, if any.
    :param solver_kind: For an unsolved result only: the captcha-solver kind (``turnstile``, ``hcaptcha``,
        ``awswaf``, ``datadome_slider``...) that would get the page further, when the handler stopped at a captcha a
        solver can act on (none was given, it does not offer the kind, or its answer was rejected). ``None`` when no
        solver could help (a ban, a block, a press-and-hold or an unsupported widget).
    """

    solved: bool
    reason: str
    cookies: List[str] = field(default_factory=list)
    used_solver: Optional[str] = None
    solver_kind: Optional[str] = None


class Handler(Protocol):
    """One vendor's detector and solver."""

    vendor: str

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise this vendor's challenge, captcha or block in ``s``, or return ``None``."""
        ...

    async def solve(
        self,
        page: Any,
        det: Detection,
        *,
        deadline: float,
        solver: Optional["SolverRouter"],
        log: Any,
    ) -> SolveResult:
        """Try to get ``page`` past ``det`` before ``deadline`` (a :func:`time.monotonic` value)."""
        ...


async def page_signal(
    page: Any,
    *,
    status: Optional[int] = None,
    headers: Optional[Dict[str, str]] = None,
    max_chars: int = MAX_HTML_CHARS,
) -> Signal:
    """Build a :class:`Signal` from a live Playwright/Patchright page, for re-checks after a solve.

    The page object does not know its document's response, so pass ``status`` and ``headers`` when you have them;
    detection rules that need them simply do not fire without them. Cookies are filtered to the ones the browser
    would send to the page URL's host. Errors while reading the page leave the matching field empty.
    """
    url = ""
    try:
        url = page.url or ""
    except Exception:  # pragma: no cover - a closed page
        pass
    html = ""
    try:
        html = (await page.content()) or ""
    except Exception:
        pass
    host = ""
    try:
        host = (urlsplit(url).hostname or "").lower()
    except ValueError:
        pass
    cookies: Dict[str, str] = {}
    try:
        for cookie in await page.context.cookies():
            if cookie_domain_matches(host, cookie.get("domain", "")):
                cookies[cookie.get("name", "")] = cookie.get("value", "")
    except Exception:
        pass
    frames: List[str] = []
    try:
        main = page.main_frame
        frames = [f.url for f in page.frames if f is not main]
    except Exception:
        pass
    return Signal(
        url=url, status=status, headers=dict(headers or {}), cookies=cookies, html=html[:max_chars], frame_urls=frames
    )


def first(items: Iterable[Any]) -> Optional[Any]:
    """The first item of ``items``, or ``None``."""
    for item in items:
        return item
    return None
