"""Clearing AWS WAF challenges and CAPTCHAs in the browser (the body of :meth:`AwsWafHandler.solve`).

* **Challenge** (``aws.challenge``, ``aws.challenge_page``, ``aws.token_status``). ``challenge.js`` interrogates
  the browser, solves a proof of work, stores ``aws-waf-token`` and reloads; a real browser passes it unaided. The
  solver waits while giving the page pointer input, and reloads once if the token changed but no new document
  arrived. If the challenge escalates to a CAPTCHA, the CAPTCHA path takes over. ``aws.token_status`` (a blocking
  status on a token site, no challenge script) gets :data:`TOKEN_STATUS_PATIENCE` seconds for the token to change
  and otherwise ends as ``blocked``; nothing on that page clears it in place.
* **CAPTCHA** (``aws.captcha``, ``aws.captcha_page``). Without a solver router this ends as ``captcha_required``.
  With one, in order:

  1. **Recognition** (``awswaf_images``, CapSolver ``AwsWafClassification``): the solver reloads the page so the
     widget fetches a fresh puzzle, reads the puzzle images and target from AWS's own ``/problem`` response, sends
     only the images to the provider, clicks the returned grid cells on the ``<awswaf-captcha>`` canvas and
     confirms. The token AWS then issues belongs to this browser session.
  2. **Token** (``awswaf``, CapMonster ``AmazonTask``): a proxyless token stored as the ``aws-waf-token`` cookie
     for the page's host, then a reload.
  3. **Voucher** (``awswaf_voucher``, 2Captcha): the ``captcha_voucher`` is exchanged at AWS's own ``/voucher``
     endpoint (on the token host from ``challenge.js``/``jsapi.js``) for the token, then as above.

  Each route ends with a re-detection; the first that clears the page wins.

Wait logic ported from Averyy/wafer ``wafer/browser/_awswaf.py`` (Apache-2.0, see NOTICE). The ``/problem`` and
``/voucher`` endpoint shapes follow xKiian/awswaf (MIT); the ``<awswaf-captcha>`` shadow-DOM canvas layout is an
observation of AWS's ``captcha.js``. The recognition route has only been exercised against a local fixture.
"""

from __future__ import annotations

import base64
import binascii
import json
import random
import re
from asyncio import ensure_future, wait_for
from time import monotonic
from urllib.parse import urlsplit

from scrapling.core._types import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple
from scrapling.engines.antibot._pagestate import Recheck, bounded, reload_page, site_cookies, solver_name, supports
from scrapling.engines.antibot._pointer import human_path, move_along, sleep_until, viewport_size, wander
from scrapling.engines.antibot.base import Detection, SolveResult, remaining
from scrapling.engines.antibot.solvers.base import provider_url

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.awswaf import AwsWafHandler
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = ["solve_aws_waf", "aws_scripts", "problem_question", "TOKEN_COOKIE"]

TOKEN_COOKIE = "aws-waf-token"  # nosec B105 - the cookie's name, not a secret
#: Hosts whose ``/problem`` and ``/verify`` answers belong to AWS WAF's captcha (subdomains included).
AWS_HOSTS = ("awswaf.com",)

#: Every AWS WAF script, on the token host (``challenge.js``/``jsapi.js``) or the captcha host (``captcha.js``).
_SCRIPT = re.compile(r"""(?i)(https://[a-z0-9.-]+\.awswaf\.com/[^"'\s<>]{1,512}?/(challenge|captcha|jsapi)\.js)""")
_COOKIE_DOMAINS = re.compile(r"""(?i)awsWafCookieDomainList\s*=\s*\[([^\]]{0,2000})\]""")

RELOAD_AFTER = 2.5  # seconds a new token may wait for the page's own reload
SOLVER_MARGIN = 3.0
PROBLEM_WAIT = 8.0
RESULT_WAIT = 8.0  # how long a stored token or a confirmed puzzle gets to clear the page
#: Seconds an ``aws.token_status`` page (no challenge script on it) gets for its token to change before the solver
#: calls it a block.
TOKEN_STATUS_PATIENCE = 8.0
#: The solver kind reported for a CAPTCHA the router could clear (``SolveResult.solver_kind``).
SOLVER_KIND = "awswaf"
GRID = 3

_VOUCHER_JS = """async ([url, voucher, existing]) => {
    const r = await fetch(url, {method: 'POST', credentials: 'omit',
        headers: {'Content-Type': 'text/plain;charset=UTF-8'},
        body: JSON.stringify({captcha_voucher: voucher, existing_token: existing || null})});
    if (!r.ok) return null;
    const data = await r.json();
    return data && data.token ? data.token : null;
}"""
# Buttons of the ``<awswaf-captcha>`` widget, read through its open shadow root. Playwright selectors pierce open
# shadow roots, so ``awswaf-captcha button`` matches them.
_BUTTON_TEXT_JS = """el => (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().toLowerCase()"""
_CONFIRM_WORDS = ("confirm", "submit", "verify", "bestätigen", "confirmer", "confirmar", "conferma", "bevestig")
_BEGIN_WORDS = ("begin", "start", "los", "commencer", "empezar", "iniziare", "beginnen")


def aws_scripts(html: str) -> Dict[str, str]:
    """``{"challenge"|"captcha"|"jsapi": url}`` for the AWS WAF scripts referenced in ``html`` (first of each)."""
    out: Dict[str, str] = {}
    for url, kind in _SCRIPT.findall(html or ""):
        out.setdefault(kind.lower(), url.replace("&amp;", "&"))
    return out


def _script_base(url: Optional[str]) -> Optional[str]:
    """``https://<host>/<path>`` without the script file name (the endpoint base AWS's SDK uses)."""
    if not url:
        return None
    return url.rsplit("/", 1)[0]


def problem_question(problem: Dict[str, Any]) -> Optional[str]:
    """The CapSolver-style question (``aws:grid:<target>``, ``aws:toycarcity:carcity``) for a ``/problem`` answer."""
    kind = str(problem.get("problem_type") or "").lower()
    target = _unquote((problem.get("assets") or {}).get("target")) or _unquote(
        (problem.get("localized_assets") or {}).get("target0")
    )
    if "toycarcity" in kind or "carcity" in kind:
        return "aws:toycarcity:carcity"
    if target and ("grid" in kind or not kind):
        return f"aws:grid:{target.strip().lower().replace(' ', '_')}"
    return None


def _unquote(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value:
        return None
    if value.startswith('"'):
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, str) else None
        except ValueError:
            return value.strip('"')
    return value


def problem_images(problem: Dict[str, Any]) -> List[bytes]:
    """Decode the puzzle images of a ``/problem`` answer (``assets.images`` is a JSON-encoded list of base64)."""
    raw = (problem.get("assets") or {}).get("images")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            raw = [raw]
    images: List[bytes] = []
    for item in raw or ():
        if not isinstance(item, str):
            continue
        if item.startswith("data:"):
            item = item.split(",", 1)[-1]
        try:
            images.append(base64.b64decode(item, validate=False))
        except (binascii.Error, ValueError):
            continue
    return images


class _ProblemWatcher:
    """Keeps the latest AWS WAF ``/problem`` (puzzle) and ``/verify`` answers seen on the page."""

    def __init__(self, page: Any) -> None:
        self.page = page
        self.problem: Optional[Dict[str, Any]] = None
        self.problems = 0
        self.verify: Optional[Dict[str, Any]] = None
        self._tasks: Set[Any] = set()
        try:
            page.on("response", self._on_response)
        except Exception:
            pass

    @staticmethod
    def _endpoint(url: str) -> Optional[str]:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        if not any(host == h or host.endswith("." + h) for h in AWS_HOSTS):
            return None
        tail = parts.path.rstrip("/").rsplit("/", 1)[-1]
        return tail if tail in ("problem", "verify") else None

    def _on_response(self, response: Any) -> None:
        try:
            endpoint = self._endpoint(response.url)
        except Exception:
            return
        if endpoint is None:
            return
        task = ensure_future(self._read(endpoint, response))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _read(self, endpoint: str, response: Any) -> None:
        try:
            data = await response.json()
        except Exception:
            return
        if not isinstance(data, dict):
            return
        if endpoint == "problem":
            self.problem = data
            self.problems += 1
        else:
            self.verify = data

    def detach(self) -> None:
        try:
            self.page.remove_listener("response", self._on_response)
        except Exception:
            pass
        for task in list(self._tasks):
            task.cancel()


async def solve_aws_waf(
    handler: "AwsWafHandler",
    page: Any,
    det: Detection,
    *,
    deadline: float,
    solver: Optional["SolverRouter"] = None,
    log: Any = None,
    rng: Optional[random.Random] = None,
) -> SolveResult:
    """Get ``page`` past the AWS WAF challenge or CAPTCHA ``det`` describes, never past ``deadline``.

    Only reloads the current URL, clicks inside the ``<awswaf-captcha>`` widget, sets ``aws-waf-token`` for the
    page's host and calls AWS's own ``/voucher`` endpoint.
    """
    run = _Run(handler, page, det, deadline, solver, log, rng or random.Random())
    try:
        if det.kind == "captcha":
            return await run.captcha()
        return await run.challenge()
    finally:
        run.close()


class _Run:
    def __init__(
        self, handler: Any, page: Any, det: Detection, deadline: float, solver: Any, log: Any, rng: random.Random
    ):
        self.handler = handler
        self.page = page
        self.det = det
        self.deadline = deadline
        self.solver = solver
        self.log = log
        self.rng = rng
        self.check = Recheck(handler, page, det)
        self.problems: Optional[_ProblemWatcher] = None
        self._pointer: Optional[Tuple[float, float]] = None

    @property
    def tracker(self) -> Any:
        return self.check.tracker

    def close(self) -> None:
        self.check.detach()
        if self.problems is not None:
            self.problems.detach()

    def _debug(self, message: str) -> None:
        if self.log is not None:
            self.log.debug(message)

    async def clear_streak(self, stop: float) -> Optional[Detection]:
        return await self.check.current(stop)

    async def result(
        self, solved: bool, reason: str, used_solver: Optional[str] = None, solver_kind: Optional[str] = None
    ) -> SolveResult:
        cookies = await site_cookies(self.page, self.deadline)
        names = [TOKEN_COOKIE] if TOKEN_COOKIE in cookies else []
        return SolveResult(
            solved=solved, reason=reason, cookies=names, used_solver=used_solver, solver_kind=solver_kind
        )

    async def wait_cleared(self, timeout: float) -> bool:
        return await self.check.wait_cleared(self.deadline, timeout)

    # ---------------------------------------------------------- challenge

    async def challenge(self) -> SolveResult:
        """Wait for ``challenge.js`` to store a token and reload (wafer ``wait_for_awswaf``)."""
        initial = (await site_cookies(self.page, self.deadline)).get(TOKEN_COOKIE)
        token_at: Optional[float] = None
        docs_at_token = 0
        reloaded = False
        next_wander = monotonic() + self.rng.uniform(0.3, 1.0)
        # A blocking status with no challenge script: give the token a moment to change, then call it a block.
        patience = monotonic() + TOKEN_STATUS_PATIENCE if self.det.rule == "aws.token_status" else None
        while remaining(self.deadline) > 0.2:
            current = await self.clear_streak(self.deadline)
            if current is None:
                return await self.result(True, "solved")
            if patience is not None and token_at is None and monotonic() >= patience:
                return await self.result(False, "blocked")
            if current.kind == "captcha":
                self._debug("AWS WAF escalated the challenge to a CAPTCHA")
                self.det.details["escalated"] = current.rule
                self.det.details.update({k: v for k, v in current.details.items() if k.startswith("aws_")})
                return await self.captcha()
            token = (await site_cookies(self.page, self.deadline)).get(TOKEN_COOKIE)
            if token_at is None:
                if token and token != initial:
                    token_at, docs_at_token = monotonic(), self.tracker.count
            elif not reloaded and self.tracker.count == docs_at_token and monotonic() - token_at >= RELOAD_AFTER:
                reloaded = True
                self._debug("aws-waf-token is set but the page did not reload; reloading it")
                await reload_page(self.page, self.deadline)
                continue
            if monotonic() >= next_wander:
                await wander(self.page, self.deadline, self.rng.uniform(0.5, 1.2), rng=self.rng, scroll=False)
                next_wander = monotonic() + self.rng.uniform(2.0, 4.0)
            else:
                await sleep_until(self.deadline, 0.5)
        return await self.result(False, "timeout")

    # ------------------------------------------------------------ captcha

    async def inputs(self) -> Dict[str, Any]:
        """``gokuProps`` fields, script URLs and the JS API key, from the detection and the current DOM."""
        info: Dict[str, Any] = {k: v for k, v in self.det.details.items() if k.startswith("aws_") and v}
        html = await bounded(self.page.content(), self.deadline, "", 3.0) or ""
        for kind, url in aws_scripts(html).items():
            info.setdefault(f"aws_{kind}_script", url)
        try:
            from scrapling.engines.antibot.awswaf import parse_aws_challenge

            for key, value in parse_aws_challenge(html).items():
                info.setdefault(key, value)
        except Exception:  # pragma: no cover - defensive: detection helpers are optional here
            pass
        return info

    async def captcha(self) -> SolveResult:
        if self.solver is None:
            return await self.result(False, "captcha_required", solver_kind=SOLVER_KIND)
        reasons: List[str] = []
        used: Optional[str] = None
        if supports(self.solver, "awswaf_images"):
            result = await self.recognition()
            if result.solved:
                return result
            reasons.append(result.reason)
            used = result.used_solver or used
        for kind in ("awswaf", "awswaf_voucher"):
            if remaining(self.deadline) <= SOLVER_MARGIN + 1.0:
                break
            if supports(self.solver, kind):
                result = await self.token(kind)
                if result.solved:
                    return result
                reasons.append(result.reason)
                used = result.used_solver or used
        if not reasons:
            return await self.result(False, "captcha_required:no_solver_kind", solver_kind=SOLVER_KIND)
        return await self.result(False, "captcha_required:" + ";".join(reasons), used, solver_kind=SOLVER_KIND)

    async def token(self, kind: str) -> SolveResult:
        """A proxyless token (``awswaf``) or voucher (``awswaf_voucher``) from the router, set as the cookie."""
        info = await self.inputs()
        sitekey = info.get("aws_key") or info.get("aws_api_key")
        provider = solver_name(self.solver)
        if not sitekey:
            return SolveResult(solved=False, reason=f"{kind}:no_sitekey")
        extra = {
            k: info[k]
            for k in ("aws_iv", "aws_context", "aws_challenge_script", "aws_captcha_script", "aws_api_key")
            if info.get(k)
        }
        existing = (await site_cookies(self.page, self.deadline)).get(TOKEN_COOKIE)
        if existing:
            extra["aws_existing_token"] = existing
        left = remaining(self.deadline) - SOLVER_MARGIN
        try:
            token = await wait_for(
                self.solver.solve_token(
                    kind, sitekey, provider_url(self.page.url), deadline=self.deadline - SOLVER_MARGIN, **extra
                ),
                timeout=max(0.1, left),
            )
        except Exception as error:
            self.det.details.setdefault("solver_errors", {})[kind] = type(error).__name__
            return SolveResult(solved=False, reason=f"{kind}:solver_error", used_solver=provider)
        provider = getattr(token, "provider", None) or provider
        value: Optional[str] = str(token)
        if kind == "awswaf_voucher":
            fields = getattr(token, "fields", {}) or {}
            base = _script_base(info.get("aws_challenge_script") or info.get("aws_jsapi_script"))
            if not base:
                return SolveResult(solved=False, reason=f"{kind}:no_token_host", used_solver=provider)
            value = await bounded(
                self.page.evaluate(
                    _VOUCHER_JS, [f"{base}/voucher", str(token), fields.get("existing_token") or existing]
                ),
                self.deadline,
                None,
                10.0,
            )
        if not value:
            return SolveResult(solved=False, reason=f"{kind}:no_token", used_solver=provider)
        if not await self.set_token(value):
            return SolveResult(solved=False, reason=f"{kind}:cookie_failed", used_solver=provider)
        await reload_page(self.page, self.deadline)
        if await self.wait_cleared(min(remaining(self.deadline), RESULT_WAIT)):
            return await self.result(True, f"solved:{kind}", provider)
        return SolveResult(solved=False, reason=f"{kind}:rejected", used_solver=provider)

    async def set_token(self, value: str) -> bool:
        parts = urlsplit(self.page.url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            return False
        cookie = {
            "name": TOKEN_COOKIE,
            "value": value,
            "url": f"{parts.scheme}://{parts.netloc}/",
            "secure": parts.scheme == "https",
            "sameSite": "Lax",
        }
        marker = object()
        return await bounded(self.page.context.add_cookies([cookie]), self.deadline, marker, 3.0) is not marker

    # -------------------------------------------------------- recognition

    async def recognition(self) -> SolveResult:
        """Reload for a fresh puzzle, recognise its images remotely, click the cells locally and confirm."""
        provider = solver_name(self.solver)
        if self.problems is None:
            self.problems = _ProblemWatcher(self.page)
        seen = self.problems.problems
        await reload_page(self.page, self.deadline)
        problem = await self.wait_problem(seen, PROBLEM_WAIT)
        if problem is None:
            await self.press_button(_BEGIN_WORDS)
            problem = await self.wait_problem(seen, PROBLEM_WAIT / 2)
        if problem is None:
            return SolveResult(solved=False, reason="awswaf_images:no_puzzle", used_solver=provider)
        question, images = problem_question(problem), problem_images(problem)
        if not question or not question.startswith("aws:grid:") or not images:
            return SolveResult(solved=False, reason="awswaf_images:unsupported_puzzle", used_solver=provider)
        left = remaining(self.deadline) - SOLVER_MARGIN
        if left <= 1.0:
            return SolveResult(solved=False, reason="awswaf_images:no_time", used_solver=provider)
        try:
            answer = await wait_for(
                # Only the puzzle images and the question leave the machine (no page URL).
                self.solver.recognize(
                    "awswaf_images",
                    images,
                    question=question,
                    deadline=self.deadline - SOLVER_MARGIN,
                ),
                timeout=left,
            )
        except Exception as error:
            self.det.details.setdefault("solver_errors", {})["awswaf_images"] = type(error).__name__
            return SolveResult(solved=False, reason="awswaf_images:solver_error", used_solver=provider)
        provider = (answer or {}).get("provider") or provider
        cells = [int(i) for i in (answer or {}).get("objects") or [] if 0 <= int(i) < GRID * GRID]
        if not cells:
            return SolveResult(solved=False, reason="awswaf_images:no_cells", used_solver=provider)
        if not await self.click_cells(cells):
            return SolveResult(solved=False, reason="awswaf_images:no_canvas", used_solver=provider)
        self.problems.verify = None
        if not await self.press_button(_CONFIRM_WORDS):
            return SolveResult(solved=False, reason="awswaf_images:no_confirm_button", used_solver=provider)
        # AWS's page reloads as soon as /verify succeeds, which can discard the answer before it is read, so the
        # page clearing is the success signal and an explicit ``success: false`` the failure signal.
        stop = min(self.deadline, monotonic() + RESULT_WAIT)
        while remaining(stop) > 0.1:
            verify = self.problems.verify
            if verify is not None and verify.get("success") is False:
                return SolveResult(solved=False, reason="awswaf_images:rejected", used_solver=provider)
            if await self.check.current(stop) is None:
                return await self.result(True, "solved:awswaf_images", provider)
            await sleep_until(stop, 0.3)
        return SolveResult(solved=False, reason="awswaf_images:not_cleared", used_solver=provider)

    async def wait_problem(self, seen: int, timeout: float) -> Optional[Dict[str, Any]]:
        stop = min(self.deadline, monotonic() + timeout)
        while remaining(stop) > 0.05:
            if self.problems is not None and self.problems.problems > seen and self.problems.problem:
                return self.problems.problem
            await sleep_until(stop, 0.2)
        return None

    async def click(self, x: float, y: float) -> bool:
        page, rng = self.page, self.rng
        width, height = await viewport_size(page)
        start = self._pointer or (rng.uniform(0.3, 0.7) * width, rng.uniform(0.3, 0.7) * height)
        try:
            if not await move_along(page, human_path(start, (x, y), rng=rng, target_width=60.0), self.deadline):
                return False
            await sleep_until(self.deadline, rng.uniform(0.08, 0.2))
            await page.mouse.down()
            await sleep_until(self.deadline, rng.uniform(0.05, 0.12))
            await page.mouse.up()
        except Exception:
            return False
        self._pointer = (x, y)
        await sleep_until(self.deadline, rng.uniform(0.25, 0.6))
        return True

    async def click_cells(self, cells: List[int]) -> bool:
        """Click grid cells (0-based, row-major) on the widget's puzzle canvas."""
        canvas = self.page.locator("awswaf-captcha canvas").first
        box = await bounded(canvas.bounding_box(), self.deadline, None, 3.0)
        if not box or box.get("width", 0) < 30 or box.get("height", 0) < 30:
            return False
        cell_w, cell_h = box["width"] / GRID, box["height"] / GRID
        for index in sorted(set(cells)):
            row, col = divmod(index, GRID)
            x = box["x"] + (col + 0.5) * cell_w + self.rng.uniform(-0.15, 0.15) * cell_w
            y = box["y"] + (row + 0.5) * cell_h + self.rng.uniform(-0.15, 0.15) * cell_h
            if not await self.click(x, y):
                return False
        return True

    async def press_button(self, words: Tuple[str, ...]) -> bool:
        """Click the first visible widget button whose label contains one of ``words``."""
        buttons = self.page.locator("awswaf-captcha button")
        count = await bounded(buttons.count(), self.deadline, 0, 3.0) or 0
        for index in range(min(count, 12)):
            button = buttons.nth(index)
            label = await bounded(button.evaluate(_BUTTON_TEXT_JS), self.deadline, "", 2.0) or ""
            if not any(word in label for word in words):
                continue
            box = await bounded(button.bounding_box(), self.deadline, None, 2.0)
            if not box or box.get("width", 0) < 5:
                continue
            x = box["x"] + box["width"] * self.rng.uniform(0.3, 0.7)
            y = box["y"] + box["height"] * self.rng.uniform(0.3, 0.7)
            return await self.click(x, y)
        return False
