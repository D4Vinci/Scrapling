"""
Functions related to generating headers and fingerprints generally
"""

from functools import lru_cache
from os import getenv
from platform import system as platform_system

from browserforge.headers import Browser, HeaderGenerator
from browserforge.headers.generator import SUPPORTED_OPERATING_SYSTEMS

from scrapling.core._types import Dict, Literal, Tuple

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows"]
_CHROMIUM_VERSION_FALLBACK = 147
_CHROME_VERSION_FALLBACK = 147


def _browser_major_from_env(name: str, fallback: int) -> int:
    value = getenv(name)
    if value and value.isdigit():
        return int(value)
    return fallback


chromium_version = _browser_major_from_env("SCRAPLING_CHROMIUM_VERSION", _CHROMIUM_VERSION_FALLBACK)
chrome_version = _browser_major_from_env("SCRAPLING_CHROME_VERSION", _CHROME_VERSION_FALLBACK)


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


@lru_cache(1, typed=True)
def default_useragent() -> str:
    return generate_headers(browser_mode=False).get("User-Agent", "")


@lru_cache(2, typed=True)
def default_browser_useragent(real_chrome: bool = False) -> str:
    return generate_headers(browser_mode="chrome" if real_chrome else True).get("User-Agent", "")


def __getattr__(name: str):
    if name == "__default_useragent__":
        return default_useragent()
    raise AttributeError(name)
