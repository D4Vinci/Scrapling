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
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and create a referer header as if this request had came from Google's search.
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
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and create a referer header as if this request had came from Google's search.
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
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and create a referer header as if this request had came from Google's search.
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
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and create a referer header as if this request had came from Google's search.
        :param kwargs: Any additional keyword arguments are passed directly to `httpx.delete()` function so check httpx documentation for details.
        :return: A Response object with `url`, `text`, `content`, `status`, `reason`, `encoding`, `cookies`, `headers`, `request_headers`, and the `adaptor` class for parsing, of course.
        """
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).delete(url, stealthy_headers, **kwargs)
        return response_object


class StealthyFetcher(BaseFetcher):
    def fetch(
            self, url: str, headless: Union[bool, str] = True, block_images: Optional[bool] = False, block_webrtc: Optional[bool] = False,
            network_idle: Optional[bool] = False, timeout: Optional[float] = 30000, page_action: Callable = do_nothing, wait_selector: Optional[str] = None,
            wait_selector_state: str = 'attached',
    ) -> Response:
        engine = CamoufoxEngine(
            timeout=timeout,
            headless=headless,
            page_action=page_action,
            block_images=block_images,
            block_webrtc=block_webrtc,
            network_idle=network_idle,
            wait_selector=wait_selector,
            wait_selector_state=wait_selector_state,
            adaptor_arguments=self.adaptor_arguments,
        )
        return engine.fetch(url)


class PlayWrightFetcher(BaseFetcher):
    def fetch(
            self,
            url: str,
            headless: Union[bool, str] = True,
            disable_resources: Optional[List] = None,
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
    ) -> Response:
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
