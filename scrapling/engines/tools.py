import os
import logging
import inspect
import platform
from scrapling._types import Any, List, Type, Union, Optional
from urllib.parse import urlparse, urlencode

from tldextract import extract
from browserforge.fingerprints import FingerprintGenerator
from browserforge.headers import HeaderGenerator, Browser


def generate_convincing_referer(url):
    """
    Takes the domain from the URL without the subdomain/suffix and make it look like you were searching google for this website

    >>> generate_convincing_referer('https://www.somewebsite.com/blah')
    'https://www.google.com/search?q=somewebsite'

    :param url: The URL you are about to fetch.
    :return:
    """
    website_name = extract(url).domain
    return f'https://www.google.com/search?q={website_name}'


def check_if_engine_usable(engine):
    if isinstance(engine, type):
        raise TypeError("Expected an engine instance, not a class definition of the engine")

    if hasattr(engine, 'fetch'):
        fetch_function = getattr(engine, "fetch")
        if callable(fetch_function):
            if len(inspect.signature(fetch_function).parameters) > 0:
                return engine
            else:
                raise TypeError("Engine class instance must have a callable method 'fetch' with the first argument used for the url.")
        else:
            raise TypeError("Invalid engine instance! Engine class must have a callable method 'fetch'")
    else:
        raise TypeError("Invalid engine instance! Engine class must have the method 'fetch'")


def construct_websocket_url(base_url, query_params):
    # Validate the base URL structure
    try:
        parsed = urlparse(base_url)

        # Check scheme
        if parsed.scheme not in ('ws', 'wss'):
            raise ValueError("URL must use 'ws://' or 'wss://' scheme")

        # Validate hostname and port
        if not parsed.netloc:
            raise ValueError("Invalid hostname")

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
        raise ValueError(f"Invalid WebSocket URL: {str(e)}")


def js_bypass_path(filename):
    current_directory = os.path.dirname(__file__)
    return os.path.join(current_directory, 'bypasses', filename)


def get_os_name():
    # Get the OS name in the same format needed for browserforge
    os_name = platform.system()
    return {
        'Linux': 'linux',
        'Darwin': 'macos',
        'Windows': 'windows',
        # For the future? because why not
        'iOS': 'ios',
    }.get(os_name)


def generate_suitable_fingerprint():
    # This would be for Browserforge playwright injector
    os_name = get_os_name()
    return FingerprintGenerator(
        browser=[Browser(name='chrome', min_version=128)],
        os=os_name,  # None is ignored
        device='desktop'
    ).generate()


def generate_headers(browser_mode=False):
    if browser_mode:
        # In this mode we don't care about anything other than matching the OS and the browser type with the browser we are using
        # So we don't raise any inconsistency red flags while websites fingerprinting us
        os_name = get_os_name()
        return HeaderGenerator(
            browser=[Browser(name='chrome', min_version=128)],
            os=os_name,  # None is ignored
            device='desktop'
        ).generate()
    else:
        # Here it's used for normal requests that aren't done through browsers so we can take it lightly
        browsers = [
            Browser(name='chrome', min_version=120),
            Browser(name='firefox', min_version=120),
            Browser(name='edge', min_version=120),
        ]
        return HeaderGenerator(browser=browsers, device='desktop').generate()


def get_variable_name(var: Any) -> Optional[str]:
    """Get the name of a variable using global and local scopes.
    :param var: The variable to find the name for
    :return: The name of the variable if found, None otherwise
    """
    for scope in [globals(), locals()]:
        for name, value in scope.items():
            if value is var:
                return name
    return None


def check_type_validity(variable: Any, valid_types: Union[List[Type], None], default_value: Any = None, critical: bool = False, param_name: Optional[str] = None) -> Any:
    """Check if a variable matches the specified type constraints.
    :param variable: The variable to check
    :param valid_types: List of valid types for the variable
    :param default_value: Value to return if type check fails
    :param critical: If True, raises TypeError instead of logging error
    :param param_name: Optional parameter name for error messages
    :return: The original variable if valid, default_value if invalid
    :raise TypeError: If critical=True and type check fails
    """
    # Use provided param_name or try to get it automatically
    var_name = param_name or get_variable_name(variable) or "Unknown"

    # Convert valid_types to a list if None
    valid_types = valid_types or []

    # Handle None value
    if variable is None:
        if type(None) in valid_types:
            return variable
        error_msg = f'Argument "{var_name}" cannot be None'
        if critical:
            raise TypeError(error_msg)
        logging.error(f'[Ignored] {error_msg}')
        return default_value

    # If no valid_types specified and variable has a value, return it
    if not valid_types:
        return variable

    # Check if variable type matches any of the valid types
    if not any(isinstance(variable, t) for t in valid_types):
        type_names = [t.__name__ for t in valid_types]
        error_msg = f'Argument "{var_name}" must be of type {" or ".join(type_names)}'
        if critical:
            raise TypeError(error_msg)
        logging.error(f'[Ignored] {error_msg}')
        return default_value

    return variable
