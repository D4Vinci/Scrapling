import httpx
from httpx._models import Response as httpxResponse

from scrapling.core._types import Dict, Optional, Tuple, Union
from scrapling.core.utils import log, lru_cache

from .toolbelt import Response, generate_convincing_referer, generate_headers


@lru_cache(typed=True)
class StaticEngine:
    def __init__(
            self, url: str, proxy: Optional[str] = None, stealthy_headers: Optional[bool] = True, follow_redirects: bool = True,
            timeout: Optional[Union[int, float]] = None, retries: Optional[int] = 3, adaptor_arguments: Tuple = None
    ):
        """An engine that utilizes httpx library, check the `Fetcher` class for more documentation.

        :param url: Target url.
        :param stealthy_headers: If enabled (default), Fetcher will create and add real browser's headers and
            create a referer header as if this request had came from Google's search of this URL's domain.
        :param proxy: A string of a proxy to use for http and https requests, the format accepted is `http://username:password@localhost:8030`
        :param follow_redirects: As the name says -- if enabled (default), redirects will be followed.
        :param timeout: The time to wait for the request to finish in seconds. The default is 10 seconds.
        :param adaptor_arguments: The arguments that will be passed in the end while creating the final Adaptor's class.
        """
        self.url = url
        self.proxy = proxy
        self.stealth = stealthy_headers
        self.timeout = timeout
        self.follow_redirects = bool(follow_redirects)
        self.retries = retries
        self._extra_headers = generate_headers(browser_mode=False)
        # Because we are using `lru_cache` for a slight optimization but both dict/dict_items are not hashable so they can't be cached
        # So my solution here was to convert it to tuple then convert it back to dictionary again here as tuples are hashable, ofc `tuple().__hash__()`
        self.adaptor_arguments = dict(adaptor_arguments) if adaptor_arguments else {}

    def _headers_job(self, headers: Optional[Dict]) -> Dict:
        """Adds useragent to headers if it doesn't exist, generates real headers and append it to current headers, and
            finally generates a referer header that looks like if this request came from Google's search of the current URL's domain.

        :param headers: Current headers in the request if the user passed any
        :return: A dictionary of the new headers.
        """
        headers = headers or {}

        # Validate headers
        if not headers.get('user-agent') and not headers.get('User-Agent'):
            headers['User-Agent'] = generate_headers(browser_mode=False).get('User-Agent')
            log.debug(f"Can't find useragent in headers so '{headers['User-Agent']}' was used.")

        if self.stealth:
            extra_headers = generate_headers(browser_mode=False)
            headers.update(extra_headers)
            headers.update({'referer': generate_convincing_referer(self.url)})

        return headers

    def _prepare_response(self, response: httpxResponse) -> Response:
        """Takes httpx response and generates `Response` object from it.

        :param response: httpx response object
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        return Response(
            url=str(response.url),
            text=response.text,
            body=response.content,
            status=response.status_code,
            reason=response.reason_phrase,
            encoding=response.encoding or 'utf-8',
            cookies=dict(response.cookies),
            headers=dict(response.headers),
            request_headers=dict(response.request.headers),
            method=response.request.method,
            **self.adaptor_arguments
        )

    def get(self, **kwargs: Dict) -> Response:
        """Make basic HTTP GET request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.get()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        with httpx.Client(proxy=self.proxy, transport=httpx.HTTPTransport(retries=self.retries)) as client:
            request = client.get(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    async def async_get(self, **kwargs: Dict) -> Response:
        """Make basic async HTTP GET request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.get()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            request = await client.get(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    def post(self, **kwargs: Dict) -> Response:
        """Make basic HTTP POST request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.post()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        with httpx.Client(proxy=self.proxy, transport=httpx.HTTPTransport(retries=self.retries)) as client:
            request = client.post(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    async def async_post(self, **kwargs: Dict) -> Response:
        """Make basic async HTTP POST request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.post()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            request = await client.post(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    def delete(self, **kwargs: Dict) -> Response:
        """Make basic HTTP DELETE request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.delete()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        with httpx.Client(proxy=self.proxy, transport=httpx.HTTPTransport(retries=self.retries)) as client:
            request = client.delete(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    async def async_delete(self, **kwargs: Dict) -> Response:
        """Make basic async HTTP DELETE request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.delete()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            request = await client.delete(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    def put(self, **kwargs: Dict) -> Response:
        """Make basic HTTP PUT request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.put()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        with httpx.Client(proxy=self.proxy, transport=httpx.HTTPTransport(retries=self.retries)) as client:
            request = client.put(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)

    async def async_put(self, **kwargs: Dict) -> Response:
        """Make basic async HTTP PUT request for you but with some added flavors.

        :param kwargs: Any keyword arguments are passed directly to `httpx.put()` function so check httpx documentation for details.
        :return: A `Response` object that is the same as `Adaptor` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        headers = self._headers_job(kwargs.pop('headers', {}))
        async with httpx.AsyncClient(proxy=self.proxy) as client:
            request = await client.put(url=self.url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)

        return self._prepare_response(request)
