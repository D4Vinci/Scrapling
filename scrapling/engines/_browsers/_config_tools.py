from functools import lru_cache

from scrapling.core._types import Tuple
from scrapling.engines.constants import (
    DEFAULT_STEALTH_FLAGS,
    HARMFUL_DEFAULT_ARGS,
    DEFAULT_FLAGS,
)
from scrapling.engines.toolbelt.navigation import js_bypass_path
from scrapling.engines.toolbelt.fingerprints import generate_headers

__default_useragent__ = generate_headers(browser_mode=True).get("User-Agent")
__default_chrome_useragent__ = generate_headers(browser_mode="chrome").get("User-Agent")


@lru_cache(1)
def _compiled_stealth_scripts():
    """Pre-read and compile stealth scripts"""
    # Basic bypasses nothing fancy as I'm still working on it
    # But with adding these bypasses to the above config, it bypasses many online tests like
    # https://bot.sannysoft.com/
    # https://kaliiiiiiiiii.github.io/brotector/
    # https://pixelscan.net/
    # https://iphey.com/
    # https://www.browserscan.net/bot-detection <== this one also checks for the CDP runtime fingerprint
    # https://arh.antoinevastel.com/bots/areyouheadless/
    # https://prescience-data.github.io/execution-monitor.html
    stealth_scripts_paths = tuple(
        js_bypass_path(script)
        for script in (
            # Order is important
            "webdriver_fully.js",
            "window_chrome.js",
            "navigator_plugins.js",
            "notification_permission.js",
            "screen_props.js",
            "playwright_fingerprint.js",
        )
    )
    scripts = []
    for script_path in stealth_scripts_paths:
        with open(script_path, "r") as f:
            scripts.append(f.read())
    return tuple(scripts)


@lru_cache(2, typed=True)
def _set_flags(hide_canvas, disable_webgl):  # pragma: no cover
    """Returns the flags that will be used while launching the browser if stealth mode is enabled"""
    flags = DEFAULT_STEALTH_FLAGS
    if hide_canvas:
        flags += ("--fingerprinting-canvas-image-data-noise",)
    if disable_webgl:
        flags += (
            "--disable-webgl",
            "--disable-webgl-image-chromium",
            "--disable-webgl2",
        )

    return flags
