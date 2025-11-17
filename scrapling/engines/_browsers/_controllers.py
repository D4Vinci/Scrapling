from playwright.sync_api import (
    Locator,
    Playwright,
    sync_playwright,
)
from playwright.async_api import (
    async_playwright,
    Locator as AsyncLocator,
    Playwright as AsyncPlaywright,
    BrowserContext as AsyncBrowserContext,
)
from patchright.sync_api import sync_playwright as sync_patchright
from patchright.async_api import async_playwright as async_patchright

from scrapling.core.utils import log
from ._base import SyncSession, AsyncSession, DynamicSessionMixin
from ._validators import validate_fetch as _validate, PlaywrightConfig
from scrapling.core._types import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    TYPE_CHECKING,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt.convertor import (
    Response,
    ResponseFactory,
)
from scrapling.engines.toolbelt.fingerprints import generate_convincing_referer

_UNSET: Any = object()


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
        user_data_dir: str = "",
        extra_flags: Optional[List[str]] = None,
        selector_config: Optional[Dict] = None,
        additional_args: Optional[Dict] = None,
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
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param user_data_dir: Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory.
        :param extra_flags: A list of additional browser flags to pass to the browser on launch.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
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
            user_data_dir=user_data_dir,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            extra_flags=extra_flags,
            selector_config=selector_config,
            additional_args=additional_args,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        super().__init__(max_pages=self.max_pages)

    def __create__(self):
        """Create a browser for this instance and context."""
        sync_context = sync_patchright if self.stealth else sync_playwright

        self.playwright: Playwright = sync_context().start()  # pyright: ignore [reportAttributeAccessIssue]

        if self.cdp_url:  # pragma: no cover
            self.context = self.playwright.chromium.connect_over_cdp(endpoint_url=self.cdp_url).new_context(
                **self.context_options
            )
        else:
            self.context = self.playwright.chromium.launch_persistent_context(**self.launch_options)

        if self.init_script:  # pragma: no cover
            self.context.add_init_script(path=self.init_script)

        if self.cookies:  # pragma: no cover
            self.context.add_cookies(self.cookies)

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
        params = _validate(
            [
                ("google_search", google_search, self.google_search),
                ("timeout", timeout, self.timeout),
                ("wait", wait, self.wait),
                ("page_action", page_action, self.page_action),
                ("extra_headers", extra_headers, self.extra_headers),
                ("disable_resources", disable_resources, self.disable_resources),
                ("wait_selector", wait_selector, self.wait_selector),
                ("wait_selector_state", wait_selector_state, self.wait_selector_state),
                ("network_idle", network_idle, self.network_idle),
                ("load_dom", load_dom, self.load_dom),
                ("selector_config", selector_config, self.selector_config),
            ],
            PlaywrightConfig,
            _UNSET,
        )

        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        referer = (
            generate_convincing_referer(url) if (params.google_search and "referer" not in self._headers_keys) else None
        )

        page_info = self._get_page(params.timeout, params.extra_headers, params.disable_resources)
        final_response = [None]
        handle_response = self._create_response_handler(page_info, final_response)

        try:  # pragma: no cover
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = page_info.page.goto(url, referer=referer)
            self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)

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
                    self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)
                except Exception as e:  # pragma: no cover
                    log.error(f"Error waiting for selector {params.wait_selector}: {e}")

            page_info.page.wait_for_timeout(params.wait)

            # Create response object
            response = ResponseFactory.from_playwright_response(
                page_info.page, first_response, final_response[0], params.selector_config
            )

            # Close the page to free up resources
            page_info.page.close()
            self.page_pool.pages.remove(page_info)

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
        user_data_dir: str = "",
        extra_flags: Optional[List[str]] = None,
        selector_config: Optional[Dict] = None,
        additional_args: Optional[Dict] = None,
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
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param user_data_dir: Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory.
        :param extra_flags: A list of additional browser flags to pass to the browser on launch.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
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
            user_data_dir=user_data_dir,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            extra_flags=extra_flags,
            selector_config=selector_config,
            additional_args=additional_args,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        super().__init__(max_pages=self.max_pages)

    async def __create__(self):
        """Create a browser for this instance and context."""
        async_context = async_patchright if self.stealth else async_playwright

        self.playwright: AsyncPlaywright = await async_context().start()  # pyright: ignore [reportAttributeAccessIssue]

        if self.cdp_url:
            browser = await self.playwright.chromium.connect_over_cdp(endpoint_url=self.cdp_url)
            self.context: AsyncBrowserContext = await browser.new_context(**self.context_options)
        else:
            self.context: AsyncBrowserContext = await self.playwright.chromium.launch_persistent_context(
                **self.launch_options
            )

        if self.init_script:  # pragma: no cover
            await self.context.add_init_script(path=self.init_script)

        if self.cookies:
            await self.context.add_cookies(self.cookies)  # pyright: ignore

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
        params = _validate(
            [
                ("google_search", google_search, self.google_search),
                ("timeout", timeout, self.timeout),
                ("wait", wait, self.wait),
                ("page_action", page_action, self.page_action),
                ("extra_headers", extra_headers, self.extra_headers),
                ("disable_resources", disable_resources, self.disable_resources),
                ("wait_selector", wait_selector, self.wait_selector),
                ("wait_selector_state", wait_selector_state, self.wait_selector_state),
                ("network_idle", network_idle, self.network_idle),
                ("load_dom", load_dom, self.load_dom),
                ("selector_config", selector_config, self.selector_config),
            ],
            PlaywrightConfig,
            _UNSET,
        )

        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        referer = (
            generate_convincing_referer(url) if (params.google_search and "referer" not in self._headers_keys) else None
        )

        page_info = await self._get_page(params.timeout, params.extra_headers, params.disable_resources)
        final_response = [None]
        handle_response = self._create_response_handler(page_info, final_response)

        if TYPE_CHECKING:
            from playwright.async_api import Page as async_Page

            if not isinstance(page_info.page, async_Page):
                raise TypeError

        try:
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = await page_info.page.goto(url, referer=referer)
            await self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)

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
                    await self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)
                except Exception as e:
                    log.error(f"Error waiting for selector {params.wait_selector}: {e}")

            await page_info.page.wait_for_timeout(params.wait)

            # Create response object
            response = await ResponseFactory.from_async_playwright_response(
                page_info.page, first_response, final_response[0], params.selector_config
            )

            # Close the page to free up resources
            await page_info.page.close()
            self.page_pool.pages.remove(page_info)
            return response

        except Exception as e:  # pragma: no cover
            page_info.mark_error()
            raise e
