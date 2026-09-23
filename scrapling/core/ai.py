from uuid import uuid4
from os import environ
from hmac import compare_digest
from asyncio import CancelledError, gather
from contextlib import contextmanager
from datetime import datetime, timezone
from dataclasses import dataclass, field

from anyio import CancelScope
from mcp.server import MCPServer
from mcp.server.mcpserver import Image
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.caching import CacheHint
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import Icon, ImageContent, TextContent, ToolAnnotations
from pydantic import AnyHttpUrl, BaseModel, Field, FiniteFloat, PositiveInt
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from patchright.async_api import TimeoutError as PatchrightTimeoutError

from scrapling import __version__
from scrapling.core.utils import log
from scrapling.core.shell import Convertor, _CONTROL_CHARS_PATTERN
from scrapling.engines.toolbelt.custom import Response as _ScraplingResponse
from scrapling.engines.static import ImpersonateType
from scrapling.fetchers import (
    FetcherSession,
    AsyncDynamicSession,
    AsyncStealthySession,
)
from scrapling.engines._browsers._types import PlaywrightFetchParams, StealthFetchParams
from scrapling.core._types import (
    Optional,
    Literal,
    Union,
    Tuple,
    Mapping,
    Dict,
    List,
    Any,
    Annotated,
    Set,
    Sequence,
    Iterator,
    SetCookieParam,
    extraction_types,
    SelectorWaitStates,
    FollowRedirects,
    SUPPORTED_HTTP_METHODS,
)

SessionType = Literal["dynamic", "stealthy", "static"]
BrowserSessionType = Literal["dynamic", "stealthy"]
SessionExtractionType = Literal[extraction_types, "snapshot"]
ScreenshotType = Literal["png", "jpeg"]
MouseButton = Literal["left", "right", "middle"]
NonNegativeFiniteFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
NonEmptyString = Annotated[str, Field(min_length=1)]
MCP_EXECUTABLE_PATH_ENV = "SCRAPLING_EXECUTABLE_PATH"
MCP_AUTH_TOKEN_ENV = "SCRAPLING_MCP_AUTH_TOKEN"  # nosec B105 - the name of the variable, not a token

_MAX_POOL_PAGES = 50  # Upper bound of `PagesCount` in scrapling/engines/_browsers/_validators.py


def _page_pool_size(urls: Sequence[str]) -> int:
    """Return a page pool size that covers the batch without leaving the validator's bounds."""
    return min(max(len(urls), 1), _MAX_POOL_PAGES)


def _typed_dict_keys(typed_dict: Any) -> frozenset:
    """Collect all the keys a TypedDict holds, including the inherited ones."""
    return frozenset(typed_dict.__required_keys__ | typed_dict.__optional_keys__)


_EXCLUDED_FETCH_KEYS = frozenset({"page_action", "page_setup", "selector_config", "proxy"})
_PLAYWRIGHT_FETCH_KEYS = _typed_dict_keys(PlaywrightFetchParams) - _EXCLUDED_FETCH_KEYS
_STEALTH_FETCH_KEYS = _typed_dict_keys(StealthFetchParams) - _EXCLUDED_FETCH_KEYS


def _session_settings(session: Any) -> Dict[str, Any]:
    """Extract the JSON-safe effective settings of a session, for the AI agent."""
    if isinstance(session, FetcherSession):
        fields = {"stealthy_headers": session._stealth} | {
            f.removeprefix("_default_"): getattr(session, f)
            for f in FetcherSession.__slots__
            if f.startswith("_default")
        }
        return {
            name: value for name, value in fields.items() if isinstance(value, (str, int, float, bool)) or value is None
        }
    config = session._config
    if config.cdp_url:
        return {}
    return {
        f: value
        for f in config.__struct_fields__
        if isinstance(value := getattr(config, f), (str, int, float, bool)) or value is None
    }


_FETCH_TOOL_ANNOTATIONS = ToolAnnotations(read_only_hint=True, open_world_hint=True)
_SESSION_TOOL_ANNOTATIONS = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=True)
_LIST_TOOL_ANNOTATIONS = ToolAnnotations(read_only_hint=True, open_world_hint=False)
_MOUSE_TOOL_ANNOTATIONS = ToolAnnotations(
    read_only_hint=False, destructive_hint=True, idempotent_hint=False, open_world_hint=True
)


class ResponseModel(BaseModel):
    """Request's response information structure."""

    status: int = Field(description="The status code returned by the website.")
    content: list[str] = Field(description="The page content as Markdown, HTML, text, or an AI ARIA snapshot.")
    url: str = Field(description="The URL given by the user that resulted in this response.")


class SessionInfo(BaseModel):
    """Information about an open browser session."""

    session_id: str = Field(description="The unique identifier of the session.")
    session_type: SessionType = Field(description="The type of the session: 'dynamic', 'stealthy', or 'static'.")
    created_at: str = Field(description="ISO timestamp of when the session was created.")
    is_alive: bool = Field(description="Whether the session is still alive and usable.")
    settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="The effective settings this session was created with.",
    )


class SessionCreatedModel(SessionInfo):
    """Response returned when a new session is created."""

    message: str = Field(description="A confirmation message.")


class SessionClosedModel(BaseModel):
    """Response returned when a session is closed."""

    session_id: str = Field(description="The unique identifier of the closed session.")
    message: str = Field(description="A confirmation message.")


@dataclass
class _SessionEntry:
    session: Any  # AsyncDynamicSession | AsyncStealthySession | FetcherSession
    session_type: SessionType
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _translate_response(
    page: _ScraplingResponse,
    extraction_type: extraction_types,
    css_selector: Optional[str],
    main_content_only: bool,
) -> ResponseModel:
    """Extract content from a response and translate it to a ResponseModel."""
    content = [
        _CONTROL_CHARS_PATTERN.sub("", chunk)
        for chunk in Convertor._extract_content(
            page,
            css_selector=css_selector,
            extraction_type=extraction_type,
            main_content_only=main_content_only,
        )
    ]
    return ResponseModel(status=page.status, content=content, url=page.url)


def _normalize_credentials(credentials: Optional[Dict[str, str]]) -> Optional[Tuple[str, str]]:
    """Convert a credentials dictionary to a tuple accepted by fetchers."""
    if not credentials:
        return None

    username = credentials.get("username")
    password = credentials.get("password")

    if username is None or password is None:
        raise ValueError("Credentials dictionary must contain both 'username' and 'password' keys")

    return username, password


class _StaticTokenVerifier(TokenVerifier):
    """Verifies requests against a single shared bearer token."""

    def __init__(self, token: str):
        self._token = token.encode()

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if compare_digest(token.encode(), self._token):
            return AccessToken(token=token, client_id="scrapling-mcp", scopes=[])
        return None


class ScraplingMCPServer:
    def __init__(self, executable_path: Optional[str] = None, auth_token: Optional[str] = None):
        """Create a Scrapling MCP server.

        :param executable_path: Optional global Chromium-compatible browser executable path for browser tools.
            If omitted, the SCRAPLING_EXECUTABLE_PATH environment variable is used when set.
        :param auth_token: Optional shared token that clients must send as `Authorization: Bearer <token>`.
            If omitted, the SCRAPLING_MCP_AUTH_TOKEN environment variable is used when set. It only applies
            to the streamable-http transport.
        """
        self._sessions: Dict[str, _SessionEntry] = {}
        self._executable_path = executable_path or environ.get(MCP_EXECUTABLE_PATH_ENV) or None
        self._auth_token = auth_token or environ.get(MCP_AUTH_TOKEN_ENV) or None

    def _resolve_executable_path(self, executable_path: Optional[str]) -> Optional[str]:
        """Return a per-call executable path or the server-wide default."""
        return executable_path or self._executable_path

    def _get_session(self, session_id: str, expected_type: List[SessionType]) -> _SessionEntry:
        """Look up an active session by ID and validate its type against the allowed types."""
        entry = self._sessions.get(session_id)
        if entry is None:
            raise ValueError(f"Session '{session_id}' not found. Use list_sessions to see active sessions.")
        if not entry.session._is_alive:
            raise ValueError(f"Session '{session_id}' is no longer alive. Open a new session.")
        if entry.session_type not in expected_type:
            raise ValueError(
                f"Session '{session_id}' is a '{entry.session_type}' session, but this tool requires a "
                f"{' or '.join(map(repr, expected_type))} session. Use the matching fetch tool for your session type."
            )
        return entry

    def _new_session_id(self, session_id: Optional[str]) -> str:
        """Generate a session ID when none is given, and reject duplicates."""
        session_id = session_id or uuid4().hex[:12]
        if session_id in self._sessions:
            raise ValueError(
                f"Session '{session_id}' already exists. Use a different ID or close the existing session first."
            )
        return session_id

    def _register_session(self, session_id: str, session: Any, session_type: SessionType) -> SessionCreatedModel:
        """Store a started session and build its creation receipt."""
        entry = _SessionEntry(session=session, session_type=session_type)
        self._sessions[session_id] = entry
        return SessionCreatedModel(
            session_id=session_id,
            session_type=session_type,
            created_at=entry.created_at,
            is_alive=True,
            settings=_session_settings(session),
            message=f"Session '{session_id}' ({session_type}) created successfully.",
        )

    async def browser_open(
        self,
        session_type: BrowserSessionType,
        session_id: Optional[str] = None,
        headless: bool = True,
        real_chrome: bool = False,
        timezone_id: str | None = None,
        locale: str | None = None,
        useragent: Optional[str] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        cdp_url: Optional[str] = None,
        executable_path: Optional[str] = None,
        cookies: Sequence[SetCookieParam] | None = None,
        # Stealthy-only params (ignored for dynamic sessions)
        hide_canvas: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        additional_args: Optional[Dict] = None,
    ) -> SessionCreatedModel:
        """Open a reusable browser session with these settings. Pass per-request options to `browser_fetch`.

        :param session_type: "dynamic" for Playwright; "stealthy" for anti-bot bypass with fingerprint spoofing.
        :param session_id: Custom ID; a random 12-character hex ID if omitted.
        :param headless: Hide the browser window.
        :param real_chrome: Use locally installed Chrome.
        :param timezone_id: Browser timezone; uses the system timezone if omitted.
        :param locale: Browser language, Accept-Language, and formatting locale; system default if omitted.
        :param useragent: User-Agent override; otherwise generated in headless mode, native in headful mode.
        :param proxy: Proxy URL, or dictionary with server and optional username/password.
        :param cdp_url: Connect to an existing Chromium browser over CDP in a new context; launch settings do not apply.
        :param executable_path: Absolute Chromium-compatible executable path; overrides the server default.
        :param cookies: Initial cookies as Playwright cookie dictionaries.
        :param hide_canvas: Stealthy only. Add noise to canvas operations.
        :param block_webrtc: Stealthy only. Disable non-proxied WebRTC UDP to reduce IP leaks.
        :param allow_webgl: Stealthy only. Enable WebGL; disabling it can trigger bot detection.
        :param additional_args: Stealthy only. Browser context options that override Scrapling settings.
        """
        session_id = self._new_session_id(session_id)
        common_kwargs: Dict[str, Any] = dict(
            proxy=proxy,
            locale=locale,
            cookies=cookies,
            cdp_url=cdp_url,
            headless=headless,
            block_ads=True,
            useragent=useragent,
            timezone_id=timezone_id,
            real_chrome=real_chrome,
            executable_path=self._resolve_executable_path(executable_path),
        )

        session: Union[AsyncDynamicSession, AsyncStealthySession]
        if session_type == "stealthy":
            session = AsyncStealthySession(
                **common_kwargs,
                hide_canvas=hide_canvas,
                block_webrtc=block_webrtc,
                allow_webgl=allow_webgl,
                additional_args=additional_args,
            )
        else:
            session = AsyncDynamicSession(**common_kwargs)

        await session.start()
        return self._register_session(session_id, session, session_type)

    async def open_request_session(
        self,
        session_id: Optional[str] = None,
        impersonate: ImpersonateType = "chrome",
        proxy: Optional[str] = None,
    ) -> SessionCreatedModel:
        """Open a reusable HTTP session for `session_make_request`, keeping cookies, connections, and request settings.

        :param session_id: Custom ID; a random 12-character hex ID if omitted.
        :param impersonate: Browser/version to impersonate; "chrome" uses the latest supported Chrome profile.
            Lists pick randomly per attempt; None disables impersonation.
        :param proxy: Proxy URL for all session requests, optionally including credentials.
        """
        session_id = self._new_session_id(session_id)
        session = FetcherSession(impersonate=impersonate, proxy=proxy)
        await session.__aenter__()
        return self._register_session(session_id, session, "static")

    async def close_session(
        self,
        session_id: str,
    ) -> SessionClosedModel:
        """Close a session and free its resources.

        :param session_id: Session ID to close.
        """
        entry = self._sessions.pop(session_id, None)
        if entry is None:
            raise ValueError(f"Session '{session_id}' not found. Use list_sessions to see active sessions.")

        if entry.session_type == "static":
            await entry.session.__aexit__(None, None, None)
        else:
            await entry.session.close()
        return SessionClosedModel(
            session_id=session_id,
            message=f"Session '{session_id}' closed successfully.",
        )

    async def list_sessions(self) -> List[SessionInfo]:
        """List registered sessions, their status, and effective settings."""
        return [
            SessionInfo(
                session_id=sid,
                session_type=entry.session_type,
                created_at=entry.created_at,
                is_alive=entry.session._is_alive,
                settings=_session_settings(entry.session),
            )
            for sid, entry in self._sessions.items()
        ]

    async def browser_snapshot(
        self,
        session_id: str,
        depth: Optional[int] = None,
        boxes: bool = True,
    ) -> str:
        """Return the current page's AI ARIA snapshot with element references as plain text, without navigating.

        :param session_id: ID from `browser_open`; call `browser_fetch` first.
        :param depth: Maximum snapshot depth; unlimited if omitted.
        :param boxes: Include element bounding boxes in viewport CSS pixels.
        """
        return await self._browser_snapshot(session_id, depth=depth, boxes=boxes)

    async def _browser_snapshot(
        self,
        session_id: str,
        css_selector: Optional[str] = None,
        depth: Optional[int] = None,
        boxes: bool = True,
    ) -> str:
        """Reserve the current page and return its AI ARIA snapshot."""
        with self._browser_page(session_id) as (session, page):
            return await session._snapshot(page, depth=depth, boxes=boxes, css_selector=css_selector)

    @contextmanager
    def _browser_page(self, session_id: str) -> Iterator[Tuple[Any, Any]]:
        entry = self._get_session(session_id, expected_type=["dynamic", "stealthy"])
        pool = entry.session.page_pool
        if not pool.pages_count:
            raise ValueError(f"Session '{session_id}' has no page. Use browser_fetch first.")
        page_info = pool.get_ready_page()
        if page_info is None:
            raise RuntimeError(f"Session '{session_id}' has a busy page. Wait for the current request to finish.")

        try:
            if page_info.page.is_closed():
                raise RuntimeError(f"Session '{session_id}' has a closed page. Use browser_fetch to open a new one.")
            yield entry.session, page_info.page
        finally:
            if page_info.page.is_closed():
                pool.remove_page(page_info)
            else:
                page_info.mark_ready()

    async def browser_mouse_move(
        self,
        session_id: str,
        x: FiniteFloat,
        y: FiniteFloat,
        steps: PositiveInt = 1,
    ) -> str:
        """Move the native browser mouse on the current page; return plain text. Coordinates are CSS pixels from the main frame viewport's top-left.

        :param session_id: ID from `browser_open`; call `browser_fetch` first.
        :param x: Horizontal position.
        :param y: Vertical position.
        :param steps: Number of mousemove events.
        """
        with self._browser_page(session_id) as (_, page):
            await page.mouse.move(x, y, steps=steps)
        return f"Mouse moved to ({x}, {y})."

    async def browser_click(
        self,
        session_id: str,
        selector: Optional[NonEmptyString] = None,
        ref: Optional[NonEmptyString] = None,
        x: Optional[FiniteFloat] = None,
        y: Optional[FiniteFloat] = None,
        button: MouseButton = "left",
        click_count: PositiveInt = 1,
        delay: NonNegativeFiniteFloat = 0,
        timeout: NonNegativeFiniteFloat = 30000,
    ) -> str:
        """Click using exactly one selector, snapshot ref, or (x, y) pair; return plain text.
        Selector/ref clicks wait and scroll into view.
        Coordinate clicks do not scroll or wait for navigation. Cancellation/timeouts release the button if the page stays open; completed actions remain.

        :param session_id: ID from `browser_open`; call `browser_fetch` first.
        :param selector: Playwright selector (e.g. CSS or XPath) matching exactly one element.
        :param ref: Element reference from the current snapshot, e.g. "e2".
        :param x: Horizontal CSS pixels from the main frame viewport's top-left.
        :param y: Vertical CSS pixels from the same origin.
        :param button: Mouse button.
        :param click_count: Click count; use 2 for a double-click.
        :param delay: Milliseconds between button press and release.
        :param timeout: Selector/ref timeout in milliseconds; 0 disables it. Ignored for coordinates.
        """
        if sum(value is not None for value in (selector, ref, x)) != 1 or (x is None) != (y is None):
            raise ValueError("Provide exactly one target: 'selector', 'ref', or both 'x' and 'y'.")
        with self._browser_page(session_id) as (_, page):
            try:
                if selector is not None or ref is not None:
                    await page.locator(selector if selector is not None else f"aria-ref={ref}").click(
                        button=button, click_count=click_count, delay=delay, timeout=timeout
                    )
                else:
                    await page.mouse.click(x, y, button=button, click_count=click_count, delay=delay)
            except (CancelledError, PlaywrightTimeoutError, PatchrightTimeoutError):
                with CancelScope(shield=True):
                    if not page.is_closed():
                        await page.mouse.up(button=button)
                raise
        return "Click sent."

    async def browser_screenshot(
        self,
        url: str,
        session_id: str,
        image_type: ScreenshotType = "png",
        full_page: bool = False,
        quality: Optional[int] = None,
        wait: int | float = 0,
        wait_selector: Optional[str] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        network_idle: bool = False,
        timeout: int | float = 30000,
    ) -> List[ImageContent | TextContent]:
        """Navigate to a URL in an open browser session; return the image and URL at capture.

        :param url: URL to navigate to and capture.
        :param session_id: ID from `browser_open`.
        :param image_type: Image format.
        :param full_page: Capture the full scrollable page.
        :param quality: JPEG quality, 0-100; invalid for PNG.
        :param wait: Extra milliseconds after capture.
        :param wait_selector: Wait for the first CSS match after capture; continue if the wait fails.
        :param wait_selector_state: Target state of `wait_selector`.
        :param network_idle: Try to wait for 500 ms without network activity; continue if the wait fails.
        :param timeout: Navigation and page-operation timeout in milliseconds.
        """
        if quality is not None and image_type != "jpeg":
            raise ValueError("'quality' is only valid when 'image_type' is 'jpeg'.")

        entry = self._get_session(session_id, expected_type=["dynamic", "stealthy"])

        screenshot_kwargs: Dict[str, Any] = {"type": image_type, "full_page": full_page}
        if quality is not None:
            screenshot_kwargs["quality"] = quality

        captured: Dict[str, Any] = {}

        async def _capture(page: Any) -> None:
            try:
                captured["bytes"] = await page.screenshot(**screenshot_kwargs)
                captured["url"] = page.url
            except Exception as exc:
                captured["error"] = exc

        await entry.session.fetch(
            url,
            page_action=_capture,
            wait=wait,
            timeout=timeout,
            network_idle=network_idle,
            wait_selector=wait_selector,
            wait_selector_state=wait_selector_state,
        )

        if "error" in captured:
            raise captured["error"]
        if "bytes" not in captured:
            raise RuntimeError(f"Failed to capture screenshot for {url}")

        image = Image(data=captured["bytes"], format=image_type).to_image_content()
        return [image, TextContent(type="text", text=captured["url"])]

    @staticmethod
    async def make_request(
        url: str,
        method: SUPPORTED_HTTP_METHODS = "GET",
        impersonate: ImpersonateType = "chrome",
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        params: Optional[Dict] = None,
        data: Optional[Dict[str, str] | str] = None,
        json: Optional[Dict | List] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int | float] = 30,
        follow_redirects: FollowRedirects = "safe",
        max_redirects: int = 30,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        proxy: Optional[str] = None,
        proxy_auth: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, str]] = None,
        verify: Optional[bool] = True,
        http3: Optional[bool] = False,
        stealthy_headers: Optional[bool] = True,
    ) -> ResponseModel:
        """Make an HTTP request without JavaScript. Suitable for low-to-mid protection.

        :param url: URL to fetch.
        :param method: HTTP method.
        :param impersonate: Browser/version to impersonate; "chrome" uses the latest supported Chrome profile.
            Lists pick randomly per attempt; None disables impersonation.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param params: Query parameters.
        :param data: Form or raw body; ignored for GET.
        :param json: JSON body; ignored for GET.
        :param headers: Request headers.
        :param cookies: Request cookies.
        :param timeout: Timeout in seconds.
        :param follow_redirects: "safe" blocks redirects to private/internal IPs; True allows all; False disables redirects.
        :param max_redirects: Redirect limit; -1 means unlimited.
        :param retries: Maximum attempts, including the first; None or values below 1 send once.
        :param retry_delay: Seconds between retries.
        :param proxy: Proxy URL, optionally including credentials.
        :param proxy_auth: Proxy basic auth: {"username": ..., "password": ...}.
        :param auth: Basic auth: {"username": ..., "password": ...}.
        :param verify: Verify TLS certificates.
        :param http3: Use HTTP/3; may conflict with browser impersonation.
        :param stealthy_headers: Fill missing browser headers and use a Google referer if none was supplied.
        """
        normalized_proxy_auth = _normalize_credentials(proxy_auth)
        normalized_auth = _normalize_credentials(auth)

        request_kwargs: Dict[str, Any] = dict(
            auth=normalized_auth,
            proxy=proxy,
            http3=http3,
            verify=verify,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            retries=retries,
            proxy_auth=normalized_proxy_auth,
            retry_delay=retry_delay,
            impersonate=impersonate,
            max_redirects=max_redirects,
            follow_redirects=follow_redirects,
            stealthy_headers=stealthy_headers,
        )
        if method != "GET":
            request_kwargs.update(data=data, json=json)

        async with FetcherSession() as session:
            page = await getattr(session, method.lower())(url, **request_kwargs)
            return _translate_response(page, extraction_type, css_selector, main_content_only)

    @staticmethod
    async def bulk_get(
        urls: List[str],
        impersonate: ImpersonateType = "chrome",
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        params: Optional[Dict] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int | float] = 30,
        follow_redirects: FollowRedirects = "safe",
        max_redirects: int = 30,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        proxy: Optional[str] = None,
        proxy_auth: Optional[Dict[str, str]] = None,
        auth: Optional[Dict[str, str]] = None,
        verify: Optional[bool] = True,
        http3: Optional[bool] = False,
        stealthy_headers: Optional[bool] = True,
    ) -> List[ResponseModel]:
        """GET multiple URLs concurrently without JavaScript. Suitable for low-to-mid protection.

        :param urls: URLs to fetch.
        :param impersonate: Browser/version to impersonate; "chrome" uses the latest supported Chrome profile.
            Lists pick randomly per attempt; None disables impersonation.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param params: Query parameters.
        :param headers: Request headers.
        :param cookies: Request cookies.
        :param timeout: Timeout in seconds.
        :param follow_redirects: "safe" blocks redirects to private/internal IPs; True allows all; False disables redirects.
        :param max_redirects: Redirect limit; -1 means unlimited.
        :param retries: Maximum attempts, including the first; None or values below 1 send once.
        :param retry_delay: Seconds between retries.
        :param proxy: Proxy URL, optionally including credentials.
        :param proxy_auth: Proxy basic auth: {"username": ..., "password": ...}.
        :param auth: Basic auth: {"username": ..., "password": ...}.
        :param verify: Verify TLS certificates.
        :param http3: Use HTTP/3; may conflict with browser impersonation.
        :param stealthy_headers: Fill missing browser headers and use a Google referer if none was supplied.
        """
        normalized_proxy_auth = _normalize_credentials(proxy_auth)
        normalized_auth = _normalize_credentials(auth)

        async with FetcherSession() as session:
            tasks: List[Any] = [
                session.get(
                    url,
                    auth=normalized_auth,
                    proxy=proxy,
                    http3=http3,
                    verify=verify,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    retries=retries,
                    proxy_auth=normalized_proxy_auth,
                    retry_delay=retry_delay,
                    impersonate=impersonate,
                    max_redirects=max_redirects,
                    follow_redirects=follow_redirects,
                    stealthy_headers=stealthy_headers,
                )
                for url in urls
            ]
            responses = await gather(*tasks)
            return [_translate_response(page, extraction_type, css_selector, main_content_only) for page in responses]

    async def browser_fetch_once(
        self,
        url: str,
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = True,  # noqa: F821
        google_search: bool = True,
        real_chrome: bool = False,
        wait: int | float = 0,
        proxy: Optional[str | Dict[str, str]] = None,
        timezone_id: str | None = None,
        locale: str | None = None,
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        executable_path: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Sequence[SetCookieParam] | None = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        pierce_shadow: bool = False,
    ) -> ResponseModel:
        """Fetch a page with Playwright and JavaScript. Suitable for low-to-mid protection.

        :param url: URL to fetch.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param headless: Hide the browser window.
        :param disable_resources: Block font, image, media, beacon, object, imageset, texttrack, websocket, csp_report, and stylesheet requests.
        :param useragent: User-Agent override; otherwise generated in headless mode, native in headful mode.
        :param cookies: Initial cookies as Playwright cookie dictionaries.
        :param pierce_shadow: Include open Shadow DOM content.
        :param network_idle: Try to wait for 500 ms without network activity; continue if the wait fails.
        :param timeout: Navigation and page-operation timeout in milliseconds.
        :param wait: Extra milliseconds after the page is ready, before returning.
        :param wait_selector: Wait for the first CSS match; continue if the wait fails.
        :param timezone_id: Browser timezone; uses the system timezone if omitted.
        :param locale: Browser language, Accept-Language, and formatting locale; system default if omitted.
        :param wait_selector_state: Target state of `wait_selector`.
        :param real_chrome: Use locally installed Chrome.
        :param cdp_url: Connect to an existing Chromium browser over CDP in a new context; launch settings do not apply.
        :param executable_path: Absolute Chromium-compatible executable path; overrides the server default.
        :param google_search: Set a Google referer, overriding any supplied referer.
        :param extra_headers: Additional request headers.
        :param proxy: Proxy URL, or dictionary with server and optional username/password.
        """
        results = await self.browser_fetch_many_once(
            urls=[url],
            extraction_type=extraction_type,
            css_selector=css_selector,
            main_content_only=main_content_only,
            headless=headless,
            google_search=google_search,
            real_chrome=real_chrome,
            wait=wait,
            proxy=proxy,
            timezone_id=timezone_id,
            locale=locale,
            extra_headers=extra_headers,
            useragent=useragent,
            cdp_url=cdp_url,
            executable_path=executable_path,
            timeout=timeout,
            disable_resources=disable_resources,
            wait_selector=wait_selector,
            cookies=cookies,
            network_idle=network_idle,
            pierce_shadow=pierce_shadow,
            wait_selector_state=wait_selector_state,
        )
        return results[0]

    async def browser_fetch_many_once(
        self,
        urls: List[str],
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = True,  # noqa: F821
        google_search: bool = True,
        real_chrome: bool = False,
        wait: int | float = 0,
        proxy: Optional[str | Dict[str, str]] = None,
        timezone_id: str | None = None,
        locale: str | None = None,
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        executable_path: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Sequence[SetCookieParam] | None = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        pierce_shadow: bool = False,
    ) -> List[ResponseModel]:
        """Fetch pages concurrently with Playwright and JavaScript. Suitable for low-to-mid protection.

        :param urls: URLs to fetch, with at most 50 concurrent pages.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param headless: Hide the browser window.
        :param disable_resources: Block font, image, media, beacon, object, imageset, texttrack, websocket, csp_report, and stylesheet requests.
        :param useragent: User-Agent override; otherwise generated in headless mode, native in headful mode.
        :param cookies: Initial cookies as Playwright cookie dictionaries.
        :param pierce_shadow: Include open Shadow DOM content.
        :param network_idle: Try to wait for 500 ms without network activity; continue if the wait fails.
        :param timeout: Navigation and page-operation timeout in milliseconds.
        :param wait: Extra milliseconds after the page is ready, before returning.
        :param wait_selector: Wait for the first CSS match; continue if the wait fails.
        :param timezone_id: Browser timezone; uses the system timezone if omitted.
        :param locale: Browser language, Accept-Language, and formatting locale; system default if omitted.
        :param wait_selector_state: Target state of `wait_selector`.
        :param real_chrome: Use locally installed Chrome.
        :param cdp_url: Connect to an existing Chromium browser over CDP in a new context; launch settings do not apply.
        :param executable_path: Absolute Chromium-compatible executable path; overrides the server default.
        :param google_search: Set a Google referer, overriding any supplied referer.
        :param extra_headers: Additional request headers.
        :param proxy: Proxy URL, or dictionary with server and optional username/password.
        """
        async with AsyncDynamicSession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            cookies=cookies,
            cdp_url=cdp_url,
            headless=headless,
            block_ads=True,
            max_pages=_page_pool_size(urls),
            useragent=useragent,
            timezone_id=timezone_id,
            real_chrome=real_chrome,
            network_idle=network_idle,
            pierce_shadow=pierce_shadow,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            executable_path=self._resolve_executable_path(executable_path),
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        ) as session:
            tasks = [session.fetch(url) for url in urls]
            responses = await gather(*tasks)

        return [_translate_response(page, extraction_type, css_selector, main_content_only) for page in responses]

    async def browser_stealth_fetch_once(
        self,
        url: str,
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = True,  # noqa: F821
        google_search: bool = True,
        real_chrome: bool = False,
        wait: int | float = 0,
        proxy: Optional[str | Dict[str, str]] = None,
        timezone_id: str | None = None,
        locale: str | None = None,
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        hide_canvas: bool = False,
        cdp_url: Optional[str] = None,
        executable_path: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Sequence[SetCookieParam] | None = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        solve_cloudflare: bool = False,
        additional_args: Optional[Dict] = None,
        pierce_shadow: bool = False,
    ) -> ResponseModel:
        """Fetch a page with a stealth browser for high-protection sites.

        :param url: URL to fetch.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param headless: Hide the browser window.
        :param disable_resources: Block font, image, media, beacon, object, imageset, texttrack, websocket, csp_report, and stylesheet requests.
        :param useragent: User-Agent override; otherwise generated in headless mode, native in headful mode.
        :param cookies: Initial cookies as Playwright cookie dictionaries.
        :param solve_cloudflare: Attempt to solve Cloudflare Turnstile/interstitial challenges before returning.
        :param allow_webgl: Enable WebGL; disabling it can trigger bot detection.
        :param pierce_shadow: Include open Shadow DOM content.
        :param network_idle: Try to wait for 500 ms without network activity; continue if the wait fails.
        :param wait: Extra milliseconds after the page is ready, before returning.
        :param timeout: Navigation and page-operation timeout in milliseconds.
        :param wait_selector: Wait for the first CSS match; continue if the wait fails.
        :param timezone_id: Browser timezone; uses the system timezone if omitted.
        :param locale: Browser language, Accept-Language, and formatting locale; system default if omitted.
        :param wait_selector_state: Target state of `wait_selector`.
        :param real_chrome: Use locally installed Chrome.
        :param hide_canvas: Add noise to canvas operations.
        :param block_webrtc: Disable non-proxied WebRTC UDP to reduce IP leaks.
        :param cdp_url: Connect to an existing Chromium browser over CDP in a new context; launch settings do not apply.
        :param executable_path: Absolute Chromium-compatible executable path; overrides the server default.
        :param google_search: Set a Google referer, overriding any supplied referer.
        :param extra_headers: Additional request headers.
        :param proxy: Proxy URL, or dictionary with server and optional username/password.
        :param additional_args: Browser context options that override Scrapling settings.
        """
        results = await self.browser_stealth_fetch_many_once(
            urls=[url],
            extraction_type=extraction_type,
            css_selector=css_selector,
            main_content_only=main_content_only,
            headless=headless,
            google_search=google_search,
            real_chrome=real_chrome,
            wait=wait,
            proxy=proxy,
            timezone_id=timezone_id,
            locale=locale,
            extra_headers=extra_headers,
            useragent=useragent,
            hide_canvas=hide_canvas,
            cdp_url=cdp_url,
            executable_path=executable_path,
            timeout=timeout,
            disable_resources=disable_resources,
            wait_selector=wait_selector,
            cookies=cookies,
            network_idle=network_idle,
            pierce_shadow=pierce_shadow,
            wait_selector_state=wait_selector_state,
            block_webrtc=block_webrtc,
            allow_webgl=allow_webgl,
            solve_cloudflare=solve_cloudflare,
            additional_args=additional_args,
        )
        return results[0]

    async def browser_stealth_fetch_many_once(
        self,
        urls: List[str],
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = True,  # noqa: F821
        google_search: bool = True,
        real_chrome: bool = False,
        wait: int | float = 0,
        proxy: Optional[str | Dict[str, str]] = None,
        timezone_id: str | None = None,
        locale: str | None = None,
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        hide_canvas: bool = False,
        cdp_url: Optional[str] = None,
        executable_path: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Sequence[SetCookieParam] | None = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        solve_cloudflare: bool = False,
        additional_args: Optional[Dict] = None,
        pierce_shadow: bool = False,
    ) -> List[ResponseModel]:
        """Fetch pages concurrently with a stealth browser for high-protection sites.

        :param urls: URLs to fetch, with at most 50 concurrent pages.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param headless: Hide the browser window.
        :param disable_resources: Block font, image, media, beacon, object, imageset, texttrack, websocket, csp_report, and stylesheet requests.
        :param useragent: User-Agent override; otherwise generated in headless mode, native in headful mode.
        :param cookies: Initial cookies as Playwright cookie dictionaries.
        :param solve_cloudflare: Attempt to solve Cloudflare Turnstile/interstitial challenges before returning.
        :param allow_webgl: Enable WebGL; disabling it can trigger bot detection.
        :param pierce_shadow: Include open Shadow DOM content.
        :param network_idle: Try to wait for 500 ms without network activity; continue if the wait fails.
        :param wait: Extra milliseconds after the page is ready, before returning.
        :param timeout: Navigation and page-operation timeout in milliseconds.
        :param wait_selector: Wait for the first CSS match; continue if the wait fails.
        :param timezone_id: Browser timezone; uses the system timezone if omitted.
        :param locale: Browser language, Accept-Language, and formatting locale; system default if omitted.
        :param wait_selector_state: Target state of `wait_selector`.
        :param real_chrome: Use locally installed Chrome.
        :param hide_canvas: Add noise to canvas operations.
        :param block_webrtc: Disable non-proxied WebRTC UDP to reduce IP leaks.
        :param cdp_url: Connect to an existing Chromium browser over CDP in a new context; launch settings do not apply.
        :param executable_path: Absolute Chromium-compatible executable path; overrides the server default.
        :param google_search: Set a Google referer, overriding any supplied referer.
        :param extra_headers: Additional request headers.
        :param proxy: Proxy URL, or dictionary with server and optional username/password.
        :param additional_args: Browser context options that override Scrapling settings.
        """
        async with AsyncStealthySession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            cdp_url=cdp_url,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            block_ads=True,
            max_pages=_page_pool_size(urls),
            useragent=useragent,
            timezone_id=timezone_id,
            real_chrome=real_chrome,
            hide_canvas=hide_canvas,
            allow_webgl=allow_webgl,
            network_idle=network_idle,
            pierce_shadow=pierce_shadow,
            block_webrtc=block_webrtc,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            executable_path=self._resolve_executable_path(executable_path),
            additional_args=additional_args,
            solve_cloudflare=solve_cloudflare,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        ) as session:
            tasks = [session.fetch(url) for url in urls]
            responses = await gather(*tasks)

        return [_translate_response(page, extraction_type, css_selector, main_content_only) for page in responses]

    async def browser_fetch(
        self,
        url: str,
        session_id: str,
        extraction_type: SessionExtractionType = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        wait: int | float = 0,
        timeout: int | float = 30000,
        google_search: bool = True,
        network_idle: bool = False,
        load_dom: bool = True,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        extra_headers: Optional[Dict[str, str]] = None,
        blocked_domains: Optional[Set[str]] = None,
        solve_cloudflare: bool = False,
        pierce_shadow: bool = False,
    ) -> ResponseModel:
        """Fetch a URL in an open browser session. Options apply only to this request.

        :param url: URL to fetch.
        :param session_id: ID from `browser_open`.
        :param extraction_type: Content output format; snapshots include element bounding boxes.
        :param css_selector: Select after `main_content_only` filtering; snapshots require exactly one match.
        :param main_content_only: Sanitize <body> before selection; False uses the full document. Ignored for snapshots.
        :param wait: Extra milliseconds after the page is ready, before returning.
        :param timeout: Navigation and page-operation timeout in milliseconds.
        :param google_search: Set a Google referer, overriding any supplied referer.
        :param pierce_shadow: Include open Shadow DOM content; ignored for snapshots.
        :param network_idle: Try to wait for 500 ms without network activity; continue if the wait fails.
        :param load_dom: Wait for DOMContentLoaded.
        :param disable_resources: Block font, image, media, beacon, object, imageset, texttrack, websocket, csp_report, and stylesheet requests.
        :param wait_selector: Wait for the first CSS match; continue if the wait fails.
        :param wait_selector_state: Target state of `wait_selector`.
        :param extra_headers: Additional request headers.
        :param blocked_domains: Block requests to these domains and their subdomains.
        :param solve_cloudflare: Attempt to solve Cloudflare Turnstile/interstitial challenges; stealthy sessions only.
        """
        entry = self._get_session(session_id, expected_type=["dynamic", "stealthy"])
        if solve_cloudflare and entry.session_type != "stealthy":
            raise ValueError(
                f"Session '{session_id}' is a '{entry.session_type}' session, so it can't solve Cloudflare "
                f"challenges. Open a 'stealthy' session for that."
            )

        fetch_keys = _STEALTH_FETCH_KEYS if entry.session_type == "stealthy" else _PLAYWRIGHT_FETCH_KEYS
        fetch_params = dict(
            wait=wait,
            timeout=timeout,
            google_search=google_search,
            network_idle=network_idle,
            pierce_shadow=pierce_shadow,
            load_dom=load_dom,
            disable_resources=disable_resources,
            wait_selector=wait_selector,
            wait_selector_state=wait_selector_state,
            extra_headers=extra_headers,
            blocked_domains=blocked_domains,
            solve_cloudflare=solve_cloudflare,
        )
        page = await entry.session.fetch(
            url, **{name: value for name, value in fetch_params.items() if name in fetch_keys}
        )
        if extraction_type == "snapshot":
            return ResponseModel(
                status=page.status, content=[await self._browser_snapshot(session_id, css_selector)], url=page.url
            )
        return _translate_response(page, extraction_type, css_selector, main_content_only)

    async def session_make_request(
        self,
        url: str,
        session_id: str,
        method: SUPPORTED_HTTP_METHODS = "GET",
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        params: Optional[Dict] = None,
        data: Optional[Dict[str, str] | str] = None,
        json: Optional[Dict | List] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int | float] = 30,
        follow_redirects: FollowRedirects = "safe",
        max_redirects: int = 30,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        auth: Optional[Dict[str, str]] = None,
        verify: Optional[bool] = True,
        http3: Optional[bool] = False,
        stealthy_headers: Optional[bool] = True,
    ) -> ResponseModel:
        """Make an HTTP request using the session's cookies, connections, impersonation, and proxy. Options apply to this request.

        :param url: URL to fetch.
        :param session_id: HTTP session ID from `open_request_session`.
        :param method: HTTP method.
        :param extraction_type: Content output format.
        :param css_selector: Select matching elements after `main_content_only` filtering.
        :param main_content_only: Sanitize <body> content before selection; False uses the full document.
        :param params: Query parameters.
        :param data: Form or raw body; ignored for GET.
        :param json: JSON body; ignored for GET.
        :param headers: Request headers.
        :param cookies: Request cookies.
        :param timeout: Timeout in seconds.
        :param follow_redirects: "safe" blocks redirects to private/internal IPs; True allows all; False disables redirects.
        :param max_redirects: Redirect limit; -1 means unlimited.
        :param retries: Maximum attempts, including the first; None or values below 1 send once.
        :param retry_delay: Seconds between retries.
        :param auth: Basic auth: {"username": ..., "password": ...}.
        :param verify: Verify TLS certificates.
        :param http3: Use HTTP/3; may conflict with browser impersonation.
        :param stealthy_headers: Fill missing browser headers and use a Google referer if none was supplied.
        """
        entry = self._get_session(session_id, expected_type=["static"])

        request_kwargs: Dict[str, Any] = dict(
            auth=_normalize_credentials(auth),
            http3=http3,
            verify=verify,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
            max_redirects=max_redirects,
            follow_redirects=follow_redirects,
            stealthy_headers=stealthy_headers,
        )
        if method != "GET":
            request_kwargs.update(data=data, json=json)

        page = await getattr(entry.session._client, method.lower())(url, **request_kwargs)
        return _translate_response(page, extraction_type, css_selector, main_content_only)

    @staticmethod
    def _transport_security(allowed_hosts: Sequence[str]) -> Optional[TransportSecuritySettings]:
        """Build the DNS-rebinding protection settings for the streamable-http transport."""
        if not allowed_hosts:
            return None
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=list(allowed_hosts),
            allowed_origins=[f"{scheme}://{host_}" for host_ in allowed_hosts for scheme in ("http", "https")],
        )

    def _build_server(self, host: str, port: int) -> MCPServer:
        """Build the MCPServer with all tools registered and the optional authentication settings applied."""
        settings: Dict[str, Any] = {
            "title": "Scrapling",
            "version": __version__,
            "website_url": "https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html",
            "icons": [
                Icon(
                    src="https://raw.githubusercontent.com/D4Vinci/Scrapling/main/docs/assets/logo.png",
                    mime_type="image/png",
                )
            ],
            "cache_hints": {"tools/list": CacheHint(ttl_ms=3_600_000, scope="public")},
            "instructions": """Follow these instructions precisely:
1. When the `browser_open` or `open_request_session` tools are used, make sure to close the session with `close_session` after you finish, and use `list_sessions` if you lose track of the open sessions or their effective settings.
2. If the user didn't specify which tool to use, start with the `make_request` tool (a plain HTTP request, defaulting to GET; set `method` for POST/PUT/DELETE), then escalate. The `make_request` tool and `bulk_get` (its GET-only bulk version) are suitable only for low-to-mid protection levels.
    For high-protection levels or websites that require JS loading, use the other tools directly.
3. For HTML, Markdown, and text extraction, if the `css_selector` resolves to more than one element, all the elements will be returned. Snapshot extraction requires a selector matching exactly one element, or no selector for the whole page.
4. For all fetch tools, the `extraction_type` parameter controls the format of the returned content: "markdown" (default) converts the page content to Markdown, "html" returns the raw HTML, and "text" returns the text content of the page.
5. For HTML, Markdown, and text extraction, `main_content_only` is enabled by default and returns only the content inside the page's `<body>` tag. Pass `main_content_only=False` when you need the full page instead.
6. If the task consists of multiple sequential requests to the same website, open a session once, then fetch through it to be more efficient:
    `browser_open` + `browser_fetch` per page for browsers, or `open_request_session` + `session_make_request` per request for plain HTTP.
7. Sessions hold the session-level configuration set when opened, while `browser_fetch`/`session_make_request` carry the per-request options and apply them on each call with the defaults shown in their schemas.
    The one-shot tools (`make_request`, `bulk_get`, `browser_fetch_once`, `browser_fetch_many_once`, `browser_stealth_fetch_once`, `browser_stealth_fetch_many_once`) never touch sessions.
8. If you are making multiple parallel one-shot requests, use the bulk version of the tool to be more efficient.
9. If you are crawling/browsing a website, be more efficient by using the `css_selector` parameter to only access the parts you are interested in and save money/time. Example: use the `a` selector to extract the urls right away.
10. The user can pass a CDP URL to connect to a remote browser session through the `browser_open` tool, then use it with the session tools.
11. Set `extraction_type="snapshot"` on `browser_fetch` to get an AI ARIA snapshot with element references and bounding boxes in its content field. Use `css_selector` to snapshot one element, or omit it for the whole page. `main_content_only` and `pierce_shadow` do not filter snapshots. Use `browser_snapshot` to read the current page without navigating; it returns plain text with boxes by default. Set `depth` to limit the tree or `boxes=False` to omit boxes.
12. Use `browser_mouse_move` to move the mouse on the current page. Use `browser_click` with exactly one target: `selector`, `ref` from the current snapshot, or both `x` and `y` viewport CSS coordinates. Selector/ref clicks use Playwright's normal waiting and scrolling; coordinate clicks do not scroll or wait for navigation. Get coordinates from `browser_snapshot` and inspect the page afterward with `browser_snapshot`. Clicks can change website data. Do not repeat a click without checking the page state.
""",
        }
        if self._auth_token:
            base_url = AnyHttpUrl(f"http://{host}:{port}")
            settings["token_verifier"] = _StaticTokenVerifier(self._auth_token)
            settings["auth"] = AuthSettings(issuer_url=base_url, resource_server_url=base_url)

        server = MCPServer(name="Scrapling", **settings)
        # Session management tools
        server.add_tool(
            self.browser_open, title="Open browser", structured_output=True, annotations=_SESSION_TOOL_ANNOTATIONS
        )
        server.add_tool(
            self.open_request_session,
            title="Open HTTP session",
            structured_output=True,
            annotations=_SESSION_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.close_session, title="Close session", structured_output=True, annotations=_SESSION_TOOL_ANNOTATIONS
        )
        server.add_tool(
            self.list_sessions, title="List sessions", structured_output=True, annotations=_LIST_TOOL_ANNOTATIONS
        )
        # HTTP tools
        server.add_tool(
            self.make_request,
            title="Send HTTP request",
            description=self.make_request.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.bulk_get,
            title="Get pages via HTTP requests",
            description=self.bulk_get.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Dynamic browser tools
        server.add_tool(
            self.browser_fetch_once,
            title="Fetch page in browser",
            description=self.browser_fetch_once.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.browser_fetch_many_once,
            title="Fetch pages in browser",
            description=self.browser_fetch_many_once.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Stealthy browser tools
        server.add_tool(
            self.browser_stealth_fetch_once,
            title="Fetch page with stealthy browser",
            description=self.browser_stealth_fetch_once.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.browser_stealth_fetch_many_once,
            title="Fetch pages with stealthy browser",
            description=self.browser_stealth_fetch_many_once.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Session-scoped fetch tools
        server.add_tool(
            self.browser_fetch,
            title="Fetch in browser session",
            description=self.browser_fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.session_make_request,
            title="Send HTTP request in HTTP session",
            description=self.session_make_request.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.browser_snapshot,
            title="Browser page snapshot",
            description=self.browser_snapshot.__doc__,
            structured_output=False,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.browser_mouse_move,
            title="Move mouse",
            description=self.browser_mouse_move.__doc__,
            structured_output=False,
            annotations=_MOUSE_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.browser_click,
            title="Click",
            description=self.browser_click.__doc__,
            structured_output=False,
            annotations=_MOUSE_TOOL_ANNOTATIONS,
        )
        # Screenshot tool (returns image + url content blocks, not structured JSON)
        server.add_tool(
            self.browser_screenshot,
            title="Take browser session screenshot",
            description=self.browser_screenshot.__doc__,
            structured_output=False,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        return server

    def serve(
        self,
        http: bool,
        host: str,
        port: int,
        allowed_hosts: Sequence[str] = (),
        allow_unauthenticated: bool = False,
    ):
        """Serve the MCP server.

        :param http: Serve over the streamable-http transport instead of stdio.
        :param host: The host to bind to when `http` is enabled.
        :param port: The port to bind to when `http` is enabled.
        :param allowed_hosts: Host names to accept, which turns on DNS-rebinding protection.
        :param allow_unauthenticated: Start the streamable-http transport without a token. The transport
            requires authentication by default, so this is the explicit opt-out.
        """
        if not http:
            if self._auth_token:
                log.warning(
                    "The authentication token only applies to the streamable-http transport, so it's ignored with stdio."
                )
        elif self._auth_token:
            if allow_unauthenticated:
                log.warning(
                    "An authentication token was given, so it takes precedence and the server still requires it."
                )
        elif not allow_unauthenticated:
            raise ValueError(
                f"Refusing to serve the MCP server over HTTP without authentication because anyone who can reach "
                f"{host}:{port} would be able to use every tool, including fetching arbitrary URLs from this machine. "
                f"Pass `--auth-token` (or set the {MCP_AUTH_TOKEN_ENV} environment variable) to require a bearer "
                f"token, or `--no-auth` to serve it unauthenticated anyway."
            )
        else:
            log.warning(
                f"The MCP server is running over HTTP without authentication, so anyone who can reach "
                f"{host}:{port} can use every tool, including fetching arbitrary URLs from this machine."
            )

        server = self._build_server(host, port)
        if http:
            server.run(
                transport="streamable-http",
                host=host,
                port=port,
                transport_security=self._transport_security(allowed_hosts),
            )
        else:
            server.run()
