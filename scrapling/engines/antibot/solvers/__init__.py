"""Paid CAPTCHA solver clients (CapMonster Cloud, CapSolver, 2Captcha) and a router.

The anti-bot handlers inject what a solver returns themselves (``cloudflare``, ``_awswaf_solver``,
``_imperva_solver``); this package only talks to the providers.

Nothing here runs unless the caller supplies provider keys, e.g.::

    router = SolverRouter.from_config({"capmonster": "KEY", "capsolver": "KEY", "2captcha": "KEY"})
    token = await router.scope().solve_token("turnstile", sitekey, page_url, deadline=deadline)
"""

from .base import (
    ALL_KINDS,
    EXPERIMENTAL_KINDS,
    RECOGNITION_KINDS,
    TOKEN_KINDS,
    SolveRecord,
    Solver,
    SolverAuthError,
    SolverBadRequest,
    SolverBalanceError,
    SolverBudgetExceeded,
    SolverConfigError,
    SolverError,
    SolverProxyNotAllowed,
    SolverRateLimited,
    SolverTimeout,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
    Token,
    provider_url,
)
from ._client import CreateTaskSolver, UrllibTransport, recaptcha_label_id, recaptcha_label_text
from .capmonster import CapMonsterSolver
from .capsolver import CapSolverSolver
from .twocaptcha import TwoCaptchaSolver
from .router import DEFAULT_ROUTES, SolverRouter

__all__ = [
    "ALL_KINDS",
    "EXPERIMENTAL_KINDS",
    "RECOGNITION_KINDS",
    "TOKEN_KINDS",
    "DEFAULT_ROUTES",
    "Token",
    "SolveRecord",
    "Solver",
    "SolverError",
    "SolverAuthError",
    "SolverBadRequest",
    "SolverBalanceError",
    "SolverBudgetExceeded",
    "SolverConfigError",
    "SolverProxyNotAllowed",
    "SolverRateLimited",
    "SolverTimeout",
    "SolverUnavailable",
    "SolverUnsolvable",
    "SolverUnsupported",
    "CreateTaskSolver",
    "UrllibTransport",
    "CapMonsterSolver",
    "CapSolverSolver",
    "TwoCaptchaSolver",
    "SolverRouter",
    "recaptcha_label_id",
    "recaptcha_label_text",
    "provider_url",
]
