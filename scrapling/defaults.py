# Left this file for backward-compatibility before 0.2.99
from scrapling.core.utils import log


# A lightweight approach to create lazy loader for each import for backward compatibility
# This will reduces initial memory footprint significantly (only loads what's used)
def __getattr__(name):
    if name == 'Fetcher':
        from scrapling.fetchers import Fetcher as cls
        log.warning('This import is deprecated now and it will be removed with v0.3. Use `from scrapling.fetchers import Fetcher` instead')
        return cls
    elif name == 'AsyncFetcher':
        from scrapling.fetchers import AsyncFetcher as cls
        log.warning('This import is deprecated now and it will be removed with v0.3. Use `from scrapling.fetchers import AsyncFetcher` instead')
        return cls
    elif name == 'StealthyFetcher':
        from scrapling.fetchers import StealthyFetcher as cls
        log.warning('This import is deprecated now and it will be removed with v0.3. Use `from scrapling.fetchers import StealthyFetcher` instead')
        return cls
    elif name == 'PlayWrightFetcher':
        from scrapling.fetchers import PlayWrightFetcher as cls
        log.warning('This import is deprecated now and it will be removed with v0.3. Use `from scrapling.fetchers import PlayWrightFetcher` instead')
        return cls
    else:
        raise AttributeError(f"module 'scrapling' has no attribute '{name}'")
