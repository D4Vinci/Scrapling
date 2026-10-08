"""Shared types for the paid CAPTCHA solver clients.

The solver clients in this package call commercial CAPTCHA-solving services (CapMonster Cloud, CapSolver and
2Captcha). They are only ever used when the caller passes its own API keys, and they never route the target
site's traffic through the service: token tasks are "proxyless" by default (the service solves the widget from
its own network and returns a token that the local browser injects), and recognition tasks only send challenge
images (the local browser performs the clicks or drags itself).

Two families of work are supported:

* **Token tasks** (:data:`TOKEN_KINDS`): Turnstile, reCAPTCHA v2/v3/Enterprise, hCaptcha, GeeTest v3/v4, AWS WAF
  and FunCaptcha. ``solve_token`` returns a :class:`Token`, which is a ``str`` (the value to inject) that also
  carries the full provider solution, the provider name and the cost of the solve.
* **Recognition tasks** (:data:`RECOGNITION_KINDS`): reCAPTCHA image grids, slider puzzles (GeeTest, DataDome),
  AWS WAF image puzzles, rotation puzzles, plain image-to-text and click coordinates. ``recognize`` returns a
  normalized ``dict`` (see :class:`Solver.recognize`).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from urllib.parse import urlsplit

from scrapling.core._types import Any, Dict, FrozenSet, List, Mapping, Optional, Protocol, Tuple, runtime_checkable

__all__ = [
    "TOKEN_KINDS",
    "RECOGNITION_KINDS",
    "EXPERIMENTAL_KINDS",
    "ALL_KINDS",
    "TOKEN_TTL",
    "Token",
    "SolveRecord",
    "Solver",
    "SolverError",
    "SolverConfigError",
    "SolverAuthError",
    "SolverBalanceError",
    "SolverUnsupported",
    "SolverBadRequest",
    "SolverUnsolvable",
    "SolverRateLimited",
    "SolverUnavailable",
    "SolverTimeout",
    "SolverBudgetExceeded",
    "SolverProxyNotAllowed",
    "FREE_FAILURES",
    "provider_url",
    "redact",
]

#: Challenge kinds that produce a token (or cookie value) for the browser to inject.
TOKEN_KINDS: FrozenSet[str] = frozenset(
    {
        "turnstile",  # Cloudflare Turnstile widget (sitekey ``0x4AAA…``)
        "turnstile_challenge",  # Turnstile embedded in a Cloudflare challenge page (experimental, see below)
        "recaptcha_v2",  # reCAPTCHA v2 checkbox or invisible
        "recaptcha_v2_enterprise",
        "recaptcha_v3",
        "recaptcha_v3_enterprise",
        "hcaptcha",
        "geetest_v3",
        "geetest_v4",
        "awswaf",  # AWS WAF CAPTCHA, returns the ``aws-waf-token`` cookie value
        "awswaf_voucher",  # AWS WAF CAPTCHA, returns ``captcha_voucher`` + ``existing_token`` (2Captcha)
        "funcaptcha",  # Arkose Labs FunCaptcha
    }
)

#: Challenge kinds where only images leave the machine and the caller performs the interaction itself.
RECOGNITION_KINDS: FrozenSet[str] = frozenset(
    {
        "recaptcha_grid",  # reCAPTCHA v2 image grid -> ``objects`` (0-based tile indices)
        "geetest_slide",  # GeeTest slide puzzle -> ``distance`` (pixels)
        "datadome_slider",  # DataDome slider puzzle -> ``distance`` (pixels)
        "slider",  # Generic piece + background slider -> ``distance`` (pixels)
        "rotate",  # Rotation puzzle -> ``angle`` (degrees)
        "awswaf_images",  # AWS WAF image puzzle -> ``objects`` / ``box`` / ``distance``
        "image_text",  # Plain text captcha -> ``text``
        "coordinates",  # Free-form "click on …" image -> ``points``
    }
)

#: Kinds that work in principle but are not proven against real sites. Routers refuse them unless enabled.
EXPERIMENTAL_KINDS: FrozenSet[str] = frozenset({"turnstile_challenge", "datadome_slider"})

ALL_KINDS: FrozenSet[str] = TOKEN_KINDS | RECOGNITION_KINDS

#: How long a freshly minted token stays usable, in seconds (vendor documentation; used for ``Token.expires_at``).
#: Turnstile: 300 s (https://developers.cloudflare.com/turnstile/get-started/server-side-validation/);
#: reCAPTCHA: 120 s (https://developers.google.com/recaptcha/docs/verify); hCaptcha: 120 s (https://docs.hcaptcha.com/);
#: AWS WAF: 300 s immunity (https://docs.aws.amazon.com/waf/latest/developerguide/waf-tokens-immunity-times.html).
TOKEN_TTL: Mapping[str, float] = {
    "turnstile": 300.0,
    "turnstile_challenge": 300.0,
    "recaptcha_v2": 120.0,
    "recaptcha_v2_enterprise": 120.0,
    "recaptcha_v3": 120.0,
    "recaptcha_v3_enterprise": 120.0,
    "hcaptcha": 120.0,
    "geetest_v3": 60.0,
    "geetest_v4": 60.0,
    "awswaf": 300.0,
    "awswaf_voucher": 60.0,
    "funcaptcha": 120.0,
}


class Token(str):
    """A solved token. The string value is what gets injected into the page; the attributes describe the solve.

    The primary string value per kind is:

    * ``turnstile`` / ``turnstile_challenge``: the Turnstile token.
    * ``recaptcha_*`` / ``hcaptcha``: the ``g-recaptcha-response`` / ``h-captcha-response`` value.
    * ``geetest_v3``: the ``validate`` value (``fields`` also holds ``challenge`` and ``seccode``).
    * ``geetest_v4``: the ``captcha_output`` value (``fields`` holds ``lot_number``, ``pass_token``, ``gen_time``, …).
    * ``awswaf``: the ``aws-waf-token`` cookie value.
    * ``awswaf_voucher``: the ``captcha_voucher`` value (``fields`` also holds ``existing_token``).
    * ``funcaptcha``: the Arkose token.
    """

    kind: str
    provider: str
    task_id: Optional[str]
    fields: Dict[str, Any]
    user_agent: Optional[str]
    cost_usd: Optional[float]
    cost_source: Optional[str]
    elapsed_s: float
    expires_at: float

    def __new__(
        cls,
        value: str,
        *,
        kind: str,
        provider: str,
        task_id: Optional[str] = None,
        fields: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
        cost_usd: Optional[float] = None,
        cost_source: Optional[str] = None,
        elapsed_s: float = 0.0,
        created_at: Optional[float] = None,
    ) -> "Token":
        obj = super().__new__(cls, value)
        obj.kind = kind
        obj.provider = provider
        obj.task_id = task_id
        obj.fields = dict(fields or {})
        obj.user_agent = user_agent
        obj.cost_usd = cost_usd
        obj.cost_source = cost_source
        obj.elapsed_s = elapsed_s
        obj.expires_at = (created_at if created_at is not None else time.monotonic()) + TOKEN_TTL.get(kind, 120.0)
        return obj

    @property
    def expired(self) -> bool:
        """True when the vendor's documented validity window has passed."""
        return time.monotonic() >= self.expires_at

    def __repr__(self) -> str:
        # Tokens are bearer credentials for the target site, so never print the value itself.
        return f"<Token kind={self.kind} provider={self.provider} len={len(self)} cost_usd={self.cost_usd}>"

    def __reduce__(self):  # pragma: no cover - pickling support for multiprocessing users
        return (
            _rebuild_token,
            (str(self), self.kind, self.provider, self.task_id, self.fields, self.user_agent, self.cost_usd),
        )


def _rebuild_token(value, kind, provider, task_id, fields, user_agent, cost_usd):  # pragma: no cover
    return Token(
        value, kind=kind, provider=provider, task_id=task_id, fields=fields, user_agent=user_agent, cost_usd=cost_usd
    )


@dataclass
class SolveRecord:
    """One attempt at one provider. Routers keep a ledger of these for cost accounting."""

    provider: str
    kind: str
    task_type: str
    ok: bool
    task_id: Optional[str] = None
    error_code: Optional[str] = None
    cost_usd: Optional[float] = None
    cost_source: Optional[str] = None  # "reported" (by the provider), "estimated" (price table) or None
    elapsed_s: float = 0.0
    started_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@runtime_checkable
class Solver(Protocol):
    """The interface every solver client (and the router) implements."""

    name: str

    def supports(self, kind: str) -> bool:
        """Return True if this solver can handle the challenge ``kind``."""
        ...

    async def solve_token(self, kind: str, sitekey: str, page_url: str, **extra: Any) -> str:
        """Solve a token challenge and return the value to inject (a :class:`Token`).

        Common keyword arguments (all optional unless the kind needs them):
        ``action``, ``cdata``, ``page_data``, ``user_agent``, ``invisible``, ``enterprise_payload``, ``api_domain``,
        ``data_s``, ``min_score``, ``cookies``, ``challenge`` (GeeTest v3), ``api_server`` (GeeTest), ``risk_type``,
        ``init_parameters`` (GeeTest v4), ``aws_context``, ``aws_iv``, ``aws_challenge_script``,
        ``aws_captcha_script``, ``aws_problem_url``, ``aws_api_key``, ``aws_existing_token``,
        ``funcaptcha_subdomain``, ``data`` (FunCaptcha blob / hCaptcha rqdata), ``proxy``, ``timeout`` (seconds) and
        ``deadline`` (``time.monotonic()`` value).
        """
        ...

    async def recognize(self, kind: str, images: List[bytes], **extra: Any) -> Dict[str, Any]:
        """Run a recognition task and return a normalized dict.

        Result keys by kind: ``recaptcha_grid`` -> ``objects`` (0-based tile indices) and ``has_object``;
        ``*slide*``/``slider`` -> ``distance``; ``rotate`` -> ``angle``; ``awswaf_images`` -> ``objects``, ``box``,
        ``distance``; ``image_text`` -> ``text``; ``coordinates`` -> ``points`` (list of ``(x, y)``).
        Every result also has ``provider``, ``task_id``, ``cost_usd``, ``cost_source``, ``elapsed_s`` and ``raw``.

        Common keyword arguments: ``question``, ``grid`` (``"3x3"``/``"4x4"``), ``page_url``, ``sitekey``,
        ``comment``, ``timeout`` and ``deadline``.
        """
        ...


# --------------------------------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------------------------------


class SolverError(Exception):
    """Base class for solver failures.

    :param provider: The solver name (``capmonster``, ``capsolver``, ``2captcha`` or ``router``).
    :param code: The provider's error code (e.g. ``ERROR_ZERO_BALANCE``) or an internal code.
    :param fallback: Whether a router should try the next provider.
    :param cooldown_s: If set, the router stops using this provider for this many seconds (bad key, no balance…).
    :param task_created: Whether the provider had accepted a task (``createTask`` returned a task id) when this was
        raised: ``True`` means the provider may still finish and bill it, ``False`` that nothing was billed, ``None``
        that it is not known (a third-party solver). Routers use it for spend accounting.
    """

    default_fallback: bool = True
    default_cooldown_s: Optional[float] = None
    task_created: Optional[bool] = None

    def __init__(
        self,
        message: str = "",
        *,
        provider: str = "",
        code: str = "",
        fallback: Optional[bool] = None,
        cooldown_s: Optional[float] = None,
        task_created: Optional[bool] = None,
    ):
        self.task_created = task_created
        self.provider = provider
        self.code = code
        self.message = message
        self.fallback = self.default_fallback if fallback is None else fallback
        self.cooldown_s = self.default_cooldown_s if cooldown_s is None else cooldown_s
        super().__init__(self.__str__())

    def __str__(self) -> str:
        parts = [p for p in (self.provider, self.code, self.message) if p]
        return ": ".join(parts) or self.__class__.__name__


class SolverConfigError(SolverError, ValueError):
    """The solver or router configuration is invalid."""

    default_fallback = False


class SolverAuthError(SolverError):
    """The API key was rejected, or the calling IP is not allowed."""

    default_cooldown_s = 600.0


class SolverBalanceError(SolverError):
    """The account has no funds left."""

    default_cooldown_s = 600.0


class SolverUnsupported(SolverError):
    """The provider does not offer this kind of task (or not with the given options)."""


class SolverBadRequest(SolverError):
    """The provider rejected the task parameters."""


class SolverUnsolvable(SolverError):
    """The provider could not solve the challenge (usually free of charge)."""


class SolverRateLimited(SolverError):
    """The provider is throttling this account or has no free workers."""

    default_cooldown_s = 60.0


class SolverUnavailable(SolverError):
    """Network failure, unexpected response or provider outage."""


class SolverTimeout(SolverError):
    """The solve did not finish before the deadline."""


class SolverBudgetExceeded(SolverError):
    """A router cap (solves per fetch, attempts or spend) would be exceeded."""

    default_fallback = False


class SolverProxyNotAllowed(SolverError):
    """A proxy was passed while proxies are disabled (the default)."""

    default_fallback = False


#: Failures providers do not bill: the task was refused, could not be solved, or never reached a worker.
FREE_FAILURES: Tuple[type, ...] = (
    SolverConfigError,
    SolverAuthError,
    SolverBalanceError,
    SolverUnsupported,
    SolverBadRequest,
    SolverUnsolvable,
    SolverRateLimited,
    SolverBudgetExceeded,
    SolverProxyNotAllowed,
)


def provider_url(url: str) -> str:
    """What a provider is told about the page: ``scheme://host[:port]/path`` with no query, fragment or credentials.

    Token tasks are bound to the page's host (and at most its path); the query string and fragment can carry
    signed-link tokens, OAuth codes or session ids that no provider needs. Anything that is not an http(s) URL is
    returned as an empty string.
    """
    try:
        parts = urlsplit(str(url or "").strip())
        host = (parts.hostname or "").lower()
        port = parts.port
    except ValueError:
        return ""
    if parts.scheme.lower() not in ("http", "https") or not host:
        return ""
    if ":" in host:  # an IPv6 literal
        host = f"[{host}]"
    netloc = f"{host}:{port}" if port else host
    return f"{parts.scheme.lower()}://{netloc}{parts.path or '/'}"


def redact(text: str, secrets: Tuple[str, ...]) -> str:
    """Replace every occurrence of each secret in ``text`` with ``***``."""
    for secret in secrets:
        if secret and len(secret) >= 4:
            text = text.replace(secret, "***")
    return text
