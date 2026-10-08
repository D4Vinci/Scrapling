"""CapSolver client (https://www.capsolver.com).

API: ``https://api.capsolver.com/createTask`` and ``/getTaskResult`` (at most 120 result requests per task; results
are kept for 5 minutes), documented at https://docs.capsolver.com/en/guide/api-server/ and
https://docs.capsolver.com/en/guide/api-gettaskresult/. Request shapes follow:

* Turnstile: https://docs.capsolver.com/en/guide/captcha/cloudflare_turnstile/ (``AntiTurnstileTaskProxyLess``,
  ``metadata.action`` / ``metadata.cdata``).
* reCAPTCHA v2: https://docs.capsolver.com/en/guide/captcha/ReCaptchaV2/ (``ReCaptchaV2TaskProxyLess``,
  ``ReCaptchaV2EnterpriseTaskProxyLess``); v3: https://docs.capsolver.com/en/guide/captcha/ReCaptchaV3/
  (``ReCaptchaV3TaskProxyLess``, ``ReCaptchaV3EnterpriseTaskProxyLess``).
* GeeTest: https://docs.capsolver.com/en/guide/captcha/Geetest/ (``GeeTestTaskProxyLess``; v3 ``gt`` + ``challenge``,
  v4 ``captchaId``).
* AWS WAF: https://docs.capsolver.com/en/guide/captcha/awsWaf/ (``AntiAwsWafTaskProxyLess`` -> ``solution.cookie``).
* Recognition (synchronous; the result comes back from ``createTask``):
  https://docs.capsolver.com/en/guide/recognition/ReCaptchaClassification/ (``ReCaptchaV2Classification``),
  https://docs.capsolver.com/en/guide/recognition/VisionEngine/ (``VisionEngine`` modules ``slider_1``, ``rotate_1``),
  https://docs.capsolver.com/en/guide/recognition/AwsWafClassification/ (``AwsWafClassification``) and
  ``ImageToTextTask``.
* Errors: https://docs.capsolver.com/en/guide/api-error/.

CapSolver has deprecated hCaptcha and FunCaptcha, so neither is offered here. ``AntiCloudflareTask`` and
``DatadomeSliderTask`` need the provider to egress through the caller's IP and are deliberately not implemented.
CapSolver does not report per-task cost; costs are estimated from https://www.capsolver.com/ (2026-10-07).
"""

from __future__ import annotations

from scrapling.core._types import Any, Dict, List, Optional, Tuple, Type

from ._client import CreateTaskSolver, ProxySpec, put, recaptcha_label_id
from .base import (
    SolverAuthError,
    SolverBadRequest,
    SolverBalanceError,
    SolverError,
    SolverRateLimited,
    SolverUnavailable,
    SolverUnsolvable,
    SolverUnsupported,
)

__all__ = ["CapSolverSolver"]

_SLIDER_KINDS = frozenset({"geetest_slide", "datadome_slider", "slider"})


class CapSolverSolver(CreateTaskSolver):
    """CapSolver. The default provider for recognition tasks (image grids, sliders, AWS WAF images)."""

    name = "capsolver"
    default_api_base = "https://api.capsolver.com"
    token_kinds = frozenset(
        {
            "turnstile",
            "recaptcha_v2",
            "recaptcha_v2_enterprise",
            "recaptcha_v3",
            "recaptcha_v3_enterprise",
            "geetest_v3",
            "geetest_v4",
            "awswaf",
        }
    )
    recognition_kinds = frozenset(
        {"recaptcha_grid", "geetest_slide", "datadome_slider", "slider", "rotate", "awswaf_images", "image_text"}
    )
    error_map = {
        "ERROR_KEY_DENIED_ACCESS": SolverAuthError,
        # Not in the error list, but returned live (2026-10-08) by getBalance for a malformed key.
        "ERROR_KEY_DOES_NOT_EXIST": SolverAuthError,
        "ERROR_IP_BANNED": SolverAuthError,
        "ERROR_ZERO_BALANCE": SolverBalanceError,
        "ERROR_SETTLEMENT_FAILED": SolverBalanceError,
        "ERROR_TASK_NOT_SUPPORTED": SolverUnsupported,
        "ERROR_INVALID_TASK_DATA": SolverBadRequest,
        "ERROR_BAD_REQUEST": SolverBadRequest,
        "ERROR_UNKNOWN_QUESTION": SolverBadRequest,
        "ERROR_INVALID_IMAGE": SolverBadRequest,
        "ERROR_PARSE_IMAGE_FAIL": SolverBadRequest,
        "ERROR_PROXY_BANNED": SolverBadRequest,
        "ERROR_CAPTCHA_UNSOLVABLE": SolverUnsolvable,
        "ERROR_TASK_TIMEOUT": SolverUnsolvable,
        "ERROR_RATE_LIMIT": SolverRateLimited,
        "ERROR_KEY_TEMP_BLOCKED": SolverRateLimited,
        "ERROR_SERVICE_UNAVALIABLE": SolverUnavailable,  # sic, as spelled by CapSolver
        "ERROR_SERVICE_UNAVAILABLE": SolverUnavailable,
        "ERROR_TASKID_INVALID": SolverUnavailable,
    }
    # ERROR_KEY_TEMP_BLOCKED lifts after 5 minutes; ERROR_IP_BANNED after 10 minutes.
    cooldown_codes = {"ERROR_KEY_TEMP_BLOCKED": 300.0, "ERROR_IP_BANNED": 600.0, "ERROR_RATE_LIMIT": 30.0}
    # USD per 1,000 (https://www.capsolver.com/, 2026-10-07). Recognition kinds use the published image price.
    default_prices = {
        "turnstile": 1.20,
        "recaptcha_v2": 0.80,
        "recaptcha_v2_enterprise": 1.00,
        "recaptcha_v3": 1.00,
        "recaptcha_v3_enterprise": 3.00,
        "geetest_v3": 1.20,
        "geetest_v4": 1.20,
        "awswaf": 2.00,
        "recaptcha_grid": 0.40,
        "geetest_slide": 0.40,
        "datadome_slider": 0.40,
        "slider": 0.40,
        "rotate": 0.40,
        "awswaf_images": 0.40,
        "image_text": 0.40,
    }
    token_first_poll = 2.0
    poll_interval = 2.0

    def error_class(self, code: str, description: str) -> Type[SolverError]:
        # A malformed key comes back from createTask as ERROR_INVALID_TASK_DATA "clientKey is invalid" (seen live
        # 2026-10-08); treat it as an auth failure so the router cools CapSolver down instead of retrying it.
        if "clientkey" in description.lower():
            return SolverAuthError
        return super().error_class(code, description)

    def build_token_task(self, kind: str, sitekey: str, page_url: str, o: Dict[str, Any]) -> Dict[str, Any]:
        task: Dict[str, Any] = {"websiteURL": page_url}
        if kind == "turnstile":
            task.update(type="AntiTurnstileTaskProxyLess", websiteKey=sitekey)
            metadata: Dict[str, Any] = {}
            put(metadata, "action", o.get("action"))
            put(metadata, "cdata", o.get("cdata"))
            put(task, "metadata", metadata)
        elif kind in ("recaptcha_v2", "recaptcha_v2_enterprise"):
            enterprise = kind.endswith("enterprise")
            task.update(
                type="ReCaptchaV2EnterpriseTaskProxyLess" if enterprise else "ReCaptchaV2TaskProxyLess",
                websiteKey=sitekey,
            )
            put(task, "pageAction", o.get("action"))
            put(task, "apiDomain", o.get("api_domain"))
            put(task, "recaptchaDataSValue", o.get("data_s"))
            if enterprise:
                put(task, "enterprisePayload", o.get("enterprise_payload"))
            if o.get("invisible"):
                task["isInvisible"] = True
        elif kind in ("recaptcha_v3", "recaptcha_v3_enterprise"):
            enterprise = kind.endswith("enterprise")
            task.update(
                type="ReCaptchaV3EnterpriseTaskProxyLess" if enterprise else "ReCaptchaV3TaskProxyLess",
                websiteKey=sitekey,
            )
            put(task, "pageAction", o.get("action"))
            put(task, "apiDomain", o.get("api_domain"))
            if enterprise:
                put(task, "enterprisePayload", o.get("enterprise_payload"))
        elif kind == "geetest_v3":
            if not o.get("challenge"):
                raise SolverBadRequest(
                    "GeeTest v3 needs a fresh challenge", provider=self.name, code="MISSING", fallback=False
                )
            task.update(type="GeeTestTaskProxyLess", gt=sitekey, challenge=o["challenge"])
            put(task, "geetestApiServerSubdomain", o.get("api_server"))
        elif kind == "geetest_v4":
            task.update(type="GeeTestTaskProxyLess", captchaId=sitekey)
            put(task, "geetestApiServerSubdomain", o.get("api_server"))
            put(task, "riskType", o.get("risk_type") or (o.get("init_parameters") or {}).get("riskType"))
        elif kind == "awswaf":
            task.update(type="AntiAwsWafTaskProxyLess")
            put(task, "awsKey", sitekey)
            put(task, "awsIv", o.get("aws_iv"))
            put(task, "awsContext", o.get("aws_context"))
            put(task, "awsChallengeJS", o.get("aws_challenge_script"))
            put(task, "awsApiJs", o.get("aws_captcha_script"))
            put(task, "awsProblemUrl", o.get("aws_problem_url"))
            put(task, "awsApiKey", o.get("aws_api_key"))
            put(task, "awsExistingToken", o.get("aws_existing_token"))
        else:  # pragma: no cover - guarded by token_kinds
            raise SolverUnsupported(kind, provider=self.name)
        return task

    def extract_token(self, kind: str, solution: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        user_agent = solution.get("userAgent")
        if kind == "turnstile":
            return solution["token"], user_agent
        if kind.startswith("recaptcha"):
            return solution["gRecaptchaResponse"], user_agent
        if kind == "geetest_v3":
            return solution["validate"], user_agent
        if kind == "geetest_v4":
            return solution["captcha_output"], user_agent
        if kind == "awswaf":
            return solution["cookie"], user_agent
        raise KeyError(kind)  # pragma: no cover

    def build_recognition_task(self, kind: str, images: List[str], o: Dict[str, Any]) -> Dict[str, Any]:
        task: Dict[str, Any]
        if kind == "recaptcha_grid":
            question = recaptcha_label_id(o.get("question") or "")
            if not question:
                raise SolverBadRequest(
                    "recaptcha_grid needs a question CapSolver knows (a /m/ label id or its English text)",
                    provider=self.name,
                    code="UNKNOWN_QUESTION",
                )
            if len(images) != 1:
                raise SolverBadRequest(
                    "ReCaptchaV2Classification takes one image (the whole grid or one tile)",
                    provider=self.name,
                    code="IMAGES",
                    fallback=False,
                )
            task = {"type": "ReCaptchaV2Classification", "image": images[0], "question": question}
            put(task, "websiteURL", o.get("page_url"))
            put(task, "websiteKey", o.get("sitekey"))
        elif kind in _SLIDER_KINDS:
            if len(images) != 2:
                raise SolverBadRequest(
                    "slider recognition takes [piece, background]", provider=self.name, code="IMAGES", fallback=False
                )
            task = {
                "type": "VisionEngine",
                "module": o.get("module") or "slider_1",
                "image": images[0],
                "imageBackground": images[1],
            }
            put(task, "websiteURL", o.get("page_url"))
        elif kind == "rotate":
            task = {"type": "VisionEngine", "module": o.get("module") or "rotate_1", "image": images[0]}
            if len(images) > 1:
                task["imageBackground"] = images[1]
            put(task, "websiteURL", o.get("page_url"))
        elif kind == "awswaf_images":
            if not o.get("question"):
                raise SolverBadRequest(
                    "awswaf_images needs a question (e.g. aws:grid:bag)",
                    provider=self.name,
                    code="MISSING",
                    fallback=False,
                )
            task = {"type": "AwsWafClassification", "images": images, "question": o["question"]}
            put(task, "websiteURL", o.get("page_url"))
        elif kind == "image_text":
            task = {"type": "ImageToTextTask", "body": images[0]}
            put(task, "module", o.get("module"))
            put(task, "websiteURL", o.get("page_url"))
        else:  # pragma: no cover - guarded by recognition_kinds
            raise SolverUnsupported(kind, provider=self.name)
        return task

    def normalize_recognition(self, kind: str, solution: Dict[str, Any], o: Dict[str, Any]) -> Dict[str, Any]:
        if kind == "recaptcha_grid":
            if solution.get("type") == "single" or "hasObject" in solution:
                has = bool(solution.get("hasObject"))
                return {"objects": [0] if has else [], "has_object": has, "size": int(solution.get("size") or 1)}
            objects = [int(i) for i in solution.get("objects") or []]
            return {"objects": objects, "has_object": bool(objects), "size": int(solution.get("size") or 0)}
        if kind in _SLIDER_KINDS:
            return {"distance": float(solution["distance"])}
        if kind == "rotate":
            return {"angle": float(solution["angle"])}
        if kind == "awswaf_images":
            return {
                "objects": [int(i) for i in solution.get("objects") or []],
                "box": solution.get("box"),
                "distance": solution.get("distance"),
            }
        if kind == "image_text":
            return {"text": str(solution["text"])}
        raise KeyError(kind)  # pragma: no cover

    def proxy_task(self, kind: str, task: Dict[str, Any], proxy: ProxySpec) -> Dict[str, Any]:
        task_type = task["type"]
        if kind == "turnstile" or not task_type.endswith("ProxyLess"):
            raise SolverUnsupported(f"{kind} has no proxied variant", provider=self.name, code="PROXY_UNSUPPORTED")
        task = dict(task)
        task["type"] = task_type[: -len("ProxyLess")]
        auth = f":{proxy.login}:{proxy.password or ''}" if proxy.login else ""
        # "type:host:port[:login:password]" (https://docs.capsolver.com/en/guide/api-how-to-use-proxy/)
        task["proxy"] = f"{proxy.type}:{proxy.host}:{proxy.port}{auth}"
        return task
