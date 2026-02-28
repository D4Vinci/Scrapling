"""
Functions related to files and URLs
"""

from urllib.parse import urlparse

from playwright.async_api import Route as async_Route
from msgspec import Struct, structs, convert, ValidationError
from playwright.sync_api import Route

from scrapling.core.utils import log
from scrapling.core._types import Dict, Set, Tuple, Optional, Callable
from scrapling.engines.constants import EXTRA_RESOURCES


class ProxyDict(Struct):
    server: str
    username: str = ""
    password: str = ""


def create_intercept_handler(disable_resources: bool, blocked_domains: Optional[Set[str]] = None) -> Callable:
    """Create a route handler that blocks both resource types and specific domains.

    :param disable_resources: Whether to block default resource types.
    :param blocked_domains: Set of domain names to block requests to.
    :return: A sync route handler function.
    """
    disabled_resources = EXTRA_RESOURCES if disable_resources else set()
    domains = blocked_domains or set()

    def handler(route: Route):
        if route.request.resource_type in disabled_resources:
            log.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
            route.abort()
        elif domains:
            hostname = urlparse(route.request.url).hostname or ""
            if any(hostname == d or hostname.endswith("." + d) for d in domains):
                log.debug(f'Blocking request to blocked domain "{hostname}" ({route.request.url})')
                route.abort()
            else:
                route.continue_()
        else:
            route.continue_()

    return handler


def create_async_intercept_handler(disable_resources: bool, blocked_domains: Optional[Set[str]] = None) -> Callable:
    """Create an async route handler that blocks both resource types and specific domains.

    :param disable_resources: Whether to block default resource types.
    :param blocked_domains: Set of domain names to block requests to.
    :return: An async route handler function.
    """
    disabled_resources = EXTRA_RESOURCES if disable_resources else set()
    domains = blocked_domains or set()

    async def handler(route: async_Route):
        if route.request.resource_type in disabled_resources:
            log.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
            await route.abort()
        elif domains:
            hostname = urlparse(route.request.url).hostname or ""
            if any(hostname == d or hostname.endswith("." + d) for d in domains):
                log.debug(f'Blocking request to blocked domain "{hostname}" ({route.request.url})')
                await route.abort()
            else:
                await route.continue_()
        else:
            await route.continue_()

    return handler


def construct_proxy_dict(proxy_string: str | Dict[str, str] | Tuple) -> Dict:
    """Validate a proxy and return it in the acceptable format for Playwright
    Reference: https://playwright.dev/python/docs/network#http-proxy

    :param proxy_string: A string or a dictionary representation of the proxy.
    :return:
    """
    if isinstance(proxy_string, str):
        proxy = urlparse(proxy_string)
        if proxy.scheme not in ("http", "https", "socks4", "socks5") or not proxy.hostname:
            raise ValueError("Invalid proxy string!")

        try:
            result = {
                "server": f"{proxy.scheme}://{proxy.hostname}",
                "username": proxy.username or "",
                "password": proxy.password or "",
            }
            if proxy.port:
                result["server"] += f":{proxy.port}"
            return result
        except ValueError:
            # Urllib will say that one of the parameters above can't be casted to the correct type like `int` for port etc...
            raise ValueError("The proxy argument's string is in invalid format!")

    elif isinstance(proxy_string, dict):
        try:
            validated = convert(proxy_string, ProxyDict)
            result_dict = structs.asdict(validated)
            return result_dict
        except ValidationError as e:
            raise TypeError(f"Invalid proxy dictionary: {e}")

    raise TypeError(f"Invalid proxy string: {proxy_string}")
