from scrapling.core._types import (Callable, Dict, List, Literal, Optional,
                                   SelectorWaitStates, Union)
from scrapling.engines import (CamoufoxEngine, PlaywrightEngine, StaticEngine,
                               check_if_engine_usable)
from scrapling.engines.toolbelt import BaseFetcher, Response


class Fetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on httpx.

    Any additional keyword arguments passed to the methods below are passed to the respective httpx's method directly.
    """
    def get(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP GET request for you but with some added flavors.

        :param url: Target url.
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request had came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.get()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries, adaptor_arguments=adaptor_arguments).get(**kwargs)
        return response_object

    def post(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP POST request for you but with some added flavors.

        :param url: Target url.
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.post()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries, adaptor_arguments=adaptor_arguments).post(**kwargs)
        return response_object

    def put(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP PUT request for you but with some added flavors.

        :param url: Target url
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.put()` function so check httpx documentation for details.

        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries, adaptor_arguments=adaptor_arguments).put(**kwargs)
        return response_object

    def delete(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP DELETE request for you but with some added flavors.

        :param url: Target url
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.delete()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries, adaptor_arguments=adaptor_arguments).delete(**kwargs)
        return response_object


class AsyncFetcher(Fetcher):
    async def get(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP GET request for you but with some added flavors.

        :param url: Target url.
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request had came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.get()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = await StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries=retries, adaptor_arguments=adaptor_arguments).async_get(**kwargs)
        return response_object

    async def post(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP POST request for you but with some added flavors.

        :param url: Target url.
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.post()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = await StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries=retries, adaptor_arguments=adaptor_arguments).async_post(**kwargs)
        return response_object

    async def put(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP PUT request for you but with some added flavors.

        :param url: Target url
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.put()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = await StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries=retries, adaptor_arguments=adaptor_arguments).async_put(**kwargs)
        return response_object

    async def delete(
            self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True,
            proxy: Optional[str] = None, retries: Optional[int] = 3, **kwargs: Dict) -> Response:
        """Make basic HTTP DELETE request for you but with some added flavors.

        :param url: Target url
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param retries: The number of retries to do through httpx if the request failed for any reason. The default is 3 retries.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.delete()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        adaptor_arguments = tuple(self.adaptor_arguments.items())
        response_object = await StaticEngine(url, proxy, stealthy_headers, follow_redirects, timeout, retries=retries, adaptor_arguments=adaptor_arguments).async_delete(**kwargs)
        return response_object


class StealthyFetcher(BaseFetcher):
    """A `Fetcher` class type that is completely stealthy fetcher that uses a modified version of Firefox.

     It works as real browsers passing almost all online tests/protections based on Camoufox.
     Other added flavors include setting the faked OS fingerprints to match the user's OS and the referer of every request is set as if this request came from Google's search of this URL's domain.
    """
    def fetch(
            self, url: str, headless: Optional[Union[bool, Literal['virtual']]] = True, block_images: Optional[bool] = False, disable_resources: Optional[bool] = False,
            block_webrtc: Optional[bool] = False, allow_webgl: Optional[bool] = True, network_idle: Optional[bool] = False, addons: Optional[List[str]] = None,
            timeout: Optional[float] = 30000, page_action: Callable = None, wait_selector: Optional[str] = None, humanize: Optional[Union[bool, float]] = True,
            wait_selector_state: SelectorWaitStates = 'attached', google_search: Optional[bool] = True, extra_headers: Optional[Dict[str, str]] = None,
            proxy: Optional[Union[str, Dict[str, str]]] = None, os_randomize: Optional[bool] = None, disable_ads: Optional[bool] = False, geoip: Optional[bool] = False,
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), 'virtual' screen mode, or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param block_webrtc: Blocks WebRTC entirely.
        :param addons: List of Firefox addons to use. Must be paths to extracted addons.
        :param disable_ads: Disabled by default, this installs `uBlock Origin` addon on the browser if enabled.
        :param humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param allow_webgl: Enabled by default. Disabling it WebGL not recommended as many WAFs now checks if WebGL is enabled.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, & spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        engine = CamoufoxEngine(
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
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
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            adaptor_arguments=self.adaptor_arguments,
        )
        return engine.fetch(url)

    async def async_fetch(
            self, url: str, headless: Optional[Union[bool, Literal['virtual']]] = True, block_images: Optional[bool] = False, disable_resources: Optional[bool] = False,
            block_webrtc: Optional[bool] = False, allow_webgl: Optional[bool] = True, network_idle: Optional[bool] = False, addons: Optional[List[str]] = None,
            timeout: Optional[float] = 30000, page_action: Callable = None, wait_selector: Optional[str] = None, humanize: Optional[Union[bool, float]] = True,
            wait_selector_state: SelectorWaitStates = 'attached', google_search: Optional[bool] = True, extra_headers: Optional[Dict[str, str]] = None,
            proxy: Optional[Union[str, Dict[str, str]]] = None, os_randomize: Optional[bool] = None, disable_ads: Optional[bool] = False, geoip: Optional[bool] = False,
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), 'virtual' screen mode, or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param block_webrtc: Blocks WebRTC entirely.
        :param addons: List of Firefox addons to use. Must be paths to extracted addons.
        :param disable_ads: Disabled by default, this installs `uBlock Origin` addon on the browser if enabled.
        :param humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param allow_webgl: Enabled by default. Disabling it WebGL not recommended as many WAFs now checks if WebGL is enabled.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, & spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param os_randomize: If enabled, Scrapling will randomize the OS fingerprints used. The default is Scrapling matching the fingerprints with the current OS.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        engine = CamoufoxEngine(
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
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
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            adaptor_arguments=self.adaptor_arguments,
        )
        return await engine.async_fetch(url)


class PlayWrightFetcher(BaseFetcher):
    """A `Fetcher` class type that provide many options, all of them are based on PlayWright.

     Using this Fetcher class, you can do requests with:
        - Vanilla Playwright without any modifications other than the ones you chose.
        - Stealthy Playwright with the stealth mode I wrote for it. It's still a work in progress but it bypasses many online tests like bot.sannysoft.com
            Some of the things stealth mode does include:
                1) Patches the CDP runtime fingerprint.
                2) Mimics some of the real browsers' properties by injecting several JS files and using custom options.
                3) Using custom flags on launch to hide Playwright even more and make it faster.
                4) Generates real browser's headers of the same type and same user OS then append it to the request.
        - Real browsers by passing the `real_chrome` argument or the CDP URL of your browser to be controlled by the Fetcher and most of the options can be enabled on it.
        - NSTBrowser's docker browserless option by passing the CDP URL and enabling `nstbrowser_mode` option.

    > Note that these are the main options with PlayWright but it can be mixed together.
    """
    def fetch(
            self, url: str, headless: Union[bool, str] = True, disable_resources: bool = None,
            useragent: Optional[str] = None, network_idle: Optional[bool] = False, timeout: Optional[float] = 30000,
            page_action: Optional[Callable] = None, wait_selector: Optional[str] = None, wait_selector_state: SelectorWaitStates = 'attached',
            hide_canvas: Optional[bool] = False, disable_webgl: Optional[bool] = False, extra_headers: Optional[Dict[str, str]] = None, google_search: Optional[bool] = True,
            proxy: Optional[Union[str, Dict[str, str]]] = None, locale: Optional[str] = 'en-US',
            stealth: Optional[bool] = False, real_chrome: Optional[bool] = False,
            cdp_url: Optional[str] = None,
            nstbrowser_mode: Optional[bool] = False, nstbrowser_config: Optional[Dict] = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have chrome browser installed on your device, enable this and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it have to be used with `cdp_url` argument or it will get completely ignored.
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        engine = PlaywrightEngine(
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
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
            adaptor_arguments=self.adaptor_arguments,
        )
        return engine.fetch(url)

    async def async_fetch(
            self, url: str, headless: Union[bool, str] = True, disable_resources: bool = None,
            useragent: Optional[str] = None, network_idle: Optional[bool] = False, timeout: Optional[float] = 30000,
            page_action: Optional[Callable] = None, wait_selector: Optional[str] = None, wait_selector_state: SelectorWaitStates = 'attached',
            hide_canvas: Optional[bool] = False, disable_webgl: Optional[bool] = False, extra_headers: Optional[Dict[str, str]] = None, google_search: Optional[bool] = True,
            proxy: Optional[Union[str, Dict[str, str]]] = None, locale: Optional[str] = 'en-US',
            stealth: Optional[bool] = False, real_chrome: Optional[bool] = False,
            cdp_url: Optional[str] = None,
            nstbrowser_mode: Optional[bool] = False, nstbrowser_config: Optional[Dict] = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30000
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param page_action: Added for automation. A function that takes the `page` object, does the automation you need, then returns `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have chrome browser installed on your device, enable this and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search for this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers/NSTBrowser through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it have to be used with `cdp_url` argument or it will get completely ignored.
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        engine = PlaywrightEngine(
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
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
            adaptor_arguments=self.adaptor_arguments,
        )
        return await engine.async_fetch(url)


class CustomFetcher(BaseFetcher):
    def fetch(self, url: str, browser_engine, **kwargs) -> Response:
        engine = check_if_engine_usable(browser_engine)(adaptor_arguments=self.adaptor_arguments, **kwargs)
        return engine.fetch(url)
