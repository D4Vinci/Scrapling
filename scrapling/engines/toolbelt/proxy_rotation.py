from threading import Lock
from time import monotonic

from scrapling.core._types import Any, Callable, Dict, List, Tuple, ProxyType


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


def cyclic_rotation(proxies: List[ProxyType], current_index: int) -> Tuple[ProxyType, int]:
    """Default cyclic rotation strategy - iterates through proxies sequentially, wrapping around at the end."""
    idx = current_index % len(proxies)
    return proxies[idx], (idx + 1) % len(proxies)


class ProxyRotator:
    """Thread-safe proxy rotator with health tracking and cooldown."""

    __slots__ = (
        "_proxies",
        "_proxy_to_index",
        "_strategy",
        "_current_index",
        "_lock",
        "_fail_count",
        "_cooldown_until",
        "_cooldown_seconds",
        "_max_failures",
    )

    def __init__(
        self,
        proxies: List[ProxyType],
        strategy: RotationStrategy = cyclic_rotation,
        cooldown_seconds: float = 60.0,
        max_failures: int = 3,
    ):
        if not proxies:
            raise ValueError("At least one proxy must be provided")

        if not callable(strategy):
            raise TypeError(f"strategy must be callable, got {type(strategy).__name__}")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds must be non-negative")
        if max_failures < 1:
            raise ValueError("max_failures must be at least 1")

        self._strategy = strategy
        self._lock = Lock()
        self._cooldown_seconds = float(cooldown_seconds)
        self._max_failures = int(max_failures)
        self._fail_count: Dict[str, int] = {}
        self._cooldown_until: Dict[str, float] = {}

        self._proxies: List[ProxyType] = []
        self._proxy_to_index: Dict[str, int] = {}
        for i, proxy in enumerate(proxies):
            if isinstance(proxy, (str, dict)):
                if isinstance(proxy, dict) and "server" not in proxy:
                    raise ValueError("Proxy dict must have a 'server' key")

                self._proxy_to_index[_get_proxy_key(proxy)] = i
                self._proxies.append(proxy)
            else:
                raise TypeError(f"Invalid proxy type: {type(proxy)}. Expected str or dict.")

        self._current_index = 0

    def _available(self) -> List[ProxyType]:
        now = monotonic()
        available = [p for p in self._proxies if self._cooldown_until.get(_get_proxy_key(p), 0.0) <= now]
        return available or list(self._proxies)

    def get_proxy(self) -> ProxyType:
        """Get the next healthy proxy according to the rotation strategy."""
        with self._lock:
            candidates = self._available()
            proxy, self._current_index = self._strategy(candidates, self._current_index)
            return proxy

    def mark_failure(self, proxy: ProxyType | None) -> None:
        if proxy is None:
            return
        key = _get_proxy_key(proxy)
        with self._lock:
            failures = self._fail_count.get(key, 0) + 1
            self._fail_count[key] = failures
            if failures >= self._max_failures:
                self._cooldown_until[key] = monotonic() + (self._cooldown_seconds * failures)

    def mark_success(self, proxy: ProxyType | None) -> None:
        if proxy is None:
            return
        key = _get_proxy_key(proxy)
        with self._lock:
            self._fail_count.pop(key, None)
            self._cooldown_until.pop(key, None)

    def health_snapshot(self) -> Dict[str, Dict[str, Any]]:
        now = monotonic()
        with self._lock:
            return {
                key: {
                    "failures": self._fail_count.get(key, 0),
                    "cooldown_remaining": max(0.0, self._cooldown_until.get(key, 0.0) - now),
                }
                for key in self._proxy_to_index
            }

    @property
    def proxies(self) -> List[ProxyType]:
        return list(self._proxies)

    def __len__(self) -> int:
        return len(self._proxies)

    def __repr__(self) -> str:
        return f"ProxyRotator(proxies={len(self._proxies)})"
