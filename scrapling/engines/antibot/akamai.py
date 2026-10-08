"""Akamai Bot Manager detection (and the browser-side solver).

Akamai shows up in four shapes:

* **SEC-CPT** (``sec_cpt``): a ``428 Precondition Required`` JSON ``{"sec-cp-challenge": "true", "provider":
  "crypto|behavioral|adaptive", "chlg_duration": N}``, or its HTML page with ``#sec-if-cpt-container`` /
  ``#sec-bc-tile-container``, often served with a 200. Crypto is a proof of work with a mandatory wait.
* **SBSD** ("state based scraping detection"): a 429 JSON ``{"t": "..."}`` from an API, or a small page whose script
  is loaded with ``?v=<uuid>&t=<n>`` (or ``/.well-known/sbsd``) that reloads itself once the sensor posts.
* **Edge block**: 403 "Access Denied ... Reference #18.xxxx" from ``AkamaiGHost`` / ``errors.edgesuite.net``.
* A 403 on a Bot Manager site (``_abck``/``bm_sz`` cookies, ``akamai-grn``) after the sensor ran: a block.

The ``_abck`` cookie tells whether the sensor was accepted: ``~0~`` in it is the usual "valid" mark, ``~-1~`` means
not (yet) validated. Not every site uses the mark, so it is reported as a hint only.

The SEC-CPT markers follow Averyy/wafer ``wafer/_challenge.py`` and the ``Reference #`` pattern follows crawl4ai
``antibot_detector.py`` (both Apache-2.0, see NOTICE).
"""

from __future__ import annotations

from json import loads as json_loads
from re import compile as re_compile

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Optional
from scrapling.engines.antibot.base import Detection, Kind, Signal, SolveResult

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["AkamaiHandler", "AKAMAI_COOKIES", "abck_state", "parse_sec_cpt"]

#: Bot Manager cookies, in the order they matter for replay.
AKAMAI_COOKIES = (
    "_abck",
    "bm_sz",
    "ak_bmsc",
    "bm_sv",
    "bm_s",
    "bm_so",
    "bm_sc",
    "bm_lso",
    "bm_mi",
    "sbsd",
    "sbsd_o",
    "sec_cpt",
)

_REFERENCE = re_compile(r"(?i)reference\s*#\s*(\d{1,3}\.[0-9a-f]{4,16}\.\d{6,12}\.[0-9a-f]{4,16})")
_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
# An SBSD script: ``src="...?v=<uuid>"`` (passive) or ``...?v=<uuid>&t=<n>`` (the active challenge).
_SBSD_SCRIPT = re_compile(rf"(?i)<script[^>]+src=[\"'][^\"']*[?&](?:amp;)?v={_UUID}(?:&(?:amp;)?t=\d+)?")
_DURATION = re_compile(r"(?i)[\"']?chlg_duration[\"']?\s*[:=]\s*[\"']?(\d{1,4})")
_PROVIDER = re_compile(r"(?i)[\"']provider[\"']\s*:\s*[\"'](\w{1,32})[\"']")
_BRANDING = re_compile(r"(?i)[\"']branding_url_content[\"']\s*:\s*[\"']([^\"']{1,512})[\"']")


def abck_state(value: Optional[str]) -> str:
    """Read the ``_abck`` cookie's validity mark: ``valid`` (``~0~``), ``invalid`` (``~-1~``), ``missing`` or
    ``unknown``."""
    if not value:
        return "missing"
    if "~0~" in value:
        return "valid"
    if "~-1~" in value:
        return "invalid"
    return "unknown"


def parse_sec_cpt(text: str) -> Dict[str, Any]:
    """Pull the SEC-CPT challenge parameters (``provider``, ``chlg_duration``, ``branding_url_content``) out of the
    428 JSON or the challenge page. Missing values are left out."""
    out: Dict[str, Any] = {}
    stripped = (text or "").strip()
    if stripped.startswith("{"):
        try:
            data = json_loads(stripped)
        except ValueError:
            data = None
        if isinstance(data, dict):
            for key in ("provider", "branding_url_content"):
                if isinstance(data.get(key), str):
                    out[key] = data[key]
            duration = data.get("chlg_duration")
            if isinstance(duration, (int, float)) or (isinstance(duration, str) and duration.isdigit()):
                out["chlg_duration"] = int(duration)
            return out
    for name, pattern in (("provider", _PROVIDER), ("branding_url_content", _BRANDING)):
        match = pattern.search(text or "")
        if match:
            out[name] = match.group(1)
    match = _DURATION.search(text or "")
    if match:
        out["chlg_duration"] = int(match.group(1))
    return out


class AkamaiHandler:
    """Detects Akamai Bot Manager challenges (SEC-CPT, SBSD) and blocks."""

    vendor = "akamai"

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise an Akamai challenge or block.

        Rules, first match wins:

        * ``akamai.sec_cpt`` (``challenge``): 428 with ``sec-cp-challenge``.
        * ``akamai.sec_cpt_html`` (``challenge``): the SEC-CPT page (``sec-if-cpt-container``,
          ``sec-bc-tile-container`` or ``/_sec/cp_challenge/``) with almost no visible text, at any status.
        * ``akamai.sbsd`` (``challenge``): 429 whose body is the SBSD ``{"t": ...}`` JSON, on an Akamai response.
        * ``akamai.sbsd_html`` (``challenge``): a near-empty page loading ``/.well-known/sbsd`` or a ``?v=<uuid>``
          SBSD script, on a Bot Manager site.
        * ``akamai.block`` (``block``): 403 "Access Denied" from the Akamai edge (``AkamaiGHost``,
          ``errors.edgesuite.net`` or a ``Reference #`` id).
        * ``akamai.edge_block`` (``block``): any other gate-sized 403 on a Bot Manager site, unless another vendor's
          challenge is on the page.
        """
        server_akamai = "akamaighost" in s.header("server")
        edge = server_akamai or "akamai-grn" in s.headers or "x-akamai-transformed" in s.headers
        bm_cookies = s.has_cookie("_abck", "bm_sz", "ak_bmsc", "bm_sv", "bm_so", "bm_s") or s.has_cookie_prefix("sbsd")
        cpt_markers = s.has("sec-if-cpt-container", "sec-bc-tile-container", "/_sec/cp_challenge/", "sec-cp-challenge")
        # The edge's error page writes its text as HTML entities (``errors&#46;edgesuite&#46;net``) in the raw body;
        # a browser's DOM has them decoded. Read the decoded text on a 403 so both forms match.
        denied_text = f"{s.title} {s.text.lower()}" if s.status == 403 else ""
        edge_page = s.has("errors.edgesuite.net") or "errors.edgesuite.net" in denied_text
        if not (edge or bm_cookies or cpt_markers or edge_page or s.has("/.well-known/sbsd")):
            return None

        details: Dict[str, Any] = {}
        if "_abck" in s.cookies:
            details["abck"] = abck_state(s.cookies["_abck"])

        def found(kind: Kind, rule: str, **extra: Any) -> Detection:
            return Detection(vendor=self.vendor, kind=kind, rule=rule, details={**details, **extra}, signal=s)

        if s.status == 428 and s.has("sec-cp-challenge"):
            return found("challenge", "akamai.sec_cpt", challenge="sec_cpt", **parse_sec_cpt(s.text or s.html))
        if cpt_markers and s.gate(1024):
            provider = "behavioral" if s.has("behavioral-content", "sec-bc-") else ("crypto" if s.has("crypto") else "")
            extra = parse_sec_cpt(s.html)
            if provider and "provider" not in extra:
                extra["provider"] = provider
            return found("challenge", "akamai.sec_cpt_html", challenge="sec_cpt", **extra)
        body = (s.text or s.html).lstrip()
        if s.status == 429 and body.startswith('{"t":') and (edge or bm_cookies):
            return found("challenge", "akamai.sbsd", challenge="sbsd")
        if s.gate(1024) and (bm_cookies or edge) and (s.has("/.well-known/sbsd") or _SBSD_SCRIPT.search(s.html)):
            return found("challenge", "akamai.sbsd_html", challenge="sbsd")
        if s.status == 403:
            reference = _REFERENCE.search(denied_text)
            if "access denied" in denied_text and (server_akamai or edge_page or reference):
                if reference:
                    details["reference"] = reference.group(1)
                return found("block", "akamai.block")
            if (edge or bm_cookies) and s.gate() and not s.marked_by_other(self.vendor):
                return found("block", "akamai.edge_block")
        return None

    async def solve(
        self,
        page: Any,
        det: Detection,
        *,
        deadline: float,
        solver: Optional["SolverRouter"],
        log: Any,
    ) -> SolveResult:
        """Get the page past an Akamai challenge within ``deadline``, retrying once (see :mod:`._akamai_solver`).

        SEC-CPT and SBSD pages are left to clear themselves under pointer input, with a local proof of work as the
        fallback; edge blocks and 429 SBSD documents get one same-origin warm-up and a second navigation. ``solver``
        is not used.
        """
        from scrapling.engines.antibot._akamai_solver import solve_akamai

        return await solve_akamai(self, page, det, deadline=deadline, solver=solver, log=log)
