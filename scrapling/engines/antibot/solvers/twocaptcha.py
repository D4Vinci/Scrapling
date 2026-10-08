"""2Captcha client, API v2 (https://2captcha.com/api-docs).

API: ``https://api.2captcha.com/createTask`` and ``/getTaskResult``; ``getTaskResult`` reports the charged ``cost``
(https://2captcha.com/api-docs/get-task-result), so 2Captcha costs are exact rather than estimated. Request shapes:

* Turnstile (widget and challenge page): https://2captcha.com/api-docs/cloudflare-turnstile (``TurnstileTaskProxyless``
  with ``action``, ``data`` = cData, ``pagedata`` = chlPageData).
* reCAPTCHA v2: https://2captcha.com/api-docs/recaptcha-v2 (``RecaptchaV2TaskProxyless``); v2 Enterprise:
  https://2captcha.com/api-docs/recaptcha-v2-enterprise (``RecaptchaV2EnterpriseTaskProxyless``); v3 (and v3
  Enterprise via ``isEnterprise``): https://2captcha.com/api-docs/recaptcha-v3 (``RecaptchaV3TaskProxyless``,
  ``minScore`` one of 0.3 / 0.7 / 0.9).
* GeeTest: https://2captcha.com/api-docs/geetest (``GeeTestTaskProxyless``; v4 via ``version: 4`` and
  ``initParameters.captcha_id``).
* AWS WAF: https://2captcha.com/api-docs/amazon-aws-waf-captcha (``AmazonTaskProxyless`` -> ``captcha_voucher`` and
  ``existing_token``; exposed as kind ``awswaf_voucher`` because it does not return the ``aws-waf-token`` cookie).
* FunCaptcha: https://2captcha.com/api-docs/arkoselabs-funcaptcha (``FunCaptchaTaskProxyless``).
* Recognition: https://2captcha.com/api-docs/grid (``GridTask``; ``click`` indices are 1-based),
  https://2captcha.com/api-docs/coordinates (``CoordinatesTask``), https://2captcha.com/api-docs/normal-captcha
  (``ImageToTextTask``).
* Errors: https://2captcha.com/api-docs/error-codes. Reports: https://2captcha.com/api-docs/report-incorrect.

2Captcha's hCaptcha documentation page returns 404 (2026-10-07), so hCaptcha is not offered here.
"""

from __future__ import annotations

import json
import time

from scrapling.core._types import Any, Dict, List, Optional, Tuple

from ._client import CreateTaskSolver, ProxySpec, parse_grid, put, recaptcha_label_text
from .base import (
    SolverAuthError,
    SolverBadRequest,
    SolverBalanceError,
    SolverRateLimited,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
)

__all__ = ["TwoCaptchaSolver"]

_V3_SCORES = (0.3, 0.7, 0.9)


class TwoCaptchaSolver(CreateTaskSolver):
    """2Captcha. The default provider for FunCaptcha and the fallback for every other token kind."""

    name = "2captcha"
    default_api_base = "https://api.2captcha.com"
    token_kinds = frozenset(
        {
            "turnstile",
            "turnstile_challenge",
            "recaptcha_v2",
            "recaptcha_v2_enterprise",
            "recaptcha_v3",
            "recaptcha_v3_enterprise",
            "geetest_v3",
            "geetest_v4",
            "awswaf_voucher",
            "funcaptcha",
        }
    )
    recognition_kinds = frozenset({"recaptcha_grid", "coordinates", "image_text"})
    error_map = {
        "ERROR_KEY_DOES_NOT_EXIST": SolverAuthError,
        "ERROR_WRONG_USER_KEY": SolverAuthError,
        "ERROR_IP_NOT_ALLOWED": SolverAuthError,
        "ERROR_IP_BLOCKED": SolverAuthError,
        "ERROR_ACCOUNT_SUSPENDED": SolverAuthError,
        "ERROR_ZERO_BALANCE": SolverBalanceError,
        "ERROR_NO_SLOT_AVAILABLE": SolverRateLimited,
        "ERROR_CAPTCHA_UNSOLVABLE": SolverUnsolvable,
        "ERROR_BAD_DUPLICATES": SolverUnsolvable,
        "ERROR_TASK_NOT_SUPPORTED": SolverUnsupported,
        "ERROR_NO_SUCH_METHOD": SolverUnsupported,
        "ERROR_TASK_ABSENT": SolverBadRequest,
        "ERROR_PAGEURL": SolverBadRequest,
        "ERROR_BAD_PARAMETERS": SolverBadRequest,
        "ERROR_RECAPTCHA_INVALID_SITEKEY": SolverBadRequest,
        "ERROR_ZERO_CAPTCHA_FILESIZE": SolverBadRequest,
        "ERROR_TOO_BIG_CAPTCHA_FILESIZE": SolverBadRequest,
        "ERROR_IMAGE_TYPE_NOT_SUPPORTED": SolverBadRequest,
        "ERROR_BAD_IMGINSTRUCTIONS": SolverBadRequest,
        "ERROR_BAD_PROXY": SolverBadRequest,
        "ERROR_NO_SUCH_CAPCHA_ID": SolverUnavailable,
    }
    cooldown_codes = {"ERROR_NO_SLOT_AVAILABLE": 10.0}
    # 2Captcha reports the cost of each task; these estimates are only used if it does not
    # (https://2captcha.com/pricing, 2026-10-07; upper end of each published range).
    default_prices = {
        "turnstile": 1.45,
        "turnstile_challenge": 1.45,
        "recaptcha_v2": 2.99,
        "recaptcha_v2_enterprise": 2.99,
        "recaptcha_v3": 2.99,
        "recaptcha_v3_enterprise": 2.99,
        "geetest_v3": 2.99,
        "geetest_v4": 2.99,
        "awswaf_voucher": 1.45,
        "funcaptcha": 50.0,
        "recaptcha_grid": 1.00,
        "coordinates": 1.00,
        "image_text": 1.00,
    }
    token_first_poll = 5.0
    poll_interval = 2.5
    recognition_first_poll = 2.0
    recognition_poll_interval = 1.5

    def reported_cost(self, response: Dict[str, Any]) -> Optional[float]:
        try:
            return float(response["cost"])
        except (KeyError, TypeError, ValueError):
            return None

    def build_token_task(self, kind: str, sitekey: str, page_url: str, o: Dict[str, Any]) -> Dict[str, Any]:
        task: Dict[str, Any] = {"websiteURL": page_url}
        if kind == "turnstile":
            task.update(type="TurnstileTaskProxyless", websiteKey=sitekey)
            put(task, "action", o.get("action"))
            put(task, "data", o.get("cdata"))
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "turnstile_challenge":
            missing = [k for k in ("action", "cdata", "page_data") if not o.get(k)]
            if missing:
                raise SolverBadRequest(
                    f"turnstile_challenge needs {', '.join(missing)}",
                    provider=self.name,
                    code="MISSING",
                    fallback=False,
                )
            task.update(
                type="TurnstileTaskProxyless",
                websiteKey=sitekey,
                action=o["action"],
                data=o["cdata"],
                pagedata=o["page_data"],
            )
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "recaptcha_v2":
            task.update(type="RecaptchaV2TaskProxyless", websiteKey=sitekey)
            put(task, "recaptchaDataSValue", o.get("data_s"))
            put(task, "userAgent", o.get("user_agent"))
            put(task, "cookies", o.get("cookies"))
            put(task, "apiDomain", o.get("api_domain"))
            if o.get("invisible"):
                task["isInvisible"] = True
        elif kind == "recaptcha_v2_enterprise":
            task.update(type="RecaptchaV2EnterpriseTaskProxyless", websiteKey=sitekey)
            put(task, "enterprisePayload", o.get("enterprise_payload"))
            put(task, "userAgent", o.get("user_agent"))
            put(task, "cookies", o.get("cookies"))
            put(task, "apiDomain", o.get("api_domain"))
            if o.get("invisible"):
                task["isInvisible"] = True
        elif kind in ("recaptcha_v3", "recaptcha_v3_enterprise"):
            task.update(
                type="RecaptchaV3TaskProxyless",
                websiteKey=sitekey,
                minScore=_v3_score(o.get("min_score")),
                isEnterprise=kind.endswith("enterprise"),
            )
            put(task, "pageAction", o.get("action"))
            put(task, "apiDomain", o.get("api_domain"))
        elif kind == "geetest_v3":
            if not o.get("challenge"):
                raise SolverBadRequest(
                    "GeeTest v3 needs a fresh challenge", provider=self.name, code="MISSING", fallback=False
                )
            task.update(type="GeeTestTaskProxyless", gt=sitekey, challenge=o["challenge"])
            put(task, "geetestApiServerSubdomain", o.get("api_server"))
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "geetest_v4":
            init = dict(o.get("init_parameters") or {})
            init.setdefault("captcha_id", sitekey)
            if o.get("risk_type"):
                init.setdefault("risk_type", o["risk_type"])
            task.update(type="GeeTestTaskProxyless", version=4, initParameters=init)
            put(task, "geetestApiServerSubdomain", o.get("api_server"))
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "awswaf_voucher":
            if not (o.get("aws_iv") and o.get("aws_context") and sitekey):
                raise SolverBadRequest(
                    "AWS WAF needs sitekey (key), aws_iv and aws_context",
                    provider=self.name,
                    code="MISSING",
                    fallback=False,
                )
            task.update(type="AmazonTaskProxyless", websiteKey=sitekey, iv=o["aws_iv"], context=o["aws_context"])
            put(task, "challengeScript", o.get("aws_challenge_script"))
            put(task, "captchaScript", o.get("aws_captcha_script"))
        elif kind == "funcaptcha":
            task.update(type="FunCaptchaTaskProxyless", websitePublicKey=sitekey)
            put(task, "funcaptchaApiJSSubdomain", o.get("funcaptcha_subdomain"))
            data = o.get("data")
            if isinstance(data, dict):
                data = json.dumps(data, separators=(",", ":"))
            put(task, "data", data)
            put(task, "userAgent", o.get("user_agent"))
        else:  # pragma: no cover - guarded by token_kinds
            raise SolverUnsupported(kind, provider=self.name)
        return task

    def extract_token(self, kind: str, solution: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        user_agent = solution.get("userAgent")
        if kind in ("turnstile", "turnstile_challenge", "funcaptcha"):
            return solution["token"], user_agent
        if kind.startswith("recaptcha"):
            return solution.get("gRecaptchaResponse") or solution["token"], user_agent
        if kind == "geetest_v3":
            return solution["validate"], user_agent
        if kind == "geetest_v4":
            return solution["captcha_output"], user_agent
        if kind == "awswaf_voucher":
            return solution["captcha_voucher"], user_agent
        raise KeyError(kind)  # pragma: no cover

    def build_recognition_task(self, kind: str, images: List[str], o: Dict[str, Any]) -> Dict[str, Any]:
        task: Dict[str, Any]
        if kind == "recaptcha_grid":
            if len(images) != 1:
                raise SolverBadRequest(
                    "GridTask takes one image (the whole grid)", provider=self.name, code="IMAGES", fallback=False
                )
            question = recaptcha_label_text(o.get("question") or o.get("comment") or "")
            if not question:
                raise SolverBadRequest(
                    "recaptcha_grid needs a question", provider=self.name, code="MISSING", fallback=False
                )
            rows, cols = parse_grid(o.get("grid"))
            task = {
                "type": "GridTask",
                "body": images[0],
                "comment": question,
                "rows": rows,
                "columns": cols,
                "imgType": "recaptcha",
            }
        elif kind == "coordinates":
            task = {"type": "CoordinatesTask", "body": images[0]}
            put(task, "comment", o.get("comment") or o.get("question"))
            if len(images) > 1:
                task["imgInstructions"] = images[1]
            put(task, "minClicks", o.get("min_clicks"))
            put(task, "maxClicks", o.get("max_clicks"))
            if "comment" not in task and "imgInstructions" not in task:
                raise SolverBadRequest(
                    "coordinates needs a comment or an instruction image",
                    provider=self.name,
                    code="MISSING",
                    fallback=False,
                )
        elif kind == "image_text":
            task = {"type": "ImageToTextTask", "body": images[0]}
            put(task, "comment", o.get("comment"))
        else:  # pragma: no cover - guarded by recognition_kinds
            raise SolverUnsupported(kind, provider=self.name)
        return task

    def normalize_recognition(self, kind: str, solution: Dict[str, Any], o: Dict[str, Any]) -> Dict[str, Any]:
        if kind == "recaptcha_grid":
            rows, cols = parse_grid(o.get("grid"))
            objects = sorted({int(i) - 1 for i in solution.get("click") or [] if 1 <= int(i) <= rows * cols})
            return {"objects": objects, "has_object": bool(objects), "size": rows * cols}
        if kind == "coordinates":
            return {"points": [(float(p["x"]), float(p["y"])) for p in solution.get("coordinates") or []]}
        if kind == "image_text":
            return {"text": str(solution["text"])}
        raise KeyError(kind)  # pragma: no cover

    def proxy_task(self, kind: str, task: Dict[str, Any], proxy: ProxySpec) -> Dict[str, Any]:
        task_type = task["type"]
        if not task_type.endswith("Proxyless") or kind in ("recaptcha_v3", "recaptcha_v3_enterprise"):
            raise SolverUnsupported(f"{kind} has no proxied variant", provider=self.name, code="PROXY_UNSUPPORTED")
        task = dict(task)
        task["type"] = task_type[: -len("Proxyless")]
        task.update(proxyType=proxy.type, proxyAddress=proxy.host, proxyPort=proxy.port)
        put(task, "proxyLogin", proxy.login)
        put(task, "proxyPassword", proxy.password)
        return task

    async def report(self, task_id: str, correct: bool, *, timeout: float = 10.0) -> bool:
        """Tell 2Captcha whether a token worked (``reportCorrect`` / ``reportIncorrect``). Returns True on success."""
        method = "reportCorrect" if correct else "reportIncorrect"
        response = await self._call(method, self._payload(taskId=int(task_id)), time.monotonic() + timeout)
        self._raise_for_error(response)
        return response.get("status") == "success"


def _v3_score(value: Any) -> float:
    """2Captcha accepts only 0.3, 0.7 or 0.9: pick the smallest allowed value that meets the request."""
    if value is None:
        return 0.3
    wanted = float(value)
    for score in _V3_SCORES:
        if score >= wanted - 1e-9:
            return score
    return _V3_SCORES[-1]
