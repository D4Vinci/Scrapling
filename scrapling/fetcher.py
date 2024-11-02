from scrapling.core._types import Dict, Optional, Union, Callable, List

from scrapling.engines.toolbelt import Response, BaseFetcher, do_nothing
from scrapling.engines import CamoufoxEngine, PlaywrightEngine, StaticEngine, check_if_engine_usable


class Fetcher(BaseFetcher):
    def get(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).get(url, stealthy_headers, **kwargs)
        return response_object

    def post(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).post(url, stealthy_headers, **kwargs)
        return response_object

    def put(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
        response_object = StaticEngine(follow_redirects, timeout, adaptor_arguments=self.adaptor_arguments).put(url, stealthy_headers, **kwargs)
        return response_object

    def delete(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Response:
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
