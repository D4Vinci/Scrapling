from .fetchers import AsyncFetcher, Fetcher, PlayWrightFetcher, StealthyFetcher

# If you are going to use Fetchers with the default settings, import them from this file instead for a cleaner looking code
Fetcher = Fetcher()
AsyncFetcher = AsyncFetcher()
StealthyFetcher = StealthyFetcher()
PlayWrightFetcher = PlayWrightFetcher()
