"""Route CAPTCHA work to the right provider, fall back on failure and keep spend bounded.

A :class:`SolverRouter` implements the same :class:`~.base.Solver` interface as a single provider, so handlers call
``router.solve_token(...)`` / ``router.recognize(...)`` without caring which provider answers.

Default routing (first provider that is configured, supports the kind and is not cooling down wins):

=========================  ==========================================
Kind                       Providers, in order
=========================  ==========================================
Turnstile                  CapMonster, CapSolver, 2Captcha
reCAPTCHA (all variants)   CapMonster, 2Captcha, CapSolver
GeeTest v3 / v4            CapMonster, 2Captcha, CapSolver
AWS WAF token (cookie)     CapMonster, CapSolver
hCaptcha                   CapMonster (the only provider still listing it)
FunCaptcha                 2Captcha
Recognition (grid/slider)  CapSolver first; CapMonster/2Captcha where they offer the same task
=========================  ==========================================

Safety rails:

* **No proxies by default.** A ``proxy`` argument raises :class:`~.base.SolverProxyNotAllowed` unless the router was
  built with ``allow_proxy=True``. The provider never reaches the target through your network or proxy.
* **Caps.** ``max_solves_per_fetch`` (default 2) bounds how many challenges one fetch may pay for,
  ``max_attempts_per_solve`` bounds provider fallbacks, and optional USD caps bound spend per fetch and in total.
  Call :meth:`SolverRouter.scope` once per fetch to get fresh per-fetch counters that share the ledger.
* **Spend is booked when a task is sent**, at the provider's estimated price, not when an answer comes back: a task
  abandoned at the deadline, cancelled with its caller or lost to network errors may still be billed, so it still
  counts against the caps. It is refunded only for failures providers do not bill (a refused task, an unsolvable
  challenge, no free worker; :data:`~.base.FREE_FAILURES`), and replaced by the provider's own figure when it
  reports one. A provider that fails after accepting a task is not followed by another provider for that challenge.
  With a USD cap set, a provider that has no price for a kind is not used for it.
* **Page URLs** reach providers as ``scheme://host/path`` only (:func:`~.base.provider_url`): no query string,
  fragment or credentials. Recognition tasks send only images and the question.
* **Deadlines.** Every call takes ``deadline`` (a ``time.monotonic()`` value) and never runs past it.
* **Cooldowns.** A provider that reports a bad key, an empty balance or throttling is skipped for a while.
* **Experimental kinds** (Turnstile challenge-page tokens, DataDome sliders) are refused unless ``experimental=True``.
"""

from __future__ import annotations

import asyncio
import time

from scrapling.core._types import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from scrapling.core.utils import log as _default_log

from ._client import CONTROL_OPTIONS, RECOGNITION_OPTIONS, TOKEN_OPTIONS
from .base import (
    ALL_KINDS,
    EXPERIMENTAL_KINDS,
    FREE_FAILURES,
    RECOGNITION_KINDS,
    TOKEN_KINDS,
    SolveRecord,
    Solver,
    SolverBadRequest,
    SolverBudgetExceeded,
    SolverConfigError,
    SolverError,
    SolverProxyNotAllowed,
    SolverTimeout,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
    provider_url,
)

__all__ = ["SolverRouter", "DEFAULT_ROUTES", "PROVIDER_NAMES"]

#: Canonical provider names accepted in configs and routes.
PROVIDER_NAMES: Tuple[str, ...] = ("capmonster", "capsolver", "2captcha")
_ALIASES = {"capmonster": "capmonster", "capsolver": "capsolver", "2captcha": "2captcha", "twocaptcha": "2captcha"}

_TOKEN_DEFAULT = ("capmonster", "2captcha", "capsolver")
DEFAULT_ROUTES: Dict[str, Tuple[str, ...]] = {
    "turnstile": ("capmonster", "capsolver", "2captcha"),
    "turnstile_challenge": ("capmonster", "2captcha"),
    "recaptcha_v2": _TOKEN_DEFAULT,
    "recaptcha_v2_enterprise": _TOKEN_DEFAULT,
    "recaptcha_v3": _TOKEN_DEFAULT,
    "recaptcha_v3_enterprise": _TOKEN_DEFAULT,
    "hcaptcha": ("capmonster",),
    "geetest_v3": _TOKEN_DEFAULT,
    "geetest_v4": _TOKEN_DEFAULT,
    "awswaf": ("capmonster", "capsolver"),
    "awswaf_voucher": ("2captcha",),
    "funcaptcha": ("2captcha",),
    "recaptcha_grid": ("capsolver", "capmonster", "2captcha"),
    "geetest_slide": ("capsolver",),
    "datadome_slider": ("capsolver",),
    "slider": ("capsolver",),
    "rotate": ("capsolver",),
    "awswaf_images": ("capsolver",),
    "image_text": ("capsolver", "capmonster", "2captcha"),
    "coordinates": ("2captcha",),
}

_CONFIG_OPTIONS = frozenset(
    {
        "allow_proxy",
        "max_solves_per_fetch",
        "max_attempts_per_solve",
        "max_cost_usd_per_fetch",
        "max_cost_usd_total",
        "timeout",
        "routes",
        "prices",
        "experimental",
        "api_bases",
        "trust_env",
        "min_attempt_s",
    }
)


class _Shared:
    """State shared by a router and all of its per-fetch scopes."""

    def __init__(self, solvers: Dict[str, Solver], routes: Dict[str, Tuple[str, ...]]):
        self.solvers = solvers
        self.routes = routes
        self.cooldown_until: Dict[str, float] = {}
        self.records: List[SolveRecord] = []
        self.spent_usd = 0.0
        self.solves = 0


class SolverRouter:
    """Pick a provider per challenge kind, with fallback, caps and cost accounting.

    :param solvers: Provider clients (any objects implementing :class:`~.base.Solver`), keyed by their ``name``.
    :param routes: ``{kind: [provider, ...]}`` overrides merged over :data:`DEFAULT_ROUTES`.
    :param allow_proxy: Let callers pass ``proxy=`` through to providers. Off by default.
    :param max_solves_per_fetch: Challenges one scope may try to solve (``None`` = unlimited).
    :param max_attempts_per_solve: Provider attempts per challenge, fallbacks included.
    :param max_cost_usd_per_fetch: Spend cap per scope (estimated before each attempt).
    :param max_cost_usd_total: Spend cap across all scopes of this router.
    :param timeout: Default seconds per ``solve_token`` call when no ``deadline``/``timeout`` is given.
    :param experimental: Allow :data:`~.base.EXPERIMENTAL_KINDS`.
    :param min_attempt_s: Do not start another provider with less time than this left before the deadline
        (default: 5 s for token kinds, 2 s for recognition kinds).
    :param log: Logger to use (defaults to Scrapling's logger).
    """

    name = "router"

    def __init__(
        self,
        solvers: Union[Iterable[Solver], Mapping[str, Solver]],
        *,
        routes: Optional[Mapping[str, Sequence[str]]] = None,
        allow_proxy: bool = False,
        max_solves_per_fetch: Optional[int] = 2,
        max_attempts_per_solve: int = 3,
        max_cost_usd_per_fetch: Optional[float] = None,
        max_cost_usd_total: Optional[float] = None,
        timeout: float = 120.0,
        experimental: bool = False,
        min_attempt_s: Optional[float] = None,
        log: Any = None,
        _shared: Optional[_Shared] = None,
    ):
        if _shared is None:
            items = solvers.items() if isinstance(solvers, Mapping) else ((s.name, s) for s in solvers)
            by_name: Dict[str, Solver] = {}
            for key, solver in items:
                canonical = _ALIASES.get(str(key).lower(), str(key))
                if canonical in by_name:
                    raise SolverConfigError(f"duplicate solver {canonical!r}", provider=self.name)
                by_name[canonical] = solver
            merged = dict(DEFAULT_ROUTES)
            for kind, names in (routes or {}).items():
                if kind not in ALL_KINDS:
                    raise SolverConfigError(f"unknown kind {kind!r} in routes", provider=self.name)
                canon = tuple(_ALIASES.get(str(n).lower(), str(n)) for n in names)
                merged[kind] = canon
            _shared = _Shared(by_name, merged)
        self._shared = _shared
        self.allow_proxy = bool(allow_proxy)
        self.max_solves_per_fetch = max_solves_per_fetch
        self.max_attempts_per_solve = max(1, int(max_attempts_per_solve))
        self.max_cost_usd_per_fetch = max_cost_usd_per_fetch
        self.max_cost_usd_total = max_cost_usd_total
        self.timeout = float(timeout)
        self.experimental = bool(experimental)
        self.min_attempt_s = None if min_attempt_s is None else float(min_attempt_s)
        self._log = log or _default_log
        self._is_scope = _shared is not None and not solvers
        self._solves = 0
        self._attempts = 0
        self._spent_usd = 0.0
        self._records: List[SolveRecord] = []

    # ---- construction -----------------------------------------------------------------------------------------

    @classmethod
    def from_config(
        cls, config: Optional[Mapping[str, Any]], *, transport: Any = None, log: Any = None
    ) -> Optional["SolverRouter"]:
        """Build a router from a plain dict, or return ``None`` when no provider key is set.

        Example::

            {"capmonster": "KEY", "capsolver": "KEY", "2captcha": "KEY", "allow_proxy": False, "max_solves_per_fetch": 2}

        Optional keys: ``max_attempts_per_solve``, ``max_cost_usd_per_fetch``, ``max_cost_usd_total``, ``timeout``,
        ``routes`` (``{kind: [provider, ...]}``), ``prices`` (``{provider: {kind: usd_per_1000}}``),
        ``experimental``, ``api_bases`` (``{provider: url}``) and ``trust_env``. Unknown keys raise
        :class:`~.base.SolverConfigError` (the message names the key, never a value).
        """
        from .capmonster import CapMonsterSolver
        from .capsolver import CapSolverSolver
        from .twocaptcha import TwoCaptchaSolver
        from ._client import UrllibTransport

        if not config:
            return None
        classes = {"capmonster": CapMonsterSolver, "capsolver": CapSolverSolver, "2captcha": TwoCaptchaSolver}
        keys: Dict[str, str] = {}
        options: Dict[str, Any] = {}
        for raw_name, value in config.items():
            name = str(raw_name).lower()
            if name in _ALIASES:
                canonical = _ALIASES[name]
                if value in (None, ""):
                    continue
                if not isinstance(value, str):
                    raise SolverConfigError(f"the {canonical} key must be a string", provider=cls.name)
                if canonical in keys:
                    raise SolverConfigError(f"{canonical} is configured twice", provider=cls.name)
                keys[canonical] = value
            elif name in _CONFIG_OPTIONS:
                options[name] = value
            else:
                raise SolverConfigError(f"unknown solver option {str(raw_name)[:40]!r}", provider=cls.name)
        if not keys:
            return None
        allow_proxy = bool(options.get("allow_proxy", False))
        api_bases = options.get("api_bases") or {}
        prices = options.get("prices") or {}
        if transport is None:
            transport = UrllibTransport(trust_env=bool(options.get("trust_env", False)))
        solvers = []
        for name, key in keys.items():
            solvers.append(
                classes[name](
                    key,
                    api_base=api_bases.get(name),
                    allow_proxy=allow_proxy,
                    transport=transport,
                    prices=prices.get(name),
                )
            )
        max_solves = options.get("max_solves_per_fetch", 2)
        return cls(
            solvers,
            routes=options.get("routes"),
            allow_proxy=allow_proxy,
            max_solves_per_fetch=None if max_solves is None else int(max_solves),
            max_attempts_per_solve=int(options.get("max_attempts_per_solve", 3)),
            max_cost_usd_per_fetch=_opt_float(options.get("max_cost_usd_per_fetch")),
            max_cost_usd_total=_opt_float(options.get("max_cost_usd_total")),
            timeout=float(options.get("timeout") or 120.0),
            experimental=bool(options.get("experimental", False)),
            min_attempt_s=_opt_float(options.get("min_attempt_s")),
            log=log,
        )

    @property
    def is_scope(self) -> bool:
        """True for a router made by :meth:`scope` (per-fetch counters over a shared ledger)."""
        return self._is_scope

    def scope(self) -> "SolverRouter":
        """Return a router with fresh per-fetch counters that shares providers, cooldowns and the total ledger."""
        return SolverRouter(
            (),
            allow_proxy=self.allow_proxy,
            max_solves_per_fetch=self.max_solves_per_fetch,
            max_attempts_per_solve=self.max_attempts_per_solve,
            max_cost_usd_per_fetch=self.max_cost_usd_per_fetch,
            max_cost_usd_total=self.max_cost_usd_total,
            timeout=self.timeout,
            experimental=self.experimental,
            min_attempt_s=self.min_attempt_s,
            log=self._log,
            _shared=self._shared,
        )

    # ---- introspection ----------------------------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"<SolverRouter providers={sorted(self._shared.solvers)} allow_proxy={self.allow_proxy}>"

    @property
    def providers(self) -> List[str]:
        return sorted(self._shared.solvers)

    def route(self, kind: str) -> List[str]:
        """Providers that would be tried for ``kind`` right now, in order."""
        now = time.monotonic()
        out = []
        for name in self._shared.routes.get(kind, ()):
            solver = self._shared.solvers.get(name)
            if solver is None or not _supports(solver, kind):
                continue
            if self._shared.cooldown_until.get(name, 0.0) > now:
                continue
            out.append(name)
        return out

    def supports(self, kind: str) -> bool:
        if kind in EXPERIMENTAL_KINDS and not self.experimental:
            return False
        return any(
            _supports(self._shared.solvers[n], kind)
            for n in self._shared.routes.get(kind, ())
            if n in self._shared.solvers
        )

    @property
    def records(self) -> List[SolveRecord]:
        """Attempts made through this scope."""
        return list(self._records)

    @property
    def all_records(self) -> List[SolveRecord]:
        """Attempts made through this router and every scope derived from it."""
        return list(self._shared.records)

    @property
    def spent_usd(self) -> float:
        return round(self._spent_usd, 6)

    @property
    def total_spent_usd(self) -> float:
        return round(self._shared.spent_usd, 6)

    @property
    def solves_used(self) -> int:
        return self._solves

    @property
    def attempts(self) -> int:
        """Provider attempts made through this scope (each one may have been billed)."""
        return self._attempts

    def summary(self) -> Dict[str, Any]:
        """A JSON-safe summary of this scope's activity (no keys, tokens or proxies)."""
        return {
            "solves": self._solves,
            "attempts": self._attempts,
            "cost_usd": self.spent_usd,
            "records": [
                {
                    "provider": r.provider,
                    "kind": r.kind,
                    "ok": r.ok,
                    "error": r.error_code,
                    "cost_usd": r.cost_usd,
                    "cost_source": r.cost_source,
                    "elapsed_s": r.elapsed_s,
                }
                for r in self._records
            ],
        }

    # ---- solving ----------------------------------------------------------------------------------------------

    async def solve_token(self, kind: str, sitekey: str, page_url: str, **extra: Any) -> str:
        if kind not in TOKEN_KINDS:
            raise SolverUnsupported(f"{kind!r} is not a token kind", provider=self.name, code="KIND_UNSUPPORTED")
        # Providers learn the page's host and path only (no query string, fragment or credentials).
        page_url = provider_url(page_url) or page_url
        return await self._dispatch(
            kind, extra, TOKEN_OPTIONS, lambda s, kw: s.solve_token(kind, sitekey, page_url, **kw)
        )

    async def recognize(self, kind: str, images: List[bytes], **extra: Any) -> Dict[str, Any]:
        if kind not in RECOGNITION_KINDS:
            raise SolverUnsupported(f"{kind!r} is not a recognition kind", provider=self.name, code="KIND_UNSUPPORTED")
        if extra.get("proxy") not in (None, ""):
            raise SolverProxyNotAllowed("recognition tasks never take a proxy", provider=self.name, code="PROXY")
        if extra.get("page_url"):
            extra["page_url"] = provider_url(extra["page_url"]) or None
        return await self._dispatch(
            kind,
            extra,
            RECOGNITION_OPTIONS,
            lambda s, kw: s.recognize(kind, images, **kw),
            units=len(images) if isinstance(images, (list, tuple)) else 1,
        )

    async def _dispatch(self, kind: str, extra: Dict[str, Any], allowed: frozenset, call, units: int = 1) -> Any:
        unknown = sorted(set(extra) - allowed - CONTROL_OPTIONS)
        if unknown:
            raise SolverBadRequest(
                f"unknown options: {', '.join(unknown)}", provider=self.name, code="BAD_OPTIONS", fallback=False
            )
        if kind in EXPERIMENTAL_KINDS and not self.experimental:
            raise SolverUnsupported(f"{kind} is experimental and disabled", provider=self.name, code="EXPERIMENTAL")
        if extra.get("proxy") not in (None, "") and not self.allow_proxy:
            raise SolverProxyNotAllowed(
                "proxies are disabled (allow_proxy=False)", provider=self.name, code="PROXY_NOT_ALLOWED"
            )

        timeout = extra.pop("timeout", None)
        deadline = time.monotonic() + float(timeout or self.timeout)
        if extra.get("deadline") is not None:
            deadline = min(deadline, float(extra.pop("deadline")))
        else:
            extra.pop("deadline", None)

        candidates = self.route(kind)
        if not candidates:
            raise SolverUnsupported(f"no configured provider for {kind}", provider=self.name, code="NO_PROVIDER")
        if self.max_solves_per_fetch is not None and self._solves >= self.max_solves_per_fetch:
            raise SolverBudgetExceeded(
                f"max_solves_per_fetch={self.max_solves_per_fetch} reached", provider=self.name, code="MAX_SOLVES"
            )

        errors: List[SolverError] = []
        attempts = 0
        counted = False
        for name in candidates:
            if attempts >= self.max_attempts_per_solve:
                break
            if self._shared.cooldown_until.get(name, 0.0) > time.monotonic():
                continue  # cooled down by a concurrent call
            solver = self._shared.solvers[name]
            estimate = _price(solver, kind, units)
            if estimate is None:
                if self._capped:
                    # Without a price the spend caps cannot bound this provider for this kind.
                    errors.append(SolverBudgetExceeded("no price with a spend cap", provider=name, code="NO_PRICE"))
                    continue
                estimate = 0.0
            if not self._within_budget(estimate):
                errors.append(SolverBudgetExceeded("spend cap reached", provider=name, code="MAX_COST"))
                continue
            remaining = deadline - time.monotonic()
            floor = (
                self.min_attempt_s if self.min_attempt_s is not None else (2.0 if kind in RECOGNITION_KINDS else 5.0)
            )
            if remaining < floor:
                errors.append(SolverTimeout("no time left for another provider", provider=name, code="DEADLINE"))
                break
            if not counted:
                self._solves += 1
                self._shared.solves += 1
                counted = True
            attempts += 1
            self._attempts += 1
            started = time.monotonic()
            # Booked before the call: a task cancelled or abandoned on the way may still be billed.
            self._charge(estimate)
            try:
                result = await call(solver, dict(extra, deadline=deadline))
            except SolverError as e:
                billed = _billed(e)
                if not billed:
                    self._charge(-estimate)
                self._note(
                    SolveRecord(
                        provider=name,
                        kind=kind,
                        task_type="",
                        ok=False,
                        error_code=e.code or type(e).__name__,
                        cost_usd=round(estimate, 6) if billed and estimate else None,
                        cost_source="estimated" if billed and estimate else None,
                        elapsed_s=round(time.monotonic() - started, 3),
                    )
                )
                if e.cooldown_s:
                    self._shared.cooldown_until[name] = time.monotonic() + float(e.cooldown_s)
                self._log.warning(f"captcha solver: {kind} via {name} failed ({e.code or type(e).__name__})")
                errors.append(e)
                # A provider that took the task and then failed may still bill it: do not pay a second one.
                if not e.fallback or (e.task_created and isinstance(e, (SolverUnavailable, SolverTimeout))):
                    raise
                continue
            except asyncio.CancelledError:
                # The caller gave up (its deadline): the task may still finish and be billed, so the estimate stays.
                self._note(
                    SolveRecord(
                        provider=name,
                        kind=kind,
                        task_type="",
                        ok=False,
                        error_code="CANCELLED",
                        cost_usd=round(estimate, 6) if estimate else None,
                        cost_source="estimated" if estimate else None,
                        elapsed_s=round(time.monotonic() - started, 3),
                    )
                )
                raise
            except Exception as e:  # a third-party Solver implementation misbehaved
                err = SolverUnavailable(f"{type(e).__name__}", provider=name, code="SOLVER_CRASH")
                self._note(
                    SolveRecord(
                        provider=name,
                        kind=kind,
                        task_type="",
                        ok=False,
                        error_code=err.code,
                        cost_usd=round(estimate, 6) if estimate else None,
                        cost_source="estimated" if estimate else None,
                        elapsed_s=round(time.monotonic() - started, 3),
                    )
                )
                self._log.warning(f"captcha solver: {kind} via {name} crashed ({type(e).__name__})")
                errors.append(err)
                continue
            cost, source = _result_cost(result)
            if cost is not None:
                self._charge(cost - estimate)  # the provider's (or the client's) own figure replaces the estimate
            elif estimate:
                cost, source = round(estimate, 6), "estimated"
            self._note(
                SolveRecord(
                    provider=name,
                    kind=kind,
                    task_type="",
                    ok=True,
                    task_id=_result_attr(result, "task_id"),
                    cost_usd=cost,
                    cost_source=source,
                    elapsed_s=round(time.monotonic() - started, 3),
                )
            )
            self._log.info(
                f"captcha solver: {kind} via {name} solved in {time.monotonic() - started:.1f}s"
                + (f" (${cost:.5f} {source})" if cost is not None else "")
            )
            return result

        summary = (
            ", ".join(f"{e.provider or '?'}={e.code or type(e).__name__}" for e in errors) or "no provider attempted"
        )
        last = errors[-1] if errors else SolverUnavailable("", provider=self.name)
        failure = type(last)(f"{kind} not solved: {summary}", provider=self.name, code=last.code, fallback=False)
        failure.errors = errors  # type: ignore[attr-defined]
        raise failure

    @property
    def _capped(self) -> bool:
        return self.max_cost_usd_per_fetch is not None or self.max_cost_usd_total is not None

    def _charge(self, amount: float) -> None:
        """Book ``amount`` USD (negative to refund) on this scope and on the shared ledger."""
        if amount:
            self._spent_usd = max(0.0, self._spent_usd + amount)
            self._shared.spent_usd = max(0.0, self._shared.spent_usd + amount)

    def _within_budget(self, estimate: float) -> bool:
        if self.max_cost_usd_per_fetch is not None and self._spent_usd + estimate > self.max_cost_usd_per_fetch + 1e-12:
            return False
        if self.max_cost_usd_total is not None and self._shared.spent_usd + estimate > self.max_cost_usd_total + 1e-12:
            return False
        return True

    def _note(self, record: SolveRecord) -> None:
        self._records.append(record)
        self._shared.records.append(record)


def _supports(solver: Solver, kind: str) -> bool:
    try:
        return bool(solver.supports(kind))
    except Exception:  # pragma: no cover - defensive against third-party solvers
        return False


def _price(solver: Any, kind: str, units: int = 1) -> Optional[float]:
    """Estimated USD for one ``kind`` task at ``solver`` (``units`` images for per-image kinds), or ``None``."""
    prices = getattr(solver, "prices", None) or {}
    if kind not in prices:
        return None
    try:
        per_task = float(prices[kind]) / 1000.0
    except (TypeError, ValueError):  # pragma: no cover
        return None
    per_image = kind in (getattr(solver, "per_image_kinds", None) or ())
    return per_task * max(1, int(units)) if per_image else per_task


def _billed(error: SolverError) -> bool:
    """Whether a failed attempt may still be billed by the provider (and so stays on the ledger)."""
    if isinstance(error, SolverUnsolvable) or error.task_created is False:
        return False
    if error.task_created is True:
        return True
    return not isinstance(error, FREE_FAILURES)


def _result_attr(result: Any, name: str) -> Any:
    if isinstance(result, dict):
        return result.get(name)
    return getattr(result, name, None)


def _result_cost(result: Any) -> Tuple[Optional[float], Optional[str]]:
    cost = _result_attr(result, "cost_usd")
    source = _result_attr(result, "cost_source")
    try:
        return (None if cost is None else float(cost)), source
    except (TypeError, ValueError):  # pragma: no cover
        return None, None


def _opt_float(value: Any) -> Optional[float]:
    return None if value is None else float(value)
