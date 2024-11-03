import logging
from scrapling.core._types import Union, Callable, Optional, Dict

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
            self, headless: Union[bool, str] = True,
            block_images: Optional[bool] = False,
            disable_resources: Optional[bool] = False,
            block_webrtc: Optional[bool] = False,
            allow_webgl: Optional[bool] = False,
            network_idle: Optional[bool] = False,
            timeout: Optional[float] = 30000,
            page_action: Callable = do_nothing,
            wait_selector: Optional[str] = None,
            wait_selector_state: str = 'attached',
            adaptor_arguments: Dict = None
    ):
        self.headless = headless
        self.block_images = bool(block_images)
        self.disable_resources = bool(disable_resources)
        self.block_webrtc = bool(block_webrtc)
        self.allow_webgl = bool(allow_webgl)
        self.network_idle = bool(network_idle)
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
        with Camoufox(
                headless=self.headless,
                block_images=self.block_images,  # Careful! it makes some websites doesn't finish loading at all like stackoverflow even in headful
                os=get_os_name(),
                block_webrtc=self.block_webrtc,
                allow_webgl=self.allow_webgl,
        ) as browser:
            page = browser.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            if self.disable_resources:
                page.route("**/*", intercept_route)

            res = page.goto(url, referer=generate_convincing_referer(url))
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
