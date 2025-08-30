# Disable loading these resources for speed
DEFAULT_DISABLED_RESOURCES = {
    "font",
    "image",
    "media",
    "beacon",
    "object",
    "imageset",
    "texttrack",
    "websocket",
    "csp_report",
    "stylesheet",
}

HARMFUL_DEFAULT_ARGS = (
    # This will be ignored to avoid detection more and possibly avoid the popup crashing bug abuse: https://issues.chromium.org/issues/340836884
    "--enable-automation",
    "--disable-popup-blocking",
    # '--disable-component-update',
    # '--disable-default-apps',
    # '--disable-extensions',
)

DEFAULT_FLAGS = (
    # Speed up chromium browsers by default
    "--no-pings",
    "--no-first-run",
    "--disable-infobars",
    "--disable-breakpad",
    "--no-service-autorun",
    "--homepage=about:blank",
    "--password-store=basic",
    "--no-default-browser-check",
    "--disable-session-crashed-bubble",
    "--disable-search-engine-choice-screen",
)

DEFAULT_STEALTH_FLAGS = (
    # Explanation: https://peter.sh/experiments/chromium-command-line-switches/
    # Generally this will make the browser faster and less detectable
    "--incognito",
    "--test-type",
    "--lang=en-US",
    "--mute-audio",
    "--disable-sync",
    "--hide-scrollbars",
    "--disable-logging",
    "--start-maximized",  # For headless check bypass
    "--enable-async-dns",
    "--accept-lang=en-US",
    "--use-mock-keychain",
    "--disable-translate",
    "--disable-extensions",
    "--disable-voice-input",
    "--window-position=0,0",
    "--disable-wake-on-wifi",
    "--ignore-gpu-blocklist",
    "--enable-tcp-fast-open",
    "--enable-web-bluetooth",
    "--disable-hang-monitor",
    "--disable-cloud-import",
    "--disable-default-apps",
    "--disable-print-preview",
    "--disable-dev-shm-usage",
    # '--disable-popup-blocking',
    "--metrics-recording-only",
    "--disable-crash-reporter",
    "--disable-partial-raster",
    "--disable-gesture-typing",
    "--disable-checker-imaging",
    "--disable-prompt-on-repost",
    "--force-color-profile=srgb",
    "--font-render-hinting=none",
    "--aggressive-cache-discard",
    "--disable-component-update",
    "--disable-cookie-encryption",
    "--disable-domain-reliability",
    "--disable-threaded-animation",
    "--disable-threaded-scrolling",
    # '--disable-reading-from-canvas', # For Firefox
    "--enable-simple-cache-backend",
    "--disable-background-networking",
    "--enable-surface-synchronization",
    "--disable-image-animation-resync",
    "--disable-renderer-backgrounding",
    "--disable-ipc-flooding-protection",
    "--prerender-from-omnibox=disabled",
    "--safebrowsing-disable-auto-update",
    "--disable-offer-upload-credit-cards",
    "--disable-features=site-per-process",
    "--disable-background-timer-throttling",
    "--disable-new-content-rendering-timeout",
    "--run-all-compositor-stages-before-draw",
    "--disable-client-side-phishing-detection",
    "--disable-backgrounding-occluded-windows",
    "--disable-layer-tree-host-memory-pressure",
    "--autoplay-policy=no-user-gesture-required",
    "--disable-offer-store-unmasked-wallet-cards",
    "--disable-blink-features=AutomationControlled",
    "--webrtc-ip-handling-policy=disable_non_proxied_udp",
    "--disable-component-extensions-with-background-pages",
    "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
    "--enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance",
    "--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4",
    "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,TranslateUI,BlinkGenPropertyTrees",
)

# Defaulting to the docker mode, token doesn't matter in it as it's passed for the container
NSTBROWSER_DEFAULT_QUERY = {
    "once": True,
    "headless": True,
    "autoClose": True,
    "fingerprint": {
        "flags": {"timezone": "BasedOnIp", "screen": "Custom"},
        "platform": "linux",  # support: windows, mac, linux
        "kernel": "chromium",  # only support: chromium
        "kernelMilestone": "128",
        "hardwareConcurrency": 8,
        "deviceMemory": 8,
    },
}
