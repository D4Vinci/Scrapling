from time import sleep as time_sleep
from asyncio import sleep as asyncio_sleep

from curl_cffi.requests.session import CurlError
from curl_cffi import CurlHttpVersion
from curl_cffi.requests.impersonate import DEFAULT_CHROME
from curl_cffi.requests import (
    ProxySpec,
    CookieTypes,
    BrowserTypeLiteral,
    Session as CurlSession,
    AsyncSession as AsyncCurlSession,
)

from scrapling.core.utils import log
from scrapling.core._types import (
    Dict,
    Optional,
    Tuple,
    Mapping,
    SUPPORTED_HTTP_METHODS,
    Awaitable,
    List,
    Any,
)

from .toolbelt import (
    Response,
    generate_convincing_referer,
    generate_headers,
    ResponseFactory,
    __default_useragent__,
)

_UNSET = object()


class FetcherSession:
    """
    A context manager that provides configured Fetcher sessions.

    When this manager is used in a 'with' or 'async with' block,
    it yields a new session configured with the manager's defaults.
    A single instance of this manager should ideally be used for one active
    session at a time (or sequentially). Re-entering a context with the
    same manager instance while a session is already active is disallowed.
    """

    def __init__(
        self,
        impersonate: Optional[BrowserTypeLiteral] = DEFAULT_CHROME,
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
    ):
        """
        :param impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
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
        """
        self.default_impersonate = impersonate
        self.stealth = stealthy_headers
        self.default_proxies = proxies or {}
        self.default_proxy = proxy or None
        self.default_proxy_auth = proxy_auth or None
        self.default_timeout = timeout
        self.default_headers = headers or {}
        self.default_retries = retries
        self.default_retry_delay = retry_delay
        self.default_follow_redirects = follow_redirects
        self.default_max_redirects = max_redirects
        self.default_verify = verify
        self.default_cert = cert
        self.default_http3 = http3
        self.selector_config = selector_config or {}

        self._curl_session: Optional[CurlSession] = None
        self._async_curl_session: Optional[AsyncCurlSession] = None

    def _merge_request_args(self, **kwargs) -> Dict[str, Any]:
        """Merge request-specific arguments with default session arguments."""
        url = kwargs.pop("url")
        request_args = {}

        headers = self.get_with_precedence(kwargs, "headers", self.default_headers)
        stealth = self.get_with_precedence(kwargs, "stealth", self.stealth)
        impersonate = self.get_with_precedence(
            kwargs, "impersonate", self.default_impersonate
        )

        if self.get_with_precedence(
            kwargs, "http3", self.default_http3
        ):  # pragma: no cover
            request_args["http_version"] = CurlHttpVersion.V3ONLY
            if impersonate:
                log.warning(
                    "The argument `http3` might cause errors if used with `impersonate` argument, try switching it off if you encounter any curl errors."
                )

        request_args.update(
            {
                "url": url,
                # Curl automatically generates the suitable browser headers when you use `impersonate`
                "headers": self._headers_job(url, headers, stealth, bool(impersonate)),
                "proxies": self.get_with_precedence(
                    kwargs, "proxies", self.default_proxies
                ),
                "proxy": self.get_with_precedence(kwargs, "proxy", self.default_proxy),
                "proxy_auth": self.get_with_precedence(
                    kwargs, "proxy_auth", self.default_proxy_auth
                ),
                "timeout": self.get_with_precedence(
                    kwargs, "timeout", self.default_timeout
                ),
                "allow_redirects": self.get_with_precedence(
                    kwargs, "allow_redirects", self.default_follow_redirects
                ),
                "max_redirects": self.get_with_precedence(
                    kwargs, "max_redirects", self.default_max_redirects
                ),
                "verify": self.get_with_precedence(
                    kwargs, "verify", self.default_verify
                ),
                "cert": self.get_with_precedence(kwargs, "cert", self.default_cert),
                "impersonate": impersonate,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if v
                    not in (
                        _UNSET,
                        None,
                    )
                },  # Add any remaining parameters (after all known ones are popped)
            }
        )
        return request_args

    def _headers_job(
        self,
        url,
        headers: Optional[Dict],
        stealth: Optional[bool],
        impersonate_enabled: bool,
    ) -> Dict:
        """Adds useragent to headers if it doesn't exist, generates real headers and append it to current headers, and
            finally generates a referer header that looks like if this request came from Google's search of the current URL's domain.

        :param headers: Current headers in the request if the user passed any
        :param stealth: Whether to enable the `stealthy_headers` argument to this request or not. If `None`, it defaults to the session default value.
        :param impersonate_enabled: Whether the browser impersonation is enabled or not.
        :return: A dictionary of the new headers.
        """
        # Handle headers - if it was _UNSET, use default_headers
        if headers is _UNSET:
            headers = self.default_headers.copy()
        else:
            # Merge session headers with request headers, request takes precedence
            headers = {**self.default_headers, **(headers or {})}

        headers_keys = set(map(str.lower, headers.keys()))
        if stealth:
            if "referer" not in headers_keys:
                headers.update({"referer": generate_convincing_referer(url)})

            if impersonate_enabled:  # Curl will generate the suitable headers
                return headers

            extra_headers = generate_headers(browser_mode=False)
            # Don't overwrite user-supplied headers
            extra_headers = {
                key: value
                for key, value in extra_headers.items()
                if key.lower() not in headers_keys
            }
            headers.update(extra_headers)

        elif "user-agent" not in headers_keys and not impersonate_enabled:
            headers["User-Agent"] = __default_useragent__
            log.debug(
                f"Can't find useragent in headers so '{headers['User-Agent']}' was used."
            )

        return headers

    def __enter__(self):
        """Creates and returns a new synchronous Fetcher Session"""
        if self._curl_session:
            raise RuntimeError(
                "This FetcherSession instance already has an active synchronous session. "
                "Create a new FetcherSession instance for a new independent session, "
                "or use the current instance sequentially after the previous context has exited."
            )
        if (
            self._async_curl_session
        ):  # Prevent mixing if async is active from this instance
            raise RuntimeError(
                "This FetcherSession instance has an active asynchronous session. "
                "Cannot enter a synchronous context simultaneously with the same manager instance."
            )

        self._curl_session = CurlSession()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the active synchronous session managed by this instance, if any."""
        if self._curl_session:
            self._curl_session.close()
            self._curl_session = None

    async def __aenter__(self):
        """Creates and returns a new asynchronous Session."""
        if self._async_curl_session:
            raise RuntimeError(
                "This FetcherSession instance already has an active asynchronous session. "
                "Create a new FetcherSession instance for a new independent session, "
                "or use the current instance sequentially after the previous context has exited."
            )
        if self._curl_session:  # Prevent mixing if sync is active from this instance
            raise RuntimeError(
                "This FetcherSession instance has an active synchronous session. "
                "Cannot enter an asynchronous context simultaneously with the same manager instance."
            )

        self._async_curl_session = AsyncCurlSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the active asynchronous session managed by this instance, if any."""
        if self._async_curl_session:
            await self._async_curl_session.close()
            self._async_curl_session = None

    def __make_request(
        self,
        method: SUPPORTED_HTTP_METHODS,
        request_args: Dict[str, Any],
        max_retries: int,
        retry_delay: int,
        selector_config: Optional[Dict] = None,
    ) -> Response:
        """
        Perform an HTTP request using the configured session.

        :param method: HTTP method to be used, supported methods are ["GET", "POST", "PUT", "DELETE"]
        :param url: Target URL for the request.
        :param request_args: Arguments to be passed to the session's `request()` method.
        :param max_retries: Maximum number of retries for the request.
        :param retry_delay: Number of seconds to wait between retries.
        :param selector_config: Arguments passed when creating the final Selector class.
        :return: A `Response` object for synchronous requests or an awaitable for asynchronous.
        """
        session = self._curl_session
        if session is True and not any(
            (self.__enter__, self.__exit__, self.__aenter__, self.__aexit__)
        ):
            # For usage inside FetcherClient
            # It turns out `curl_cffi` caches impersonation state, so if you turned it off, then on then off, it won't be off on the last time.
            session = CurlSession()

        if session:
            for attempt in range(max_retries):
                try:
                    response = session.request(method, **request_args)
                    # response.raise_for_status()  # Retry responses with a status code between 200-400
                    return ResponseFactory.from_http_request(response, selector_config)
                except CurlError as e:  # pragma: no cover
                    if attempt < max_retries - 1:
                        log.error(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds..."
                        )
                        time_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail

        raise RuntimeError("No active session available.")  # pragma: no cover

    async def __make_async_request(
        self,
        method: SUPPORTED_HTTP_METHODS,
        request_args: Dict[str, Any],
        max_retries: int,
        retry_delay: int,
        selector_config: Optional[Dict] = None,
    ) -> Response:
        """
        Perform an HTTP request using the configured session.

        :param method: HTTP method to be used, supported methods are ["GET", "POST", "PUT", "DELETE"]
        :param url: Target URL for the request.
        :param request_args: Arguments to be passed to the session's `request()` method.
        :param max_retries: Maximum number of retries for the request.
        :param retry_delay: Number of seconds to wait between retries.
        :param selector_config: Arguments passed when creating the final Selector class.
        :return: A `Response` object for synchronous requests or an awaitable for asynchronous.
        """
        session = self._async_curl_session
        if session is True and not any(
            (self.__enter__, self.__exit__, self.__aenter__, self.__aexit__)
        ):
            # For usage inside the ` AsyncFetcherClient ` class, and that's for several reasons
            # 1. It turns out `curl_cffi` caches impersonation state, so if you turned it off, then on then off, it won't be off on the last time.
            # 2. `curl_cffi` doesn't support making async requests without sessions
            # 3. Using a single session for many requests at the same time in async doesn't sit well with curl_cffi.
            session = AsyncCurlSession()

        if session:
            for attempt in range(max_retries):
                try:
                    response = await session.request(method, **request_args)
                    # response.raise_for_status()  # Retry responses with a status code between 200-400
                    return ResponseFactory.from_http_request(response, selector_config)
                except CurlError as e:  # pragma: no cover
                    if attempt < max_retries - 1:
                        log.error(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds..."
                        )
                        await asyncio_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail

        raise RuntimeError("No active session available.")  # pragma: no cover

    @staticmethod
    def get_with_precedence(kwargs, key, default_value):
        """Get value with request-level priority over session-level"""
        request_value = kwargs.pop(key, _UNSET)
        return request_value if request_value is not _UNSET else default_value

    def __prepare_and_dispatch(
        self,
        method: SUPPORTED_HTTP_METHODS,
        stealth: Optional[bool] = None,
        **kwargs,
    ) -> Response | Awaitable[Response]:
        """
        Internal dispatcher. Prepares arguments and calls sync or async request helper.

        :param method: HTTP method to be used, supported methods are ["GET", "POST", "PUT", "DELETE"]
        :param stealth: Whether to enable the `stealthy_headers` argument to this request or not. If `None`, it defaults to the session default value.
        :param url: Target URL for the request.
        :param kwargs: Additional request-specific arguments.
        :return: A `Response` object for synchronous requests or an awaitable for asynchronous.
        """
        stealth = self.stealth if stealth is None else stealth

        selector_config = kwargs.pop("selector_config", {}) or self.selector_config
        max_retries = self.get_with_precedence(kwargs, "retries", self.default_retries)
        retry_delay = self.get_with_precedence(
            kwargs, "retry_delay", self.default_retry_delay
        )
        request_args = self._merge_request_args(stealth=stealth, **kwargs)
        if self._curl_session:
            return self.__make_request(
                method, request_args, max_retries, retry_delay, selector_config
            )
        elif self._async_curl_session:
            # The returned value is a Coroutine
            return self.__make_async_request(
                method, request_args, max_retries, retry_delay, selector_config
            )

        raise RuntimeError("No active session available.")

    def get(
        self,
        url: str,
        params: Optional[Dict | List | Tuple] = None,
        headers: Optional[Mapping[str, Optional[str]]] = _UNSET,
        cookies: Optional[CookieTypes] = None,
        timeout: Optional[int | float] = _UNSET,
        follow_redirects: Optional[bool] = _UNSET,
        max_redirects: Optional[int] = _UNSET,
        retries: Optional[int] = _UNSET,
        retry_delay: Optional[int] = _UNSET,
        proxies: Optional[ProxySpec] = _UNSET,
        proxy: Optional[str] = _UNSET,
        proxy_auth: Optional[Tuple[str, str]] = _UNSET,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = _UNSET,
        cert: Optional[str | Tuple[str, str]] = _UNSET,
        impersonate: Optional[BrowserTypeLiteral] = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response | Awaitable[Response]:
        """
        Perform a GET request.

        :param url: Target URL for the request.
        :param params: Query string parameters for the request.
        :param headers: Headers to include in the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxies: Dict of proxies to use.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
        :param verify: Whether to verify HTTPS certificates.
        :param cert: Tuple of (cert, key) filenames for the client certificate.
        :param impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the [`curl_cffi.requests.Session().request()`, `curl_cffi.requests.AsyncSession().request()`] method.
        :return: A `Response` object or an awaitable for async.
        """
        request_args = {
            "url": url,
            "params": params,
            "headers": headers,
            "cookies": cookies,
            "timeout": timeout,
            "retry_delay": retry_delay,
            "allow_redirects": follow_redirects,
            "max_redirects": max_redirects,
            "retries": retries,
            "proxies": proxies,
            "proxy": proxy,
            "proxy_auth": proxy_auth,
            "auth": auth,
            "verify": verify,
            "cert": cert,
            "impersonate": impersonate,
            "http3": http3,
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "GET", stealth=stealthy_headers, **request_args
        )

    def post(
        self,
        url: str,
        data: Optional[Dict | str] = None,
        json: Optional[Dict | List] = None,
        headers: Optional[Mapping[str, Optional[str]]] = _UNSET,
        params: Optional[Dict | List | Tuple] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: Optional[int | float] = _UNSET,
        follow_redirects: Optional[bool] = _UNSET,
        max_redirects: Optional[int] = _UNSET,
        retries: Optional[int] = _UNSET,
        retry_delay: Optional[int] = _UNSET,
        proxies: Optional[ProxySpec] = _UNSET,
        proxy: Optional[str] = _UNSET,
        proxy_auth: Optional[Tuple[str, str]] = _UNSET,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = _UNSET,
        cert: Optional[str | Tuple[str, str]] = _UNSET,
        impersonate: Optional[BrowserTypeLiteral] = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response | Awaitable[Response]:
        """
        Perform a POST request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
        :param headers: Headers to include in the request.
        :param params: Query string parameters for the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxies: Dict of proxies to use. Format: {"http": proxy_url, "https": proxy_url}.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
        :param verify: Whether to verify HTTPS certificates. Defaults to True.
        :param cert: Tuple of (cert, key) filenames for the client certificate.
        :param impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the [`curl_cffi.requests.Session().request()`, `curl_cffi.requests.AsyncSession().request()`] method.
        :return: A `Response` object or an awaitable for async.
        """
        request_args = {
            "url": url,
            "data": data,
            "json": json,
            "headers": headers,
            "params": params,
            "cookies": cookies,
            "timeout": timeout,
            "retry_delay": retry_delay,
            "proxy": proxy,
            "impersonate": impersonate,
            "allow_redirects": follow_redirects,
            "max_redirects": max_redirects,
            "retries": retries,
            "proxies": proxies,
            "proxy_auth": proxy_auth,
            "auth": auth,
            "verify": verify,
            "cert": cert,
            "http3": http3,
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "POST", stealth=stealthy_headers, **request_args
        )

    def put(
        self,
        url: str,
        data: Optional[Dict | str] = None,
        json: Optional[Dict | List] = None,
        headers: Optional[Mapping[str, Optional[str]]] = _UNSET,
        params: Optional[Dict | List | Tuple] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: Optional[int | float] = _UNSET,
        follow_redirects: Optional[bool] = _UNSET,
        max_redirects: Optional[int] = _UNSET,
        retries: Optional[int] = _UNSET,
        retry_delay: Optional[int] = _UNSET,
        proxies: Optional[ProxySpec] = _UNSET,
        proxy: Optional[str] = _UNSET,
        proxy_auth: Optional[Tuple[str, str]] = _UNSET,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = _UNSET,
        cert: Optional[str | Tuple[str, str]] = _UNSET,
        impersonate: Optional[BrowserTypeLiteral] = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response | Awaitable[Response]:
        """
        Perform a PUT request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
        :param headers: Headers to include in the request.
        :param params: Query string parameters for the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxies: Dict of proxies to use. Format: {"http": proxy_url, "https": proxy_url}.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
        :param verify: Whether to verify HTTPS certificates. Defaults to True.
        :param cert: Tuple of (cert, key) filenames for the client certificate.
        :param impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the [`curl_cffi.requests.Session().request()`, `curl_cffi.requests.AsyncSession().request()`] method.
        :return: A `Response` object or an awaitable for async.
        """
        request_args = {
            "url": url,
            "data": data,
            "json": json,
            "headers": headers,
            "params": params,
            "cookies": cookies,
            "timeout": timeout,
            "retry_delay": retry_delay,
            "proxy": proxy,
            "impersonate": impersonate,
            "allow_redirects": follow_redirects,
            "max_redirects": max_redirects,
            "retries": retries,
            "proxies": proxies,
            "proxy_auth": proxy_auth,
            "auth": auth,
            "verify": verify,
            "cert": cert,
            "http3": http3,
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "PUT", stealth=stealthy_headers, **request_args
        )

    def delete(
        self,
        url: str,
        data: Optional[Dict | str] = None,
        json: Optional[Dict | List] = None,
        headers: Optional[Mapping[str, Optional[str]]] = _UNSET,
        params: Optional[Dict | List | Tuple] = None,
        cookies: Optional[CookieTypes] = None,
        timeout: Optional[int | float] = _UNSET,
        follow_redirects: Optional[bool] = _UNSET,
        max_redirects: Optional[int] = _UNSET,
        retries: Optional[int] = _UNSET,
        retry_delay: Optional[int] = _UNSET,
        proxies: Optional[ProxySpec] = _UNSET,
        proxy: Optional[str] = _UNSET,
        proxy_auth: Optional[Tuple[str, str]] = _UNSET,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = _UNSET,
        cert: Optional[str | Tuple[str, str]] = _UNSET,
        impersonate: Optional[BrowserTypeLiteral] = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response | Awaitable[Response]:
        """
        Perform a DELETE request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
        :param headers: Headers to include in the request.
        :param params: Query string parameters for the request.
        :param cookies: Cookies to use in the request.
        :param timeout: Number of seconds to wait before timing out.
        :param follow_redirects: Whether to follow redirects. Defaults to True.
        :param max_redirects: Maximum number of redirects. Default 30, use -1 for unlimited.
        :param retries: Number of retry attempts. Defaults to 3.
        :param retry_delay: Number of seconds to wait between retry attempts. Defaults to 1 second.
        :param proxies: Dict of proxies to use. Format: {"http": proxy_url, "https": proxy_url}.
        :param proxy: Proxy URL to use. Format: "http://username:password@localhost:8030".
                     Cannot be used together with the `proxies` parameter.
        :param proxy_auth: HTTP basic auth for proxy, tuple of (username, password).
        :param auth: HTTP basic auth tuple of (username, password). Only basic auth is supported.
        :param verify: Whether to verify HTTPS certificates. Defaults to True.
        :param cert: Tuple of (cert, key) filenames for the client certificate.
        :param impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the [`curl_cffi.requests.Session().request()`, `curl_cffi.requests.AsyncSession().request()`] method.
        :return: A `Response` object or an awaitable for async.
        """
        request_args = {
            "url": url,
            # Careful of sending a body in a DELETE request, it might cause some websites to reject the request as per https://www.rfc-editor.org/rfc/rfc7231#section-4.3.5,
            # But some websites accept it, it depends on the implementation used.
            "data": data,
            "json": json,
            "headers": headers,
            "params": params,
            "cookies": cookies,
            "timeout": timeout,
            "retry_delay": retry_delay,
            "proxy": proxy,
            "impersonate": impersonate,
            "allow_redirects": follow_redirects,
            "max_redirects": max_redirects,
            "retries": retries,
            "proxies": proxies,
            "proxy_auth": proxy_auth,
            "auth": auth,
            "verify": verify,
            "cert": cert,
            "http3": http3,
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "DELETE", stealth=stealthy_headers, **request_args
        )


class FetcherClient(FetcherSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__enter__ = None
        self.__exit__ = None
        self.__aenter__ = None
        self.__aexit__ = None
        self._curl_session = True


class AsyncFetcherClient(FetcherSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__enter__ = None
        self.__exit__ = None
        self.__aenter__ = None
        self.__aexit__ = None
        self._async_curl_session = True
