from random import randint
from re import compile as re_compile
from time import sleep as time_sleep
from asyncio import sleep as asyncio_sleep

from playwright.sync_api import Locator, Page, BrowserContext
from playwright.async_api import (
    Page as async_Page,
    Locator as AsyncLocator,
    BrowserContext as AsyncBrowserContext,
)
from patchright.sync_api import sync_playwright
from patchright.async_api import async_playwright

from scrapling.core.utils import log
from scrapling.core._types import Any, Optional, ProxyType, Unpack
from scrapling.engines.toolbelt.proxy_rotation import is_proxy_error
from scrapling.engines.toolbelt.convertor import Response, ResponseFactory
from scrapling.engines.toolbelt.fingerprints import generate_convincing_referer
from scrapling.engines._browsers._config_tools import _compiled_stealth_scripts
from scrapling.engines._browsers._types import StealthSession, StealthFetchParams
from scrapling.engines._browsers._base import SyncSession, AsyncSession, StealthySessionMixin
from scrapling.engines._browsers._validators import validate_fetch as _validate, StealthConfig

__CF_PATTERN__ = re_compile(r"^https?://challenges\.cloudflare\.com/cdn-cgi/challenge-platform/.*")


class StealthySession(SyncSession, StealthySessionMixin):
    """A Stealthy Browser session manager with page pooling."""

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

    def __init__(self, **kwargs: Unpack[StealthSession]):
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
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param allow_webgl: Enabled by default. Disabling it disables WebGL and WebGL 2.0 support entirely. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
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

    def start(self) -> None:
        """Create a browser for this instance and context."""
        if not self.playwright:
            self.playwright = sync_playwright().start()

            try:
                if self._config.cdp_url:  # pragma: no cover
                    self.browser = self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url)
                    if not self._config.proxy_rotator:
                        assert self.browser is not None
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

    def _initialize_context(self, config, ctx: BrowserContext) -> BrowserContext:
        """Initialize the browser context."""
        for script in _compiled_stealth_scripts():
            ctx.add_init_script(script=script)

        ctx = super()._initialize_context(config, ctx)
        return ctx

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

                outer_box: Any = {}
                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is not None:
                    self._wait_for_page_stability(iframe, True, False)

                    if challenge_type != "embedded":
                        while not iframe.frame_element().is_visible():
                            # Double-checking that the iframe is loaded
                            page.wait_for_timeout(500)

                    outer_box = iframe.frame_element().bounding_box()

                if not iframe or not outer_box:
                    if "<title>Just a moment...</title>" not in (ResponseFactory._get_page_content(page)):
                        log.info("Cloudflare captcha is solved")
                        return

                    outer_box = page.locator(box_selector).last.bounding_box()

                # Calculate the Captcha coordinates for any viewport
                captcha_x, captcha_y = outer_box["x"] + randint(26, 28), outer_box["y"] + randint(25, 27)

                # Move the mouse to the center of the window, then press and hold the left mouse button
                page.mouse.click(captcha_x, captcha_y, delay=randint(100, 200), button="left")
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

    def fetch(self, url: str, **kwargs: Unpack[StealthFetchParams]) -> Response:
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
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param proxy: Static proxy to override rotator and session proxy. A new browser context will be created and used with it.
        :return: A `Response` object.
        """
        static_proxy = kwargs.pop("proxy", None)

        params = _validate(kwargs, self, StealthConfig)
        if not self._is_alive:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        request_headers_keys = {h.lower() for h in params.extra_headers.keys()} if params.extra_headers else set()
        referer = (
            generate_convincing_referer(url)
            if (params.google_search and "referer" not in request_headers_keys)
            else None
        )

        for attempt in range(self._config.retries):
            proxy: Optional[ProxyType] = None
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

                    if params.solve_cloudflare:
                        self._cloudflare_solver(page)
                        # Make sure the page is fully loaded after the captcha
                        self._wait_for_page_stability(page, params.load_dom, params.network_idle)

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


class AsyncStealthySession(AsyncSession, StealthySessionMixin):
    """An async Stealthy Browser session manager with page pooling."""

    __slots__ = (
        "_config",
        "_context_options",
        "_browser_options",
        "_user_data_dir",
        "_headers_keys",
    )

    def __init__(self, **kwargs: Unpack[StealthSession]):
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
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
        :param allow_webgl: Enabled by default. Disabling it disables WebGL and WebGL 2.0 support entirely. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
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
        super().__init__(max_pages=self._config.max_pages)

    async def start(self) -> None:
        """Create a browser for this instance and context."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            try:
                if self._config.cdp_url:
                    self.browser = await self.playwright.chromium.connect_over_cdp(endpoint_url=self._config.cdp_url)
                    if not self._config.proxy_rotator:
                        assert self.browser is not None
                        self.context = await self.browser.new_context(**self._context_options)
                elif self._config.proxy_rotator:
                    self.browser = await self.playwright.chromium.launch(**self._browser_options)
                else:
                    persistent_options = (
                        self._browser_options | self._context_options | {"user_data_dir": self._user_data_dir}
                    )
                    self.context = await self.playwright.chromium.launch_persistent_context(**persistent_options)

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

    async def _initialize_context(self, config: Any, ctx: AsyncBrowserContext) -> AsyncBrowserContext:
        """Initialize the browser context."""
        for script in _compiled_stealth_scripts():
            await ctx.add_init_script(script=script)

        ctx = await super()._initialize_context(config, ctx)
        return ctx

    async def _cloudflare_solver(self, page: async_Page) -> None:  # pragma: no cover
        """Solve the cloudflare challenge displayed on the playwright page passed

        :param page: The targeted page
        :return:
        """
        await self._wait_for_networkidle(page, timeout=5000)
        challenge_type = self._detect_cloudflare(await ResponseFactory._get_async_page_content(page))
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":
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

                outer_box: Any = {}
                iframe = page.frame(url=__CF_PATTERN__)
                if iframe is not None:
                    await self._wait_for_page_stability(iframe, True, False)

                    if challenge_type != "embedded":
                        while not await (await iframe.frame_element()).is_visible():
                            # Double-checking that the iframe is loaded
                            await page.wait_for_timeout(500)

                    outer_box = await (await iframe.frame_element()).bounding_box()

                if not iframe or not outer_box:
                    if "<title>Just a moment...</title>" not in (await ResponseFactory._get_async_page_content(page)):
                        log.info("Cloudflare captcha is solved")
                        return

                    outer_box = await page.locator(box_selector).last.bounding_box()

                # Calculate the Captcha coordinates for any viewport
                captcha_x, captcha_y = outer_box["x"] + randint(26, 28), outer_box["y"] + randint(25, 27)

                # Move the mouse to the center of the window, then press and hold the left mouse button
                await page.mouse.click(captcha_x, captcha_y, delay=randint(100, 200), button="left")
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
                    await page.locator(box_selector).last.wait_for(state="detached")
                    await page.locator(".zone-name-title").wait_for(state="hidden")
                await self._wait_for_page_stability(page, True, False)

                log.info("Cloudflare captcha is solved")
                return

    async def fetch(self, url: str, **kwargs: Unpack[StealthFetchParams]) -> Response:
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
        :param solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param proxy: Static proxy to override rotator and session proxy. A new browser context will be created and used with it.
        :return: A `Response` object.
        """
        static_proxy = kwargs.pop("proxy", None)

        params = _validate(kwargs, self, StealthConfig)

        if not self._is_alive:  # pragma: no cover
            raise RuntimeError("Context manager has been closed")

        request_headers_keys = {h.lower() for h in params.extra_headers.keys()} if params.extra_headers else set()
        referer = (
            generate_convincing_referer(url)
            if (params.google_search and "referer" not in request_headers_keys)
            else None
        )

        for attempt in range(self._config.retries):
            proxy: Optional[ProxyType] = None
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

                    if params.solve_cloudflare:
                        await self._cloudflare_solver(page)
                        # Make sure the page is fully loaded after the captcha
                        await self._wait_for_page_stability(page, params.load_dom, params.network_idle)

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
