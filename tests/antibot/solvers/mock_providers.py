"""A local stand-in for the CapMonster Cloud, CapSolver and 2Captcha ``createTask`` APIs.

Each provider is served under its own path prefix (``/capmonster``, ``/capsolver``, ``/2captcha``). The server checks
every task against the request shape in the provider's documentation and answers like the real API:

* CapMonster Cloud: https://docs.capmonster.cloud/docs/api/methods/create-task/ and the task pages under
  https://github.com/CapMonsterCloud/capmonster-captcha-solver-docs/tree/main/docs/captchas
  (turnstile-task, turnstile-challenge-task, no-captcha-task, recaptcha-v2-enterprise-task, recaptcha-v3-task,
  recaptcha-v3-enterprise-task, hcaptcha-task, geetest-task, amazon-task, recaptcha-click); errors:
  docs/api/api-errors.mdx.
* CapSolver: https://docs.capsolver.com/en/guide/api-server/ and the task pages
  https://docs.capsolver.com/en/guide/captcha/cloudflare_turnstile/, .../captcha/ReCaptchaV2/, .../captcha/ReCaptchaV3/,
  .../captcha/Geetest/, .../captcha/awsWaf/, .../recognition/ReCaptchaClassification/, .../recognition/VisionEngine/,
  .../recognition/AwsWafClassification/; errors: https://docs.capsolver.com/en/guide/api-error/.
* 2Captcha API v2: https://2captcha.com/api-docs/create-task, https://2captcha.com/api-docs/get-task-result (adds
  ``cost``), and the task pages cloudflare-turnstile, recaptcha-v2, recaptcha-v2-enterprise, recaptcha-v3, geetest,
  amazon-aws-waf-captcha, arkoselabs-funcaptcha, grid, coordinates, normal-captcha; errors:
  https://2captcha.com/api-docs/error-codes.

Unknown task fields are rejected so that a typo in a client shows up as a test failure.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional, Set, Tuple

PROXY_FIELDS = {"proxyType", "proxyAddress", "proxyPort", "proxyLogin", "proxyPassword"}


def _spec(required: Set[str], optional: Set[str] = frozenset()) -> Tuple[Set[str], Set[str]]:
    return set(required) | {"type"}, set(optional)


CAPMONSTER: Dict[str, Tuple[Set[str], Set[str]]] = {
    "TurnstileTask": _spec(
        {"websiteURL", "websiteKey"},
        {"pageAction", "data", "userAgent", "cloudflareTaskType", "pageData", "apiJsUrl", "htmlPageBase64"}
        | PROXY_FIELDS,
    ),
    "RecaptchaV2Task": _spec(
        {"websiteURL", "websiteKey"}, {"recaptchaDataSValue", "userAgent", "cookies", "isInvisible"} | PROXY_FIELDS
    ),
    "RecaptchaV2EnterpriseTask": _spec(
        {"websiteURL", "websiteKey"},
        {"enterprisePayload", "apiDomain", "pageAction", "userAgent", "cookies"} | PROXY_FIELDS,
    ),
    "RecaptchaV3TaskProxyless": _spec({"websiteURL", "websiteKey"}, {"minScore", "pageAction", "isEnterprise"}),
    "RecaptchaV3EnterpriseTask": _spec({"websiteURL", "websiteKey"}, {"minScore", "pageAction"}),
    "HCaptchaTask": _spec(
        {"websiteURL", "websiteKey"},
        {"isInvisible", "data", "userAgent", "cookies", "fallbackToActualUA"} | PROXY_FIELDS,
    ),
    "GeeTestTask": _spec(
        {"websiteURL", "gt", "version"},
        {"challenge", "geetestApiServerSubdomain", "geetestGetLib", "initParameters", "userAgent"} | PROXY_FIELDS,
    ),
    "AmazonTask": _spec(
        {"websiteURL"},
        {"websiteKey", "captchaScript", "cookieSolution", "userAgent", "challengeScript", "context", "iv"}
        | PROXY_FIELDS,
    ),
    "ComplexImageTask": _spec({"class", "metadata"}, {"imageUrls", "imagesBase64", "userAgent", "websiteURL"}),
    "ImageToTextTask": _spec({"body"}, {"CapMonsterModule", "recognizingThreshold", "case", "numeric", "math"}),
}

CAPSOLVER: Dict[str, Tuple[Set[str], Set[str]]] = {
    "AntiTurnstileTaskProxyLess": _spec({"websiteURL", "websiteKey"}, {"metadata"}),
    "ReCaptchaV2TaskProxyLess": _spec(
        {"websiteURL", "websiteKey"}, {"isInvisible", "pageAction", "recaptchaDataSValue", "apiDomain"}
    ),
    "ReCaptchaV2EnterpriseTaskProxyLess": _spec(
        {"websiteURL", "websiteKey"},
        {"isInvisible", "pageAction", "recaptchaDataSValue", "apiDomain", "enterprisePayload"},
    ),
    "ReCaptchaV2EnterpriseTask": _spec(
        {"websiteURL", "websiteKey", "proxy"},
        {"isInvisible", "pageAction", "recaptchaDataSValue", "apiDomain", "enterprisePayload"},
    ),
    "ReCaptchaV3TaskProxyLess": _spec({"websiteURL", "websiteKey"}, {"pageAction", "apiDomain"}),
    "ReCaptchaV3EnterpriseTaskProxyLess": _spec(
        {"websiteURL", "websiteKey"}, {"pageAction", "apiDomain", "enterprisePayload"}
    ),
    "GeeTestTaskProxyLess": _spec(
        {"websiteURL"}, {"gt", "challenge", "captchaId", "geetestApiServerSubdomain", "riskType"}
    ),
    "AntiAwsWafTaskProxyLess": _spec(
        {"websiteURL"},
        {
            "awsKey",
            "awsIv",
            "awsContext",
            "awsChallengeJS",
            "awsApiJs",
            "awsProblemUrl",
            "awsApiKey",
            "awsExistingToken",
        },
    ),
    "ReCaptchaV2Classification": _spec({"image", "question"}, {"websiteURL", "websiteKey"}),
    "VisionEngine": _spec({"module", "image"}, {"imageBackground", "websiteURL", "question"}),
    "AwsWafClassification": _spec({"images", "question"}, {"websiteURL"}),
    "ImageToTextTask": _spec({"body"}, {"module", "websiteURL", "images", "score", "case"}),
}
CAPSOLVER_SYNC = {"ReCaptchaV2Classification", "VisionEngine", "AwsWafClassification", "ImageToTextTask"}

_2C_TOKEN = {
    "TurnstileTaskProxyless": ({"websiteURL", "websiteKey"}, {"action", "data", "pagedata", "userAgent"}),
    "RecaptchaV2TaskProxyless": (
        {"websiteURL", "websiteKey"},
        {"recaptchaDataSValue", "isInvisible", "userAgent", "cookies", "apiDomain"},
    ),
    "RecaptchaV2EnterpriseTaskProxyless": (
        {"websiteURL", "websiteKey"},
        {"enterprisePayload", "isInvisible", "userAgent", "cookies", "apiDomain"},
    ),
    "RecaptchaV3TaskProxyless": ({"websiteURL", "websiteKey", "minScore"}, {"pageAction", "isEnterprise", "apiDomain"}),
    "GeeTestTaskProxyless": (
        {"websiteURL"},
        {"gt", "challenge", "geetestApiServerSubdomain", "userAgent", "version", "initParameters"},
    ),
    "AmazonTaskProxyless": ({"websiteURL", "websiteKey", "iv", "context"}, {"challengeScript", "captchaScript"}),
    "FunCaptchaTaskProxyless": ({"websiteURL", "websitePublicKey"}, {"funcaptchaApiJSSubdomain", "data", "userAgent"}),
}
TWOCAPTCHA: Dict[str, Tuple[Set[str], Set[str]]] = {}
for _name, (_req, _opt) in _2C_TOKEN.items():
    TWOCAPTCHA[_name] = _spec(_req, _opt)
    if _name != "RecaptchaV3TaskProxyless":  # every other task has a proxied twin without the suffix
        TWOCAPTCHA[_name[: -len("Proxyless")]] = _spec(
            _req | {"proxyType", "proxyAddress", "proxyPort"}, _opt | PROXY_FIELDS
        )
TWOCAPTCHA.update(
    {
        "GridTask": _spec({"body"}, {"comment", "rows", "columns", "imgInstructions", "imgType"}),
        "CoordinatesTask": _spec({"body"}, {"comment", "imgInstructions", "minClicks", "maxClicks"}),
        "ImageToTextTask": _spec({"body"}, {"comment", "phrase", "case", "numeric", "math", "minLength", "maxLength"}),
    }
)

SCHEMAS = {"capmonster": CAPMONSTER, "capsolver": CAPSOLVER, "2captcha": TWOCAPTCHA}
BAD_KEY = {
    "capmonster": "ERROR_KEY_DOES_NOT_EXIST",
    "capsolver": "ERROR_KEY_DENIED_ACCESS",
    "2captcha": "ERROR_KEY_DOES_NOT_EXIST",
}
BAD_TASK = {
    "capmonster": "ERROR_TASK_NOT_SUPPORTED",
    "capsolver": "ERROR_TASK_NOT_SUPPORTED",
    "2captcha": "ERROR_TASK_NOT_SUPPORTED",
}
BAD_FIELDS = {
    "capmonster": "ERROR_INVALID_TASK",
    "capsolver": "ERROR_INVALID_TASK_DATA",
    "2captcha": "ERROR_BAD_PARAMETERS",
}
TASK_ID_IS_INT = {"capmonster": True, "capsolver": False, "2captcha": True}


def solution_for(provider: str, task: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    t = task["type"]
    token = f"TOKEN-{provider}-{task_id}"
    if t.startswith("Turnstile") or t.startswith("AntiTurnstile"):
        return {"token": token, "userAgent": "Mozilla/5.0 (solver UA)"}
    if t.startswith(("Recaptcha", "ReCaptchaV", "HCaptcha")) and "Classification" not in t:
        out = {"gRecaptchaResponse": token}
        if provider == "2captcha":
            out["token"] = token
        return out
    if t.startswith("GeeTest"):
        if task.get("challenge"):
            return {
                "challenge": task["challenge"],
                "validate": f"VALIDATE-{task_id}",
                "seccode": f"VALIDATE-{task_id}|jordan",
            }
        return {
            "captcha_id": task.get("gt")
            or task.get("captchaId")
            or (task.get("initParameters") or {}).get("captcha_id"),
            "lot_number": "lot",
            "pass_token": "pass",
            "gen_time": "1700000000",
            "captcha_output": f"OUTPUT-{task_id}",
        }
    if t == "AmazonTask":
        return {"cookies": {"aws-waf-token": f"AWS-{task_id}"}, "userAgent": "UA"}
    if t == "AntiAwsWafTaskProxyLess":
        return {"cookie": f"AWS-{task_id}"}
    if t.startswith("AmazonTask"):
        return {"captcha_voucher": f"VOUCHER-{task_id}", "existing_token": f"EXISTING-{task_id}"}
    if t.startswith("FunCaptcha"):
        return {"token": f"{token}|r=eu-west-1|pk={task.get('websitePublicKey')}"}
    if t == "ComplexImageTask":
        n = len(task.get("imagesBase64") or task.get("imageUrls") or [])
        n = 9 if n == 1 else n
        return {"answer": [i in (1, 4) for i in range(n)]}
    if t == "ReCaptchaV2Classification":
        return {"type": "multi", "objects": [0, 4, 8], "size": 9}
    if t == "VisionEngine":
        return {"distance": 213} if task["module"].startswith("slider") else {"angle": 45.5}
    if t == "AwsWafClassification":
        return {"objects": [0, 3, 7]}
    if t == "ImageToTextTask":
        return {"text": "w93bx"}
    if t == "GridTask":
        return {"click": [1, 5, 9]}
    if t == "CoordinatesTask":
        return {"coordinates": [{"x": 10, "y": 20}, {"x": 30.5, "y": 40}]}
    raise AssertionError(f"no mock solution for {t}")


class MockProviders:
    """The mock server. Tests tweak ``key``, ``polls_needed``, ``fail``, ``hang``, ``http_error``."""

    def __init__(self) -> None:
        self.key = "test-key-0123456789"
        self.requests: List[Tuple[str, str, Dict[str, Any]]] = []  # (provider, method, body)
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.polls_needed = 1
        self.fail: Dict[str, Tuple[str, str]] = {}  # provider -> (errorCode, errorDescription) from getTaskResult
        self.create_fail: Dict[str, Tuple[str, str]] = {}  # provider -> error from createTask
        self.hang: Set[str] = set()  # providers that never finish
        self.http_error: Dict[str, int] = {}  # provider -> HTTP status with an HTML body
        self.balance = 12.5
        self._lock = threading.Lock()
        self._next = 1000
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self._thread = threading.Thread(target=self._server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)

    @property
    def origin(self) -> str:
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def base(self, provider: str) -> str:
        return f"{self.origin}/{provider}"

    def start(self) -> "MockProviders":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def created(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Tasks sent to createTask (optionally for one provider), oldest first."""
        return [b["task"] for p, m, b in self.requests if m == "createTask" and (provider is None or p == provider)]

    # ---- request handling -------------------------------------------------------------------------------------

    def handle(self, provider: str, method: str, body: Dict[str, Any]) -> Tuple[int, Any]:
        with self._lock:
            self.requests.append((provider, method, body))
        if provider in self.http_error:
            return self.http_error[provider], "<html>Bad gateway</html>"
        if body.get("clientKey") != self.key:
            return 200, _err(
                BAD_KEY[provider], "Account authorization key not found in the system or has incorrect format"
            )
        if method == "getBalance":
            return 200, {"errorId": 0, "balance": self.balance}
        if method == "createTask":
            return 200, self._create(provider, body.get("task") or {})
        if method == "getTaskResult":
            return 200, self._result(provider, body.get("taskId"))
        if method in ("reportCorrect", "reportIncorrect") and provider == "2captcha":
            return 200, {"errorId": 0, "status": "success"}
        return 404, _err("ERROR_NO_SUCH_METHOD", "no such method")

    def _create(self, provider: str, task: Dict[str, Any]) -> Dict[str, Any]:
        if provider in self.create_fail:
            return _err(*self.create_fail[provider])
        schema = SCHEMAS[provider].get(task.get("type", ""))
        if schema is None:
            return _err(BAD_TASK[provider], f"task type {task.get('type')!r} is not supported")
        required, optional = schema
        missing = required - set(task)
        unknown = set(task) - required - optional
        if missing or unknown:
            return _err(BAD_FIELDS[provider], f"missing={sorted(missing)} unknown={sorted(unknown)}")
        with self._lock:
            self._next += 1
            task_id = str(self._next) if TASK_ID_IS_INT[provider] else f"cs-{self._next:08x}-uuid"
            self.tasks[f"{provider}:{task_id}"] = {"task": task, "polls": 0}
        if provider == "capsolver" and task["type"] in CAPSOLVER_SYNC:
            return {
                "errorId": 0,
                "status": "ready",
                "taskId": task_id,
                "solution": solution_for(provider, task, task_id),
            }
        return {"errorId": 0, "taskId": int(task_id) if TASK_ID_IS_INT[provider] else task_id}

    def _result(self, provider: str, task_id: Any) -> Dict[str, Any]:
        entry = self.tasks.get(f"{provider}:{task_id}")
        if entry is None:
            code = {"capsolver": "ERROR_TASKID_INVALID"}.get(provider, "ERROR_NO_SUCH_CAPCHA_ID")
            return _err(code, "task not found")
        entry["polls"] += 1
        if provider in self.hang or entry["polls"] < self.polls_needed:
            return {"errorId": 0, "status": "processing"}
        if provider in self.fail:
            return _err(*self.fail[provider])
        out: Dict[str, Any] = {
            "errorId": 0,
            "status": "ready",
            "solution": solution_for(provider, entry["task"], str(task_id)),
        }
        if provider == "2captcha":
            out.update(cost="0.00145", ip="1.2.3.4", createTime=1692863536, endTime=1692863556, solveCount=1)
        return out

    def _handler(self):
        mock = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length)
                try:
                    body = json.loads(raw)
                except ValueError:
                    body = {}
                parts = self.path.strip("/").split("/")
                if len(parts) != 2 or parts[0] not in SCHEMAS:
                    self.send_response(404)
                    self.end_headers()
                    return
                if self.headers.get("Content-Type") != "application/json":
                    status, payload = 400, _err("ERROR_BAD_REQUEST", "expected JSON")
                else:
                    status, payload = mock.handle(parts[0], parts[1], body)
                data = payload.encode() if isinstance(payload, str) else json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "text/html" if isinstance(payload, str) else "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):  # keep test output clean
                pass

        return Handler


def _err(code: str, description: str) -> Dict[str, Any]:
    return {"errorId": 1, "errorCode": code, "errorDescription": description}
