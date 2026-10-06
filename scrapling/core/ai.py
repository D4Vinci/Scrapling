from uuid import uuid4
from os import environ
from json import dumps
from time import monotonic
from hmac import compare_digest
from functools import wraps
from contextlib import contextmanager
from datetime import datetime, timezone
from dataclasses import dataclass, field

from anyio import CancelScope
from curl_cffi.curl import CurlError
from curl_cffi.requests import BrowserTypeLiteral
from mcp.server import MCPServer
from mcp.server.mcpserver import Image
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.caching import CacheHint
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import Icon, ImageContent, TextContent, ToolAnnotations
from msgspec import ValidationError as MsgspecValidationError
from pydantic import AnyHttpUrl, BaseModel, Field
from patchright.async_api import Error as PatchrightError

from scrapling import __version__
from scrapling.core.utils import log
from scrapling.core._browser_actions import (
    BrowserAction,
    NonEmptyString,
    NonNegativeFiniteFloat,
    _run_actions,
    _validate_actions,
)
from scrapling.core._network_formatting import NetworkPart, NetworkRequestInfo, NetworkRequestModel, _request_details
from scrapling.core.shell import Convertor, _CONTROL_CHARS_PATTERN
from scrapling.engines.toolbelt.custom import Response as _ScraplingResponse
from scrapling.fetchers import FetcherSession, AsyncStealthySession
from scrapling.engines._browsers._types import StealthFetchParams
from scrapling.core._types import (
    Optional,
    Literal,
    Tuple,
    Mapping,
    Dict,
    List,
    Any,
    Awaitable,
    Callable,
    Annotated,
    TypeAliasType,
    Set,
    Sequence,
    Iterator,
    SetCookieParam,
    extraction_types,
    SelectorWaitStates,
    FollowRedirects,
    SUPPORTED_HTTP_METHODS,
)

_BrowserProfile = TypeAliasType("_BrowserProfile", BrowserTypeLiteral)
_MCPImpersonateType = _BrowserProfile | List[_BrowserProfile] | None

SessionType = Literal["stealthy", "static"]
SessionExtractionType = Literal[extraction_types, "snapshot"]
ScreenshotType = Literal["png", "jpeg"]
MCP_EXECUTABLE_PATH_ENV = "SCRAPLING_EXECUTABLE_PATH"
MCP_AUTH_TOKEN_ENV = "SCRAPLING_MCP_AUTH_TOKEN"  # nosec B105 - the name of the variable, not a token


def _typed_dict_keys(typed_dict: Any) -> frozenset:
    """Collect all the keys a TypedDict holds, including the inherited ones."""
    return frozenset(typed_dict.__required_keys__ | typed_dict.__optional_keys__)


_EXCLUDED_FETCH_KEYS = frozenset({"page_action", "page_setup", "selector_config", "proxy"})
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
_INPUT_TOOL_ANNOTATIONS = ToolAnnotations(
    read_only_hint=False, destructive_hint=True, idempotent_hint=False, open_world_hint=True
)


class ResponseModel(BaseModel):
    """Request's response information structure."""

    status: int = Field(description="The status code returned by the website.")
    content: list[str] = Field(description="The page content as Markdown, HTML, text, or an AI ARIA snapshot.")
    url: str = Field(description="The URL given by the user that resulted in this response.")


class NetworkRequestsModel(BaseModel):
    """Recorded request summaries and pagination details."""

    requests: List[NetworkRequestInfo]
    next_cursor: int
    has_more: bool
    dropped_count: int


class SessionInfo(BaseModel):
    """Information about an open browser session."""

    session_id: str = Field(description="The unique identifier of the session.")
    session_type: SessionType = Field(description="The type of the session: 'stealthy' or 'static'.")
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
    session: Any
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


def _mcp_tool(tool: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @wraps(tool)
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return await tool(*args, **kwargs)
        except (ValueError, RuntimeError, TypeError, PatchrightError, CurlError) as error:
            if isinstance(error, TypeError) and not isinstance(error.__cause__, MsgspecValidationError):
                raise
            raise ToolError(str(error)) from error

    return wrapped


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
        hide_canvas: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        additional_args: Optional[Dict] = None,
    ) -> SessionCreatedModel:
        """Open a reusable stealthy browser session. Pass per-request options to `browser_fetch`.

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
        :param hide_canvas: Add noise to canvas operations.
        :param block_webrtc: Disable non-proxied WebRTC UDP to reduce IP leaks.
        :param allow_webgl: Enable WebGL; disabling it can trigger bot detection.
        :param additional_args: Browser context options that override Scrapling settings.
        """
        session_id = self._new_session_id(session_id)
        session = AsyncStealthySession(
            proxy=proxy,
            locale=locale,
            cookies=cookies,
            cdp_url=cdp_url,
            headless=headless,
            block_ads=True,
            record_requests=True,
            useragent=useragent,
            timezone_id=timezone_id,
            real_chrome=real_chrome,
            executable_path=self._resolve_executable_path(executable_path),
            hide_canvas=hide_canvas,
            block_webrtc=block_webrtc,
            allow_webgl=allow_webgl,
            additional_args=additional_args,
        )
        await session.start()
        return self._register_session(session_id, session, "stealthy")

    async def open_request_session(
        self,
        session_id: Optional[str] = None,
        impersonate: _MCPImpersonateType = "chrome",
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

    async def browser_network_requests(
        self,
        session_id: str,
        url_pattern: Optional[str] = None,
        include_static: bool = False,
        after_id: Annotated[int, Field(ge=0)] = 0,
        limit: Annotated[int, Field(ge=1, le=200)] = 50,
    ) -> NetworkRequestsModel:
        """List completed requests across page changes, with IDs and pagination. Recording starts when the browser session opens.

        :param session_id: Browser session ID.
        :param url_pattern: Filter URLs by regular expression.
        :param include_static: Include successful non-API requests too.
        :param after_id: Return requests with a higher ID; use next_cursor for more.
        :param limit: Maximum requests to return.
        """
        network = self._get_session(session_id, ["stealthy"]).session.network
        records = network.search(
            url_pattern=url_pattern, include_static=include_static, after_id=after_id, limit=limit + 1
        )
        shown = records[:limit]
        return NetworkRequestsModel(
            requests=[NetworkRequestInfo.model_validate(record, from_attributes=True) for record in shown],
            next_cursor=shown[-1].meta["network_id"] if shown else max(after_id, network.last_id),
            has_more=len(records) > limit,
            dropped_count=network.dropped_count,
        )

    async def browser_network_request(
        self,
        session_id: str,
        request_id: Annotated[int, Field(ge=1)],
        part: NetworkPart = "summary",
    ) -> NetworkRequestModel:
        """Read a complete saved request part without resending it, with structured data and availability notes.

        :param session_id: Browser session ID.
        :param request_id: ID from `browser_network_requests`.
        :param part: Request summary, headers, or text body; incomplete headers are marked.
        """
        network = self._get_session(session_id, ["stealthy"]).session.network
        record = network.get(request_id)
        if record is None:
            raise ValueError(
                f"Request {request_id} was not found or is no longer retained. Use browser_network_requests."
            )
        return _request_details(record, part)

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
        entry = self._get_session(session_id, expected_type=["stealthy"])
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

    async def browser_actions(
        self,
        session_id: str,
        actions: Annotated[List[BrowserAction], Field(min_length=1)],
        slowly: bool = False,
    ) -> str:
        """Run mouse, field, key, and wait actions in order; return plain text without a snapshot.
        Stop on the first error, identifying its action; partial effects remain. No retries.
        Element mouse targets auto-wait and scroll into view; coordinates and wheel do not wait for navigation or scrolling.
        Cancelled/timed-out clicks attempt button release. Load waits observe the current document, not future navigation.

        :param session_id: ID from `browser_open`; call `browser_fetch` first.
        :param actions: Ordered actions; fields need one selector/ref, mouse targets one selector/ref or viewport (x, y).
        :param slowly: Fresh random delays: 50-150 ms per character, 100-300 ms between all actions, including waits.
        """
        _validate_actions(actions)
        with self._browser_page(session_id) as (_, page):
            await _run_actions(page, actions, slowly)
        return "Actions completed."

    async def browser_evaluate(
        self,
        session_id: str,
        expression: NonEmptyString,
        arg: Optional[Dict[str, Any]] = None,
        isolated_context: bool = True,
    ) -> str:
        """Run JavaScript on the current page, await promises, and return JSON text without a snapshot.
        Return JSON-compatible values; null/undefined become null. Script effects are not undone on failure.
        Cancellation stops waiting, but may not stop the script.

        :param session_id: ID from `browser_open`; call `browser_fetch` first.
        :param expression: JavaScript expression or function to invoke.
        :param arg: JSON object passed to the function; use properties for scalar or array values.
        :param isolated_context: False accesses the page's own JS variables; True uses a separate context with the same DOM.
        """
        with self._browser_page(session_id) as (_, page):
            return dumps(
                await page.evaluate(expression, arg=arg, isolated_context=isolated_context),
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            )

    async def browser_screenshot(
        self,
        session_id: str,
        image_type: ScreenshotType = "png",
        full_page: bool = False,
        quality: Optional[Annotated[int, Field(ge=0, le=100)]] = None,
        timeout: NonNegativeFiniteFloat = 30000,
        selector: Optional[NonEmptyString] = None,
        ref: Optional[NonEmptyString] = None,
    ) -> List[ImageContent | TextContent]:
        """Capture the current page or one element without navigating; return the image and current URL.
        Element capture waits and scrolls into view. Use browser_actions for other waits before capture.

        :param session_id: ID from `browser_open`; call `browser_fetch` first.
        :param image_type: Image format.
        :param full_page: Capture the full scrollable page; incompatible with selector/ref.
        :param quality: JPEG quality, 0-100; invalid for PNG.
        :param timeout: Capture limit in milliseconds; 0 disables it.
        :param selector: Playwright selector matching one element; omit when using ref.
        :param ref: Current snapshot element reference; omit both targets for page capture.
        """
        if quality is not None and image_type != "jpeg":
            raise ValueError("'quality' is only valid when 'image_type' is 'jpeg'.")
        if selector is not None and ref is not None:
            raise ValueError("Provide either 'selector' or 'ref', not both.")
        if full_page and (selector is not None or ref is not None):
            raise ValueError("'full_page' cannot be combined with 'selector' or 'ref'.")

        with self._browser_page(session_id) as (_, page):
            options: Dict[str, Any] = {"type": image_type, "quality": quality, "timeout": timeout}
            if selector is not None or ref is not None:
                started = monotonic()
                element = await page.locator(selector or f"aria-ref={ref}").element_handle(timeout=timeout)
                try:
                    options["timeout"] = max(1, timeout - (monotonic() - started) * 1000) if timeout else 0
                    data = await element.screenshot(**options)
                except BaseException as exc:
                    try:
                        with CancelScope(shield=True):
                            await element.dispose()
                    except Exception as cleanup_error:
                        raise exc from cleanup_error
                    raise
                with CancelScope(shield=True):
                    await element.dispose()
            else:
                data = await page.screenshot(full_page=full_page, **options)
            return [Image(data=data, format=image_type).to_image_content(), TextContent(type="text", text=page.url)]

    @staticmethod
    async def make_request(
        url: str,
        method: SUPPORTED_HTTP_METHODS = "GET",
        impersonate: _MCPImpersonateType = "chrome",
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

    async def browser_fetch_once(
        self,
        url: str,
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = True,
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
        """Fetch a page with a stealth browser and JavaScript rendering.

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
        async with AsyncStealthySession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            cdp_url=cdp_url,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            block_ads=True,
            max_pages=1,
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
            page = await session.fetch(url)

        return _translate_response(page, extraction_type, css_selector, main_content_only)

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
        """Fetch a URL in an open stealthy browser session. Options apply only to this request.

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
        :param solve_cloudflare: Attempt to solve Cloudflare Turnstile/interstitial challenges.
        """
        entry = self._get_session(session_id, expected_type=["stealthy"])
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
            url, **{name: value for name, value in fetch_params.items() if name in _STEALTH_FETCH_KEYS}
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
            "instructions": """1. Close sessions when done. Use `list_sessions` to check sessions and settings. Read needed network data before closing; closing removes access to its history.
2. Unless the user chooses a tool, start with HTTP for low to mid protection; use browsers for strong protection or JavaScript.
3. Use `make_request` or `browser_fetch_once` for standalone fetches; they close automatically. Use sessions for related requests or follow-up browser actions and network history.
4. Use `css_selector` to reduce output. HTML/Markdown/text return all matches; snapshots require one match or no selector for the whole page.
5. Session options persist from opening; fetch options apply per call, with schema defaults.
6. Each browser session uses one page; finish each call before starting the next in that session.
7. Snapshots include refs and boxes by default; `main_content_only` and `pierce_shadow` do not filter them.
8. `browser_actions` chains mouse, field, key and wait actions on the current page. Move/click needs one selector, current snapshot ref, or viewport (x, y) in CSS pixels; fields need one selector/ref. Wheel uses the current pointer without waiting for scrolling; coordinate clicks do not wait for navigation. Load waits observe the current document; wait for a result element for delayed navigation.
9. Network history saves completed requests and responses across page changes. Failed/unfinished requests are omitted; closing does not wait for running captures. Use `include_static=True` to list successful non-API traffic. Limits: 1000 requests and 20 MiB of saved response bodies; oldest records are removed first. Only response bodies with a text Content-Type are read and saved. Response bodies over 1 MiB are skipped; unavailable bodies are marked.""",
        }
        if self._auth_token:
            base_url = AnyHttpUrl(f"http://{host}:{port}")
            settings["token_verifier"] = _StaticTokenVerifier(self._auth_token)
            settings["auth"] = AuthSettings(issuer_url=base_url, resource_server_url=base_url)

        server = MCPServer(name="Scrapling", **settings)
        # Session management tools
        server.add_tool(
            _mcp_tool(self.browser_open),
            title="Open browser",
            structured_output=True,
            annotations=_SESSION_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.open_request_session),
            title="Open HTTP session",
            structured_output=True,
            annotations=_SESSION_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.close_session),
            title="Close session",
            structured_output=True,
            annotations=_SESSION_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.list_sessions),
            title="List sessions",
            structured_output=True,
            annotations=_LIST_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.make_request),
            title="Send HTTP request",
            description=self.make_request.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.browser_fetch_once),
            title="Fetch page in browser",
            description=self.browser_fetch_once.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Session-scoped fetch tools
        server.add_tool(
            _mcp_tool(self.browser_fetch),
            title="Fetch in browser session",
            description=self.browser_fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.session_make_request),
            title="Send HTTP request in HTTP session",
            description=self.session_make_request.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.browser_snapshot),
            title="Browser page snapshot",
            description=self.browser_snapshot.__doc__,
            structured_output=False,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.browser_actions),
            title="Browser actions",
            description=self.browser_actions.__doc__,
            structured_output=False,
            annotations=_INPUT_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.browser_evaluate),
            title="Run JavaScript",
            description=self.browser_evaluate.__doc__,
            structured_output=False,
            annotations=_INPUT_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.browser_network_requests),
            title="List network requests",
            annotations=_LIST_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            _mcp_tool(self.browser_network_request),
            title="Read network request",
            annotations=_LIST_TOOL_ANNOTATIONS,
        )
        # Screenshot tool (returns image + url content blocks, not structured JSON)
        server.add_tool(
            _mcp_tool(self.browser_screenshot),
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
