from scrapling.engines.toolbelt.fingerprints import generate_headers

__default_useragent__ = generate_headers(browser_mode=True).get("User-Agent")
__default_chrome_useragent__ = generate_headers(browser_mode="chrome").get("User-Agent")
