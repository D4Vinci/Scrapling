"""Cloudflare detection and solving.

Cloudflare's challenge pages ("Just a moment...", in the visitor's language) carry ``window._cf_chl_opt`` with
``cType: 'non-interactive' | 'managed' | 'interactive'`` and are served with ``cf-mitigated: challenge`` (403, or
503 on older configurations). Site owners can also gate a page with a Turnstile widget. Blocks that no browser can
clear are error 1010 (the browser signature is banned), 1015 (rate limited) and the WAF's "Sorry, you have been
blocked" (1020).

Solving reuses Scrapling's own Cloudflare solver (:meth:`AsyncStealthySession._cloudflare_solver`), bounded by the
handler's deadline, then re-checks the page with :meth:`CloudflareHandler.detect`, so detection and the solver agree
on what a challenge is. A Turnstile widget that the click does not clear can be solved with a paid
captcha solver: the token goes only into the widget's own ``cf-turnstile-response`` field and callback.

The ``_cf_chl_ctx`` marker and the error-page check follow Averyy/wafer ``wafer/_challenge.py`` (Apache-2.0, see
NOTICE).
"""

from __future__ import annotations

from asyncio import TimeoutError as AsyncTimeoutError, wait_for
from re import compile as re_compile
from time import monotonic
from urllib.parse import urlsplit

from scrapling.core._types import TYPE_CHECKING, Any, Dict, Optional
from scrapling.engines.antibot.base import (
    SOLVABLE_KINDS,
    Detection,
    Kind,
    Signal,
    SolveResult,
    cookie_domain_matches,
    page_signal,
    remaining,
)
from scrapling.engines.antibot.solvers.base import provider_url

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["CloudflareHandler", "CF_COOKIES", "challenge_type", "turnstile_params"]

#: Cookies Cloudflare sets for a cleared visitor.
CF_COOKIES = ("cf_clearance", "__cf_bm", "_cfuvid")

#: The challenge types Scrapling's solver knows (``cType`` in ``window._cf_chl_opt``).
CHALLENGE_TYPES = ("non-interactive", "managed", "interactive")

_CTYPE = re_compile(r"cType:\s*'([a-z-]{1,32})'")
_WIDGET = re_compile(r"""(?i)class\s*=\s*["'][^"']*\bcf-turnstile\b""")
_ATTR = re_compile(r"""(?i)data-(sitekey|action|cdata|callback)\s*=\s*["']([^"']{1,512})["']""")
_RAY = re_compile(r"(?i)(?:cloudflare\s+ray\s+id:?\s*(?:<[^>]*>\s*)*|cRay:\s*')([0-9a-f]{12,20})")
_BLOCK_COPY = ("sorry, you have been blocked", "attention required!", "error code: 1020", "access denied")
_ERROR_PAGE = ("cloudflare ray id", "cf-error-details", "/cdn-cgi/styles/cf.errors.css", "cf-wrapper")

# Each wait inside Scrapling's solver uses the page's default timeout; keep every one short so the deadline holds.
_STEP_TIMEOUT_MS = 5000
# Time kept back from the solver for the settle and the re-check.
_RESERVE_S = 1.5
# Runs of Scrapling's solver (each makes up to three attempts of its own) while an interstitial stays on the page.
_MAX_RUNS = 2
# Hands a solver's token to the Turnstile widget: its response field(s) and the callback it declares, nothing else.
_RESPONSE_FIELDS = '[name="cf-turnstile-response"], [name="g-recaptcha-response"]'
_INJECT_JS = (
    "([token, callback]) => { for (const el of document.querySelectorAll('%s')) { el.value = token; } }"
    % _RESPONSE_FIELDS
)
_INJECT_AND_CALLBACK_JS = (
    "([token, callback]) => { for (const el of document.querySelectorAll('%s')) { el.value = token; }"
    " if (callback && typeof window[callback] === 'function') { window[callback](token); } }" % _RESPONSE_FIELDS
)


def challenge_type(html: str) -> Optional[str]:
    """The ``cType`` of a Cloudflare challenge page (``non-interactive``, ``managed`` or ``interactive``)."""
    match = _CTYPE.search(html or "")
    return match.group(1) if match and match.group(1) in CHALLENGE_TYPES else None


def turnstile_params(html: str) -> Dict[str, str]:
    """The first Turnstile widget's ``data-sitekey``/``data-action``/``data-cdata``/``data-callback`` attributes."""
    out: Dict[str, str] = {}
    widget = _WIDGET.search(html or "")
    if not widget:
        return out
    # Attributes of the widget element: from the tag start to its closing ``>``.
    start = html.rfind("<", 0, widget.start())
    end = html.find(">", widget.end())
    tag = html[start : end if end != -1 else len(html)]
    for name, value in _ATTR.findall(tag):
        out.setdefault(name.lower(), value)
    return out


class CloudflareHandler:
    """Detects Cloudflare challenges, Turnstile gates and blocks; solves them with Scrapling's solver."""

    vendor = "cloudflare"

    # ------------------------------------------------------------------ detect

    def detect(self, s: Signal) -> Optional[Detection]:
        """Recognise a Cloudflare challenge, Turnstile gate or block.

        Rules, first match wins:

        * ``cf.challenge`` (``challenge``): ``cf-mitigated: challenge`` on an error status (or with the challenge
          still on the page). A 200 with the header and no challenge left is a stale header from the first response,
          not a detection.
        * ``cf.interstitial`` (``challenge``): the challenge page itself: a ``cType`` (Scrapling's own marker, in
          any language), "Just a moment" with the challenge platform script, or ``_cf_chl_opt`` on a 403/503.
        * ``cf.fingerprint`` (``block``): error 1010, the browser's signature is banned.
        * ``cf.rate_limit`` (``block``): error 1015, or a Cloudflare 429 with no other vendor's challenge.
        * ``cf.waf`` (``block``): the WAF's "Sorry, you have been blocked" page (error 1020).
        * ``cf.turnstile`` (``captcha``): a Turnstile widget on a page with almost no visible text.
        """
        server_cf = "cloudflare" in s.header("server")
        mitigated = s.header("cf-mitigated") == "challenge"
        ctype = challenge_type(s.html) if "ctype" in s.lower else None
        chl_opt = s.has("window._cf_chl_opt", "_cf_chl_ctx")
        moment = s.title.startswith("just a moment") and s.has("/cdn-cgi/challenge-platform/")
        on_page = bool(ctype) or moment or chl_opt
        widget = bool(_WIDGET.search(s.html)) or s.has("cf-turnstile-response")
        error_page = s.has(*_ERROR_PAGE)
        if not (server_cf or mitigated or on_page or widget or error_page or "cf-ray" in s.headers):
            return None

        details: Dict[str, Any] = {}
        if ctype:
            details["ctype"] = ctype
        ray = s.headers.get("cf-ray", "")
        if not ray:
            match = _RAY.search(s.html)
            ray = match.group(1) if match else ""
        if ray:
            details["ray"] = ray

        def found(kind: Kind, rule: str, **extra: Any) -> Detection:
            return Detection(vendor=self.vendor, kind=kind, rule=rule, details={**details, **extra}, signal=s)

        if mitigated and (s.is_error or s.status is None or on_page):
            return found("challenge", "cf.challenge")
        if ctype or moment or (chl_opt and s.status_in(403, 503, unknown=True)):
            return found("challenge", "cf.interstitial")
        cf_served = server_cf or error_page
        if cf_served and s.status_in(403, 429, 503, unknown=True):
            if s.has("error code: 1010", "banned your access based on your browser's signature"):
                return found("block", "cf.fingerprint")
            if s.has("error code: 1015"):
                return found("block", "cf.rate_limit", reason="rate_limit")
        if server_cf and s.status == 429 and not s.marked_by_other(self.vendor):
            return found("block", "cf.rate_limit", reason="rate_limit")
        if s.status_in(403, unknown=True) and error_page and s.has(*_BLOCK_COPY):
            return found("block", "cf.waf")
        if widget and s.gate(1024):
            return found("captcha", "cf.turnstile", **turnstile_params(s.html))
        return None

    # ------------------------------------------------------------------ solve

    async def solve(
        self,
        page: Any,
        det: Detection,
        *,
        deadline: float,
        solver: Optional["SolverRouter"],
        log: Any,
    ) -> SolveResult:
        """Run Scrapling's Cloudflare solver on ``page`` within ``deadline``, then re-check the page.

        Blocks are not attempted. A run that fails part-way (the widget frame is late, the page reloads under it) is
        repeated once while the challenge is still there. A Turnstile gate the click did not clear is handed to
        ``solver`` (when given) as a ``turnstile`` token task.
        """
        if det.kind not in SOLVABLE_KINDS:
            return SolveResult(solved=False, reason=f"{det.kind}:{det.rule}")
        if remaining(deadline) <= _RESERVE_S:
            return SolveResult(solved=False, reason="timeout")
        before = await _cookie_values(page, CF_COOKIES)
        left: Detection = det
        timed_out = False
        for _ in range(_MAX_RUNS):
            timed_out = await self._run_scrapling_solver(page, deadline, log)
            await _settle(page, deadline)
            current = self.detect(await page_signal(page))
            if current is None:
                return SolveResult(solved=True, reason="solved", cookies=await _earned(page, before))
            left = current
            if left.kind not in SOLVABLE_KINDS:
                # The challenge turned into a block (1010, 1015, a WAF rule): nothing more to try.
                return SolveResult(solved=False, reason=f"{left.kind}:{left.rule}")
            if timed_out or left.kind == "captcha" or remaining(deadline) <= 2 * _RESERVE_S:
                break
        # A Turnstile gate with a site key is what a captcha solver can clear (``turnstile`` token task).
        solver_kind = "turnstile" if left.kind == "captcha" and left.details.get("sitekey") else None
        if solver_kind and solver is not None:
            return await self._solve_turnstile(page, left, before, deadline=deadline, solver=solver, log=log)
        return SolveResult(
            solved=False, reason="timeout" if timed_out else f"unsolved:{left.rule}", solver_kind=solver_kind
        )

    @staticmethod
    async def _run_scrapling_solver(page: Any, deadline: float, log: Any) -> bool:
        """Run Scrapling's solver with every inner wait capped; return True if the deadline cut it short."""
        from scrapling.engines._browsers._stealth import AsyncStealthySession

        # The solver only uses the session's stateless helpers, so a bare instance is enough (as in its own tests).
        runner = object.__new__(AsyncStealthySession)
        budget = remaining(deadline) - _RESERVE_S
        try:
            page.set_default_timeout(max(1, int(min(_STEP_TIMEOUT_MS / 1000, budget) * 1000)))
        except Exception:  # pragma: no cover - a closed page
            pass
        cutoff = monotonic() + max(0.1, budget)
        try:
            await wait_for(runner._cloudflare_solver(page), timeout=max(0.1, budget))
            return False
        except AsyncTimeoutError as error:
            # Since Python 3.11 a timeout raised inside the solver is the same class as ours; tell them apart by time.
            if monotonic() >= cutoff - 0.05:
                log.debug("Cloudflare solver stopped at the deadline")
                return True
            log.debug(f"Cloudflare solver failed: {error}")
            return False
        except Exception as error:
            log.debug(f"Cloudflare solver failed: {error}")
            return False
        finally:
            try:
                page.set_default_timeout(max(1000, int(remaining(deadline) * 1000)))
            except Exception:  # pragma: no cover
                pass

    async def _solve_turnstile(
        self,
        page: Any,
        det: Detection,
        before: Dict[str, str],
        *,
        deadline: float,
        solver: "SolverRouter",
        log: Any,
    ) -> SolveResult:
        """Get a Turnstile token from the captcha solver and hand it to the widget."""
        extra: Dict[str, Any] = {"deadline": deadline}
        for key in ("action", "cdata"):
            if det.details.get(key):
                extra[key] = det.details[key]
        used = None
        try:
            token = await wait_for(
                solver.solve_token("turnstile", det.details["sitekey"], provider_url(page.url), **extra),
                timeout=max(0.1, remaining(deadline) - _RESERVE_S),
            )
            used = getattr(token, "provider", None) or getattr(solver, "name", None) or "solver"
        except AsyncTimeoutError:
            return SolveResult(solved=False, reason="timeout", solver_kind="turnstile")
        except Exception as error:
            log.debug(f"Turnstile solver failed: {error}")
            return SolveResult(solved=False, reason="unsolved:solver_error", solver_kind="turnstile")
        try:
            # Only the widget's response field and its declared callback are touched.
            # The callback is a page function, so this runs in the page's own world.
            arg = [str(token), det.details.get("callback") or ""]
            await page.evaluate(_INJECT_AND_CALLBACK_JS, arg, isolated_context=False)
        except TypeError:
            # Plain Playwright has no isolated_context argument.
            await page.evaluate(_INJECT_JS, [str(token), ""])
        except Exception as error:
            log.debug(f"Turnstile token injection failed: {error}")
        await _settle(page, deadline)
        left = self.detect(await page_signal(page))
        if left is None:
            return SolveResult(solved=True, reason="solved", cookies=await _earned(page, before), used_solver=used)
        return SolveResult(
            solved=False, reason="unsolved:turnstile_token_not_accepted", used_solver=used, solver_kind="turnstile"
        )


async def _settle(page: Any, deadline: float) -> None:
    """Wait (bounded) for the document that a cleared challenge reloads into."""
    timeout = min(5.0, remaining(deadline) - 0.5)
    if timeout <= 0:
        return
    try:
        await page.wait_for_load_state("load", timeout=int(timeout * 1000))
    except Exception:
        pass


async def _cookie_values(page: Any, names: tuple) -> Dict[str, str]:
    """Values of the named cookies the browser would send to the page's host."""
    try:
        host = (urlsplit(page.url).hostname or "").lower()
        cookies = await page.context.cookies()
    except Exception:
        return {}
    return {
        c.get("name", ""): c.get("value", "")
        for c in cookies
        if c.get("name") in names and cookie_domain_matches(host, c.get("domain", ""))
    }


async def _earned(page: Any, before: Dict[str, str]) -> list:
    """Names of the Cloudflare cookies that are new or changed since ``before``."""
    after = await _cookie_values(page, CF_COOKIES)
    return [name for name in CF_COOKIES if name in after and after[name] != before.get(name)]
