from pathlib import Path
import re
from inspect import signature
from difflib import SequenceMatcher
from urllib.parse import urljoin

from cssselect import SelectorError, SelectorSyntaxError
from cssselect import parse as split_selectors
from lxml.html import HtmlElement, HtmlMixin, HTMLParser
from lxml.etree import (
    XPath,
    tostring,
    fromstring,
    XPathError,
    XPathEvalError,
    _ElementUnicodeResult,
)

from scrapling.core._types import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    Pattern,
    Callable,
    Optional,
    Iterable,
    overload,
    Generator,
    SupportsIndex,
)
from scrapling.core.custom_types import AttributesHandler, TextHandler, TextHandlers
from scrapling.core.mixins import SelectorsGeneration
from scrapling.core.storage import (
    SQLiteStorageSystem,
    StorageSystemMixin,
    _StorageTools,
)
from scrapling.core.translator import translator as _translator
from scrapling.core.utils import clean_spaces, flatten, html_forbidden, log

__DEFAULT_DB_FILE__ = str(Path(__file__).parent / "elements_storage.db")
# Attributes that are Python reserved words and can't be used directly
# Ex: find_all('a', class="blah") -> find_all('a', class_="blah")
# https://www.w3schools.com/python/python_ref_keywords.asp
_whitelisted = {
    "class_": "class",
    "for_": "for",
}
# Pre-compiled selectors for efficiency
_find_all_elements = XPath(".//*")
_find_all_elements_with_spaces = XPath(
    ".//*[normalize-space(text())]"
)  # This selector gets all elements with text content


class Selector(SelectorsGeneration):
    __slots__ = (
        "url",
        "encoding",
        "__adaptive_enabled",
        "_root",
        "_storage",
        "__keep_comments",
        "__huge_tree_enabled",
        "__attributes",
        "__text",
        "__tag",
        "__keep_cdata",
        "_raw_body",
    )

    def __init__(
        self,
        content: Optional[str | bytes] = None,
        url: Optional[str] = None,
        encoding: str = "utf8",
        huge_tree: bool = True,
        root: Optional[HtmlElement] = None,
        keep_comments: Optional[bool] = False,
        keep_cdata: Optional[bool] = False,
        adaptive: Optional[bool] = False,
        _storage: object = None,
        storage: Any = SQLiteStorageSystem,
        storage_args: Optional[Dict] = None,
        **kwargs,
    ):
        """The main class that works as a wrapper for the HTML input data. Using this class, you can search for elements
        with expressions in CSS, XPath, or with simply text. Check the docs for more info.

        Here we try to extend module ``lxml.html.HtmlElement`` while maintaining a simpler interface, We are not
        inheriting from the ``lxml.html.HtmlElement`` because it's not pickleable, which makes a lot of reference jobs
        not possible. You can test it here and see code explodes with `AssertionError: invalid Element proxy at...`.
        It's an old issue with lxml, see `this entry <https://bugs.launchpad.net/lxml/+bug/736708>`

        :param content: HTML content as either string or bytes.
        :param url: It allows storing a URL with the HTML data for retrieving later.
        :param encoding: The encoding type that will be used in HTML parsing, default is `UTF-8`
        :param huge_tree: Enabled by default, should always be enabled when parsing large HTML documents. This controls
             the libxml2 feature that forbids parsing certain large documents to protect from possible memory exhaustion.
        :param root: Used internally to pass etree objects instead of text/body arguments, it takes the highest priority.
            Don't use it unless you know what you are doing!
        :param keep_comments: While parsing the HTML body, drop comments or not. Disabled by default for obvious reasons
        :param keep_cdata: While parsing the HTML body, drop cdata or not. Disabled by default for cleaner HTML.
        :param adaptive: Globally turn off the adaptive feature in all functions, this argument takes higher
            priority over all adaptive related arguments/functions in the class.
        :param storage: The storage class to be passed for adaptive functionalities, see ``Docs`` for more info.
        :param storage_args: A dictionary of ``argument->value`` pairs to be passed for the storage class.
            If empty, default values will be used.
        """
        if root is None and content is None:
            raise ValueError(
                "Selector class needs HTML content, or root arguments to work"
            )

        self.__text = None
        if root is None:
            if isinstance(content, str):
                body = (
                    content.strip().replace("\x00", "").encode(encoding) or b"<html/>"
                )
            elif isinstance(content, bytes):
                body = content.replace(b"\x00", b"").strip()
            else:
                raise TypeError(
                    f"content argument must be str or bytes, got {type(content)}"
                )

            # https://lxml.de/api/lxml.etree.HTMLParser-class.html
            parser = HTMLParser(
                recover=True,
                remove_blank_text=True,
                remove_comments=(not keep_comments),
                encoding=encoding,
                compact=True,
                huge_tree=huge_tree,
                default_doctype=True,
                strip_cdata=(not keep_cdata),
            )
            self._root = fromstring(body, parser=parser, base_url=url)

            self._raw_body = body.decode()

        else:
            # All HTML types inherit from HtmlMixin so this to check for all at once
            if not issubclass(type(root), HtmlMixin):
                raise TypeError(
                    f"Root have to be a valid element of `html` module types to work, not of type {type(root)}"
                )

            self._root = root
            self._raw_body = ""

        self.__adaptive_enabled = adaptive

        if self.__adaptive_enabled:
            if _storage is not None:
                self._storage = _storage
            else:
                if not storage_args:
                    storage_args = {
                        "storage_file": __DEFAULT_DB_FILE__,
                        "url": url,
                    }

                if not hasattr(storage, "__wrapped__"):
                    raise ValueError(
                        "Storage class must be wrapped with lru_cache decorator, see docs for info"
                    )

                if not issubclass(
                    storage.__wrapped__, StorageSystemMixin
                ):  # pragma: no cover
                    raise ValueError(
                        "Storage system must be inherited from class `StorageSystemMixin`"
                    )

                self._storage = storage(**storage_args)

        self.__keep_comments = keep_comments
        self.__keep_cdata = keep_cdata
        self.__huge_tree_enabled = huge_tree
        self.encoding = encoding
        self.url = url
        # For selector stuff
        self.__attributes = None
        self.__tag = None

    @property
    def __response_data(self):
        # No need to check if all response attributes exist or not because if `status` exist, then the rest exist (Save some CPU cycles for speed)
        if not hasattr(self, "_cached_response_data"):
            self._cached_response_data = (
                {
                    key: getattr(self, key)
                    for key in (
                        "status",
                        "reason",
                        "cookies",
                        "history",
                        "headers",
                        "request_headers",
                    )
                }
                if hasattr(self, "status")
                else {}
            )
        return self._cached_response_data

    def __getitem__(self, key: str) -> TextHandler:
        return self.attrib[key]

    def __contains__(self, key: str) -> bool:
        return key in self.attrib

    # Node functionalities, I wanted to move to a separate Mixin class, but it had a slight impact on performance
    @staticmethod
    def _is_text_node(
        element: HtmlElement | _ElementUnicodeResult,
    ) -> bool:
        """Return True if the given element is a result of a string expression
        Examples:
            XPath -> '/text()', '/@attribute', etc...
            CSS3 -> '::text', '::attr(attrib)'...
        """
        # Faster than checking `element.is_attribute or element.is_text or element.is_tail`
        return issubclass(type(element), _ElementUnicodeResult)

    @staticmethod
    def __content_convertor(
        element: HtmlElement | _ElementUnicodeResult,
    ) -> TextHandler:
        """Used internally to convert a single element's text content to TextHandler directly without checks

        This single line has been isolated like this, so when it's used with `map` we get that slight performance boost vs. list comprehension
        """
        return TextHandler(element)

    def __element_convertor(self, element: HtmlElement) -> "Selector":
        """Used internally to convert a single HtmlElement to Selector directly without checks"""
        db_instance = (
            self._storage if (hasattr(self, "_storage") and self._storage) else None
        )
        return Selector(
            root=element,
            url=self.url,
            encoding=self.encoding,
            adaptive=self.__adaptive_enabled,
            _storage=db_instance,  # Reuse existing storage if it exists otherwise it won't be checked if `adaptive` is turned off
            keep_comments=self.__keep_comments,
            keep_cdata=self.__keep_cdata,
            huge_tree=self.__huge_tree_enabled,
            **self.__response_data,
        )

    def __handle_element(
        self, element: HtmlElement | _ElementUnicodeResult
    ) -> Optional[Union[TextHandler, "Selector"]]:
        """Used internally in all functions to convert a single element to type (Selector|TextHandler) when possible"""
        if element is None:
            return None
        elif self._is_text_node(element):
            # `_ElementUnicodeResult` basically inherit from `str` so it's fine
            return self.__content_convertor(element)
        else:
            return self.__element_convertor(element)

    def __handle_elements(
        self, result: List[HtmlElement | _ElementUnicodeResult]
    ) -> Union["Selectors", "TextHandlers"]:
        """Used internally in all functions to convert results to type (Selectors|TextHandlers) in bulk when possible"""
        if not result:
            return Selectors()

        # From within the code, this method will always get a list of the same type,
        # so we will continue without checks for a slight performance boost
        if self._is_text_node(result[0]):
            return TextHandlers(map(TextHandler, result))

        return Selectors(map(self.__element_convertor, result))

    def __getstate__(self) -> Any:
        # lxml don't like it :)
        raise TypeError("Can't pickle Selector objects")

    # The following four properties I made them into functions instead of variables directly
    # So they don't slow down the process of initializing many instances of the class and gets executed only
    # when the user needs them for the first time for that specific element and gets cached for next times
    # Doing that only made the library performance test sky rocked multiple times faster than before
    # because I was executing them on initialization before :))
    @property
    def tag(self) -> str:
        """Get the tag name of the element"""
        if not self.__tag:
            self.__tag = self._root.tag
        return self.__tag

    @property
    def text(self) -> TextHandler:
        """Get text content of the element"""
        if self.__text is None:
            # If you want to escape lxml default behavior and remove comments like this `<span>CONDITION: <!-- -->Excellent</span>`
            # before extracting text, then keep `keep_comments` set to False while initializing the first class
            self.__text = TextHandler(self._root.text or "")
        return self.__text

    def get_all_text(
        self,
        separator: str = "\n",
        strip: bool = False,
        ignore_tags: Tuple = (
            "script",
            "style",
        ),
        valid_values: bool = True,
    ) -> TextHandler:
        """Get all child strings of this element, concatenated using the given separator.

        :param separator: Strings will be concatenated using this separator.
        :param strip: If True, strings will be stripped before being concatenated.
        :param ignore_tags: A tuple of all tag names you want to ignore
        :param valid_values: If enabled, elements with text-content that is empty or only whitespaces will be ignored

        :return: A TextHandler
        """
        ignored_elements = set()
        if ignore_tags:
            for element in self._root.iter(*ignore_tags):
                ignored_elements.add(element)
                ignored_elements.update(set(_find_all_elements(element)))

        _all_strings = []
        for node in self._root.iter():
            if node not in ignored_elements:
                text = node.text
                if text and isinstance(text, str):
                    processed_text = text.strip() if strip else text
                    if not valid_values or processed_text.strip():
                        _all_strings.append(processed_text)

        return TextHandler(separator).join(_all_strings)

    def urljoin(self, relative_url: str) -> str:
        """Join this Selector's url with a relative url to form an absolute full URL."""
        return urljoin(self.url, relative_url)

    @property
    def attrib(self) -> AttributesHandler:
        """Get attributes of the element"""
        if not self.__attributes:
            self.__attributes = AttributesHandler(self._root.attrib)
        return self.__attributes

    @property
    def html_content(self) -> TextHandler:
        """Return the inner HTML code of the element"""
        return TextHandler(
            tostring(self._root, encoding="unicode", method="html", with_tail=False)
        )

    body = html_content

    def prettify(self) -> TextHandler:
        """Return a prettified version of the element's inner html-code"""
        return TextHandler(
            tostring(
                self._root,
                encoding="unicode",
                pretty_print=True,
                method="html",
                with_tail=False,
            )
        )

    def has_class(self, class_name: str) -> bool:
        """Check if the element has a specific class
        :param class_name: The class name to check for
        :return: True if element has class with that name otherwise False
        """
        return class_name in self._root.classes

    @property
    def parent(self) -> Optional["Selector"]:
        """Return the direct parent of the element or ``None`` otherwise"""
        return self.__handle_element(self._root.getparent())

    @property
    def below_elements(self) -> "Selectors":
        """Return all elements under the current element in the DOM tree"""
        below = _find_all_elements(self._root)
        return self.__handle_elements(below)

    @property
    def children(self) -> "Selectors":
        """Return the children elements of the current element or empty list otherwise"""
        return Selectors(
            self.__element_convertor(child)
            for child in self._root.iterchildren()
            if not isinstance(child, html_forbidden)
        )

    @property
    def siblings(self) -> "Selectors":
        """Return other children of the current element's parent or empty list otherwise"""
        if self.parent:
            return Selectors(
                child for child in self.parent.children if child._root != self._root
            )
        return Selectors()

    def iterancestors(self) -> Generator["Selector", None, None]:
        """Return a generator that loops over all ancestors of the element, starting with the element's parent."""
        for ancestor in self._root.iterancestors():
            yield self.__element_convertor(ancestor)

    def find_ancestor(self, func: Callable[["Selector"], bool]) -> Optional["Selector"]:
        """Loop over all ancestors of the element till one match the passed function
        :param func: A function that takes each ancestor as an argument and returns True/False
        :return: The first ancestor that match the function or ``None`` otherwise.
        """
        for ancestor in self.iterancestors():
            if func(ancestor):
                return ancestor
        return None

    @property
    def path(self) -> "Selectors":
        """Returns a list of type `Selectors` that contains the path leading to the current element from the root."""
        lst = list(self.iterancestors())
        return Selectors(lst)

    @property
    def next(self) -> Optional["Selector"]:
        """Returns the next element of the current element in the children of the parent or ``None`` otherwise."""
        next_element = self._root.getnext()
        while next_element is not None and isinstance(next_element, html_forbidden):
            # Ignore HTML comments and unwanted types
            next_element = next_element.getnext()

        return self.__handle_element(next_element)

    @property
    def previous(self) -> Optional["Selector"]:
        """Returns the previous element of the current element in the children of the parent or ``None`` otherwise."""
        prev_element = self._root.getprevious()
        while prev_element is not None and isinstance(prev_element, html_forbidden):
            # Ignore HTML comments and unwanted types
            prev_element = prev_element.getprevious()

        return self.__handle_element(prev_element)

    # For easy copy-paste from Scrapy/parsel code when needed :)
    def get(self, default=None):
        return self

    def get_all(self):
        return self

    extract = get_all
    extract_first = get

    def __str__(self) -> str:
        return self.html_content

    def __repr__(self) -> str:
        length_limit = 40
        data = "<"
        content = clean_spaces(self.html_content)
        if len(content) > length_limit:
            content = content[:length_limit].strip() + "..."
        data += f"data='{content}'"

        if self.parent:
            parent_content = clean_spaces(self.parent.html_content)
            if len(parent_content) > length_limit:
                parent_content = parent_content[:length_limit].strip() + "..."

            data += f" parent='{parent_content}'"

        return data + ">"

    # From here we start with the selecting functions
    def relocate(
        self,
        element: Union[Dict, HtmlElement, "Selector"],
        percentage: int = 0,
        selector_type: bool = False,
    ) -> Union[List[HtmlElement], "Selectors"]:
        """This function will search again for the element in the page tree, used automatically on page structure change

        :param element: The element we want to relocate in the tree
        :param percentage: The minimum percentage to accept and not going lower than that. Be aware that the percentage
         calculation depends solely on the page structure, so don't play with this number unless you must know
         what you are doing!
        :param selector_type: If True, the return result will be converted to `Selectors` object
        :return: List of pure HTML elements that got the highest matching score or 'Selectors' object
        """
        score_table = {}
        # Note: `element` will most likely always be a dictionary at this point.
        if isinstance(element, self.__class__):
            element = element._root

        if issubclass(type(element), HtmlElement):
            element = _StorageTools.element_to_dict(element)

        for node in _find_all_elements(self._root):
            # Collect all elements in the page, then for each element get the matching score of it against the node.
            # Hence: the code doesn't stop even if the score was 100%
            # because there might be another element(s) left in page with the same score
            score = self.__calculate_similarity_score(element, node)
            score_table.setdefault(score, []).append(node)

        if score_table:
            highest_probability = max(score_table.keys())
            if score_table[highest_probability] and highest_probability >= percentage:
                if log.getEffectiveLevel() < 20:
                    # No need to execute this part if the logging level is not debugging
                    log.debug(f"Highest probability was {highest_probability}%")
                    log.debug("Top 5 best matching elements are: ")
                    for percent in tuple(sorted(score_table.keys(), reverse=True))[:5]:
                        log.debug(
                            f"{percent} -> {self.__handle_elements(score_table[percent])}"
                        )

                if not selector_type:
                    return score_table[highest_probability]
                return self.__handle_elements(score_table[highest_probability])
        return []

    def css_first(
        self,
        selector: str,
        identifier: str = "",
        adaptive: bool = False,
        auto_save: bool = False,
        percentage: int = 0,
    ) -> Union["Selector", "TextHandler", None]:
        """Search the current tree with CSS3 selectors and return the first result if possible, otherwise return `None`

        **Important:
        It's recommended to use the identifier argument if you plan to use a different selector later
        and want to relocate the same element(s)**

        :param selector: The CSS3 selector to be used.
        :param adaptive: Enabled will make the function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in adaptive,
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `adaptive` later
        :param percentage: The minimum percentage to accept while `adaptive` is working and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure, so don't play with this
         number unless you must know what you are doing!
        """
        for element in self.css(
            selector,
            identifier,
            adaptive,
            auto_save,
            percentage,
            _scrapling_first_match=True,
        ):
            return element
        return None

    def xpath_first(
        self,
        selector: str,
        identifier: str = "",
        adaptive: bool = False,
        auto_save: bool = False,
        percentage: int = 0,
        **kwargs: Any,
    ) -> Union["Selector", "TextHandler", None]:
        """Search the current tree with XPath selectors and return the first result if possible, otherwise return `None`

        **Important:
        It's recommended to use the identifier argument if you plan to use a different selector later
        and want to relocate the same element(s)**

         Note: **Additional keyword arguments will be passed as XPath variables in the XPath expression!**

        :param selector: The XPath selector to be used.
        :param adaptive: Enabled will make the function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in adaptive,
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `adaptive` later
        :param percentage: The minimum percentage to accept while `adaptive` is working and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure, so don't play with this
         number unless you must know what you are doing!
        """
        for element in self.xpath(
            selector,
            identifier,
            adaptive,
            auto_save,
            percentage,
            _scrapling_first_match=True,
            **kwargs,
        ):
            return element
        return None

    def css(
        self,
        selector: str,
        identifier: str = "",
        adaptive: bool = False,
        auto_save: bool = False,
        percentage: int = 0,
        **kwargs: Any,
    ) -> Union["Selectors", List, "TextHandlers"]:
        """Search the current tree with CSS3 selectors

        **Important:
        It's recommended to use the identifier argument if you plan to use a different selector later
        and want to relocate the same element(s)**

        :param selector: The CSS3 selector to be used.
        :param adaptive: Enabled will make the function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in adaptive,
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `adaptive` later
        :param percentage: The minimum percentage to accept while `adaptive` is working and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure, so don't play with this
         number unless you must know what you are doing!

        :return: `Selectors` class.
        """
        try:
            if not self.__adaptive_enabled or "," not in selector:
                # No need to split selectors in this case, let's save some CPU cycles :)
                xpath_selector = _translator.css_to_xpath(selector)
                return self.xpath(
                    xpath_selector,
                    identifier or selector,
                    adaptive,
                    auto_save,
                    percentage,
                    _scrapling_first_match=kwargs.pop("_scrapling_first_match", False),
                )

            results = []
            for single_selector in split_selectors(selector):
                # I'm doing this only so the `save` function saves data correctly for combined selectors
                # Like using the ',' to combine two different selectors that point to different elements.
                xpath_selector = _translator.css_to_xpath(single_selector.canonical())
                results += self.xpath(
                    xpath_selector,
                    identifier or single_selector.canonical(),
                    adaptive,
                    auto_save,
                    percentage,
                    _scrapling_first_match=kwargs.pop("_scrapling_first_match", False),
                )

            return results
        except (
            SelectorError,
            SelectorSyntaxError,
        ) as e:
            raise SelectorSyntaxError(
                f"Invalid CSS selector '{selector}': {str(e)}"
            ) from e

    def xpath(
        self,
        selector: str,
        identifier: str = "",
        adaptive: bool = False,
        auto_save: bool = False,
        percentage: int = 0,
        **kwargs: Any,
    ) -> Union["Selectors", "TextHandlers"]:
        """Search the current tree with XPath selectors

        **Important:
        It's recommended to use the identifier argument if you plan to use a different selector later
        and want to relocate the same element(s)**

         Note: **Additional keyword arguments will be passed as XPath variables in the XPath expression!**

        :param selector: The XPath selector to be used.
        :param adaptive: Enabled will make the function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in adaptive,
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `adaptive` later
        :param percentage: The minimum percentage to accept while `adaptive` is working and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure, so don't play with this
         number unless you must know what you are doing!

        :return: `Selectors` class.
        """
        _first_match = kwargs.pop(
            "_scrapling_first_match", False
        )  # Used internally only to speed up `css_first` and `xpath_first`
        try:
            if elements := self._root.xpath(selector, **kwargs):
                if not self.__adaptive_enabled and auto_save:
                    log.warning(
                        "Argument `auto_save` will be ignored because `adaptive` wasn't enabled on initialization. Check docs for more info."
                    )
                elif self.__adaptive_enabled and auto_save:
                    self.save(elements[0], identifier or selector)

                return self.__handle_elements(
                    elements[0:1] if (_first_match and elements) else elements
                )
            elif self.__adaptive_enabled:
                if adaptive:
                    element_data = self.retrieve(identifier or selector)
                    if element_data:
                        elements = self.relocate(element_data, percentage)
                        if elements is not None and auto_save:
                            self.save(elements[0], identifier or selector)

                return self.__handle_elements(
                    elements[0:1] if (_first_match and elements) else elements
                )
            else:
                if adaptive:
                    log.warning(
                        "Argument `adaptive` will be ignored because `adaptive` wasn't enabled on initialization. Check docs for more info."
                    )
                elif auto_save:
                    log.warning(
                        "Argument `auto_save` will be ignored because `adaptive` wasn't enabled on initialization. Check docs for more info."
                    )

                return self.__handle_elements(
                    elements[0:1] if (_first_match and elements) else elements
                )

        except (
            SelectorError,
            SelectorSyntaxError,
            XPathError,
            XPathEvalError,
        ) as e:
            raise SelectorSyntaxError(f"Invalid XPath selector: {selector}") from e

    def find_all(
        self,
        *args: str | Iterable[str] | Pattern | Callable | Dict[str, str],
        **kwargs: str,
    ) -> "Selectors":
        """Find elements by filters of your creations for ease.

        :param args: Tag name(s), iterable of tag names, regex patterns, function, or a dictionary of elements' attributes. Leave empty for selecting all.
        :param kwargs: The attributes you want to filter elements based on it.
        :return: The `Selectors` object of the elements or empty list
        """

        if not args and not kwargs:
            raise TypeError(
                "You have to pass something to search with, like tag name(s), tag attributes, or both."
            )

        attributes = dict()
        tags, patterns = set(), set()
        results, functions, selectors = Selectors(), [], []

        # Brace yourself for a wonderful journey!
        for arg in args:
            if isinstance(arg, str):
                tags.add(arg)

            elif type(arg) in (list, tuple, set):
                if not all(map(lambda x: isinstance(x, str), arg)):
                    raise TypeError(
                        "Nested Iterables are not accepted, only iterables of tag names are accepted"
                    )
                tags.update(set(arg))

            elif isinstance(arg, dict):
                if not all(
                    [
                        (isinstance(k, str) and isinstance(v, str))
                        for k, v in arg.items()
                    ]
                ):
                    raise TypeError(
                        "Nested dictionaries are not accepted, only string keys and string values are accepted"
                    )
                attributes.update(arg)

            elif isinstance(arg, re.Pattern):
                patterns.add(arg)

            elif callable(arg):
                if len(signature(arg).parameters) > 0:
                    functions.append(arg)
                else:
                    raise TypeError(
                        "Callable filter function must have at least one argument to take `Selector` objects."
                    )

            else:
                raise TypeError(
                    f'Argument with type "{type(arg)}" is not accepted, please read the docs.'
                )

        if not all(
            [(isinstance(k, str) and isinstance(v, str)) for k, v in kwargs.items()]
        ):
            raise TypeError("Only string values are accepted for arguments")

        for attribute_name, value in kwargs.items():
            # Only replace names for kwargs, replacing them in dictionaries doesn't make sense
            attribute_name = _whitelisted.get(attribute_name, attribute_name)
            attributes[attribute_name] = value

        # It's easier and faster to build a selector than traversing the tree
        tags = tags or ["*"]
        for tag in tags:
            selector = tag
            for key, value in attributes.items():
                value = value.replace('"', r"\"")  # Escape double quotes in user input
                # Not escaping anything with the key so the user can pass patterns like {'href*': '/p/'} or get errors :)
                selector += '[{}="{}"]'.format(key, value)
            if selector != "*":
                selectors.append(selector)

        if selectors:
            results = self.css(", ".join(selectors))
            if results:
                # From the results, get the ones that fulfill passed regex patterns
                for pattern in patterns:
                    results = results.filter(
                        lambda e: e.text.re(pattern, check_match=True)
                    )

                # From the results, get the ones that fulfill passed functions
                for function in functions:
                    results = results.filter(function)
        else:
            results = results or self.below_elements
            for pattern in patterns:
                results = results.filter(lambda e: e.text.re(pattern, check_match=True))

            # Collect an element if it fulfills the passed function otherwise
            for function in functions:
                results = results.filter(function)

        return results

    def find(
        self,
        *args: str | Iterable[str] | Pattern | Callable | Dict[str, str],
        **kwargs: str,
    ) -> Optional["Selector"]:
        """Find elements by filters of your creations for ease, then return the first result. Otherwise return `None`.

        :param args: Tag name(s), iterable of tag names, regex patterns, function, or a dictionary of elements' attributes. Leave empty for selecting all.
        :param kwargs: The attributes you want to filter elements based on it.
        :return: The `Selector` object of the element or `None` if the result didn't match
        """
        for element in self.find_all(*args, **kwargs):
            return element
        return None

    def __calculate_similarity_score(
        self, original: Dict, candidate: HtmlElement
    ) -> float:
        """Used internally to calculate a score that shows how a candidate element similar to the original one

        :param original: The original element in the form of the dictionary generated from `element_to_dict` function
        :param candidate: The element to compare with the original element.
        :return: A percentage score of how similar is the candidate to the original element
        """
        score, checks = 0, 0
        candidate = _StorageTools.element_to_dict(candidate)

        # Possible TODO:
        # Study the idea of giving weight to each test below so some are more important than others
        # Current results: With weights some websites had better score while it was worse for others
        score += 1 if original["tag"] == candidate["tag"] else 0  # * 0.3  # 30%
        checks += 1

        if original["text"]:
            score += SequenceMatcher(
                None, original["text"], candidate.get("text") or ""
            ).ratio()  # * 0.3  # 30%
            checks += 1

        # if both don't have attributes, it still counts for something!
        score += self.__calculate_dict_diff(
            original["attributes"], candidate["attributes"]
        )  # * 0.3  # 30%
        checks += 1

        # Separate similarity test for class, id, href,... this will help in full structural changes
        for attrib in (
            "class",
            "id",
            "href",
            "src",
        ):
            if original["attributes"].get(attrib):
                score += SequenceMatcher(
                    None,
                    original["attributes"][attrib],
                    candidate["attributes"].get(attrib) or "",
                ).ratio()  # * 0.3  # 30%
                checks += 1

        score += SequenceMatcher(
            None, original["path"], candidate["path"]
        ).ratio()  # * 0.1  # 10%
        checks += 1

        if original.get("parent_name"):
            # Then we start comparing parents' data
            if candidate.get("parent_name"):
                score += SequenceMatcher(
                    None, original["parent_name"], candidate.get("parent_name") or ""
                ).ratio()  # * 0.2  # 20%
                checks += 1

                score += self.__calculate_dict_diff(
                    original["parent_attribs"], candidate.get("parent_attribs") or {}
                )  # * 0.2  # 20%
                checks += 1

                if original["parent_text"]:
                    score += SequenceMatcher(
                        None,
                        original["parent_text"],
                        candidate.get("parent_text") or "",
                    ).ratio()  # * 0.1  # 10%
                    checks += 1
            # else:
            #     # The original element has a parent and this one not, this is not a good sign
            #     score -= 0.1

        if original.get("siblings"):
            score += SequenceMatcher(
                None, original["siblings"], candidate.get("siblings") or []
            ).ratio()  # * 0.1  # 10%
            checks += 1

        # How % sure? let's see
        return round((score / checks) * 100, 2)

    @staticmethod
    def __calculate_dict_diff(dict1: Dict, dict2: Dict) -> float:
        """Used internally to calculate similarity between two dictionaries as SequenceMatcher doesn't accept dictionaries"""
        score = (
            SequenceMatcher(None, tuple(dict1.keys()), tuple(dict2.keys())).ratio()
            * 0.5
        )
        score += (
            SequenceMatcher(None, tuple(dict1.values()), tuple(dict2.values())).ratio()
            * 0.5
        )
        return score

    def save(self, element: Union["Selector", HtmlElement], identifier: str) -> None:
        """Saves the element's unique properties to the storage for retrieval and relocation later

        :param element: The element itself that we want to save to storage, it can be a ` Selector ` or pure ` HtmlElement `
        :param identifier: This is the identifier that will be used to retrieve the element later from the storage. See
            the docs for more info.
        """
        if self.__adaptive_enabled:
            if isinstance(element, self.__class__):
                element = element._root

            if self._is_text_node(element):
                element = element.getparent()

            self._storage.save(element, identifier)
        else:
            log.critical(
                "Can't use `adaptive` features while it's disabled globally, you have to start a new class instance."
            )

    def retrieve(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Using the identifier, we search the storage and return the unique properties of the element

        :param identifier: This is the identifier that will be used to retrieve the element from the storage. See
            the docs for more info.
        :return: A dictionary of the unique properties
        """
        if self.__adaptive_enabled:
            return self._storage.retrieve(identifier)

        log.critical(
            "Can't use `adaptive` features while it's disabled globally, you have to start a new class instance."
        )
        return None

    # Operations on text functions
    def json(self) -> Dict:
        """Return JSON response if the response is jsonable otherwise throws error"""
        if self._raw_body:
            return TextHandler(self._raw_body).json()
        elif self.text:
            return self.text.json()
        else:
            return self.get_all_text(strip=True).json()

    def re(
        self,
        regex: str | Pattern[str],
        replace_entities: bool = True,
        clean_match: bool = False,
        case_sensitive: bool = True,
    ) -> TextHandlers:
        """Apply the given regex to the current text and return a list of strings with the matches.

        :param regex: Can be either a compiled regular expression or a string.
        :param replace_entities: If enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if disabled, the function will set the regex to ignore the letters case while compiling it
        """
        return self.text.re(regex, replace_entities, clean_match, case_sensitive)

    def re_first(
        self,
        regex: str | Pattern[str],
        default=None,
        replace_entities: bool = True,
        clean_match: bool = False,
        case_sensitive: bool = True,
    ) -> TextHandler:
        """Apply the given regex to text and return the first match if found, otherwise return the default value.

        :param regex: Can be either a compiled regular expression or a string.
        :param default: The default value to be returned if there is no match
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if disabled, the function will set the regex to ignore the letters case while compiling it
        """
        return self.text.re_first(
            regex, default, replace_entities, clean_match, case_sensitive
        )

    @staticmethod
    def __get_attributes(element: HtmlElement, ignore_attributes: List | Tuple) -> Dict:
        """Return attributes dictionary without the ignored list"""
        return {k: v for k, v in element.attrib.items() if k not in ignore_attributes}

    def __are_alike(
        self,
        original: HtmlElement,
        original_attributes: Dict,
        candidate: HtmlElement,
        ignore_attributes: List | Tuple,
        similarity_threshold: float,
        match_text: bool = False,
    ) -> bool:
        """Calculate a score of how much these elements are alike and return True
        if the score is higher or equals the threshold"""
        candidate_attributes = (
            self.__get_attributes(candidate, ignore_attributes)
            if ignore_attributes
            else candidate.attrib
        )
        score, checks = 0, 0

        if original_attributes:
            score += sum(
                SequenceMatcher(None, v, candidate_attributes.get(k, "")).ratio()
                for k, v in original_attributes.items()
            )
            checks += len(candidate_attributes)
        else:
            if not candidate_attributes:
                # Both don't have attributes, this must mean something
                score += 1
                checks += 1

        if match_text:
            score += SequenceMatcher(
                None,
                clean_spaces(original.text or ""),
                clean_spaces(candidate.text or ""),
            ).ratio()
            checks += 1

        if checks:
            return round(score / checks, 2) >= similarity_threshold
        return False

    def find_similar(
        self,
        similarity_threshold: float = 0.2,
        ignore_attributes: List | Tuple = (
            "href",
            "src",
        ),
        match_text: bool = False,
    ) -> "Selectors":
        """Find elements that are in the same tree depth in the page with the same tag name and same parent tag etc...
        then return the ones that match the current element attributes with a percentage higher than the input threshold.

        This function is inspired by AutoScraper and made for cases where you, for example, found a product div inside
        a products-list container and want to find other products using that element as a starting point EXCEPT
        this function works in any case without depending on the element type.

        :param similarity_threshold: The percentage to use while comparing element attributes.
            Note: Elements found before attributes matching/comparison will be sharing the same depth, same tag name,
            same parent tag name, and same grand parent tag name. So they are 99% likely to be correct unless you are
            extremely unlucky, then attributes matching comes into play, so don't play with this number unless
            you are getting the results you don't want.
            Also, if the current element doesn't have attributes and the similar element as well, then it's a 100% match.
        :param ignore_attributes: Attribute names passed will be ignored while matching the attributes in the last step.
            The default value is to ignore `href` and `src` as URLs can change a lot between elements, so it's unreliable
        :param match_text: If True, element text content will be taken into calculation while matching.
            Not recommended to use in normal cases, but it depends.

        :return: A ``Selectors`` container of ``Selector`` objects or empty list
        """
        # We will use the elements' root from now on to get the speed boost of using Lxml directly
        root = self._root
        similar_elements = list()

        current_depth = len(list(root.iterancestors()))
        target_attrs = (
            self.__get_attributes(root, ignore_attributes)
            if ignore_attributes
            else root.attrib
        )

        path_parts = [self.tag]
        if (parent := root.getparent()) is not None:
            path_parts.insert(0, parent.tag)
            if (grandparent := parent.getparent()) is not None:
                path_parts.insert(0, grandparent.tag)

        xpath_path = "//{}".format("/".join(path_parts))
        potential_matches = root.xpath(
            f"{xpath_path}[count(ancestor::*) = {current_depth}]"
        )

        for potential_match in potential_matches:
            if potential_match != root and self.__are_alike(
                root,
                target_attrs,
                potential_match,
                ignore_attributes,
                similarity_threshold,
                match_text,
            ):
                similar_elements.append(potential_match)

        return Selectors(map(self.__element_convertor, similar_elements))

    def find_by_text(
        self,
        text: str,
        first_match: bool = True,
        partial: bool = False,
        case_sensitive: bool = False,
        clean_match: bool = True,
    ) -> Union["Selectors", "Selector"]:
        """Find elements that its text content fully/partially matches input.
        :param text: Text query to match
        :param first_match: Returns the first element that matches conditions, enabled by default
        :param partial: If enabled, the function returns elements that contain the input text
        :param case_sensitive: if enabled, the letters case will be taken into consideration
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        """

        results = Selectors()
        if not case_sensitive:
            text = text.lower()

        for node in self.__handle_elements(_find_all_elements_with_spaces(self._root)):
            """Check if element matches given text otherwise, traverse the children tree and iterate"""
            node_text = node.text
            if clean_match:
                node_text = node_text.clean()

            if not case_sensitive:
                node_text = node_text.lower()

            if partial:
                if text in node_text:
                    results.append(node)
            elif text == node_text:
                results.append(node)

            if first_match and results:
                # we got an element so we should stop
                break

        if first_match:
            if results:
                return results[0]
        return results

    def find_by_regex(
        self,
        query: str | Pattern[str],
        first_match: bool = True,
        case_sensitive: bool = False,
        clean_match: bool = True,
    ) -> Union["Selectors", "Selector"]:
        """Find elements that its text content matches the input regex pattern.
        :param query: Regex query/pattern to match
        :param first_match: Return the first element that matches conditions; enabled by default.
        :param case_sensitive: If enabled, the letters case will be taken into consideration in the regex.
        :param clean_match: If enabled, this will ignore all whitespaces and consecutive spaces while matching.
        """
        results = Selectors()

        for node in self.__handle_elements(_find_all_elements_with_spaces(self._root)):
            """Check if element matches given regex otherwise, traverse the children tree and iterate"""
            node_text = node.text
            if node_text.re(
                query,
                check_match=True,
                clean_match=clean_match,
                case_sensitive=case_sensitive,
            ):
                results.append(node)

            if first_match and results:
                # we got an element so we should stop
                break

        if results and first_match:
            return results[0]
        return results


class Selectors(List[Selector]):
    """
    The `Selectors` class is a subclass of the builtin ``List`` class, which provides a few additional methods.
    """

    __slots__ = ()

    @overload
    def __getitem__(self, pos: SupportsIndex) -> Selector:
        pass

    @overload
    def __getitem__(self, pos: slice) -> "Selectors":
        pass

    def __getitem__(self, pos: SupportsIndex | slice) -> Union[Selector, "Selectors"]:
        lst = super().__getitem__(pos)
        if isinstance(pos, slice):
            return self.__class__(lst)
        else:
            return lst

    def xpath(
        self,
        selector: str,
        identifier: str = "",
        auto_save: bool = False,
        percentage: int = 0,
        **kwargs: Any,
    ) -> "Selectors":
        """
        Call the ``.xpath()`` method for each element in this list and return
        their results as another `Selectors` class.

        **Important:
        It's recommended to use the identifier argument if you plan to use a different selector later
        and want to relocate the same element(s)**

         Note: **Additional keyword arguments will be passed as XPath variables in the XPath expression!**

        :param selector: The XPath selector to be used.
        :param identifier: A string that will be used to retrieve element's data in adaptive,
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `adaptive` later
        :param percentage: The minimum percentage to accept while `adaptive` is working and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure, so don't play with this
         number unless you must know what you are doing!

        :return: `Selectors` class.
        """
        results = [
            n.xpath(
                selector, identifier or selector, False, auto_save, percentage, **kwargs
            )
            for n in self
        ]
        return self.__class__(flatten(results))

    def css(
        self,
        selector: str,
        identifier: str = "",
        auto_save: bool = False,
        percentage: int = 0,
    ) -> "Selectors":
        """
        Call the ``.css()`` method for each element in this list and return
        their results flattened as another `Selectors` class.

        **Important:
        It's recommended to use the identifier argument if you plan to use a different selector later
        and want to relocate the same element(s)**

        :param selector: The CSS3 selector to be used.
        :param identifier: A string that will be used to retrieve element's data in adaptive,
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `adaptive` later
        :param percentage: The minimum percentage to accept while `adaptive` is working and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure, so don't play with this
         number unless you must know what you are doing!

        :return: `Selectors` class.
        """
        results = [
            n.css(selector, identifier or selector, False, auto_save, percentage)
            for n in self
        ]
        return self.__class__(flatten(results))

    def re(
        self,
        regex: str | Pattern,
        replace_entities: bool = True,
        clean_match: bool = False,
        case_sensitive: bool = True,
    ) -> TextHandlers:
        """Call the ``.re()`` method for each element in this list and return
        their results flattened as List of TextHandler.

        :param regex: Can be either a compiled regular expression or a string.
        :param replace_entities: If enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if disabled, the function will set the regex to ignore the letters case while compiling it
        """
        results = [
            n.text.re(regex, replace_entities, clean_match, case_sensitive)
            for n in self
        ]
        return TextHandlers(flatten(results))

    def re_first(
        self,
        regex: str | Pattern,
        default=None,
        replace_entities: bool = True,
        clean_match: bool = False,
        case_sensitive: bool = True,
    ) -> TextHandler:
        """Call the ``.re_first()`` method for each element in this list and return
        the first result or the default value otherwise.

        :param regex: Can be either a compiled regular expression or a string.
        :param default: The default value to be returned if there is no match
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if disabled, function will set the regex to ignore the letters case while compiling it
        """
        for n in self:
            for result in n.re(regex, replace_entities, clean_match, case_sensitive):
                return result
        return default

    def search(self, func: Callable[["Selector"], bool]) -> Optional["Selector"]:
        """Loop over all current elements and return the first element that matches the passed function
        :param func: A function that takes each element as an argument and returns True/False
        :return: The first element that match the function or ``None`` otherwise.
        """
        for element in self:
            if func(element):
                return element
        return None

    def filter(self, func: Callable[["Selector"], bool]) -> "Selectors":
        """Filter current elements based on the passed function
        :param func: A function that takes each element as an argument and returns True/False
        :return: The new `Selectors` object or empty list otherwise.
        """
        return self.__class__([element for element in self if func(element)])

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

    @property
    def first(self):
        """Returns the first item of the current list or `None` if the list is empty"""
        return self.get()

    @property
    def last(self):
        """Returns the last item of the current list or `None` if the list is empty"""
        return self[-1] if len(self) > 0 else None

    @property
    def length(self):
        """Returns the length of the current list"""
        return len(self)

    def __getstate__(self) -> Any:  # pragma: no cover
        # lxml don't like it :)
        raise TypeError("Can't pickle Selectors object")


# For backward compatibility
Adaptor = Selector
Adaptors = Selectors
