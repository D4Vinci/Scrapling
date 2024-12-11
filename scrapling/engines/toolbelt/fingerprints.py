"""
Functions related to generating headers and fingerprints generally
"""

import platform

from browserforge.fingerprints import Fingerprint, FingerprintGenerator
from browserforge.headers import Browser, HeaderGenerator
from tldextract import extract

from scrapling.core._types import Dict, Union
from scrapling.core.utils import lru_cache


@lru_cache(None, typed=True)
def generate_convincing_referer(url: str) -> str:
    """Takes the domain from the URL without the subdomain/suffix and make it look like you were searching google for this website

    >>> generate_convincing_referer('https://www.somewebsite.com/blah')
    'https://www.google.com/search?q=somewebsite'

    :param url: The URL you are about to fetch.
    :return: Google's search URL of the domain name
    """
    website_name = extract(url).domain
    return f'https://www.google.com/search?q={website_name}'


@lru_cache(None, typed=True)
def get_os_name() -> Union[str, None]:
    """Get the current OS name in the same format needed for browserforge

    :return: Current OS name or `None` otherwise
    """
    #
    os_name = platform.system()
    return {
        'Linux': 'linux',
        'Darwin': 'macos',
        'Windows': 'windows',
        # For the future? because why not
        'iOS': 'ios',
    }.get(os_name)


def generate_suitable_fingerprint() -> Fingerprint:
    """Generates a browserforge's fingerprint that matches current OS, desktop device, and Chrome with version 128 at least.

    This function was originally created to test Browserforge's injector.
    :return: `Fingerprint` object
    """
    return FingerprintGenerator(
        browser=[Browser(name='chrome', min_version=128)],
        os=get_os_name(),  # None is ignored
        device='desktop'
    ).generate()


def generate_headers(browser_mode: bool = False) -> Dict:
    """Generate real browser-like headers using browserforge's generator

    :param browser_mode: If enabled, the headers created are used for playwright so it have to match everything
    :return: A dictionary of the generated headers
    """
    if browser_mode:
        # In this mode we don't care about anything other than matching the OS and the browser type with the browser we are using
        # So we don't raise any inconsistency red flags while websites fingerprinting us
        os_name = get_os_name()
        return HeaderGenerator(
            browser=[Browser(name='chrome', min_version=130)],
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
