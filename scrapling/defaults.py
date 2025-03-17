# If you are going to use Fetchers with the default settings, import them from this file instead for a cleaner looking code

# A lightweight approach to create lazy loader for each import for backward compatibility
# This will reduces initial memory footprint significantly (only loads what's used)
def __getattr__(name):
    if name == 'Fetcher':
        from scrapling.fetchers import Fetcher as cls
        return cls()
    elif name == 'AsyncFetcher':
        from scrapling.fetchers import AsyncFetcher as cls
        return cls()
    elif name == 'StealthyFetcher':
        from scrapling.fetchers import StealthyFetcher as cls
        return cls()
    elif name == 'PlayWrightFetcher':
        from scrapling.fetchers import PlayWrightFetcher as cls
        return cls()
    else:
        raise AttributeError(f"module 'scrapling' has no attribute '{name}'")
