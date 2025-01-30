import re
import typing
from collections.abc import Mapping
from types import MappingProxyType

from orjson import dumps, loads
from w3lib.html import replace_entities as _replace_entities

from scrapling.core._types import (Dict, Iterable, List, Literal, Optional,
                                   Pattern, SupportsIndex, TypeVar, Union)
from scrapling.core.utils import _is_iterable, flatten

# Define type variable for AttributeHandler value type
_TextHandlerType = TypeVar('_TextHandlerType', bound='TextHandler')


class TextHandler(str):
    """Extends standard Python string by adding more functionality"""
    __slots__ = ()

    def __new__(cls, string):
        if isinstance(string, str):
            return super().__new__(cls, string)
        return super().__new__(cls, '')

    @typing.overload
    def __getitem__(self, key: SupportsIndex) -> 'TextHandler':
        pass

    @typing.overload
    def __getitem__(self, key: slice) -> "TextHandlers":
        pass

    def __getitem__(self, key: Union[SupportsIndex, slice]) -> Union["TextHandler", "TextHandlers"]:
        lst = super().__getitem__(key)
        if isinstance(key, slice):
            lst = [TextHandler(s) for s in lst]
            return TextHandlers(typing.cast(List[_TextHandlerType], lst))
        return typing.cast(_TextHandlerType, TextHandler(lst))

    def split(self, sep: str = None, maxsplit: SupportsIndex = -1) -> 'TextHandlers':
        return TextHandlers(
            typing.cast(List[_TextHandlerType], [TextHandler(s) for s in super().split(sep, maxsplit)])
        )

    def strip(self, chars: str = None) -> Union[str, 'TextHandler']:
        return TextHandler(super().strip(chars))

    def lstrip(self, chars: str = None) -> Union[str, 'TextHandler']:
        return TextHandler(super().lstrip(chars))

    def rstrip(self, chars: str = None) -> Union[str, 'TextHandler']:
        return TextHandler(super().rstrip(chars))

    def capitalize(self) -> Union[str, 'TextHandler']:
        return TextHandler(super().capitalize())

    def casefold(self) -> Union[str, 'TextHandler']:
        return TextHandler(super().casefold())

    def center(self, width: SupportsIndex, fillchar: str = ' ') -> Union[str, 'TextHandler']:
        return TextHandler(super().center(width, fillchar))

    def expandtabs(self, tabsize: SupportsIndex = 8) -> Union[str, 'TextHandler']:
        return TextHandler(super().expandtabs(tabsize))

    def format(self, *args: str, **kwargs: str) -> Union[str, 'TextHandler']:
        return TextHandler(super().format(*args, **kwargs))

    def format_map(self, mapping) -> Union[str, 'TextHandler']:
        return TextHandler(super().format_map(mapping))

    def join(self, iterable: Iterable[str]) -> Union[str, 'TextHandler']:
        return TextHandler(super().join(iterable))

    def ljust(self, width: SupportsIndex, fillchar: str = ' ') -> Union[str, 'TextHandler']:
        return TextHandler(super().ljust(width, fillchar))

    def rjust(self, width: SupportsIndex, fillchar: str = ' ') -> Union[str, 'TextHandler']:
        return TextHandler(super().rjust(width, fillchar))

    def swapcase(self) -> Union[str, 'TextHandler']:
        return TextHandler(super().swapcase())

    def title(self) -> Union[str, 'TextHandler']:
        return TextHandler(super().title())

    def translate(self, table) -> Union[str, 'TextHandler']:
        return TextHandler(super().translate(table))

    def zfill(self, width: SupportsIndex) -> Union[str, 'TextHandler']:
        return TextHandler(super().zfill(width))

    def replace(self, old: str, new: str, count: SupportsIndex = -1) -> Union[str, 'TextHandler']:
        return TextHandler(super().replace(old, new, count))

    def upper(self) -> Union[str, 'TextHandler']:
        return TextHandler(super().upper())

    def lower(self) -> Union[str, 'TextHandler']:
        return TextHandler(super().lower())
    ##############

    def sort(self, reverse: bool = False) -> Union[str, 'TextHandler']:
        """Return a sorted version of the string"""
        return self.__class__("".join(sorted(self, reverse=reverse)))

    def clean(self) -> Union[str, 'TextHandler']:
        """Return a new version of the string after removing all white spaces and consecutive spaces"""
        data = re.sub(r'[\t|\r|\n]', '', self)
        data = re.sub(' +', ' ', data)
        return self.__class__(data.strip())

    # For easy copy-paste from Scrapy/parsel code when needed :)
    def get(self, default=None):
        return self

    def get_all(self):
        return self

    extract = get_all
    extract_first = get

    def json(self) -> Dict:
        """Return json response if the response is jsonable otherwise throw error"""
        # Using str function as a workaround for orjson issue with subclasses of str
        # Check this out: https://github.com/ijl/orjson/issues/445
        return loads(str(self))

    @typing.overload
    def re(
        self,
        regex: Union[str, Pattern[str]],
        check_match: Literal[True],
        replace_entities: bool = True,
        clean_match: bool = False,
        case_sensitive: bool = False,
    ) -> bool:
        ...

    @typing.overload
    def re(
        self,
        regex: Union[str, Pattern[str]],
        replace_entities: bool = True,
        clean_match: bool = False,
        case_sensitive: bool = False,
        check_match: Literal[False] = False,
    ) -> "TextHandlers[TextHandler]":
        ...

    def re(
            self, regex: Union[str, Pattern[str]], replace_entities: bool = True, clean_match: bool = False,
            case_sensitive: bool = False, check_match: bool = False
    ) -> Union["TextHandlers[TextHandler]", bool]:
        """Apply the given regex to the current text and return a list of strings with the matches.

        :param regex: Can be either a compiled regular expression or a string.
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it
        :param check_match: used to quickly check if this regex matches or not without any operations on the results

        """
        if isinstance(regex, str):
            if not case_sensitive:
                regex = re.compile(regex, re.UNICODE)
            else:
                regex = re.compile(regex, flags=re.UNICODE | re.IGNORECASE)

        input_text = self.clean() if clean_match else self
        results = regex.findall(input_text)
        if check_match:
            return bool(results)

        if all(_is_iterable(res) for res in results):
            results = flatten(results)

        if not replace_entities:
            return TextHandlers(typing.cast(List[_TextHandlerType], [TextHandler(string) for string in results]))

        return TextHandlers(typing.cast(List[_TextHandlerType], [TextHandler(_replace_entities(s)) for s in results]))

    def re_first(self, regex: Union[str, Pattern[str]], default=None, replace_entities: bool = True,
                 clean_match: bool = False, case_sensitive: bool = False) -> "TextHandler":
        """Apply the given regex to text and return the first match if found, otherwise return the default value.

        :param regex: Can be either a compiled regular expression or a string.
        :param default: The default value to be returned if there is no match
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it

        """
        result = self.re(regex, replace_entities, clean_match=clean_match, case_sensitive=case_sensitive)
        return result[0] if result else default


class TextHandlers(List[TextHandler]):
    """
    The :class:`TextHandlers` class is a subclass of the builtin ``List`` class, which provides a few additional methods.
    """
    __slots__ = ()

    @typing.overload
    def __getitem__(self, pos: SupportsIndex) -> TextHandler:
        pass

    @typing.overload
    def __getitem__(self, pos: slice) -> "TextHandlers":
        pass

    def __getitem__(self, pos: Union[SupportsIndex, slice]) -> Union[TextHandler, "TextHandlers"]:
        lst = super().__getitem__(pos)
        if isinstance(pos, slice):
            lst = [TextHandler(s) for s in lst]
            return TextHandlers(typing.cast(List[_TextHandlerType], lst))
        return typing.cast(_TextHandlerType, TextHandler(lst))

    def re(self, regex: Union[str, Pattern[str]], replace_entities: bool = True, clean_match: bool = False,
            case_sensitive: bool = False) -> 'TextHandlers[TextHandler]':
        """Call the ``.re()`` method for each element in this list and return
        their results flattened as TextHandlers.

        :param regex: Can be either a compiled regular expression or a string.
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it
        """
        results = [
            n.re(regex, replace_entities, clean_match, case_sensitive) for n in self
        ]
        return TextHandlers(flatten(results))

    def re_first(self, regex: Union[str, Pattern[str]], default=None, replace_entities: bool = True,
                 clean_match: bool = False, case_sensitive: bool = False) -> TextHandler:
        """Call the ``.re_first()`` method for each element in this list and return
        the first result or the default value otherwise.

        :param regex: Can be either a compiled regular expression or a string.
        :param default: The default value to be returned if there is no match
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it
        """
        for n in self:
            for result in n.re(regex, replace_entities, clean_match, case_sensitive):
                return result
        return default

    # For easy copy-paste from Scrapy/parsel code when needed :)
    def get(self, default=None):
        """Returns the first item of the current list
        :param default: the default value to return if the current list is empty
        """
        return self[0] if len(self) > 0 else default

    def extract(self):
        return self

    extract_first = get
    get_all = extract


class AttributesHandler(Mapping[str, _TextHandlerType]):
    """A read-only mapping to use instead of the standard dictionary for the speed boost but at the same time I use it to add more functionalities.
        If standard dictionary is needed, just convert this class to dictionary with `dict` function
    """
    __slots__ = ('_data',)

    def __init__(self, mapping=None, **kwargs):
        mapping = {
            key: TextHandler(value) if type(value) is str else value
            for key, value in mapping.items()
        } if mapping is not None else {}

        if kwargs:
            mapping.update({
                key: TextHandler(value) if type(value) is str else value
                for key, value in kwargs.items()
            })

        # Fastest read-only mapping type
        self._data = MappingProxyType(mapping)

    def get(self, key: str, default: Optional[str] = None) -> Union[_TextHandlerType, None]:
        """Acts like standard dictionary `.get()` method"""
        return self._data.get(key, default)

    def search_values(self, keyword, partial=False):
        """Search current attributes by values and return dictionary of each matching item
        :param keyword: The keyword to search for in the attributes values
        :param partial: If True, the function will search if keyword in each value instead of perfect match
        """
        for key, value in self._data.items():
            if partial:
                if keyword in value:
                    yield AttributesHandler({key: value})
            else:
                if keyword == value:
                    yield AttributesHandler({key: value})

    @property
    def json_string(self):
        """Convert current attributes to JSON string if the attributes are JSON serializable otherwise throws error"""
        return dumps(dict(self._data))

    def __getitem__(self, key: str) -> _TextHandlerType:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    def __str__(self):
        return str(self._data)

    def __contains__(self, key):
        return key in self._data
