from functools import lru_cache

from scrapling.core._types import Tuple
from scrapling.engines.constants import (
    DEFAULT_STEALTH_FLAGS,
    HARMFUL_DEFAULT_ARGS,
    DEFAULT_FLAGS,
)
from scrapling.engines.toolbelt import js_bypass_path, generate_headers

__default_useragent__ = generate_headers(browser_mode=True).get("User-Agent")


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


@lru_cache(2, typed=True)
def _launch_kwargs(
    headless,
    proxy,
    locale,
    extra_headers,
    useragent,
    real_chrome,
    stealth,
    hide_canvas,
    disable_webgl,
) -> Tuple:
    """Creates the arguments we will use while launching playwright's browser"""
    launch_kwargs = {
        "locale": locale,
        "headless": headless,
        "args": DEFAULT_FLAGS,
        "color_scheme": "dark",  # Bypasses the 'prefersLightColor' check in creepjs
        "proxy": proxy or tuple(),
        "device_scale_factor": 2,
        "ignore_default_args": HARMFUL_DEFAULT_ARGS,
        "channel": "chrome" if real_chrome else "chromium",
        "extra_http_headers": extra_headers or tuple(),
        "user_agent": useragent or __default_useragent__,
    }
    if stealth:
        launch_kwargs.update(
            {
                "args": DEFAULT_FLAGS + _set_flags(hide_canvas, disable_webgl),
                "chromium_sandbox": True,
                "is_mobile": False,
                "has_touch": False,
                # I'm thinking about disabling it to rest from all Service Workers' headache, but let's keep it as it is for now
                "service_workers": "allow",
                "ignore_https_errors": True,
                "screen": {"width": 1920, "height": 1080},
                "viewport": {"width": 1920, "height": 1080},
                "permissions": ["geolocation", "notifications"],
            }
        )

    return tuple(launch_kwargs.items())


@lru_cache(2, typed=True)
def _context_kwargs(proxy, locale, extra_headers, useragent, stealth) -> Tuple:
    """Creates the arguments for the browser context"""
    context_kwargs = {
        "proxy": proxy or tuple(),
        "locale": locale,
        "color_scheme": "dark",  # Bypasses the 'prefersLightColor' check in creepjs
        "device_scale_factor": 2,
        "extra_http_headers": extra_headers or tuple(),
        "user_agent": useragent or __default_useragent__,
    }
    if stealth:
        context_kwargs.update(
            {
                "is_mobile": False,
                "has_touch": False,
                # I'm thinking about disabling it to rest from all Service Workers' headache, but let's keep it as it is for now
                "service_workers": "allow",
                "ignore_https_errors": True,
                "screen": {"width": 1920, "height": 1080},
                "viewport": {"width": 1920, "height": 1080},
                "permissions": ["geolocation", "notifications"],
            }
        )

    return tuple(context_kwargs.items())
