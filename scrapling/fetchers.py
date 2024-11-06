from scrapling.core._types import Dict, Optional, Union, Callable, List

from scrapling.engines.toolbelt import Response, BaseFetcher, do_nothing
from scrapling.engines import CamoufoxEngine, PlaywrightEngine, StaticEngine, check_if_engine_usable


class Fetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on httpx.

    Any additional keyword arguments passed to the methods below are passed to the respective httpx's method directly.
    """
    def get(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        """Make basic HTTP GET request for you but with some added flavors.
        :param url: Target url.
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. Default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request had came from Google's search of this URL's domain.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.get()` function so check httpx documentation for details.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).get(url, stealthy_headers, **kwargs)
        return response_object

    def post(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        """Make basic HTTP POST request for you but with some added flavors.
        :param url: Target url.
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. Default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.post()` function so check httpx documentation for details.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).post(url, stealthy_headers, **kwargs)
        return response_object

    def put(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        """Make basic HTTP PUT request for you but with some added flavors.
        :param url: Target url
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. Default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
        create a referer header as if this request came from Google's search of this URL's domain.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.put()` function so check httpx documentation for details.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).put(url, stealthy_headers, **kwargs)
        return response_object

    def delete(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = 10, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        """Make basic HTTP DELETE request for you but with some added flavors.
        :param url: Target url
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. Default is 10 seconds.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request came from Google's search of this URL's domain.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.delete()` function so check httpx documentation for details.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).delete(url, stealthy_headers, **kwargs)
        return response_object


class StealthyFetcher(BaseFetcher):
    """A `Fetcher` class type that is completely stealthy fetcher that uses a modified version of Firefox.

     It works as real browsers passing almost all online tests/protections based on Camoufox.
     Other added flavors include setting the faked OS fingerprints to match the user's OS and the referer of every request is set as if this request came from Google's search of this URL's domain.
    """
    def fetch(
            self, url: str, headless: Union[bool, str] = True, block_images: Optional[bool] = False, disable_resources: Optional[bool] = False,
            block_webrtc: Optional[bool] = False, allow_webgl: Optional[bool] = False, network_idle: Optional[bool] = False, addons: Optional[List[str]] = None,
            timeout: Optional[float] = 30000, page_action: Callable = do_nothing, wait_selector: Optional[str] = None, humanize: Optional[Union[bool, float]] = True,
            wait_selector_state: str = 'attached',
    ) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.
        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), virtual screen mode, or headful/visible mode.
        :param block_images: Prevent the loading of images through Firefox preferences.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param disable_resources: Drop requests of unnecessary resources for speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param block_webrtc: Blocks WebRTC entirely.
        :param addons: List of Firefox addons to use. Must be paths to extracted addons.
        :param humanize: Humanize the cursor movement. Takes either True, or the MAX duration in seconds of the cursor movement. The cursor typically takes up to 1.5 seconds to move across the window.
        :param allow_webgl: Whether to allow WebGL. To prevent leaks, only use this for special cases.
        :param network_idle: Wait for the page to not do do any requests.
        :param timeout: The timeout in milliseconds that's used in all operations and waits through the page. Default is 30000.
        :param page_action: Added for automation. A function that takes the `page` object, do the automation you need, then return `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        engine = CamoufoxEngine(
            timeout=timeout,
            headless=headless,
            page_action=page_action,
            block_images=block_images,
            block_webrtc=block_webrtc,
            addons=addons,
            humanize=humanize,
            allow_webgl=allow_webgl,
            disable_resources=disable_resources,
            network_idle=network_idle,
            wait_selector=wait_selector,
            wait_selector_state=wait_selector_state,
            adaptor_arguments=self.adaptor_arguments,
        )
        return engine.fetch(url)


class PlayWrightFetcher(BaseFetcher):
    """A `Fetcher` class type that provide many options, all of them are based on PlayWright.

     Using this Fetcher class, you can do requests with:
        - Vanilla Playwright without any modifications other than the ones you chose.
        - Stealthy Playwright with the stealth mode I wrote for it. It's still a work in progress but it bypasses many online tests like bot.sannysoft.com
        Some of the things stealth mode do includes:
            1) Patches the CDP runtime fingerprint.
            2) Mimics some of real browsers' properties by injects several JS files and using custom options.
            3) Using custom flags on launch to hide playwright even more and make it faster.
            4) Sets the referer of every request as if this request came from Google's search of this URL's domain.
            5) Generates real browser's headers of the same type and same user OS then append it to the request.
        - Real browsers by passing the CDP URL of your browser to be controlled by the Fetcher and most of the options can be enabled on it.
        - NSTBrowser's docker browserless option by passing the CDP URL and enabling `nstbrowser_mode` option.
        > Note that these are the main options with PlayWright but it can be mixed together.
    """
    def fetch(
            self, url: str, headless: Union[bool, str] = True, disable_resources: bool = None,
            useragent: Optional[str] = None, network_idle: Optional[bool] = False, timeout: Optional[float] = 30000,
            page_action: Callable = do_nothing, wait_selector: Optional[str] = None, wait_selector_state: Optional[str] = 'attached',
            hide_canvas: bool = True, disable_webgl: bool = False,
            stealth: bool = False,
            cdp_url: Optional[str] = None,
            nstbrowser_mode: bool = False, nstbrowser_config: Optional[Dict] = None,
    ) -> Response:
        """Opens up a browser and do your request based on your chosen options below.
        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for speed boost. It depends but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param network_idle: Wait for the page to not do do any requests.
        :param timeout: The timeout in milliseconds that's used in all operations and waits through the page. Default is 30000.
        :param page_action: Added for automation. A function that takes the `page` object, do the automation you need, then return `page` again.
        :param wait_selector: Wait for a specific css selector to be in a specific state.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. Default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param nstbrowser_mode: Enables NSTBrowser mode, it have to be used with `cdp_url` argument or it will get completely ignored.
        :param nstbrowser_config: The config you want to send with requests to the NSTBrowser. If left empty, Scrapling defaults to an optimized NSTBrowser's docker browserless config.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        engine = PlaywrightEngine(
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            headless=headless,
            useragent=useragent,
            page_action=page_action,
            hide_canvas=hide_canvas,
            network_idle=network_idle,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            nstbrowser_mode=nstbrowser_mode,
            nstbrowser_config=nstbrowser_config,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            adaptor_arguments=self.adaptor_arguments,
        )
        return engine.fetch(url)


class CustomFetcher(BaseFetcher):
    def fetch(self, url: str, browser_engine, **kwargs) -> Response:
        engine = check_if_engine_usable(browser_engine)(adaptor_arguments=self.adaptor_arguments, **kwargs)
        return engine.fetch(url)
