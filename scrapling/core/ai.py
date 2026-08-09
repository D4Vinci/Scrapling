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
from scrapling.core._types import (
    Optional,
    Literal,
    Union,
    Tuple,
    Mapping,
    Dict,
    List,
    Any,
    Sequence,
    SetCookieParam,
    extraction_types,
    SelectorWaitStates,
    FollowRedirects,
)

SessionType = Literal["dynamic", "stealthy"]
ScreenshotType = Literal["png", "jpeg"]
MCP_EXECUTABLE_PATH_ENV = "SCRAPLING_EXECUTABLE_PATH"
MCP_AUTH_TOKEN_ENV = "SCRAPLING_MCP_AUTH_TOKEN"  # nosec B105 - the name of the variable, not a token

_MAX_POOL_PAGES = 50  # Upper bound of `PagesCount` in scrapling/engines/_browsers/_validators.py


def _page_pool_size(urls: Sequence[str]) -> int:
    """Return a page pool size that covers the batch without leaving the validator's bounds."""
    return min(max(len(urls), 1), _MAX_POOL_PAGES)


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
    session_type: SessionType = Field(description="The type of the session: 'dynamic' or 'stealthy'.")
    created_at: str = Field(description="ISO timestamp of when the session was created.")
    is_alive: bool = Field(description="Whether the session is still alive and usable.")


class SessionCreatedModel(SessionInfo):
    """Response returned when a new session is created."""

    message: str = Field(description="A confirmation message.")


class SessionClosedModel(BaseModel):
    """Response returned when a session is closed."""

    session_id: str = Field(description="The unique identifier of the closed session.")
    message: str = Field(description="A confirmation message.")


@dataclass
class _SessionEntry:
    session: Any  # AsyncDynamicSession | AsyncStealthySession
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

    async def open_session(
        self,
        session_type: SessionType,
        session_id: Optional[str] = None,
        headless: bool = True,
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
        max_pages: int = 5,
        # Stealthy-only params (ignored for dynamic sessions)
        hide_canvas: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        solve_cloudflare: bool = False,
        additional_args: Optional[Dict] = None,
    ) -> SessionCreatedModel:
        """Open a persistent browser session that can be reused across multiple fetch calls.
        This avoids the overhead of launching a new browser for each request.

        :param session_type: The type of session to open. Use "dynamic" for standard Playwright browser, or "stealthy" for anti-bot bypass with fingerprint spoofing.
        :param session_id: Optional custom session ID. If not provided, a random 12-character hex ID will be generated. Useful for naming sessions for easier management.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc.
        :param extra_headers: A dictionary of extra headers to add to the request.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this session.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param cookies: Set cookies for the session. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param max_pages: Maximum number of concurrent pages/tabs in the browser. Defaults to 5. Higher values allow more parallel fetches.
        :param hide_canvas: (Stealthy only) Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: (Stealthy only) Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param allow_webgl: (Stealthy only) Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param solve_cloudflare: (Stealthy only) Solves all types of the Cloudflare's Turnstile/Interstitial challenges.
        :param additional_args: (Stealthy only) Additional arguments to be passed to Playwright's context as additional settings.
        """
        session_id = session_id or uuid4().hex[:12]
        if session_id in self._sessions:
            raise ValueError(
                f"Session '{session_id}' already exists. Use a different ID or close the existing session first."
            )

        common_kwargs: Dict[str, Any] = dict(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            cookies=cookies,
            cdp_url=cdp_url,
            headless=headless,
            block_ads=True,
            max_pages=max_pages,
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
        )

        session: Union[AsyncDynamicSession, AsyncStealthySession]
        if session_type == "stealthy":
            session = AsyncStealthySession(
                **common_kwargs,
                hide_canvas=hide_canvas,
                block_webrtc=block_webrtc,
                allow_webgl=allow_webgl,
                solve_cloudflare=solve_cloudflare,
                additional_args=additional_args,
            )
        else:
            session = AsyncDynamicSession(**common_kwargs)

        await session.start()

        entry = _SessionEntry(session=session, session_type=session_type)
        self._sessions[session_id] = entry

        return SessionCreatedModel(
            session_id=session_id,
            session_type=session_type,
            created_at=entry.created_at,
            is_alive=True,
            message=f"Session '{session_id}' ({session_type}) created successfully.",
        )

    async def close_session(
        self,
        session_id: str,
    ) -> SessionClosedModel:
        """Close a persistent browser session and free its resources.

        :param session_id: The unique identifier of the session to close. Use list_sessions to see active sessions.
        """
        entry = self._sessions.pop(session_id, None)
        if entry is None:
            raise ValueError(f"Session '{session_id}' not found. Use list_sessions to see active sessions.")

        await entry.session.close()
        return SessionClosedModel(
            session_id=session_id,
            message=f"Session '{session_id}' closed successfully.",
        )

    async def list_sessions(self) -> List[SessionInfo]:
        """List all active browser sessions with their details."""
        return [
            SessionInfo(
                session_id=sid,
                session_type=entry.session_type,
                created_at=entry.created_at,
                is_alive=entry.session._is_alive,
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
        :param full_page: When True, captures the full scrollable page instead of just the viewport. Defaults to False.
        :param quality: Image quality (0-100) for JPEG only. Raises if passed with `image_type="png"`.
        :param wait: Time in milliseconds to wait after page load before capturing. Defaults to 0.
        :param wait_selector: Optional CSS selector to wait for before capturing.
        :param wait_selector_state: State to wait for the selector. Defaults to "attached".
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: Timeout in milliseconds for page operations. Defaults to 30,000.
        """
        if quality is not None and image_type != "jpeg":
            raise ValueError("'quality' is only valid when 'image_type' is 'jpeg'.")

        entry = self._get_session(session_id, expected_type=None)

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
            wait=wait,
            timeout=timeout,
            network_idle=network_idle,
            wait_selector=wait_selector,
            wait_selector_state=wait_selector_state,
            page_action=_capture,
        )

        if "error" in captured:
            raise captured["error"]
        if "bytes" not in captured:
            raise RuntimeError(f"Failed to capture screenshot for {url}")

        image = Image(data=captured["bytes"], format=image_type).to_image_content()
        return [image, TextContent(type="text", text=captured["url"])]

    @staticmethod
    async def get(
        url: str,
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
    ) -> ResponseModel:
        """Make GET HTTP request to a URL and return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param url: The URL to request.
        :param impersonate: Browser version to impersonate its fingerprint. It's using the latest chrome version by default.
        :param extraction_type: The type of content to extract from the page: "markdown" (default), "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to "safe", which follows redirects but rejects those targeting internal/private IPs (SSRF protection).
            Pass True to follow all redirects without restriction.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy in dictionary format with `username` and `password` keys.
        :param auth: HTTP basic auth in dictionary format with `username` and `password` keys.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets a Google referer header.
        """
        results = await ScraplingMCPServer.bulk_get(
            urls=[url],
            impersonate=impersonate,
            extraction_type=extraction_type,
            css_selector=css_selector,
            main_content_only=main_content_only,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            retries=retries,
            retry_delay=retry_delay,
            proxy=proxy,
            proxy_auth=proxy_auth,
            auth=auth,
            verify=verify,
            http3=http3,
            stealthy_headers=stealthy_headers,
        )
        return results[0]

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
        :param extraction_type: The type of content to extract from the page: "markdown" (default), "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to "safe", which follows redirects but rejects those targeting internal/private IPs (SSRF protection).
            Pass True to follow all redirects without restriction.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy in dictionary format with `username` and `password` keys.
        :param auth: HTTP basic auth in dictionary format with `username` and `password` keys.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
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
        session_id: Optional[str] = None,
    ) -> ResponseModel:
        """Use playwright to open a browser to fetch a URL and return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param url: The URL to request.
        :param extraction_type: The type of content to extract from the page: "markdown" (default), "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system default locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param session_id: Optional session ID from open_session. If provided, reuses the existing browser session instead of creating a new one.
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
            session_id=session_id,
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
        session_id: Optional[str] = None,
    ) -> List[ResponseModel]:
        """Use playwright to open a browser, then fetch a group of URLs at the same time, and for each page return a structured output of the result.
        Only suitable for low-mid protection levels.

        :param urls: A list of the URLs to request. Batches bigger than 50 URLs are fetched through a pool of 50 concurrent pages.
        :param extraction_type: The type of content to extract from the page: "markdown" (default), "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system default locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param session_id: Optional session ID from open_session. If provided, reuses the existing browser session instead of creating a new one.
        """
        if session_id:
            entry = self._get_session(session_id, "dynamic")
            tasks = [
                entry.session.fetch(
                    url,
                    wait=wait,
                    timeout=timeout,
                    google_search=google_search,
                    extra_headers=extra_headers,
                    disable_resources=disable_resources,
                    wait_selector=wait_selector,
                    wait_selector_state=wait_selector_state,
                    network_idle=network_idle,
                    proxy=proxy,
                )
                for url in urls
            ]
            responses = await gather(*tasks)
        else:
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
        session_id: Optional[str] = None,
    ) -> ResponseModel:
        """Use the stealthy fetcher to fetch a URL and return a structured output of the result.
        The only fetcher suitable for high-protection websites.

        :param url: The URL to request.
        :param extraction_type: The type of content to extract from the page: "markdown" (default), "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system default locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        :param session_id: Optional session ID from open_session. If provided, reuses the existing browser session instead of creating a new one.
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
            session_id=session_id,
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
        session_id: Optional[str] = None,
    ) -> List[ResponseModel]:
        """Use the stealthy fetcher to fetch a group of URLs at the same time, and for each page return a structured output of the result.
        The only fetcher suitable for high-protection websites.

        :param urls: A list of the URLs to request. Batches bigger than 50 URLs are fetched through a pool of 50 concurrent pages.
        :param extraction_type: The type of content to extract from the page: "markdown" (default), "html", or "text".
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system default locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param executable_path: Absolute path to a custom Chromium-compatible browser executable. Overrides the server-wide default for this request.
        :param google_search: Enabled by default, Scrapling will set a Google referer header.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by `google_search` takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        :param session_id: Optional session ID from open_session. If provided, reuses the existing browser session instead of creating a new one.
        """
        if session_id:
            entry = self._get_session(session_id, "stealthy")
            tasks = [
                entry.session.fetch(
                    url,
                    wait=wait,
                    timeout=timeout,
                    google_search=google_search,
                    extra_headers=extra_headers,
                    disable_resources=disable_resources,
                    wait_selector=wait_selector,
                    wait_selector_state=wait_selector_state,
                    network_idle=network_idle,
                    proxy=proxy,
                    solve_cloudflare=solve_cloudflare,
                )
                for url in urls
            ]
            responses = await gather(*tasks)
        else:
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
1. When the `open_session` tool is used, make sure to close the session with `close_session` after you finish, and use `list_sessions` if you lose track of the open sessions.
2. If the user didn't specify which tool to use, start with the `get` tool, then escalate. The `get` tool and the bulk version are only suitable for low-mid protection levels.
    For high-protection levels or websites that require JS loading, use the other tools directly.
3. For all tools, if the `css_selector` resolves to more than one element, all the elements will be returned.
4. For all fetch tools, the `extraction_type` parameter controls the format of the returned content: "markdown" (default) converts the page content to Markdown, "html" returns the raw HTML, and "text" returns the text content of the page.
5. For all fetch tools, `main_content_only` is enabled by default and returns only the content inside the page's `<body>` tag. Pass `main_content_only=False` when you need the full page instead.
6. If the task consists of multiple requests to the same website, open a session to be more efficient.
7. For browser-based tools, if a `session_id` is provided (from open_session), the browser session will be reused instead of creating a new one.
    When using a session, browser-level params (headless, proxy, locale, etc.) are ignored since they were set at session creation time.
8. If you are making multiple requests, use the bulk version of the tool to be more efficient.
9. If you are crawling/browsing a website, be more efficient by using the `css_selector` parameter to only access the parts you are interested in and save money/time. Example: use the `a` selector to extract the urls right away.
10. The user can pass a CDP URL to connect to a remote browser session through the `open_session` tool, then use it in the rest of the tools.
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
            self.close_session, title="close_session", structured_output=True, annotations=_SESSION_TOOL_ANNOTATIONS
        )
        server.add_tool(
            self.list_sessions, title="list_sessions", structured_output=True, annotations=_LIST_TOOL_ANNOTATIONS
        )
        # HTTP tools
        server.add_tool(
            self.get,
            title="get",
            description=self.get.__doc__,
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
        # Screenshot tool (returns image + url content blocks, not structured JSON)
        server.add_tool(
            self.screenshot,
            title="screenshot",
            description=self.screenshot.__doc__,
            structured_output=False,
            annotations=_FETCH_TOOL_ANNOTATIONS,
        )
        return server

    def serve(self, http: bool, host: str, port: int, allowed_hosts: Sequence[str] = ()):
        """Serve the MCP server."""
        if http and not self._auth_token:
            log.warning(
                f"The MCP server is running over HTTP without authentication, so anyone who can reach "
                f"{host}:{port} can use every tool, including fetching arbitrary URLs from this machine. "
                f"Pass `--auth-token` (or set the {MCP_AUTH_TOKEN_ENV} environment variable) to require a bearer token."
            )
        elif self._auth_token and not http:
            log.warning(
                "The authentication token only applies to the streamable-http transport, so it's ignored with stdio."
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
