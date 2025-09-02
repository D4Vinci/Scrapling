from scrapling.core._types import (
    Callable,
    Dict,
    List,
    Optional,
    SelectorWaitStates,
    Iterable,
)
from scrapling.engines import (
    FetcherSession,
    StealthySession,
    AsyncStealthySession,
    DynamicSession,
    AsyncDynamicSession,
    FetcherClient as _FetcherClient,
    AsyncFetcherClient as _AsyncFetcherClient,
)
from scrapling.engines.toolbelt import BaseFetcher, Response

__FetcherClientInstance__ = _FetcherClient()
__AsyncFetcherClientInstance__ = _AsyncFetcherClient()


class Fetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on `curl_cffi`."""

    get = __FetcherClientInstance__.get
    post = __FetcherClientInstance__.post
    put = __FetcherClientInstance__.put
    delete = __FetcherClientInstance__.delete


class AsyncFetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on `curl_cffi`."""

    get = __AsyncFetcherClientInstance__.get
    post = __AsyncFetcherClientInstance__.post
    put = __AsyncFetcherClientInstance__.put
    delete = __AsyncFetcherClientInstance__.delete


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
        :param solve_cloudflare: Solves all 3 types of the Cloudflare's Turnstile wait page before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
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
            ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        with StealthySession(
            wait=wait,
            max_pages=1,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            humanize=humanize,
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
        :param solve_cloudflare: Solves all 3 types of the Cloudflare's Turnstile wait page before returning the response to you.
        :param allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
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
            ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

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


class DynamicFetcher(BaseFetcher):
    """A `Fetcher` class type that provide many options, all of them are based on PlayWright.

     Using this Fetcher class, you can do requests with:
        - Vanilla Playwright without any modifications other than the ones you chose.
        - Stealthy Playwright with the stealth mode I wrote for it. It's still a work in progress, but it bypasses many online tests like bot.sannysoft.com
            Some of the things stealth mode does include:
                1) Patches the CDP runtime fingerprint.
                2) Mimics some of the real browsers' properties by injecting several JS files and using custom options.
                3) Using custom flags on launch to hide Playwright even more and make it faster.
                4) Generates real browser's headers of the same type and same user OS, then append it to the request.
        - Real browsers by passing the `real_chrome` argument or the CDP URL of your browser to be controlled by the Fetcher, and most of the options can be enabled on it.
        - NSTBrowser's docker browserless option by passing the CDP URL and enabling `nstbrowser_mode` option.

    > Note that these are the main options with PlayWright, but it can be mixed.
    """

    @classmethod
    def fetch(
        cls,
        url: str,
        headless: bool = True,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: int | float = 0,
        page_action: Optional[Callable] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        cookies: Optional[Iterable[Dict]] = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        custom_config: Optional[Dict] = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :return: A `Response` object.
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            raise ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        with DynamicSession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            cookies=cookies,
            headless=headless,
            useragent=useragent,
            real_chrome=real_chrome,
            page_action=page_action,
            hide_canvas=hide_canvas,
            init_script=init_script,
            network_idle=network_idle,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            selector_config={**cls._generate_parser_arguments(), **custom_config},
        ) as session:
            return session.fetch(url)

    @classmethod
    async def async_fetch(
        cls,
        url: str,
        headless: bool = True,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: int | float = 0,
        page_action: Optional[Callable] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        init_script: Optional[str] = None,
        cookies: Optional[Iterable[Dict]] = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
        custom_config: Optional[Dict] = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :return: A `Response` object.
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            raise ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        async with AsyncDynamicSession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            cookies=cookies,
            headless=headless,
            useragent=useragent,
            max_pages=1,
            real_chrome=real_chrome,
            page_action=page_action,
            hide_canvas=hide_canvas,
            init_script=init_script,
            network_idle=network_idle,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            selector_config={**cls._generate_parser_arguments(), **custom_config},
        ) as session:
            return await session.fetch(url)


PlayWrightFetcher = DynamicFetcher  # For backward-compatibility
