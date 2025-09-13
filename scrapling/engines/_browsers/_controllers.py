from playwright.sync_api import (
    Response as SyncPlaywrightResponse,
    sync_playwright,
    Playwright,
    Locator,
)
from playwright.async_api import (
    async_playwright,
    Response as AsyncPlaywrightResponse,
    BrowserContext as AsyncBrowserContext,
    Playwright as AsyncPlaywright,
    Locator as AsyncLocator,
)
from rebrowser_playwright.sync_api import sync_playwright as sync_rebrowser_playwright
from rebrowser_playwright.async_api import (
    async_playwright as async_rebrowser_playwright,
)

from scrapling.core.utils import log
from ._base import SyncSession, AsyncSession, DynamicSessionMixin
from ._validators import validate, PlaywrightConfig
from scrapling.core._types import (
    Dict,
    List,
    Optional,
    Callable,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt.convertor import (
    Response,
    ResponseFactory,
)
from scrapling.engines.toolbelt.fingerprints import generate_convincing_referer

_UNSET = object()


class DynamicSession(DynamicSessionMixin, SyncSession):
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
        "load_dom",
        "wait_selector",
        "init_script",
        "wait_selector_state",
        "wait",
        "playwright",
        "browser",
        "context",
        "page_pool",
        "_closed",
        "selector_config",
        "page_action",
        "launch_options",
        "context_options",
        "cdp_url",
        "_headers_keys",
    )

    def __init__(
        self,
        __max_pages: int = 1,
        headless: bool = True,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: int | float = 0,
        page_action: Optional[Callable] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        cookies: Optional[List[Dict]] = None,
        network_idle: bool = False,
        load_dom: bool = True,
        wait_selector_state: SelectorWaitStates = "attached",
        selector_config: Optional[Dict] = None,
    ):
        """A Browser session manager with page pooling, it's using a persistent browser Context by default with a temporary user profile directory.

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        """
        self.__validate__(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            cookies=cookies,
            load_dom=load_dom,
            headless=headless,
            useragent=useragent,
            max_pages=__max_pages,
            real_chrome=real_chrome,
            page_action=page_action,
            hide_canvas=hide_canvas,
            init_script=init_script,
            network_idle=network_idle,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            selector_config=selector_config,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        super().__init__(max_pages=self.max_pages)

    def __create__(self):
        """Create a browser for this instance and context."""
        sync_context = sync_rebrowser_playwright
        if not self.stealth or self.real_chrome:
            # Because rebrowser_playwright doesn't play well with real browsers
            sync_context = sync_playwright

        self.playwright: Playwright = sync_context().start()

        if self.cdp_url:  # pragma: no cover
            self.context = self.playwright.chromium.connect_over_cdp(endpoint_url=self.cdp_url).new_context(
                **self.context_options
            )
        else:
            self.context = self.playwright.chromium.launch_persistent_context(user_data_dir="", **self.launch_options)

        # Get the default page and close it
        default_page = self.context.pages[0]
        default_page.close()

        if self.init_script:  # pragma: no cover
            self.context.add_init_script(path=self.init_script)

        if self.cookies:  # pragma: no cover
            self.context.add_cookies(self.cookies)

    def __enter__(self):
        self.__create__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):  # pragma: no cover
        """Close all resources"""
        if self._closed:
            return

        if self.context:
            self.context.close()
            self.context = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self._closed = True

    def fetch(
        self,
        url: str,
        google_search: bool = _UNSET,
        timeout: int | float = _UNSET,
        wait: int | float = _UNSET,
        page_action: Optional[Callable] = _UNSET,
        extra_headers: Optional[Dict[str, str]] = _UNSET,
        disable_resources: bool = _UNSET,
        wait_selector: Optional[str] = _UNSET,
        wait_selector_state: SelectorWaitStates = _UNSET,
        network_idle: bool = _UNSET,
        load_dom: bool = _UNSET,
        selector_config: Optional[Dict] = _UNSET,
    ) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :return: A `Response` object.
        """
        # Validate all resolved parameters
        params = validate(
            dict(
                google_search=self._get_with_precedence(google_search, self.google_search, _UNSET),
                timeout=self._get_with_precedence(timeout, self.timeout, _UNSET),
                wait=self._get_with_precedence(wait, self.wait, _UNSET),
                page_action=self._get_with_precedence(page_action, self.page_action, _UNSET),
                extra_headers=self._get_with_precedence(extra_headers, self.extra_headers, _UNSET),
                disable_resources=self._get_with_precedence(disable_resources, self.disable_resources, _UNSET),
                wait_selector=self._get_with_precedence(wait_selector, self.wait_selector, _UNSET),
                wait_selector_state=self._get_with_precedence(wait_selector_state, self.wait_selector_state, _UNSET),
                network_idle=self._get_with_precedence(network_idle, self.network_idle, _UNSET),
                load_dom=self._get_with_precedence(load_dom, self.load_dom, _UNSET),
                selector_config=self._get_with_precedence(selector_config, self.selector_config, _UNSET),
            ),
            PlaywrightConfig,
        )

        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        final_response = None
        referer = (
            generate_convincing_referer(url) if (params.google_search and "referer" not in self._headers_keys) else None
        )

        def handle_response(finished_response: SyncPlaywrightResponse):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        page_info = self._get_page(params.timeout, params.extra_headers, params.disable_resources)
        page_info.mark_busy(url=url)

        try:  # pragma: no cover
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = page_info.page.goto(url, referer=referer)
            if params.load_dom:
                page_info.page.wait_for_load_state(state="domcontentloaded")

            if params.network_idle:
                page_info.page.wait_for_load_state("networkidle")

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if params.page_action:
                try:
                    _ = params.page_action(page_info.page)
                except Exception as e:  # pragma: no cover
                    log.error(f"Error executing page_action: {e}")

            if params.wait_selector:
                try:
                    waiter: Locator = page_info.page.locator(params.wait_selector)
                    waiter.first.wait_for(state=params.wait_selector_state)
                    # Wait again after waiting for the selector, helpful with protections like Cloudflare
                    page_info.page.wait_for_load_state(state="load")
                    if params.load_dom:
                        page_info.page.wait_for_load_state(state="domcontentloaded")
                    if params.network_idle:
                        page_info.page.wait_for_load_state("networkidle")
                except Exception as e:  # pragma: no cover
                    log.error(f"Error waiting for selector {params.wait_selector}: {e}")

            page_info.page.wait_for_timeout(params.wait)

            # Create response object
            response = ResponseFactory.from_playwright_response(
                page_info.page, first_response, final_response, params.selector_config
            )

            # Mark the page as finished for next use
            page_info.mark_finished()

            return response

        except Exception as e:
            page_info.mark_error()
            raise e


class AsyncDynamicSession(DynamicSessionMixin, AsyncSession):
    """An async Browser session manager with page pooling, it's using a persistent browser Context by default with a temporary user profile directory."""

    def __init__(
        self,
        max_pages: int = 1,
        headless: bool = True,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: int | float = 0,
        page_action: Optional[Callable] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        cookies: Optional[List[Dict]] = None,
        network_idle: bool = False,
        load_dom: bool = True,
        wait_selector_state: SelectorWaitStates = "attached",
        selector_config: Optional[Dict] = None,
    ):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        """

        self.__validate__(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            cookies=cookies,
            load_dom=load_dom,
            headless=headless,
            useragent=useragent,
            max_pages=max_pages,
            real_chrome=real_chrome,
            page_action=page_action,
            hide_canvas=hide_canvas,
            init_script=init_script,
            network_idle=network_idle,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            selector_config=selector_config,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        super().__init__(max_pages=self.max_pages)

    async def __create__(self):
        """Create a browser for this instance and context."""
        async_context = async_rebrowser_playwright
        if not self.stealth or self.real_chrome:
            # Because rebrowser_playwright doesn't play well with real browsers
            async_context = async_playwright

        self.playwright: AsyncPlaywright = await async_context().start()

        if self.cdp_url:
            browser = await self.playwright.chromium.connect_over_cdp(endpoint_url=self.cdp_url)
            self.context: AsyncBrowserContext = await browser.new_context(**self.context_options)
        else:
            self.context: AsyncBrowserContext = await self.playwright.chromium.launch_persistent_context(
                user_data_dir="", **self.launch_options
            )

        # Get the default page and close it
        default_page = self.context.pages[0]
        await default_page.close()

        if self.init_script:  # pragma: no cover
            await self.context.add_init_script(path=self.init_script)

        if self.cookies:
            await self.context.add_cookies(self.cookies)

    async def __aenter__(self):
        await self.__create__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close all resources"""
        if self._closed:  # pragma: no cover
            return

        if self.context:
            await self.context.close()
            self.context = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

        self._closed = True

    async def fetch(
        self,
        url: str,
        google_search: bool = _UNSET,
        timeout: int | float = _UNSET,
        wait: int | float = _UNSET,
        page_action: Optional[Callable] = _UNSET,
        extra_headers: Optional[Dict[str, str]] = _UNSET,
        disable_resources: bool = _UNSET,
        wait_selector: Optional[str] = _UNSET,
        wait_selector_state: SelectorWaitStates = _UNSET,
        network_idle: bool = _UNSET,
        load_dom: bool = _UNSET,
        selector_config: Optional[Dict] = _UNSET,
    ) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :return: A `Response` object.
        """
        # Validate all resolved parameters
        params = validate(
            dict(
                google_search=self._get_with_precedence(google_search, self.google_search, _UNSET),
                timeout=self._get_with_precedence(timeout, self.timeout, _UNSET),
                wait=self._get_with_precedence(wait, self.wait, _UNSET),
                page_action=self._get_with_precedence(page_action, self.page_action, _UNSET),
                extra_headers=self._get_with_precedence(extra_headers, self.extra_headers, _UNSET),
                disable_resources=self._get_with_precedence(disable_resources, self.disable_resources, _UNSET),
                wait_selector=self._get_with_precedence(wait_selector, self.wait_selector, _UNSET),
                wait_selector_state=self._get_with_precedence(wait_selector_state, self.wait_selector_state, _UNSET),
                network_idle=self._get_with_precedence(network_idle, self.network_idle, _UNSET),
                load_dom=self._get_with_precedence(load_dom, self.load_dom, _UNSET),
                selector_config=self._get_with_precedence(selector_config, self.selector_config, _UNSET),
            ),
            PlaywrightConfig,
        )

        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        final_response = None
        referer = (
            generate_convincing_referer(url) if (params.google_search and "referer" not in self._headers_keys) else None
        )

        async def handle_response(finished_response: AsyncPlaywrightResponse):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        page_info = await self._get_page(params.timeout, params.extra_headers, params.disable_resources)
        page_info.mark_busy(url=url)

        try:
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = await page_info.page.goto(url, referer=referer)
            if self.load_dom:
                await page_info.page.wait_for_load_state(state="domcontentloaded")

            if params.network_idle:
                await page_info.page.wait_for_load_state("networkidle")

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if params.page_action:
                try:
                    _ = await params.page_action(page_info.page)
                except Exception as e:
                    log.error(f"Error executing page_action: {e}")

            if params.wait_selector:
                try:
                    waiter: AsyncLocator = page_info.page.locator(params.wait_selector)
                    await waiter.first.wait_for(state=params.wait_selector_state)
                    # Wait again after waiting for the selector, helpful with protections like Cloudflare
                    await page_info.page.wait_for_load_state(state="load")
                    if self.load_dom:
                        await page_info.page.wait_for_load_state(state="domcontentloaded")
                    if params.network_idle:
                        await page_info.page.wait_for_load_state("networkidle")
                except Exception as e:
                    log.error(f"Error waiting for selector {params.wait_selector}: {e}")

            await page_info.page.wait_for_timeout(params.wait)

            # Create response object
            response = await ResponseFactory.from_async_playwright_response(
                page_info.page, first_response, final_response, params.selector_config
            )

            # Mark the page as finished for next use
            page_info.mark_finished()

            return response

        except Exception as e:  # pragma: no cover
            page_info.mark_error()
            raise e
