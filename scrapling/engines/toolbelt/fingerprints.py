"""
Functions related to generating headers and fingerprints generally
"""

from platform import system as platform_system

from tldextract import extract
from browserforge.headers import Browser, HeaderGenerator

from scrapling.core._types import Dict, Optional
from scrapling.core.utils import lru_cache

__OS_NAME__ = platform_system()


@lru_cache(10, typed=True)
def generate_convincing_referer(url: str) -> str:
    """Takes the domain from the URL without the subdomain/suffix and make it look like you were searching Google for this website

    >>> generate_convincing_referer('https://www.somewebsite.com/blah')
    'https://www.google.com/search?q=somewebsite'

    :param url: The URL you are about to fetch.
    :return: Google's search URL of the domain name
    """
    website_name = extract(url).domain
    return f"https://www.google.com/search?q={website_name}"


@lru_cache(1, typed=True)
def get_os_name() -> Optional[str]:
    """Get the current OS name in the same format needed for browserforge

    :return: Current OS name or `None` otherwise
    """
    return {
        "Linux": "linux",
        "Darwin": "macos",
        "Windows": "windows",
        # For the future? because why not?
        "iOS": "ios",
    }.get(__OS_NAME__)


def generate_headers(browser_mode: bool = False) -> Dict:
    """Generate real browser-like headers using browserforge's generator

    :param browser_mode: If enabled, the headers created are used for playwright, so it has to match everything
    :return: A dictionary of the generated headers
    """
    # In the browser mode, we don't care about anything other than matching the OS and the browser type with the browser we are using,
    # So we don't raise any inconsistency red flags while websites fingerprinting us
    os_name = get_os_name()
    browsers = [Browser(name="chrome", min_version=130)]
    if not browser_mode:
        os_name = ("windows", "macos", "linux")
        browsers.extend(
            [
                Browser(name="firefox", min_version=130),
                Browser(name="edge", min_version=130),
            ]
        )

    return HeaderGenerator(browser=browsers, os=os_name, device="desktop").generate()


__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")
