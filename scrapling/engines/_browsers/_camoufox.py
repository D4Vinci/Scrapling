from random import randint
from re import compile as re_compile

from playwright.sync_api import (
    Response as SyncPlaywrightResponse,
    sync_playwright,
    Locator,
    Page,
)
from playwright.async_api import (
    async_playwright,
    Response as AsyncPlaywrightResponse,
    BrowserContext as AsyncBrowserContext,
    Playwright as AsyncPlaywright,
    Locator as AsyncLocator,
    Page as async_Page,
)
from playwright._impl._errors import Error as PlaywrightError

from ._validators import validate_fetch as _validate
from ._base import SyncSession, AsyncSession, StealthySessionMixin
from scrapling.core.utils import log
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

__CF_PATTERN__ = re_compile("challenges.cloudflare.com/cdn-cgi/challenge-platform/.*")
_UNSET: Any = object()


class StealthySession(StealthySessionMixin, SyncSession):
    """A Stealthy session manager with page pooling."""

    __slots__ = (
        "max_pages",
        "headless",
        "block_images",
        "disable_resources",
        "block_webrtc",
        "allow_webgl",
        "network_idle",
        "load_dom",
        "humanize",
        "solve_cloudflare",
        "wait",
        "timeout",
        "page_action",
        "wait_selector",
        "init_script",
        "addons",
        "wait_selector_state",
        "cookies",
        "google_search",
        "extra_headers",
        "proxy",
        "os_randomize",
        "disable_ads",
        "geoip",
        "selector_config",
        "additional_args",
        "playwright",
        "browser",
        "context",
        "page_pool",
        "_closed",
        "launch_options",
        "_headers_keys",
    )

    def __init__(
        self,
        __max_pages: int = 1,
        headless: bool = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
        load_dom: bool = True,
        humanize: bool | float = True,
        solve_cloudflare: bool = False,
        wait: int | float = 0,
        timeout: int | float = 30000,
        page_action: Optional[Callable] = None,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[List[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        user_data_dir: str = "",
        selector_config: Optional[Dict] = None,
        additional_args: Optional[Dict] = None,
    ):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param block_webrtc: Blocks WebRTC entirely.
        :param cookies: Set cookies for the next request.
        :param addons: List of Firefox addons to use. Must be paths to extracted addons.
        :param humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param user_data_dir: Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """

        self.__validate__(
            wait=wait,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            humanize=humanize,
            load_dom=load_dom,
            max_pages=__max_pages,
            disable_ads=disable_ads,
            allow_webgl=allow_webgl,
            page_action=page_action,
            init_script=init_script,
            network_idle=network_idle,
            block_images=block_images,
            block_webrtc=block_webrtc,
            os_randomize=os_randomize,
            user_data_dir=user_data_dir,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            additional_args=additional_args,
            selector_config=selector_config,
            solve_cloudflare=solve_cloudflare,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        super().__init__(max_pages=self.max_pages)

    def __create__(self):
        """Create a browser for this instance and context."""
        self.playwright = sync_playwright().start()
        self.context = self.playwright.firefox.launch_persistent_context(**self.launch_options)

        if self.init_script:  # pragma: no cover
            self.context.add_init_script(path=self.init_script)

        if self.cookies:  # pragma: no cover
            self.context.add_cookies(self.cookies)

    def __enter__(self):  # pragma: no cover
        self.__create__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):  # pragma: no cover
        """Close all resources"""
        if self._closed:  # pragma: no cover
            return

        if self.context:
            self.context.close()
            self.context = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self._closed = True

    @staticmethod
    def _get_page_content(page: Page) -> str:
        """
        A workaround for the Playwright issue with `page.content()` on Windows. Ref.: https://github.com/microsoft/playwright/issues/16108
        :param page: The page to extract content from.
        :return:
        """
        while True:
            try:
                return page.content() or ""
            except PlaywrightError:
                page.wait_for_timeout(1000)
                continue
        return ""  # pyright: ignore

    def _solve_cloudflare(self, page: Page) -> None:  # pragma: no cover
        """Solve the cloudflare challenge displayed on the playwright page passed

        :param page: The targeted page
        :return:
        """
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightError:
            pass
        challenge_type = self._detect_cloudflare(self._get_page_content(page))
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":
                while "<title>Just a moment...</title>" in (self._get_page_content(page)):
                    log.info("Waiting for Cloudflare wait page to disappear.")
                    page.wait_for_timeout(1000)
                    page.wait_for_load_state()
                log.info("Cloudflare captcha is solved")
                return

            else:
                box_selector = "#cf_turnstile div, #cf-turnstile div, .turnstile>div>div"
                if challenge_type != "embedded":
                    box_selector = ".main-content p+div>div>div"
                    while "Verifying you are human." in self._get_page_content(page):
                        # Waiting for the verify spinner to disappear, checking every 1s if it disappeared
                        page.wait_for_timeout(500)

                log.info(f"Looking for iframe with pattern: {__CF_PATTERN__.pattern}")
                outer_box = {}
                iframe = page.frame(url=__CF_PATTERN__)
                log.info(f"Iframe found: {iframe is not None}")

                if iframe is not None:
                    log.info("Waiting for iframe to load...")
                    iframe.wait_for_load_state(state="domcontentloaded")
                    iframe.wait_for_load_state("networkidle")

                    if challenge_type != "embedded":
                        while not iframe.frame_element().is_visible():
                            # Double-checking that the iframe is loaded
                            page.wait_for_timeout(500)
                    log.info("Getting iframe bounding box...")
                    outer_box: Any = iframe.frame_element().bounding_box()
                    log.info(f"Iframe bounding box: {outer_box}")

                if not iframe or not outer_box:
                    log.info(f"Trying to find element with selector: {box_selector}")
                    try:
                        outer_box: Any = page.locator(box_selector).last.bounding_box(timeout=5000)
                        log.info(f"Element bounding box: {outer_box}")
                    except Exception as e:
                        log.error(f"Failed to get bounding box: {e}")
                        # For embedded type, if we can't find the box, just skip clicking
                        if challenge_type == "embedded":
                            log.info("Embedded type: Skipping click and waiting for completion")
                            page.wait_for_timeout(3000)
                            try:
                                page.wait_for_load_state("networkidle", timeout=10000)
                            except PlaywrightError:
                                pass
                            page.wait_for_load_state(state="load")
                            page.wait_for_load_state(state="domcontentloaded")
                            log.info("Cloudflare captcha is solved (or bypassed)")
                            return
                        raise

                # Calculate the Captcha coordinates for any viewport
                log.info("Calculating captcha coordinates...")
                captcha_x, captcha_y = outer_box["x"] + randint(26, 28), outer_box["y"] + randint(25, 27)
                log.info(f"Clicking at coordinates: ({captcha_x}, {captcha_y})")

                # Move the mouse to the center of the window, then press and hold the left mouse button
                page.mouse.click(captcha_x, captcha_y, delay=60, button="left")
                log.info("Waiting for networkidle after click...")
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except PlaywrightError:
                    log.info("Initial networkidle timeout, continuing...")

                if challenge_type != "embedded":
                    if iframe is not None:
                        # Wait for the frame to be removed from the page
                        log.info("Waiting for iframe to be removed...")
                        iframe_removal_attempts = 0
                        while iframe in page.frames and iframe_removal_attempts < 50:  # Max 5 seconds
                            page.wait_for_timeout(100)
                            iframe_removal_attempts += 1
                        log.info("Iframe removed or timeout reached")

                    log.info("Waiting for elements to be detached/hidden...")
                    page.locator(box_selector).last.wait_for(state="detached")
                    page.locator(".zone-name-title").wait_for(state="hidden")
                else:
                    # For embedded type, the iframe and elements stay in the page
                    # Just wait for the challenge to complete
                    log.info("Embedded type: Waiting for challenge completion...")
                    page.wait_for_timeout(3000)  # Give some time for the challenge to process
                    # Wait for network to be idle as the challenge completion may trigger network requests
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except PlaywrightError:
                        # If networkidle times out, just continue as the challenge might be solved
                        log.info("Networkidle timeout, continuing...")
                        pass

                log.info("Final page load states...")
                page.wait_for_load_state(state="load")
                page.wait_for_load_state(state="domcontentloaded")

                log.info("Cloudflare captcha is solved")
                return

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
        solve_cloudflare: bool = _UNSET,
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
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
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
                ("solve_cloudflare", solve_cloudflare, self.solve_cloudflare),
                ("selector_config", selector_config, self.selector_config),
            ],
            _UNSET,
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
                and finished_response.request.frame == page_info.page.main_frame
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

            if params.solve_cloudflare:
                self._solve_cloudflare(page_info.page)
                # Make sure the page is fully loaded after the captcha
                page_info.page.wait_for_load_state(state="load")
                if params.load_dom:
                    page_info.page.wait_for_load_state(state="domcontentloaded")
                if params.network_idle:
                    page_info.page.wait_for_load_state("networkidle")

            if params.page_action:
                try:
                    _ = params.page_action(page_info.page)
                except Exception as e:
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
                except Exception as e:
                    log.error(f"Error waiting for selector {params.wait_selector}: {e}")

            page_info.page.wait_for_timeout(params.wait)
            response = ResponseFactory.from_playwright_response(
                page_info.page, first_response, final_response, params.selector_config
            )

            # Close the page to free up resources
            page_info.page.close()
            self.page_pool.pages.remove(page_info)

            return response

        except Exception as e:  # pragma: no cover
            page_info.mark_error()
            raise e


class AsyncStealthySession(StealthySessionMixin, AsyncSession):
    """A Stealthy session manager with page pooling."""

    def __init__(
        self,
        max_pages: int = 1,
        headless: bool = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
        load_dom: bool = True,
        humanize: bool | float = True,
        solve_cloudflare: bool = False,
        wait: int | float = 0,
        timeout: int | float = 30000,
        page_action: Optional[Callable] = None,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[List[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        user_data_dir: str = "",
        selector_config: Optional[Dict] = None,
        additional_args: Optional[Dict] = None,
    ):
        """A Browser session manager with page pooling

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param block_webrtc: Blocks WebRTC entirely.
        :param cookies: Set cookies for the next request.
        :param addons: List of Firefox addons to use. Must be paths to extracted addons.
        :param humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param user_data_dir: Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """
        self.__validate__(
            wait=wait,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            load_dom=load_dom,
            humanize=humanize,
            max_pages=max_pages,
            disable_ads=disable_ads,
            allow_webgl=allow_webgl,
            page_action=page_action,
            init_script=init_script,
            network_idle=network_idle,
            block_images=block_images,
            block_webrtc=block_webrtc,
            os_randomize=os_randomize,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            user_data_dir=user_data_dir,
            additional_args=additional_args,
            selector_config=selector_config,
            solve_cloudflare=solve_cloudflare,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        super().__init__(max_pages=self.max_pages)

    async def __create__(self):
        """Create a browser for this instance and context."""
        self.playwright: AsyncPlaywright = await async_playwright().start()
        self.context: AsyncBrowserContext = await self.playwright.firefox.launch_persistent_context(
            **self.launch_options
        )

        if self.init_script:  # pragma: no cover
            await self.context.add_init_script(path=self.init_script)

        if self.cookies:
            await self.context.add_cookies(self.cookies)  # pyright: ignore [reportArgumentType]

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
            self.context = None  # pyright: ignore

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None  # pyright: ignore

        self._closed = True

    @staticmethod
    async def _get_page_content(page: async_Page) -> str:
        """
        A workaround for the Playwright issue with `page.content()` on Windows. Ref.: https://github.com/microsoft/playwright/issues/16108
        :param page: The page to extract content from.
        :return:
        """
        while True:
            try:
                return (await page.content()) or ""
            except PlaywrightError:
                await page.wait_for_timeout(1000)
                continue
        return ""  # pyright: ignore

    async def _solve_cloudflare(self, page: async_Page):
        """Solve the cloudflare challenge displayed on the playwright page passed. The async version

        :param page: The async targeted page
        :return:
        """
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightError:
            pass
        challenge_type = self._detect_cloudflare(await self._get_page_content(page))
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":  # pragma: no cover
                while "<title>Just a moment...</title>" in (await self._get_page_content(page)):
                    log.info("Waiting for Cloudflare wait page to disappear.")
                    await page.wait_for_timeout(1000)
                    await page.wait_for_load_state()
                log.info("Cloudflare captcha is solved")
                return

            else:
                box_selector = "#cf_turnstile div, #cf-turnstile div, .turnstile>div>div"
                if challenge_type != "embedded":
                    box_selector = ".main-content p+div>div>div"
                    while "Verifying you are human." in (await self._get_page_content(page)):
                        # Waiting for the verify spinner to disappear, checking every 1s if it disappeared
                        await page.wait_for_timeout(500)

                outer_box = {}
                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is not None:
                    await iframe.wait_for_load_state(state="domcontentloaded")
                    await iframe.wait_for_load_state("networkidle")

                    if challenge_type != "embedded":
                        while not await (await iframe.frame_element()).is_visible():
                            # Double-checking that the iframe is loaded
                            await page.wait_for_timeout(500)
                    outer_box: Any = await (await iframe.frame_element()).bounding_box()

                if not iframe or not outer_box:
                    try:
                        outer_box: Any = await page.locator(box_selector).last.bounding_box(timeout=5000)
                    except Exception as e:
                        log.error(f"Failed to get bounding box: {e}")
                        # For embedded type, if we can't find the box, just skip clicking
                        if challenge_type == "embedded":
                            log.info("Embedded type: Skipping click and waiting for completion")
                            await page.wait_for_timeout(3000)
                            try:
                                await page.wait_for_load_state("networkidle", timeout=10000)
                            except PlaywrightError:
                                pass
                            await page.wait_for_load_state(state="load")
                            await page.wait_for_load_state(state="domcontentloaded")
                            log.info("Cloudflare captcha is solved (or bypassed)")
                            return
                        raise

                # Calculate the Captcha coordinates for any viewport
                captcha_x, captcha_y = outer_box["x"] + randint(26, 28), outer_box["y"] + randint(25, 27)

                # Move the mouse to the center of the window, then press and hold the left mouse button
                await page.mouse.click(captcha_x, captcha_y, delay=60, button="left")
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except PlaywrightError:
                    pass

                if challenge_type != "embedded":
                    if iframe is not None:
                        # Wait for the frame to be removed from the page
                        iframe_removal_attempts = 0
                        while iframe in page.frames and iframe_removal_attempts < 50:  # Max 5 seconds
                            await page.wait_for_timeout(100)
                            iframe_removal_attempts += 1

                    await page.locator(box_selector).wait_for(state="detached")
                    await page.locator(".zone-name-title").wait_for(state="hidden")
                else:
                    # For embedded type, the iframe and elements stay in the page
                    # Just wait for the challenge to complete
                    await page.wait_for_timeout(3000)  # Give some time for the challenge to process
                    # Wait for network to be idle as the challenge completion may trigger network requests
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except PlaywrightError:
                        # If networkidle times out, just continue as the challenge might be solved
                        pass
                await page.wait_for_load_state(state="load")
                await page.wait_for_load_state(state="domcontentloaded")

                log.info("Cloudflare captcha is solved")
                return

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
        solve_cloudflare: bool = _UNSET,
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
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
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
                ("solve_cloudflare", solve_cloudflare, self.solve_cloudflare),
                ("selector_config", selector_config, self.selector_config),
            ],
            _UNSET,
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
                and finished_response.request.frame == page_info.page.main_frame
            ):
                final_response = finished_response

        page_info = await self._get_page(params.timeout, params.extra_headers, params.disable_resources)
        page_info.mark_busy(url=url)

        if TYPE_CHECKING:
            if not isinstance(page_info.page, async_Page):
                raise TypeError

        try:
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = await page_info.page.goto(url, referer=referer)
            if params.load_dom:
                await page_info.page.wait_for_load_state(state="domcontentloaded")

            if params.network_idle:
                await page_info.page.wait_for_load_state("networkidle")

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if params.solve_cloudflare:
                await self._solve_cloudflare(page_info.page)
                # Make sure the page is fully loaded after the captcha
                await page_info.page.wait_for_load_state(state="load")
                if params.load_dom:
                    await page_info.page.wait_for_load_state(state="domcontentloaded")
                if params.network_idle:
                    await page_info.page.wait_for_load_state("networkidle")

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
                    if params.load_dom:
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

            # Close the page to free up resources
            await page_info.page.close()
            self.page_pool.pages.remove(page_info)

            return response

        except Exception as e:
            page_info.mark_error()
            raise e
