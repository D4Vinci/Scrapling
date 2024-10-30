import logging
from scrapling._types import Union, Optional, Dict

from .tools import generate_convincing_referer, generate_headers

import httpx


class StaticEngine:
    def __init__(
            self,
            follow_redirects: bool = True,
            timeout: Optional[Union[int, float]] = None,
    ):
        self.timeout = timeout
        self.follow_redirects = bool(follow_redirects)
        self._extra_headers = generate_headers(browser_mode=False)

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

    def get(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.get(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return request.text

    def post(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.post(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return request.text

    def delete(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.delete(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return request.text

    def put(self, url: str, stealthy_headers: Optional[bool] = True, **kwargs: Dict):
        headers = self._headers_job(kwargs.get('headers'), url, stealthy_headers)
        request = httpx.put(url=url, headers=headers, follow_redirects=self.follow_redirects, timeout=self.timeout, **kwargs)
        return request.text
