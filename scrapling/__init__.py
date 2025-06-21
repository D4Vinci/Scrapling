__author__ = "Karim Shoair (karim.shoair@pm.me)"
__version__ = "0.3-beta"
__copyright__ = "Copyright (c) 2024 Karim Shoair"


# A lightweight approach to create lazy loader for each import for backward compatibility
# This will reduces initial memory footprint significantly (only loads what's used)
def __getattr__(name):
    if name == "Fetcher":
        from scrapling.fetchers import Fetcher as cls

        return cls
    elif name == "Adaptor":
        from scrapling.parser import Adaptor as cls

        return cls
    elif name == "Adaptors":
        from scrapling.parser import Adaptors as cls

        return cls
    elif name == "AttributesHandler":
        from scrapling.core.custom_types import AttributesHandler as cls

        return cls
    elif name == "TextHandler":
        from scrapling.core.custom_types import TextHandler as cls

        return cls
    elif name == "AsyncFetcher":
        from scrapling.fetchers import AsyncFetcher as cls

        return cls
    elif name == "StealthyFetcher":
        from scrapling.fetchers import StealthyFetcher as cls

        return cls
    elif name == "DynamicFetcher":
        from scrapling.fetchers import DynamicFetcher as cls

        return cls
    elif name == "CustomFetcher":
        from scrapling.fetchers import CustomFetcher as cls

        return cls
    else:
        raise AttributeError(f"module 'scrapling' has no attribute '{name}'")


__all__ = ["Adaptor", "Fetcher", "AsyncFetcher", "StealthyFetcher", "DynamicFetcher"]
