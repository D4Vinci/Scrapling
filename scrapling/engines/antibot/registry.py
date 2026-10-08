"""The anti-bot handlers, in detection order.

Order matters when one page carries more than one vendor (DataDome behind Cloudflare's edge, Imperva in front of
DataDome, HUMAN on an Akamai edge). Each handler only fires on its own challenge markers, an explicit vendor header
or a vendor-specific blocking status, and the broad "blocking status on this vendor's site" rules step aside when
another vendor's challenge is on the page, so the order below decides only genuine ties:

1. Cloudflare first: ``cf-mitigated`` is the most explicit header there is.
2. AWS WAF: ``x-amzn-waf-action`` is just as explicit.
3. DataDome, Kasada, HUMAN: challenge pages with unique markers, often served through another vendor's edge.
4. Akamai and Imperva last: their edge headers and cookies sit on top of other vendors' pages.
"""

from __future__ import annotations

from scrapling.core._types import Dict, List, Optional, Tuple
from scrapling.engines.antibot.akamai import AkamaiHandler
from scrapling.engines.antibot.awswaf import AwsWafHandler
from scrapling.engines.antibot.base import Handler
from scrapling.engines.antibot.cloudflare import CloudflareHandler
from scrapling.engines.antibot.datadome import DataDomeHandler
from scrapling.engines.antibot.imperva import ImpervaHandler
from scrapling.engines.antibot.kasada import KasadaHandler
from scrapling.engines.antibot.perimeterx import PerimeterXHandler

__all__ = ["HANDLERS", "VENDORS", "get", "normalize_vendor"]

#: One instance of every handler, in detection order.
HANDLERS: List[Handler] = [
    CloudflareHandler(),
    AwsWafHandler(),
    DataDomeHandler(),
    KasadaHandler(),
    PerimeterXHandler(),
    AkamaiHandler(),
    ImpervaHandler(),
]

#: The vendor names, in detection order.
VENDORS: Tuple[str, ...] = tuple(h.vendor for h in HANDLERS)

_ALIASES: Dict[str, str] = {
    "cf": "cloudflare",
    "aws": "aws_waf",
    "awswaf": "aws_waf",
    "aws-waf": "aws_waf",
    "dd": "datadome",
    "px": "perimeterx",
    "human": "perimeterx",
    "humansecurity": "perimeterx",
    "akamai_bot_manager": "akamai",
    "incapsula": "imperva",
}

_BY_VENDOR: Dict[str, Handler] = {h.vendor: h for h in HANDLERS}


def normalize_vendor(vendor: str) -> str:
    """The canonical vendor name for ``vendor`` (case-insensitive; accepts aliases such as ``px`` or ``awswaf``)."""
    name = (vendor or "").strip().lower()
    return _ALIASES.get(name, name)


def get(vendor: str) -> Optional[Handler]:
    """The handler for ``vendor`` (aliases accepted), or ``None`` if there is none."""
    return _BY_VENDOR.get(normalize_vendor(vendor))
