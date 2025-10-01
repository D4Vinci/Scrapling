from scrapling.core._types import (
    Callable,
    Dict,
    List,
    Optional,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt.custom import BaseFetcher, Response
from scrapling.engines._browsers._camoufox import StealthySession, AsyncStealthySession


class StealthyFetcher(BaseFetcher):
    """A `Fetcher` class type that is a completely stealthy fetcher that uses a modified version of Firefox.

    It works as real browsers passing almost all online tests/protections based on Camoufox.
    Other added flavors include setting the faked OS fingerprints to match the user's OS, and the referer of every request is set as if this request came from Google's search of this URL's domain.
    """

    @classmethod
    def fetch(
        cls,
        url: str,
        headless: bool = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
        load_dom: bool = True,
        humanize: bool | float = True,
        solve_cloudflare: bool = False,
        wait: int | float = 0,
        timeout: int | float = 30000,
        page_action: Optional[Callable] = None,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[List[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        custom_config: Optional[Dict] = None,
        additional_args: Optional[Dict] = None,
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
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
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object.
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            ValueError(f"The custom parser config must be of type dictionary, got {cls.__class__}")

        with StealthySession(
            wait=wait,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            humanize=humanize,
            load_dom=load_dom,
            disable_ads=disable_ads,
            allow_webgl=allow_webgl,
            page_action=page_action,
            init_script=init_script,
            network_idle=network_idle,
            block_images=block_images,
            block_webrtc=block_webrtc,
            os_randomize=os_randomize,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            solve_cloudflare=solve_cloudflare,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            selector_config={**cls._generate_parser_arguments(), **custom_config},
            additional_args=additional_args or {},
        ) as engine:
            return engine.fetch(url)

    @classmethod
    async def async_fetch(
        cls,
        url: str,
        headless: bool = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
        load_dom: bool = True,
        humanize: bool | float = True,
        solve_cloudflare: bool = False,
        wait: int | float = 0,
        timeout: int | float = 30000,
        page_action: Optional[Callable] = None,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[List[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        custom_config: Optional[Dict] = None,
        additional_args: Optional[Dict] = None,
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
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
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object.
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            ValueError(f"The custom parser config must be of type dictionary, got {cls.__class__}")

        async with AsyncStealthySession(
            wait=wait,
            max_pages=1,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            humanize=humanize,
            load_dom=load_dom,
            disable_ads=disable_ads,
            allow_webgl=allow_webgl,
            page_action=page_action,
            init_script=init_script,
            network_idle=network_idle,
            block_images=block_images,
            block_webrtc=block_webrtc,
            os_randomize=os_randomize,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            solve_cloudflare=solve_cloudflare,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            selector_config={**cls._generate_parser_arguments(), **custom_config},
            additional_args=additional_args or {},
        ) as engine:
            return await engine.fetch(url)
