from scrapling.core._types import Unpack
from scrapling.engines._browsers._types import StealthSession
from scrapling.engines.toolbelt.custom import BaseFetcher, Response
from scrapling.engines._browsers._stealth import StealthySession, AsyncStealthySession


class StealthyFetcher(BaseFetcher):
    """A `Fetcher` class type which is a completely stealthy built on top of Chromium.

    It works as real browsers passing almost all online tests/protections with many customization options.
    """

    @classmethod
    def fetch(cls, url: str, **kwargs: Unpack[StealthSession]) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param kwargs: Browser session configuration options including:
            - headless: Run the browser in headless/hidden (default), or headful/visible mode.
            - disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
                Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
                This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
            - useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
            - cookies: Set cookies for the next request.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
            - locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
                rules. Defaults to the system default locale.
            - timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
            - real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
            - hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
            - block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
            - allow_webgl: Enabled by default. Disabling it disables WebGL and WebGL 2.0 support entirely. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
            - proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
            - user_data_dir: Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory.
            - extra_flags: A list of additional browser flags to pass to the browser on launch.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
            - additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object.
        """
        selector_config = kwargs.get("selector_config", {}) or kwargs.get(
            "custom_config", {}
        )  # Checking `custom_config` for backward compatibility
        if not isinstance(selector_config, dict):
            raise TypeError("Argument `selector_config` must be a dictionary.")

        kwargs["selector_config"] = {**cls._generate_parser_arguments(), **selector_config}

        with StealthySession(**kwargs) as engine:
            return engine.fetch(url)

    @classmethod
    async def async_fetch(cls, url: str, **kwargs: Unpack[StealthSession]) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param kwargs: Browser session configuration options including:
            - headless: Run the browser in headless/hidden (default), or headful/visible mode.
            - disable_resources: Drop requests of unnecessary resources for a speed boost. It depends, but it made requests ~25% faster in my tests for some websites.
                Requests dropped are of type `font`, `image`, `media`, `beacon`, `object`, `imageset`, `texttrack`, `websocket`, `csp_report`, and `stylesheet`.
                This can help save your proxy usage but be careful with this option as it makes some websites never finish loading.
            - useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
            - cookies: Set cookies for the next request.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the ` Response ` object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - init_script: An absolute path to a JavaScript file to be executed on page creation for all pages in this session.
            - locale: Specify user locale, for example, `en-GB`, `de-DE`, etc. Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting
                rules. Defaults to the system default locale.
            - timezone_id: Changes the timezone of the browser. Defaults to the system timezone.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
            - real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
            - hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
            - block_webrtc: Forces WebRTC to respect proxy settings to prevent local IP address leak.
            - allow_webgl: Enabled by default. Disabling it disables WebGL and WebGL 2.0 support entirely. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - extra_headers: A dictionary of extra headers to add to the request. _The referer set by the `google_search` argument takes priority over the referer set here if used together._
            - proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
            - user_data_dir: Path to a User Data Directory, which stores browser session data like cookies and local storage. The default is to create a temporary directory.
            - extra_flags: A list of additional browser flags to pass to the browser on launch.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
            - additional_args: Additional arguments to be passed to Playwright's context as additional settings, and it takes higher priority than Scrapling's settings.
        :return: A `Response` object.
        """
        selector_config = kwargs.get("selector_config", {}) or kwargs.get(
            "custom_config", {}
        )  # Checking `custom_config` for backward compatibility
        if not isinstance(selector_config, dict):
            raise TypeError("Argument `selector_config` must be a dictionary.")

        kwargs["selector_config"] = {**cls._generate_parser_arguments(), **selector_config}

        async with AsyncStealthySession(**kwargs) as engine:
            return await engine.fetch(url)
