import re

from camoufox import DefaultAddons
from playwright.sync_api import Page
from camoufox.sync_api import Camoufox
from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Page as async_Page

from scrapling.core._types import (
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    SelectorWaitStates,
    Union,
    Iterable,
)
from scrapling.core.utils import log
from scrapling.engines.toolbelt import (
    Response,
    StatusText,
    async_intercept_route,
    check_type_validity,
    construct_proxy_dict,
    generate_convincing_referer,
    get_os_name,
    intercept_route,
)


class CamoufoxEngine:
    def __init__(
        self,
        headless: Union[bool, Literal["virtual"]] = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
        humanize: Union[bool, float] = True,
        solve_cloudflare: Optional[bool] = False,
        wait: Optional[int] = 0,
        timeout: Optional[float] = 30000,
        page_action: Callable = None,
        wait_selector: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[Iterable[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        adaptor_arguments: Dict = None,
        additional_arguments: Dict = None,
    ):
        """An engine that uses the Camoufox library; Check the `StealthyFetcher` class for more documentation.

        :param headless: Run the browser in headless/hidden (default), virtual screen mode, or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.
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
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        :param additional_arguments: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """
        self.headless = headless
        self.block_images = bool(block_images)
        self.disable_resources = bool(disable_resources)
        self.block_webrtc = bool(block_webrtc)
        self.allow_webgl = bool(allow_webgl)
        self.network_idle = bool(network_idle)
        self.google_search = bool(google_search)
        self.os_randomize = bool(os_randomize)
        self.disable_ads = bool(disable_ads)
        self.geoip = bool(geoip)
        self.extra_headers = extra_headers or {}
        self.additional_arguments = additional_arguments or {}
        self.proxy = construct_proxy_dict(proxy)
        self.addons = addons or []
        self.cookies = cookies or []
        self.humanize = humanize
        self.solve_cloudflare = solve_cloudflare
        self.timeout = check_type_validity(timeout, [int, float], 30_000)
        self.wait = check_type_validity(wait, [int, float], 0)

        if self.solve_cloudflare and self.timeout < 60_000:
            self.timeout = 60_000

        # Page action callable validation
        self.page_action = None
        if page_action is not None:
            if callable(page_action):
                self.page_action = page_action
            else:
                log.error('[Ignored] Argument "page_action" must be callable')

        self.wait_selector = wait_selector
        self.wait_selector_state = wait_selector_state
        self.adaptor_arguments = adaptor_arguments if adaptor_arguments else {}

    def _get_camoufox_options(self):
        """Return consistent browser options dictionary for both sync and async methods"""
        humanize = self.humanize
        if self.solve_cloudflare:
            humanize = True

        return {
            "geoip": self.geoip,
            "proxy": self.proxy,
            "enable_cache": True,
            "addons": self.addons,
            "exclude_addons": [] if self.disable_ads else [DefaultAddons.UBO],
            "headless": self.headless,
            "humanize": humanize,
            "i_know_what_im_doing": True,  # To turn warnings off with the user configurations
            "allow_webgl": self.allow_webgl,
            "block_webrtc": self.block_webrtc,
            "block_images": self.block_images,  # Careful! it makes some websites don't finish loading at all like stackoverflow even in headful mode.
            "os": None if self.os_randomize else get_os_name(),
            **self.additional_arguments,
        }

    def _process_response_history(self, first_response):
        """Process response history to build a list of Response objects"""
        history = []
        current_request = first_response.request.redirected_from

        try:
            while current_request:
                try:
                    current_response = current_request.response()
                    history.insert(
                        0,
                        Response(
                            url=current_request.url,
                            # using current_response.text() will trigger "Error: Response.text: Response body is unavailable for redirect responses"
                            text="",
                            body=b"",
                            status=current_response.status if current_response else 301,
                            reason=(
                                current_response.status_text
                                or StatusText.get(current_response.status)
                            )
                            if current_response
                            else StatusText.get(301),
                            encoding=current_response.headers.get("content-type", "")
                            or "utf-8",
                            cookies=tuple(),
                            headers=current_response.all_headers()
                            if current_response
                            else {},
                            request_headers=current_request.all_headers(),
                            **self.adaptor_arguments,
                        ),
                    )
                except Exception as e:
                    log.error(f"Error processing redirect: {e}")
                    break

                current_request = current_request.redirected_from
        except Exception as e:
            log.error(f"Error processing response history: {e}")

        return history

    async def _async_process_response_history(self, first_response):
        """Process response history to build a list of Response objects"""
        history = []
        current_request = first_response.request.redirected_from

        try:
            while current_request:
                try:
                    current_response = await current_request.response()
                    history.insert(
                        0,
                        Response(
                            url=current_request.url,
                            # using current_response.text() will trigger "Error: Response.text: Response body is unavailable for redirect responses"
                            text="",
                            body=b"",
                            status=current_response.status if current_response else 301,
                            reason=(
                                current_response.status_text
                                or StatusText.get(current_response.status)
                            )
                            if current_response
                            else StatusText.get(301),
                            encoding=current_response.headers.get("content-type", "")
                            or "utf-8",
                            cookies=tuple(),
                            headers=await current_response.all_headers()
                            if current_response
                            else {},
                            request_headers=await current_request.all_headers(),
                            **self.adaptor_arguments,
                        ),
                    )
                except Exception as e:
                    log.error(f"Error processing redirect: {e}")
                    break

                current_request = current_request.redirected_from
        except Exception as e:
            log.error(f"Error processing response history: {e}")

        return history

    @staticmethod
    def __detect_cloudflare(page_content):
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

    def _solve_cloudflare(self, page: Page) -> None:
        """Solve the cloudflare challenge displayed on the playwright page passed

        :param page: The targeted page
        :return:
        """
        page_content = page.content()
        challenge_type = self.__detect_cloudflare(page_content)
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

                iframe = page.frame(
                    url=re.compile(
                        "challenges.cloudflare.com/cdn-cgi/challenge-platform/.*"
                    )
                )
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

    async def _async_solve_cloudflare(self, page: async_Page):
        """Solve the cloudflare challenge displayed on the playwright page passed. The async version

        :param page: The async targeted page
        :return:
        """
        page_content = await page.content()
        challenge_type = self.__detect_cloudflare(page_content)
        if not challenge_type:
            log.error("No Cloudflare challenge found.")
            return
        else:
            log.info(f'The turnstile version discovered is "{challenge_type}"')
            if challenge_type == "non-interactive":
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

                iframe = page.frame(
                    url=re.compile(
                        "challenges.cloudflare.com/cdn-cgi/challenge-platform/.*"
                    )
                )
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

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        final_response = None
        referer = generate_convincing_referer(url) if self.google_search else None

        def handle_response(finished_response):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        with Camoufox(**self._get_camoufox_options()) as browser:
            context = browser.new_context()
            if self.cookies:
                context.add_cookies(self.cookies)

            page = context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            page.on("response", handle_response)

            if self.disable_resources:
                page.route("**/*", intercept_route)

            if self.extra_headers:
                page.set_extra_http_headers(self.extra_headers)

            first_response = page.goto(url, referer=referer)
            page.wait_for_load_state(state="domcontentloaded")

            if self.network_idle:
                page.wait_for_load_state("networkidle")

            if self.solve_cloudflare:
                self._solve_cloudflare(page)
                # Make sure the page is fully loaded after the captcha
                page.wait_for_load_state(state="load")
                page.wait_for_load_state(state="domcontentloaded")
                if self.network_idle:
                    page.wait_for_load_state("networkidle")

            if self.page_action is not None:
                try:
                    page = self.page_action(page)
                except Exception as e:
                    log.error(f"Error executing page_action: {e}")

            if self.wait_selector and type(self.wait_selector) is str:
                try:
                    waiter = page.locator(self.wait_selector)
                    waiter.first.wait_for(state=self.wait_selector_state)
                    # Wait again after waiting for the selector, helpful with protections like Cloudflare
                    page.wait_for_load_state(state="load")
                    page.wait_for_load_state(state="domcontentloaded")
                    if self.network_idle:
                        page.wait_for_load_state("networkidle")
                except Exception as e:
                    log.error(f"Error waiting for selector {self.wait_selector}: {e}")

            page.wait_for_timeout(self.wait)
            # In case we didn't catch a document type somehow
            final_response = final_response if final_response else first_response
            if not final_response:
                raise ValueError("Failed to get a response from the page")

            # This will be parsed inside `Response`
            encoding = (
                final_response.headers.get("content-type", "") or "utf-8"
            )  # default encoding
            # PlayWright API sometimes give empty status text for some reason!
            status_text = final_response.status_text or StatusText.get(
                final_response.status
            )

            history = self._process_response_history(first_response)
            try:
                page_content = page.content()
            except Exception as e:
                log.error(f"Error getting page content: {e}")
                page_content = ""

            response = Response(
                url=page.url,
                text=page_content,
                body=page_content.encode("utf-8"),
                status=final_response.status,
                reason=status_text,
                encoding=encoding,
                cookies=tuple(dict(cookie) for cookie in page.context.cookies()),
                headers=first_response.all_headers(),
                request_headers=first_response.request.all_headers(),
                history=history,
                **self.adaptor_arguments,
            )
            page.close()
            context.close()

        return response

    async def async_fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        final_response = None
        referer = generate_convincing_referer(url) if self.google_search else None

        async def handle_response(finished_response):
            nonlocal final_response
            if (
                finished_response.request.resource_type == "document"
                and finished_response.request.is_navigation_request()
            ):
                final_response = finished_response

        async with AsyncCamoufox(**self._get_camoufox_options()) as browser:
            context = await browser.new_context()
            if self.cookies:
                await context.add_cookies(self.cookies)

            page = await context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            page.on("response", handle_response)

            if self.disable_resources:
                await page.route("**/*", async_intercept_route)

            if self.extra_headers:
                await page.set_extra_http_headers(self.extra_headers)

            first_response = await page.goto(url, referer=referer)
            await page.wait_for_load_state(state="domcontentloaded")

            if self.network_idle:
                await page.wait_for_load_state("networkidle")

            if self.solve_cloudflare:
                await self._async_solve_cloudflare(page)
                # Make sure the page is fully loaded after the captcha
                await page.wait_for_load_state(state="load")
                await page.wait_for_load_state(state="domcontentloaded")
                if self.network_idle:
                    await page.wait_for_load_state("networkidle")

            if self.page_action is not None:
                try:
                    page = await self.page_action(page)
                except Exception as e:
                    log.error(f"Error executing async page_action: {e}")

            if self.wait_selector and type(self.wait_selector) is str:
                try:
                    waiter = page.locator(self.wait_selector)
                    await waiter.first.wait_for(state=self.wait_selector_state)
                    # Wait again after waiting for the selector, helpful with protections like Cloudflare
                    await page.wait_for_load_state(state="load")
                    await page.wait_for_load_state(state="domcontentloaded")
                    if self.network_idle:
                        await page.wait_for_load_state("networkidle")
                except Exception as e:
                    log.error(f"Error waiting for selector {self.wait_selector}: {e}")

            await page.wait_for_timeout(self.wait)
            # In case we didn't catch a document type somehow
            final_response = final_response if final_response else first_response
            if not final_response:
                raise ValueError("Failed to get a response from the page")

            # This will be parsed inside `Response`
            encoding = (
                final_response.headers.get("content-type", "") or "utf-8"
            )  # default encoding
            # PlayWright API sometimes give empty status text for some reason!
            status_text = final_response.status_text or StatusText.get(
                final_response.status
            )

            history = await self._async_process_response_history(first_response)
            try:
                page_content = await page.content()
            except Exception as e:
                log.error(f"Error getting page content in async: {e}")
                page_content = ""

            response = Response(
                url=page.url,
                text=page_content,
                body=page_content.encode("utf-8"),
                status=final_response.status,
                reason=status_text,
                encoding=encoding,
                cookies=tuple(dict(cookie) for cookie in await page.context.cookies()),
                headers=await first_response.all_headers(),
                request_headers=await first_response.request.all_headers(),
                history=history,
                **self.adaptor_arguments,
            )
            await page.close()
            await context.close()

        return response
