from abc import ABC
from random import choice
from time import sleep as time_sleep
from asyncio import sleep as asyncio_sleep

from curl_cffi.curl import CurlError
from curl_cffi import CurlHttpVersion
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

from .toolbelt.custom import Response
from .toolbelt.convertor import ResponseFactory
from .toolbelt.fingerprints import generate_convincing_referer, generate_headers, __default_useragent__

_UNSET: Any = object()
_NO_SESSION: Any = object()

# Type alias for `impersonate` parameter - accepts a single browser or list of browsers
ImpersonateType = BrowserTypeLiteral | List[BrowserTypeLiteral] | None


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
    ):
        self._default_impersonate = impersonate
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

    @staticmethod
    def _get_with_precedence(request_val: Any, default_val: Any) -> Any:
        """Get value with request-level priority over session-level"""
        return request_val if request_val is not _UNSET else default_val

    def _merge_request_args(self, **method_kwargs) -> Dict[str, Any]:
        """Merge request-specific arguments with default session arguments."""
        url = method_kwargs.pop("url")
        impersonate = _select_random_browser(
            self._get_with_precedence(method_kwargs.pop("impersonate"), self._default_impersonate)
        )
        http3_enabled = self._get_with_precedence(method_kwargs.pop("http3"), self._default_http3)
        final_args = {
            "url": url,
            # Curl automatically generates the suitable browser headers when you use `impersonate`
            "headers": self._headers_job(
                url,
                self._get_with_precedence(method_kwargs.pop("headers"), self._default_headers),
                self._get_with_precedence(method_kwargs.pop("stealth"), self._stealth),
                bool(impersonate),
            ),
            "proxies": self._get_with_precedence(method_kwargs.pop("proxies"), self._default_proxies),
            "proxy": self._get_with_precedence(method_kwargs.pop("proxy"), self._default_proxy),
            "proxy_auth": self._get_with_precedence(method_kwargs.pop("proxy_auth"), self._default_proxy_auth),
            "timeout": self._get_with_precedence(method_kwargs.pop("timeout"), self._default_timeout),
            "allow_redirects": self._get_with_precedence(
                method_kwargs.pop("follow_redirects"), self._default_follow_redirects
            ),
            "max_redirects": self._get_with_precedence(method_kwargs.pop("max_redirects"), self._default_max_redirects),
            "verify": self._get_with_precedence(method_kwargs.pop("verify"), self._default_verify),
            "cert": self._get_with_precedence(method_kwargs.pop("cert"), self._default_cert),
            "impersonate": impersonate,
            **{
                k: v
                for k, v in method_kwargs.items()
                if v
                not in (
                    _UNSET,
                    None,
                )
            },  # Add any remaining parameters (after all known ones are popped)
        }
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
        final_headers = {**self._default_headers, **(headers if headers and headers is not _UNSET else {})}
        headers_keys = {k.lower() for k in final_headers}
        if stealth:
            if "referer" not in headers_keys:
                final_headers["referer"] = generate_convincing_referer(url)

            if not impersonate_enabled:  # Curl will generate the suitable headers
                extra_headers = generate_headers(browser_mode=False)
                final_headers.update(
                    {k: v for k, v in extra_headers.items() if k.lower() not in headers_keys}
                )  # Don't overwrite user-supplied headers

        elif "user-agent" not in headers_keys and not impersonate_enabled:
            final_headers["User-Agent"] = __default_useragent__
            log.debug(f"Can't find useragent in headers so '{final_headers['User-Agent']}' was used.")

        return final_headers


class _SyncSessionLogic(_ConfigurationLogic):
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
    ):
        super().__init__(
            impersonate,
            http3,
            stealthy_headers,
            proxies,
            proxy,
            proxy_auth,
            timeout,
            headers,
            retries,
            retry_delay,
            follow_redirects,
            max_redirects,
            verify,
            cert,
            selector_config,
        )
        self._curl_session: Optional[CurlSession] = None

    def __enter__(self):
        """Creates and returns a new synchronous Fetcher Session"""
        if self._curl_session:
            raise RuntimeError("This FetcherSession instance already has an active synchronous session.")

        self._curl_session = CurlSession()
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

    def __make_request(
        self,
        method: SUPPORTED_HTTP_METHODS,
        stealth: Optional[bool] = None,
        **kwargs,
    ) -> Response:
        """
        Perform an HTTP request using the configured session.
        """
        stealth = self._stealth if stealth is None else stealth

        selector_config = kwargs.pop("selector_config", {}) or self.selector_config
        max_retries = self._get_with_precedence(kwargs.pop("retries"), self._default_retries)
        retry_delay = self._get_with_precedence(kwargs.pop("retry_delay"), self._default_retry_delay)
        request_args = self._merge_request_args(stealth=stealth, **kwargs)

        session = self._curl_session
        one_off_request = False
        if session is _NO_SESSION and self.__enter__ is None:
            # For usage inside FetcherClient
            # It turns out `curl_cffi` caches impersonation state, so if you turned it off, then on then off, it won't be off on the last time.
            session = CurlSession()
            one_off_request = True

        if session:
            for attempt in range(max_retries):
                try:
                    response = session.request(method, **request_args)
                    result = ResponseFactory.from_http_request(response, selector_config)
                    return result
                except CurlError as e:  # pragma: no cover
                    if attempt < max_retries - 1:
                        log.error(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                        time_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail
                finally:
                    if session and one_off_request:
                        session.close()

        raise RuntimeError("No active session available.")  # pragma: no cover

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
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
        :param impersonate: Browser version to impersonate. Automatically defaults to the latest available Chrome version.
        :param http3: Whether to use HTTP3. Defaults to False. It might be problematic if used it with `impersonate`.
        :param stealthy_headers: If enabled (default), it creates and adds real browser headers. It also sets the referer header as if this request came from a Google search of URL's domain.
        :param kwargs: Additional keyword arguments to pass to the [`curl_cffi.requests.Session().request()`, `curl_cffi.requests.AsyncSession().request()`] method.
        :return: A `Response` object.
        """
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("GET", stealth=stealthy_headers, **method_args)

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response:
        """
        Perform a POST request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
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
        :return: A `Response` object.
        """
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            data,
            json,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("POST", stealth=stealthy_headers, **method_args)

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response:
        """
        Perform a PUT request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
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
        :return: A `Response` object.
        """
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            data,
            json,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("PUT", stealth=stealthy_headers, **method_args)

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Response:
        """
        Perform a DELETE request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
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
        :return: A `Response` object.
        """
        # Careful of sending a body in a DELETE request, it might cause some websites to reject the request as per https://www.rfc-editor.org/rfc/rfc7231#section-4.3.5,
        # But some websites accept it, it depends on the implementation used.
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            data,
            json,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("DELETE", stealth=stealthy_headers, **method_args)


class _ASyncSessionLogic(_ConfigurationLogic):
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
    ):
        super().__init__(
            impersonate,
            http3,
            stealthy_headers,
            proxies,
            proxy,
            proxy_auth,
            timeout,
            headers,
            retries,
            retry_delay,
            follow_redirects,
            max_redirects,
            verify,
            cert,
            selector_config,
        )
        self._async_curl_session: Optional[AsyncCurlSession] = None

    async def __aenter__(self):
        """Creates and returns a new asynchronous Session."""
        if self._async_curl_session:
            raise RuntimeError("This FetcherSession instance already has an active asynchronous session.")

        self._async_curl_session = AsyncCurlSession()
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

    async def __make_request(
        self,
        method: SUPPORTED_HTTP_METHODS,
        stealth: Optional[bool] = None,
        **kwargs,
    ) -> Response:
        """
        Perform an HTTP request using the configured session.
        """
        stealth = self._stealth if stealth is None else stealth

        selector_config = kwargs.pop("selector_config", {}) or self.selector_config
        max_retries = self._get_with_precedence(kwargs.pop("retries"), self._default_retries)
        retry_delay = self._get_with_precedence(kwargs.pop("retry_delay"), self._default_retry_delay)
        request_args = self._merge_request_args(stealth=stealth, **kwargs)

        session = self._async_curl_session
        one_off_request = False
        if session is _NO_SESSION and self.__aenter__ is None:
            # For usage inside the ` AsyncFetcherClient ` class, and that's for several reasons
            # 1. It turns out `curl_cffi` caches impersonation state, so if you turned it off, then on then off, it won't be off on the last time.
            # 2. `curl_cffi` doesn't support making async requests without sessions
            # 3. Using a single session for many requests at the same time in async doesn't sit well with curl_cffi.
            session = AsyncCurlSession()
            one_off_request = True

        if session:
            for attempt in range(max_retries):
                try:
                    response = await session.request(method, **request_args)
                    result = ResponseFactory.from_http_request(response, selector_config)
                    return result
                except CurlError as e:  # pragma: no cover
                    if attempt < max_retries - 1:
                        log.error(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                        await asyncio_sleep(retry_delay)
                    else:
                        log.error(f"Failed after {max_retries} attempts: {e}")
                        raise  # Raise the exception if all retries fail
                finally:
                    if session and one_off_request:
                        await session.close()

        raise RuntimeError("No active session available.")  # pragma: no cover

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Awaitable[Response]:
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
        :return: A `Response` object.
        """
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("GET", stealth=stealthy_headers, **method_args)

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Awaitable[Response]:
        """
        Perform a POST request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
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
        :return: A `Response` object.
        """
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            data,
            json,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("POST", stealth=stealthy_headers, **method_args)

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Awaitable[Response]:
        """
        Perform a PUT request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
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
        :return: A `Response` object.
        """
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            data,
            json,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("PUT", stealth=stealthy_headers, **method_args)

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
        impersonate: ImpersonateType = _UNSET,
        http3: Optional[bool] = _UNSET,
        stealthy_headers: Optional[bool] = _UNSET,
        **kwargs,
    ) -> Awaitable[Response]:
        """
        Perform a DELETE request.

        :param url: Target URL for the request.
        :param data: Form data to include in the request body.
        :param json: A JSON serializable object to include in the body of the request.
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
        :return: A `Response` object.
        """
        # Careful of sending a body in a DELETE request, it might cause some websites to reject the request as per https://www.rfc-editor.org/rfc/rfc7231#section-4.3.5,
        # But some websites accept it, it depends on the implementation used.
        method_args = {k: v for k, v in locals().items() if k not in ("self", "stealthy_headers", "kwargs")}
        method_args.update(kwargs)
        # For type checking (not accessed error)
        _ = (
            url,
            params,
            headers,
            data,
            json,
            cookies,
            timeout,
            follow_redirects,
            max_redirects,
            retries,
            retry_delay,
            proxies,
            proxy,
            proxy_auth,
            auth,
            verify,
            cert,
            impersonate,
            http3,
        )
        return self.__make_request("DELETE", stealth=stealthy_headers, **method_args)


class FetcherSession:
    """
    A factory context manager that provides configured Fetcher sessions.

    When this manager is used in a 'with' or 'async with' block,
    it yields a new session configured with the manager's defaults.
    A single instance of this manager should ideally be used for one active
    session at a time (or sequentially). Re-entering a context with the
    same manager instance while a session is already active is disallowed.
    """

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
        self._client: _SyncSessionLogic | _ASyncSessionLogic | None = None

    def __enter__(self) -> _SyncSessionLogic:
        """Creates and returns a new synchronous Fetcher Session"""
        if self._client is None:
            # Use **vars(self) to avoid repeating all parameters
            config = {k.replace("_default_", ""): v for k, v in vars(self).items() if k.startswith("_default")}
            config["stealthy_headers"] = self._stealth
            config["selector_config"] = self.selector_config
            self._client = _SyncSessionLogic(**config)
            return self._client.__enter__()
        raise RuntimeError("This FetcherSession instance already has an active synchronous session.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None and isinstance(self._client, _SyncSessionLogic):
            self._client.__exit__(exc_type, exc_val, exc_tb)
            self._client = None
            return
        raise RuntimeError("Cannot exit invalid session")

    async def __aenter__(self) -> _ASyncSessionLogic:
        """Creates and returns a new asynchronous Session."""
        if self._client is None:
            # Use **vars(self) to avoid repeating all parameters
            config = {k.replace("_default_", ""): v for k, v in vars(self).items() if k.startswith("_default")}
            config["stealthy_headers"] = self._stealth
            config["selector_config"] = self.selector_config
            self._client = _ASyncSessionLogic(**config)
            return await self._client.__aenter__()
        raise RuntimeError("This FetcherSession instance already has an active asynchronous session.")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None and isinstance(self._client, _ASyncSessionLogic):
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            self._client = None
            return
        raise RuntimeError("Cannot exit invalid session")


class FetcherClient(_SyncSessionLogic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__enter__: Any = None
        self.__exit__: Any = None
        self._curl_session: Any = _NO_SESSION


class AsyncFetcherClient(_ASyncSessionLogic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__aenter__: Any = None
        self.__aexit__: Any = None
        self._async_curl_session: Any = _NO_SESSION
