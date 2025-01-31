import json

from scrapling.core._types import (Callable, Dict, Optional,
                                   SelectorWaitStates, Union)
from scrapling.core.utils import log, lru_cache
from scrapling.engines.constants import (DEFAULT_STEALTH_FLAGS,
                                         NSTBROWSER_DEFAULT_QUERY)
from scrapling.engines.toolbelt import (Response, StatusText,
                                        async_intercept_route,
                                        check_type_validity, construct_cdp_url,
                                        construct_proxy_dict,
                                        generate_convincing_referer,
                                        generate_headers, intercept_route,
                                        js_bypass_path)


class PlaywrightEngine:
    def __init__(
            self, headless: Union[bool, str] = True,
            disable_resources: bool = False,
            useragent: Optional[str] = None,
            network_idle: Optional[bool] = False,
            timeout: Optional[float] = 30000,
            page_action: Callable = None,
            wait_selector: Optional[str] = None,
            locale: Optional[str] = 'en-US',
            wait_selector_state: SelectorWaitStates = 'attached',
            stealth: Optional[bool] = False,
            real_chrome: Optional[bool] = False,
            hide_canvas: Optional[bool] = False,
            disable_webgl: Optional[bool] = False,
            cdp_url: Optional[str] = None,
            nstbrowser_mode: Optional[bool] = False,
            nstbrowser_config: Optional[Dict] = None,
            google_search: Optional[bool] = True,
            extra_headers: Optional[Dict[str, str]] = None,
            proxy: Optional[Union[str, Dict[str, str]]] = None,
            adaptor_arguments: Dict = None
    ):
        """An engine that utilizes PlayWright library, check the `PlayWrightFetcher` class for more documentation.

        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have chrome browser installed on your device, enable this and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it have to be used with `cdp_url` argument or it will get completely ignored.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        """
        self.headless = headless
        self.locale = check_type_validity(locale, [str], 'en-US', param_name='locale')
        self.disable_resources = disable_resources
        self.network_idle = bool(network_idle)
        self.stealth = bool(stealth)
        self.hide_canvas = bool(hide_canvas)
        self.disable_webgl = bool(disable_webgl)
        self.real_chrome = bool(real_chrome)
        self.google_search = bool(google_search)
        self.extra_headers = extra_headers or {}
        self.proxy = construct_proxy_dict(proxy)
        self.cdp_url = cdp_url
        self.useragent = useragent
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
        self.nstbrowser_mode = bool(nstbrowser_mode)
        self.nstbrowser_config = nstbrowser_config
        self.adaptor_arguments = adaptor_arguments if adaptor_arguments else {}
        self.harmful_default_args = [
            # This will be ignored to avoid detection more and possibly avoid the popup crashing bug abuse: https://issues.chromium.org/issues/340836884
            '--enable-automation',
            '--disable-popup-blocking',
            # '--disable-component-update',
            # '--disable-default-apps',
            # '--disable-extensions',
        ]

    def _cdp_url_logic(self) -> str:
        """Constructs new CDP URL if NSTBrowser is enabled otherwise return CDP URL as it is
        :return: CDP URL
        """
        cdp_url = self.cdp_url
        if self.nstbrowser_mode:
            if self.nstbrowser_config and isinstance(self.nstbrowser_config, dict):
                config = self.nstbrowser_config
            else:
                query = NSTBROWSER_DEFAULT_QUERY.copy()
                if self.stealth:
                    flags = self.__set_flags()
                    query.update({
                        "args": dict(zip(flags, [''] * len(flags))),  # browser args should be a dictionary
                    })

                config = {
                    'config': json.dumps(query),
                    # 'token': ''
                }
            cdp_url = construct_cdp_url(cdp_url, config)
        else:
            # To validate it
            cdp_url = construct_cdp_url(cdp_url)

        return cdp_url

    @lru_cache(typed=True)
    def __set_flags(self):
        """Returns the flags that will be used while launching the browser if stealth mode is enabled"""
        flags = DEFAULT_STEALTH_FLAGS
        if self.hide_canvas:
            flags += ('--fingerprinting-canvas-image-data-noise',)
        if self.disable_webgl:
            flags += ('--disable-webgl', '--disable-webgl-image-chromium', '--disable-webgl2',)

        return flags

    def __launch_kwargs(self):
        """Creates the arguments we will use while launching playwright's browser"""
        launch_kwargs = {'headless': self.headless, 'ignore_default_args': self.harmful_default_args, 'channel': 'chrome' if self.real_chrome else 'chromium'}
        if self.stealth:
            launch_kwargs.update({'args': self.__set_flags(), 'chromium_sandbox': True})

        return launch_kwargs

    def __context_kwargs(self):
        """Creates the arguments for the browser context"""
        context_kwargs = {
            "proxy": self.proxy,
            "locale": self.locale,
            "color_scheme": 'dark',  # Bypasses the 'prefersLightColor' check in creepjs
            "device_scale_factor": 2,
            "extra_http_headers": self.extra_headers if self.extra_headers else {},
            "user_agent": self.useragent if self.useragent else generate_headers(browser_mode=True).get('User-Agent'),
        }
        if self.stealth:
            context_kwargs.update({
                'is_mobile': False,
                'has_touch': False,
                # I'm thinking about disabling it to rest from all Service Workers headache but let's keep it as it is for now
                'service_workers': 'allow',
                'ignore_https_errors': True,
                'screen': {'width': 1920, 'height': 1080},
                'viewport': {'width': 1920, 'height': 1080},
                'permissions': ['geolocation', 'notifications']
            })

        return context_kwargs

    @lru_cache()
    def __stealth_scripts(self):
        # Basic bypasses nothing fancy as I'm still working on it
        # But with adding these bypasses to the above config, it bypasses many online tests like
        # https://bot.sannysoft.com/
        # https://kaliiiiiiiiii.github.io/brotector/
        # https://pixelscan.net/
        # https://iphey.com/
        # https://www.browserscan.net/bot-detection <== this one also checks for the CDP runtime fingerprint
        # https://arh.antoinevastel.com/bots/areyouheadless/
        # https://prescience-data.github.io/execution-monitor.html
        return tuple(
            js_bypass_path(script) for script in (
                # Order is important
                'webdriver_fully.js', 'window_chrome.js', 'navigator_plugins.js', 'pdf_viewer.js',
                'notification_permission.js', 'screen_props.js', 'playwright_fingerprint.js'
            )
        )

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        from playwright.sync_api import Response as PlaywrightResponse
        if not self.stealth or self.real_chrome:
            # Because rebrowser_playwright doesn't play well with real browsers
            from playwright.sync_api import sync_playwright
        else:
            from rebrowser_playwright.sync_api import sync_playwright

        # Store the final response
        final_response = None

        def handle_response(finished_response: PlaywrightResponse):
            nonlocal final_response
            if finished_response.request.resource_type == "document" and finished_response.request.is_navigation_request():
                final_response = finished_response

        with sync_playwright() as p:
            # Creating the browser
            if self.cdp_url:
                cdp_url = self._cdp_url_logic()
                browser = p.chromium.connect_over_cdp(endpoint_url=cdp_url)
            else:
                browser = p.chromium.launch(**self.__launch_kwargs())

            context = browser.new_context(**self.__context_kwargs())
            # Finally we are in business
            page = context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            # Listen for all responses
            page.on("response", handle_response)

            if self.extra_headers:
                page.set_extra_http_headers(self.extra_headers)

            if self.disable_resources:
                page.route("**/*", intercept_route)

            if self.stealth:
                for script in self.__stealth_scripts():
                    page.add_init_script(path=script)

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
        """Async version of `fetch`

        :param url: Target url.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        from playwright.async_api import Response as PlaywrightResponse
        if not self.stealth or self.real_chrome:
            # Because rebrowser_playwright doesn't play well with real browsers
            from playwright.async_api import async_playwright
        else:
            from rebrowser_playwright.async_api import async_playwright

        # Store the final response
        final_response = None

        async def handle_response(finished_response: PlaywrightResponse):
            nonlocal final_response
            if finished_response.request.resource_type == "document" and finished_response.request.is_navigation_request():
                final_response = finished_response

        async with async_playwright() as p:
            # Creating the browser
            if self.cdp_url:
                cdp_url = self._cdp_url_logic()
                browser = await p.chromium.connect_over_cdp(endpoint_url=cdp_url)
            else:
                browser = await p.chromium.launch(**self.__launch_kwargs())

            context = await browser.new_context(**self.__context_kwargs())
            # Finally we are in business
            page = await context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            # Listen for all responses
            page.on("response", handle_response)

            if self.extra_headers:
                await page.set_extra_http_headers(self.extra_headers)

            if self.disable_resources:
                await page.route("**/*", async_intercept_route)

            if self.stealth:
                for script in self.__stealth_scripts():
                    await page.add_init_script(path=script)

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
