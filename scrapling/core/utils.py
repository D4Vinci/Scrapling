import re
import logging
from itertools import chain
# Using cache on top of a class is brilliant way to achieve Singleton design pattern without much code
from functools import lru_cache as cache  # functools.cache is available on Python 3.9+ only so let's keep lru_cache

from scrapling.core._types import Dict, Iterable, Any, Union

import orjson
from lxml import html

html_forbidden = {html.HtmlComment, }
logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


def is_jsonable(content: Union[bytes, str]) -> bool:
    if type(content) is bytes:
        content = content.decode()

    try:
        _ = orjson.loads(content)
        return True
    except orjson.JSONDecodeError:
        return False


@cache(None, typed=True)
def setup_basic_logging(level: str = 'debug'):
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    lvl = levels[level.lower()]
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    # Configure the root logger
    logging.basicConfig(level=lvl, handlers=[handler])


def flatten(lst: Iterable):
    return list(chain.from_iterable(lst))


def _is_iterable(s: Any):
    # This will be used only in regex functions to make sure it's iterable but not string/bytes
    return isinstance(s, (list, tuple,))


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
            'tag': str(element.tag),
            'attributes': cls.__clean_attributes(element),
            'text': element.text.strip() if element.text else None,
            'path': cls._get_element_path(element)
        }
        if parent is not None:
            result.update({
                'parent_name': parent.tag,
                'parent_attribs': dict(parent.attrib),
                'parent_text': parent.text.strip() if parent.text else None
            })

            siblings = [child.tag for child in parent.iterchildren() if child != element]
            if siblings:
                result.update({'siblings': tuple(siblings)})

        children = [child.tag for child in element.iterchildren() if type(child) not in html_forbidden]
        if children:
            result.update({'children': tuple(children)})

        return result

    @classmethod
    def _get_element_path(cls, element: html.HtmlElement):
        parent = element.getparent()
        return tuple(
            (element.tag,) if parent is None else (
                    cls._get_element_path(parent) + (element.tag,)
            )
        )


# def _root_type_verifier(method):
#     # Just to make sure we are safe
#     @wraps(method)
#     def _impl(self, *args, **kw):
#         # All html types inherits from HtmlMixin so this to check for all at once
#         if not issubclass(type(self._root), html.HtmlMixin):
#             raise ValueError(f"Cannot use function on a Node of type {type(self._root)!r}")
#         return method(self, *args, **kw)
#     return _impl


@cache(None, typed=True)
def clean_spaces(string):
    string = string.replace('\t', ' ')
    string = re.sub('[\n|\r]', '', string)
    return re.sub(' +', ' ', string)
