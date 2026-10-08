"""The ``createTask`` / ``getTaskResult`` client shared by CapMonster Cloud, CapSolver and 2Captcha.

All three providers use the same JSON API design (first published by Anti-Captcha):

* ``POST {api}/createTask`` with ``{"clientKey": KEY, "task": {"type": ..., ...}}`` returns ``{"errorId": 0, "taskId": ...}``
  (or, for synchronous recognition tasks, ``{"errorId": 0, "status": "ready", "solution": {...}}`` directly).
* ``POST {api}/getTaskResult`` with ``{"clientKey": KEY, "taskId": ...}`` returns ``{"status": "processing"}`` until the
  result is ``{"status": "ready", "solution": {...}}``. Each provider allows at most 120 result requests per task.
* Any failure is ``{"errorId": <non-zero>, "errorCode": "ERROR_…", "errorDescription": "…"}``.

Documentation:
https://docs.capmonster.cloud/docs/api/methods/create-task/ (mirror: github.com/CapMonsterCloud/capmonster-captcha-solver-docs),
https://docs.capsolver.com/en/guide/api-createtask/, https://docs.capsolver.com/en/guide/api-gettaskresult/,
https://2captcha.com/api-docs/create-task, https://2captcha.com/api-docs/get-task-result.

The HTTP layer is the standard library (``urllib``) run in a worker thread, so the solvers add no dependencies.
Keys and proxy credentials never appear in logs, exception messages or ``repr``.
"""

from __future__ import annotations

import asyncio
import base64
import json
import ssl
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit, unquote

from scrapling.core._types import Any, Awaitable, Callable, Dict, FrozenSet, List, Mapping, Optional, Tuple, Type, Union

from scrapling.core.utils import log

from .base import (
    RECOGNITION_KINDS,
    TOKEN_KINDS,
    SolveRecord,
    SolverBadRequest,
    SolverConfigError,
    SolverError,
    SolverProxyNotAllowed,
    SolverTimeout,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
    Token,
    provider_url,
    redact,
)

#: ``(url, payload, timeout_seconds) -> parsed JSON object``. Injectable for tests and custom HTTP stacks.
JsonTransport = Callable[[str, Dict[str, Any], float], Awaitable[Dict[str, Any]]]

#: Keyword arguments ``solve_token`` understands. Anything else is a caller bug and is rejected before any spend.
TOKEN_OPTIONS: FrozenSet[str] = frozenset(
    {
        "action",
        "cdata",
        "page_data",
        "user_agent",
        "invisible",
        "enterprise_payload",
        "api_domain",
        "data_s",
        "min_score",
        "cookies",
        "challenge",
        "api_server",
        "risk_type",
        "init_parameters",
        "aws_context",
        "aws_iv",
        "aws_challenge_script",
        "aws_captcha_script",
        "aws_problem_url",
        "aws_api_key",
        "aws_existing_token",
        "funcaptcha_subdomain",
        "data",
    }
)
#: Keyword arguments ``recognize`` understands.
RECOGNITION_OPTIONS: FrozenSet[str] = frozenset(
    {"question", "grid", "page_url", "sitekey", "comment", "module", "min_clicks", "max_clicks"}
)
#: Keyword arguments every call understands.
CONTROL_OPTIONS: FrozenSet[str] = frozenset({"timeout", "deadline", "proxy"})

_MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class UrllibTransport:
    """POST JSON with ``urllib`` in a worker thread.

    :param trust_env: Honour ``HTTP(S)_PROXY`` environment variables. Off by default: solver APIs must be reached
        directly (CapSolver asks clients not to call it through proxies), and the environment may point at a
        proxy meant for something else.
    :param ssl_context: The TLS context for HTTPS calls, such as one built from ``certifi`` when the interpreter's
        default certificate store is not usable. ``None`` uses Python's default verified context.
    """

    def __init__(
        self,
        *,
        trust_env: bool = False,
        user_agent: str = "scrapling-antibot/1.0",
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        handlers: List[urllib.request.BaseHandler] = [] if trust_env else [urllib.request.ProxyHandler({})]
        if ssl_context is not None:
            if ssl_context.verify_mode != ssl.CERT_REQUIRED or not ssl_context.check_hostname:
                raise ValueError("ssl_context must verify certificates and host names")
            handlers.append(urllib.request.HTTPSHandler(context=ssl_context))
        self._opener = urllib.request.build_opener(*handlers)
        self._user_agent = user_agent

    async def __call__(self, url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        return await asyncio.to_thread(self._post, url, payload, timeout)

    def _post(self, url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": self._user_agent},
        )
        try:
            with self._opener.open(request, timeout=max(0.5, timeout)) as response:  # nosec B310
                status = response.status
                raw = response.read(_MAX_RESPONSE_BYTES)
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                raw = e.read(_MAX_RESPONSE_BYTES)
            except Exception:  # pragma: no cover - broken error body
                raw = b""
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # Only the exception type: URLs carry no secrets, but reasons can echo proxy settings.
            raise _TransportError(f"network error ({type(e).__name__})") from None
        try:
            data = json.loads(raw.decode("utf-8", "replace")) if raw else None
        except ValueError:
            data = None
        if not isinstance(data, dict):
            raise _TransportError(f"HTTP {status} with a non-JSON body")
        if status >= 500 and not data.get("errorId"):
            raise _TransportError(f"HTTP {status}")
        return data


class _TransportError(Exception):
    pass


def _b64(image: Union[bytes, bytearray, memoryview, str]) -> str:
    """Base64-encode an image. Strings are assumed to be base64 already (a ``data:`` prefix is stripped)."""
    if isinstance(image, str):
        return image.split(",", 1)[1] if image.startswith("data:") else image
    if isinstance(image, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(image)).decode("ascii")
    raise SolverBadRequest(f"images must be bytes or base64 strings, not {type(image).__name__}", fallback=False)


def put(task: Dict[str, Any], key: str, value: Any) -> None:
    """Set ``task[key]`` only when ``value`` is meaningful (not None and not an empty string/dict)."""
    if value is None or value == "" or value == {}:
        return
    task[key] = value


class ProxySpec:
    """A parsed proxy. ``repr`` hides credentials."""

    __slots__ = ("type", "host", "port", "login", "password")

    def __init__(self, type: str, host: str, port: int, login: Optional[str] = None, password: Optional[str] = None):
        self.type, self.host, self.port, self.login, self.password = type, host, port, login, password

    @classmethod
    def parse(cls, proxy: Union[str, Mapping[str, Any]]) -> "ProxySpec":
        if isinstance(proxy, Mapping):
            p_type = str(proxy.get("type") or proxy.get("scheme") or "http").lower()
            host = proxy.get("address") or proxy.get("host") or proxy.get("server")
            port = proxy.get("port")
            login = proxy.get("login") or proxy.get("username")
            password = proxy.get("password")
            if host and "://" in str(host):
                return cls.parse(str(host)) if port is None else cls.parse(f"{host}:{port}")
        elif isinstance(proxy, str):
            parts = urlsplit(proxy if "://" in proxy else f"http://{proxy}")
            p_type, host, port = parts.scheme.lower(), parts.hostname, parts.port
            login = unquote(parts.username) if parts.username else None
            password = unquote(parts.password) if parts.password else None
        else:
            raise SolverConfigError("proxy must be a URL string or a mapping", fallback=False)
        if p_type not in ("http", "https", "socks4", "socks5"):
            raise SolverConfigError(f"unsupported proxy type {p_type!r}", fallback=False)
        try:
            port_n = int(port)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise SolverConfigError("proxy needs a host and a numeric port", fallback=False) from None
        if not host:
            raise SolverConfigError("proxy needs a host and a numeric port", fallback=False)
        return cls(p_type, str(host), port_n, login, password)

    def secrets(self) -> Tuple[str, ...]:
        return tuple(s for s in (self.login, self.password) if s)

    def __repr__(self) -> str:
        return f"<ProxySpec {self.type}://{self.host}:{self.port}{' (auth)' if self.login else ''}>"


class CreateTaskSolver:
    """Base class for createTask-family providers. Subclasses describe their task types; this class runs them.

    :param api_key: The provider account key. Stored privately; never logged.
    :param api_base: Override the API origin (tests point this at a local mock server).
    :param allow_proxy: Permit proxied task variants. Off by default: the provider must never reach the target
        through your own network or proxy, so only proxyless tasks are sent.
    :param timeout: Default seconds a single solve may take (token tasks). Recognition tasks default to 30 s.
    :param transport: Custom HTTP function (see :data:`JsonTransport`).
    :param prices: USD per 1,000 solves by kind, overriding the built-in estimates used for cost accounting.
    """

    name: str = ""
    default_api_base: str = ""
    token_kinds: FrozenSet[str] = frozenset()
    recognition_kinds: FrozenSet[str] = frozenset()
    #: provider error code -> exception class
    error_map: Mapping[str, Type[SolverError]] = {}
    #: provider error code -> seconds to stop using this provider (overrides the exception default)
    cooldown_codes: Mapping[str, float] = {}
    #: Estimated USD per 1,000 solves (used when the provider does not report the cost of a task).
    default_prices: Mapping[str, float] = {}
    #: Kinds that are billed per image rather than per task.
    per_image_kinds: FrozenSet[str] = frozenset()
    token_first_poll: float = 3.0
    recognition_first_poll: float = 0.5
    poll_interval: float = 2.0
    recognition_poll_interval: float = 1.0
    max_polls: int = 120
    request_timeout: float = 20.0
    default_token_timeout: float = 120.0
    default_recognition_timeout: float = 30.0

    def __init__(
        self,
        api_key: str,
        *,
        api_base: Optional[str] = None,
        allow_proxy: bool = False,
        timeout: Optional[float] = None,
        transport: Optional[JsonTransport] = None,
        prices: Optional[Mapping[str, float]] = None,
    ):
        if not isinstance(api_key, str) or not api_key.strip():
            raise SolverConfigError("an API key is required", provider=self.name)
        self.__key = api_key.strip()
        self.api_base = (api_base or self.default_api_base).rstrip("/")
        self.allow_proxy = bool(allow_proxy)
        self.timeout = float(timeout) if timeout else self.default_token_timeout
        self._transport: JsonTransport = transport or UrllibTransport()
        self.prices: Dict[str, float] = dict(self.default_prices)
        if prices:
            self.prices.update({k: float(v) for k, v in prices.items()})
        #: Every attempt made by this client (successful or not), oldest first.
        self.records: List[SolveRecord] = []

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self.name!r} api_base={self.api_base!r} allow_proxy={self.allow_proxy}>"
        )

    # ---- capability -------------------------------------------------------------------------------------------

    def supports(self, kind: str) -> bool:
        return kind in self.token_kinds or kind in self.recognition_kinds

    # ---- subclass hooks ---------------------------------------------------------------------------------------

    def build_token_task(self, kind: str, sitekey: str, page_url: str, o: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def extract_token(self, kind: str, solution: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Return ``(value, user_agent)`` from a token solution."""
        raise NotImplementedError

    def build_recognition_task(self, kind: str, images: List[str], o: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def normalize_recognition(self, kind: str, solution: Dict[str, Any], o: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def proxy_task(self, kind: str, task: Dict[str, Any], proxy: ProxySpec) -> Dict[str, Any]:
        """Turn a proxyless task into the provider's proxied variant."""
        raise SolverUnsupported("proxied tasks are not supported", provider=self.name, code="PROXY_UNSUPPORTED")

    def reported_cost(self, response: Dict[str, Any]) -> Optional[float]:
        """The cost the provider reports for a finished task, if it reports one."""
        return None

    # ---- public API -------------------------------------------------------------------------------------------

    async def solve_token(self, kind: str, sitekey: str, page_url: str, **extra: Any) -> Token:
        if kind not in self.token_kinds:
            raise SolverUnsupported(f"{kind!r} is not offered", provider=self.name, code="KIND_UNSUPPORTED")
        timeout, deadline, proxy, o = self._split_options(extra, TOKEN_OPTIONS, self.timeout)
        if not sitekey and kind not in ("awswaf", "awswaf_voucher"):
            raise SolverBadRequest("a sitekey is required", provider=self.name, code="NO_SITEKEY", fallback=False)
        # The provider learns the page's host and path only: never its query string, fragment or credentials.
        page_url = provider_url(page_url)
        if not page_url:
            raise SolverBadRequest("page_url is required", provider=self.name, code="NO_PAGE_URL", fallback=False)
        task = self.build_token_task(kind, sitekey, page_url, o)
        task = self._maybe_proxy(kind, task, proxy)
        started = time.monotonic()
        response, task_id = await self._run(kind, task, deadline, self.token_first_poll, self.poll_interval, proxy)
        solution = response.get("solution") or {}
        try:
            value, user_agent = self.extract_token(kind, solution)
        except (KeyError, TypeError, ValueError):
            value, user_agent = "", None
        if not value or not isinstance(value, str):
            self._record(kind, task, False, task_id, "EMPTY_SOLUTION", started, response)
            raise SolverUnavailable(
                "the solution has no token", provider=self.name, code="EMPTY_SOLUTION", task_created=True
            )
        cost, source = self._record(kind, task, True, task_id, None, started, response)
        elapsed = time.monotonic() - started
        log.debug(f"{self.name}: {kind} token ready in {elapsed:.1f}s (task {task_id})")
        return Token(
            value,
            kind=kind,
            provider=self.name,
            task_id=task_id,
            fields=solution,
            user_agent=user_agent,
            cost_usd=cost,
            cost_source=source,
            elapsed_s=elapsed,
        )

    async def recognize(self, kind: str, images: List[bytes], **extra: Any) -> Dict[str, Any]:
        if kind not in self.recognition_kinds:
            raise SolverUnsupported(f"{kind!r} is not offered", provider=self.name, code="KIND_UNSUPPORTED")
        if not isinstance(images, (list, tuple)) or not images:
            raise SolverBadRequest(
                "images must be a non-empty list", provider=self.name, code="NO_IMAGES", fallback=False
            )
        timeout, deadline, proxy, o = self._split_options(extra, RECOGNITION_OPTIONS, self.default_recognition_timeout)
        if o.get("page_url"):
            o["page_url"] = provider_url(o["page_url"]) or None
            if o["page_url"] is None:
                del o["page_url"]
        if proxy is not None:
            raise SolverBadRequest(
                "recognition tasks never take a proxy", provider=self.name, code="PROXY", fallback=False
            )
        encoded = [_b64(i) for i in images]
        task = self.build_recognition_task(kind, encoded, o)
        started = time.monotonic()
        response, task_id = await self._run(
            kind, task, deadline, self.recognition_first_poll, self.recognition_poll_interval, None, units=len(encoded)
        )
        solution = response.get("solution") or {}
        try:
            result = self.normalize_recognition(kind, solution, o)
        except (KeyError, TypeError, ValueError):
            self._record(kind, task, False, task_id, "BAD_SOLUTION", started, response, units=len(encoded))
            raise SolverUnavailable(
                "unexpected recognition solution", provider=self.name, code="BAD_SOLUTION", task_created=True
            ) from None
        cost, source = self._record(kind, task, True, task_id, None, started, response, units=len(encoded))
        elapsed = time.monotonic() - started
        result.update(
            provider=self.name, task_id=task_id, cost_usd=cost, cost_source=source, elapsed_s=elapsed, raw=solution
        )
        log.debug(f"{self.name}: {kind} recognized in {elapsed:.1f}s")
        return result

    async def get_balance(self, *, timeout: float = 15.0) -> float:
        """Return the account balance in USD."""
        deadline = time.monotonic() + timeout
        response = await self._call("getBalance", {"clientKey": self.__key}, deadline)
        self._raise_for_error(response)
        try:
            return float(response["balance"])
        except (KeyError, TypeError, ValueError):
            raise SolverUnavailable("no balance in response", provider=self.name, code="BAD_RESPONSE") from None

    # ---- internals --------------------------------------------------------------------------------------------

    def _split_options(
        self, extra: Dict[str, Any], allowed: FrozenSet[str], default_timeout: float
    ) -> Tuple[float, float, Any, Dict[str, Any]]:
        unknown = sorted(set(extra) - allowed - CONTROL_OPTIONS)
        if unknown:
            raise SolverBadRequest(
                f"unknown options: {', '.join(unknown)}", provider=self.name, code="BAD_OPTIONS", fallback=False
            )
        o = {k: v for k, v in extra.items() if k in allowed and v is not None}
        timeout = float(extra.get("timeout") or default_timeout)
        deadline = time.monotonic() + timeout
        if extra.get("deadline") is not None:
            deadline = min(deadline, float(extra["deadline"]))
        if deadline <= time.monotonic():
            raise SolverTimeout(
                "no time left before the deadline", provider=self.name, code="DEADLINE", task_created=False
            )
        return timeout, deadline, extra.get("proxy"), o

    def _maybe_proxy(self, kind: str, task: Dict[str, Any], proxy: Any) -> Dict[str, Any]:
        if proxy is None or proxy == "":
            return task
        if not self.allow_proxy:
            raise SolverProxyNotAllowed(
                "proxies are disabled (allow_proxy=False)", provider=self.name, code="PROXY_NOT_ALLOWED"
            )
        return self.proxy_task(kind, task, ProxySpec.parse(proxy))

    def _payload(self, **fields: Any) -> Dict[str, Any]:
        """A request body carrying the account key (for provider-specific methods in subclasses)."""
        return {"clientKey": self.__key, **fields}

    def _secrets(self, proxy: Optional[ProxySpec] = None) -> Tuple[str, ...]:
        return (self.__key,) + (proxy.secrets() if proxy else ())

    async def _call(self, method: str, payload: Dict[str, Any], deadline: float) -> Dict[str, Any]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SolverTimeout("deadline reached", provider=self.name, code="DEADLINE")
        try:
            return await self._transport(f"{self.api_base}/{method}", payload, min(self.request_timeout, remaining))
        except _TransportError as e:
            raise SolverUnavailable(redact(str(e), self._secrets()), provider=self.name, code="NETWORK") from None
        except SolverError:
            raise
        except Exception as e:  # custom transports
            raise SolverUnavailable(
                redact(f"transport failed ({type(e).__name__})", self._secrets()), provider=self.name, code="NETWORK"
            ) from None

    def _raise_for_error(self, response: Dict[str, Any], proxy: Optional[ProxySpec] = None) -> None:
        error_id = response.get("errorId")
        if not error_id:
            return
        code = str(response.get("errorCode") or f"errorId {error_id}")
        description = redact(str(response.get("errorDescription") or ""), self._secrets(proxy))[:300]
        cls = self.error_class(code, description)
        raise cls(description, provider=self.name, code=code, cooldown_s=self.cooldown_codes.get(code))

    def error_class(self, code: str, description: str) -> Type[SolverError]:
        """Map a provider error to an exception class (subclasses refine this for undocumented responses)."""
        return self.error_map.get(code, SolverError)

    async def _run(
        self,
        kind: str,
        task: Dict[str, Any],
        deadline: float,
        first_poll: float,
        interval: float,
        proxy: Any,
        *,
        units: int = 1,
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        proxy_spec = ProxySpec.parse(proxy) if proxy not in (None, "") else None
        started = time.monotonic()
        task_id: Optional[str] = None
        try:
            created = await self._call("createTask", {"clientKey": self.__key, "task": task}, deadline)
            self._raise_for_error(created, proxy_spec)
            if created.get("status") == "ready" and created.get("solution") is not None:
                return created, _str_or_none(created.get("taskId"))
            raw_id = created.get("taskId")
            if raw_id in (None, ""):
                raise SolverUnavailable("createTask returned no taskId", provider=self.name, code="NO_TASK_ID")
            task_id = str(raw_id)
            await _sleep_until(first_poll, deadline)
            polls = 0
            network_failures = 0
            while True:
                if time.monotonic() >= deadline:
                    raise SolverTimeout(
                        f"not solved within the deadline ({polls} polls)", provider=self.name, code="TIMEOUT"
                    )
                try:
                    result = await self._call("getTaskResult", {"clientKey": self.__key, "taskId": raw_id}, deadline)
                except SolverUnavailable:
                    network_failures += 1
                    if network_failures >= 3:
                        raise
                    await _sleep_until(interval, deadline)
                    continue
                network_failures = 0
                self._raise_for_error(result, proxy_spec)
                status = result.get("status")
                if status == "ready":
                    return result, task_id
                if status == "failed":
                    raise SolverUnsolvable(
                        "the task failed", provider=self.name, code=str(result.get("errorCode") or "FAILED")
                    )
                polls += 1
                if polls >= self.max_polls:
                    raise SolverTimeout("poll limit reached", provider=self.name, code="POLL_LIMIT")
                await _sleep_until(interval, deadline)
        except SolverError as e:
            # The router books spend by this: a task the provider accepted may still be billed.
            e.task_created = task_id is not None
            self._record(kind, task, False, task_id, e.code or type(e).__name__, started, None, units=units)
            raise

    def _record(
        self,
        kind: str,
        task: Dict[str, Any],
        ok: bool,
        task_id: Optional[str],
        error_code: Optional[str],
        started: float,
        response: Optional[Dict[str, Any]],
        *,
        units: int = 1,
    ) -> Tuple[Optional[float], Optional[str]]:
        cost: Optional[float] = None
        source: Optional[str] = None
        if ok:
            reported = self.reported_cost(response or {})
            if reported is not None:
                cost, source = reported, "reported"
            elif kind in self.prices:
                n = units if kind in self.per_image_kinds else 1
                cost, source = round(self.prices[kind] * n / 1000.0, 6), "estimated"
        self.records.append(
            SolveRecord(
                provider=self.name,
                kind=kind,
                task_type=str(task.get("type", "")),
                ok=ok,
                task_id=task_id,
                error_code=error_code,
                cost_usd=cost,
                cost_source=source,
                elapsed_s=round(time.monotonic() - started, 3),
            )
        )
        return cost, source


async def _sleep_until(seconds: float, deadline: float) -> None:
    delay = min(seconds, deadline - time.monotonic())
    if delay > 0:
        await asyncio.sleep(delay)


def _str_or_none(value: Any) -> Optional[str]:
    return None if value in (None, "") else str(value)


def parse_grid(grid: Any, default: Tuple[int, int] = (3, 3)) -> Tuple[int, int]:
    """Parse ``"3x3"`` / ``(4, 4)`` / ``9`` / ``16`` into ``(rows, columns)``."""
    if grid is None or grid == "":
        return default
    if isinstance(grid, (tuple, list)) and len(grid) == 2:
        return int(grid[0]), int(grid[1])
    if isinstance(grid, int):
        side = int(round(grid**0.5))
        return side, side
    text = str(grid).lower().replace(" ", "")
    if "x" in text:
        rows, cols = text.split("x", 1)
        return int(rows), int(cols)
    side = int(round(int(text) ** 0.5))
    return side, side


__all__ = [
    "CreateTaskSolver",
    "JsonTransport",
    "UrllibTransport",
    "ProxySpec",
    "TOKEN_OPTIONS",
    "RECOGNITION_OPTIONS",
    "CONTROL_OPTIONS",
    "put",
    "parse_grid",
    "TOKEN_KINDS",
    "RECOGNITION_KINDS",
]


#: reCAPTCHA v2 image-grid label ids (as used by Google's ``rc-imageselect`` payload and CapSolver's
#: ``ReCaptchaV2Classification``, https://docs.capsolver.com/en/guide/recognition/ReCaptchaClassification/) mapped to
#: the English keywords shown in the challenge text ("Select all images with crosswalks").
RECAPTCHA_LABELS: Dict[str, Tuple[str, ...]] = {
    "/m/0pg52": ("taxis", "taxi"),
    "/m/01bjv": ("bus", "buses"),
    "/m/02yvhj": ("school bus", "school buses"),
    "/m/04_sv": ("motorcycles", "motorcycle"),
    "/m/013xlm": ("tractors", "tractor"),
    "/m/0h8ls87": ("chimneys", "chimney"),
    "/m/014xcs": ("crosswalks", "crosswalk"),
    "/m/015qff": ("traffic lights", "traffic light"),
    "/m/0199g": ("bicycles", "bicycle"),
    "/m/015qbp": ("parking meters", "parking meter"),
    "/m/0k4j": ("cars", "car"),
    "/m/015kr": ("bridges", "bridge"),
    "/m/019jd": ("boats", "boat"),
    "/m/0cdl1": ("palm trees", "palm tree"),
    "/m/09d_r": ("mountains or hills", "mountains", "hills"),
    "/m/01pns0": ("fire hydrants", "fire hydrant", "a fire hydrant"),
    "/m/01lynh": ("stairs", "staircase"),
}


def recaptcha_label_id(question: str) -> Optional[str]:
    """Map a reCAPTCHA question ("Select all images with crosswalks", "crosswalks" or "/m/014xcs") to its label id."""
    if not question:
        return None
    q = question.strip().lower()
    if q.startswith("/m/"):
        return q
    best: Optional[Tuple[int, str]] = None
    for label_id, words in RECAPTCHA_LABELS.items():
        for word in words:
            if word in q and (best is None or len(word) > best[0]):
                best = (len(word), label_id)
    return best[1] if best else None


def recaptcha_label_text(question: str) -> str:
    """Map a label id to its English text; other questions are returned unchanged."""
    q = (question or "").strip()
    if q.lower() in RECAPTCHA_LABELS:
        return RECAPTCHA_LABELS[q.lower()][0]
    return q
