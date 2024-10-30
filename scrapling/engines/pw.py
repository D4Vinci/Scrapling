import json
import logging
from scrapling._types import Union, Callable, Optional, List, Dict

from .tools import check_type_validity, generate_headers, js_bypass_path, construct_websocket_url, generate_convincing_referer

# Disable loading these resources for speed
DEFAULT_DISABLED_RESOURCES = ['beacon', 'csp_report', 'font', 'image', 'imageset', 'media', 'object', 'texttrack', 'stylesheet', 'websocket']
DEFAULT_STEALTH_FLAGS = [
    # Explanation: https://peter.sh/experiments/chromium-command-line-switches/
    # Generally this will make the browser faster and less detectable
    '--incognito', '--accept-lang=en-US', '--lang=en-US', '--no-pings', '--mute-audio', '--no-first-run', '--no-default-browser-check', '--disable-cloud-import',
    '--disable-gesture-typing', '--disable-offer-store-unmasked-wallet-cards', '--disable-offer-upload-credit-cards', '--disable-print-preview', '--disable-voice-input',
    '--disable-wake-on-wifi', '--disable-cookie-encryption', '--ignore-gpu-blocklist', '--enable-async-dns', '--enable-simple-cache-backend', '--enable-tcp-fast-open',
    '--prerender-from-omnibox=disabled', '--enable-web-bluetooth', '--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,TranslateUI,BlinkGenPropertyTrees',
    '--aggressive-cache-discard', '--disable-ipc-flooding-protection', '--disable-blink-features=AutomationControlled', '--test-type',
    '--enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance',
    '--disable-breakpad', '--disable-component-update', '--disable-domain-reliability', '--disable-sync', '--disable-client-side-phishing-detection',
    '--disable-hang-monitor', '--disable-popup-blocking', '--disable-prompt-on-repost', '--metrics-recording-only', '--safebrowsing-disable-auto-update', '--password-store=basic',
    '--autoplay-policy=no-user-gesture-required', '--use-mock-keychain', '--force-webrtc-ip-handling-policy=disable_non_proxied_udp',
    '--webrtc-ip-handling-policy=disable_non_proxied_udp', '--disable-session-crashed-bubble', '--disable-crash-reporter', '--disable-dev-shm-usage', '--force-color-profile=srgb',
    '--disable-translate', '--disable-background-networking', '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows', '--disable-infobars',
    '--hide-scrollbars', '--disable-renderer-backgrounding', '--font-render-hinting=none', '--disable-logging', '--enable-surface-synchronization',
    '--run-all-compositor-stages-before-draw', '--disable-threaded-animation', '--disable-threaded-scrolling', '--disable-checker-imaging',
    '--disable-new-content-rendering-timeout', '--disable-image-animation-resync', '--disable-partial-raster',
    '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4',
    '--disable-layer-tree-host-memory-pressure',
    '--window-position=0,0',
    '--disable-features=site-per-process',
    '--disable-default-apps',
    '--disable-component-extensions-with-background-pages',
    '--disable-extensions',
    # "--disable-reading-from-canvas",  # For Firefox
    '--start-maximized'  # For headless check bypass
]


def _do_nothing(page):
    # Anything
    return page


class PlaywrightEngine:
    def __init__(
            self, headless: Union[bool, str] = True,
            disable_resources: Optional[List] = None,
            useragent: Optional[str] = None,
            network_idle: Optional[bool] = False,
            timeout: Optional[float] = 30000,
            page_action: Callable = _do_nothing,
            wait_selector: Optional[str] = None,
            wait_selector_state: Optional[str] = 'attached',
            stealth: bool = False,
            hide_canvas: bool = True,
            disable_webgl: bool = False,
            cdp_url: Optional[str] = None,
            nstbrowser_mode: bool = False,
            nstbrowser_config: Optional[Dict] = None,
    ):
        self.headless = headless
        self.disable_resources = disable_resources
        self.network_idle = bool(network_idle)
        self.stealth = bool(stealth)
        self.hide_canvas = bool(hide_canvas)
        self.disable_webgl = bool(disable_webgl)
        self.cdp_url = cdp_url
        self.useragent = useragent
        self.timeout = check_type_validity(timeout, [int, float], 30000)
        if callable(page_action):
            self.page_action = page_action
        else:
            self.page_action = _do_nothing
            logging.error('[Ignored] Argument "page_action" must be callable')

        self.wait_selector = wait_selector
        self.wait_selector_state = wait_selector_state
        self.nstbrowser_mode = bool(nstbrowser_mode)
        self.nstbrowser_config = nstbrowser_config

    def _cdp_url_logic(self, flags: Optional[dict] = None):
        cdp_url = self.cdp_url
        if self.nstbrowser_mode:
            if self.nstbrowser_config and type(self.nstbrowser_config) is Dict:
                config = self.nstbrowser_config
            else:
                # Defaulting to the docker mode, token doesn't matter in it as it's passed for the container
                query = {
                    "once": True,
                    "headless": True,
                    "autoClose": True,
                    "fingerprint": {
                        "flags": {
                            "timezone": "BasedOnIp",
                            "screen": "Custom"
                        },
                        "platform": 'linux',  # support: windows, mac, linux
                        "kernel": 'chromium',  # only support: chromium
                        "kernelMilestone": '128',
                        "hardwareConcurrency": 8,
                        "deviceMemory": 8,
                    },
                }
                if flags:
                    query.update({
                        "args": dict(zip(flags, [''] * len(flags))),  # browser args should be a dictionary
                    })

                config = {
                    'config': json.dumps(query),
                    # 'token': ''
                }
            cdp_url = construct_websocket_url(cdp_url, config)

        return cdp_url

    def fetch(self, url):
        if not self.stealth:
            from playwright.sync_api import sync_playwright
        else:
            from rebrowser_playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # Handle the UserAgent early
            if self.useragent:
                extra_headers = {}
                useragent = self.useragent
            else:
                extra_headers = generate_headers(browser_mode=True)
                useragent = extra_headers.get('User-Agent')

            # Prepare the flags before diving
            flags = DEFAULT_STEALTH_FLAGS
            if self.hide_canvas:
                flags += ['--fingerprinting-canvas-image-data-noise']
            if self.disable_webgl:
                flags += ['--disable-webgl', '--disable-webgl-image-chromium', '--disable-webgl2']

            # Creating the browser
            if self.cdp_url:
                cdp_url = self._cdp_url_logic(flags if self.stealth else None)
                browser = p.chromium.connect_over_cdp(endpoint_url=cdp_url)
            else:
                if self.stealth:
                    browser = p.chromium.launch(headless=self.headless, args=flags, ignore_default_args=['--enable-automation'], chromium_sandbox=True)
                else:
                    browser = p.chromium.launch(headless=self.headless, ignore_default_args=['--enable-automation'])

            # Creating the context
            if self.stealth:
                context = browser.new_context(
                    locale='en-US',
                    is_mobile=False,
                    has_touch=False,
                    color_scheme='dark',  # Bypasses the 'prefersLightColor' check in creepjs
                    user_agent=useragent,
                    device_scale_factor=2,
                    # I'm thinking about disabling it to rest from all Service Workers headache but let's keep it as it is for now
                    service_workers="allow",
                    ignore_https_errors=True,
                    extra_http_headers=extra_headers,
                    screen={"width": 1920, "height": 1080},
                    viewport={"width": 1920, "height": 1080},
                    permissions=["geolocation", 'notifications'],
                )
            else:
                context = browser.new_context(
                    color_scheme='dark',
                    user_agent=useragent,
                    device_scale_factor=2,
                    extra_http_headers=extra_headers
                )

            # Finally we are in business
            page = context.new_page()
            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)
            if self.stealth:
                # Basic bypasses nothing fancy as I'm still working on it
                # But with adding these bypasses to the above config, it bypasses many online tests like
                # https://bot.sannysoft.com/
                # https://kaliiiiiiiiii.github.io/brotector/
                # https://pixelscan.net/
                # https://iphey.com/
                # https://www.browserscan.net/bot-detection <== this one also checks for the CDP runtime fingerprint
                # https://arh.antoinevastel.com/bots/areyouheadless/
                # https://prescience-data.github.io/execution-monitor.html
                page.add_init_script(path=js_bypass_path('webdriver_fully.js'))
                page.add_init_script(path=js_bypass_path('window_chrome.js'))
                page.add_init_script(path=js_bypass_path('navigator_plugins.js'))
                page.add_init_script(path=js_bypass_path('pdf_viewer.js'))
                page.add_init_script(path=js_bypass_path('notification_permission.js'))
                page.add_init_script(path=js_bypass_path('screen_props.js'))
                page.add_init_script(path=js_bypass_path('playwright_fingerprint.js'))

            page.goto(url, referer=generate_convincing_referer(url) if self.stealth else None)
            page.wait_for_load_state(state="load")
            page.wait_for_load_state(state="domcontentloaded")
            if self.network_idle:
                page.wait_for_load_state('networkidle')

            page = self.page_action(page)

            if self.wait_selector and type(self.wait_selector) is str:
                waiter = page.locator(self.wait_selector)
                waiter.wait_for(state=self.wait_selector_state)

            html = page.content()
            page.close()
        return html
