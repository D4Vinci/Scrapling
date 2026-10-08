"""Clearing Akamai Bot Manager challenges in the page (the body of :meth:`AkamaiHandler.solve`).

What the page can be stuck on, and what :func:`solve_akamai` does:

* **SEC-CPT** (``akamai.sec_cpt``: a 428 JSON answer; ``akamai.sec_cpt_html``: the ``sec-if-cpt`` interstitial).
  The interstitial runs Akamai's own challenge iframe, which waits ``data-duration`` seconds, solves a SHA-256
  proof of work (``crypto``/``adaptive``) or collects sensor data (``behavioral``), then reloads. The solver first
  lets the page do that while giving the sensor pointer input. If the page stalls, or there is no page script at
  all (a 428 JSON document), it solves the proof of work itself, posts it from inside the page to
  ``/_sec/verify?provider=...``, runs the sensor on the branding page for behavioural providers, calls the verify
  endpoint and goes back to the target. Success is a ``sec_cpt`` cookie containing ``~3~``.
* **SBSD** (``akamai.sbsd_html``: the challenge page with a ``?v=<uuid>&t=<n>`` script; ``akamai.sbsd``: a 429
  ``{"t":..}`` document). The challenge page posts its payload and reloads itself; the solver waits for that with
  pointer input and reloads once if it stalls. A 429 JSON document runs no script, so it gets the warm-up below.
* **Edge block** (``akamai.block`` "Access Denied", ``akamai.edge_block``). Often an unvalidated ``_abck`` on a
  strict path. The solver retries once: it opens the site's root (same origin), lets ``bmak`` post sensors until
  ``_abck`` is valid, then navigates back to the target.

After each step the page is re-detected; a second attempt runs if a challenge is still there (retry once).

``_abck`` validity uses Akamai's client stop signal (second ``~`` field): ``-1`` means "keep posting sensors",
``0`` (the familiar ``~0~``) means valid, ``n`` means valid after ``n`` posts; a non-negative fourth field marks a
cookie that a protected endpoint invalidated, which one more sensor post repairs.

Parts are ported from Hyper Solutions' MIT-licensed ``hyper-sdk-py`` (``hyper_sdk/akamai/sec_cpt.py``,
``stop_signal.py`` and ``script_path.py``; Copyright (c) 2024 Hyper Solutions, see NOTICE). They run locally and
need no API key. Waiting for the challenge document to resolve instead of trusting the first new document follows
Averyy/wafer ``wafer/browser/_akamai.py`` (Apache-2.0, see NOTICE).
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import random
import re
from asyncio import to_thread, wait_for
from dataclasses import dataclass, field
from html import unescape
from time import monotonic
from urllib.parse import urljoin, urlsplit

from scrapling.core._types import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple
from scrapling.engines.antibot._pointer import sleep_until, wander
from scrapling.engines.antibot.base import Detection, SolveResult, page_signal, remaining

if TYPE_CHECKING:  # pragma: no cover
    from scrapling.engines.antibot.solvers.router import SolverRouter

__all__ = [
    "solve_akamai",
    "SecCptChallenge",
    "SecCptChallengeData",
    "solve_sec_cpt_answers",
    "is_cookie_valid",
    "is_cookie_invalidated",
    "parse_script_path",
    "parse_sbsd",
    "CLEARANCE_COOKIES",
]

#: Cookies that make up an Akamai clearance, for replay (names only are ever reported).
CLEARANCE_COOKIES = (
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

# ---------------------------------------------------------------------------------------------------------------
# Ported from Hyper Solutions hyper-sdk-py (MIT License, Copyright (c) 2024 Hyper Solutions), commit c494cbb:
# hyper_sdk/akamai/sec_cpt.py, stop_signal.py and script_path.py. See NOTICE for the license text.
# Changes: dataclasses; the JSON form keeps ``count`` (upstream drops it and raises a TypeError) and reads the
# behavioural fields; the HTML form also reads the ``provider`` attribute; the hash is reduced with int.from_bytes
# (same result as the byte loop); the proof of work stops at a deadline; parse errors raise ValueError.
# ---------------------------------------------------------------------------------------------------------------

_SEC_DURATION = re.compile(r"data-duration=[\"']?(\d+)")
_SEC_CHALLENGE = re.compile(r'challenge="(.*?)"')
_SEC_PAGE = re.compile(r"data-duration=[\"']?\d+[\"']?\s+src=\"([^\"]+)\"")
_SEC_PROVIDER = re.compile(r"""\bprovider=["']?([a-z]+)""", re.IGNORECASE)
_SCRIPT_PATH = re.compile(
    r'<script type="text/javascript"\s+(?:nonce=".*?")?\s*src="([a-z\d/\-_]+)"(?:\s+defer)?></script>', re.IGNORECASE
)


@dataclass
class SecCptChallengeData:
    """The proof-of-work parameters of a SEC-CPT ``crypto`` or ``adaptive`` challenge."""

    token: str
    timestamp: int
    nonce: str
    difficulty: int
    count: int = 1


@dataclass
class SecCptChallenge:
    """A parsed SEC-CPT challenge.

    :param duration: Seconds the server requires before it accepts an answer (cannot be shortened).
    :param challenge_path: The challenge page (HTML form) or branding page (JSON form).
    :param challenge_data: Proof-of-work parameters, or ``None`` for a behavioural-only challenge.
    :param provider: ``crypto``, ``behavioral`` or ``adaptive``.
    :param verify_url: The dynamic verify path of a ``behavioral`` challenge.
    :param branding_url: The branding page that runs the sensor (``behavioral``/``adaptive``).
    """

    duration: int
    challenge_path: str
    challenge_data: Optional[SecCptChallengeData]
    provider: str = "crypto"
    verify_url: str = ""
    branding_url: str = ""

    @staticmethod
    def parse(html: str) -> "SecCptChallenge":
        """Parse the interstitial HTML (``<iframe ... challenge="<base64 json>" data-duration=N src="...">``)."""
        match = _SEC_CHALLENGE.search(html)
        if not match:
            raise ValueError("SEC-CPT challenge data not found")
        try:
            raw = json.loads(base64.b64decode(unescape(match.group(1))))
        except (binascii.Error, ValueError) as error:
            raise ValueError(f"SEC-CPT challenge data is not base64 JSON: {error}") from error
        if not isinstance(raw, dict):
            raise ValueError("SEC-CPT challenge data is not a JSON object")
        duration = _SEC_DURATION.search(html)
        if not duration:
            raise ValueError("SEC-CPT duration not found")
        page = _SEC_PAGE.search(html)
        if not page:
            raise ValueError("SEC-CPT challenge path not found")
        provider = _SEC_PROVIDER.search(html)
        return SecCptChallenge(
            duration=int(duration.group(1)),
            challenge_path=unescape(page.group(1)),
            challenge_data=_challenge_data(raw),
            provider=(provider.group(1).lower() if provider else "crypto"),
        )

    @staticmethod
    def parse_from_json(payload: "str | Dict[str, Any]") -> "SecCptChallenge":
        """Parse the 428 JSON answer (``{"sec-cp-challenge": "true", "provider": ..., ...}``)."""
        data = json.loads(payload) if isinstance(payload, str) else dict(payload)
        provider = str(data.get("provider") or "crypto").lower()
        has_pow = bool(data.get("token")) and data.get("difficulty") not in (None, "", 0)
        return SecCptChallenge(
            duration=int(data.get("chlg_duration") or 0),
            challenge_path=str(data.get("branding_url_content") or ""),
            challenge_data=_challenge_data(data) if has_pow else None,
            provider=provider,
            verify_url=str(data.get("verify_url") or ""),
            branding_url=str(data.get("branding_cust_url") or ""),
        )

    def generate_sec_cpt_payload(self, sec_cpt_cookie: str, *, deadline: Optional[float] = None) -> str:
        """The JSON body for ``POST /_sec/verify?provider=<provider>``.

        :param sec_cpt_cookie: The current ``sec_cpt`` cookie value; its first ``~`` field seeds the hashes.
        :param deadline: ``time.monotonic()`` time to give up at (raises ``TimeoutError``).
        """
        sec, sep, _ = sec_cpt_cookie.partition("~")
        if not sep:
            raise ValueError("Malformed sec_cpt cookie")
        if self.challenge_data is None:
            raise ValueError("This SEC-CPT challenge has no proof of work")
        answers = solve_sec_cpt_answers(sec, self.challenge_data, deadline=deadline)
        return json.dumps({"token": self.challenge_data.token, "answers": answers})


def _challenge_data(raw: Dict[str, Any]) -> SecCptChallengeData:
    return SecCptChallengeData(
        token=str(raw.get("token", "")),
        timestamp=int(raw.get("timestamp", 0) or 0),
        nonce=str(raw.get("nonce", "")),
        difficulty=int(raw.get("difficulty", 0) or 0),
        count=int(raw.get("count", 1) or 1),
    )


def solve_sec_cpt_answers(sec: str, data: SecCptChallengeData, *, deadline: Optional[float] = None) -> List[str]:
    """Find ``data.count`` answers with ``sha256(sec + timestamp + nonce + difficulty + answer) % difficulty == 0``.

    The difficulty goes up by one after every answer found, as Akamai's own script does.
    """
    if data.difficulty <= 0:
        raise ValueError("SEC-CPT difficulty must be positive")
    answers: List[str] = []
    difficulty = data.difficulty
    prefix = f"{sec}{data.timestamp}{data.nonce}"
    tries = 0
    while len(answers) < max(1, data.count):
        answer = f"0.{os.urandom(8).hex()}"
        digest = hashlib.sha256(f"{prefix}{difficulty}{answer}".encode("ascii")).digest()
        if int.from_bytes(digest, "big") % difficulty == 0:
            answers.append(answer)
            difficulty += 1
            continue
        tries += 1
        if deadline is not None and tries % 4096 == 0 and monotonic() >= deadline:
            raise TimeoutError("SEC-CPT proof of work ran out of time")
    return answers


def is_cookie_valid(cookie: str, request_count: int) -> bool:
    """Whether ``_abck`` says sensor posting can stop (Akamai's client stop signal).

    The second ``~`` field is the number of sensor posts after which the cookie is good; ``-1`` means not yet.
    """
    parts = cookie.split("~")
    if len(parts) < 2:
        return False
    try:
        threshold = int(parts[1])
    except ValueError:
        threshold = -1
    return threshold != -1 and request_count >= threshold


def is_cookie_invalidated(cookie: str) -> bool:
    """Whether a protected endpoint invalidated ``_abck`` (its fourth ``~`` field is set); one more post repairs it."""
    parts = cookie.split("~")
    if len(parts) < 4:
        return False
    try:
        signal = int(parts[3])
    except ValueError:
        signal = -1
    return signal > -1


def parse_script_path(html: str) -> Optional[str]:
    """The Bot Manager sensor script path (``/yMOlMy/yS/3T/...``) from a page, or ``None``."""
    match = _SCRIPT_PATH.search(html)
    return match.group(1) if match else None


# --------------------------------------------------------------------------------------------- end of the port

_SBSD = re.compile(r"""src=["'](/[A-Za-z\d/\-_.]+)\?v=([0-9a-fA-F-]{36})(?:&(?:amp;)?t=([A-Za-z\d]+))?["']""")
_SEC_MARKERS = ("sec-if-cpt-container", "/_sec/cp_challenge/", "sec-bc-tile-container", "sec-cpt-if")
_SMALL_PAGE = 50_000
_MAX_ATTEMPTS = 2

#: Seconds past the mandatory duration to let a proof-of-work interstitial clear itself before solving it locally.
SEC_GRACE_POW = 8.0
#: Seconds to let a behavioural interstitial (sensor only) clear itself.
SEC_GRACE_SENSOR = 12.0
#: Seconds to wait for an SBSD challenge page to post and reload itself (first try, retry).
SBSD_WAIT = (10.0, 6.0)
#: Seconds of pointer activity on the site root for ``bmak`` to validate ``_abck`` during the warm-up.
WARMUP_SENSOR_WAIT = 8.0


def parse_sbsd(html: str) -> Optional[Dict[str, str]]:
    """The SBSD script reference as ``{"path", "v", "t"}`` (``t`` is empty for passive SBSD), or ``None``."""
    match = _SBSD.search(html)
    if not match:
        return None
    return {"path": match.group(1), "v": match.group(2), "t": match.group(3) or ""}


def json_document(html: str) -> Optional[Dict[str, Any]]:
    """A JSON object as the browser shows a JSON document (inside ``<pre>``), or from raw JSON text."""
    text = unescape(re.sub(r"<[^>]+>", "", html or "")).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        value = json.loads(text[start : end + 1])
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def sec_cpt_from_page(html: str) -> Optional[SecCptChallenge]:
    """The SEC-CPT challenge on the page: the interstitial's iframe, or a 428 JSON document. ``None`` if neither."""
    try:
        return SecCptChallenge.parse(html)
    except ValueError:
        pass
    data = json_document(html)
    if data is not None and str(data.get("sec-cp-challenge", "")).lower() == "true":
        return SecCptChallenge.parse_from_json(data)
    match = _SEC_PROVIDER.search(html)
    if match and any(marker in html.lower() for marker in _SEC_MARKERS):
        # An interstitial without proof-of-work data (behavioural): nothing to compute, only to wait for.
        return SecCptChallenge(duration=0, challenge_path="", challenge_data=None, provider=match.group(1).lower())
    return None


def origin_of(url: str) -> str:
    """``scheme://host[:port]`` of ``url``."""
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


class _Tracker:
    """Counts sensor posts and follows the main frame's documents while a solve runs."""

    def __init__(self, page: Any) -> None:
        self.page = page
        self.sensor_posts = 0
        self.sbsd_posts = 0
        self.documents: List[Tuple[str, int]] = []
        self.status: Optional[int] = None
        self.headers: Dict[str, str] = {}

    def on_request(self, request: Any) -> None:
        try:
            if request.method != "POST":
                return
            body = request.post_data or ""
        except Exception:
            return
        if body.startswith('{"sensor_data"'):
            self.sensor_posts += 1
        elif body.startswith('{"body"'):
            self.sbsd_posts += 1

    def on_response(self, response: Any) -> None:
        try:
            request = response.request
            if request.resource_type != "document" or request.frame != self.page.main_frame:
                return
            self.documents.append((response.url, response.status))
            self.status = response.status
            self.headers = {str(k).lower(): str(v) for k, v in (response.headers or {}).items()}
        except Exception:
            pass

    def __enter__(self) -> "_Tracker":
        self.page.on("request", self.on_request)
        self.page.on("response", self.on_response)
        return self

    def __exit__(self, *_: Any) -> None:
        for event, handler in (("request", self.on_request), ("response", self.on_response)):
            try:
                self.page.remove_listener(event, handler)
            except Exception:  # pragma: no cover
                pass


async def solve_akamai(
    handler: Any,
    page: Any,
    det: Detection,
    *,
    deadline: float,
    solver: "Optional[SolverRouter]" = None,
    log: Any,
    rng: Optional[random.Random] = None,
    warmup: bool = True,
) -> SolveResult:
    """Clear the Akamai state ``det`` describes within ``deadline``, retrying once.

    Never leaves the target origin: the only navigations are to the site's root, the SEC-CPT branding page and
    back to the target. ``solver`` is not used; nothing here needs a paid solver.

    :param handler: The :class:`~scrapling.engines.antibot.akamai.AkamaiHandler`, whose ``detect`` re-checks the page.
    :param warmup: Allow the same-origin warm-up retry for edge blocks and 429 SBSD documents.
    """
    run = _Run(handler, page, deadline, log, rng or random.Random(), warmup)
    with _Tracker(page) as tracker:
        run.tracker = tracker
        return await run.solve(det)


class _Run:
    """One solve: the page, its target URL, the deadline and the tracker."""

    def __init__(self, handler: Any, page: Any, deadline: float, log: Any, rng: random.Random, warmup: bool) -> None:
        self.handler = handler
        self.page = page
        self.target = page.url
        self.origin = origin_of(self.target)
        self.deadline = deadline
        self.log = log
        self.rng = rng
        self.warmup_allowed = warmup
        self.warmed = False
        self.tracker: _Tracker = None  # type: ignore[assignment]

    async def solve(self, det: Detection) -> SolveResult:
        current = det
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            if remaining(self.deadline) < 1.0:
                return SolveResult(solved=False, reason="timeout")
            self.log.info(f"Akamai: {current.rule} (attempt {attempt})")
            if current.rule in ("akamai.sec_cpt", "akamai.sec_cpt_html"):
                step = await self.sec_cpt(current, retry=attempt > 1)
            elif current.rule == "akamai.sbsd_html":
                step = await self.sbsd_page(retry=attempt > 1)
            elif current.rule in ("akamai.sbsd", "akamai.block", "akamai.edge_block"):
                if self.warmed or not self.warmup_allowed:
                    return SolveResult(solved=False, reason=f"unsolved:{current.rule}")
                step = await self.warmup()
                if step == "root_blocked":
                    return SolveResult(solved=False, reason="unsolved:root_blocked")
            else:
                return SolveResult(solved=False, reason=f"unsolved:{current.rule}")

            again = await self.recheck(current)
            if again is None or again.vendor != "akamai":
                await self.settle_sensor(budget=3.0)
                return SolveResult(solved=True, reason=f"solved:{step}", cookies=await self.clearance_names())
            self.log.info(f"Akamai: still {again.rule} after {step}")
            current = again
        return SolveResult(solved=False, reason=f"unsolved:{current.rule}")

    # SEC-CPT -----------------------------------------------------------------------------------------------

    async def sec_cpt(self, det: Detection, *, retry: bool) -> str:
        started = monotonic()
        html = await self.html()
        challenge = sec_cpt_from_page(html)
        provider = challenge.provider if challenge else str(det.details.get("provider") or "")
        duration = float(challenge.duration if challenge else det.details.get("chlg_duration") or 0)

        if det.rule == "akamai.sec_cpt_html":
            # Phase A: the interstitial solves itself; give the sensor something to see while it does. Some
            # interstitials reload into themselves a few times first, so only a page without the markers counts.
            grace = SEC_GRACE_POW if provider in ("crypto", "adaptive") else SEC_GRACE_SENSOR
            documents = len(self.tracker.documents)
            if await self.watch((grace / 2) if retry else (duration + grace), lambda: self.sec_cleared(documents)):
                await self.reload_if_stuck()
                return "sec_cpt"
            reloads = len(self.tracker.documents) - documents
            self.log.info(f"Akamai: SEC-CPT interstitial did not clear by itself ({reloads} reloads)")
            started = monotonic() - duration  # the page has already waited the mandatory duration
            if challenge is None:
                challenge = sec_cpt_from_page(await self.html())

        # Phase B: solve it ourselves (the only way for a 428 JSON document, which runs no script).
        if challenge is None:
            if retry:
                return "sec_cpt_stuck"
            await self.goto(self.target)
            return "sec_cpt_reload"
        if challenge.challenge_data is not None:
            if not await sleep_until(self.deadline, max(0.0, started + challenge.duration - monotonic())):
                return "timeout"
            cookie = (await self.cookies()).get("sec_cpt", "")
            if not cookie:
                self.log.info("Akamai: no sec_cpt cookie to seed the proof of work")
                await self.goto(self.target)
                return "sec_cpt_reload"
            try:
                body = await to_thread(challenge.generate_sec_cpt_payload, cookie, deadline=self.deadline - 1.0)
            except (TimeoutError, ValueError) as error:
                self.log.info(f"Akamai: SEC-CPT proof of work failed: {error}")
                return "sec_cpt_pow_failed"
            status, _ = await self.fetch(f"/_sec/verify?provider={challenge.provider}", "POST", body)
            self.log.debug(f"Akamai: SEC-CPT answers posted ({status})")
        if challenge.provider in ("behavioral", "adaptive") and challenge.branding_url:
            branding = urljoin(self.origin + "/", challenge.branding_url)
            if origin_of(branding) == self.origin and await self.goto(branding) is not None:
                posts = self.tracker.sensor_posts
                await self.watch(8.0, lambda: self.sensor_progress(posts))
        verify = "/_sec/cp_challenge/verify"
        if challenge.provider == "behavioral" and challenge.verify_url:
            verify = "/" + challenge.verify_url.lstrip("/")
        status, _ = await self.fetch(verify, "GET", None)
        cleared = "~3~" in (await self.cookies()).get("sec_cpt", "")
        self.log.debug(f"Akamai: SEC-CPT verify answered {status}; sec_cpt {'cleared' if cleared else 'not cleared'}")
        await self.goto(self.target)
        return "sec_cpt_pow" if challenge.challenge_data is not None else "sec_cpt_sensor"

    async def sec_cleared(self, documents: int = 0) -> bool:
        """``sec_cpt`` carries ``~3~``, or a new document (after the first ``documents``) loaded without the
        interstitial's markers."""
        if "~3~" in (await self.cookies()).get("sec_cpt", ""):
            return True
        if len(self.tracker.documents) <= documents or self.tracker.status == 428:
            return False
        budget = min(3.0, remaining(self.deadline) - 0.5)
        if budget > 0.1:
            try:
                await self.page.wait_for_load_state("load", timeout=int(budget * 1000))
            except Exception:
                return False
        return not await self.on_sec_page()

    async def on_sec_page(self) -> bool:
        html = (await self.html(_SMALL_PAGE + 1)).lower()
        return len(html) <= _SMALL_PAGE and any(marker in html for marker in _SEC_MARKERS)

    async def reload_if_stuck(self) -> None:
        """``sec_cpt`` is cleared but the interstitial has not reloaded yet: give it 3 s, then load the target."""
        stop = min(self.deadline, monotonic() + 3.0)
        while monotonic() < stop:
            if not await self.on_sec_page():
                return
            await sleep_until(stop, 0.25)
        if await self.on_sec_page():
            await self.goto(self.target)

    async def sensor_progress(self, posts_before: int) -> bool:
        if "~3~" in (await self.cookies()).get("sec_cpt", ""):
            return True
        return self.tracker.sensor_posts - posts_before >= 3

    # SBSD ----------------------------------------------------------------------------------------------------

    async def sbsd_page(self, *, retry: bool) -> str:
        """Active SBSD (``?v=..&t=..``) reloads itself once its payload is posted; passive SBSD (``?v=`` only, often
        on a block page) only posts, and the next navigation is judged with the new ``sbsd`` cookies."""
        documents = len(self.tracker.documents)
        posts = self.tracker.sbsd_posts
        sbsd = parse_sbsd(await self.html(_SMALL_PAGE + 1))
        budget = SBSD_WAIT[1] if retry else SBSD_WAIT[0]

        if sbsd is not None and not sbsd["t"]:

            async def posted() -> bool:
                return self.tracker.sbsd_posts - posts >= 2 or len(self.tracker.documents) > documents

            await self.watch(budget, posted, min_time=1.0)
            self.log.debug(f"Akamai: passive SBSD made {self.tracker.sbsd_posts - posts} posts")
            if len(self.tracker.documents) == documents:
                await self.goto(self.target)
            return "sbsd_passive"

        async def reloaded() -> bool:
            if len(self.tracker.documents) <= documents:
                return False
            found = parse_sbsd(await self.html(_SMALL_PAGE + 1))
            return not (found and found["t"])

        if await self.watch(budget, reloaded):
            return "sbsd"
        self.log.info("Akamai: SBSD page did not reload by itself, reloading")
        await self.goto(self.target)
        return "sbsd_reload"

    # Warm-up retry ----------------------------------------------------------------------------------------

    async def warmup(self) -> str:
        """Open the site's root, let ``bmak`` post until ``_abck`` is valid, then navigate back to the target once."""
        self.warmed = True
        root = self.origin + "/"
        if urlsplit(self.target).path not in ("", "/"):
            response = await self.goto(root, wait_until="domcontentloaded")
            if response is None:
                return "timeout"
            if response.status in (403, 429):
                signal = await page_signal(self.page, status=response.status, headers=self.tracker.headers)
                found = self.handler.detect(signal)
                if found is not None and found.kind == "block":
                    self.log.info("Akamai: the site root is blocked too")
                    return "root_blocked"
        posts = self.tracker.sensor_posts
        await self.watch(WARMUP_SENSOR_WAIT, lambda: self.abck_ready(posts), min_time=1.5)
        abck = (await self.cookies()).get("_abck", "")
        made = self.tracker.sensor_posts - posts
        self.log.debug(
            f"Akamai: warm-up made {made} sensor and {self.tracker.sbsd_posts} SBSD posts, "
            f"_abck valid: {is_cookie_valid(abck, made)}, invalidated: {is_cookie_invalidated(abck)}"
        )
        await self.goto(self.target, referer=root)
        return "warmup"

    async def abck_ready(self, posts_before: int) -> bool:
        abck = (await self.cookies()).get("_abck")
        if not abck:
            return False
        return is_cookie_valid(abck, self.tracker.sensor_posts - posts_before) and not is_cookie_invalidated(abck)

    async def settle_sensor(self, *, budget: float) -> None:
        """After a clear, give ``bmak`` a moment to validate ``_abck`` so the cookies replay (optional, bounded)."""
        abck = (await self.cookies()).get("_abck")
        if not abck or (is_cookie_valid(abck, 0) and not is_cookie_invalidated(abck)):
            return
        posts = self.tracker.sensor_posts
        await self.watch(min(budget, remaining(self.deadline) - 0.5), lambda: self.abck_ready(posts))

    # Page plumbing --------------------------------------------------------------------------------------------

    async def recheck(self, current: Detection) -> Optional[Detection]:
        """Detect again on the page as it is now.

        Every way out of an Akamai challenge loads a new main document, so without one the page counts as unchanged;
        so does a page that cannot be read (still navigating at the deadline). Neither is ever taken for cleared.
        """
        if not self.tracker.documents:
            return current
        budget = min(5.0, remaining(self.deadline) - 0.5)
        if budget > 0.1:
            try:
                await self.page.wait_for_load_state("load", timeout=int(budget * 1000))
            except Exception:
                pass
        try:
            signal = await wait_for(
                page_signal(self.page, status=self.tracker.status, headers=self.tracker.headers),
                max(0.1, min(5.0, remaining(self.deadline))),
            )
        except Exception:
            return current
        if not signal.html:
            return current
        return self.handler.detect(signal)

    async def watch(self, budget: float, done: Callable[[], Any], *, min_time: float = 0.0) -> bool:
        """Move the pointer like a reader for up to ``budget`` seconds until ``await done()`` is true."""
        start = monotonic()
        stop = min(self.deadline - 0.5, start + budget)
        position = None
        while monotonic() < stop:
            try:
                if monotonic() - start >= min_time and await done():
                    return True
            except Exception:
                pass
            position = await wander(self.page, stop, self.rng.uniform(0.4, 0.9), rng=self.rng, start=position)
            await sleep_until(stop, 0.1)
        try:
            return bool(await done())
        except Exception:
            return False

    async def html(self, limit: int = 2_000_000) -> str:
        try:
            return (await wait_for(self.page.content(), max(0.1, min(5.0, remaining(self.deadline)))))[:limit]
        except Exception:
            return ""

    async def cookies(self) -> Dict[str, str]:
        try:
            jar = await self.page.context.cookies([self.page.url])
        except Exception:
            return {}
        return {c.get("name", ""): c.get("value", "") for c in jar}

    async def clearance_names(self) -> List[str]:
        names = await self.cookies()
        return [n for n in CLEARANCE_COOKIES if n in names]

    async def goto(self, url: str, *, wait_until: str = "load", referer: Optional[str] = None) -> Any:
        """Navigate within the target origin and the deadline; ``None`` when there was no time or it failed."""
        if origin_of(url) != self.origin:  # pragma: no cover - every caller builds same-origin URLs
            raise ValueError(f"refusing to leave {self.origin} for {url}")
        budget = remaining(self.deadline) - 0.5
        if budget < 1.0:
            return None
        try:
            return await self.page.goto(url, wait_until=wait_until, timeout=int(budget * 1000), referer=referer)
        except Exception as error:
            self.log.debug(f"Akamai: navigation to {url} failed: {type(error).__name__}")
            return None

    async def fetch(self, path: str, method: str, body: Optional[str]) -> Tuple[int, str]:
        """A same-origin request from inside the page, so it carries the browser's own cookies, TLS and headers."""
        url = urljoin(self.origin + "/", path)
        budget = remaining(self.deadline) - 0.25
        if budget <= 0.2 or origin_of(url) != self.origin:
            return 0, ""
        try:
            status, text = await wait_for(self.page.evaluate(_FETCH_JS, [url, method, body]), min(budget, 15.0))
            return int(status), str(text)
        except Exception:
            return 0, ""


_FETCH_JS = """async ([url, method, body]) => {
    const init = {method: method, credentials: 'same-origin', headers: {}};
    if (body !== null) { init.body = body; init.headers['Content-Type'] = 'application/json'; }
    const response = await fetch(url, init);
    return [response.status, (await response.text()).slice(0, 4096)];
}"""
