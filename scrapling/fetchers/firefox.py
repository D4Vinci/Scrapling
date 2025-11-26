from scrapling.core._types import Unpack
from scrapling.engines._browsers._types import CamoufoxSession
from scrapling.engines.toolbelt.custom import BaseFetcher, Response
from scrapling.engines._browsers._camoufox import StealthySession, AsyncStealthySession


class StealthyFetcher(BaseFetcher):
    """A `Fetcher` class type that is a completely stealthy fetcher that uses a modified version of Firefox.

    It works as real browsers passing almost all online tests/protections based on Camoufox.
    Other added flavors include setting the faked OS fingerprints to match the user's OS, and the referer of every request is set as if this request came from Google's search of this URL's domain.
    """

    @classmethod
    def fetch(cls, url: str, **kwargs: Unpack[CamoufoxSession]) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param kwargs: Browser session configuration options including:
            - headless: Run the browser in headless/hidden (default), or headful/visible mode.
            - block_images: Prevent the loading of images through Firefox preferences.
            - disable_resources: Drop requests of unnecessary resources for a speed boost.
            - block_webrtc: Blocks WebRTC entirely.
            - allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement.
            - solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
            - addons: List of Firefox addons to use. Must be paths to extracted addons.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - cookies: Set cookies for the next request.
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - extra_headers: A dictionary of extra headers to add to the request.
            - proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
            - os_randomize: If enabled, Scrapling will randomize the OS fingerprints used.
            - disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
            - geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
            - additional_args: Additional arguments to be passed to Camoufox as additional settings.
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
    async def async_fetch(cls, url: str, **kwargs: Unpack[CamoufoxSession]) -> Response:
        """
        Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param kwargs: Browser session configuration options including:
            - headless: Run the browser in headless/hidden (default), or headful/visible mode.
            - block_images: Prevent the loading of images through Firefox preferences.
            - disable_resources: Drop requests of unnecessary resources for a speed boost.
            - block_webrtc: Blocks WebRTC entirely.
            - allow_webgl: Enabled by default. Disabling WebGL is not recommended as many WAFs now check if WebGL is enabled.
            - network_idle: Wait for the page until there are no network connections for at least 500 ms.
            - load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
            - humanize: Humanize the cursor movement. Takes either True or the MAX duration in seconds of the cursor movement.
            - solve_cloudflare: Solves all types of the Cloudflare's Turnstile/Interstitial challenges before returning the response to you.
            - wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
            - timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
            - page_action: Added for automation. A function that takes the `page` object and does the automation you need.
            - wait_selector: Wait for a specific CSS selector to be in a specific state.
            - init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
            - addons: List of Firefox addons to use. Must be paths to extracted addons.
            - wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
            - cookies: Set cookies for the next request.
            - google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
            - extra_headers: A dictionary of extra headers to add to the request.
            - proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
            - os_randomize: If enabled, Scrapling will randomize the OS fingerprints used.
            - disable_ads: Disabled by default, this installs the `uBlock Origin` addon on the browser if enabled.
            - geoip: Recommended to use with proxies; Automatically use IP's longitude, latitude, timezone, country, locale, and spoof the WebRTC IP address.
            - selector_config: The arguments that will be passed in the end while creating the final Selector's class.
            - additional_args: Additional arguments to be passed to Camoufox as additional settings.
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
