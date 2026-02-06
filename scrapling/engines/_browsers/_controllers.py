from time import sleep as time_sleep
from asyncio import sleep as asyncio_sleep

from playwright.sync_api import (
    Locator,
    sync_playwright,
)
from playwright.async_api import (
    async_playwright,
    Locator as AsyncLocator,
    BrowserContext as AsyncBrowserContext,
)

from scrapling.core.utils import log
from scrapling.core._types import Unpack
from scrapling.engines.toolbelt.proxy_rotation import is_proxy_error
from scrapling.engines.toolbelt.convertor import Response, ResponseFactory
from scrapling.engines.toolbelt.fingerprints import generate_convincing_referer
from scrapling.engines._browsers._types import PlaywrightSession, PlaywrightFetchParams
from scrapling.engines._browsers._base import SyncSession, AsyncSession, DynamicSessionMixin
from scrapling.engines._browsers._validators import validate_fetch as _validate, PlaywrightConfig


class DynamicSession(SyncSession, DynamicSessionMixin):
    """A Browser session manager with page pooling."""

    __slots__ = (
        "_config",
        "_context_options",
        "_browser_options",
        "_user_data_dir",
        "_headers_keys",
        "max_pages",
        "page_pool",
        "_max_wait_for_page",
        "playwright",
        "context",
    )

    def __init__(self, **kwargs: Unpack[PlaywrightSession]):
        """A Browser session manager with page pooling, it's using a persistent browser Context by default with a temporary user profile directory.

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param blocked_domains: A set of domain names to block requests to. Subdomains are also matched (e.g., ``"example.com"`` blocks ``"sub.example.com"`` too).
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system default locale.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
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
        self.__validate__(**kwargs)
        super().__init__()

    def start(self):
        """Create a browser for this instance and context."""
        if not self.playwright:
            self.playwright = sync_playwright().start()

            try:
                if self._config.cdp_url:  # pragma: no cover
                    self.browser = self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url)
                    if not self._config.proxy_rotator and self.browser:
                        self.context = self.browser.new_context(**self._context_options)
                elif self._config.proxy_rotator:
                    self.browser = self.playwright.chromium.launch(**self._browser_options)
                else:
                    persistent_options = (
                        self._browser_options | self._context_options | {"user_data_dir": self._user_data_dir}
                    )
                    self.context = self.playwright.chromium.launch_persistent_context(**persistent_options)

                if self.context:
                    self.context = self._initialize_context(self._config, self.context)

                self._is_alive = True
            except Exception:
                # Clean up playwright if browser setup fails
                self.playwright.stop()
                self.playwright = None
                raise
        else:
            raise RuntimeError("Session has been already started")

    def fetch(self, url: str, **kwargs: Unpack[PlaywrightFetchParams]) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param blocked_domains: A set of domain names to block requests to. Subdomains are also matched (e.g., ``"example.com"`` blocks ``"sub.example.com"`` too).
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param proxy: Static proxy to override rotator and session proxy. A new browser context will be created and used with it.
        :return: A `Response` object.
        """
        static_proxy = kwargs.pop("proxy", None)

        params = _validate(kwargs, self, PlaywrightConfig)
        if not self._is_alive:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        request_headers_keys = {h.lower() for h in params.extra_headers.keys()} if params.extra_headers else set()
        referer = (
            generate_convincing_referer(url)
            if (params.google_search and "referer" not in request_headers_keys)
            else None
        )

        for attempt in range(self._config.retries):
            if self._config.proxy_rotator and static_proxy is None:
                proxy = self._config.proxy_rotator.get_proxy()
            else:
                proxy = static_proxy

            with self._page_generator(
                params.timeout, params.extra_headers, params.disable_resources, proxy, params.blocked_domains
            ) as page_info:
                final_response = [None]
                page = page_info.page
                page.on("response", self._create_response_handler(page_info, final_response))

                try:
                    first_response = page.goto(url, referer=referer)
                    self._wait_for_page_stability(page, params.load_dom, params.network_idle)

                    if not first_response:
                        raise RuntimeError(f"Failed to get response for {url}")

                    if params.page_action:
                        try:
                            _ = params.page_action(page)
                        except Exception as e:  # pragma: no cover
                            log.error(f"Error executing page_action: {e}")

                    if params.wait_selector:
                        try:
                            waiter: Locator = page.locator(params.wait_selector)
                            waiter.first.wait_for(state=params.wait_selector_state)
                            self._wait_for_page_stability(page, params.load_dom, params.network_idle)
                        except Exception as e:  # pragma: no cover
                            log.error(f"Error waiting for selector {params.wait_selector}: {e}")

                    page.wait_for_timeout(params.wait)

                    response = ResponseFactory.from_playwright_response(
                        page, first_response, final_response[0], params.selector_config, meta={"proxy": proxy}
                    )
                    return response

                except Exception as e:
                    page_info.mark_error()
                    if attempt < self._config.retries - 1:
                        if is_proxy_error(e):
                            log.warning(
                                f"Proxy '{proxy}' failed (attempt {attempt + 1}) | Retrying in {self._config.retry_delay}s..."
                            )
                        else:
                            log.warning(
                                f"Attempt {attempt + 1} failed: {e}. Retrying in {self._config.retry_delay}s..."
                            )
                        time_sleep(self._config.retry_delay)
                    else:
                        log.error(f"Failed after {self._config.retries} attempts: {e}")
                        raise

        raise RuntimeError("Request failed")  # pragma: no cover


class AsyncDynamicSession(AsyncSession, DynamicSessionMixin):
    """An async Browser session manager with page pooling, it's using a persistent browser Context by default with a temporary user profile directory."""

    __slots__ = (
        "_config",
        "_context_options",
        "_browser_options",
        "_user_data_dir",
        "_headers_keys",
    )

    def __init__(self, **kwargs: Unpack[PlaywrightSession]):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param blocked_domains: A set of domain names to block requests to. Subdomains are also matched (e.g., ``"example.com"`` blocks ``"sub.example.com"`` too).
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
            rules. Defaults to the system default locale.
        :param timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
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
        self.__validate__(**kwargs)
        super().__init__(max_pages=self._config.max_pages)

    async def start(self):
        """Create a browser for this instance and context."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            try:
                if self._config.cdp_url:
                    self.browser = await self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url)
                    if not self._config.proxy_rotator and self.browser:
                        self.context: AsyncBrowserContext = await self.browser.new_context(**self._context_options)
                elif self._config.proxy_rotator:
                    self.browser = await self.playwright.chromium.launch(**self._browser_options)
                else:
                    persistent_options = (
                        self._browser_options | self._context_options | {"user_data_dir": self._user_data_dir}
                    )
                    self.context: AsyncBrowserContext = await self.playwright.chromium.launch_persistent_context(
                        **persistent_options
                    )

                if self.context:
                    self.context = await self._initialize_context(self._config, self.context)

                self._is_alive = True
            except Exception:
                # Clean up playwright if browser setup fails
                await self.playwright.stop()
                self.playwright = None
                raise
        else:
            raise RuntimeError("Session has been already started")

    async def fetch(self, url: str, **kwargs: Unpack[PlaywrightFetchParams]) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
        :param blocked_domains: A set of domain names to block requests to. Subdomains are also matched (e.g., ``"example.com"`` blocks ``"sub.example.com"`` too).
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param proxy: Static proxy to override rotator and session proxy. A new browser context will be created and used with it.
        :return: A `Response` object.
        """
        static_proxy = kwargs.pop("proxy", None)

        params = _validate(kwargs, self, PlaywrightConfig)

        if not self._is_alive:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        request_headers_keys = {h.lower() for h in params.extra_headers.keys()} if params.extra_headers else set()
        referer = (
            generate_convincing_referer(url)
            if (params.google_search and "referer" not in request_headers_keys)
            else None
        )

        for attempt in range(self._config.retries):
            if self._config.proxy_rotator and static_proxy is None:
                proxy = self._config.proxy_rotator.get_proxy()
            else:
                proxy = static_proxy

            async with self._page_generator(
                params.timeout, params.extra_headers, params.disable_resources, proxy, params.blocked_domains
            ) as page_info:
                final_response = [None]
                page = page_info.page
                page.on("response", self._create_response_handler(page_info, final_response))

                try:
                    first_response = await page.goto(url, referer=referer)
                    await self._wait_for_page_stability(page, params.load_dom, params.network_idle)

                    if not first_response:
                        raise RuntimeError(f"Failed to get response for {url}")

                    if params.page_action:
                        try:
                            _ = await params.page_action(page)
                        except Exception as e:  # pragma: no cover
                            log.error(f"Error executing page_action: {e}")

                    if params.wait_selector:
                        try:
                            waiter: AsyncLocator = page.locator(params.wait_selector)
                            await waiter.first.wait_for(state=params.wait_selector_state)
                            await self._wait_for_page_stability(page, params.load_dom, params.network_idle)
                        except Exception as e:  # pragma: no cover
                            log.error(f"Error waiting for selector {params.wait_selector}: {e}")

                    await page.wait_for_timeout(params.wait)

                    response = await ResponseFactory.from_async_playwright_response(
                        page, first_response, final_response[0], params.selector_config, meta={"proxy": proxy}
                    )
                    return response

                except Exception as e:
                    page_info.mark_error()
                    if attempt < self._config.retries - 1:
                        if is_proxy_error(e):
                            log.warning(
                                f"Proxy '{proxy}' failed (attempt {attempt + 1}) | Retrying in {self._config.retry_delay}s..."
                            )
                        else:
                            log.warning(
                                f"Attempt {attempt + 1} failed: {e}. Retrying in {self._config.retry_delay}s..."
                            )
                        await asyncio_sleep(self._config.retry_delay)
                    else:
                        log.error(f"Failed after {self._config.retries} attempts: {e}")
                        raise

        raise RuntimeError("Request failed")  # pragma: no cover
