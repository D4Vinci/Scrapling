from scrapling.core._types import Unpack
from scrapling.engines._browsers._types import PlaywrightSession
from scrapling.engines.toolbelt.custom import BaseFetcher, Response
from scrapling.engines._browsers._controllers import DynamicSession, AsyncDynamicSession


class DynamicFetcher(BaseFetcher):
    """A `Fetcher` that provide many options to fetch/load websites' pages through chromium-based browsers."""

    @classmethod
    def fetch(cls, url: str, **kwargs: Unpack[PlaywrightSession]) -> Response:
        """Opens up a browser and do your request based on your chosen options below.

        :param url: Target url.
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
        :param blocked_domains: A set of domain names to block requests to. Subdomains are also matched (e.g., ``"example.com"`` blocks ``"sub.example.com"`` too).
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param locale: Set the locale for the browser if wanted. Defaults to the system default locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request.
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param extra_flags: A list of additional browser flags to pass to the browser on launch.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings.
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
        :param headless: Run the browser in headless/hidden (default), or headful/visible mode.
        :param disable_resources: Drop requests for unnecessary resources for a speed boost.
        :param blocked_domains: A set of domain names to block requests to. Subdomains are also matched (e.g., ``"example.com"`` blocks ``"sub.example.com"`` too).
        :param useragent: Pass a useragent string to be used. Otherwise the fetcher will generate a real Useragent of the same browser and use it.
        :param cookies: Set cookies for the next request.
        :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
        :param load_dom: Enabled by default, wait for all JavaScript on page(s) to fully load and execute.
        :param timeout: The timeout in milliseconds that is used in all operations and waits through the page. The default is 30,000
        :param wait: The time (milliseconds) the fetcher will wait after everything finishes before closing the page and returning the Response object.
        :param page_action: Added for automation. A function that takes the `page` object and does the automation you need.
        :param wait_selector: Wait for a specific CSS selector to be in a specific state.
        :param init_script: An absolute path to a JavaScript file to be executed on page creation with this request.
        :param locale: Set the locale for the browser if wanted. Defaults to the system default locale.
        :param wait_selector_state: The state to wait for the selector given with `wait_selector`. The default state is `attached`.
        :param real_chrome: If you have a Chrome browser installed on your device, enable this, and the Fetcher will launch an instance of your browser and use it.
        :param cdp_url: Instead of launching a new browser instance, connect to this CDP URL to control real browsers through CDP.
        :param google_search: Enabled by default, Scrapling will set the referer header to be as if this request came from a Google search of this website's domain name.
        :param extra_headers: A dictionary of extra headers to add to the request.
        :param proxy: The proxy to be used with requests, it can be a string or a dictionary with the keys 'server', 'username', and 'password' only.
        :param extra_flags: A list of additional browser flags to pass to the browser on launch.
        :param selector_config: The arguments that will be passed in the end while creating the final Selector's class.
        :param additional_args: Additional arguments to be passed to Playwright's context as additional settings.
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
