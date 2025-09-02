from time import time, sleep
from re import compile as re_compile
from asyncio import sleep as asyncio_sleep, Lock

from camoufox import DefaultAddons
from camoufox.utils import launch_options as generate_launch_options
from playwright.sync_api import (
    Response as SyncPlaywrightResponse,
    sync_playwright,
    BrowserContext,
    Playwright,
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

from scrapling.core.utils import log
from ._page import PageInfo, PagePool
from ._validators import validate, CamoufoxConfig
from scrapling.core._types import (
    Dict,
    List,
    Optional,
    Callable,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt import (
    Response,
    ResponseFactory,
    async_intercept_route,
    generate_convincing_referer,
    get_os_name,
    intercept_route,
)

__CF_PATTERN__ = re_compile("challenges.cloudflare.com/cdn-cgi/challenge-platform/.*")


class StealthySession:
    """A Stealthy session manager with page pooling."""

    __slots__ = (
        "max_pages",
        "headless",
        "block_images",
        "disable_resources",
        "block_webrtc",
        "allow_webgl",
        "network_idle",
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
        max_pages: int = 1,
        headless: bool = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
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
        :param solve_cloudflare: Solves all 3 types of the Cloudflare's Turnstile wait page before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """

        params = {
            "max_pages": max_pages,
            "headless": headless,
            "block_images": block_images,
            "disable_resources": disable_resources,
            "block_webrtc": block_webrtc,
            "allow_webgl": allow_webgl,
            "network_idle": network_idle,
            "humanize": humanize,
            "solve_cloudflare": solve_cloudflare,
            "wait": wait,
            "timeout": timeout,
            "page_action": page_action,
            "wait_selector": wait_selector,
            "init_script": init_script,
            "addons": addons,
            "wait_selector_state": wait_selector_state,
            "cookies": cookies,
            "google_search": google_search,
            "extra_headers": extra_headers,
            "proxy": proxy,
            "os_randomize": os_randomize,
            "disable_ads": disable_ads,
            "geoip": geoip,
            "selector_config": selector_config,
            "additional_args": additional_args,
        }
        config = validate(params, CamoufoxConfig)

        self.max_pages = config.max_pages
        self.headless = config.headless
        self.block_images = config.block_images
        self.disable_resources = config.disable_resources
        self.block_webrtc = config.block_webrtc
        self.allow_webgl = config.allow_webgl
        self.network_idle = config.network_idle
        self.humanize = config.humanize
        self.solve_cloudflare = config.solve_cloudflare
        self.wait = config.wait
        self.timeout = config.timeout
        self.page_action = config.page_action
        self.wait_selector = config.wait_selector
        self.init_script = config.init_script
        self.addons = config.addons
        self.wait_selector_state = config.wait_selector_state
        self.cookies = config.cookies
        self.google_search = config.google_search
        self.extra_headers = config.extra_headers
        self.proxy = config.proxy
        self.os_randomize = config.os_randomize
        self.disable_ads = config.disable_ads
        self.geoip = config.geoip
        self.selector_config = config.selector_config
        self.additional_args = config.additional_args

        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page_pool = PagePool(self.max_pages)
        self._closed = False
        self.selector_config = config.selector_config
        self.page_action = config.page_action
        self._headers_keys = (
            set(map(str.lower, self.extra_headers.keys()))
            if self.extra_headers
            else set()
        )
        self.__initiate_browser_options__()

    def __initiate_browser_options__(self):
        """Initiate browser options."""
        self.launch_options = generate_launch_options(
            **{
                "geoip": self.geoip,
                "proxy": dict(self.proxy) if self.proxy else self.proxy,
                "enable_cache": True,
                "addons": self.addons,
                "exclude_addons": [] if self.disable_ads else [DefaultAddons.UBO],
                "headless": self.headless,
                "humanize": True if self.solve_cloudflare else self.humanize,
                "i_know_what_im_doing": True,  # To turn warnings off with the user configurations
                "allow_webgl": self.allow_webgl,
                "block_webrtc": self.block_webrtc,
                "block_images": self.block_images,  # Careful! it makes some websites don't finish loading at all like stackoverflow even in headful mode.
                "os": None if self.os_randomize else get_os_name(),
                "user_data_dir": "",
                **self.additional_args,
            }
        )

    def __create__(self):
        """Create a browser for this instance and context."""
        self.playwright = sync_playwright().start()
        self.context = (
            self.playwright.firefox.launch_persistent_context(  # pragma: no cover
                **self.launch_options
            )
        )
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

    def _get_or_create_page(self) -> PageInfo:  # pragma: no cover
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

            return self.page_pool.add_page(page)

        # Wait for a page to become available
        max_wait = 30
        start_time = time()

        while time() - start_time < max_wait:
            page_info = self.page_pool.get_ready_page()
            if page_info:
                return page_info
            sleep(0.05)

        raise TimeoutError("No pages available within timeout period")

    @staticmethod
    def _detect_cloudflare(page_content):
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

        return None

    def _solve_cloudflare(self, page: Page) -> None:  # pragma: no cover
        """Solve the cloudflare challenge displayed on the playwright page passed

        :param page: The targeted page
        :return:
        """
        challenge_type = self._detect_cloudflare(page.content())
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":
                while "<title>Just a moment...</title>" in (page.content()):
                    log.info("Waiting for Cloudflare wait page to disappear.")
                    page.wait_for_timeout(1000)
                    page.wait_for_load_state()
                log.info("Cloudflare captcha is solved")
                return

            else:
                while "Verifying you are human." in page.content():
                    # Waiting for the verify spinner to disappear, checking every 1s if it disappeared
                    page.wait_for_timeout(500)

                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is None:
                    log.info("Didn't find Cloudflare iframe!")
                    return

                while not iframe.frame_element().is_visible():
                    # Double-checking that the iframe is loaded
                    page.wait_for_timeout(500)

                # Calculate the Captcha coordinates for any viewport
                outer_box = page.locator(".main-content p+div>div>div").bounding_box()
                captcha_x, captcha_y = outer_box["x"] + 26, outer_box["y"] + 25

                # Move the mouse to the center of the window, then press and hold the left mouse button
                page.mouse.click(captcha_x, captcha_y, delay=60, button="left")
                page.locator(".zone-name-title").wait_for(state="hidden")
                page.wait_for_load_state(state="domcontentloaded")

                log.info("Cloudflare captcha is solved")
                return

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :return: A `Response` object.
        """
        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        final_response = None
        referer = (
            generate_convincing_referer(url)
            if (self.google_search and "referer" not in self._headers_keys)
            else None
        )

        def handle_response(finished_response: SyncPlaywrightResponse):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        page_info = self._get_or_create_page()
        page_info.mark_busy(url=url)

        try:  # pragma: no cover
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = page_info.page.goto(url, referer=referer)
            page_info.page.wait_for_load_state(state="domcontentloaded")

            if self.network_idle:
                page_info.page.wait_for_load_state("networkidle")

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if self.solve_cloudflare:
                self._solve_cloudflare(page_info.page)
                # Make sure the page is fully loaded after the captcha
                page_info.page.wait_for_load_state(state="load")
                page_info.page.wait_for_load_state(state="domcontentloaded")
                if self.network_idle:
                    page_info.page.wait_for_load_state("networkidle")

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
            response = ResponseFactory.from_playwright_response(
                page_info.page, first_response, final_response, self.selector_config
            )

            # Mark the page as ready for next use
            page_info.mark_ready()

            return response

        except Exception as e:  # pragma: no cover
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


class AsyncStealthySession(StealthySession):
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
        :param solve_cloudflare: Solves all 3 types of the Cloudflare's Turnstile wait page before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param max_pages: The maximum number of tabs to be opened at the same time. It will be used in rotation through a PagePool.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """
        super().__init__(
            max_pages,
            headless,
            block_images,
            disable_resources,
            block_webrtc,
            allow_webgl,
            network_idle,
            humanize,
            solve_cloudflare,
            wait,
            timeout,
            page_action,
            wait_selector,
            init_script,
            addons,
            wait_selector_state,
            cookies,
            google_search,
            extra_headers,
            proxy,
            os_randomize,
            disable_ads,
            geoip,
            selector_config,
            additional_args,
        )
        self.playwright: Optional[AsyncPlaywright] = None
        self.context: Optional[AsyncBrowserContext] = None
        self._lock = Lock()
        self.__enter__ = None
        self.__exit__ = None

    async def __create__(self):
        """Create a browser for this instance and context."""
        self.playwright: AsyncPlaywright = await async_playwright().start()
        self.context: AsyncBrowserContext = (
            await self.playwright.firefox.launch_persistent_context(
                **self.launch_options
            )
        )
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

                return self.page_pool.add_page(page)

        # Wait for a page to become available
        max_wait = 30
        start_time = time()

        while time() - start_time < max_wait:  # pragma: no cover
            page_info = self.page_pool.get_ready_page()
            if page_info:
                return page_info
            await asyncio_sleep(0.05)

        raise TimeoutError("No pages available within timeout period")

    async def _solve_cloudflare(self, page: async_Page):
        """Solve the cloudflare challenge displayed on the playwright page passed. The async version

        :param page: The async targeted page
        :return:
        """
        challenge_type = self._detect_cloudflare(await page.content())
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":  # pragma: no cover
                while "<title>Just a moment...</title>" in (await page.content()):
                    log.info("Waiting for Cloudflare wait page to disappear.")
                    await page.wait_for_timeout(1000)
                    await page.wait_for_load_state()
                log.info("Cloudflare captcha is solved")
                return

            else:
                while "Verifying you are human." in (await page.content()):
                    # Waiting for the verify spinner to disappear, checking every 1s if it disappeared
                    await page.wait_for_timeout(500)

                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is None:
                    log.info("Didn't find Cloudflare iframe!")
                    return

                while not await (await iframe.frame_element()).is_visible():
                    # Double-checking that the iframe is loaded
                    await page.wait_for_timeout(500)

                # Calculate the Captcha coordinates for any viewport
                outer_box = await page.locator(
                    ".main-content p+div>div>div"
                ).bounding_box()
                captcha_x, captcha_y = outer_box["x"] + 26, outer_box["y"] + 25

                # Move the mouse to the center of the window, then press and hold the left mouse button
                await page.mouse.click(captcha_x, captcha_y, delay=60, button="left")
                await page.locator(".zone-name-title").wait_for(state="hidden")
                await page.wait_for_load_state(state="domcontentloaded")

                log.info("Cloudflare captcha is solved")
                return

    async def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :return: A `Response` object.
        """
        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        final_response = None
        referer = (
            generate_convincing_referer(url)
            if (self.google_search and "referer" not in self._headers_keys)
            else None
        )

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

            if self.solve_cloudflare:
                await self._solve_cloudflare(page_info.page)
                # Make sure the page is fully loaded after the captcha
                await page_info.page.wait_for_load_state(state="load")
                await page_info.page.wait_for_load_state(state="domcontentloaded")
                if self.network_idle:
                    await page_info.page.wait_for_load_state("networkidle")

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
                page_info.page, first_response, final_response, self.selector_config
            )

            # Mark the page as ready for next use
            page_info.mark_ready()

            return response

        except Exception as e:
            page_info.mark_error()
            raise e
