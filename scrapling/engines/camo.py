import logging
from scrapling._types import Union, Callable, Optional

from .tools import check_type_validity, get_os_name, generate_convincing_referer

from camoufox.sync_api import Camoufox


def _do_nothing(page):
    # Anything
    return page


class CamoufoxEngine:
    def __init__(
            self, headless: Union[bool, str] = True,
            block_images: Optional[bool] = True,
            block_webrtc: Optional[bool] = False,
            network_idle: Optional[bool] = False,
            timeout: Optional[float] = 30000,
            page_action: Callable = _do_nothing,
            wait_selector: Optional[str] = None,
            wait_selector_state: str = 'attached',
    ):
        self.headless = headless
        self.block_images = bool(block_images)
        self.block_webrtc = bool(block_webrtc)
        self.network_idle = bool(network_idle)
        self.timeout = check_type_validity(timeout, [int, float], 30000)
        if callable(page_action):
            self.page_action = page_action
        else:
            self.page_action = _do_nothing
            logging.error('[Ignored] Argument "page_action" must be callable')

        self.wait_selector = wait_selector
        self.wait_selector_state = wait_selector_state

    def fetch(self, url: str):
        with Camoufox(
                headless=self.headless,
                block_images=self.block_images,
                os=get_os_name(),
                block_webrtc=self.block_webrtc,
        ) as browser:
            page = browser.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            page.goto(url, referer=generate_convincing_referer(url))
            page.wait_for_load_state(state="load")
            page.wait_for_load_state(state="domcontentloaded")
            if self.network_idle:
                page.wait_for_load_state('networkidle')

            page = self.page_action(page)

            if self.wait_selector and type(self.wait_selector) is str:
                waiter = page.locator(self.wait_selector)
                waiter.wait_for(state=self.wait_selector_state)

            html = page.content()
            page.close()
        return html
