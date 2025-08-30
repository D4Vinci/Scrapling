from pathlib import Path
from subprocess import check_output
from sys import executable as python_executable

from scrapling.core.utils import log
from scrapling.engines.toolbelt import Response
from scrapling.core._types import List, Optional, Dict, Tuple, Any, Callable
from scrapling.fetchers import Fetcher, DynamicFetcher, StealthyFetcher
from scrapling.core.shell import Convertor, _CookieParser, _ParseHeaders

from orjson import loads as json_loads, JSONDecodeError
from click import command, option, Choice, group, argument

__OUTPUT_FILE_HELP__ = "The output file path can be an HTML file, a Markdown file of the HTML content, or the text content itself. Use file extensions (`.html`/`.md`/`.txt`) respectively."
__PACKAGE_DIR__ = Path(__file__).parent


def __Execute(cmd: List[str], help_line: str) -> None:  # pragma: no cover
    print(f"Installing {help_line}...")
    _ = check_output(cmd, shell=False)  # nosec B603
    # I meant to not use try except here


def __ParseJSONData(json_string: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Parse JSON string into a Python object"""
    if not json_string:
        return None

    try:
        return json_loads(json_string)
    except JSONDecodeError as e:  # pragma: no cover
        raise ValueError(f"Invalid JSON data '{json_string}': {e}")


def __Request_and_Save(
    fetcher_func: Callable[..., Response],
    url: str,
    output_file: str,
    css_selector: Optional[str] = None,
    **kwargs,
) -> None:
    """Make a request using the specified fetcher function and save the result"""
    # Handle relative paths - convert to an absolute path based on the current working directory
    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_file

    response = fetcher_func(url, **kwargs)
    Convertor.write_content_to_file(response, str(output_path), css_selector)
    log.info(f"Content successfully saved to '{output_path}'")


def __ParseExtractArguments(
    headers: List[str], cookies: str, params: str, json: Optional[str] = None
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Optional[Dict[str, str]]]:
    """Parse arguments for extract command"""
    parsed_headers, parsed_cookies = _ParseHeaders(headers)
    if cookies:
        for key, value in _CookieParser(cookies):
            try:
                parsed_cookies[key] = value
            except Exception as e:
                raise ValueError(f"Could not parse cookies '{cookies}': {e}")

    parsed_json = __ParseJSONData(json)
    parsed_params = {}
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            parsed_params[key] = value

    return parsed_headers, parsed_cookies, parsed_params, parsed_json


def __BuildRequest(
    headers: List[str], cookies: str, params: str, json: Optional[str] = None, **kwargs
) -> Dict:
    """Build a request object using the specified arguments"""
    # Parse parameters
    parsed_headers, parsed_cookies, parsed_params, parsed_json = (
        __ParseExtractArguments(headers, cookies, params, json)
    )
    # Build request arguments
    request_kwargs = {
        "headers": parsed_headers if parsed_headers else None,
        "cookies": parsed_cookies if parsed_cookies else None,
    }
    if parsed_json:
        request_kwargs["json"] = parsed_json
    if parsed_params:
        request_kwargs["params"] = parsed_params
    if "proxy" in kwargs:
        request_kwargs["proxy"] = kwargs.pop("proxy")

    return {**request_kwargs, **kwargs}


@command(help="Install all Scrapling's Fetchers dependencies")
@option(
    "-f",
    "--force",
    "force",
    is_flag=True,
    default=False,
    type=bool,
    help="Force Scrapling to reinstall all Fetchers dependencies",
)
def install(force):  # pragma: no cover
    if (
        force
        or not __PACKAGE_DIR__.joinpath(".scrapling_dependencies_installed").exists()
    ):
        __Execute(
            [python_executable, "-m", "playwright", "install", "chromium"],
            "Playwright browsers",
        )
        __Execute(
            [
                python_executable,
                "-m",
                "playwright",
                "install-deps",
                "chromium",
                "firefox",
            ],
            "Playwright dependencies",
        )
        __Execute(
            [python_executable, "-m", "camoufox", "fetch", "--browserforge"],
            "Camoufox browser and databases",
        )
        # if no errors raised by the above commands, then we add the below file
        __PACKAGE_DIR__.joinpath(".scrapling_dependencies_installed").touch()
    else:
        print("The dependencies are already installed")


@command(help="Run Scrapling's MCP server (Check the docs for more info).")
def mcp():
    from scrapling.core.ai import ScraplingMCPServer

    ScraplingMCPServer().serve()


@command(help="Interactive scraping console")
@option(
    "-c",
    "--code",
    "code",
    is_flag=False,
    default="",
    type=str,
    help="Evaluate the code in the shell, print the result and exit",
)
@option(
    "-L",
    "--loglevel",
    "level",
    is_flag=False,
    default="debug",
    type=Choice(
        ["debug", "info", "warning", "error", "critical", "fatal"], case_sensitive=False
    ),
    help="Log level (default: DEBUG)",
)
def shell(code, level):
    from scrapling.core.shell import CustomShell

    console = CustomShell(code=code, log_level=level)
    console.start()


@group(
    help="Fetch web pages using various fetchers and extract full/selected HTML content as HTML, Markdown, or extract text content."
)
def extract():
    """Extract content from web pages and save to files"""
    pass


@extract.command(
    help=f"Perform a GET request and save the content to a file.\n\n{__OUTPUT_FILE_HELP__}"
)
@argument("url", required=True)
@argument("output_file", required=True)
@option(
    "--headers",
    "-H",
    multiple=True,
    help='HTTP headers in format "Key: Value" (can be used multiple times)',
)
@option("--cookies", help='Cookies string in format "name1=value1; name2=value2"')
@option(
    "--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)"
)
@option("--proxy", help='Proxy URL in format "http://username:password@host:port"')
@option(
    "--css-selector",
    "-s",
    help="CSS selector to extract specific content from the page. It returns all matches.",
)
@option(
    "--params",
    "-p",
    multiple=True,
    help='Query parameters in format "key=value" (can be used multiple times)',
)
@option(
    "--follow-redirects/--no-follow-redirects",
    default=True,
    help="Whether to follow redirects (default: True)",
)
@option(
    "--verify/--no-verify",
    default=True,
    help="Whether to verify SSL certificates (default: True)",
)
@option("--impersonate", help="Browser to impersonate (e.g., chrome, firefox).")
@option(
    "--stealthy-headers/--no-stealthy-headers",
    default=True,
    help="Use stealthy browser headers (default: True)",
)
def get(
    url,
    output_file,
    headers,
    cookies,
    timeout,
    proxy,
    css_selector,
    params,
    follow_redirects,
    verify,
    impersonate,
    stealthy_headers,
):
    """
    Perform a GET request and save the content to a file.

    :param url: Target URL for the request.
    :param output_file: Output file path (.md for Markdown, .html for HTML).
    :param headers: HTTP headers to include in the request.
    :param cookies: Cookies to use in the request.
    :param timeout: Number of seconds to wait before timing out.
    :param proxy: Proxy URL to use. (Format: "http://username:password@localhost:8030")
    :param css_selector: CSS selector to extract specific content.
    :param params: Query string parameters for the request.
    :param follow_redirects: Whether to follow redirects.
    :param verify: Whether to verify HTTPS certificates.
    :param impersonate: Browser version to impersonate.
    :param stealthy_headers: If enabled, creates and adds real browser headers.
    """

    kwargs = __BuildRequest(
        headers,
        cookies,
        params,
        None,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        stealthy_headers=stealthy_headers,
        impersonate=impersonate,
        proxy=proxy,
    )
    __Request_and_Save(Fetcher.get, url, output_file, css_selector, **kwargs)


@extract.command(
    help=f"Perform a POST request and save the content to a file.\n\n{__OUTPUT_FILE_HELP__}"
)
@argument("url", required=True)
@argument("output_file", required=True)
@option(
    "--data",
    "-d",
    help='Form data to include in the request body (as string, ex: "param1=value1&param2=value2")',
)
@option("--json", "-j", help="JSON data to include in the request body (as string)")
@option(
    "--headers",
    "-H",
    multiple=True,
    help='HTTP headers in format "Key: Value" (can be used multiple times)',
)
@option("--cookies", help='Cookies string in format "name1=value1; name2=value2"')
@option(
    "--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)"
)
@option("--proxy", help='Proxy URL in format "http://username:password@host:port"')
@option(
    "--css-selector",
    "-s",
    help="CSS selector to extract specific content from the page. It returns all matches.",
)
@option(
    "--params",
    "-p",
    multiple=True,
    help='Query parameters in format "key=value" (can be used multiple times)',
)
@option(
    "--follow-redirects/--no-follow-redirects",
    default=True,
    help="Whether to follow redirects (default: True)",
)
@option(
    "--verify/--no-verify",
    default=True,
    help="Whether to verify SSL certificates (default: True)",
)
@option("--impersonate", help="Browser to impersonate (e.g., chrome, firefox).")
@option(
    "--stealthy-headers/--no-stealthy-headers",
    default=True,
    help="Use stealthy browser headers (default: True)",
)
def post(
    url,
    output_file,
    data,
    json,
    headers,
    cookies,
    timeout,
    proxy,
    css_selector,
    params,
    follow_redirects,
    verify,
    impersonate,
    stealthy_headers,
):
    """
    Perform a POST request and save the content to a file.

    :param url: Target URL for the request.
    :param output_file: Output file path (.md for Markdown, .html for HTML).
    :param data: Form data to include in the request body. (as string, ex: "param1=value1&param2=value2")
    :param json: A JSON serializable object to include in the body of the request.
    :param headers: Headers to include in the request.
    :param cookies: Cookies to use in the request.
    :param timeout: Number of seconds to wait before timing out.
    :param proxy: Proxy URL to use.
    :param css_selector: CSS selector to extract specific content.
    :param params: Query string parameters for the request.
    :param follow_redirects: Whether to follow redirects.
    :param verify: Whether to verify HTTPS certificates.
    :param impersonate: Browser version to impersonate.
    :param stealthy_headers: If enabled, creates and adds real browser headers.
    """

    kwargs = __BuildRequest(
        headers,
        cookies,
        params,
        json,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        stealthy_headers=stealthy_headers,
        impersonate=impersonate,
        proxy=proxy,
        data=data,
    )
    __Request_and_Save(Fetcher.post, url, output_file, css_selector, **kwargs)


@extract.command(
    help=f"Perform a PUT request and save the content to a file.\n\n{__OUTPUT_FILE_HELP__}"
)
@argument("url", required=True)
@argument("output_file", required=True)
@option("--data", "-d", help="Form data to include in the request body")
@option("--json", "-j", help="JSON data to include in the request body (as string)")
@option(
    "--headers",
    "-H",
    multiple=True,
    help='HTTP headers in format "Key: Value" (can be used multiple times)',
)
@option("--cookies", help='Cookies string in format "name1=value1; name2=value2"')
@option(
    "--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)"
)
@option("--proxy", help='Proxy URL in format "http://username:password@host:port"')
@option(
    "--css-selector",
    "-s",
    help="CSS selector to extract specific content from the page. It returns all matches.",
)
@option(
    "--params",
    "-p",
    multiple=True,
    help='Query parameters in format "key=value" (can be used multiple times)',
)
@option(
    "--follow-redirects/--no-follow-redirects",
    default=True,
    help="Whether to follow redirects (default: True)",
)
@option(
    "--verify/--no-verify",
    default=True,
    help="Whether to verify SSL certificates (default: True)",
)
@option("--impersonate", help="Browser to impersonate (e.g., chrome, firefox).")
@option(
    "--stealthy-headers/--no-stealthy-headers",
    default=True,
    help="Use stealthy browser headers (default: True)",
)
def put(
    url,
    output_file,
    data,
    json,
    headers,
    cookies,
    timeout,
    proxy,
    css_selector,
    params,
    follow_redirects,
    verify,
    impersonate,
    stealthy_headers,
):
    """
    Perform a PUT request and save the content to a file.

    :param url: Target URL for the request.
    :param output_file: Output file path (.md for Markdown, .html for HTML).
    :param data: Form data to include in the request body.
    :param json: A JSON serializable object to include in the body of the request.
    :param headers: Headers to include in the request.
    :param cookies: Cookies to use in the request.
    :param timeout: Number of seconds to wait before timing out.
    :param proxy: Proxy URL to use.
    :param css_selector: CSS selector to extract specific content.
    :param params: Query string parameters for the request.
    :param follow_redirects: Whether to follow redirects.
    :param verify: Whether to verify HTTPS certificates.
    :param impersonate: Browser version to impersonate.
    :param stealthy_headers: If enabled, creates and adds real browser headers.
    """

    kwargs = __BuildRequest(
        headers,
        cookies,
        params,
        json,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        stealthy_headers=stealthy_headers,
        impersonate=impersonate,
        proxy=proxy,
        data=data,
    )
    __Request_and_Save(Fetcher.put, url, output_file, css_selector, **kwargs)


@extract.command(
    help=f"Perform a DELETE request and save the content to a file.\n\n{__OUTPUT_FILE_HELP__}"
)
@argument("url", required=True)
@argument("output_file", required=True)
@option(
    "--headers",
    "-H",
    multiple=True,
    help='HTTP headers in format "Key: Value" (can be used multiple times)',
)
@option("--cookies", help='Cookies string in format "name1=value1; name2=value2"')
@option(
    "--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)"
)
@option("--proxy", help='Proxy URL in format "http://username:password@host:port"')
@option(
    "--css-selector",
    "-s",
    help="CSS selector to extract specific content from the page. It returns all matches.",
)
@option(
    "--params",
    "-p",
    multiple=True,
    help='Query parameters in format "key=value" (can be used multiple times)',
)
@option(
    "--follow-redirects/--no-follow-redirects",
    default=True,
    help="Whether to follow redirects (default: True)",
)
@option(
    "--verify/--no-verify",
    default=True,
    help="Whether to verify SSL certificates (default: True)",
)
@option("--impersonate", help="Browser to impersonate (e.g., chrome, firefox).")
@option(
    "--stealthy-headers/--no-stealthy-headers",
    default=True,
    help="Use stealthy browser headers (default: True)",
)
def delete(
    url,
    output_file,
    headers,
    cookies,
    timeout,
    proxy,
    css_selector,
    params,
    follow_redirects,
    verify,
    impersonate,
    stealthy_headers,
):
    """
    Perform a DELETE request and save the content to a file.

    :param url: Target URL for the request.
    :param output_file: Output file path (.md for Markdown, .html for HTML).
    :param headers: Headers to include in the request.
    :param cookies: Cookies to use in the request.
    :param timeout: Number of seconds to wait before timing out.
    :param proxy: Proxy URL to use.
    :param css_selector: CSS selector to extract specific content.
    :param params: Query string parameters for the request.
    :param follow_redirects: Whether to follow redirects.
    :param verify: Whether to verify HTTPS certificates.
    :param impersonate: Browser version to impersonate.
    :param stealthy_headers: If enabled, creates and adds real browser headers.
    """

    kwargs = __BuildRequest(
        headers,
        cookies,
        params,
        None,
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify=verify,
        stealthy_headers=stealthy_headers,
        impersonate=impersonate,
        proxy=proxy,
    )
    __Request_and_Save(Fetcher.delete, url, output_file, css_selector, **kwargs)


@extract.command(
    help=f"Use DynamicFetcher to fetch content with browser automation.\n\n{__OUTPUT_FILE_HELP__}"
)
@argument("url", required=True)
@argument("output_file", required=True)
@option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode (default: True)",
)
@option(
    "--disable-resources/--enable-resources",
    default=False,
    help="Drop unnecessary resources for speed boost (default: False)",
)
@option(
    "--network-idle/--no-network-idle",
    default=False,
    help="Wait for network idle (default: False)",
)
@option(
    "--timeout",
    type=int,
    default=30000,
    help="Timeout in milliseconds (default: 30000)",
)
@option(
    "--wait",
    type=int,
    default=0,
    help="Additional wait time in milliseconds after page load (default: 0)",
)
@option(
    "--css-selector",
    "-s",
    help="CSS selector to extract specific content from the page. It returns all matches.",
)
@option("--wait-selector", help="CSS selector to wait for before proceeding")
@option("--locale", default="en-US", help="Browser locale (default: en-US)")
@option(
    "--stealth/--no-stealth", default=False, help="Enable stealth mode (default: False)"
)
@option(
    "--hide-canvas/--show-canvas",
    default=False,
    help="Add noise to canvas operations (default: False)",
)
@option(
    "--disable-webgl/--enable-webgl",
    default=False,
    help="Disable WebGL support (default: False)",
)
@option("--proxy", help='Proxy URL in format "http://username:password@host:port"')
@option(
    "--extra-headers",
    "-H",
    multiple=True,
    help='Extra headers in format "Key: Value" (can be used multiple times)',
)
def fetch(
    url,
    output_file,
    headless,
    disable_resources,
    network_idle,
    timeout,
    wait,
    css_selector,
    wait_selector,
    locale,
    stealth,
    hide_canvas,
    disable_webgl,
    proxy,
    extra_headers,
):
    """
    Opens up a browser and fetch content using DynamicFetcher.

    :param url: Target url.
    :param output_file: Output file path (.md for Markdown, .html for HTML).
    :param headless: Run the browser in headless/hidden or headful/visible mode.
    :param disable_resources: Drop requests of unnecessary resources for a speed boost.
    :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
    :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
    :param wait: The time (milliseconds) the fetcher will wait after everything finishes before returning.
    :param css_selector: CSS selector to extract specific content.
    :param wait_selector: Wait for a specific CSS selector to be in a specific state.
    :param locale: Set the locale for the browser.
    :param stealth: Enables stealth mode.
    :param hide_canvas: Add random noise to canvas operations to prevent fingerprinting.
    :param disable_webgl: Disables WebGL and WebGL 2.0 support entirely.
    :param proxy: The proxy to be used with requests.
    :param extra_headers: Extra headers to add to the request.
    """

    # Parse parameters
    parsed_headers, _ = _ParseHeaders(extra_headers, False)

    # Build request arguments
    kwargs = {
        "headless": headless,
        "disable_resources": disable_resources,
        "network_idle": network_idle,
        "timeout": timeout,
        "locale": locale,
        "stealth": stealth,
        "hide_canvas": hide_canvas,
        "disable_webgl": disable_webgl,
    }

    if wait > 0:
        kwargs["wait"] = wait
    if wait_selector:
        kwargs["wait_selector"] = wait_selector
    if proxy:
        kwargs["proxy"] = proxy
    if parsed_headers:
        kwargs["extra_headers"] = parsed_headers

    __Request_and_Save(DynamicFetcher.fetch, url, output_file, css_selector, **kwargs)


@extract.command(
    help=f"Use StealthyFetcher to fetch content with advanced stealth features.\n\n{__OUTPUT_FILE_HELP__}"
)
@argument("url", required=True)
@argument("output_file", required=True)
@option(
    "--headless/--no-headless",
    default=True,
    help="Run browser in headless mode (default: True)",
)
@option(
    "--block-images/--allow-images",
    default=False,
    help="Block image loading (default: False)",
)
@option(
    "--disable-resources/--enable-resources",
    default=False,
    help="Drop unnecessary resources for speed boost (default: False)",
)
@option(
    "--block-webrtc/--allow-webrtc",
    default=False,
    help="Block WebRTC entirely (default: False)",
)
@option(
    "--humanize/--no-humanize",
    default=False,
    help="Humanize cursor movement (default: False)",
)
@option(
    "--solve-cloudflare/--no-solve-cloudflare",
    default=False,
    help="Solve Cloudflare challenges (default: False)",
)
@option("--allow-webgl/--block-webgl", default=True, help="Allow WebGL (default: True)")
@option(
    "--network-idle/--no-network-idle",
    default=False,
    help="Wait for network idle (default: False)",
)
@option(
    "--disable-ads/--allow-ads",
    default=False,
    help="Install uBlock Origin addon (default: False)",
)
@option(
    "--timeout",
    type=int,
    default=30000,
    help="Timeout in milliseconds (default: 30000)",
)
@option(
    "--wait",
    type=int,
    default=0,
    help="Additional wait time in milliseconds after page load (default: 0)",
)
@option(
    "--css-selector",
    "-s",
    help="CSS selector to extract specific content from the page. It returns all matches.",
)
@option("--wait-selector", help="CSS selector to wait for before proceeding")
@option(
    "--geoip/--no-geoip",
    default=False,
    help="Use IP geolocation for timezone/locale (default: False)",
)
@option("--proxy", help='Proxy URL in format "http://username:password@host:port"')
@option(
    "--extra-headers",
    "-H",
    multiple=True,
    help='Extra headers in format "Key: Value" (can be used multiple times)',
)
def stealthy_fetch(
    url,
    output_file,
    headless,
    block_images,
    disable_resources,
    block_webrtc,
    humanize,
    solve_cloudflare,
    allow_webgl,
    network_idle,
    disable_ads,
    timeout,
    wait,
    css_selector,
    wait_selector,
    geoip,
    proxy,
    extra_headers,
):
    """
    Opens up a browser with advanced stealth features and fetch content using StealthyFetcher.

    :param url: Target url.
    :param output_file: Output file path (.md for Markdown, .html for HTML).
    :param headless: Run the browser in headless/hidden, or headful/visible mode.
    :param block_images: Prevent the loading of images through Firefox preferences.
    :param disable_resources: Drop requests of unnecessary resources for a speed boost.
    :param block_webrtc: Blocks WebRTC entirely.
    :param humanize: Humanize the cursor movement.
    :param solve_cloudflare: Solves all 3 types of the Cloudflare's Turnstile wait page.
    :param allow_webgl: Allow WebGL (recommended to keep enabled).
    :param network_idle: Wait for the page until there are no network connections for at least 500 ms.
    :param disable_ads: Install the uBlock Origin addon on the browser.
    :param timeout: The timeout in milliseconds that is used in all operations and waits through the page.
    :param wait: The time (milliseconds) the fetcher will wait after everything finishes before returning.
    :param css_selector: CSS selector to extract specific content.
    :param wait_selector: Wait for a specific CSS selector to be in a specific state.
    :param geoip: Automatically use IP's longitude, latitude, timezone, country, locale.
    :param proxy: The proxy to be used with requests.
    :param extra_headers: Extra headers to add to the request.
    """

    # Parse parameters
    parsed_headers, _ = _ParseHeaders(extra_headers, False)

    # Build request arguments
    kwargs = {
        "headless": headless,
        "block_images": block_images,
        "disable_resources": disable_resources,
        "block_webrtc": block_webrtc,
        "humanize": humanize,
        "solve_cloudflare": solve_cloudflare,
        "allow_webgl": allow_webgl,
        "network_idle": network_idle,
        "disable_ads": disable_ads,
        "timeout": timeout,
        "geoip": geoip,
    }

    if wait > 0:
        kwargs["wait"] = wait
    if wait_selector:
        kwargs["wait_selector"] = wait_selector
    if proxy:
        kwargs["proxy"] = proxy
    if parsed_headers:
        kwargs["extra_headers"] = parsed_headers

    __Request_and_Save(StealthyFetcher.fetch, url, output_file, css_selector, **kwargs)


@group()
def main():
    pass


# Adding commands
main.add_command(install)
main.add_command(shell)
main.add_command(extract)
main.add_command(mcp)
