"""AWS WAF detection (and the browser-side solver).

AWS WAF answers a request with no valid ``aws-waf-token`` with:

* **Challenge**: HTTP 202 and ``x-amzn-waf-action: challenge``; the page runs ``challenge.js`` from
  ``<id>.<region>.token.awswaf.com`` with ``window.gokuProps = {key, iv, context}``, earns the token and reloads.
* **CAPTCHA**: HTTP 405 and ``x-amzn-waf-action: captcha``; the page renders ``AwsWafCaptcha`` from ``captcha.js``.
  Some sites serve the CAPTCHA page with their own status (401) and no header.

Served pages often load the same SDK (``jsapi.js``, ``AwsWafIntegration``) and carry the token cookie, so the SDK
alone is not a detection. The parsed ``gokuProps`` and script URLs are returned for the solver.

The ``gokuProps``/``awsWafCookieDomainList`` markers follow Averyy/wafer ``wafer/_challenge.py`` (Apache-2.0, see
NOTICE).
"""

from __future__ import annotations

from re import compile as re_compile

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Optional
from scrapling.engines.antibot.base import Detection, Kind, Signal, SolveResult

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["AwsWafHandler", "parse_aws_challenge"]

_SCRIPT = re_compile(r"(?i)(https://[a-z0-9.-]+\.awswaf\.com/[^\"'\s<>]{1,512}?/(challenge|captcha|jsapi)\.js)")
_GOKU = re_compile(r"(?is)gokuProps\s*=\s*\{(.{0,4000}?)\}")
_GOKU_FIELD = re_compile(r"""["']?(key|iv|context)["']?\s*:\s*["']([^"']{1,4000})["']""")
_API_KEY = re_compile(r"""(?i)apiKey["']?\s*:\s*["']([^"']{8,4000})["']""")
_CAPTCHA_MARKERS = ("awswafcaptcha", "captcha.js", 'id="captcha-container"', "awswaf-captcha")
# Not ``AwsWafIntegration``: that is the SDK served pages call, not the challenge page.
_CHALLENGE_MARKERS = ("gokuprops", "awswafcookiedomainlist", "challenge.js")


def parse_aws_challenge(html: str) -> Dict[str, Any]:
    """Extract the AWS WAF challenge parameters: ``aws_key``/``aws_iv``/``aws_context`` (``gokuProps``),
    ``aws_challenge_script``, ``aws_captcha_script``, ``aws_jsapi_script`` and ``aws_api_key``. Missing values are
    left out."""
    out: Dict[str, Any] = {}
    goku = _GOKU.search(html or "")
    if goku:
        for name, value in _GOKU_FIELD.findall(goku.group(1)):
            out[f"aws_{name}"] = value
    for url, kind in _SCRIPT.findall(html or ""):
        out.setdefault(f"aws_{kind.lower()}_script", url)
    api_key = _API_KEY.search(html or "")
    if api_key:
        out["aws_api_key"] = api_key.group(1)
    return out


class AwsWafHandler:
    """Detects AWS WAF challenges and CAPTCHAs."""

    vendor = "aws_waf"

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise an AWS WAF challenge or CAPTCHA.

        Rules, first match wins:

        * ``aws.challenge`` / ``aws.captcha``: the ``x-amzn-waf-action`` header.
        * ``aws.captcha_page`` (``captcha``): the ``AwsWafCaptcha`` page on a 4xx (or unknown) status with almost no
          visible text.
        * ``aws.challenge_page`` (``challenge``): the ``gokuProps``/``challenge.js`` page served with 202 (or with an
          unknown status and almost no visible text).
        * ``aws.token_status`` (``challenge``): an ``aws-waf-token`` site answering 202/403/405/429 with a gate-sized
          page and no other vendor's challenge on it.
        """
        action = s.header("x-amzn-waf-action")
        sdk = s.has("awswaf.com", "gokuprops", "awswafintegration", "awswafcaptcha")
        token = s.has_cookie("aws-waf-token")
        if not (action or sdk or (token and s.is_error) or s.status == 202):
            return None

        def found(kind: Kind, rule: str) -> Detection:
            return Detection(vendor=self.vendor, kind=kind, rule=rule, details=parse_aws_challenge(s.html), signal=s)

        if action == "challenge":
            return found("challenge", "aws.challenge")
        if action == "captcha":
            return found("captcha", "aws.captcha")
        if sdk and s.has(*_CAPTCHA_MARKERS) and (s.is_error or s.status is None) and s.gate():
            return found("captcha", "aws.captcha_page")
        if sdk and s.has(*_CHALLENGE_MARKERS) and (s.status == 202 or (s.status is None and s.gate(256))):
            return found("challenge", "aws.challenge_page")
        if token and s.status_in(202, 403, 405, 429) and s.gate() and not s.marked_by_other(self.vendor):
            return found("challenge", "aws.token_status")
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
        """Get the page past an AWS WAF challenge (wait for ``challenge.js``) or CAPTCHA (``solver`` recognition, then a
        token). See :func:`scrapling.engines.antibot._awswaf_solver.solve_aws_waf`.
        """
        from scrapling.engines.antibot._awswaf_solver import solve_aws_waf

        return await solve_aws_waf(self, page, det, deadline=deadline, solver=solver, log=log)
