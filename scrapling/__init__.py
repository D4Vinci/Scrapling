# Declare top-level shortcuts
from scrapling.fetchers import Fetcher, StealthyFetcher, PlayWrightFetcher, CustomFetcher
from scrapling.parser import Adaptor, Adaptors
from scrapling.core.custom_types import TextHandler, AttributesHandler

__author__ = "Karim Shoair (karim.shoair@pm.me)"
__version__ = "0.2.7"
__copyright__ = "Copyright (c) 2024 Karim Shoair"


__all__ = ['Adaptor', 'Fetcher', 'StealthyFetcher', 'PlayWrightFetcher']
