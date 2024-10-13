import re
import os
import logging
from itertools import chain
from logging import handlers
# Using cache on top of a class is brilliant way to achieve Singleton design pattern without much code
from functools import lru_cache as cache  # functools.cache is available on Python 3.9+ only so let's keep lru_cache

from typing import Dict, Iterable, Any

from lxml import html
html_forbidden = {html.HtmlComment, }
logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


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


@cache(None, typed=True)
class _Logger(object):
    # I will leave this class here for now in case I decide I want to come back to use it :)
    __slots__ = ('console_logger', 'logger_file_path',)
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, filename: str = 'debug.log', level: str = 'debug', when: str = 'midnight', backcount: int = 1):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)
        format_str = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

        # on-screen output
        lvl = self.levels[level.lower()]
        self.console_logger = logging.getLogger('Scrapling')
        self.console_logger.setLevel(lvl)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(lvl)
        console_handler.setFormatter(format_str)
        self.console_logger.addHandler(console_handler)

        if lvl == logging.DEBUG:
            filename = os.path.join(os.path.dirname(__file__), 'logs', filename)
            self.logger_file_path = filename
            # Automatically generates the logging file at specified intervals
            file_handler = handlers.TimedRotatingFileHandler(
                # If more than (backcount+1) existed, oldest logs will be deleted
                filename=filename, when=when, backupCount=backcount, encoding='utf-8'
            )
            file_handler.setLevel(lvl)
            file_handler.setFormatter(format_str)
            # This for the logger when it appends the date to the new log
            file_handler.namer = lambda name: name.replace(".log", "") + ".log"
            self.console_logger.addHandler(file_handler)
            self.debug(f'Debug log path: {self.logger_file_path}')
        else:
            self.logger_file_path = None

    def debug(self, message: str) -> None:
        self.console_logger.debug(message)

    def info(self, message: str) -> None:
        self.console_logger.info(message)

    def warning(self, message: str) -> None:
        self.console_logger.warning(message)

    def error(self, message: str) -> None:
        self.console_logger.error(message)

    def critical(self, message: str) -> None:
        self.console_logger.critical(message)


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
