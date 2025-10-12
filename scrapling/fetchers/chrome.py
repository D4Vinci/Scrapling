from scrapling.core._types import (
    Callable,
    List,
    Dict,
    Optional,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt.custom import BaseFetcher, Response
from scrapling.engines._browsers._controllers import DynamicSession, AsyncDynamicSession


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
        cookies: Optional[List[Dict]] = None,
        network_idle: bool = False,
        load_dom: bool = True,
        wait_selector_state: SelectorWaitStates = "attached",
        additional_args: Optional[Dict] = None,
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
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object.
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            raise ValueError(f"The custom parser config must be of type dictionary, got {cls.__class__}")

        with DynamicSession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            cookies=cookies,
            headless=headless,
            load_dom=load_dom,
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
            additional_args=additional_args,
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
        cookies: Optional[List[Dict]] = None,
        network_idle: bool = False,
        load_dom: bool = True,
        wait_selector_state: SelectorWaitStates = "attached",
        additional_args: Optional[Dict] = None,
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
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param locale: Set the locale for the browser if wanted. The default value is `en-US`.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
        :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param custom_config: A dictionary of custom parser arguments to use with this request. Any argument passed will override any class parameters values.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object.
        """
        if not custom_config:
            custom_config = {}
        elif not isinstance(custom_config, dict):
            raise ValueError(f"The custom parser config must be of type dictionary, got {cls.__class__}")

        async with AsyncDynamicSession(
            wait=wait,
            max_pages=1,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            stealth=stealth,
            cdp_url=cdp_url,
            cookies=cookies,
            headless=headless,
            load_dom=load_dom,
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
            additional_args=additional_args,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            selector_config={**cls._generate_parser_arguments(), **custom_config},
        ) as session:
            return await session.fetch(url)


PlayWrightFetcher = DynamicFetcher  # For backward-compatibility
