"""
Functions related to generating headers and fingerprints generally
"""

from functools import lru_cache
from platform import system as platform_system

from apify_fingerprint_datapoints import get_browser_helper_file
from browserforge.headers import Browser, HeaderGenerator
from browserforge.headers.generator import SUPPORTED_OPERATING_SYSTEMS
from orjson import loads

from scrapling.core._types import Dict, Literal, Tuple

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows"]
# Current versions hardcoded for now (Playwright doesn't allow to know the version of a browser without launching it)
chromium_version = 149
chrome_version = 149


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


@lru_cache(4, typed=True)
def _dataset_versions(name: str) -> Tuple:
    """Get the major versions of a browser that the installed fingerprints dataset ships with.

    :param name: The browser name as browserforge knows it
    :return: The versions found, ordered from the newest to the oldest
    """
    prefix = f"{name}/"
    entries = loads(get_browser_helper_file().read_bytes())
    versions = {int(entry[len(prefix) :].split(".")[0]) for entry in entries if entry.startswith(prefix)}
    return tuple(sorted(versions, reverse=True))


@lru_cache(8, typed=True)
def _newest_supported_version(name: str, ceiling: int, os_name: OSName | Tuple) -> int:
    """Find the newest version of a browser that the installed browserforge dataset can still generate headers for.

    :param name: The browser name as browserforge knows it
    :param ceiling: The wanted version, no version newer than it is considered
    :param os_name: The same OS constraint the caller uses, as it affects which versions are usable
    :return: The newest usable version, or `ceiling` itself if none was found
    """
    # Shipping a version doesn't mean headers can be generated for it, as the OS and the device
    # have to line up with it as well, so each candidate is confirmed before we settle on it
    for version in _dataset_versions(name):
        if version > ceiling:
            continue

        try:
            HeaderGenerator(
                browser=[Browser(name=name, min_version=version, max_version=version)],
                os=os_name,
                device="desktop",
            ).generate()
            return version
        except ValueError:
            continue

    return ceiling


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
    try:
        return HeaderGenerator(browser=browsers, os=os_name, device="desktop").generate()
    except ValueError:
        # The versions above are pinned to the browsers we drive, but browserforge's dataset is shipped
        # separately and can lag behind them. Degrading to the newest version it does know about keeps the
        # pinning intent while stopping that data gap from turning into an import-time crash.
        supported = _newest_supported_version("chrome", ver, os_name)
        browsers[0] = Browser(name="chrome", min_version=supported, max_version=supported)
        return HeaderGenerator(browser=browsers, os=os_name, device="desktop").generate()


__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")
