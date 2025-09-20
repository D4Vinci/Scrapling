from time import time
from asyncio import sleep as asyncio_sleep, Lock

from camoufox import DefaultAddons
from playwright.sync_api import BrowserContext, Playwright
from playwright.async_api import (
    BrowserContext as AsyncBrowserContext,
    Playwright as AsyncPlaywright,
)
from camoufox.utils import (
    launch_options as generate_launch_options,
    installed_verstr as camoufox_version,
)

from scrapling.engines.toolbelt.navigation import intercept_route, async_intercept_route
from scrapling.core._types import (
    Any,
    Dict,
    Optional,
)
from ._page import PageInfo, PagePool
from ._config_tools import _compiled_stealth_scripts
from ._config_tools import _launch_kwargs, _context_kwargs
from scrapling.engines.toolbelt.fingerprints import get_os_name
from ._validators import validate, PlaywrightConfig, CamoufoxConfig

__ff_version_str__ = camoufox_version().split(".", 1)[0]


class SyncSession:
    def __init__(self, max_pages: int = 1):
        self.max_pages = max_pages
        self.page_pool = PagePool(max_pages)
        self._max_wait_for_page = 60
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self._closed = False

    def _get_page(
        self,
        timeout: int | float,
        extra_headers: Optional[Dict[str, str]],
        disable_resources: bool,
    ) -> PageInfo:  # pragma: no cover
        """Get a new page to use"""

        # No need to check if a page is available or not in sync code because the code blocked before reaching here till the page closed, ofc.
        page = self.context.new_page()
        page.set_default_navigation_timeout(timeout)
        page.set_default_timeout(timeout)
        if extra_headers:
            page.set_extra_http_headers(extra_headers)

        if disable_resources:
            page.route("**/*", intercept_route)

        if getattr(self, "stealth", False):
            for script in _compiled_stealth_scripts():
                page.add_init_script(script=script)

        return self.page_pool.add_page(page)

    @staticmethod
    def _get_with_precedence(request_value: Any, session_value: Any, sentinel_value: object) -> Any:
        """Get value with request-level priority over session-level"""
        return request_value if request_value is not sentinel_value else session_value

    def get_pool_stats(self) -> Dict[str, int]:
        """Get statistics about the current page pool"""
        return {
            "total_pages": self.page_pool.pages_count,
            "busy_pages": self.page_pool.busy_count,
            "max_pages": self.max_pages,
        }


class AsyncSession(SyncSession):
    def __init__(self, max_pages: int = 1):
        super().__init__(max_pages)
        self.playwright: Optional[AsyncPlaywright] = None
        self.context: Optional[AsyncBrowserContext] = None
        self._lock = Lock()

    async def _get_page(
        self,
        timeout: int | float,
        extra_headers: Optional[Dict[str, str]],
        disable_resources: bool,
    ) -> PageInfo:  # pragma: no cover
        """Get a new page to use"""
        async with self._lock:
            # If we're at max capacity after cleanup, wait for busy pages to finish
            if self.page_pool.pages_count >= self.max_pages:
                start_time = time()
                while time() - start_time < self._max_wait_for_page:
                    await asyncio_sleep(0.05)
                    if self.page_pool.pages_count < self.max_pages:
                        break
                else:
                    raise TimeoutError(
                        f"No pages finished to clear place in the pool within the {self._max_wait_for_page}s timeout period"
                    )

            page = await self.context.new_page()
            page.set_default_navigation_timeout(timeout)
            page.set_default_timeout(timeout)
            if extra_headers:
                await page.set_extra_http_headers(extra_headers)

            if disable_resources:
                await page.route("**/*", async_intercept_route)

            if getattr(self, "stealth", False):
                for script in _compiled_stealth_scripts():
                    await page.add_init_script(script=script)

            return self.page_pool.add_page(page)


class DynamicSessionMixin:
    def __validate__(self, **params):
        config = validate(params, model=PlaywrightConfig)

        self.max_pages = config.max_pages
        self.headless = config.headless
        self.hide_canvas = config.hide_canvas
        self.disable_webgl = config.disable_webgl
        self.real_chrome = config.real_chrome
        self.stealth = config.stealth
        self.google_search = config.google_search
        self.wait = config.wait
        self.proxy = config.proxy
        self.locale = config.locale
        self.extra_headers = config.extra_headers
        self.useragent = config.useragent
        self.timeout = config.timeout
        self.cookies = config.cookies
        self.disable_resources = config.disable_resources
        self.cdp_url = config.cdp_url
        self.network_idle = config.network_idle
        self.load_dom = config.load_dom
        self.wait_selector = config.wait_selector
        self.init_script = config.init_script
        self.wait_selector_state = config.wait_selector_state
        self.selector_config = config.selector_config
        self.page_action = config.page_action
        self._headers_keys = set(map(str.lower, self.extra_headers.keys())) if self.extra_headers else set()
        self.__initiate_browser_options__()

    def __initiate_browser_options__(self):
        if not self.cdp_url:
            # `launch_options` is used with persistent context
            self.launch_options = dict(
                _launch_kwargs(
                    self.headless,
                    self.proxy,
                    self.locale,
                    tuple(self.extra_headers.items()) if self.extra_headers else tuple(),
                    self.useragent,
                    self.real_chrome,
                    self.stealth,
                    self.hide_canvas,
                    self.disable_webgl,
                )
            )
            self.launch_options["extra_http_headers"] = dict(self.launch_options["extra_http_headers"])
            self.launch_options["proxy"] = dict(self.launch_options["proxy"]) or None
            self.context_options = dict()
        else:
            # while `context_options` is left to be used when cdp mode is enabled
            self.launch_options = dict()
            self.context_options = dict(
                _context_kwargs(
                    self.proxy,
                    self.locale,
                    tuple(self.extra_headers.items()) if self.extra_headers else tuple(),
                    self.useragent,
                    self.stealth,
                )
            )
            self.context_options["extra_http_headers"] = dict(self.context_options["extra_http_headers"])
            self.context_options["proxy"] = dict(self.context_options["proxy"]) or None


class StealthySessionMixin:
    def __validate__(self, **params):
        config = validate(params, model=CamoufoxConfig)

        self.max_pages = config.max_pages
        self.headless = config.headless
        self.block_images = config.block_images
        self.disable_resources = config.disable_resources
        self.block_webrtc = config.block_webrtc
        self.allow_webgl = config.allow_webgl
        self.network_idle = config.network_idle
        self.load_dom = config.load_dom
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
        self.page_action = config.page_action
        self._headers_keys = set(map(str.lower, self.extra_headers.keys())) if self.extra_headers else set()
        self.__initiate_browser_options__()

    def __initiate_browser_options__(self):
        """Initiate browser options."""
        self.launch_options = generate_launch_options(
            **{
                "geoip": self.geoip,
                "proxy": dict(self.proxy) if self.proxy else self.proxy,
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
                "ff_version": __ff_version_str__,
                "firefox_user_prefs": {
                    # This is what enabling `enable_cache` does internally, so we do it from here instead
                    "browser.sessionhistory.max_entries": 10,
                    "browser.sessionhistory.max_total_viewers": -1,
                    "browser.cache.memory.enable": True,
                    "browser.cache.disk_cache_ssl": True,
                    "browser.cache.disk.smart_size.enabled": True,
                },
                **self.additional_args,
            }
        )

    @staticmethod
    def _detect_cloudflare(page_content: str) -> str | None:
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
