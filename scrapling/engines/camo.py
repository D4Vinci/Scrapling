import logging
from scrapling.core._types import Union, Callable, Optional, Dict, List, Literal

from scrapling.engines.toolbelt import (
    Response,
    do_nothing,
    get_os_name,
    intercept_route,
    check_type_validity,
    generate_convincing_referer,
)

from camoufox.sync_api import Camoufox


class CamoufoxEngine:
    def __init__(
            self, headless: Optional[Union[bool, Literal['virtual']]] = True, block_images: Optional[bool] = False, disable_resources: Optional[bool] = False,
            block_webrtc: Optional[bool] = False, allow_webgl: Optional[bool] = False, network_idle: Optional[bool] = False, humanize: Optional[Union[bool, float]] = True,
            timeout: Optional[float] = 30000, page_action: Callable = do_nothing, wait_selector: Optional[str] = None, addons: Optional[List[str]] = None,
            wait_selector_state: str = 'attached', google_search: Optional[bool] = True, extra_headers: Optional[Dict[str, str]] = None, adaptor_arguments: Dict = None
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
        :param humanize: Humanize the cursor movement. Takes either True, or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param allow_webgl: Whether to allow WebGL. To prevent leaks, only use this for special cases.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that's used in all operations and waits through the page. Default is 30000.
        :param page_action: Added for automation. A function that takes the `page` object, do the automation you need, then return `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to headers on the request. The referer set by the `google_search` argument takes priority over the referer set here if used together.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        """
        self.headless = headless
        self.block_images = bool(block_images)
        self.disable_resources = bool(disable_resources)
        self.block_webrtc = bool(block_webrtc)
        self.allow_webgl = bool(allow_webgl)
        self.network_idle = bool(network_idle)
        self.google_search = bool(google_search)
        self.extra_headers = extra_headers or {}
        self.addons = addons or []
        self.humanize = humanize
        self.timeout = check_type_validity(timeout, [int, float], 30000)
        if callable(page_action):
            self.page_action = page_action
        else:
            self.page_action = do_nothing
            logging.error('[Ignored] Argument "page_action" must be callable')

        self.wait_selector = wait_selector
        self.wait_selector_state = wait_selector_state
        self.adaptor_arguments = adaptor_arguments if adaptor_arguments else {}

    def fetch(self, url: str) -> Response:
        """Opens up the browser and do your request based on your chosen options.

        :param url: Target url.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        with Camoufox(
                headless=self.headless,
                block_images=self.block_images,  # Careful! it makes some websites doesn't finish loading at all like stackoverflow even in headful
                os=get_os_name(),
                block_webrtc=self.block_webrtc,
                allow_webgl=self.allow_webgl,
                addons=self.addons,
                humanize=self.humanize,
                i_know_what_im_doing=True,  # To turn warnings off with user configurations
        ) as browser:
            page = browser.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            if self.disable_resources:
                page.route("**/*", intercept_route)

            if self.extra_headers:
                page.set_extra_http_headers(self.extra_headers)

            if self.google_search:
                res = page.goto(url, referer=generate_convincing_referer(url))
            else:
                res = page.goto(url)

            page.wait_for_load_state(state="load")
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
                text=res.text(),
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
