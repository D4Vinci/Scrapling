"""In-memory stand-ins for a Patchright page, for the Imperva, AWS WAF and Kasada solver tests.

``FakePage`` plays a scripted timeline (``page.at(seconds, action)``) against the solver: actions run the first time
the solver reads the page after their time has come, the way a vendor script finishes in the background while the
solver polls. ``page.navigate(html, status, headers)`` replaces the document and emits the main-frame response that
a reload would produce.
"""

from __future__ import annotations

from time import monotonic
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

PARAGRAPHS = "\n".join(
    f"<p>Paragraph {i}: plush toys, building sets and board games for every age, with prices, stock levels and "
    f"delivery times for each store near you, plus reviews from other parents.</p>"
    for i in range(30)
)
CONTENT = f"<!doctype html><html><head><title>Toys</title></head><body><h1>Toys</h1>{PARAGRAPHS}</body></html>"


class FakeResponse:
    def __init__(
        self,
        url: str,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        *,
        frame: Any = None,
        resource_type: str = "document",
        method: str = "GET",
        json_body: Any = None,
    ) -> None:
        self.url = url
        self.status = status
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.frame = frame
        self.request = SimpleNamespace(resource_type=resource_type, method=method)
        self._json = json_body

    async def json(self) -> Any:
        if self._json is None:
            raise ValueError("no JSON body")
        return self._json


class FakeElement:
    def __init__(self, box: Optional[Dict[str, float]]) -> None:
        self.box = box

    async def bounding_box(self) -> Optional[Dict[str, float]]:
        return self.box


class FakeFrame:
    def __init__(self, url: str, html: str = "", box: Optional[Dict[str, float]] = None, evaluate: Any = None) -> None:
        self.url = url
        self.html = html
        self.box = box
        self.evaluate_result = evaluate
        self.evaluations: List[Tuple[str, Any]] = []
        self.locator_box: Optional[Dict[str, float]] = None
        self.selectors: List[str] = []

    async def content(self) -> str:
        return self.html

    def locator(self, selector: str) -> SimpleNamespace:
        self.selectors.append(selector)
        return SimpleNamespace(first=FakeElement(self.locator_box))

    async def frame_element(self) -> FakeElement:
        return FakeElement(self.box)

    async def evaluate(self, expression: str, arg: Any = None) -> Any:
        self.evaluations.append((expression, arg))
        result = self.evaluate_result
        return result(expression, arg) if callable(result) else result


class FakeMouse:
    def __init__(self) -> None:
        self.moves = 0
        self.downs: List[Tuple[float, float]] = []
        self.ups = 0
        self.position = (0.0, 0.0)

    async def move(self, x: float, y: float, **_: Any) -> None:
        self.moves += 1
        self.position = (x, y)

    async def down(self, **_: Any) -> None:
        self.downs.append(self.position)

    async def up(self, **_: Any) -> None:
        self.ups += 1

    async def wheel(self, *_: Any) -> None:
        return None


class FakeContext:
    def __init__(self, page: "FakePage") -> None:
        self.page = page
        self.store: Dict[str, str] = {}
        self.added: List[Dict[str, Any]] = []

    async def cookies(self, urls: Any = None) -> List[Dict[str, Any]]:
        self.page.tick()
        host = urlsplit(self.page.url).hostname or ""
        return [{"name": n, "value": v, "domain": host, "path": "/"} for n, v in self.store.items()]

    async def add_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        for cookie in cookies:
            self.added.append(cookie)
            self.store[cookie["name"]] = cookie["value"]


class FakePage:
    """A page whose document, cookies and frames follow a scripted timeline."""

    def __init__(self, url: str, html: str, viewport: Tuple[int, int] = (1280, 800)) -> None:
        self.url = url
        self.html = html
        self.context = FakeContext(self)
        self.main_frame = FakeFrame(url, html)
        self.child_frames: List[FakeFrame] = []
        self.mouse = FakeMouse()
        self.viewport_size = {"width": viewport[0], "height": viewport[1]}
        self.listeners: Dict[str, List[Callable]] = {}
        self.reloads = 0
        self.on_reload: Optional[Callable[["FakePage"], None]] = None
        self.evaluations: List[Tuple[str, Any]] = []
        self.evaluate_result: Any = None
        self._timeline: List[Tuple[float, Callable[["FakePage"], None]]] = []
        self._t0 = monotonic()

    # -- scripting -------------------------------------------------------------------------------------------

    def at(self, seconds: float, action: Callable[["FakePage"], None]) -> "FakePage":
        """Run ``action(page)`` once ``seconds`` have passed since the page was created."""
        self._timeline.append((seconds, action))
        self._timeline.sort(key=lambda item: item[0])
        return self

    def tick(self) -> None:
        now = monotonic() - self._t0
        while self._timeline and self._timeline[0][0] <= now:
            _, action = self._timeline.pop(0)
            action(self)

    def navigate(
        self, html: str, status: int = 200, headers: Optional[Dict[str, str]] = None, frames: Optional[List[FakeFrame]] = None
    ) -> None:
        """Replace the document (and its child frames) and emit its main-frame response (what a reload produces)."""
        self.html = html
        self.main_frame.html = html
        self.child_frames = list(frames or [])
        self.emit(FakeResponse(self.url, status, headers, frame=self.main_frame))

    def emit(self, response: FakeResponse) -> None:
        for listener in list(self.listeners.get("response", ())):
            listener(response)

    # -- the Page API the solvers use -------------------------------------------------------------------------

    @property
    def frames(self) -> List[FakeFrame]:
        return [self.main_frame, *self.child_frames]

    def on(self, event: str, listener: Callable) -> None:
        self.listeners.setdefault(event, []).append(listener)

    def remove_listener(self, event: str, listener: Callable) -> None:
        if listener in self.listeners.get(event, []):
            self.listeners[event].remove(listener)

    async def content(self) -> str:
        self.tick()
        return self.html

    async def wait_for_load_state(self, *_: Any, **__: Any) -> None:
        self.tick()

    async def reload(self, **_: Any) -> None:
        self.reloads += 1
        if self.on_reload is not None:
            self.on_reload(self)

    async def evaluate(self, expression: str, arg: Any = None) -> Any:
        self.evaluations.append((expression, arg))
        result = self.evaluate_result
        return result(expression, arg) if callable(result) else result


class FakeToken(str):
    """What a solver router returns: the value, plus the provider that solved it."""

    def __new__(cls, value: str, provider: str = "fakeprov", **fields: Any) -> "FakeToken":
        obj = super().__new__(cls, value)
        obj.provider = provider
        obj.fields = fields
        return obj


class FakeSolver:
    """A solver router stand-in: ``kinds`` it supports, canned answers, and a log of the calls."""

    name = "router"

    def __init__(self, kinds: Tuple[str, ...], token: str = "TOKEN", answer: Optional[Dict[str, Any]] = None, **fields: Any):
        self.kinds = kinds
        self.token = token
        self.fields = fields
        self.answer = answer or {}
        self.calls: List[Tuple[str, Any, Any, Dict[str, Any]]] = []

    def supports(self, kind: str) -> bool:
        return kind in self.kinds

    async def solve_token(self, kind: str, sitekey: str, page_url: str, **extra: Any) -> str:
        self.calls.append((kind, sitekey, page_url, extra))
        return FakeToken(self.token, **self.fields)

    async def recognize(self, kind: str, images: List[bytes], **extra: Any) -> Dict[str, Any]:
        self.calls.append((kind, len(images), None, extra))
        return dict(self.answer, provider="fakeprov")


async def no_wander(page: Any, deadline: float, duration: float, **_: Any) -> Tuple[float, float]:
    """A stand-in for :func:`scrapling.engines.antibot._pointer.wander` that returns at once."""
    return (0.0, 0.0)
