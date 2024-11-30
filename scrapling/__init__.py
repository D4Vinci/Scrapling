# Declare top-level shortcuts
from scrapling.core.custom_types import AttributesHandler, TextHandler
from scrapling.fetchers import (CustomFetcher, Fetcher, PlayWrightFetcher,
                                StealthyFetcher)
from scrapling.parser import Adaptor, Adaptors

__author__ = "Karim Shoair (karim.shoair@pm.me)"
__version__ = "0.2.8"
__copyright__ = "Copyright (c) 2024 Karim Shoair"


__all__ = ['Adaptor', 'Fetcher', 'StealthyFetcher', 'PlayWrightFetcher']
