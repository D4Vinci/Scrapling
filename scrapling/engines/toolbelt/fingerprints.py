"""
Functions related to generating headers and fingerprints generally
"""

from functools import lru_cache
from platform import system as platform_system

from browserforge.headers import Browser, HeaderGenerator
from browserforge.headers.generator import SUPPORTED_OPERATING_SYSTEMS

from scrapling.core._types import Dict, Literal, Tuple

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows"]
# Current versions hardcoded for now (Playwright doesn't allow to know the version of a browser without launching it)
chromium_version = 145
chrome_version = 145


@lru_cache(1, typed=True)
def get_os_name() -> OSName | Tuple:
    """Get the current OS name in the same format needed for browserforge, if the OS is Unknown, return None so browserforge uses all.

    :return: Current OS name or `None` otherwise
    """
    match __OS_NAME__:  # pragma: no cover
        case "Linux":
            return "linux"
        case "Darwin":
            return "macos"
        case "Windows":
            return "windows"
        case _:
            return SUPPORTED_OPERATING_SYSTEMS


def generate_headers(browser_mode: bool | str = False) -> Dict:
    """Generate real browser-like headers using browserforge's generator

    :param browser_mode: If enabled, the headers created are used for playwright, so it has to match everything
    :return: A dictionary of the generated headers
    """
    # In the browser mode, we don't care about anything other than matching the OS and the browser type with the browser we are using,
    # So we don't raise any inconsistency red flags while websites fingerprinting us
    os_name = get_os_name()
    ver = chrome_version if browser_mode and browser_mode == "chrome" else chromium_version
    browsers = [Browser(name="chrome", min_version=ver, max_version=ver)]
    if not browser_mode:
        os_name = ("windows", "macos", "linux")
        browsers.extend(
            [
                Browser(name="firefox", min_version=142),
                Browser(name="edge", min_version=140),
            ]
        )
    return HeaderGenerator(browser=browsers, os=os_name, device="desktop").generate()


__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")
