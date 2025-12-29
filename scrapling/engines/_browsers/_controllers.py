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

from scrapling.core.utils import log
from scrapling.core._types import Unpack, TYPE_CHECKING
from ._types import PlaywrightSession, PlaywrightFetchParams
from ._base import SyncSession, AsyncSession, DynamicSessionMixin
from ._validators import validate_fetch as _validate, PlaywrightConfig
from scrapling.engines.toolbelt.convertor import Response, ResponseFactory
from scrapling.engines.toolbelt.fingerprints import generate_convincing_referer


class DynamicSession(SyncSession, DynamicSessionMixin):
    """A Browser session manager with page pooling."""

    __slots__ = (
        "_config",
        "_context_options",
        "_launch_options",
        "max_pages",
        "page_pool",
        "_max_wait_for_page",
        "playwright",
        "context",
        "_closed",
    )

    def __init__(self, **kwargs: Unpack[PlaywrightSession]):
        """A Browser session manager with page pooling, it's using a persistent browser Context by default with a temporary user profile directory.

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
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
            self.playwright: Playwright = sync_playwright().start()  # pyright: ignore [reportAttributeAccessIssue]

            if self._config.cdp_url:  # pragma: no cover
                browser = self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url)
                self.context = browser.new_context(**self._context_options)
            else:
                self.context = self.playwright.chromium.launch_persistent_context(**self._launch_options)

            if self._config.init_script:  # pragma: no cover
                self.context.add_init_script(path=self._config.init_script)

            if self._config.cookies:  # pragma: no cover
                self.context.add_cookies(self._config.cookies)
        else:
            raise RuntimeError("Session has been already started")

    def fetch(self, url: str, **kwargs: Unpack[PlaywrightFetchParams]) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param kwargs: Additional keyword arguments including:
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
            - disable_resources: Drop requests for unnecessary resources for a speed boost.
                Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :return: A `Response` object.
        """
        params = _validate(kwargs, self, PlaywrightConfig)
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


class AsyncDynamicSession(AsyncSession, DynamicSessionMixin):
    """An async Browser session manager with page pooling, it's using a persistent browser Context by default with a temporary user profile directory."""

    def __init__(self, **kwargs: Unpack[PlaywrightSession]):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
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
            self.playwright: AsyncPlaywright = await async_playwright().start()  # pyright: ignore [reportAttributeAccessIssue]

            if self._config.cdp_url:
                browser = await self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url)
                self.context: AsyncBrowserContext = await browser.new_context(**self._context_options)
            else:
                self.context: AsyncBrowserContext = await self.playwright.chromium.launch_persistent_context(
                    **self._launch_options
                )

            if self._config.init_script:  # pragma: no cover
                await self.context.add_init_script(path=self._config.init_script)

            if self._config.cookies:
                await self.context.add_cookies(self._config.cookies)  # pyright: ignore
        else:
            raise RuntimeError("Session has been already started")

    async def fetch(self, url: str, **kwargs: Unpack[PlaywrightFetchParams]) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param kwargs: Additional keyword arguments including:
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
            - disable_resources: Drop requests for unnecessary resources for a speed boost.
                Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :return: A `Response` object.
        """
        params = _validate(kwargs, self, PlaywrightConfig)

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
