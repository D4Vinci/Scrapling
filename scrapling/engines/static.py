import logging

from scrapling.core._types import Union, Optional, Dict
from .toolbelt import Response, generate_convincing_referer, generate_headers

import httpx
from httpx._models import Response as httpxResponse


class StaticEngine:
    def __init__(
            self,
            follow_redirects: bool = True,
            timeout: Optional[Union[int, float]] = None,
            adaptor_arguments: Dict = None
    ):
        self.timeout = timeout
        self.follow_redirects = bool(follow_redirects)
        self._extra_headers = generate_headers(browser_mode=False)
        self.adaptor_arguments = adaptor_arguments if adaptor_arguments else {}

    @staticmethod
    def _headers_job(headers, url, stealth):
        headers = headers or {}

        # Validate headers
        if not headers.get('user-agent') and not headers.get('User-Agent'):
            headers['User-Agent'] = generate_headers(browser_mode=False).get('User-Agent')
            logging.info(f"Can't find useragent in headers so '{headers['User-Agent']}' was used.")

        if stealth:
            extra_headers = generate_headers(browser_mode=False)
            headers.update(extra_headers)
            headers.update({'referer': generate_convincing_referer(url)})

        return headers

    def _prepare_response(self, response: httpxResponse):
        return Response(
            url=str(response.url),
            text=response.text,
            content=response.content,
            status=response.status_code,
            reason=response.reason_phrase,
            encoding=response.encoding or 'utf-8',
            cookies=dict(response.cookies),
            headers=dict(response.headers),
            request_headers=response.request.headers,
            adaptor_arguments=self.adaptor_arguments
        )

    def get(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.get(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return self._prepare_response(request)

    def post(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.post(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return self._prepare_response(request)

    def delete(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.delete(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return self._prepare_response(request)

    def put(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.put(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return self._prepare_response(request)
