from time import time
from asyncio import sleep as asyncio_sleep, Lock
from contextlib import contextmanager, asynccontextmanager

from playwright.sync_api._generated import Page
from playwright.sync_api import (
    Frame,
    Browser,
    BrowserContext,
    Playwright,
    Response as SyncPlaywrightResponse,
)
from playwright.async_api._generated import Page as AsyncPage
from playwright.async_api import (
    Frame as AsyncFrame,
    Browser as AsyncBrowser,
    Playwright as AsyncPlaywright,
    Response as AsyncPlaywrightResponse,
    BrowserContext as AsyncBrowserContext,
)
from playwright._impl._errors import Error as PlaywrightError

from scrapling.parser import Selector
from scrapling.engines._browsers._page import PageInfo, PagePool
from scrapling.engines._browsers._validators import validate, PlaywrightConfig, StealthConfig
from scrapling.engines._browsers._config_tools import __default_chrome_useragent__, __default_useragent__
from scrapling.engines.toolbelt.navigation import construct_proxy_dict, intercept_route, async_intercept_route
from scrapling.core._types import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    TYPE_CHECKING,
    overload,
    Tuple,
    ProxyType,
    Generator,
    AsyncGenerator,
)
from scrapling.engines.constants import (
    DEFAULT_STEALTH_FLAGS,
    HARMFUL_DEFAULT_ARGS,
    DEFAULT_FLAGS,
)


class SyncSession:
    _config: "PlaywrightConfig | StealthConfig"
    _context_options: Dict[str, Any]

    def _build_context_with_proxy(self, proxy: Optional[ProxyType] = None) -> Dict[str, Any]:
        raise NotImplementedError  # pragma: no cover

    def __init__(self, max_pages: int = 1):
        self.max_pages = max_pages
        self.page_pool = PagePool(max_pages)
        self._max_wait_for_page = 60
        self.playwright: Playwright | Any = None
        self.context: BrowserContext | Any = None
        self.browser: Optional[Browser] = None
        self._is_alive = False

    def start(self):
        pass

    def close(self):  # pragma: no cover
        """Close all resources"""
        if not self._is_alive:
            return

        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None  # pyright: ignore

        self._is_alive = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _initialize_context(self, config: PlaywrightConfig | StealthConfig, ctx: BrowserContext) -> BrowserContext:
        """Initialize the browser context."""
        if config.init_script:
            ctx.add_init_script(path=config.init_script)

        if config.cookies:  # pragma: no cover
            ctx.add_cookies(config.cookies)

        return ctx

    def _get_page(
        self,
        timeout: int | float,
        extra_headers: Optional[Dict[str, str]],
        disable_resources: bool,
        context: Optional[BrowserContext] = None,
    ) -> PageInfo[Page]:  # pragma: no cover
        """Get a new page to use"""
        # No need to check if a page is available or not in sync code because the code blocked before reaching here till the page closed, ofc.
        ctx = context if context is not None else self.context
        assert ctx is not None, "Browser context not initialized"
        page = ctx.new_page()
        page.set_default_navigation_timeout(timeout)
        page.set_default_timeout(timeout)
        if extra_headers:
            page.set_extra_http_headers(extra_headers)

        if disable_resources:
            page.route("**/*", intercept_route)

        page_info = self.page_pool.add_page(page)
        page_info.mark_busy()
        return page_info

    def get_pool_stats(self) -> Dict[str, int]:
        """Get statistics about the current page pool"""
        return {
            "total_pages": self.page_pool.pages_count,
            "busy_pages": self.page_pool.busy_count,
            "max_pages": self.max_pages,
        }

    @staticmethod
    def _wait_for_networkidle(page: Page | Frame, timeout: Optional[int] = None):
        """Wait for the page to become idle (no network activity) even if there are never-ending requests."""
        try:
            page.wait_for_load_state("networkidle", timeout=timeout)
        except (PlaywrightError, Exception):
            pass

    def _wait_for_page_stability(self, page: Page | Frame, load_dom: bool, network_idle: bool):
        page.wait_for_load_state(state="load")
        if load_dom:
            page.wait_for_load_state(state="domcontentloaded")
        if network_idle:
            self._wait_for_networkidle(page)

    @staticmethod
    def _create_response_handler(page_info: PageInfo[Page], response_container: List) -> Callable:
        """Create a response handler that captures the final navigation response.

        :param page_info: The PageInfo object containing the page
        :param response_container: A list to store the final response (mutable container)
        :return: A callback function for page.on("response", ...)
        """

        def handle_response(finished_response: SyncPlaywrightResponse):
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
                and finished_response.request.frame == page_info.page.main_frame
            ):
                response_container[0] = finished_response

        return handle_response

    @contextmanager
    def _page_generator(
        self,
        timeout: int | float,
        extra_headers: Optional[Dict[str, str]],
        disable_resources: bool,
        proxy: Optional[ProxyType] = None,
    ) -> Generator["PageInfo[Page]", None, None]:
        """Acquire a page - either from persistent context or fresh context with proxy."""
        if self._config.proxy_rotator:
            # Rotation mode: create fresh context with the provided proxy
            if not self.browser:  # pragma: no cover
                raise RuntimeError("Browser not initialized for proxy rotation mode")
            context_options = self._build_context_with_proxy(proxy)
            context: BrowserContext = self.browser.new_context(**context_options)

            try:
                context = self._initialize_context(self._config, context)
                page_info = self._get_page(timeout, extra_headers, disable_resources, context=context)
                yield page_info
            finally:
                context.close()
        else:
            # Standard mode: use PagePool with persistent context
            page_info = self._get_page(timeout, extra_headers, disable_resources)
            try:
                yield page_info
            finally:
                page_info.page.close()
                self.page_pool.pages.remove(page_info)


class AsyncSession:
    _config: "PlaywrightConfig | StealthConfig"
    _context_options: Dict[str, Any]

    def _build_context_with_proxy(self, proxy: Optional[ProxyType] = None) -> Dict[str, Any]:
        raise NotImplementedError  # pragma: no cover

    def __init__(self, max_pages: int = 1):
        self.max_pages = max_pages
        self.page_pool = PagePool(max_pages)
        self._max_wait_for_page = 60
        self.playwright: AsyncPlaywright | Any = None
        self.context: AsyncBrowserContext | Any = None
        self.browser: Optional[AsyncBrowser] = None
        self._is_alive = False
        self._lock = Lock()

    async def start(self):
        pass

    async def close(self):
        """Close all resources"""
        if not self._is_alive:  # pragma: no cover
            return

        if self.context:
            await self.context.close()
            self.context = None  # pyright: ignore

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None  # pyright: ignore

        self._is_alive = False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _initialize_context(
        self, config: PlaywrightConfig | StealthConfig, ctx: AsyncBrowserContext
    ) -> AsyncBrowserContext:
        """Initialize the browser context."""
        if config.init_script:  # pragma: no cover
            await ctx.add_init_script(path=config.init_script)

        if config.cookies:  # pragma: no cover
            await ctx.add_cookies(config.cookies)

        return ctx

    async def _get_page(
        self,
        timeout: int | float,
        extra_headers: Optional[Dict[str, str]],
        disable_resources: bool,
        context: Optional[AsyncBrowserContext] = None,
    ) -> PageInfo[AsyncPage]:  # pragma: no cover
        """Get a new page to use"""
        ctx = context if context is not None else self.context
        if TYPE_CHECKING:
            assert ctx is not None, "Browser context not initialized"

        async with self._lock:
            # If we're at max capacity after cleanup, wait for busy pages to finish
            if context is None and self.page_pool.pages_count >= self.max_pages:
                # Only applies when using persistent context
                start_time = time()
                while time() - start_time < self._max_wait_for_page:
                    await asyncio_sleep(0.05)
                    if self.page_pool.pages_count < self.max_pages:
                        break
                else:
                    raise TimeoutError(
                        f"No pages finished to clear place in the pool within the {self._max_wait_for_page}s timeout period"
                    )

            page = await ctx.new_page()
            page.set_default_navigation_timeout(timeout)
            page.set_default_timeout(timeout)
            if extra_headers:
                await page.set_extra_http_headers(extra_headers)

            if disable_resources:
                await page.route("**/*", async_intercept_route)

            return self.page_pool.add_page(page)

    def get_pool_stats(self) -> Dict[str, int]:
        """Get statistics about the current page pool"""
        return {
            "total_pages": self.page_pool.pages_count,
            "busy_pages": self.page_pool.busy_count,
            "max_pages": self.max_pages,
        }

    @staticmethod
    async def _wait_for_networkidle(page: AsyncPage | AsyncFrame, timeout: Optional[int] = None):
        """Wait for the page to become idle (no network activity) even if there are never-ending requests."""
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
        except (PlaywrightError, Exception):
            pass

    async def _wait_for_page_stability(self, page: AsyncPage | AsyncFrame, load_dom: bool, network_idle: bool):
        await page.wait_for_load_state(state="load")
        if load_dom:
            await page.wait_for_load_state(state="domcontentloaded")
        if network_idle:
            await self._wait_for_networkidle(page)

    @staticmethod
    def _create_response_handler(page_info: PageInfo[AsyncPage], response_container: List) -> Callable:
        """Create an async response handler that captures the final navigation response.

        :param page_info: The PageInfo object containing the page
        :param response_container: A list to store the final response (mutable container)
        :return: A callback function for page.on("response", ...)
        """

        async def handle_response(finished_response: AsyncPlaywrightResponse):
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
                and finished_response.request.frame == page_info.page.main_frame
            ):
                response_container[0] = finished_response

        return handle_response

    @asynccontextmanager
    async def _page_generator(
        self,
        timeout: int | float,
        extra_headers: Optional[Dict[str, str]],
        disable_resources: bool,
        proxy: Optional[ProxyType] = None,
    ) -> AsyncGenerator["PageInfo[AsyncPage]", None]:
        """Acquire a page - either from persistent context or fresh context with proxy."""
        if self._config.proxy_rotator:
            # Rotation mode: create fresh context with the provided proxy
            if not self.browser:  # pragma: no cover
                raise RuntimeError("Browser not initialized for proxy rotation mode")
            context_options = self._build_context_with_proxy(proxy)
            context: AsyncBrowserContext = await self.browser.new_context(**context_options)

            try:
                context = await self._initialize_context(self._config, context)
                page_info = await self._get_page(timeout, extra_headers, disable_resources, context=context)
                yield page_info
            finally:
                await context.close()
        else:
            # Standard mode: use PagePool with persistent context
            page_info = await self._get_page(timeout, extra_headers, disable_resources)
            try:
                yield page_info
            finally:
                await page_info.page.close()
                self.page_pool.pages.remove(page_info)


class BaseSessionMixin:
    @overload
    def __validate_routine__(self, params: Dict, model: type[StealthConfig]) -> StealthConfig: ...

    @overload
    def __validate_routine__(self, params: Dict, model: type[PlaywrightConfig]) -> PlaywrightConfig: ...

    def __validate_routine__(
        self, params: Dict, model: type[PlaywrightConfig] | type[StealthConfig]
    ) -> PlaywrightConfig | StealthConfig:
        # Dark color scheme bypasses the 'prefersLightColor' check in creepjs
        self._context_options: Dict[str, Any] = {"color_scheme": "dark", "device_scale_factor": 2}
        self._browser_options: Dict[str, Any] = {
            "args": DEFAULT_FLAGS,
            "ignore_default_args": HARMFUL_DEFAULT_ARGS,
        }
        if "__max_pages" in params:
            params["max_pages"] = params.pop("__max_pages")

        config = validate(params, model=model)
        self._headers_keys = (
            {header.lower() for header in config.extra_headers.keys()} if config.extra_headers else set()
        )

        return config

    def __generate_options__(self, extra_flags: Tuple | None = None) -> None:
        config: PlaywrightConfig | StealthConfig = self._config  # type: ignore[has-type]
        self._context_options.update(
            {
                "proxy": config.proxy,
                "locale": config.locale,
                "timezone_id": config.timezone_id,
                "extra_http_headers": config.extra_headers,
            }
        )
        # The default useragent in the headful is always correct now in the current versions of Playwright
        if config.useragent:
            self._context_options["user_agent"] = config.useragent
        elif not config.useragent and config.headless:
            self._context_options["user_agent"] = (
                __default_chrome_useragent__ if config.real_chrome else __default_useragent__
            )

        if not config.cdp_url:
            flags = self._browser_options["args"]
            if config.extra_flags or extra_flags:
                flags = list(set(flags + (config.extra_flags or extra_flags)))

            self._browser_options.update(
                {
                    "args": flags,
                    "headless": config.headless,
                    "channel": "chrome" if config.real_chrome else "chromium",
                }
            )

            self._user_data_dir = config.user_data_dir
        else:
            self._browser_options = {}

        if config.additional_args:
            self._context_options.update(config.additional_args)

    def _build_context_with_proxy(self, proxy: Optional[ProxyType] = None) -> Dict[str, Any]:
        """
        Build context options with a specific proxy for rotation mode.

        :param proxy: Proxy URL string or Playwright-style proxy dict to use for this context.
        :return: Dictionary of context options for browser.new_context().
        """

        context_options = self._context_options.copy()

        # Override proxy if provided
        if proxy:
            context_options["proxy"] = construct_proxy_dict(proxy)

        return context_options


class DynamicSessionMixin(BaseSessionMixin):
    def __validate__(self, **params):
        self._config = self.__validate_routine__(params, model=PlaywrightConfig)
        self.__generate_options__()


class StealthySessionMixin(BaseSessionMixin):
    def __validate__(self, **params):
        self._config: StealthConfig = self.__validate_routine__(params, model=StealthConfig)
        self._context_options.update(
            {
                "is_mobile": False,
                "has_touch": False,
                # I'm thinking about disabling it to rest from all Service Workers' headache, but let's keep it as it is for now
                "service_workers": "allow",
                "ignore_https_errors": True,
                "screen": {"width": 1920, "height": 1080},
                "viewport": {"width": 1920, "height": 1080},
                "permissions": ["geolocation", "notifications"],
            }
        )
        self.__generate_stealth_options()

    def __generate_stealth_options(self) -> None:
        flags = tuple()
        if not self._config.cdp_url:
            flags = DEFAULT_FLAGS + DEFAULT_STEALTH_FLAGS

            if self._config.block_webrtc:
                flags += (
                    "--webrtc-ip-handling-policy=disable_non_proxied_udp",
                    "--force-webrtc-ip-handling-policy",  # Ensures the policy is enforced
                )
            if not self._config.allow_webgl:
                flags += (
                    "--disable-webgl",
                    "--disable-webgl-image-chromium",
                    "--disable-webgl2",
                )
            if self._config.hide_canvas:
                flags += ("--fingerprinting-canvas-image-data-noise",)

        super(StealthySessionMixin, self).__generate_options__(flags)

    @staticmethod
    def _detect_cloudflare(page_content: str) -> str | None:
        """
        Detect the type of Cloudflare challenge present in the provided page content.

        This function analyzes the given page content to identify whether a specific
        type of Cloudflare challenge is present. It checks for three predefined
        challenge types: non-interactive, managed, and interactive. If a challenge
        type is detected, it returns the corresponding type as a string. If no
        challenge type is detected, it returns None.

        Args:
            page_content (str): The content of the page to analyze for Cloudflare
                challenge types.

        Returns:
            str: A string representing the detected Cloudflare challenge type, if
                found. Returns None if no challenge matches.
        """
        challenge_types = (
            "non-interactive",
            "managed",
            "interactive",
        )
        for ctype in challenge_types:
            if f"cType: '{ctype}'" in page_content:
                return ctype

        # Check if turnstile captcha is embedded inside the page (Usually inside a closed Shadow iframe)
        selector = Selector(content=page_content)
        if selector.css('script[src*="challenges.cloudflare.com/turnstile/v"]'):
            return "embedded"

        return None
