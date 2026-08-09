"""
Functions related to generating headers and fingerprints generally
"""

import re
import sys
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path
from platform import system as platform_system

from browserforge.headers import Browser, HeaderGenerator
from browserforge.headers.generator import SUPPORTED_DEVICES, SUPPORTED_OPERATING_SYSTEMS
from orjson import loads

from scrapling.core._types import Dict, Literal, Tuple

__OS_NAME__ = platform_system()
OSName = Literal["linux", "macos", "windows", "android", "ios"]
DESKTOP_OS = ("linux", "macos", "windows")
MINIMUM_VERSION = 149


@lru_cache(1, typed=True)
def get_os_name() -> OSName | Tuple:
    """Get the current OS name in the same format needed for browserforge, if the OS is Unknown, return all the OSes browserforge supports.

    :return: Current OS name or all supported OSes otherwise
    """
    match __OS_NAME__:  # pragma: no cover
        case "Linux":
            return "android" if hasattr(sys, "getandroidapilevel") else "linux"
        case "Darwin":
            return "macos"
        case "Windows":
            return "windows"
        case "Android":
            return "android"
        case "iOS" | "iPadOS":
            return "ios"
        case _:
            return SUPPORTED_OPERATING_SYSTEMS


@lru_cache(2, typed=True)
def driven_browser_version(package: str = "playwright") -> int | None:
    """Get the Chromium major version the installed automation package drives, read from its bundled `browsers.json`.

    :param package: The automation package to inspect, e.g. `"playwright"` or `"patchright"`
    :return: The Chromium major version, or `None` if it couldn't be determined
    """
    spec = find_spec(package)
    if spec is None or not spec.origin:
        return None
    path = Path(spec.origin).parent / "driver" / "package" / "browsers.json"
    if not path.is_file():
        return None
    try:
        browsers = loads(path.read_bytes()).get("browsers", [])
        version = next((entry["browserVersion"] for entry in browsers if entry.get("name") == "chromium"), None)
        return int(version.partition(".")[0]) if version else None
    except (ValueError, TypeError, KeyError):
        return None


def generate_headers(browser_mode: bool | str = False) -> Dict:
    """Generate real browser-like headers using browserforge's generator

    :param browser_mode: If enabled, the headers created are used for playwright, so it has to match everything
    :return: A dictionary of the generated headers
    """
    os_name = get_os_name()
    device: str | Tuple = (
        "desktop" if os_name in DESKTOP_OS else "mobile" if isinstance(os_name, str) else SUPPORTED_DEVICES
    )
    if not browser_mode and os_name in DESKTOP_OS:
        os_name = DESKTOP_OS
    browsers = [Browser(name="chrome", min_version=MINIMUM_VERSION)]
    if not browser_mode:
        browsers.extend([Browser(name="firefox", min_version=147), Browser(name="edge", min_version=145)])
    try:
        headers = HeaderGenerator(browser=browsers, os=os_name, device=device).generate()
    except ValueError:
        headers = HeaderGenerator(
            browser=[Browser(name=b.name) for b in browsers], os=os_name, device=device
        ).generate()
    if browser_mode and (driven := driven_browser_version() or driven_browser_version("patchright")):
        if user_agent := headers.get("User-Agent"):
            headers["User-Agent"] = re.sub(r"Chrome/[\d.]+", f"Chrome/{driven}.0.0.0", user_agent)
    return headers


__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")
