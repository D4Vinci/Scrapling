import json
import logging
from scrapling.core._types import Union, Callable, Optional, List, Dict

from scrapling.engines.constants import DEFAULT_STEALTH_FLAGS, NSTBROWSER_DEFAULT_QUERY
from scrapling.engines.toolbelt import (
    Response,
    do_nothing,
    js_bypass_path,
    intercept_route,
    generate_headers,
    check_type_validity,
    construct_cdp_url,
    generate_convincing_referer,
)


class PlaywrightEngine:
    def __init__(
            self, headless: Union[bool, str] = True,
            disable_resources: bool = False,
            useragent: Optional[str] = None,
            network_idle: Optional[bool] = False,
            timeout: Optional[float] = 30000,
            page_action: Callable = do_nothing,
            wait_selector: Optional[str] = None,
            wait_selector_state: Optional[str] = 'attached',
            stealth: bool = False,
            hide_canvas: bool = True,
            disable_webgl: bool = False,
            cdp_url: Optional[str] = None,
            nstbrowser_mode: bool = False,
            nstbrowser_config: Optional[Dict] = None,
            google_search: Optional[bool] = True,
            extra_headers: Optional[Dict[str, str]] = None,
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
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it have to be used with `cdp_url` argument or it will get completely ignored.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        """
        self.headless = headless
        self.disable_resources = disable_resources
        self.network_idle = bool(network_idle)
        self.stealth = bool(stealth)
        self.hide_canvas = bool(hide_canvas)
        self.disable_webgl = bool(disable_webgl)
        self.google_search = bool(google_search)
        self.extra_headers = extra_headers or {}
        self.cdp_url = cdp_url
        self.useragent = useragent
        self.timeout = check_type_validity(timeout, [int, float], 30000)
        if callable(page_action):
            self.page_action = page_action
        else:
            self.page_action = do_nothing
            logging.error('[Ignored] Argument "page_action" must be callable')

        self.wait_selector = wait_selector
        self.wait_selector_state = wait_selector_state
        self.nstbrowser_mode = bool(nstbrowser_mode)
        self.nstbrowser_config = nstbrowser_config
        self.adaptor_arguments = adaptor_arguments if adaptor_arguments else {}

    def _cdp_url_logic(self, flags: Optional[List] = None) -> str:
        """Constructs new CDP URL if NSTBrowser is enabled otherwise return CDP URL as it is

        :param flags: Chrome flags to be added to NSTBrowser query
        :return: CDP URL
        """
        cdp_url = self.cdp_url
        if self.nstbrowser_mode:
            if self.nstbrowser_config and type(self.nstbrowser_config) is Dict:
                config = self.nstbrowser_config
            else:
                query = NSTBROWSER_DEFAULT_QUERY.copy()
                if flags:
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

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        if not self.stealth:
            from playwright.sync_api import sync_playwright
        else:
            from rebrowser_playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # Handle the UserAgent early
            if self.useragent:
                extra_headers = {}
                useragent = self.useragent
            else:
                extra_headers = generate_headers(browser_mode=True)
                useragent = extra_headers.get('User-Agent')

            # Prepare the flags before diving
            flags = DEFAULT_STEALTH_FLAGS
            if self.hide_canvas:
                flags += ['--fingerprinting-canvas-image-data-noise']
            if self.disable_webgl:
                flags += ['--disable-webgl', '--disable-webgl-image-chromium', '--disable-webgl2']

            # Creating the browser
            if self.cdp_url:
                cdp_url = self._cdp_url_logic(flags if self.stealth else None)
                browser = p.chromium.connect_over_cdp(endpoint_url=cdp_url)
            else:
                if self.stealth:
                    browser = p.chromium.launch(headless=self.headless, args=flags, ignore_default_args=['--enable-automation'], chromium_sandbox=True)
                else:
                    browser = p.chromium.launch(headless=self.headless, ignore_default_args=['--enable-automation'])

            # Creating the context
            if self.stealth:
                context = browser.new_context(
                    locale='en-US',
                    is_mobile=False,
                    has_touch=False,
                    color_scheme='dark',  # Bypasses the 'prefersLightColor' check in creepjs
                    user_agent=useragent,
                    device_scale_factor=2,
                    # I'm thinking about disabling it to rest from all Service Workers headache but let's keep it as it is for now
                    service_workers="allow",
                    ignore_https_errors=True,
                    extra_http_headers=extra_headers,
                    screen={"width": 1920, "height": 1080},
                    viewport={"width": 1920, "height": 1080},
                    permissions=["geolocation", 'notifications'],
                )
            else:
                context = browser.new_context(
                    color_scheme='dark',
                    user_agent=useragent,
                    device_scale_factor=2,
                    extra_http_headers=extra_headers
                )

            # Finally we are in business
            page = context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)

            if self.extra_headers:
                page.set_extra_http_headers(self.extra_headers)

            if self.disable_resources:
                page.route("**/*", intercept_route)

            if self.stealth:
                # Basic bypasses nothing fancy as I'm still working on it
                # But with adding these bypasses to the above config, it bypasses many online tests like
                # https://bot.sannysoft.com/
                # https://kaliiiiiiiiii.github.io/brotector/
                # https://pixelscan.net/
                # https://iphey.com/
                # https://www.browserscan.net/bot-detection <== this one also checks for the CDP runtime fingerprint
                # https://arh.antoinevastel.com/bots/areyouheadless/
                # https://prescience-data.github.io/execution-monitor.html
                page.add_init_script(path=js_bypass_path('webdriver_fully.js'))
                page.add_init_script(path=js_bypass_path('window_chrome.js'))
                page.add_init_script(path=js_bypass_path('navigator_plugins.js'))
                page.add_init_script(path=js_bypass_path('pdf_viewer.js'))
                page.add_init_script(path=js_bypass_path('notification_permission.js'))
                page.add_init_script(path=js_bypass_path('screen_props.js'))
                page.add_init_script(path=js_bypass_path('playwright_fingerprint.js'))

            res = page.goto(url, referer=generate_convincing_referer(url) if self.google_search else None)
            page.wait_for_load_state(state="domcontentloaded")
            if self.network_idle:
                page.wait_for_load_state('networkidle')

            page = self.page_action(page)

            if self.wait_selector and type(self.wait_selector) is str:
                waiter = page.locator(self.wait_selector)
                waiter.wait_for(state=self.wait_selector_state)

            content_type = res.headers.get('content-type', '')
            # Parse charset from content-type
            encoding = 'utf-8'  # default encoding
            if 'charset=' in content_type.lower():
                encoding = content_type.lower().split('charset=')[-1].split(';')[0].strip()

            response = Response(
                url=res.url,
                text=page.content(),
                content=res.body(),
                status=res.status,
                reason=res.status_text,
                encoding=encoding,
                cookies={cookie['name']: cookie['value'] for cookie in page.context.cookies()},
                headers=res.all_headers(),
                request_headers=res.request.all_headers(),
                adaptor_arguments=self.adaptor_arguments
            )
            page.close()
        return response
