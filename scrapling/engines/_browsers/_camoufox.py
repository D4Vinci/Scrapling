from random import randint
from re import compile as re_compile

from playwright.sync_api import (
    Page,
    Locator,
    sync_playwright,
)
from playwright.async_api import (
    async_playwright,
    Page as async_Page,
    Locator as AsyncLocator,
    Playwright as AsyncPlaywright,
    BrowserContext as AsyncBrowserContext,
)

from scrapling.core.utils import log
from ._types import CamoufoxSession, CamoufoxFetchParams
from scrapling.core._types import Any, Unpack, TYPE_CHECKING
from ._base import SyncSession, AsyncSession, StealthySessionMixin
from ._validators import validate_fetch as _validate, CamoufoxConfig
from scrapling.engines.toolbelt.convertor import Response, ResponseFactory
from scrapling.engines.toolbelt.fingerprints import generate_convincing_referer

__CF_PATTERN__ = re_compile("challenges.cloudflare.com/cdn-cgi/challenge-platform/.*")


class StealthySession(StealthySessionMixin, SyncSession):
    """A Stealthy session manager with page pooling."""

    __slots__ = (
        "_max_pages",
        "_headless",
        "_block_images",
        "_disable_resources",
        "_block_webrtc",
        "_allow_webgl",
        "_network_idle",
        "_load_dom",
        "_humanize",
        "_solve_cloudflare",
        "_wait",
        "_timeout",
        "_page_action",
        "_wait_selector",
        "_init_script",
        "_addons",
        "_wait_selector_state",
        "_cookies",
        "_google_search",
        "_extra_headers",
        "_proxy",
        "_os_randomize",
        "_disable_ads",
        "_geoip",
        "_selector_config",
        "_additional_args",
        "playwright",
        "browser",
        "context",
        "page_pool",
        "_closed",
        "launch_options",
        "_headers_keys",
        "_user_data_dir",
    )

    def __init__(self, **kwargs: Unpack[CamoufoxSession]):
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
        self.__validate__(**kwargs)
        super().__init__(max_pages=self._max_pages)

    def __create__(self):
        """Create a browser for this instance and context."""
        self.playwright = sync_playwright().start()
        self.context = self.playwright.firefox.launch_persistent_context(**self.launch_options)

        if self._init_script:  # pragma: no cover
            self.context.add_init_script(path=self._init_script)

        if self._cookies:  # pragma: no cover
            self.context.add_cookies(self._cookies)

    def _cloudflare_solver(self, page: Page) -> None:  # pragma: no cover
        """Solve the cloudflare challenge displayed on the playwright page passed

        :param page: The targeted page
        :return:
        """
        self._wait_for_networkidle(page, timeout=5000)
        challenge_type = self._detect_cloudflare(ResponseFactory._get_page_content(page))
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":
                while "<title>Just a moment...</title>" in (ResponseFactory._get_page_content(page)):
                    log.info("Waiting for Cloudflare wait page to disappear.")
                    page.wait_for_timeout(1000)
                    page.wait_for_load_state()
                log.info("Cloudflare captcha is solved")
                return

            else:
                box_selector = "#cf_turnstile div, #cf-turnstile div, .turnstile>div>div"
                if challenge_type != "embedded":
                    box_selector = ".main-content p+div>div>div"
                    while "Verifying you are human." in ResponseFactory._get_page_content(page):
                        # Waiting for the verify spinner to disappear, checking every 1s if it disappeared
                        page.wait_for_timeout(500)

                outer_box = {}
                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is not None:
                    self._wait_for_page_stability(iframe, True, True)

                    if challenge_type != "embedded":
                        while not iframe.frame_element().is_visible():
                            # Double-checking that the iframe is loaded
                            page.wait_for_timeout(500)
                    outer_box: Any = iframe.frame_element().bounding_box()

                if not iframe or not outer_box:
                    outer_box: Any = page.locator(box_selector).last.bounding_box()

                # Calculate the Captcha coordinates for any viewport
                captcha_x, captcha_y = outer_box["x"] + randint(26, 28), outer_box["y"] + randint(25, 27)

                # Move the mouse to the center of the window, then press and hold the left mouse button
                page.mouse.click(captcha_x, captcha_y, delay=60, button="left")
                self._wait_for_networkidle(page)
                if iframe is not None:
                    # Wait for the frame to be removed from the page (with 30s timeout = 300 iterations * 100 ms)
                    attempts = 0
                    while iframe in page.frames:
                        if attempts >= 300:
                            log.info("Cloudflare iframe didn't disappear after 30s, continuing...")
                            break
                        page.wait_for_timeout(100)
                        attempts += 1
                if challenge_type != "embedded":
                    page.locator(box_selector).last.wait_for(state="detached")
                    page.locator(".zone-name-title").wait_for(state="hidden")
                self._wait_for_page_stability(page, True, False)

                log.info("Cloudflare captcha is solved")
                return

    def fetch(self, url: str, **kwargs: Unpack[CamoufoxFetchParams]) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param kwargs: Additional keyword arguments including:
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
            - disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
                Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
                This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :return: A `Response` object.
        """
        params = _validate(kwargs, self, CamoufoxConfig)

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

            if params.solve_cloudflare:
                self._cloudflare_solver(page_info.page)
                # Make sure the page is fully loaded after the captcha
                self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)

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
                    self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)
                except Exception as e:
                    log.error(f"Error waiting for selector {params.wait_selector}: {e}")

            page_info.page.wait_for_timeout(params.wait)
            response = ResponseFactory.from_playwright_response(
                page_info.page, first_response, final_response[0], params.selector_config
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

    def __init__(self, **kwargs: Unpack[CamoufoxSession]):
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
        self.__validate__(**kwargs)
        super().__init__(max_pages=self._max_pages)

    async def __create__(self):
        """Create a browser for this instance and context."""
        self.playwright: AsyncPlaywright = await async_playwright().start()
        self.context: AsyncBrowserContext = await self.playwright.firefox.launch_persistent_context(
            **self.launch_options
        )

        if self._init_script:  # pragma: no cover
            await self.context.add_init_script(path=self._init_script)

        if self._cookies:
            await self.context.add_cookies(self._cookies)  # pyright: ignore [reportArgumentType]

    async def _cloudflare_solver(self, page: async_Page):  # pragma: no cover
        """Solve the cloudflare challenge displayed on the playwright page passed. The async version

        :param page: The async targeted page
        :return:
        """
        await self._wait_for_networkidle(page, timeout=5000)
        challenge_type = self._detect_cloudflare(await ResponseFactory._get_async_page_content(page))
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":  # pragma: no cover
                while "<title>Just a moment...</title>" in (await ResponseFactory._get_async_page_content(page)):
                    log.info("Waiting for Cloudflare wait page to disappear.")
                    await page.wait_for_timeout(1000)
                    await page.wait_for_load_state()
                log.info("Cloudflare captcha is solved")
                return

            else:
                box_selector = "#cf_turnstile div, #cf-turnstile div, .turnstile>div>div"
                if challenge_type != "embedded":
                    box_selector = ".main-content p+div>div>div"
                    while "Verifying you are human." in (await ResponseFactory._get_async_page_content(page)):
                        # Waiting for the verify spinner to disappear, checking every 1s if it disappeared
                        await page.wait_for_timeout(500)

                outer_box = {}
                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is not None:
                    await self._wait_for_page_stability(iframe, True, True)

                    if challenge_type != "embedded":
                        while not await (await iframe.frame_element()).is_visible():
                            # Double-checking that the iframe is loaded
                            await page.wait_for_timeout(500)
                    outer_box: Any = await (await iframe.frame_element()).bounding_box()

                if not iframe or not outer_box:
                    outer_box: Any = await page.locator(box_selector).last.bounding_box()

                # Calculate the Captcha coordinates for any viewport
                captcha_x, captcha_y = outer_box["x"] + randint(26, 28), outer_box["y"] + randint(25, 27)

                # Move the mouse to the center of the window, then press and hold the left mouse button
                await page.mouse.click(captcha_x, captcha_y, delay=60, button="left")
                await self._wait_for_networkidle(page)
                if iframe is not None:
                    # Wait for the frame to be removed from the page (with 30s timeout = 300 iterations * 100 ms)
                    attempts = 0
                    while iframe in page.frames:
                        if attempts >= 300:
                            log.info("Cloudflare iframe didn't disappear after 30s, continuing...")
                            break
                        await page.wait_for_timeout(100)
                        attempts += 1
                if challenge_type != "embedded":
                    await page.locator(box_selector).wait_for(state="detached")
                    await page.locator(".zone-name-title").wait_for(state="hidden")
                await self._wait_for_page_stability(page, True, False)

                log.info("Cloudflare captcha is solved")
                return

    async def fetch(self, url: str, **kwargs: Unpack[CamoufoxFetchParams]) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: The Target url.
        :param kwargs: Additional keyword arguments including:
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
            - disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
                Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
                This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :return: A `Response` object.
        """
        params = _validate(kwargs, self, CamoufoxConfig)

        if self._closed:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        referer = (
            generate_convincing_referer(url) if (params.google_search and "referer" not in self._headers_keys) else None
        )

        page_info = await self._get_page(params.timeout, params.extra_headers, params.disable_resources)
        final_response = [None]
        handle_response = self._create_response_handler(page_info, final_response)

        if TYPE_CHECKING:
            if not isinstance(page_info.page, async_Page):
                raise TypeError

        try:
            # Navigate to URL and wait for a specified state
            page_info.page.on("response", handle_response)
            first_response = await page_info.page.goto(url, referer=referer)
            await self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)

            if not first_response:
                raise RuntimeError(f"Failed to get response for {url}")

            if params.solve_cloudflare:
                await self._cloudflare_solver(page_info.page)
                # Make sure the page is fully loaded after the captcha
                await self._wait_for_page_stability(page_info.page, params.load_dom, params.network_idle)

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

        except Exception as e:
            page_info.mark_error()
            raise e
