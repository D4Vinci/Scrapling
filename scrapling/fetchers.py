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
from scrapling.engines import (
    FetcherSession,
    CamoufoxEngine,
    PlaywrightEngine,
    check_if_engine_usable,
    FetcherClient as _FetcherClient,
    AsyncFetcherClient as _AsyncFetcherClient,
)
from scrapling.engines.toolbelt import BaseFetcher, Response

__FetcherClientInstance__ = _FetcherClient()


class Fetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on `curl_cffi`."""

    get = __FetcherClientInstance__.get
    post = __FetcherClientInstance__.post
    put = __FetcherClientInstance__.put
    delete = __FetcherClientInstance__.delete


class AsyncFetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on `curl_cffi`."""

    get = _AsyncFetcherClient.get
    post = _AsyncFetcherClient.post
    put = _AsyncFetcherClient.put
    delete = _AsyncFetcherClient.delete


class StealthyFetcher(BaseFetcher):
    """A `Fetcher` class type that is a completely stealthy fetcher that uses a modified version of Firefox.

    It works as real browsers passing almost all online tests/protections based on Camoufox.
    Other added flavors include setting the faked OS fingerprints to match the user's OS, and the referer of every request is set as if this request came from Google's search of this URL's domain.
    """

    @classmethod
    def fetch(
        cls,
        url: str,
        headless: Union[bool, Literal["virtual"]] = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        allow_webgl: bool = True,
        network_idle: bool = False,
        addons: Optional[List[str]] = None,
        cookies: Optional[Iterable[Dict]] = None,
        wait: Optional[int] = 0,
        timeout: Optional[float] = 30000,
        page_action: Callable = None,
        wait_selector: Optional[str] = None,
        humanize: Optional[Union[bool, float]] = True,
        solve_cloudflare: Optional[bool] = False,
        wait_selector_state: SelectorWaitStates = "attached",
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        custom_config: Dict = None,
        additional_arguments: Dict = None,
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), virtual screen mode, or headful/visible mode.
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
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :param additional_arguments: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        engine = CamoufoxEngine(
            wait=wait,
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
            adaptor_arguments={**cls._generate_parser_arguments(), **custom_config},
            additional_arguments=additional_arguments or {},
        )
        return engine.fetch(url)

    @classmethod
    async def async_fetch(
        cls,
        url: str,
        headless: Union[bool, Literal["virtual"]] = True,  # noqa: F821
        block_images: bool = False,
        disable_resources: bool = False,
        block_webrtc: bool = False,
        cookies: Optional[Iterable[Dict]] = None,
        allow_webgl: bool = True,
        network_idle: bool = False,
        addons: Optional[List[str]] = None,
        wait: Optional[int] = 0,
        timeout: Optional[float] = 30000,
        page_action: Callable = None,
        wait_selector: Optional[str] = None,
        humanize: Optional[Union[bool, float]] = True,
        solve_cloudflare: Optional[bool] = False,
        wait_selector_state: SelectorWaitStates = "attached",
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        custom_config: Dict = None,
        additional_arguments: Dict = None,
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), virtual screen mode, or headful/visible mode.
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
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :param additional_arguments: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        engine = CamoufoxEngine(
            wait=wait,
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
            adaptor_arguments={**cls._generate_parser_arguments(), **custom_config},
            additional_arguments=additional_arguments or {},
        )
        return await engine.async_fetch(url)


class PlayWrightFetcher(BaseFetcher):
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
        headless: Union[bool, str] = True,
        disable_resources: bool = None,
        useragent: Optional[str] = None,
        network_idle: bool = False,
        timeout: Optional[float] = 30000,
        wait: Optional[int] = 0,
        cookies: Optional[Iterable[Dict]] = None,
        page_action: Optional[Callable] = None,
        wait_selector: Optional[str] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        extra_headers: Optional[Dict[str, str]] = None,
        google_search: bool = True,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        locale: Optional[str] = "en-US",
        stealth: bool = False,
        real_chrome: bool = False,
        cdp_url: Optional[str] = None,
        nstbrowser_mode: bool = False,
        nstbrowser_config: Optional[Dict] = None,
        custom_config: Dict = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param cookies: Set cookies for the next request.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it has to be used with the ` cdp_url ` argument, or it will get completely ignored.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        engine = PlaywrightEngine(
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
            network_idle=network_idle,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            nstbrowser_mode=nstbrowser_mode,
            nstbrowser_config=nstbrowser_config,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            adaptor_arguments={**cls._generate_parser_arguments(), **custom_config},
        )
        return engine.fetch(url)

    @classmethod
    async def async_fetch(
        cls,
        url: str,
        headless: Union[bool, str] = True,
        disable_resources: bool = None,
        useragent: Optional[str] = None,
        network_idle: bool = False,
        timeout: Optional[float] = 30000,
        wait: Optional[int] = 0,
        cookies: Optional[Iterable[Dict]] = None,
        page_action: Optional[Callable] = None,
        wait_selector: Optional[str] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        extra_headers: Optional[Dict[str, str]] = None,
        google_search: bool = True,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
        locale: Optional[str] = "en-US",
        stealth: bool = False,
        real_chrome: bool = False,
        cdp_url: Optional[str] = None,
        nstbrowser_mode: bool = False,
        nstbrowser_config: Optional[Dict] = None,
        custom_config: Dict = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param cookies: Set cookies for the next request.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it has to be used with the ` cdp_url ` argument, or it will get completely ignored.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            ValueError(
                f"The custom parser config must be of type dictionary, got {cls.__class__}"
            )

        engine = PlaywrightEngine(
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
            network_idle=network_idle,
            google_search=google_search,
            extra_headers=extra_headers,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            nstbrowser_mode=nstbrowser_mode,
            nstbrowser_config=nstbrowser_config,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            adaptor_arguments={**cls._generate_parser_arguments(), **custom_config},
        )
        return await engine.async_fetch(url)


class CustomFetcher(BaseFetcher):
    @classmethod
    def fetch(cls, url: str, browser_engine, **kwargs) -> Response:
        engine = check_if_engine_usable(browser_engine)(
            adaptor_arguments=cls._generate_parser_arguments(), **kwargs
        )
        return engine.fetch(url)
