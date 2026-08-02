from functools import lru_cache

from scrapling.engines.toolbelt.fingerprints import generate_headers


@lru_cache(2, typed=True)
def get_default_useragent(browser_mode: bool | str = True) -> str | None:
    """Generate and cache the default user agent for a browser session.

    :param browser_mode: The browser mode passed to the fingerprint generator.
    :return: The generated user agent, if available.
    """
    return generate_headers(browser_mode=browser_mode).get("User-Agent")
