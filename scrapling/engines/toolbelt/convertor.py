from functools import lru_cache
from re import compile as re_compile

from curl_cffi.requests import Response as CurlResponse
from playwright._impl._errors import Error as PlaywrightError
from playwright.sync_api import Page as SyncPage, Response as SyncResponse
from playwright.async_api import Page as AsyncPage, Response as AsyncResponse

from scrapling.core.utils import log
from .custom import Response, StatusText
from scrapling.core._types import Dict, Optional

__CHARSET_RE__ = re_compile(r"charset=([\w-]+)")


class ResponseFactory:
    """
    Factory class for creating `Response` objects from various sources.

    This class provides multiple static and instance methods for building standardized `Response` objects
    from diverse input sources such as Playwright responses, asynchronous Playwright responses,
    and raw HTTP request responses. It supports handling response histories, constructing the proper
    response objects, and managing encoding, headers, cookies, and other attributes.
    """

    @classmethod
    @lru_cache(maxsize=16)
    def __extract_browser_encoding(cls, content_type: str | None, default: str = "utf-8") -> str:
        """Extract browser encoding from headers.
        Ex: from header "content-type: text/html; charset=utf-8" -> "utf-8
        """
        if content_type:
            # Because Playwright can't do that by themselves like all libraries for some reason :3
            match = __CHARSET_RE__.search(content_type)
            return match.group(1) if match else default
        return default

    @classmethod
    def _process_response_history(cls, first_response: SyncResponse, parser_arguments: Dict) -> list[Response]:
        """Process response history to build a list of `Response` objects"""
        history = []
        current_request = first_response.request.redirected_from

        try:
            while current_request:
                try:
                    current_response = current_request.response()
                    history.insert(
                        0,
                        Response(
                            **{
                                "url": current_request.url,
                                # using current_response.text() will trigger "Error: Response.text: Response body is unavailable for redirect responses"
                                "content": "",
                                "status": current_response.status if current_response else 301,
                                "reason": (current_response.status_text or StatusText.get(current_response.status))
                                if current_response
                                else StatusText.get(301),
                                "encoding": cls.__extract_browser_encoding(
                                    current_response.headers.get("content-type", "")
                                )
                                if current_response
                                else "utf-8",
                                "cookies": tuple(),
                                "headers": current_response.all_headers() if current_response else {},
                                "request_headers": current_request.all_headers(),
                                **parser_arguments,
                            }
                        ),
                    )
                except Exception as e:  # pragma: no cover
                    log.error(f"Error processing redirect: {e}")
                    break

                current_request = current_request.redirected_from
        except Exception as e:  # pragma: no cover
            log.error(f"Error processing response history: {e}")

        return history

    @classmethod
    def from_playwright_response(
        cls,
        page: SyncPage,
        first_response: SyncResponse,
        final_response: Optional[SyncResponse],
        parser_arguments: Dict,
    ) -> Response:
        """
        Transforms a Playwright response into an internal `Response` object, encapsulating
        the page's content, response status, headers, and relevant metadata.

        The function handles potential issues, such as empty or missing final responses,
        by falling back to the first response if necessary. Encoding and status text
        are also derived from the provided response headers or reasonable defaults.
        Additionally, the page content and cookies are extracted for further use.

        :param page: A synchronous Playwright `Page` instance that represents the current browser page. Required to retrieve the page's URL, cookies, and content.
        :param final_response: The last response received for the given request from the Playwright instance. Typically used as the main response object to derive status, headers, and other metadata.
        :param first_response: An earlier or initial Playwright `Response` object that may serve as a fallback response in the absence of the final one.
        :param parser_arguments: A dictionary containing additional arguments needed for parsing or further customization of the returned `Response`. These arguments are dynamically unpacked into
            the `Response` object.

        :return: A fully populated `Response` object containing the page's URL, content, status, headers, cookies, and other derived metadata.
        :rtype: Response
        """
        # In case we didn't catch a document type somehow
        final_response = final_response if final_response else first_response
        if not final_response:
            raise ValueError("Failed to get a response from the page")

        encoding = cls.__extract_browser_encoding(final_response.headers.get("content-type", ""))
        # PlayWright API sometimes give empty status text for some reason!
        status_text = final_response.status_text or StatusText.get(final_response.status)

        history = cls._process_response_history(first_response, parser_arguments)
        try:
            page_content = cls._get_page_content(page)
        except Exception as e:  # pragma: no cover
            log.error(f"Error getting page content: {e}")
            page_content = ""

        return Response(
            **{
                "url": page.url,
                "content": page_content,
                "raw_response": final_response.text(),
                "status": final_response.status,
                "reason": status_text,
                "encoding": encoding,
                "cookies": tuple(dict(cookie) for cookie in page.context.cookies()),
                "headers": first_response.all_headers(),
                "request_headers": first_response.request.all_headers(),
                "history": history,
                **parser_arguments,
            }
        )

    @classmethod
    async def _async_process_response_history(
        cls, first_response: AsyncResponse, parser_arguments: Dict
    ) -> list[Response]:
        """Process response history to build a list of `Response` objects"""
        history = []
        current_request = first_response.request.redirected_from

        try:
            while current_request:
                try:
                    current_response = await current_request.response()
                    history.insert(
                        0,
                        Response(
                            **{
                                "url": current_request.url,
                                # using current_response.text() will trigger "Error: Response.text: Response body is unavailable for redirect responses"
                                "content": "",
                                "status": current_response.status if current_response else 301,
                                "reason": (current_response.status_text or StatusText.get(current_response.status))
                                if current_response
                                else StatusText.get(301),
                                "encoding": cls.__extract_browser_encoding(
                                    current_response.headers.get("content-type", "")
                                )
                                if current_response
                                else "utf-8",
                                "cookies": tuple(),
                                "headers": await current_response.all_headers() if current_response else {},
                                "request_headers": await current_request.all_headers(),
                                **parser_arguments,
                            }
                        ),
                    )
                except Exception as e:  # pragma: no cover
                    log.error(f"Error processing redirect: {e}")
                    break

                current_request = current_request.redirected_from
        except Exception as e:  # pragma: no cover
            log.error(f"Error processing response history: {e}")

        return history

    @classmethod
    def _get_page_content(cls, page: SyncPage) -> str:
        """
        A workaround for the Playwright issue with `page.content()` on Windows. Ref.: https://github.com/microsoft/playwright/issues/16108
        :param page: The page to extract content from.
        :return:
        """
        while True:
            try:
                return page.content() or ""
            except PlaywrightError:
                page.wait_for_timeout(500)
                continue
        return ""  # pyright: ignore

    @classmethod
    async def _get_async_page_content(cls, page: AsyncPage) -> str:
        """
        A workaround for the Playwright issue with `page.content()` on Windows. Ref.: https://github.com/microsoft/playwright/issues/16108
        :param page: The page to extract content from.
        :return:
        """
        while True:
            try:
                return (await page.content()) or ""
            except PlaywrightError:
                await page.wait_for_timeout(500)
                continue
        return ""  # pyright: ignore

    @classmethod
    async def from_async_playwright_response(
        cls,
        page: AsyncPage,
        first_response: AsyncResponse,
        final_response: Optional[AsyncResponse],
        parser_arguments: Dict,
    ) -> Response:
        """
        Transforms a Playwright response into an internal `Response` object, encapsulating
        the page's content, response status, headers, and relevant metadata.

        The function handles potential issues, such as empty or missing final responses,
        by falling back to the first response if necessary. Encoding and status text
        are also derived from the provided response headers or reasonable defaults.
        Additionally, the page content and cookies are extracted for further use.

        :param page: An asynchronous Playwright `Page` instance that represents the current browser page. Required to retrieve the page's URL, cookies, and content.
        :param final_response: The last response received for the given request from the Playwright instance. Typically used as the main response object to derive status, headers, and other metadata.
        :param first_response: An earlier or initial Playwright `Response` object that may serve as a fallback response in the absence of the final one.
        :param parser_arguments: A dictionary containing additional arguments needed for parsing or further customization of the returned `Response`. These arguments are dynamically unpacked into
            the `Response` object.

        :return: A fully populated `Response` object containing the page's URL, content, status, headers, cookies, and other derived metadata.
        :rtype: Response
        """
        # In case we didn't catch a document type somehow
        final_response = final_response if final_response else first_response
        if not final_response:
            raise ValueError("Failed to get a response from the page")

        encoding = cls.__extract_browser_encoding(final_response.headers.get("content-type", ""))
        # PlayWright API sometimes give empty status text for some reason!
        status_text = final_response.status_text or StatusText.get(final_response.status)

        history = await cls._async_process_response_history(first_response, parser_arguments)
        try:
            page_content = await cls._get_async_page_content(page)
        except Exception as e:  # pragma: no cover
            log.error(f"Error getting page content in async: {e}")
            page_content = ""

        return Response(
            **{
                "url": page.url,
                "content": page_content,
                "status": final_response.status,
                "raw_response": await final_response.text(),
                "reason": status_text,
                "encoding": encoding,
                "cookies": tuple(dict(cookie) for cookie in await page.context.cookies()),
                "headers": await first_response.all_headers(),
                "request_headers": await first_response.request.all_headers(),
                "history": history,
                **parser_arguments,
            }
        )

    @staticmethod
    def from_http_request(response: CurlResponse, parser_arguments: Dict) -> Response:
        """Takes `curl_cffi` response and generates `Response` object from it.

        :param response: `curl_cffi` response object
        :param parser_arguments: Additional arguments to be passed to the `Response` object constructor.
        :return: A `Response` object that is the same as `Selector` object except it has these added attributes: `status`, `reason`, `cookies`, `headers`, and `request_headers`
        """
        return Response(
            **{
                "url": response.url,
                "content": response.content,
                "status": response.status_code,
                "reason": response.reason,
                "encoding": response.encoding or "utf-8",
                "cookies": dict(response.cookies),
                "headers": dict(response.headers),
                "request_headers": dict(response.request.headers) if response.request else {},
                "method": response.request.method if response.request else "GET",
                "history": response.history,  # https://github.com/lexiforest/curl_cffi/issues/82
                **parser_arguments,
            }
        )
