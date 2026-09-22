// Mirrors scrapling/cli.py's `extract` option decorators, so the same
// catalog drives both the request builder here and the form the client
// renders (fetched via GET /api/options-schema instead of duplicated in JS).

export const FETCHER_TYPES = {
  get: {
    kind: "http",
    label: "GET",
    hint: "Plain HTTP GET request. Fastest option — no browser, no JavaScript rendering. Good for static pages and APIs.",
  },
  post: {
    kind: "http",
    label: "POST",
    supportsBody: true,
    hint: "Plain HTTP POST request with an optional JSON or form body. Use this to submit a form or hit an API endpoint.",
  },
  put: {
    kind: "http",
    label: "PUT",
    supportsBody: true,
    hint: "Plain HTTP PUT request with an optional JSON or form body.",
  },
  delete: {
    kind: "http",
    label: "DELETE",
    hint: "Plain HTTP DELETE request. No body support.",
  },
  fetch: {
    kind: "browser",
    label: "Fetch (browser)",
    hint: "Loads the page in a real headless browser (Playwright/Patchright), so JavaScript-rendered content works. Slower than GET, especially on a Pi.",
  },
  stealthy_fetch: {
    kind: "browser",
    label: "Stealthy fetch (anti-bot)",
    hint: "Same as Fetch, but with anti-bot evasion (Cloudflare Turnstile bypass, fingerprint spoofing). Slowest option — use it when GET/Fetch get blocked.",
  },
};

// Internal fetcher-type keys use underscores; the actual `scrapling extract`
// subcommand names use dashes (Click derives `stealthy-fetch` from the
// function name `stealthy_fetch`).
export const CLI_COMMAND_NAME = {
  get: "get",
  post: "post",
  put: "put",
  delete: "delete",
  fetch: "fetch",
  stealthy_fetch: "stealthy-fetch",
};

export const OUTPUT_FORMATS = [
  {
    value: "html",
    label: "HTML",
    extension: "html",
    hint: "Saves the page's raw HTML to a single .html file, unmodified aside from the CSS selector scope.",
  },
  {
    value: "md",
    label: "Markdown",
    extension: "md",
    hint: "Converts the HTML to Markdown and saves it to a single .md file. Good for feeding into an LLM or reading as plain text with structure.",
  },
  {
    value: "txt",
    label: "Text",
    extension: "txt",
    hint: "Strips all HTML tags and saves just the visible text to a single .txt file.",
  },
  {
    value: "images",
    label: "Images",
    kind: "images",
    hint: "Instead of one file, downloads every image found on the page (or inside the CSS selector, if set) into its own folder. Includes lazy-loaded images (data-src/srcset) and resolves relative URLs automatically.",
  },
];

// curl_cffi's fixed set of impersonable browser families (see docs/fetching/static.md);
// exact per-version strings like "chrome110" change with each curl_cffi release, so
// the picker offers the stable family names and lets --impersonate pick the latest.
export const IMPERSONATE_CHOICES = [
  "chrome",
  "chrome_android",
  "edge",
  "safari",
  "safari_ios",
  "firefox",
  "tor",
];

const COMMON_HTTP_OPTIONS = [
  {
    name: "ai_targeted",
    flag: "--ai-targeted",
    type: "boolean",
    default: false,
    label: "AI-targeted extraction",
    hint: "On: keeps only the page's main content (article/body text), stripping nav, ads, and boilerplate — closer to what an LLM would want. Off: saves the full page as-is.",
  },
  {
    name: "stealthy_headers",
    flag: "--stealthy-headers",
    negFlag: "--no-stealthy-headers",
    type: "boolean",
    default: true,
    label: "Stealthy headers",
    hint: "On (default): sends a realistic, randomized browser-like header set instead of a generic HTTP client signature, making the request look less like a bot.",
  },
  {
    name: "impersonate",
    flag: "--impersonate",
    type: "multiselect",
    choices: IMPERSONATE_CHOICES,
    label: "Impersonate browser(s)",
    hint: "Makes the TLS/HTTP fingerprint match a real browser instead of a generic HTTP client. Pick one for a fixed fingerprint, or several to have each request randomly use one of them. Leave empty to use the library default.",
  },
  {
    name: "verify",
    flag: "--verify",
    negFlag: "--no-verify",
    type: "boolean",
    default: true,
    label: "Verify SSL",
    hint: "On (default): rejects invalid/self-signed TLS certificates, like a normal browser would. Turn off only for trusted internal/dev sites with broken certs.",
  },
  {
    name: "follow_redirects",
    flag: "--follow-redirects",
    negFlag: "--no-follow-redirects",
    type: "boolean",
    default: true,
    label: "Follow redirects",
    hint: "On (default): automatically follows HTTP 3xx redirects to the final URL. Off: saves whatever the first response is, redirect or not.",
  },
  {
    name: "params",
    flag: "--params",
    type: "list",
    label: "Query params",
    placeholder: "q=web scraping",
    hint: "One key=value per line. Appended to the URL's query string.",
  },
  {
    name: "css_selector",
    flag: "--css-selector",
    type: "string",
    label: "CSS selector",
    placeholder: ".product-title, article p",
    hint: "Only content matching this selector is saved; leave blank to save the whole page.",
  },
  {
    name: "proxy",
    flag: "--proxy",
    type: "string",
    label: "Proxy URL",
    placeholder: "http://username:password@host:port",
    hint: "Routes this request through an HTTP(S) proxy.",
  },
  {
    name: "timeout",
    flag: "--timeout",
    type: "number",
    default: 30,
    label: "Timeout (seconds)",
    hint: "How long to wait for a response before giving up and marking the job as failed.",
  },
  {
    name: "cookies",
    flag: "--cookies",
    type: "string",
    label: "Cookies",
    placeholder: "session=abc123; user=john",
    hint: "Semicolon-separated name=value pairs, exactly like a browser's Cookie header.",
  },
  {
    name: "headers",
    flag: "--headers",
    type: "list",
    label: "Headers",
    placeholder: "User-Agent: MyBot/1.0",
    hint: 'One "Key: Value" per line.',
  },
];

const DATA_OPTIONS = [
  {
    name: "json",
    flag: "--json",
    type: "string",
    label: "JSON body",
    placeholder: '{"username": "test", "action": "search"}',
    hint: "Raw JSON, sent as the request body with a JSON content type.",
  },
  {
    name: "data",
    flag: "--data",
    type: "string",
    label: "Form data",
    placeholder: "key1=value1&key2=value2",
    hint: "URL-encoded form body (like a plain HTML form submit). Ignored if JSON body is set.",
  },
];

const COMMON_BROWSER_OPTIONS = [
  {
    name: "ai_targeted",
    flag: "--ai-targeted",
    type: "boolean",
    default: false,
    label: "AI-targeted extraction",
    hint: "On: keeps only the page's main content (article/body text), stripping nav, ads, and boilerplate. Off: saves the full page as-is.",
  },
  {
    name: "executable_path",
    flag: "--executable-path",
    type: "string",
    label: "Custom browser executable path",
    placeholder: "/usr/bin/chromium",
    hint: "Only needed to use a specific Chromium-compatible browser instead of the bundled one.",
  },
  {
    name: "extra_headers",
    flag: "--extra-headers",
    type: "list",
    label: "Extra headers",
    placeholder: "Accept-Language: en-US",
    hint: 'One "Key: Value" per line.',
  },
  {
    name: "proxy",
    flag: "--proxy",
    type: "string",
    label: "Proxy URL",
    placeholder: "http://username:password@host:port",
    hint: "Routes browser traffic through an HTTP(S) proxy.",
  },
  {
    name: "real_chrome",
    flag: "--real-chrome",
    negFlag: "--no-real-chrome",
    type: "boolean",
    default: false,
    label: "Use real installed Chrome",
    hint: "On: launches your system's installed Google Chrome instead of the bundled Chromium. Requires Chrome to actually be installed on the Pi.",
  },
  {
    name: "locale",
    flag: "--locale",
    type: "string",
    label: "Locale",
    placeholder: "en-US",
    hint: "BCP-47 language tag, e.g. en-US or de-DE. Leave blank to use the system default.",
  },
  {
    name: "wait_selector",
    flag: "--wait-selector",
    type: "string",
    label: "Wait for CSS selector",
    placeholder: ".content-loaded",
    hint: "Pauses until an element matching this selector appears, useful for content that loads after the initial page load.",
  },
  {
    name: "css_selector",
    flag: "--css-selector",
    type: "string",
    label: "CSS selector",
    placeholder: ".product-title, article p",
    hint: "Only content matching this selector is saved; leave blank to save the whole page.",
  },
  {
    name: "wait",
    flag: "--wait",
    type: "number",
    default: 0,
    label: "Extra wait after load (ms)",
    hint: "Fixed pause after the page loads, before saving — useful for content that fades/animates in a bit after load.",
  },
  {
    name: "timeout",
    flag: "--timeout",
    type: "number",
    default: 30000,
    label: "Timeout (ms)",
    hint: "How long to wait for the page to load before giving up and marking the job as failed.",
  },
  {
    name: "network_idle",
    flag: "--network-idle",
    negFlag: "--no-network-idle",
    type: "boolean",
    default: false,
    label: "Wait for network idle",
    hint: "On: waits until network requests quiet down before saving, useful for pages that keep loading data (infinite scroll, lazy images) after the initial render.",
  },
  {
    name: "disable_resources",
    flag: "--disable-resources",
    negFlag: "--enable-resources",
    type: "boolean",
    default: false,
    label: "Disable resources (speed boost)",
    hint: "On: skips loading images/fonts/stylesheets for a faster page load. Turn off if you're using the Images output format, since it needs images to actually load.",
  },
  {
    name: "headless",
    flag: "--headless",
    negFlag: "--no-headless",
    type: "boolean",
    default: true,
    label: "Headless",
    hint: "On (default): runs the browser with no visible window (required on a headless Pi). Off opens a real window — only useful if the Pi has a display attached.",
  },
  {
    name: "dns_over_https",
    flag: "--dns-over-https",
    negFlag: "--no-dns-over-https",
    type: "boolean",
    default: false,
    label: "DNS over HTTPS",
    hint: "On: resolves domains via encrypted DNS-over-HTTPS instead of the system resolver, hiding DNS lookups from the local network.",
  },
  {
    name: "block_ads",
    flag: "--block-ads",
    negFlag: "--no-block-ads",
    type: "boolean",
    default: false,
    label: "Block ads/trackers",
    hint: "On: blocks known ad/tracker domains while the page loads, which also speeds things up.",
  },
];

const STEALTH_ONLY_OPTIONS = [
  {
    name: "block_webrtc",
    flag: "--block-webrtc",
    negFlag: "--allow-webrtc",
    type: "boolean",
    default: false,
    label: "Block WebRTC",
    hint: "On: disables WebRTC, which sites can otherwise use to leak your real IP address even behind a proxy.",
  },
  {
    name: "solve_cloudflare",
    flag: "--solve-cloudflare",
    negFlag: "--no-solve-cloudflare",
    type: "boolean",
    default: false,
    label: "Solve Cloudflare challenges",
    hint: "On: automatically attempts to solve Cloudflare Turnstile/JS challenges before saving the page. Adds time but is often required for protected sites.",
  },
  {
    name: "allow_webgl",
    flag: "--allow-webgl",
    negFlag: "--block-webgl",
    type: "boolean",
    default: true,
    label: "Allow WebGL",
    hint: "On (default): leaves WebGL enabled, which is what a real browser does — disabling it can itself look suspicious to anti-bot systems.",
  },
  {
    name: "hide_canvas",
    flag: "--hide-canvas",
    negFlag: "--show-canvas",
    type: "boolean",
    default: false,
    label: "Hide canvas (add noise)",
    hint: "On: adds subtle noise to canvas rendering to defeat canvas-fingerprinting anti-bot checks.",
  },
];

export const ALL_OPTIONS = {
  get: COMMON_HTTP_OPTIONS,
  delete: COMMON_HTTP_OPTIONS,
  post: [...DATA_OPTIONS, ...COMMON_HTTP_OPTIONS],
  put: [...DATA_OPTIONS, ...COMMON_HTTP_OPTIONS],
  fetch: COMMON_BROWSER_OPTIONS,
  stealthy_fetch: [...COMMON_BROWSER_OPTIONS, ...STEALTH_ONLY_OPTIONS],
};
