"""
Functions related to generating headers and fingerprints generally
"""

import json
from functools import lru_cache
from platform import system as platform_system

from apify_fingerprint_datapoints import get_browser_helper_file
from browserforge.headers import Browser, HeaderGenerator
from browserforge.headers.generator import SUPPORTED_OPERATING_SYSTEMS

from scrapling.core._types import Dict, Literal, Tuple

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows"]


# The installed `apify-fingerprint-datapoints` release only ships fingerprint data up to a
# certain browser version. Playwright doesn't expose the real installed browser version without
# launching it, so we ask the datapack itself what the newest version it actually has data for is,
# instead of hardcoding a version number that can drift ahead of the installed datapack and make
# browserforge's HeaderGenerator raise `ValueError: No headers based on this input can be
# generated` at import time (see https://github.com/D4Vinci/Scrapling/issues/396).
@lru_cache(1, typed=True)
def _max_supported_version(browser: str) -> int:
    """Get the newest major version of `browser` that the installed fingerprint datapack has data for.

    :param browser: Browser name as used in the datapack, e.g. ``"chrome"``.
    :return: Newest supported major version number.
    """
    entries = json.loads(get_browser_helper_file().read_bytes())
    versions = [int(entry.split("/")[1].split(".")[0]) for entry in entries if entry.startswith(f"{browser}/")]
    if not versions:
        raise ValueError(f"The installed fingerprint datapack has no entries for browser {browser!r}")
    return max(versions)


chromium_version = _max_supported_version("chrome")
chrome_version = chromium_version


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
