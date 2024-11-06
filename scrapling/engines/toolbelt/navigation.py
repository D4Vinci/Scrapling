"""
Functions related to files and URLs
"""

import os
import logging
from urllib.parse import urlparse, urlencode

from scrapling.core._types import Union, Dict, Optional
from scrapling.engines.constants import DEFAULT_DISABLED_RESOURCES

from playwright.sync_api import Route


def intercept_route(route: Route) -> Union[Route, None]:
    """This is just a route handler but it drops requests that its type falls in `DEFAULT_DISABLED_RESOURCES`

    :param route: PlayWright `Route` object of the current page
    :return: PlayWright `Route` object
    """
    if route.request.resource_type in DEFAULT_DISABLED_RESOURCES:
        logging.debug(f'Blocking background resource "{route.request.url}" of type "{route.request.resource_type}"')
        return route.abort()
    return route.continue_()


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


def js_bypass_path(filename: str) -> str:
    """Takes the base filename of JS file inside the `bypasses` folder then return the full path of it

    :param filename: The base filename of the JS file.
    :return: The full path of the JS file.
    """
    current_directory = os.path.dirname(__file__)
    return os.path.join(current_directory, 'bypasses', filename)
