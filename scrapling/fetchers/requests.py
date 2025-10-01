from scrapling.core._types import (
    Callable,
    Dict,
    List,
    Optional,
    SelectorWaitStates,
    Iterable,
)
from scrapling.engines.static import (
    FetcherSession,
    FetcherClient as _FetcherClient,
    AsyncFetcherClient as _AsyncFetcherClient,
)
from scrapling.engines.toolbelt.custom import BaseFetcher, Response


__FetcherClientInstance__ = _FetcherClient()
__AsyncFetcherClientInstance__ = _AsyncFetcherClient()


class Fetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on `curl_cffi`."""

    get = __FetcherClientInstance__.get
    post = __FetcherClientInstance__.post
    put = __FetcherClientInstance__.put
    delete = __FetcherClientInstance__.delete


class AsyncFetcher(BaseFetcher):
    """A basic `Fetcher` class type that can only do basic GET, POST, PUT, and DELETE HTTP requests based on `curl_cffi`."""

    get = __AsyncFetcherClientInstance__.get
    post = __AsyncFetcherClientInstance__.post
    put = __AsyncFetcherClientInstance__.put
    delete = __AsyncFetcherClientInstance__.delete
