from .fetchers import AsyncFetcher as _AsyncFetcher
from .fetchers import Fetcher as _Fetcher
from .fetchers import PlayWrightFetcher as _PlayWrightFetcher
from .fetchers import StealthyFetcher as _StealthyFetcher

# If you are going to use Fetchers with the default settings, import them from this file instead for a cleaner looking code
Fetcher = _Fetcher()
AsyncFetcher = _AsyncFetcher()
StealthyFetcher = _StealthyFetcher()
PlayWrightFetcher = _PlayWrightFetcher()
