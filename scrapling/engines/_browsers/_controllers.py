import time
import asyncio

# from camoufox import AsyncNewBrowser, NewBrowser
from playwright.sync_api import (
    sync_playwright,
    BrowserType,
    Browser,
    BrowserContext,
    Playwright,
    Locator,
)
from playwright.async_api import (
    async_playwright,
    BrowserType as AsyncBrowserType,
    Browser as AsyncBrowser,
    BrowserContext as AsyncBrowserContext,
    Playwright as AsyncPlaywright,
    Locator as AsyncLocator,
)
from playwright.sync_api import Response as SyncPlaywrightResponse
from playwright.async_api import Response as AsyncPlaywrightResponse
from rebrowser_playwright.sync_api import sync_playwright as sync_rebrowser_playwright
from rebrowser_playwright.async_api import (
    async_playwright as async_rebrowser_playwright,
)

from scrapling.core.utils import log
from ._page import PageInfo, PagePool
from ._validators import validate, PlaywrightConfig
from ._config_tools import _compiled_stealth_scripts, _launch_kwargs, _context_kwargs
from scrapling.core._types import (
    Dict,
    Optional,
    Union,
    Iterable,
    Callable,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt import (
    Response,
    ResponseFactory,
    generate_convincing_referer,
    intercept_route,
    async_intercept_route,
)


class DynamicSession:
    """A Browser session manager with page pooling."""

    __slots__ = (
        "max_pages",
        "headless",
        "hide_canvas",
        "disable_webgl",
        "real_chrome",
        "stealth",
        "google_search",
        "proxy",
        "locale",
        "extra_headers",
        "useragent",
        "timeout",
        "cookies",
        "disable_resources",
        "network_idle",
        "wait_selector",
        "wait_selector_state",
        "wait",
        "playwright",
        "browser",
        "context",
        "page_pool",
        "_closed",
        "adaptor_arguments",
        "page_action",
        "launch_options",
        "context_options",
        "cdp_url",
    )

    def __init__(
        self,
        max_pages: int = 1,
        headless: bool = True,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: Union[int, float] = 0,
        page_action: Optional[Callable] = None,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: Union[int, float] = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Optional[Iterable[Dict]] = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        adaptor_arguments: Optional[Dict] = None,
    ):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        """

        params = {
            "max_pages": max_pages,
            "headless": headless,
            "google_search": google_search,
            "hide_canvas": hide_canvas,
            "disable_webgl": disable_webgl,
            "real_chrome": real_chrome,
            "stealth": stealth,
            "wait": wait,
            "page_action": page_action,
            "proxy": proxy,
            "locale": locale,
            "extra_headers": extra_headers,
            "useragent": useragent,
            "timeout": timeout,
            "adaptor_arguments": adaptor_arguments,
            "disable_resources": disable_resources,
            "wait_selector": wait_selector,
            "cookies": cookies,
            "network_idle": network_idle,
            "wait_selector_state": wait_selector_state,
            "cdp_url": cdp_url,
        }
        config = validate(params, PlaywrightConfig)

        self.max_pages = config.max_pages
        self.headless = config.headless
        self.hide_canvas = config.hide_canvas
        self.disable_webgl = config.disable_webgl
        self.real_chrome = config.real_chrome
        self.stealth = config.stealth
        self.google_search = config.google_search
        self.wait = config.wait
        self.proxy = config.proxy
        self.locale = config.locale
        self.extra_headers = config.extra_headers
        self.useragent = config.useragent
        self.timeout = config.timeout
        self.cookies = list(config.cookies) if config.cookies else []
        self.disable_resources = config.disable_resources
        self.cdp_url = config.cdp_url
        self.network_idle = config.network_idle
        self.wait_selector = config.wait_selector
        self.wait_selector_state = config.wait_selector_state

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Union[BrowserType, Browser]] = None
        self.context: Optional[BrowserContext] = None
        self.page_pool = PagePool(self.max_pages)
        self._closed = False
        self.adaptor_arguments = config.adaptor_arguments or {}
        self.page_action = config.page_action
        self.__initiate_browser_options__()

    def __initiate_browser_options__(self):
        self.launch_options = dict(
            _launch_kwargs(
                self.headless,
                self.real_chrome,
                self.stealth,
                self.hide_canvas,
                self.disable_webgl,
            )
        )
        self.context_options = dict(
            _context_kwargs(
                self.proxy,
                self.locale,
                tuple(self.extra_headers.items()) if self.extra_headers else tuple(),
                self.useragent,
                self.stealth,
            )
        )
        self.context_options["extra_http_headers"] = dict(
            self.context_options["extra_http_headers"]
        )
        self.context_options["proxy"] = dict(self.context_options["proxy"]) or None

    def __create__(self):
        """Create a browser for this instance and context."""
        sync_context = sync_rebrowser_playwright
        if not self.stealth or self.real_chrome:
            # Because rebrowser_playwright doesn't play well with real browsers
            sync_context = sync_playwright

        self.playwright = sync_context().start()

        browser_launcher = getattr(
            self.playwright, "chrome" if self.real_chrome else "chromium"
        )
        if self.cdp_url:
            self.browser = browser_launcher.connect_over_cdp(endpoint_url=self.cdp_url)
        else:
            self.browser = browser_launcher.launch(**self.launch_options)

        self.context = self.browser.new_context(**self.context_options)
        if self.cookies:
            self.context.add_cookies(self.cookies)

    def __enter__(self):
        self.__create__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close all resources"""
        if self._closed:
            return

        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self._closed = True

    def _get_or_create_page(self) -> PageInfo:
        """Get an available page or create a new one"""
        # Try to get a ready page first
        page_info = self.page_pool.get_ready_page()
        if page_info:
            return page_info

        # Create a new page if under limit
        if self.page_pool.pages_count < self.max_pages:
            page = self.context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            if self.extra_headers:
                page.set_extra_http_headers(self.extra_headers)

            if self.disable_resources:
                page.route("**/*", intercept_route)

            if self.stealth:
                for script in _compiled_stealth_scripts():
                    page.add_init_script(path=script)

            return self.page_pool.add_page(page)

        # Wait for a page to become available
        max_wait = 30
        start_time = time.time()

        while time.time() - start_time < max_wait:
            page_info = self.page_pool.get_ready_page()
            if page_info:
                return page_info
            time.sleep(0.05)

        raise TimeoutError("No pages available within timeout period")

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :return: A `Response` object.
        """
        if self._closed:
            raise RuntimeError("Context manager has been closed")

        final_response = None
        referer = generate_convincing_referer(url) if self.google_search else None

        def handle_response(finished_response: SyncPlaywrightResponse):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        page_info = self._get_or_create_page()
        page_info.mark_busy(url=url)

        try:
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = page_info.page.goto(url, referer=referer)
            page_info.page.wait_for_load_state(state="domcontentloaded")

            if self.network_idle:
                page_info.page.wait_for_load_state("networkidle")

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if self.page_action is not None:
                try:
                    page_info.page = self.page_action(page_info.page)
                except Exception as e:
                    log.error(f"Error executing page_action: {e}")

            if self.wait_selector:
                try:
                    waiter: Locator = page_info.page.locator(self.wait_selector)
                    waiter.first.wait_for(state=self.wait_selector_state)
                    # Wait again after waiting for the selector, helpful with protections like Cloudflare
                    page_info.page.wait_for_load_state(state="load")
                    page_info.page.wait_for_load_state(state="domcontentloaded")
                    if self.network_idle:
                        page_info.page.wait_for_load_state("networkidle")
                except Exception as e:
                    log.error(f"Error waiting for selector {self.wait_selector}: {e}")

            page_info.page.wait_for_timeout(self.wait)

            # Create response object
            response = ResponseFactory.from_playwright_response(
                page_info.page, first_response, final_response, self.adaptor_arguments
            )

            # Mark the page as ready for next use
            page_info.mark_ready()

            return response

        except Exception as e:
            page_info.mark_error()
            raise e

    def get_pool_stats(self) -> Dict[str, int]:
        """Get statistics about the current page pool"""
        return {
            "total_pages": self.page_pool.pages_count,
            "ready_pages": self.page_pool.ready_count,
            "busy_pages": self.page_pool.busy_count,
            "max_pages": self.max_pages,
        }


class AsyncDynamicSession(DynamicSession):
    """A Browser session manager with page pooling"""

    def __init__(
        self,
        max_pages: int = 1,
        headless: bool = True,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: Union[int, float] = 0,
        page_action: Optional[Callable] = None,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: Union[int, float] = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Optional[Iterable[Dict]] = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        adaptor_arguments: Optional[Dict] = None,
    ):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        """

        super().__init__(
            max_pages,
            headless,
            google_search,
            hide_canvas,
            disable_webgl,
            real_chrome,
            stealth,
            wait,
            page_action,
            proxy,
            locale,
            extra_headers,
            useragent,
            cdp_url,
            timeout,
            disable_resources,
            wait_selector,
            cookies,
            network_idle,
            wait_selector_state,
            adaptor_arguments,
        )

        self.playwright: Optional[AsyncPlaywright] = None
        self.browser: Optional[Union[AsyncBrowserType, AsyncBrowser]] = None
        self.context: Optional[AsyncBrowserContext] = None
        self._lock = asyncio.Lock()
        self.__enter__ = None
        self.__exit__ = None

    async def __create__(self):
        """Create a browser for this instance and context."""
        async_context = async_rebrowser_playwright
        if not self.stealth or self.real_chrome:
            # Because rebrowser_playwright doesn't play well with real browsers
            async_context = async_playwright

        self.playwright: AsyncPlaywright = await async_context().start()

        browser_launcher: AsyncBrowserType = getattr(
            self.playwright, "chrome" if self.real_chrome else "chromium"
        )
        if self.cdp_url:
            self.browser = await browser_launcher.connect_over_cdp(
                endpoint_url=self.cdp_url
            )
        else:
            self.browser = await browser_launcher.launch(**self.launch_options)

        self.context: AsyncBrowserContext = await self.browser.new_context(
            **self.context_options
        )

        if self.cookies:
            await self.context.add_cookies(self.cookies)

    async def __aenter__(self):
        await self.__create__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close all resources"""
        if self._closed:
            return

        if self.context:
            await self.context.close()
            self.context = None

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        self._closed = True

    async def _get_or_create_page(self) -> PageInfo:
        """Get an available page or create a new one"""
        async with self._lock:
            # Try to get a ready page first
            page_info = self.page_pool.get_ready_page()
            if page_info:
                return page_info

            # Create a new page if under limit
            if self.page_pool.pages_count < self.max_pages:
                page = await self.context.new_page()
                page.set_default_navigation_timeout(self.timeout)
                page.set_default_timeout(self.timeout)
                if self.extra_headers:
                    await page.set_extra_http_headers(self.extra_headers)

                if self.disable_resources:
                    await page.route("**/*", async_intercept_route)

                if self.stealth:
                    for script in _compiled_stealth_scripts():
                        await page.add_init_script(path=script)

                return self.page_pool.add_page(page)

        # Wait for a page to become available
        max_wait = 30  # seconds
        start_time = time.time()

        while time.time() - start_time < max_wait:
            page_info = self.page_pool.get_ready_page()
            if page_info:
                return page_info
            await asyncio.sleep(0.05)

        raise TimeoutError("No pages available within timeout period")

    async def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :return: A `Response` object.
        """
        if self._closed:
            raise RuntimeError("Context manager has been closed")

        final_response = None
        referer = generate_convincing_referer(url) if self.google_search else None

        async def handle_response(finished_response: AsyncPlaywrightResponse):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        page_info = await self._get_or_create_page()
        page_info.mark_busy(url=url)

        try:
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = await page_info.page.goto(url, referer=referer)
            await page_info.page.wait_for_load_state(state="domcontentloaded")

            if self.network_idle:
                await page_info.page.wait_for_load_state("networkidle")

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if self.page_action is not None:
                try:
                    page_info.page = await self.page_action(page_info.page)
                except Exception as e:
                    log.error(f"Error executing page_action: {e}")

            if self.wait_selector:
                try:
                    waiter: AsyncLocator = page_info.page.locator(self.wait_selector)
                    await waiter.first.wait_for(state=self.wait_selector_state)
                    # Wait again after waiting for the selector, helpful with protections like Cloudflare
                    await page_info.page.wait_for_load_state(state="load")
                    await page_info.page.wait_for_load_state(state="domcontentloaded")
                    if self.network_idle:
                        await page_info.page.wait_for_load_state("networkidle")
                except Exception as e:
                    log.error(f"Error waiting for selector {self.wait_selector}: {e}")

            await page_info.page.wait_for_timeout(self.wait)

            # Create response object
            response = await ResponseFactory.from_async_playwright_response(
                page_info.page, first_response, final_response, self.adaptor_arguments
            )

            # Mark the page as ready for next use
            page_info.mark_ready()

            return response

        except Exception as e:
            page_info.mark_error()
            raise e
