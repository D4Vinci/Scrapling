from scrapling.core._types import Unpack
from scrapling.engines._browsers._types import PlaywrightSession
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
    def fetch(cls, url: str, **kwargs: Unpack[PlaywrightSession]) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param kwargs: Browser session configuration options including:
            - headless: Run the browser in headless/hidden (default), or headful/visible mode.
            - disable_resources: Drop requests of unnecessary resources for a speed boost.
            - useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
            - cookies: Set cookies for the next request.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
            - locale: Set the locale for the browser if wanted. The default value is `en-US`.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
            - real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
            - hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
            - disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
            - cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - extra_headers: A dictionary of extra headers to add to the request.
            - proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
            - extra_flags: A list of additional browser flags to pass to the browser on launch.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
            - additional_args: Additional arguments to be passed to Playwright's context as additional settings.
        :return: A `Response` object.
        """
        selector_config = kwargs.get("selector_config", {}) or kwargs.get(
            "custom_config", {}
        )  # Checking `custom_config` for backward compatibility
        if not isinstance(selector_config, dict):
            raise TypeError("Argument `selector_config` must be a dictionary.")

        kwargs["selector_config"] = {**cls._generate_parser_arguments(), **selector_config}

        with DynamicSession(**kwargs) as session:
            return session.fetch(url)

    @classmethod
    async def async_fetch(cls, url: str, **kwargs: Unpack[PlaywrightSession]) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param kwargs: Browser session configuration options including:
            - headless: Run the browser in headless/hidden (default), or headful/visible mode.
            - disable_resources: Drop requests of unnecessary resources for a speed boost.
            - useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
            - cookies: Set cookies for the next request.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
            - locale: Set the locale for the browser if wanted. The default value is `en-US`.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - stealth: Enables stealth mode, check the documentation to see what stealth mode does currently.
            - real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
            - hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
            - disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
            - cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - extra_headers: A dictionary of extra headers to add to the request.
            - proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
            - extra_flags: A list of additional browser flags to pass to the browser on launch.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
            - additional_args: Additional arguments to be passed to Playwright's context as additional settings.
        :return: A `Response` object.
        """
        selector_config = kwargs.get("selector_config", {}) or kwargs.get(
            "custom_config", {}
        )  # Checking `custom_config` for backward compatibility
        if not isinstance(selector_config, dict):
            raise TypeError("Argument `selector_config` must be a dictionary.")

        kwargs["selector_config"] = {**cls._generate_parser_arguments(), **selector_config}

        async with AsyncDynamicSession(**kwargs) as session:
            return await session.fetch(url)


PlayWrightFetcher = DynamicFetcher  # For backward-compatibility
