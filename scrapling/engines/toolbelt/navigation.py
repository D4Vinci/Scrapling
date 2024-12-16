"""
Functions related to files and URLs
"""
import os
from urllib.parse import urlencode, urlparse

from playwright.async_api import Route as async_Route
from playwright.sync_api import Route

from scrapling.core._types import Dict, Optional, Union
from scrapling.core.utils import log, lru_cache
from scrapling.engines.constants import DEFAULT_DISABLED_RESOURCES


def intercept_route(route: Route):
    """This is just a route handler but it drops requests that its type falls in `DEFAULT_DISABLED_RESOURCES`

    :param route: PlayWright `Route` object of the current page
    :return: PlayWright `Route` object
    """
    if route.request.resource_type in DEFAULT_DISABLED_RESOURCES:
        log.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
        route.abort()
    else:
        route.continue_()


async def async_intercept_route(route: async_Route):
    """This is just a route handler but it drops requests that its type falls in `DEFAULT_DISABLED_RESOURCES`

    :param route: PlayWright `Route` object of the current page
    :return: PlayWright `Route` object
    """
    if route.request.resource_type in DEFAULT_DISABLED_RESOURCES:
        log.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
        await route.abort()
    else:
        await route.continue_()


def construct_proxy_dict(proxy_string: Union[str, Dict[str, str]]) -> Union[Dict, None]:
    """Validate a proxy and return it in the acceptable format for Playwright
    Reference: https://playwright.dev/python/docs/network#http-proxy

    :param proxy_string: A string or a dictionary representation of the proxy.
    :return:
    """
    if proxy_string:
        if isinstance(proxy_string, str):
            proxy = urlparse(proxy_string)
            try:
                return {
                    'server': f'{proxy.scheme}://{proxy.hostname}:{proxy.port}',
                    'username': proxy.username or '',
                    'password': proxy.password or '',
                }
            except ValueError:
                # Urllib will say that one of the parameters above can't be casted to the correct type like `int` for port etc...
                raise TypeError('The proxy argument\'s string is in invalid format!')

        elif isinstance(proxy_string, dict):
            valid_keys = ('server', 'username', 'password', )
            if all(key in valid_keys for key in proxy_string.keys()) and not any(key not in valid_keys for key in proxy_string.keys()):
                return proxy_string
            else:
                raise TypeError(f'A proxy dictionary must have only these keys: {valid_keys}')

        else:
            raise TypeError(f'Invalid type of proxy ({type(proxy_string)}), the proxy argument must be a string or a dictionary!')

    # The default value for proxy in Playwright's source is `None`
    return None


def construct_cdp_url(cdp_url: str, query_params: Optional[Dict] = None) -> str:
    """Takes a CDP URL, reconstruct it to check it's valid, then adds encoded parameters if exists

    :param cdp_url: The target URL.
    :param query_params: A dictionary of the parameters to add.
    :return: The new CDP URL.
    """
    try:
        # Validate the base URL structure
        parsed = urlparse(cdp_url)

        # Check scheme
        if parsed.scheme not in ('ws', 'wss'):
            raise ValueError("CDP URL must use 'ws://' or 'wss://' scheme")

        # Validate hostname and port
        if not parsed.netloc:
            raise ValueError("Invalid hostname for the CDP URL")

        # Ensure path starts with /
        path = parsed.path
        if not path.startswith('/'):
            path = '/' + path

        # Reconstruct the base URL with validated parts
        validated_base = f"{parsed.scheme}://{parsed.netloc}{path}"

        # Add query parameters
        if query_params:
            query_string = urlencode(query_params)
            return f"{validated_base}?{query_string}"

        return validated_base

    except Exception as e:
        raise ValueError(f"Invalid CDP URL: {str(e)}")


@lru_cache(None, typed=True)
def js_bypass_path(filename: str) -> str:
    """Takes the base filename of JS file inside the `bypasses` folder then return the full path of it

    :param filename: The base filename of the JS file.
    :return: The full path of the JS file.
    """
    current_directory = os.path.dirname(__file__)
    return os.path.join(current_directory, 'bypasses', filename)
