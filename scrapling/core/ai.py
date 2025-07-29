from asyncio import gather

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from scrapling.core.shell import Convertor
from scrapling.engines.toolbelt import Response as _ScraplingResponse
from scrapling.fetchers import (
    Fetcher,
    FetcherSession,
    DynamicFetcher,
    AsyncDynamicSession,
    StealthyFetcher,
    AsyncStealthySession,
)
from scrapling.core._types import (
    Optional,
    Tuple,
    extraction_types,
    Mapping,
    Dict,
    List,
    SelectorWaitStates,
    Generator,
)
from curl_cffi.requests import (
    BrowserTypeLiteral,
)


class ResponseModel(BaseModel):
    """Request's response information structure."""

    status: int = Field(description="The status code returned by the website.")
    content: list[str] = Field(
        description="The content as Markdown/HTML or the text content of the page."
    )
    url: str = Field(
        description="The URL given by the user that resulted in this response."
    )


def _ContentTranslator(
    content: Generator[str, None, None], page: _ScraplingResponse
) -> ResponseModel:
    """Convert a content generator to a list of ResponseModel objects."""
    return ResponseModel(
        status=page.status, content=[result for result in content], url=page.url
    )


class ScraplingMCPServer:
    _server = FastMCP(name="Scrapling")

    @staticmethod
    @_server.tool()
    def get(
        url: str,
        impersonate: Optional[BrowserTypeLiteral] = "chrome",
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        params: Optional[Dict | List | Tuple] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[Dict[str, str] | list[tuple[str, str]]] = None,
        timeout: Optional[int | float] = 30,
        follow_redirects: bool = True,
        max_redirects: int = 30,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        proxy: Optional[str] = None,
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,
        http3: Optional[bool] = False,
        stealthy_headers: Optional[bool] = True,
    ) -> ResponseModel:
        """Make GET HTTP request to a URL and return a structured output of the result.
        Note: This is only suitable for low-mid protection levels. For high-protection levels or websites that require JS loading, use the other tools directly.
        Note: If the `css_selector` resolves to more than one element, all the elements will be returned.

        :param url: The URL to request.
        :param impersonate: Browser version to impersonate its fingerprint. It's using the latest chrome version by default.
        :param extraction_type: The type of content to extract from the page. Defaults to "markdown". Options are:
            - Markdown will convert the page content to Markdown format.
            - HTML will return the raw HTML content of the page.
            - Text will return the text content of the page.
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        """
        page = Fetcher.get(
            url,
            auth=auth,
            proxy=proxy,
            http3=http3,
            verify=verify,
            params=params,
            proxy_auth=proxy_auth,
            retry_delay=retry_delay,
            stealthy_headers=stealthy_headers,
            impersonate=impersonate,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            retries=retries,
            max_redirects=max_redirects,
            follow_redirects=follow_redirects,
        )
        return _ContentTranslator(
            Convertor._extract_content(
                page,
                css_selector=css_selector,
                extraction_type=extraction_type,
                main_content_only=main_content_only,
            ),
            page,
        )

    @staticmethod
    @_server.tool()
    async def bulk_get(
        urls: Tuple[str, ...],
        impersonate: Optional[BrowserTypeLiteral] = "chrome",
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        params: Optional[Dict | List | Tuple] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[Dict[str, str] | list[tuple[str, str]]] = None,
        timeout: Optional[int | float] = 30,
        follow_redirects: bool = True,
        max_redirects: int = 30,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        proxy: Optional[str] = None,
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,
        http3: Optional[bool] = False,
        stealthy_headers: Optional[bool] = True,
    ) -> List[ResponseModel]:
        """Make GET HTTP request to a group of URLs and for each URL, return a structured output of the result.
        Note: This is only suitable for low-mid protection levels. For high-protection levels or websites that require JS loading, use the other tools directly.
        Note: If the `css_selector` resolves to more than one element, all the elements will be returned.

        :param urls: A tuple of the URLs to request.
        :param impersonate: Browser version to impersonate its fingerprint. It's using the latest chrome version by default.
        :param extraction_type: The type of content to extract from the page. Defaults to "markdown". Options are:
            - Markdown will convert the page content to Markdown format.
            - HTML will return the raw HTML content of the page.
            - Text will return the text content of the page.
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param params: Query string parameters for the request.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
        :param verify: Whether to verify HTTPS certificates.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        """
        async with FetcherSession() as session:
            tasks = [
                session.get(
                    url,
                    auth=auth,
                    proxy=proxy,
                    http3=http3,
                    verify=verify,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    timeout=timeout,
                    retries=retries,
                    proxy_auth=proxy_auth,
                    retry_delay=retry_delay,
                    impersonate=impersonate,
                    max_redirects=max_redirects,
                    follow_redirects=follow_redirects,
                    stealthy_headers=stealthy_headers,
                )
                for url in urls
            ]
            responses = await gather(*tasks)
            return [
                _ContentTranslator(
                    Convertor._extract_content(
                        page,
                        css_selector=css_selector,
                        extraction_type=extraction_type,
                        main_content_only=main_content_only,
                    ),
                    page,
                )
                for page in responses
            ]

    @staticmethod
    @_server.tool()
    async def fetch(
        url: str,
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = False,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: int | float = 0,
        proxy: Optional[str | Dict[str, str]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Optional[List[Dict]] = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
    ) -> ResponseModel:
        """Use playwright to open a browser to fetch a URL and return a structured output of the result.
        Note: This is only suitable for low-mid protection levels.
        Note: If the `css_selector` resolves to more than one element, all the elements will be returned.

        :param url: The URL to request.
        :param extraction_type: The type of content to extract from the page. Defaults to "markdown". Options are:
            - Markdown will convert the page content to Markdown format.
            - HTML will return the raw HTML content of the page.
            - Text will return the text content of the page.
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
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
        """
        page = await DynamicFetcher.async_fetch(
            url,
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            cookies=cookies,
            stealth=stealth,
            cdp_url=cdp_url,
            headless=headless,
            useragent=useragent,
            hide_canvas=hide_canvas,
            real_chrome=real_chrome,
            network_idle=network_idle,
            wait_selector=wait_selector,
            disable_webgl=disable_webgl,
            extra_headers=extra_headers,
            google_search=google_search,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        )
        return _ContentTranslator(
            Convertor._extract_content(
                page,
                css_selector=css_selector,
                extraction_type=extraction_type,
                main_content_only=main_content_only,
            ),
            page,
        )

    @staticmethod
    @_server.tool()
    async def bulk_fetch(
        urls: Tuple[str, ...],
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
        headless: bool = False,
        google_search: bool = True,
        hide_canvas: bool = False,
        disable_webgl: bool = False,
        real_chrome: bool = False,
        stealth: bool = False,
        wait: int | float = 0,
        proxy: Optional[str | Dict[str, str]] = None,
        locale: str = "en-US",
        extra_headers: Optional[Dict[str, str]] = None,
        useragent: Optional[str] = None,
        cdp_url: Optional[str] = None,
        timeout: int | float = 30000,
        disable_resources: bool = False,
        wait_selector: Optional[str] = None,
        cookies: Optional[List[Dict]] = None,
        network_idle: bool = False,
        wait_selector_state: SelectorWaitStates = "attached",
    ) -> List[ResponseModel]:
        """Use playwright to open a browser, then fetch a group of URLs at the same time, and for each page return a structured output of the result.
        Note: This is only suitable for low-mid protection levels.
        Note: If the `css_selector` resolves to more than one element, all the elements will be returned.

        :param urls: A tuple of the URLs to request.
        :param extraction_type: The type of content to extract from the page. Defaults to "markdown". Options are:
            - Markdown will convert the page content to Markdown format.
            - HTML will return the raw HTML content of the page.
            - Text will return the text content of the page.
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
            Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
            This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request. It should be in a dictionary format that Playwright accepts.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
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
        """
        async with AsyncDynamicSession(
            wait=wait,
            proxy=proxy,
            locale=locale,
            timeout=timeout,
            cookies=cookies,
            stealth=stealth,
            cdp_url=cdp_url,
            headless=headless,
            max_pages=len(urls),
            useragent=useragent,
            hide_canvas=hide_canvas,
            real_chrome=real_chrome,
            network_idle=network_idle,
            wait_selector=wait_selector,
            google_search=google_search,
            disable_webgl=disable_webgl,
            extra_headers=extra_headers,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
        ) as session:
            tasks = [session.fetch(url) for url in urls]
            responses = await gather(*tasks)
            return [
                _ContentTranslator(
                    Convertor._extract_content(
                        page,
                        css_selector=css_selector,
                        extraction_type=extraction_type,
                        main_content_only=main_content_only,
                    ),
                    page,
                )
                for page in responses
            ]

    @staticmethod
    @_server.tool()
    async def stealthy_fetch(
        url: str,
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
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
        wait_selector: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[List[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        additional_args: Optional[Dict] = None,
    ) -> ResponseModel:
        """Use Scrapling's version of the Camoufox browser to fetch a URL and return a structured output of the result.
        Note: This is best suitable for high protection levels. It's slower than the other tools.
        Note: If the `css_selector` resolves to more than one element, all the elements will be returned.

        :param url: The URL to request.
        :param extraction_type: The type of content to extract from the page. Defaults to "markdown". Options are:
            - Markdown will convert the page content to Markdown format.
            - HTML will return the raw HTML content of the page.
            - Text will return the text content of the page.
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
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
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """
        page = await StealthyFetcher.async_fetch(
            url,
            wait=wait,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            humanize=humanize,
            allow_webgl=allow_webgl,
            disable_ads=disable_ads,
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
            additional_args=additional_args,
        )
        return _ContentTranslator(
            Convertor._extract_content(
                page,
                css_selector=css_selector,
                extraction_type=extraction_type,
                main_content_only=main_content_only,
            ),
            page,
        )

    @staticmethod
    @_server.tool()
    async def bulk_stealthy_fetch(
        urls: Tuple[str, ...],
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = True,
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
        wait_selector: Optional[str] = None,
        addons: Optional[List[str]] = None,
        wait_selector_state: SelectorWaitStates = "attached",
        cookies: Optional[List[Dict]] = None,
        google_search: bool = True,
        extra_headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str | Dict[str, str]] = None,
        os_randomize: bool = False,
        disable_ads: bool = False,
        geoip: bool = False,
        additional_args: Optional[Dict] = None,
    ) -> List[ResponseModel]:
        """Use Scrapling's version of the Camoufox browser to fetch a group of URLs at the same time, and for each page return a structured output of the result.
        Note: This is best suitable for high protection levels. It's slower than the other tools.
        Note: If the `css_selector` resolves to more than one element, all the elements will be returned.

        :param urls: A tuple of the URLs to request.
        :param extraction_type: The type of content to extract from the page. Defaults to "markdown". Options are:
            - Markdown will convert the page content to Markdown format.
            - HTML will return the raw HTML content of the page.
            - Text will return the text content of the page.
        :param css_selector: CSS selector to extract the content from the page. If main_content_only is True, then it will be executed on the main content of the page. Defaults to None.
        :param main_content_only: Whether to extract only the main content of the page. Defaults to True. The main content here is the data inside the `<body>` tag.
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
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            It will also calculate and spoof the browser's language based on the distribution of language speakers in the target region.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param additional_args: Additional arguments to be passed to Camoufox as additional settings, and it takes higher priority than Scrapling's settings.
        """
        async with AsyncStealthySession(
            wait=wait,
            proxy=proxy,
            geoip=geoip,
            addons=addons,
            timeout=timeout,
            cookies=cookies,
            headless=headless,
            humanize=humanize,
            max_pages=len(urls),
            allow_webgl=allow_webgl,
            disable_ads=disable_ads,
            block_images=block_images,
            block_webrtc=block_webrtc,
            network_idle=network_idle,
            os_randomize=os_randomize,
            wait_selector=wait_selector,
            google_search=google_search,
            extra_headers=extra_headers,
            solve_cloudflare=solve_cloudflare,
            disable_resources=disable_resources,
            wait_selector_state=wait_selector_state,
            additional_args=additional_args,
        ) as session:
            tasks = [session.fetch(url) for url in urls]
            responses = await gather(*tasks)
            return [
                _ContentTranslator(
                    Convertor._extract_content(
                        page,
                        css_selector=css_selector,
                        extraction_type=extraction_type,
                        main_content_only=main_content_only,
                    ),
                    page,
                )
                for page in responses
            ]

    def serve(self):
        """Serve the MCP server."""
        self._server.run(transport="stdio")
