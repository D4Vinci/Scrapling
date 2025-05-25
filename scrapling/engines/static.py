from time import sleep as time_sleep
from asyncio import sleep as asyncio_sleep

from curl_cffi.requests.session import CurlError
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
    Union,
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
)

__default_useragent__ = generate_headers(browser_mode=False).get("User-Agent")


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
        impersonate: Optional[str] = "chrome136",
        stealthy_headers: Optional[bool] = True,
        proxies: Optional[Dict[str, str]] = None,
        proxy: Optional[str] = None,
        proxy_auth: Optional[Tuple[str, str]] = None,
        timeout: Optional[Union[int, float]] = 30,
        headers: Optional[Dict[str, str]] = None,
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,
        follow_redirects: bool = True,
        max_redirects: int = 30,
        verify: bool = True,
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        adaptor_arguments: Optional[Dict] = None,
    ):
        """
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
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
        :param adaptor_arguments: Arguments passed when creating the final Adaptor class.
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
        self.adaptor_arguments = adaptor_arguments or {}

        self._curl_session: Optional[CurlSession] = None
        self._async_curl_session: Optional[AsyncCurlSession] = None

    def _merge_request_args(self, **kwargs) -> Dict[str, Any]:
        """Merge request-specific arguments with default session arguments."""
        request_args = {
            "headers": self._headers_job(
                kwargs["url"], kwargs.get("headers"), kwargs.pop("stealth")
            ),
            "proxies": kwargs.get("proxies", self.default_proxies),
            "proxy": kwargs.get("proxy", self.default_proxy),
            "proxy_auth": kwargs.get("proxy_auth", self.default_proxy_auth),
            "timeout": kwargs.get("timeout", self.default_timeout),
            "allow_redirects": kwargs.get(
                "follow_redirects", self.default_follow_redirects
            ),
            "max_redirects": kwargs.get("max_redirects", self.default_max_redirects),
            "verify": kwargs.get("verify", self.default_verify),
            "cert": kwargs.get("cert", self.default_cert),
            "impersonate": kwargs.get("impersonate", self.default_impersonate),
            **kwargs,
        }
        return request_args

    def _headers_job(
        self, url, headers: Optional[Dict], stealth: Optional[bool]
    ) -> Dict:
        """Adds useragent to headers if it doesn't exist, generates real headers and append it to current headers, and
            finally generates a referer header that looks like if this request came from Google's search of the current URL's domain.

        :param headers: Current headers in the request if the user passed any
        :param stealth: Whether to enable the `stealthy_headers` argument to this request or not. If `None`, it defaults to the session default value.
        :return: A dictionary of the new headers.
        """
        headers = {**self.default_headers, **(headers or {})}
        headers_keys = set(map(str.lower, headers.keys()))

        if stealth:
            extra_headers = generate_headers(browser_mode=False)
            # Don't overwrite user-supplied headers
            extra_headers = {
                key: value
                for key, value in extra_headers.items()
                if key.lower() not in headers_keys
            }
            headers.update(extra_headers)
            if "referer" not in headers_keys:
                headers.update({"referer": generate_convincing_referer(url)})

        elif "user-agent" not in headers_keys:
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
        adaptor_arguments: Optional[Dict] = None,
    ) -> Response:
        """
        Perform an HTTP request using the configured session.

        :param method: HTTP method to be used, supported methods are ["GET", "POST", "PUT", "DELETE"]
        :param url: Target URL for the request.
        :param request_args: Arguments to be passed to the session's `request()` method.
        :param max_retries: Maximum number of retries for the request.
        :param retry_delay: Number of seconds to wait between retries.
        :param adaptor_arguments: Arguments passed when creating the final Adaptor class.
        :return: A `Response` object for synchronous requests or an awaitable for asynchronous.
        """
        if self._curl_session:
            for attempt in range(max_retries):
                try:
                    response = self._curl_session.request(method, **request_args)
                    # response.raise_for_status()  # Retry responses with a status code between 200-400
                    return ResponseFactory.from_http_request(
                        response, adaptor_arguments
                    )
                except CurlError as e:
                    if attempt < max_retries - 1:
                        log.error(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds..."
                        )
                        time_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail

        raise RuntimeError("No active session available.")

    async def __make_async_request(
        self,
        method: SUPPORTED_HTTP_METHODS,
        request_args: Dict[str, Any],
        max_retries: int,
        retry_delay: int,
        adaptor_arguments: Optional[Dict] = None,
    ) -> Response:
        """
        Perform an HTTP request using the configured session.

        :param method: HTTP method to be used, supported methods are ["GET", "POST", "PUT", "DELETE"]
        :param url: Target URL for the request.
        :param request_args: Arguments to be passed to the session's `request()` method.
        :param max_retries: Maximum number of retries for the request.
        :param retry_delay: Number of seconds to wait between retries.
        :param adaptor_arguments: Arguments passed when creating the final Adaptor class.
        :return: A `Response` object for synchronous requests or an awaitable for asynchronous.
        """
        if self._async_curl_session:
            for attempt in range(max_retries):
                try:
                    response = await self._async_curl_session.request(
                        method, **request_args
                    )
                    # response.raise_for_status()  # Retry responses with a status code between 200-400
                    return ResponseFactory.from_http_request(
                        response, adaptor_arguments
                    )
                except CurlError as e:
                    if attempt < max_retries - 1:
                        log.error(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds..."
                        )
                        await asyncio_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail

        raise RuntimeError("No active session available.")

    def __prepare_and_dispatch(
        self,
        method: SUPPORTED_HTTP_METHODS,
        stealth: Optional[bool] = None,
        **kwargs,
    ) -> Union[Response, Awaitable[Response]]:
        """
        Internal dispatcher. Prepares arguments and calls sync or async request helper.

        :param method: HTTP method to be used, supported methods are ["GET", "POST", "PUT", "DELETE"]
        :param stealth: Whether to enable the `stealthy_headers` argument to this request or not. If `None`, it defaults to the session default value.
        :param url: Target URL for the request.
        :param kwargs: Additional request-specific arguments.
        :return: A `Response` object for synchronous requests or an awaitable for asynchronous.
        """
        stealth = self.stealth if stealth is None else stealth

        adaptor_arguments = (
            kwargs.pop("adaptor_arguments", {}) or self.adaptor_arguments
        )
        max_retries = kwargs.pop("retries", self.default_retries)
        retry_delay = kwargs.pop("retry_delay", self.default_retry_delay)
        request_args = self._merge_request_args(stealth=stealth, **kwargs)
        if self._curl_session:
            return self.__make_request(
                method, request_args, max_retries, retry_delay, adaptor_arguments
            )
        elif self._async_curl_session:
            # The returned value is a Coroutine
            return self.__make_async_request(
                method, request_args, max_retries, retry_delay, adaptor_arguments
            )

        raise RuntimeError("No active session available.")

    def get(
        self,
        url: str,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Union[Response, Awaitable[Response]]:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
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
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "GET", stealth=stealthy_headers, **request_args
        )

    def post(
        self,
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Union[Dict, List]] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Union[Response, Awaitable[Response]]:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
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
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "POST", stealth=stealthy_headers, **request_args
        )

    def put(
        self,
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Union[Dict, List]] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Union[Response, Awaitable[Response]]:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
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
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "PUT", stealth=stealthy_headers, **request_args
        )

    def delete(
        self,
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Union[Dict, List]] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Union[Response, Awaitable[Response]]:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
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
            **kwargs,
        }
        return self.__prepare_and_dispatch(
            "DELETE", stealth=stealthy_headers, **request_args
        )


class FetcherClient(FetcherSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Using one session for all requests is faster than using stateless `curl_cffi.get`
        self.__enter__ = None
        self.__exit__ = None
        self.__aenter__ = None
        self.__aexit__ = None
        self._curl_session = CurlSession()


class AsyncFetcherClient:
    # Since curl_cffi doesn't support making async requests without sessions
    # And using a single session for many requests at the same time in async doesn't sit well with curl_cffi.
    # We do this

    @staticmethod
    async def get(
        url: str,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        headers: Optional[Mapping[str, Optional[str]]] = None,
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Response:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the `curl_cffi.requests.AsyncSession().request()` method.
        :return: An awaitable `Response` object.
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
            **kwargs,
        }
        async with FetcherSession(stealthy_headers=stealthy_headers) as client:
            return await client.get(**request_args)

    @staticmethod
    async def post(
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Union[Dict, List]] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Response:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the `curl_cffi.requests.AsyncSession().request()` method.
        :return: An awaitable `Response` object.
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
            **kwargs,
        }
        async with FetcherSession(stealthy_headers=stealthy_headers) as client:
            return await client.post(**request_args)

    @staticmethod
    async def put(
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Union[Dict, List]] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Response:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the `curl_cffi.requests.AsyncSession().request()` method.
        :return: An awaitable `Response` object.
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
            **kwargs,
        }
        async with FetcherSession(stealthy_headers=stealthy_headers) as client:
            return await client.put(**request_args)

    @staticmethod
    async def delete(
        url: str,
        data: Optional[Union[Dict, str]] = None,
        json: Optional[Union[Dict, List]] = None,
        headers: Optional[Mapping[str, Optional[str]]] = None,
        params: Optional[Union[Dict, List, Tuple]] = None,  # <--
        cookies: Optional[CookieTypes] = None,  # <--
        timeout: Optional[Union[int, float]] = 30,  # <--
        follow_redirects: Optional[bool] = True,  # <--
        max_redirects: Optional[int] = 30,  # <--
        retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1,  # <--
        proxies: Optional[ProxySpec] = None,  # <--
        proxy: Optional[str] = None,  # <--
        proxy_auth: Optional[Tuple[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        verify: Optional[bool] = True,  # <--
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        impersonate: Optional[BrowserTypeLiteral] = "chrome136",  # <--
        stealthy_headers: Optional[bool] = True,
        **kwargs,
    ) -> Response:
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
        :param impersonate: Browser version to impersonate. Defaults to "chrome136".
        :param stealthy_headers: If enabled for this request (default), it creates and adds real browser headers. It also referer header as if it is from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the `curl_cffi.requests.AsyncSession().request()` method.
        :return: An awaitable `Response` object.
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
            **kwargs,
        }
        async with FetcherSession(stealthy_headers=stealthy_headers) as client:
            return await client.delete(**request_args)
