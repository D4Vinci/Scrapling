__author__ = "Karim Shoair (karim.shoair@pm.me)"
__version__ = "0.3.1"
__copyright__ = "Copyright (c) 2024 Karim Shoair"


# A lightweight approach to create a lazy loader for each import for backward compatibility
# This will reduces initial memory footprint significantly (only loads what's used)
def __getattr__(name):
    lazy_imports = {
        "Fetcher": ("scrapling.fetchers", "Fetcher"),
        "Selector": ("scrapling.parser", "Selector"),
        "Selectors": ("scrapling.parser", "Selectors"),
        "AttributesHandler": ("scrapling.core.custom_types", "AttributesHandler"),
        "TextHandler": ("scrapling.core.custom_types", "TextHandler"),
        "AsyncFetcher": ("scrapling.fetchers", "AsyncFetcher"),
        "StealthyFetcher": ("scrapling.fetchers", "StealthyFetcher"),
        "DynamicFetcher": ("scrapling.fetchers", "DynamicFetcher"),
    }

    if name in lazy_imports:
        module_path, class_name = lazy_imports[name]
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    else:
        raise AttributeError(f"module 'scrapling' has no attribute '{name}'")


__all__ = ["Selector", "Fetcher", "AsyncFetcher", "StealthyFetcher", "DynamicFetcher"]
