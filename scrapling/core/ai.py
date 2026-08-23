from uuid import uuid4
from os import environ
from hmac import compare_digest
from asyncio import gather
from datetime import datetime, timezone
from dataclasses import dataclass, field

from mcp.server import MCPServer
from mcp.server.mcpserver import Image
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.caching import CacheHint
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import Icon, ImageContent, TextContent, ToolAnnotations
from pydantic import AnyHttpUrl, BaseModel, Field

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
    Set,
    Sequence,
    SetCookieParam,
    extraction_types,
    SelectorWaitStates,
    FollowRedirects,
    SUPPORTED_HTTP_METHODS,
)

SessionType = Literal["dynamic", "stealthy", "static"]
BrowserSessionType = Literal["dynamic", "stealthy"]
ScreenshotType = Literal["png", "jpeg"]
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


class ResponseModel(BaseModel):
    """Request's response information structure."""

    status: int = Field(description="The status code returned by the website.")
    content: list[str] = Field(description="The content as Markdown/HTML or the text content of the page.")
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

    def _get_session(self, session_id: str, expected_type: Optional[SessionType]) -> _SessionEntry:
        """Look up a session by ID, optionally validating its type. Pass `None` to skip the type check."""
        entry = self._sessions.get(session_id)
        if entry is None:
            raise ValueError(f"Session '{session_id}' not found. Use list_sessions to see active sessions.")
        if not entry.session._is_alive:
            raise ValueError(f"Session '{session_id}' is no longer alive. Open a new session.")
        if expected_type is not None and entry.session_type != expected_type:
            raise ValueError(
                f"Session '{session_id}' is a '{entry.session_type}' session, but this tool requires a "
                f"'{expected_type}' session. Use the matching fetch tool for your session type."
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

    async def open_session(
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
        """Open a persistent browser session that can be reused across multiple `session_fetch` calls.
        This avoids the overhead of launching a new browser for each request. Sessions hold the browser-level
        configuration only; per-request options are passed to `session_fetch` on each call.

        :param session_type: The type of session to open. Use "dynamic" for standard Playwright browser, or "stealthy" for anti-bot bypass with fingerprint spoofing.
        :param session_id: Optional custom session ID. If not provided, a random 12-character hex ID will be generated. Useful for naming sessions for easier management.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param proxy: The proxy used for every request in this session, as a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this session.
        :param cookies: Set cookies for the session. It should be in a dictionary format that Playwright accepts.
        :param hide_canvas: (Stealthy only) Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: (Stealthy only) Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param allow_webgl: (Stealthy only) Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param additional_args: (Stealthy only) Additional arguments to be passed to Playwright's context as additional settings.
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
        """Open a persistent HTTP requests session (no browser) that can be reused across multiple
        `session_make_request` calls, keeping cookies, connections, and the browser fingerprint between requests.
        The session holds this configuration only; per-request options are passed to `session_make_request` on each call.
        It shares `close_session`/`list_sessions` with the browser sessions and shows there as a 'static' session.

        :param session_id: Optional custom session ID. If not provided, a random 12-character hex ID will be generated. Useful for naming sessions for easier management.
        :param impersonate: Browser version to impersonate its fingerprint on every request. It's using the latest chrome version by default.
        :param proxy: The proxy URL used for every request in this session. Format: "http://username:password@localhost:8030".
        """
        session_id = self._new_session_id(session_id)
        session = FetcherSession(impersonate=impersonate, proxy=proxy)
        await session.__aenter__()
        return self._register_session(session_id, session, "static")

    async def close_session(
        self,
        session_id: str,
    ) -> SessionClosedModel:
        """Close a persistent session and free its resources.

        :param session_id: The unique identifier of the session to close. Use list_sessions to see active sessions.
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
        """List all active sessions with their details, including the effective settings each one was created with."""
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

    async def screenshot(
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
        """Capture a screenshot of a web page using an existing browser session and return it as an image.
        A browser session must be opened first with `open_session` (either `dynamic` or `stealthy`); the session ID is then passed here.

        :param url: The URL to navigate to and capture.
        :param session_id: ID of an open browser session created with `open_session`.
        :param image_type: Image format. Defaults to "png". Use "jpeg" for smaller file sizes.
        :param full_page: When True, captures the full scrollable page instead of just the viewport.
        :param quality: Image quality (0-100) for JPEG only. Raises if passed with `image_type="png"`.
        :param wait: Time in milliseconds to wait after page load before capturing.
        :param wait_selector: Optional CSS selector to wait for before capturing.
        :param wait_selector_state: State to wait for the selector.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: Timeout in milliseconds for page operations.
        """
        if quality is not None and image_type != "jpeg":
            raise ValueError("'quality' is only valid when 'image_type' is 'jpeg'.")

        entry = self._get_session(session_id, expected_type=None)
        if entry.session_type == "static":
            raise ValueError(
                f"Session '{session_id}' is a 'static' session, so it can't take screenshots. "
                f"Open a 'dynamic' or 'stealthy' session for that."
            )

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
        """Make an HTTP request to a URL with any method (GET, POST, PUT, DELETE) and return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param url: The URL to request.
        :param method: The HTTP method to use: "GET" (default), "POST", "PUT", or "DELETE".
        :param impersonate: Browser version to impersonate its fingerprint. It's using the latest chrome version by default.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param data: Form data for the request body. Used with "POST", "PUT", and "DELETE" only.
        :param json: A JSON-serializable object for the request body. Used with "POST", "PUT", and "DELETE" only.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to "safe", which follows redirects but rejects those targeting internal/private IPs (SSRF protection).
            Pass True to follow all redirects without restriction.
        :param max_redirects: Maximum number of redirects. Use -1 for unlimited.
        :param retries: Number of retry attempts.
        :param retry_delay: Number of seconds to wait between retry attempts.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy in dictionary format with `username` and `password` keys.
        :param auth: HTTP basic auth in dictionary format with `username` and `password` keys.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets a Google referer header.
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
        """Make GET HTTP request to a group of URLs and for each URL, return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param urls: A list of the URLs to request.
        :param impersonate: Browser version to impersonate its fingerprint. It's using the latest chrome version by default.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to "safe", which follows redirects but rejects those targeting internal/private IPs (SSRF protection).
            Pass True to follow all redirects without restriction.
        :param max_redirects: Maximum number of redirects. Use -1 for unlimited.
        :param retries: Number of retry attempts.
        :param retry_delay: Number of seconds to wait between retry attempts.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy in dictionary format with `username` and `password` keys.
        :param auth: HTTP basic auth in dictionary format with `username` and `password` keys.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets a Google referer header.
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

    async def fetch(
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
    ) -> ResponseModel:
        """Use playwright to open a browser to fetch a URL and return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param url: The URL to request.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        """
        results = await self.bulk_fetch(
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
            wait_selector_state=wait_selector_state,
        )
        return results[0]

    async def bulk_fetch(
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
    ) -> List[ResponseModel]:
        """Use playwright to open a browser, then fetch a group of URLs at the same time, and for each page return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param urls: A list of the URLs to request. Batches bigger than 50 URLs are fetched through a pool of 50 concurrent pages.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
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

    async def stealthy_fetch(
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
    ) -> ResponseModel:
        """Use the stealthy fetcher to fetch a URL and return a structured output of the result.
        The only fetcher suitable for high-protection websites.

        :param url: The URL to request.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        """
        results = await self.bulk_stealthy_fetch(
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
            wait_selector_state=wait_selector_state,
            block_webrtc=block_webrtc,
            allow_webgl=allow_webgl,
            solve_cloudflare=solve_cloudflare,
            additional_args=additional_args,
        )
        return results[0]

    async def bulk_stealthy_fetch(
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
    ) -> List[ResponseModel]:
        """Use the stealthy fetcher to fetch a group of URLs at the same time, and for each page return a structured output of the result.
        The only fetcher suitable for high-protection websites.

        :param urls: A list of the URLs to request. Batches bigger than 50 URLs are fetched through a pool of 50 concurrent pages.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
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

    async def session_fetch(
        self,
        url: str,
        session_id: str,
        extraction_type: extraction_types = "markdown",
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
    ) -> ResponseModel:
        """Fetch a URL through a browser session previously opened with `open_session` and return a structured output of the result.
        The session (dynamic or stealthy) holds the browser-level configuration; every option here applies to this request only, with the defaults shown.

        :param url: The URL to request.
        :param session_id: ID of an open browser session created with `open_session`.
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the `Response` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on the page to fully load and execute.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param blocked_domains: A list of domain names to block requests to for this request. Subdomains are also matched.
        :param solve_cloudflare: (Stealthy sessions only) Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response.
        """
        entry = self._get_session(session_id, expected_type=None)
        if entry.session_type == "static":
            raise ValueError(
                f"Session '{session_id}' is a 'static' session. Use `session_make_request` with it instead."
            )
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
        """Make an HTTP request with any method (GET, POST, PUT, DELETE) through a requests session previously opened
        with `open_request_session`, keeping its cookies, connections, and browser fingerprint across calls. The session
        holds the impersonation and proxy configuration; every option here applies to this request only, with the defaults shown.

        :param url: The URL to request.
        :param session_id: ID of an open requests session created with `open_request_session`.
        :param method: The HTTP method to use: "GET" (default), "POST", "PUT", or "DELETE".
        :param extraction_type: The type of content to extract from the page: "markdown", "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page.
        :param main_content_only: Whether to extract only the main content of the page. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param data: Form data for the request body. Used with "POST", "PUT", and "DELETE" only.
        :param json: A JSON-serializable object for the request body. Used with "POST", "PUT", and "DELETE" only.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to "safe", which follows redirects but rejects those targeting internal/private IPs (SSRF protection).
            Pass True to follow all redirects without restriction.
        :param max_redirects: Maximum number of redirects. Use -1 for unlimited.
        :param retries: Number of retry attempts.
        :param retry_delay: Number of seconds to wait between retry attempts.
        :param auth: HTTP basic auth in dictionary format with `username` and `password` keys.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets a Google referer header.
        """
        entry = self._get_session(session_id, expected_type="static")

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
1. When the `open_session` or `open_request_session` tools are used, make sure to close the session with `close_session` after you finish, and use `list_sessions` if you lose track of the open sessions or their effective settings.
2. If the user didn't specify which tool to use, start with the `make_request` tool (a plain HTTP request, defaulting to GET; set `method` for POST/PUT/DELETE), then escalate. The `make_request` tool and `bulk_get` (its GET-only bulk version) are suitable only for low-to-mid protection levels.
    For high-protection levels or websites that require JS loading, use the other tools directly.
3. For all tools, if the `css_selector` resolves to more than one element, all the elements will be returned.
4. For all fetch tools, the `extraction_type` parameter controls the format of the returned content: "markdown" (default) converts the page content to Markdown, "html" returns the raw HTML, and "text" returns the text content of the page.
5. For all fetch tools, `main_content_only` is enabled by default and returns only the content inside the page's `<body>` tag. Pass `main_content_only=False` when you need the full page instead.
6. If the task consists of multiple sequential requests to the same website, open a session once, then fetch through it to be more efficient:
    `open_session` + `session_fetch` per page for browsers, or `open_request_session` + `session_make_request` per request for plain HTTP.
7. Sessions hold the session-level configuration set when opened, while `session_fetch`/`session_make_request` carry the per-request options and apply them on each call with the defaults shown in their schemas.
    The one-shot tools (`make_request`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`) never touch sessions.
8. If you are making multiple parallel one-shot requests, use the bulk version of the tool to be more efficient.
9. If you are crawling/browsing a website, be more efficient by using the `css_selector` parameter to only access the parts you are interested in and save money/time. Example: use the `a` selector to extract the urls right away.
10. The user can pass a CDP URL to connect to a remote browser session through the `open_session` tool, then use it with the session tools.
""",
        }
        if self._auth_token:
            base_url = AnyHttpUrl(f"http://{host}:{port}")
            settings["token_verifier"] = _StaticTokenVerifier(self._auth_token)
            settings["auth"] = AuthSettings(issuer_url=base_url, resource_server_url=base_url)

        server = MCPServer(name="Scrapling", **settings)
        # Session management tools
        server.add_tool(
            self.open_session, title="open_session", structured_output=True, annotations=_SESSION_TOOL_ANNOTATIONS
        )
        server.add_tool(
            self.open_request_session,
            title="open_request_session",
            structured_output=True,
            annotations=_SESSION_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.close_session, title="close_session", structured_output=True, annotations=_SESSION_TOOL_ANNOTATIONS
        )
        server.add_tool(
            self.list_sessions, title="list_sessions", structured_output=True, annotations=_LIST_TOOL_ANNOTATIONS
        )
        # HTTP tools
        server.add_tool(
            self.make_request,
            title="make_request",
            description=self.make_request.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.bulk_get,
            title="bulk_get",
            description=self.bulk_get.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Dynamic browser tools
        server.add_tool(
            self.fetch,
            title="fetch",
            description=self.fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.bulk_fetch,
            title="bulk_fetch",
            description=self.bulk_fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Stealthy browser tools
        server.add_tool(
            self.stealthy_fetch,
            title="stealthy_fetch",
            description=self.stealthy_fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.bulk_stealthy_fetch,
            title="bulk_stealthy_fetch",
            description=self.bulk_stealthy_fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Session-scoped fetch tools
        server.add_tool(
            self.session_fetch,
            title="session_fetch",
            description=self.session_fetch.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        server.add_tool(
            self.session_make_request,
            title="session_make_request",
            description=self.session_make_request.__doc__,
            structured_output=True,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        # Screenshot tool (returns image + url content blocks, not structured JSON)
        server.add_tool(
            self.screenshot,
            title="screenshot",
            description=self.screenshot.__doc__,
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
