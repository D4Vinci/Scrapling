from threading import Lock

from scrapling.core._types import Callable, Dict, List, Tuple, ProxyType


RotationStrategy = Callable[[List[ProxyType], int], Tuple[ProxyType, int]]
_PROXY_ERROR_INDICATORS = {
    "net::err_proxy",
    "net::err_tunnel",
    "connection refused",
    "connection reset",
    "connection timed out",
    "failed to connect",
    "could not resolve proxy",
}


def _get_proxy_key(proxy: ProxyType) -> str:
    """Generate a unique key for a proxy (for dicts it's server plus username)."""
    if isinstance(proxy, str):
        return proxy
    server = proxy.get("server", "")
    username = proxy.get("username", "")
    return f"{server}|{username}"


def is_proxy_error(error: Exception) -> bool:
    """Check if an error is proxy-related. Works for both HTTP and browser errors."""
    error_msg = str(error).lower()
    return any(indicator in error_msg for indicator in _PROXY_ERROR_INDICATORS)


def round_robin(proxies: List[ProxyType], current_index: int) -> Tuple[ProxyType, int]:
    """Default round-robin rotation strategy."""
    idx = current_index % len(proxies)
    return proxies[idx], (idx + 1) % len(proxies)


class ProxyRotator:
    """
    A thread-safe proxy rotator with pluggable rotation strategies.

    Supports:
    - Round-robin rotation (default)
    - Custom rotation strategies via callable
    - Both string URLs and Playwright-style dict proxies
    """

    __slots__ = ("_proxies", "_proxy_to_index", "_strategy", "_current_index", "_lock")

    def __init__(
        self,
        proxies: List[ProxyType],
        strategy: RotationStrategy = round_robin,
    ):
        """
        Initialize the proxy rotator.

        :param proxies: List of proxy URLs or Playwright-style proxy dicts.
            - String format: "http://proxy1:8080" or "http://user:pass@proxy:8080"
            - Dict format: {"server": "http://proxy:8080", "username": "user", "password": "pass"}
        :param strategy: Rotation strategy function. Takes (proxies, current_index) and returns (proxy, next_index). Defaults to round_robin.
        """
        if not proxies:
            raise ValueError("At least one proxy must be provided")

        if not callable(strategy):
            raise TypeError(f"strategy must be callable, got {type(strategy).__name__}")

        self._strategy = strategy
        self._lock = Lock()

        # Validate and store proxies
        self._proxies: List[ProxyType] = []
        self._proxy_to_index: Dict[str, int] = {}  # O(1) lookup by unique key (server + username)
        for i, proxy in enumerate(proxies):
            if isinstance(proxy, (str, dict)):
                if isinstance(proxy, dict) and "server" not in proxy:
                    raise ValueError("Proxy dict must have a 'server' key")

                self._proxy_to_index[_get_proxy_key(proxy)] = i
                self._proxies.append(proxy)
            else:
                raise TypeError(f"Invalid proxy type: {type(proxy)}. Expected str or dict.")

        self._current_index = 0

    def get_proxy(self) -> ProxyType:
        """Get the next proxy according to the rotation strategy."""
        with self._lock:
            proxy, self._current_index = self._strategy(self._proxies, self._current_index)
            return proxy

    @property
    def proxies(self) -> List[ProxyType]:
        """Get a copy of all configured proxies."""
        return list(self._proxies)

    def __len__(self) -> int:
        """Return the total number of configured proxies."""
        return len(self._proxies)

    def __repr__(self) -> str:
        return f"ProxyRotator(proxies={len(self._proxies)})"
