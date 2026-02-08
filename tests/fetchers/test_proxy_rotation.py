import pytest
import random
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from scrapling.engines.toolbelt import ProxyRotator, is_proxy_error, round_robin


class TestRoundRobinStrategy:
    """Test the default round_robin strategy function"""

    def test_round_robin_cycles_through_proxies(self):
        """Test that round_robin returns proxies in order"""
        proxies = ["http://p1:8080", "http://p2:8080", "http://p3:8080"]

        proxy, next_idx = round_robin(proxies, 0)
        assert proxy == "http://p1:8080"
        assert next_idx == 1

        proxy, next_idx = round_robin(proxies, 1)
        assert proxy == "http://p2:8080"
        assert next_idx == 2

        proxy, next_idx = round_robin(proxies, 2)
        assert proxy == "http://p3:8080"
        assert next_idx == 0  # Wraps around

    def test_round_robin_wraps_index(self):
        """Test that round_robin handles index overflow"""
        proxies = ["http://p1:8080", "http://p2:8080"]

        # Index larger than list length should wrap
        proxy, next_idx = round_robin(proxies, 5)
        assert proxy == "http://p2:8080"  # 5 % 2 = 1
        assert next_idx == 0


class TestProxyRotatorCreation:
    """Test ProxyRotator initialization and validation"""

    def test_create_with_string_proxies(self):
        """Test creating rotator with string proxy URLs"""
        proxies = ["http://p1:8080", "http://p2:8080"]
        rotator = ProxyRotator(proxies)

        assert len(rotator) == 2
        assert rotator.proxies == proxies

    def test_create_with_dict_proxies(self):
        """Test creating rotator with dict proxies"""
        proxies = [
            {"server": "http://p1:8080", "username": "user1", "password": "pass1"},
            {"server": "http://p2:8080"},
        ]
        rotator = ProxyRotator(proxies)

        assert len(rotator) == 2
        assert rotator.proxies == proxies

    def test_create_with_mixed_proxies(self):
        """Test creating rotator with mixed string and dict proxies"""
        proxies = [
            "http://p1:8080",
            {"server": "http://p2:8080", "username": "user"},
        ]
        rotator = ProxyRotator(proxies)

        assert len(rotator) == 2

    def test_empty_proxies_raises_error(self):
        """Test that empty proxy list raises ValueError"""
        with pytest.raises(ValueError, match="At least one proxy must be provided"):
            ProxyRotator([])

    def test_dict_without_server_raises_error(self):
        """Test that dict proxy without 'server' key raises ValueError"""
        with pytest.raises(ValueError, match="Proxy dict must have a 'server' key"):
            ProxyRotator([{"username": "user", "password": "pass"}])

    def test_invalid_proxy_type_raises_error(self):
        """Test that invalid proxy type raises TypeError"""
        with pytest.raises(TypeError, match="Invalid proxy type"):
            ProxyRotator([123])

        with pytest.raises(TypeError, match="Invalid proxy type"):
            ProxyRotator([None])

    def test_non_callable_strategy_raises_error(self):
        """Test that non-callable strategy raises TypeError"""
        with pytest.raises(TypeError, match="strategy must be callable"):
            ProxyRotator(["http://p1:8080"], strategy="round_robin")

        with pytest.raises(TypeError, match="strategy must be callable"):
            ProxyRotator(["http://p1:8080"], strategy=123)


class TestProxyRotatorRotation:
    """Test ProxyRotator rotation behavior"""

    def test_get_proxy_round_robin(self):
        """Test that get_proxy cycles through proxies in order"""
        proxies = ["http://p1:8080", "http://p2:8080", "http://p3:8080"]
        rotator = ProxyRotator(proxies)

        # First cycle
        assert rotator.get_proxy() == "http://p1:8080"
        assert rotator.get_proxy() == "http://p2:8080"
        assert rotator.get_proxy() == "http://p3:8080"

        # Second cycle - wraps around
        assert rotator.get_proxy() == "http://p1:8080"
        assert rotator.get_proxy() == "http://p2:8080"
        assert rotator.get_proxy() == "http://p3:8080"

    def test_get_proxy_single_proxy(self):
        """Test rotation with single proxy always returns the same proxy"""
        rotator = ProxyRotator(["http://only:8080"])

        for _ in range(5):
            assert rotator.get_proxy() == "http://only:8080"

    def test_get_proxy_with_dict_proxies(self):
        """Test rotation with dict proxies"""
        proxies = [
            {"server": "http://p1:8080"},
            {"server": "http://p2:8080"},
        ]
        rotator = ProxyRotator(proxies)

        assert rotator.get_proxy() == {"server": "http://p1:8080"}
        assert rotator.get_proxy() == {"server": "http://p2:8080"}
        assert rotator.get_proxy() == {"server": "http://p1:8080"}


class TestCustomStrategies:
    """Test ProxyRotator with custom rotation strategies"""

    def test_random_strategy(self):
        """Test custom random selection strategy"""
        def random_strategy(proxies, idx):
            return random.choice(proxies), idx

        proxies = ["http://p1:8080", "http://p2:8080", "http://p3:8080"]
        rotator = ProxyRotator(proxies, strategy=random_strategy)

        # Get multiple proxies - they should all be valid
        results = [rotator.get_proxy() for _ in range(10)]
        assert all(p in proxies for p in results)

    def test_sticky_strategy(self):
        """Test custom sticky strategy that always returns first proxy"""
        def sticky_strategy(proxies, idx):
            return proxies[0], idx

        rotator = ProxyRotator(
            ["http://p1:8080", "http://p2:8080"],
            strategy=sticky_strategy
        )

        for _ in range(5):
            assert rotator.get_proxy() == "http://p1:8080"

    def test_weighted_strategy(self):
        """Test custom weighted strategy"""
        call_count = {"count": 0}

        def alternating_strategy(proxies, idx):
            # Returns first proxy twice, then second proxy once
            call_count["count"] += 1
            if call_count["count"] % 3 == 0:
                return proxies[1], idx
            return proxies[0], idx

        rotator = ProxyRotator(
            ["http://primary:8080", "http://backup:8080"],
            strategy=alternating_strategy
        )

        assert rotator.get_proxy() == "http://primary:8080"
        assert rotator.get_proxy() == "http://primary:8080"
        assert rotator.get_proxy() == "http://backup:8080"

    def test_lambda_strategy(self):
        """Test using lambda as strategy"""
        rotator = ProxyRotator(
            ["http://p1:8080", "http://p2:8080"],
            strategy=lambda proxies, idx: (proxies[-1], idx)  # Always last
        )

        assert rotator.get_proxy() == "http://p2:8080"
        assert rotator.get_proxy() == "http://p2:8080"


class TestProxyRotatorProperties:
    """Test ProxyRotator properties and methods"""

    def test_proxies_property_returns_copy(self):
        """Test that proxies property returns a copy, not the original list"""
        original = ["http://p1:8080", "http://p2:8080"]
        rotator = ProxyRotator(original)

        proxies_copy = rotator.proxies
        proxies_copy.append("http://p3:8080")

        # Original should be unchanged
        assert len(rotator) == 2
        assert len(rotator.proxies) == 2

    def test_len_returns_proxy_count(self):
        """Test __len__ returns correct count"""
        assert len(ProxyRotator(["http://p1:8080"])) == 1
        assert len(ProxyRotator(["http://p1:8080", "http://p2:8080"])) == 2
        assert len(ProxyRotator(["a", "b", "c", "d", "e"])) == 5

    def test_repr(self):
        """Test __repr__ format"""
        rotator = ProxyRotator(["http://p1:8080", "http://p2:8080", "http://p3:8080"])
        assert repr(rotator) == "ProxyRotator(proxies=3)"


class TestProxyRotatorThreadSafety:
    """Test ProxyRotator thread safety"""

    def test_concurrent_get_proxy(self):
        """Test that concurrent get_proxy calls don't cause errors"""
        proxies = [f"http://p{i}:8080" for i in range(10)]
        rotator = ProxyRotator(proxies)
        results = []

        def get_proxies(n):
            for _ in range(n):
                results.append(rotator.get_proxy())

        threads = [Thread(target=get_proxies, args=(100,)) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All results should be valid proxies
        assert len(results) == 1000
        assert all(p in proxies for p in results)

    def test_thread_pool_concurrent_access(self):
        """Test concurrent access using ThreadPoolExecutor"""
        proxies = ["http://p1:8080", "http://p2:8080", "http://p3:8080"]
        rotator = ProxyRotator(proxies)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(rotator.get_proxy) for _ in range(100)]
            results = [f.result() for f in futures]

        assert len(results) == 100
        assert all(p in proxies for p in results)


class TestIsProxyError:
    """Test is_proxy_error utility function"""

    @pytest.mark.parametrize("error_msg", [
        "net::err_proxy_connection_failed",
        "NET::ERR_PROXY_AUTH_FAILED",
        "net::err_tunnel_connection_failed",
        "Connection refused by proxy",
        "Connection reset by peer",
        "Connection timed out while connecting to proxy",
        "Failed to connect to proxy server",
        "Could not resolve proxy host",
    ])
    def test_proxy_errors_detected(self, error_msg):
        """Test that proxy-related errors are detected"""
        assert is_proxy_error(Exception(error_msg)) is True

    @pytest.mark.parametrize("error_msg", [
        "Page not found",
        "404 Not Found",
        "Internal server error",
        "DNS resolution failed",
        "SSL certificate error",
        "Timeout waiting for response",
        "Invalid JSON response",
    ])
    def test_non_proxy_errors_not_detected(self, error_msg):
        """Test that non-proxy errors are not detected as proxy errors"""
        assert is_proxy_error(Exception(error_msg)) is False

    def test_case_insensitive_detection(self):
        """Test that error detection is case-insensitive"""
        assert is_proxy_error(Exception("NET::ERR_PROXY")) is True
        assert is_proxy_error(Exception("Net::Err_Proxy")) is True
        assert is_proxy_error(Exception("CONNECTION REFUSED")) is True

    def test_empty_error_message(self):
        """Test handling of empty error message"""
        assert is_proxy_error(Exception("")) is False

    def test_custom_exception_types(self):
        """Test with custom exception types"""
        class CustomError(Exception):
            pass

        assert is_proxy_error(CustomError("net::err_proxy_failed")) is True
        assert is_proxy_error(CustomError("normal error")) is False
