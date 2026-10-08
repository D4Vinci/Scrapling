"""CapMonster Cloud client (https://capmonster.cloud).

API: ``https://api.capmonster.cloud/createTask`` and ``/getTaskResult`` (``getTaskResult`` allows at most 120 requests
per task). Official documentation lives at https://docs.capmonster.cloud/ and is mirrored in
https://github.com/CapMonsterCloud/capmonster-captcha-solver-docs (``docs/captchas/*.mdx``, ``docs/api/*``), which is
what the request shapes below follow:

* Turnstile: ``turnstile-task.mdx`` (``TurnstileTask``; proxyless unless proxy fields are added).
* Turnstile on a Cloudflare challenge page: ``turnstile-challenge-task.mdx`` (``cloudflareTaskType: "token"``).
* reCAPTCHA v2: ``no-captcha-task.mdx`` (``RecaptchaV2Task``); v2 Enterprise: ``recaptcha-v2-enterprise-task.mdx``
  (``RecaptchaV2EnterpriseTask``); v3: ``recaptcha-v3-task.mdx`` (``RecaptchaV3TaskProxyless``); v3 Enterprise:
  ``recaptcha-v3-enterprise-task.mdx`` (``RecaptchaV3EnterpriseTask``).
* hCaptcha: ``hcaptcha-task.mdx`` (``HCaptchaTask``; listed in the docs, absent from the price page).
* GeeTest v3/v4: ``geetest-task.mdx`` (``GeeTestTask`` with ``version`` 3 or 4).
* AWS WAF: ``amazon-task.mdx`` (``AmazonTask`` with ``cookieSolution: true`` -> ``cookies["aws-waf-token"]``).
* reCAPTCHA image grid recognition: ``recaptcha-click.mdx`` (``ComplexImageTask`` class ``recaptcha``).
* Errors: ``docs/api/api-errors.mdx``.

CapMonster does not report per-task cost, so costs are estimated from the public price list
(https://capmonster.cloud/en/prices, checked 2026-10-07).
"""

from __future__ import annotations

from scrapling.core._types import Any, Dict, List, Optional, Tuple

from ._client import CreateTaskSolver, ProxySpec, parse_grid, put, recaptcha_label_id, recaptcha_label_text
from .base import (
    SolverAuthError,
    SolverBadRequest,
    SolverBalanceError,
    SolverRateLimited,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
)

__all__ = ["CapMonsterSolver"]


class CapMonsterSolver(CreateTaskSolver):
    """CapMonster Cloud. The default provider for Turnstile, reCAPTCHA, GeeTest and AWS WAF tokens."""

    name = "capmonster"
    default_api_base = "https://api.capmonster.cloud"
    token_kinds = frozenset(
        {
            "turnstile",
            "turnstile_challenge",
            "recaptcha_v2",
            "recaptcha_v2_enterprise",
            "recaptcha_v3",
            "recaptcha_v3_enterprise",
            "hcaptcha",
            "geetest_v3",
            "geetest_v4",
            "awswaf",
        }
    )
    recognition_kinds = frozenset({"recaptcha_grid", "image_text"})
    error_map = {
        "ERROR_KEY_DOES_NOT_EXIST": SolverAuthError,
        "ERROR_IP_NOT_ALLOWED": SolverAuthError,
        "ERROR_IP_BANNED": SolverAuthError,
        "ERROR_IP_BLOCKED": SolverAuthError,
        "ERROR_ZERO_BALANCE": SolverBalanceError,
        "ERROR_NO_SUCH_CAPCHA_ID": SolverUnavailable,
        "ERROR_CAPTCHA_UNSOLVABLE": SolverUnsolvable,
        "ERROR_RECAPTCHA_TIMEOUT": SolverUnsolvable,
        "ERROR_TOKEN_EXPIRED": SolverUnsolvable,
        "ERROR_TOO_MUCH_REQUESTS": SolverRateLimited,
        "ERROR_SERVICE_NOT_AVAILABLE": SolverUnavailable,
        "ERROR_TASK_NOT_SUPPORTED": SolverUnsupported,
        "ERROR_NO_SUCH_METHOD": SolverUnsupported,
        "ERROR_TASK_ABSENT": SolverBadRequest,
        "ERROR_INVALID_TASK": SolverBadRequest,
        "ERROR_RECAPTCHA_INVALID_SITEKEY": SolverBadRequest,
        "ERROR_RECAPTCHA_INVALID_DOMAIN": SolverBadRequest,
        "ERROR_DOMAIN_NOT_ALLOWED": SolverBadRequest,
        "ERROR_WRONG_USERAGENT": SolverBadRequest,
        "ERROR_ZERO_CAPTCHA_FILESIZE": SolverBadRequest,
        "ERROR_TOO_BIG_CAPTCHA_FILESIZE": SolverBadRequest,
        "ERROR_PROXY_CONNECT_REFUSED": SolverBadRequest,
        "ERROR_PROXY_CREDENTIALS_INVALID_CHARACTER": SolverBadRequest,
        "ERROR_PROXY_BANNED": SolverBadRequest,
        "ERROR_PROXY_MISSING": SolverBadRequest,
        "ERROR_PROXY_NOT_AUTHORISED": SolverBadRequest,
        "ERROR_PROXY_READ_TIMEOUT": SolverBadRequest,
    }
    cooldown_codes = {"ERROR_TOO_MUCH_REQUESTS": 30.0}
    # USD per 1,000 (https://capmonster.cloud/en/prices, 2026-10-07). reCAPTCHA grid images are $0.04 per 1,000 images.
    # hCaptcha is not on the price page: 3.00 is a deliberately high estimate so spend caps still bound it.
    default_prices = {
        "turnstile": 1.30,
        "turnstile_challenge": 1.30,
        "recaptcha_v2": 0.60,
        "recaptcha_v2_enterprise": 1.00,
        "recaptcha_v3": 0.90,
        "recaptcha_v3_enterprise": 1.50,
        "geetest_v3": 1.20,
        "geetest_v4": 1.20,
        "awswaf": 1.40,
        "hcaptcha": 3.00,
        "recaptcha_grid": 0.04,
        "image_text": 0.30,
    }
    per_image_kinds = frozenset({"recaptcha_grid"})
    token_first_poll = 3.0
    poll_interval = 2.0

    def build_token_task(self, kind: str, sitekey: str, page_url: str, o: Dict[str, Any]) -> Dict[str, Any]:
        task: Dict[str, Any] = {"websiteURL": page_url}
        if kind == "turnstile":
            task.update(type="TurnstileTask", websiteKey=sitekey)
            put(task, "pageAction", o.get("action"))
            put(task, "data", o.get("cdata"))
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "turnstile_challenge":
            missing = [k for k in ("action", "cdata", "page_data", "user_agent") if not o.get(k)]
            if missing:
                raise SolverBadRequest(
                    f"turnstile_challenge needs {', '.join(missing)}",
                    provider=self.name,
                    code="MISSING",
                    fallback=False,
                )
            task.update(
                type="TurnstileTask",
                websiteKey=sitekey,
                cloudflareTaskType="token",
                pageAction=o["action"],
                data=o["cdata"],
                pageData=o["page_data"],
                userAgent=o["user_agent"],
            )
        elif kind == "recaptcha_v2":
            task.update(type="RecaptchaV2Task", websiteKey=sitekey)
            put(task, "recaptchaDataSValue", o.get("data_s"))
            put(task, "userAgent", o.get("user_agent"))
            put(task, "cookies", o.get("cookies"))
            if o.get("invisible"):
                task["isInvisible"] = True
        elif kind == "recaptcha_v2_enterprise":
            task.update(type="RecaptchaV2EnterpriseTask", websiteKey=sitekey)
            put(task, "enterprisePayload", o.get("enterprise_payload"))
            put(task, "apiDomain", o.get("api_domain"))
            put(task, "pageAction", o.get("action"))
            put(task, "userAgent", o.get("user_agent"))
            put(task, "cookies", o.get("cookies"))
        elif kind == "recaptcha_v3":
            task.update(type="RecaptchaV3TaskProxyless", websiteKey=sitekey, isEnterprise=False)
            put(task, "minScore", _score(o.get("min_score")))
            put(task, "pageAction", o.get("action"))
        elif kind == "recaptcha_v3_enterprise":
            task.update(type="RecaptchaV3EnterpriseTask", websiteKey=sitekey)
            put(task, "minScore", _score(o.get("min_score")))
            put(task, "pageAction", o.get("action"))
        elif kind == "hcaptcha":
            task.update(type="HCaptchaTask", websiteKey=sitekey)
            put(task, "data", o.get("data"))
            put(task, "userAgent", o.get("user_agent"))
            put(task, "cookies", o.get("cookies"))
            if o.get("invisible"):
                task["isInvisible"] = True
        elif kind == "geetest_v3":
            if not o.get("challenge"):
                raise SolverBadRequest(
                    "GeeTest v3 needs a fresh challenge", provider=self.name, code="MISSING", fallback=False
                )
            task.update(type="GeeTestTask", gt=sitekey, challenge=o["challenge"], version=3)
            put(task, "geetestApiServerSubdomain", o.get("api_server"))
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "geetest_v4":
            task.update(type="GeeTestTask", gt=sitekey, version=4)
            init = dict(o.get("init_parameters") or {})
            if o.get("risk_type"):
                init.setdefault("riskType", o["risk_type"])
            put(task, "initParameters", init)
            put(task, "geetestApiServerSubdomain", o.get("api_server"))
            put(task, "userAgent", o.get("user_agent"))
        elif kind == "awswaf":
            task.update(type="AmazonTask", cookieSolution=True)
            put(task, "websiteKey", sitekey)
            put(task, "captchaScript", o.get("aws_captcha_script"))
            put(task, "challengeScript", o.get("aws_challenge_script"))
            put(task, "context", o.get("aws_context"))
            put(task, "iv", o.get("aws_iv"))
            put(task, "userAgent", o.get("user_agent"))
            variant_1 = bool(sitekey and o.get("aws_captcha_script"))
            variant_2 = bool(o.get("aws_challenge_script") and o.get("aws_context") and o.get("aws_iv"))
            if not (variant_1 or variant_2):
                raise SolverBadRequest(
                    "AWS WAF needs sitekey + aws_captcha_script, or aws_challenge_script + aws_context + aws_iv",
                    provider=self.name,
                    code="MISSING",
                )
        else:  # pragma: no cover - guarded by token_kinds
            raise SolverUnsupported(kind, provider=self.name)
        return task

    def extract_token(self, kind: str, solution: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        user_agent = solution.get("userAgent")
        if kind in ("turnstile", "turnstile_challenge"):
            return solution["token"], user_agent
        if kind.startswith("recaptcha") or kind == "hcaptcha":
            return solution["gRecaptchaResponse"], user_agent
        if kind == "geetest_v3":
            return solution["validate"], user_agent
        if kind == "geetest_v4":
            return solution["captcha_output"], user_agent
        if kind == "awswaf":
            cookies = solution.get("cookies") or {}
            for name, value in cookies.items():
                if name.lower() == "aws-waf-token":
                    return value, user_agent
            return "", user_agent
        raise KeyError(kind)  # pragma: no cover

    def build_recognition_task(self, kind: str, images: List[str], o: Dict[str, Any]) -> Dict[str, Any]:
        if kind == "recaptcha_grid":
            question = o.get("question")
            if not question:
                raise SolverBadRequest(
                    "recaptcha_grid needs a question", provider=self.name, code="MISSING", fallback=False
                )
            rows, cols = parse_grid(o.get("grid"), (4, 4) if len(images) == 16 else (3, 3))
            label = recaptcha_label_id(question)
            metadata: Dict[str, Any] = {"Grid": f"{rows}x{cols}"}
            if label:
                metadata["TaskDefinition"] = label
            else:
                metadata["Task"] = recaptcha_label_text(question)
            task: Dict[str, Any] = {
                "type": "ComplexImageTask",
                "class": "recaptcha",
                "imagesBase64": images,
                "metadata": metadata,
            }
            put(task, "websiteURL", o.get("page_url"))
            return task
        if kind == "image_text":
            return {"type": "ImageToTextTask", "body": images[0]}
        raise SolverUnsupported(kind, provider=self.name)  # pragma: no cover

    def normalize_recognition(self, kind: str, solution: Dict[str, Any], o: Dict[str, Any]) -> Dict[str, Any]:
        if kind == "recaptcha_grid":
            answer = solution["answer"]
            objects = [i for i, hit in enumerate(answer) if hit]
            return {"objects": objects, "has_object": bool(objects), "size": len(answer)}
        if kind == "image_text":
            return {"text": str(solution["text"])}
        raise KeyError(kind)  # pragma: no cover

    def proxy_task(self, kind: str, task: Dict[str, Any], proxy: ProxySpec) -> Dict[str, Any]:
        if task["type"].endswith("Proxyless"):
            raise SolverUnsupported(f"{kind} has no proxied variant", provider=self.name, code="PROXY_UNSUPPORTED")
        task = dict(task)
        task.update(proxyType=proxy.type, proxyAddress=proxy.host, proxyPort=proxy.port)
        put(task, "proxyLogin", proxy.login)
        put(task, "proxyPassword", proxy.password)
        return task


def _score(value: Any) -> Optional[float]:
    if value is None:
        return None
    return max(0.1, min(0.9, float(value)))
