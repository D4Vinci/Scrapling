import logging
from itertools import chain
from re import compile as re_compile
from contextvars import ContextVar, Token

from lxml import html

from scrapling.core._types import Any, Dict, Iterable, List

# Using cache on top of a class is a brilliant way to achieve a Singleton design pattern without much code
from functools import lru_cache  # isort:skip

html_forbidden = (html.HtmlComment,)

__CLEANING_TABLE__ = str.maketrans("\t\r\n", "   ")
__CONSECUTIVE_SPACES_REGEX__ = re_compile(r" +")


@lru_cache(1, typed=True)
def setup_logger():
    """Create Scrapling's library logger without forcing application logging config."""
    logger = logging.getLogger("scrapling")
    if not any(isinstance(handler, logging.NullHandler) for handler in logger.handlers):
        logger.addHandler(logging.NullHandler())
    return logger


_current_logger: ContextVar[logging.Logger] = ContextVar("scrapling_logger", default=setup_logger())


class LoggerProxy:
    def __getattr__(self, name: str):
        return getattr(_current_logger.get(), name)


log = LoggerProxy()


def set_logger(logger: logging.Logger) -> Token:
    """Set the current context logger. Returns token for reset."""
    return _current_logger.set(logger)


def reset_logger(token: Token) -> None:
    """Reset logger to previous state using token."""
    _current_logger.reset(token)


def flatten(lst: Iterable[Any]) -> List[Any]:
    return list(chain.from_iterable(lst))


def _is_iterable(obj: Any) -> bool:
    # This will be used only in regex functions to make sure it's iterable but not string/bytes
    return isinstance(
        obj,
        (
            list,
            tuple,
        ),
    )


class _StorageTools:
    @staticmethod
    def __clean_attributes(element: html.HtmlElement, forbidden: tuple = ()) -> Dict:
        if not element.attrib:
            return {}
        return {k: v.strip() for k, v in element.attrib.items() if v and v.strip() and k not in forbidden}

    @classmethod
    def element_to_dict(cls, element: html.HtmlElement) -> Dict:
        parent = element.getparent()
        result = {
            "tag": str(element.tag),
            "attributes": cls.__clean_attributes(element),
            "text": element.text.strip() if element.text else None,
            "path": cls._get_element_path(element),
        }
        if parent is not None:
            result.update(
                {
                    "parent_name": parent.tag,
                    "parent_attribs": dict(parent.attrib),
                    "parent_text": parent.text.strip() if parent.text else None,
                }
            )

            siblings = [child.tag for child in parent.iterchildren() if child != element]
            if siblings:
                result.update({"siblings": tuple(siblings)})

        children = [child.tag for child in element.iterchildren() if not isinstance(child, html_forbidden)]
        if children:
            result.update({"children": tuple(children)})

        return result

    @classmethod
    def _get_element_path(cls, element: html.HtmlElement):
        parts = []
        current = element
        while current is not None:
            parts.append(current.tag)
            current = current.getparent()
        return tuple(reversed(parts))


@lru_cache(128, typed=True)
def clean_spaces(string: str) -> str:
    string = string.translate(__CLEANING_TABLE__)
    return __CONSECUTIVE_SPACES_REGEX__.sub(" ", string)
