import logging
from itertools import chain
from re import compile as re_compile

from lxml import html

from scrapling.core._types import Any, Dict, Iterable, List

# Using cache on top of a class is a brilliant way to achieve a Singleton design pattern without much code
from functools import lru_cache  # isort:skip

html_forbidden = (html.HtmlComment,)

__CLEANING_TABLE__ = str.maketrans({"\t": " ", "\n": None, "\r": None})
__CONSECUTIVE_SPACES_REGEX__ = re_compile(r" +")


@lru_cache(1, typed=True)
def setup_logger():
    """Create and configure a logger with a standard format.

    :returns: logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("scrapling")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handler to logger (if not already added)
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


log = setup_logger()


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
        return {
            k: v.strip()
            for k, v in element.attrib.items()
            if v and v.strip() and k not in forbidden
        }

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

            siblings = [
                child.tag for child in parent.iterchildren() if child != element
            ]
            if siblings:
                result.update({"siblings": tuple(siblings)})

        children = [
            child.tag
            for child in element.iterchildren()
            if not isinstance(child, html_forbidden)
        ]
        if children:
            result.update({"children": tuple(children)})

        return result

    @classmethod
    def _get_element_path(cls, element: html.HtmlElement):
        parent = element.getparent()
        return tuple(
            (element.tag,)
            if parent is None
            else (cls._get_element_path(parent) + (element.tag,))
        )


@lru_cache(128, typed=True)
def clean_spaces(string):
    string = string.translate(__CLEANING_TABLE__)
    return __CONSECUTIVE_SPACES_REGEX__.sub(" ", string)
