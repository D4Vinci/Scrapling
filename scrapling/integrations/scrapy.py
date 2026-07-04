"""Scrapy integration.

Decorate Scrapy spider callbacks with `scrapling_response` to receive a Scrapling `Response`
object instead of the Scrapy response, so you get Scrapling's full parsing API inside existing
Scrapy projects without changing how the spider crawls.
"""

from functools import partial, wraps
from inspect import isasyncgenfunction, iscoroutinefunction, isgeneratorfunction

from scrapling.core._types import Any, Callable, Dict, Optional, Tuple
from scrapling.engines.toolbelt.custom import Response, StatusText

try:
    from scrapy.http import Response as ScrapyResponse
except (ImportError, ModuleNotFoundError) as e:
    raise ModuleNotFoundError(
        "This integration requires Scrapy installed, please install it first with `pip install scrapy`"
    ) from e

__all__ = ["scrapling_response", "convert_response"]


def convert_response(response: ScrapyResponse, **selector_config: Any) -> Response:
    """Convert a Scrapy response to a Scrapling `Response` object.

    Can be used directly anywhere you have a Scrapy response at hand (middlewares, pipelines, ...).

    :param response: The Scrapy response to convert.
    :param selector_config: Configuration options passed to the `Response` constructor, like
        `huge_tree`, `keep_comments`, `keep_cdata`, `adaptive`, `storage`, `storage_args`, and `adaptive_domain`.
    :return: A Scrapling `Response` object ready for parsing.
    """
    request = response.request
    cookies: Dict[str, str] = {}
    # `to_unicode_dict` below joins duplicate headers with commas, which corrupts multiple
    # `Set-Cookie` headers, so cookies are parsed from the raw header lines instead.
    for line in response.headers.getlist(b"Set-Cookie"):
        pair = line.split(b";", 1)[0]
        if b"=" in pair:
            name, _, value = pair.decode("latin-1").partition("=")
            cookies[name.strip()] = value.strip()

    return Response(
        url=response.url,
        content=response.body,
        status=response.status,
        reason=StatusText.get(response.status),
        cookies=cookies,
        headers=dict(response.headers.to_unicode_dict()),
        request_headers=dict(request.headers.to_unicode_dict()) if request else {},
        encoding=getattr(response, "encoding", "utf-8"),  # Binary responses don't have an encoding
        method=request.method if request else "GET",
        meta=dict(response.meta) if request else {},  # `meta` raises AttributeError without a request
        **selector_config,
    )


def scrapling_response(func: Optional[Callable] = None, **selector_config: Any) -> Callable:
    """Decorator that converts the Scrapy response passed to a spider callback into a Scrapling `Response`.

    Works bare or parameterized, on any callback kind Scrapy supports (regular, generator,
    coroutine, and async generator functions)::

        class MySpider(scrapy.Spider):
            @scrapling_response
            def parse(self, response):  # `response` is a Scrapling Response
                product = response.find_by_text("Vans Old Skool", partial=True)
                for similar in product.find_similar():
                    yield {"name": similar.get_all_text(strip=True)}

            @scrapling_response(adaptive=True)
            def parse_product(self, response):
                ...

    :param func: The decorated callback. Left empty in the parameterized form.
    :param selector_config: Configuration options passed to the `Response` constructor, like
        `huge_tree`, `keep_comments`, `keep_cdata`, `adaptive`, `storage`, `storage_args`, and `adaptive_domain`.
    :return: The wrapped callback. The wrapper keeps the callback's kind, name, and docstring,
        so Scrapy's callback introspection keeps working.
    """
    if func is None:
        return partial(scrapling_response, **selector_config)

    def _convert_arguments(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        converted = list(args)
        for index, argument in enumerate(converted):
            if isinstance(argument, ScrapyResponse):
                converted[index] = convert_response(argument, **selector_config)
                return tuple(converted), kwargs

        for key, value in kwargs.items():
            if isinstance(value, ScrapyResponse):
                kwargs[key] = convert_response(value, **selector_config)
                return tuple(converted), kwargs

        raise TypeError(f"No Scrapy response found in the arguments of '{getattr(func, '__name__', func)}'")

    # Each callback kind gets a wrapper of the same kind because Scrapy inspects the callback
    # function itself, not just what it returns.
    if isasyncgenfunction(func):

        @wraps(func)
        async def async_gen_wrapper(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = _convert_arguments(args, kwargs)
            async for result in func(*args, **kwargs):
                yield result

        return async_gen_wrapper

    elif iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = _convert_arguments(args, kwargs)
            return await func(*args, **kwargs)

        return async_wrapper

    elif isgeneratorfunction(func):

        @wraps(func)
        def gen_wrapper(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = _convert_arguments(args, kwargs)
            yield from func(*args, **kwargs)

        return gen_wrapper

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        args, kwargs = _convert_arguments(args, kwargs)
        return func(*args, **kwargs)

    return wrapper
