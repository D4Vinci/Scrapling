from camoufox import DefaultAddons
from camoufox.async_api import AsyncCamoufox
from camoufox.sync_api import Camoufox

from scrapling.core._types import (Callable, Dict, List, Literal, Optional,
                                   SelectorWaitStates, Union)
from scrapling.core.utils import log
from scrapling.engines.toolbelt import (Response, StatusText,
                                        async_intercept_route,
                                        check_type_validity,
                                        construct_proxy_dict,
                                        generate_convincing_referer,
                                        get_os_name, intercept_route)


class CamoufoxEngine:
    def __init__(
            self, headless: Optional[Union[bool, Literal['virtual']]] = True, block_images: Optional[bool] = False, disable_resources: Optional[bool] = False,
            block_webrtc: Optional[bool] = False, allow_webgl: Optional[bool] = True, network_idle: Optional[bool] = False, humanize: Optional[Union[bool, float]] = True,
            timeout: Optional[float] = 30000, page_action: Callable = None, wait_selector: Optional[str] = None, addons: Optional[List[str]] = None,
            wait_selector_state: Optional[SelectorWaitStates] = 'attached', google_search: Optional[bool] = True, extra_headers: Optional[Dict[str, str]] = None,
            proxy: Optional[Union[str, Dict[str, str]]] = None, os_randomize: Optional[bool] = None, disable_ads: Optional[bool] = False,
            geoip: Optional[bool] = False,
            adaptor_arguments: Dict = None,
    ):
        """An engine that utilizes Camoufox library, check the `StealthyFetcher` class for more documentation.

        :param headless: Run the browser in headless/hidden (default), virtual screen mode, or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param block_webrtc: Blocks WebRTC entirely.
        :param addons: List of Firefox addons to use. Must be paths to extracted addons.
        :param humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param allow_webgl: Enabled by default. Disabling it WebGL not recommended as many WAFs now checks if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param disable_ads: Disabled by default, this installs `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, & spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
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
        self.proxy = construct_proxy_dict(proxy)
        self.addons = addons or []
        self.humanize = humanize
        self.timeout = check_type_validity(timeout, [int, float], 30000)
        if page_action is not None:
            if callable(page_action):
                self.page_action = page_action
            else:
                self.page_action = None
                log.error('[Ignored] Argument "page_action" must be callable')
        else:
            self.page_action = None

        self.wait_selector = wait_selector
        self.wait_selector_state = wait_selector_state
        self.adaptor_arguments = adaptor_arguments if adaptor_arguments else {}

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        addons = [] if self.disable_ads else [DefaultAddons.UBO]
        # Store the final response
        final_response = None

        def handle_response(finished_response):
            nonlocal final_response
            if finished_response.request.resource_type == "document" and finished_response.request.is_navigation_request():
                final_response = finished_response

        with Camoufox(
                geoip=self.geoip,
                proxy=self.proxy,
                disable_coop=True,
                enable_cache=True,
                addons=self.addons,
                exclude_addons=addons,
                headless=self.headless,
                humanize=self.humanize,
                i_know_what_im_doing=True,  # To turn warnings off with the user configurations
                allow_webgl=self.allow_webgl,
                block_webrtc=self.block_webrtc,
                block_images=self.block_images,  # Careful! it makes some websites doesn't finish loading at all like stackoverflow even in headful
                os=None if self.os_randomize else get_os_name(),
        ) as browser:
            page = browser.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            # Listen for all responses
            page.on("response", handle_response)
            if self.disable_resources:
                page.route("**/*", intercept_route)

            if self.extra_headers:
                page.set_extra_http_headers(self.extra_headers)

            first_response = page.goto(url, referer=generate_convincing_referer(url) if self.google_search else None)
            page.wait_for_load_state(state="domcontentloaded")
            if self.network_idle:
                page.wait_for_load_state('networkidle')

            if self.page_action is not None:
                page = self.page_action(page)

            if self.wait_selector and type(self.wait_selector) is str:
                waiter = page.locator(self.wait_selector)
                waiter.first.wait_for(state=self.wait_selector_state)
                # Wait again after waiting for the selector, helpful with protections like Cloudflare
                page.wait_for_load_state(state="load")
                page.wait_for_load_state(state="domcontentloaded")
                if self.network_idle:
                    page.wait_for_load_state('networkidle')

            # In case we didn't catch a document type somehow
            final_response = final_response if final_response else first_response
            # This will be parsed inside `Response`
            encoding = final_response.headers.get('content-type', '') or 'utf-8'  # default encoding
            # PlayWright API sometimes give empty status text for some reason!
            status_text = final_response.status_text or StatusText.get(final_response.status)

            response = Response(
                url=page.url,
                text=page.content(),
                body=page.content().encode('utf-8'),
                status=final_response.status,
                reason=status_text,
                encoding=encoding,
                cookies={cookie['name']: cookie['value'] for cookie in page.context.cookies()},
                headers=first_response.all_headers(),
                request_headers=first_response.request.all_headers(),
                **self.adaptor_arguments
            )
            page.close()

        return response

    async def async_fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        addons = [] if self.disable_ads else [DefaultAddons.UBO]
        # Store the final response
        final_response = None

        async def handle_response(finished_response):
            nonlocal final_response
            if finished_response.request.resource_type == "document" and finished_response.request.is_navigation_request():
                final_response = finished_response

        async with AsyncCamoufox(
                geoip=self.geoip,
                proxy=self.proxy,
                disable_coop=True,
                enable_cache=True,
                addons=self.addons,
                exclude_addons=addons,
                headless=self.headless,
                humanize=self.humanize,
                i_know_what_im_doing=True,  # To turn warnings off with the user configurations
                allow_webgl=self.allow_webgl,
                block_webrtc=self.block_webrtc,
                block_images=self.block_images,  # Careful! it makes some websites doesn't finish loading at all like stackoverflow even in headful
                os=None if self.os_randomize else get_os_name(),
        ) as browser:
            page = await browser.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            # Listen for all responses
            page.on("response", handle_response)
            if self.disable_resources:
                await page.route("**/*", async_intercept_route)

            if self.extra_headers:
                await page.set_extra_http_headers(self.extra_headers)

            first_response = await page.goto(url, referer=generate_convincing_referer(url) if self.google_search else None)
            await page.wait_for_load_state(state="domcontentloaded")
            if self.network_idle:
                await page.wait_for_load_state('networkidle')

            if self.page_action is not None:
                page = await self.page_action(page)

            if self.wait_selector and type(self.wait_selector) is str:
                waiter = page.locator(self.wait_selector)
                await waiter.first.wait_for(state=self.wait_selector_state)
                # Wait again after waiting for the selector, helpful with protections like Cloudflare
                await page.wait_for_load_state(state="load")
                await page.wait_for_load_state(state="domcontentloaded")
                if self.network_idle:
                    await page.wait_for_load_state('networkidle')

            # In case we didn't catch a document type somehow
            final_response = final_response if final_response else first_response
            # This will be parsed inside `Response`
            encoding = final_response.headers.get('content-type', '') or 'utf-8'  # default encoding
            # PlayWright API sometimes give empty status text for some reason!
            status_text = final_response.status_text or StatusText.get(final_response.status)

            response = Response(
                url=page.url,
                text=await page.content(),
                body=(await page.content()).encode('utf-8'),
                status=final_response.status,
                reason=status_text,
                encoding=encoding,
                cookies={cookie['name']: cookie['value'] for cookie in await page.context.cookies()},
                headers=await first_response.all_headers(),
                request_headers=await first_response.request.all_headers(),
                **self.adaptor_arguments
            )
            await page.close()

        return response
