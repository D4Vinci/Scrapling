// Mirrors scrapling/cli.py's `extract` option decorators, so the same
// catalog drives both the request builder here and the form the client
// renders (fetched via GET /api/options-schema instead of duplicated in JS).

export const FETCHER_TYPES = {
  get: { kind: "http", label: "GET" },
  post: { kind: "http", label: "POST", supportsBody: true },
  put: { kind: "http", label: "PUT", supportsBody: true },
  delete: { kind: "http", label: "DELETE" },
  fetch: { kind: "browser", label: "Fetch (browser)" },
  stealthy_fetch: { kind: "browser", label: "Stealthy fetch (anti-bot)" },
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
  { value: "html", label: "HTML", extension: "html" },
  { value: "md", label: "Markdown", extension: "md" },
  { value: "txt", label: "Text", extension: "txt" },
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
  { name: "ai_targeted", flag: "--ai-targeted", type: "boolean", default: false, label: "AI-targeted extraction" },
  {
    name: "stealthy_headers",
    flag: "--stealthy-headers",
    negFlag: "--no-stealthy-headers",
    type: "boolean",
    default: true,
    label: "Stealthy headers",
  },
  {
    name: "impersonate",
    flag: "--impersonate",
    type: "multiselect",
    choices: IMPERSONATE_CHOICES,
    label: "Impersonate browser(s)",
    hint: "Pick more than one to have each request randomly use one of them.",
  },
  { name: "verify", flag: "--verify", negFlag: "--no-verify", type: "boolean", default: true, label: "Verify SSL" },
  {
    name: "follow_redirects",
    flag: "--follow-redirects",
    negFlag: "--no-follow-redirects",
    type: "boolean",
    default: true,
    label: "Follow redirects",
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
  { name: "timeout", flag: "--timeout", type: "number", default: 30, label: "Timeout (seconds)" },
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
  { name: "ai_targeted", flag: "--ai-targeted", type: "boolean", default: false, label: "AI-targeted extraction" },
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
  { name: "wait", flag: "--wait", type: "number", default: 0, label: "Extra wait after load (ms)" },
  { name: "timeout", flag: "--timeout", type: "number", default: 30000, label: "Timeout (ms)" },
  {
    name: "network_idle",
    flag: "--network-idle",
    negFlag: "--no-network-idle",
    type: "boolean",
    default: false,
    label: "Wait for network idle",
  },
  {
    name: "disable_resources",
    flag: "--disable-resources",
    negFlag: "--enable-resources",
    type: "boolean",
    default: false,
    label: "Disable resources (speed boost)",
  },
  { name: "headless", flag: "--headless", negFlag: "--no-headless", type: "boolean", default: true, label: "Headless" },
  {
    name: "dns_over_https",
    flag: "--dns-over-https",
    negFlag: "--no-dns-over-https",
    type: "boolean",
    default: false,
    label: "DNS over HTTPS",
  },
  {
    name: "block_ads",
    flag: "--block-ads",
    negFlag: "--no-block-ads",
    type: "boolean",
    default: false,
    label: "Block ads/trackers",
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
  },
  {
    name: "solve_cloudflare",
    flag: "--solve-cloudflare",
    negFlag: "--no-solve-cloudflare",
    type: "boolean",
    default: false,
    label: "Solve Cloudflare challenges",
  },
  { name: "allow_webgl", flag: "--allow-webgl", negFlag: "--block-webgl", type: "boolean", default: true, label: "Allow WebGL" },
  {
    name: "hide_canvas",
    flag: "--hide-canvas",
    negFlag: "--show-canvas",
    type: "boolean",
    default: false,
    label: "Hide canvas (add noise)",
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
