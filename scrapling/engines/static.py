from abc import ABC
from random import choice
from time import sleep as time_sleep
from asyncio import sleep as asyncio_sleep

from curl_cffi.curl import CurlError
from curl_cffi import CurlHttpVersion
from curl_cffi.requests import (
    BrowserTypeLiteral,
    Session as CurlSession,
    AsyncSession as AsyncCurlSession,
)

from scrapling.core.utils import log
from scrapling.core._types import (
    Any,
    Dict,
    Tuple,
    Unpack,
    Optional,
    Awaitable,
    SUPPORTED_HTTP_METHODS,
)

from .toolbelt.custom import Response
from .toolbelt.convertor import ResponseFactory
from .toolbelt.proxy_rotation import ProxyRotator, is_proxy_error
from ._browsers._types import RequestsSession, GetRequestParams, DataRequestParams, ImpersonateType
from .toolbelt.fingerprints import generate_convincing_referer, generate_headers, __default_useragent__

_NO_SESSION: Any = object()


def _select_random_browser(impersonate: ImpersonateType) -> Optional[BrowserTypeLiteral]:
    """
    Handle browser selection logic for the ` impersonate ` parameter.

    If impersonate is a list, randomly select one browser from it.
    If it's a string or None, return as is.
    """
    if isinstance(impersonate, list):
        if not impersonate:
            return None
        return choice(impersonate)
    return impersonate


class _ConfigurationLogic(ABC):
    # Core Logic Handler (Internal Engine)
    __slots__ = (
        "_default_impersonate",
        "_stealth",
        "_default_proxies",
        "_default_proxy",
        "_default_proxy_auth",
        "_default_timeout",
        "_default_headers",
        "_default_retries",
        "_default_retry_delay",
        "_default_follow_redirects",
        "_default_max_redirects",
        "_default_verify",
        "_default_cert",
        "_default_http3",
        "selector_config",
        "_is_alive",
        "_proxy_rotator",
    )

    def __init__(self, **kwargs: Unpack[RequestsSession]):
        self._default_impersonate = kwargs.get("impersonate", "chrome")
        self._stealth = kwargs.get("stealthy_headers", True)
        self._default_proxies = kwargs.get("proxies") or {}
        self._default_proxy = kwargs.get("proxy") or None
        self._default_proxy_auth = kwargs.get("proxy_auth") or None
        self._default_timeout = kwargs.get("timeout", 30)
        self._default_headers = kwargs.get("headers") or {}
        self._default_retries = kwargs.get("retries", 3)
        self._default_retry_delay = kwargs.get("retry_delay", 1)
        self._default_follow_redirects = kwargs.get("follow_redirects", True)
        self._default_max_redirects = kwargs.get("max_redirects", 30)
        self._default_verify = kwargs.get("verify", True)
        self._default_cert = kwargs.get("cert") or None
        self._default_http3 = kwargs.get("http3", False)
        self.selector_config = kwargs.get("selector_config") or {}
        self._is_alive = False
        self._proxy_rotator: Optional[ProxyRotator] = kwargs.get("proxy_rotator")

        if self._proxy_rotator and (self._default_proxy or self._default_proxies):
            raise ValueError(
                "Cannot use 'proxy_rotator' together with 'proxy' or 'proxies'. "
                "Use either a static proxy or proxy rotation, not both."
            )

    @staticmethod
    def _get_param(kwargs: Dict, key: str, default: Any) -> Any:
        """Get parameter from kwargs if present, otherwise return default."""
        return kwargs[key] if key in kwargs else default

    def _merge_request_args(self, **method_kwargs) -> Dict[str, Any]:
        """Merge request-specific arguments with default session arguments."""
        url = method_kwargs.pop("url")

        # Get parameters from kwargs or use defaults
        impersonate = self._get_param(method_kwargs, "impersonate", self._default_impersonate)
        impersonate = _select_random_browser(impersonate)
        http3_enabled = self._get_param(method_kwargs, "http3", self._default_http3)
        stealth = self._get_param(method_kwargs, "stealth", self._stealth)

        final_args = {
            "url": url,
            # Curl automatically generates the suitable browser headers when you use `impersonate`
            "headers": self._headers_job(
                url,
                self._get_param(method_kwargs, "headers", self._default_headers),
                stealth,
                bool(impersonate),
            ),
            "proxies": self._get_param(method_kwargs, "proxies", self._default_proxies),
            "proxy": self._get_param(method_kwargs, "proxy", self._default_proxy),
            "proxy_auth": self._get_param(method_kwargs, "proxy_auth", self._default_proxy_auth),
            "timeout": self._get_param(method_kwargs, "timeout", self._default_timeout),
            "allow_redirects": self._get_param(method_kwargs, "follow_redirects", self._default_follow_redirects),
            "max_redirects": self._get_param(method_kwargs, "max_redirects", self._default_max_redirects),
            "verify": self._get_param(method_kwargs, "verify", self._default_verify),
            "cert": self._get_param(method_kwargs, "cert", self._default_cert),
            "impersonate": impersonate,
        }

        # Add any remaining parameters that weren't explicitly handled above
        # Skip the ones we already processed plus internal params
        skip_keys = {
            "impersonate",
            "http3",
            "stealth",
            "headers",
            "proxies",
            "proxy",
            "proxy_auth",
            "timeout",
            "follow_redirects",
            "max_redirects",
            "verify",
            "cert",
            "retries",
            "retry_delay",
            "selector_config",
            # Browser session params (ignored by HTTP sessions)
            "extra_headers",
            "google_search",
        }
        for k, v in method_kwargs.items():
            if k not in skip_keys and v is not None:
                final_args[k] = v

        if http3_enabled:  # pragma: no cover
            final_args["http_version"] = CurlHttpVersion.V3ONLY
            if impersonate:
                log.warning(
                    "The argument `http3` might cause errors if used with `impersonate` argument, try switching it off if you encounter any curl errors."
                )

        return final_args

    def _headers_job(self, url, headers: Dict, stealth: bool, impersonate_enabled: bool) -> Dict:
        """
        1. Adds a useragent to the headers if it doesn't have one
        2. Generates real headers and append them to current headers
        3. Generates a referer header that looks like as if this request came from a Google's search of the current URL's domain.
        """
        # Merge session headers with request headers, request takes precedence (if it was set)
        final_headers = {**self._default_headers, **(headers if headers else {})}
        headers_keys = {k.lower() for k in final_headers}
        if stealth:
            if "referer" not in headers_keys:
                final_headers["referer"] = generate_convincing_referer(url)

            if not impersonate_enabled:  # Curl will generate the suitable headers
                extra_headers = generate_headers(browser_mode=False)
                final_headers.update(
                    {k: v for k, v in extra_headers.items() if k.lower() not in headers_keys}
                )  # Don't overwrite user-supplied headers

        elif "user-agent" not in headers_keys and not impersonate_enabled:  # pragma: no cover
            final_headers["User-Agent"] = __default_useragent__
            log.debug(f"Can't find useragent in headers so '{final_headers['User-Agent']}' was used.")

        return final_headers


class _SyncSessionLogic(_ConfigurationLogic):
    __slots__ = ("_curl_session",)

    def __init__(self, **kwargs: Unpack[RequestsSession]):
        super().__init__(**kwargs)
        self._curl_session: Optional[CurlSession] = None

    def __enter__(self):
        """Creates and returns a new synchronous Fetcher Session"""
        if self._is_alive:
            raise RuntimeError("This FetcherSession instance already has an active synchronous session.")

        self._curl_session = CurlSession()
        self._is_alive = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the active synchronous session managed by this instance, if any."""
        # For type checking (not accessed error)
        _ = (
            exc_type,
            exc_val,
            exc_tb,
        )
        if self._curl_session:
            self._curl_session.close()
            self._curl_session = None

        self._is_alive = False

    def _make_request(self, method: SUPPORTED_HTTP_METHODS, stealth: Optional[bool] = None, **kwargs) -> Response:
        """
        Perform an HTTP request using the configured session.
        """
        stealth = self._stealth if stealth is None else stealth

        selector_config = self._get_param(kwargs, "selector_config", self.selector_config) or self.selector_config
        max_retries = self._get_param(kwargs, "retries", self._default_retries)
        retry_delay = self._get_param(kwargs, "retry_delay", self._default_retry_delay)
        static_proxy = kwargs.pop("proxy", None)

        session = self._curl_session
        one_off_request = False
        if session is _NO_SESSION and self.__enter__ is None:
            # For usage inside FetcherClient
            # It turns out `curl_cffi` caches impersonation state, so if you turned it off, then on then off, it won't be off on the last time.
            session = CurlSession()
            one_off_request = True

        if not session:
            raise RuntimeError("No active session available.")  # pragma: no cover

        try:
            for attempt in range(max_retries):
                if self._proxy_rotator and static_proxy is None:
                    proxy = self._proxy_rotator.get_proxy()
                else:
                    proxy = static_proxy

                request_args = self._merge_request_args(stealth=stealth, proxy=proxy, **kwargs)
                try:
                    response = session.request(method, **request_args)
                    result = ResponseFactory.from_http_request(response, selector_config, meta={"proxy": proxy})
                    return result
                except CurlError as e:  # pragma: no cover
                    if attempt < max_retries - 1:
                        # Now if the rotator is enabled, we will try again with the new proxy
                        # If it's not enabled, then we will try again with the same proxy
                        if is_proxy_error(e):
                            log.warning(
                                f"Proxy '{proxy}' failed (attempt {attempt + 1}) | Retrying in {retry_delay} seconds..."
                            )
                        else:
                            log.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                        time_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail
        finally:
            if session and one_off_request:
                session.close()

        raise RuntimeError("No active session available.")  # pragma: no cover

    def get(self, url: str, **kwargs: Unpack[GetRequestParams]) -> Response:
        """
        Perform a GET request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.Session().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("GET", stealth=stealthy_headers, url=url, **kwargs)

    def post(self, url: str, **kwargs: Unpack[DataRequestParams]) -> Response:
        """
        Perform a POST request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.Session().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - data: Form data to include in the request body.
            - json: A JSON serializable object to include in the body of the request.
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("POST", stealth=stealthy_headers, url=url, **kwargs)

    def put(self, url: str, **kwargs: Unpack[DataRequestParams]) -> Response:
        """
        Perform a PUT request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.Session().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - data: Form data to include in the request body.
            - json: A JSON serializable object to include in the body of the request.
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("PUT", stealth=stealthy_headers, url=url, **kwargs)

    def delete(self, url: str, **kwargs: Unpack[DataRequestParams]) -> Response:
        """
        Perform a DELETE request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.Session().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - data: Form data to include in the request body.
            - json: A JSON serializable object to include in the body of the request.
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        # Careful of sending a body in a DELETE request, it might cause some websites to reject the request as per https://www.rfc-editor.org/rfc/rfc7231#section-4.3.5,
        # But some websites accept it, it depends on the implementation used.
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("DELETE", stealth=stealthy_headers, url=url, **kwargs)


class _ASyncSessionLogic(_ConfigurationLogic):
    __slots__ = ("_async_curl_session",)

    def __init__(self, **kwargs: Unpack[RequestsSession]):
        super().__init__(**kwargs)
        self._async_curl_session: Optional[AsyncCurlSession] = None

    async def __aenter__(self):  # pragma: no cover
        """Creates and returns a new asynchronous Session."""
        if self._is_alive:
            raise RuntimeError("This FetcherSession instance already has an active asynchronous session.")

        self._async_curl_session = AsyncCurlSession()
        self._is_alive = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the active asynchronous session managed by this instance, if any."""
        # For type checking (not accessed error)
        _ = (
            exc_type,
            exc_val,
            exc_tb,
        )
        if self._async_curl_session:
            await self._async_curl_session.close()
            self._async_curl_session = None

        self._is_alive = False

    async def _make_request(self, method: SUPPORTED_HTTP_METHODS, stealth: Optional[bool] = None, **kwargs) -> Response:
        """
        Perform an HTTP request using the configured session.
        """
        stealth = self._stealth if stealth is None else stealth

        selector_config = self._get_param(kwargs, "selector_config", self.selector_config) or self.selector_config
        max_retries = self._get_param(kwargs, "retries", self._default_retries)
        retry_delay = self._get_param(kwargs, "retry_delay", self._default_retry_delay)
        static_proxy = kwargs.pop("proxy", None)

        session = self._async_curl_session
        one_off_request = False
        if session is _NO_SESSION and self.__aenter__ is None:
            # For usage inside the ` AsyncFetcherClient ` class, and that's for several reasons
            # 1. It turns out `curl_cffi` caches impersonation state, so if you turned it off, then on then off, it won't be off on the last time.
            # 2. `curl_cffi` doesn't support making async requests without sessions
            # 3. Using a single session for many requests at the same time in async doesn't sit well with curl_cffi.
            session = AsyncCurlSession()
            one_off_request = True

        if not session:
            raise RuntimeError("No active session available.")  # pragma: no cover

        try:
            # Determine if we should use proxy rotation
            for attempt in range(max_retries):
                if self._proxy_rotator and static_proxy is None:
                    proxy = self._proxy_rotator.get_proxy()
                else:
                    proxy = static_proxy

                request_args = self._merge_request_args(stealth=stealth, proxy=proxy, **kwargs)
                try:
                    response = await session.request(method, **request_args)
                    result = ResponseFactory.from_http_request(response, selector_config, meta={"proxy": proxy})
                    return result
                except CurlError as e:  # pragma: no cover
                    if attempt < max_retries - 1:
                        # Now if the rotator is enabled, we will try again with the new proxy
                        # If it's not enabled, then we will try again with the same proxy
                        if is_proxy_error(e):
                            log.warning(
                                f"Proxy '{proxy}' failed (attempt {attempt + 1}) | Retrying in {retry_delay} seconds..."
                            )
                        else:
                            log.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")

                        await asyncio_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail
        finally:
            if session and one_off_request:
                await session.close()

        raise RuntimeError("No active session available.")  # pragma: no cover

    def get(self, url: str, **kwargs: Unpack[GetRequestParams]) -> Awaitable[Response]:
        """
        Perform a GET request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.AsyncSession().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("GET", stealth=stealthy_headers, url=url, **kwargs)

    def post(self, url: str, **kwargs: Unpack[DataRequestParams]) -> Awaitable[Response]:
        """
        Perform a POST request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.AsyncSession().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - data: Form data to include in the request body.
            - json: A JSON serializable object to include in the body of the request.
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("POST", stealth=stealthy_headers, url=url, **kwargs)

    def put(self, url: str, **kwargs: Unpack[DataRequestParams]) -> Awaitable[Response]:
        """
        Perform a PUT request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.AsyncSession().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - data: Form data to include in the request body.
            - json: A JSON serializable object to include in the body of the request.
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("PUT", stealth=stealthy_headers, url=url, **kwargs)

    def delete(self, url: str, **kwargs: Unpack[DataRequestParams]) -> Awaitable[Response]:
        """
        Perform a DELETE request.

        Any additional keyword arguments are passed to the `curl_cffi.requests.AsyncSession().request()` method.

        :param url: Target URL for the request.
        :param kwargs: Additional keyword arguments including:
            - data: Form data to include in the request body.
            - json: A JSON serializable object to include in the body of the request.
            - params: Query string parameters for the request.
            - headers: Headers to include in the request.
            - cookies: Cookies to use in the request.
            - timeout: Number of seconds to wait before timing out.
            - follow_redirects: Whether to follow redirects. Defaults to True.
            - max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
            - retries: Number of retry attempts. Defaults to 3.
            - retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
            - proxies: Dict of proxies to use.
            - proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
            - proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
            - auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
            - verify: Whether to verify HTTPS certificates.
            - cert: Tuple of (cert, key) filenames for the client certificate.
            - impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
            - http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
            - stealthy_headers: If enabled (default), it creates and adds real browser headers.
        :return: A `Response` object.
        """
        # Careful of sending a body in a DELETE request, it might cause some websites to reject the request as per https://www.rfc-editor.org/rfc/rfc7231#section-4.3.5,
        # But some websites accept it, it depends on the implementation used.
        stealthy_headers = kwargs.pop("stealthy_headers", None)
        return self._make_request("DELETE", stealth=stealthy_headers, url=url, **kwargs)


class FetcherSession:
    """
    A factory context manager that provides configured Fetcher sessions.

    When this manager is used in a 'with' or 'async with' block,
    it yields a new session configured with the manager's defaults.
    A single instance of this manager should ideally be used for one active
    session at a time (or sequentially). Re-entering a context with the
    same manager instance while a session is already active is disallowed.
    """

    __slots__ = (
        "_default_impersonate",
        "_stealth",
        "_default_proxies",
        "_default_proxy",
        "_default_proxy_auth",
        "_default_timeout",
        "_default_headers",
        "_default_retries",
        "_default_retry_delay",
        "_default_follow_redirects",
        "_default_max_redirects",
        "_default_verify",
        "_default_cert",
        "_default_http3",
        "selector_config",
        "_client",
        "_is_alive",
        "_proxy_rotator",
    )

    def __init__(
        self,
        impersonate: ImpersonateType = "chrome",
        http3: Optional[bool] = False,
        stealthy_headers: Optional[bool] = True,
        proxies: Optional[Dict[str, str]] = None,
        proxy: Optional[str] = None,
        proxy_auth: Optional[Tuple[str, str]] = None,
        timeout: Optional[int | float] = 30,
        headers: Optional[Dict[str, str]] = None,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        follow_redirects: bool = True,
        max_redirects: int = 30,
        verify: bool = True,
        cert: Optional[str | Tuple[str, str]] = None,
        selector_config: Optional[Dict] = None,
        proxy_rotator: Optional[ProxyRotator] = None,
    ):
        """
        :param impersonate: Browser version to impersonate. Can be a single browser string or a list of browser strings for random selection. (Default: latest available Chrome version)
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        :param proxies: Dict of proxies to use. Format: {"http": proxy_url, "https": proxy_url}.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param timeout: Number of seconds to wait before timing out.
        :param headers: Headers to include in the session with every request.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param verify: Whether to verify HTTPS certificates. Defaults to True.
        :param cert: Tuple of (cert, key) filenames for the client certificate.
        :param selector_config: Arguments passed when creating the final Selector class.
        :param proxy_rotator: A ProxyRotator instance for automatic proxy rotation.
        """
        self._default_impersonate: ImpersonateType = impersonate
        self._stealth = stealthy_headers
        self._default_proxies = proxies or {}
        self._default_proxy = proxy or None
        self._default_proxy_auth = proxy_auth or None
        self._default_timeout = timeout
        self._default_headers = headers or {}
        self._default_retries = retries
        self._default_retry_delay = retry_delay
        self._default_follow_redirects = follow_redirects
        self._default_max_redirects = max_redirects
        self._default_verify = verify
        self._default_cert = cert
        self._default_http3 = http3
        self.selector_config = selector_config or {}
        self._is_alive = False
        self._client: _SyncSessionLogic | _ASyncSessionLogic | None = None
        self._proxy_rotator = proxy_rotator

    def __enter__(self) -> _SyncSessionLogic:
        """Creates and returns a new synchronous Fetcher Session"""
        if self._client is None:
            # Use **vars(self) to avoid repeating all parameters
            config = {k.replace("_default_", ""): getattr(self, k) for k in self.__slots__ if k.startswith("_default")}
            config["stealthy_headers"] = self._stealth
            config["selector_config"] = self.selector_config
            config["proxy_rotator"] = self._proxy_rotator
            self._client = _SyncSessionLogic(**config)
            self._is_alive = True
            return self._client.__enter__()
        raise RuntimeError("This FetcherSession instance already has an active synchronous session.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None and isinstance(self._client, _SyncSessionLogic):
            self._client.__exit__(exc_type, exc_val, exc_tb)
            self._client = None
            self._is_alive = False
            return
        raise RuntimeError("Cannot exit invalid session")

    async def __aenter__(self) -> _ASyncSessionLogic:
        """Creates and returns a new asynchronous Session."""
        if self._client is None:
            # Use **vars(self) to avoid repeating all parameters
            config = {k.replace("_default_", ""): getattr(self, k) for k in self.__slots__ if k.startswith("_default")}
            config["stealthy_headers"] = self._stealth
            config["selector_config"] = self.selector_config
            config["proxy_rotator"] = self._proxy_rotator
            self._client = _ASyncSessionLogic(**config)
            self._is_alive = True
            return await self._client.__aenter__()
        raise RuntimeError("This FetcherSession instance already has an active asynchronous session.")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None and isinstance(self._client, _ASyncSessionLogic):
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            self._client = None
            self._is_alive = False
            return
        raise RuntimeError("Cannot exit invalid session")


class FetcherClient(_SyncSessionLogic):
    __slots__ = ("__enter__", "__exit__")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__enter__: Any = None
        self.__exit__: Any = None
        self._curl_session: Any = _NO_SESSION


class AsyncFetcherClient(_ASyncSessionLogic):
    __slots__ = ("__aenter__", "__aexit__")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__aenter__: Any = None
        self.__aexit__: Any = None
        self._async_curl_session: Any = _NO_SESSION
