import inspect
import os
import re
import typing
from difflib import SequenceMatcher
from urllib.parse import urljoin

from cssselect import SelectorError, SelectorSyntaxError
from cssselect import parse as split_selectors
from lxml import etree, html

from scrapling.core._types import (Any, Callable, Dict, Generator, Iterable,
                                   List, Optional, Pattern, SupportsIndex,
                                   Tuple, Union)
from scrapling.core.custom_types import (AttributesHandler, TextHandler,
                                         TextHandlers)
from scrapling.core.mixins import SelectorsGeneration
from scrapling.core.storage_adaptors import (SQLiteStorageSystem,
                                             StorageSystemMixin, _StorageTools)
from scrapling.core.translator import HTMLTranslator
from scrapling.core.utils import (clean_spaces, flatten, html_forbidden,
                                  is_jsonable, log)


class Adaptor(SelectorsGeneration):
    __slots__ = (
        'url', 'encoding', '__auto_match_enabled', '_root', '_storage',
        '__keep_comments', '__huge_tree_enabled', '__attributes', '__text', '__tag',
        '__keep_cdata', '__raw_body'
    )

    def __init__(
            self,
            text: Optional[str] = None,
            url: Optional[str] = None,
            body: bytes = b"",
            encoding: str = "utf8",
            huge_tree: bool = True,
            root: Optional[html.HtmlElement] = None,
            keep_comments: Optional[bool] = False,
            keep_cdata: Optional[bool] = False,
            auto_match: Optional[bool] = True,
            storage: Any = SQLiteStorageSystem,
            storage_args: Optional[Dict] = None,
            **kwargs
    ):
        """The main class that works as a wrapper for the HTML input data. Using this class, you can search for elements
        with expressions in CSS, XPath, or with simply text. Check the docs for more info.

        Here we try to extend module ``lxml.html.HtmlElement`` while maintaining a simpler interface, We are not
        inheriting from the ``lxml.html.HtmlElement`` because it's not pickleable which makes a lot of reference jobs
        not possible. You can test it here and see code explodes with `AssertionError: invalid Element proxy at...`.
        It's an old issue with lxml, see `this entry <https://bugs.launchpad.net/lxml/+bug/736708>`

        :param text: HTML body passed as text.
        :param url: allows storing a URL with the html data for retrieving later.
        :param body: HTML body as ``bytes`` object. It can be used instead of the ``text`` argument.
        :param encoding: The encoding type that will be used in HTML parsing, default is `UTF-8`
        :param huge_tree: Enabled by default, should always be enabled when parsing large HTML documents. This controls
            libxml2 feature that forbids parsing certain large documents to protect from possible memory exhaustion.
        :param root: Used internally to pass etree objects instead of text/body arguments, it takes highest priority.
            Don't use it unless you know what you are doing!
        :param keep_comments: While parsing the HTML body, drop comments or not. Disabled by default for obvious reasons
        :param keep_cdata: While parsing the HTML body, drop cdata or not. Disabled by default for cleaner HTML.
        :param auto_match: Globally turn-off the auto-match feature in all functions, this argument takes higher
            priority over all auto-match related arguments/functions in the class.
        :param storage: The storage class to be passed for auto-matching functionalities, see ``Docs`` for more info.
        :param storage_args: A dictionary of ``argument->value`` pairs to be passed for the storage class.
            If empty, default values will be used.
        """
        if root is None and not body and text is None:
            raise ValueError("Adaptor class needs text, body, or root arguments to work")

        self.__text = None
        self.__raw_body = ''
        if root is None:
            if text is None:
                if not body or not isinstance(body, bytes):
                    raise TypeError(f"body argument must be valid and of type bytes, got {body.__class__}")

                body = body.replace(b"\x00", b"").strip()
                self.__raw_body = body.replace(b"\x00", b"").strip().decode()
            else:
                if not isinstance(text, str):
                    raise TypeError(f"text argument must be of type str, got {text.__class__}")

                body = text.strip().replace("\x00", "").encode(encoding) or b"<html/>"
                self.__raw_body = text.strip()

            # https://lxml.de/api/lxml.etree.HTMLParser-class.html
            parser = html.HTMLParser(
                recover=True, remove_blank_text=True, remove_comments=(not keep_comments), encoding=encoding,
                compact=True, huge_tree=huge_tree, default_doctype=True, strip_cdata=(not keep_cdata),
            )
            self._root = etree.fromstring(body, parser=parser, base_url=url)
            if is_jsonable(text or body.decode()):
                self.__text = TextHandler(text or body.decode())

        else:
            # All html types inherits from HtmlMixin so this to check for all at once
            if not issubclass(type(root), html.HtmlMixin):
                raise TypeError(
                    f"Root have to be a valid element of `html` module types to work, not of type {type(root)}"
                )

            self._root = root

        self.__auto_match_enabled = auto_match

        if self.__auto_match_enabled:
            if not storage_args:
                storage_args = {
                    'storage_file': os.path.join(os.path.dirname(__file__), 'elements_storage.db'),
                    'url': url
                }

            if not hasattr(storage, '__wrapped__'):
                raise ValueError("Storage class must be wrapped with lru_cache decorator, see docs for info")

            if not issubclass(storage.__wrapped__, StorageSystemMixin):
                raise ValueError("Storage system must be inherited from class `StorageSystemMixin`")

            self._storage = storage(**storage_args)

        self.__keep_comments = keep_comments
        self.__keep_cdata = keep_cdata
        self.__huge_tree_enabled = huge_tree
        self.encoding = encoding
        self.url = url
        # For selector stuff
        self.__attributes = None
        self.__tag = None
        # No need to check if all response attributes exist or not because if `status` exist, then the rest exist (Save some CPU cycles for speed)
        self.__response_data = {
            key: getattr(self, key) for key in ('status', 'reason', 'cookies', 'headers', 'request_headers',)
        } if hasattr(self, 'status') else {}

    # Node functionalities, I wanted to move to separate Mixin class but it had slight impact on performance
    @staticmethod
    def _is_text_node(element: Union[html.HtmlElement, etree._ElementUnicodeResult]) -> bool:
        """Return True if given element is a result of a string expression
        Examples:
            XPath -> '/text()', '/@attribute' etc...
            CSS3  -> '::text', '::attr(attrib)'...
        """
        # Faster than checking `element.is_attribute or element.is_text or element.is_tail`
        return issubclass(type(element), etree._ElementUnicodeResult)

    @staticmethod
    def __content_convertor(element: Union[html.HtmlElement, etree._ElementUnicodeResult]) -> TextHandler:
        """Used internally to convert a single element's text content to TextHandler directly without checks

        This single line has been isolated like this so when it's used with map we get that slight performance boost vs list comprehension
        """
        return TextHandler(str(element))

    def __element_convertor(self, element: html.HtmlElement) -> 'Adaptor':
        """Used internally to convert a single HtmlElement to Adaptor directly without checks"""
        return Adaptor(
            root=element,
            text='', body=b'',  # Since root argument is provided, both `text` and `body` will be ignored so this is just a filler
            url=self.url, encoding=self.encoding, auto_match=self.__auto_match_enabled,
            keep_comments=self.__keep_comments, keep_cdata=self.__keep_cdata,
            huge_tree=self.__huge_tree_enabled,
            **self.__response_data
        )

    def __handle_element(self, element: Union[html.HtmlElement, etree._ElementUnicodeResult]) -> Union[TextHandler, 'Adaptor', None]:
        """Used internally in all functions to convert a single element to type (Adaptor|TextHandler) when possible"""
        if element is None:
            return None
        elif self._is_text_node(element):
            # etree._ElementUnicodeResult basically inherit from `str` so it's fine
            return self.__content_convertor(element)
        else:
            return self.__element_convertor(element)

    def __handle_elements(self, result: List[Union[html.HtmlElement, etree._ElementUnicodeResult]]) -> Union['Adaptors', 'TextHandlers', List]:
        """Used internally in all functions to convert results to type (Adaptors|TextHandlers) in bulk when possible"""
        if not len(result):  # Lxml will give a warning if I used something like `not result`
            return Adaptors([])

        # From within the code, this method will always get a list of the same type
        # so we will continue without checks for slight performance boost
        if self._is_text_node(result[0]):
            return TextHandlers(list(map(self.__content_convertor, result)))

        return Adaptors(list(map(self.__element_convertor, result)))

    def __getstate__(self) -> Any:
        # lxml don't like it :)
        raise TypeError("Can't pickle Adaptor objects")

    # The following four properties I made them into functions instead of variables directly
    # So they don't slow down the process of initializing many instances of the class and gets executed only
    # when the user need them for the first time for that specific element and gets cached for next times
    # Doing that only made the library performance test sky rocked multiple times faster than before
    # because I was executing them on initialization before :))
    @property
    def tag(self) -> str:
        """Get tag name of the element"""
        if not self.__tag:
            self.__tag = self._root.tag
        return self.__tag

    @property
    def text(self) -> TextHandler:
        """Get text content of the element"""
        if not self.__text:
            # If you want to escape lxml default behaviour and remove comments like this `<span>CONDITION: <!-- -->Excellent</span>`
            # before extracting text then keep `keep_comments` set to False while initializing the first class
            self.__text = TextHandler(self._root.text)
        return self.__text

    def get_all_text(self, separator: str = "\n", strip: bool = False, ignore_tags: Tuple = ('script', 'style',), valid_values: bool = True) -> TextHandler:
        """Get all child strings of this element, concatenated using the given separator.

        :param separator: Strings will be concatenated using this separator.
        :param strip: If True, strings will be stripped before being concatenated.
        :param ignore_tags: A tuple of all tag names you want to ignore
        :param valid_values: If enabled, elements with text-content that is empty or only whitespaces will be ignored

        :return: A TextHandler
        """
        _all_strings = []
        for node in self._root.xpath('.//*'):
            if node.tag not in ignore_tags:
                text = node.text
                if text and type(text) is str:
                    if valid_values and text.strip():
                        _all_strings.append(text if not strip else text.strip())
                    else:
                        _all_strings.append(text if not strip else text.strip())

        return TextHandler(separator.join(_all_strings))

    def urljoin(self, relative_url: str) -> str:
        """Join this Adaptor's url with a relative url to form an absolute full URL."""
        return urljoin(self.url, relative_url)

    @property
    def attrib(self) -> AttributesHandler:
        """Get attributes of the element"""
        if not self.__attributes:
            self.__attributes = AttributesHandler(self._root.attrib)
        return self.__attributes

    @property
    def html_content(self) -> TextHandler:
        """Return the inner html code of the element"""
        return TextHandler(etree.tostring(self._root, encoding='unicode', method='html', with_tail=False))

    @property
    def body(self) -> TextHandler:
        """Return raw HTML code of the element/page without any processing when possible or return `Adaptor.html_content`"""
        return TextHandler(self.__raw_body) or self.html_content

    def prettify(self) -> TextHandler:
        """Return a prettified version of the element's inner html-code"""
        return TextHandler(etree.tostring(self._root, encoding='unicode', pretty_print=True, method='html', with_tail=False))

    def has_class(self, class_name: str) -> bool:
        """Check if element has a specific class
        :param class_name: The class name to check for
        :return: True if element has class with that name otherwise False
        """
        return class_name in self._root.classes

    @property
    def parent(self) -> Union['Adaptor', None]:
        """Return the direct parent of the element or ``None`` otherwise"""
        return self.__handle_element(self._root.getparent())

    @property
    def below_elements(self) -> 'Adaptors[Adaptor]':
        """Return all elements under the current element in the DOM tree"""
        below = self._root.xpath('.//*')
        return self.__handle_elements(below)

    @property
    def children(self) -> 'Adaptors[Adaptor]':
        """Return the children elements of the current element or empty list otherwise"""
        return Adaptors([
            self.__element_convertor(child) for child in self._root.iterchildren() if type(child) not in html_forbidden
        ])

    @property
    def siblings(self) -> 'Adaptors[Adaptor]':
        """Return other children of the current element's parent or empty list otherwise"""
        if self.parent:
            return Adaptors([child for child in self.parent.children if child._root != self._root])
        return Adaptors([])

    def iterancestors(self) -> Generator['Adaptor', None, None]:
        """Return a generator that loops over all ancestors of the element, starting with element's parent."""
        for ancestor in self._root.iterancestors():
            yield self.__element_convertor(ancestor)

    def find_ancestor(self, func: Callable[['Adaptor'], bool]) -> Union['Adaptor', None]:
        """Loop over all ancestors of the element till one match the passed function
        :param func: A function that takes each ancestor as an argument and returns True/False
        :return: The first ancestor that match the function or ``None`` otherwise.
        """
        for ancestor in self.iterancestors():
            if func(ancestor):
                return ancestor
        return None

    @property
    def path(self) -> 'Adaptors[Adaptor]':
        """Returns list of type :class:`Adaptors` that contains the path leading to the current element from the root."""
        lst = list(self.iterancestors())
        return Adaptors(lst)

    @property
    def next(self) -> Union['Adaptor', None]:
        """Returns the next element of the current element in the children of the parent or ``None`` otherwise."""
        next_element = self._root.getnext()
        if next_element is not None:
            while type(next_element) in html_forbidden:
                # Ignore html comments and unwanted types
                next_element = next_element.getnext()

        return self.__handle_element(next_element)

    @property
    def previous(self) -> Union['Adaptor', None]:
        """Returns the previous element of the current element in the children of the parent or ``None`` otherwise."""
        prev_element = self._root.getprevious()
        if prev_element is not None:
            while type(prev_element) in html_forbidden:
                # Ignore html comments and unwanted types
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
            content = content[:length_limit].strip() + '...'
        data += f"data='{content}'"

        if self.parent:
            parent_content = clean_spaces(self.parent.html_content)
            if len(parent_content) > length_limit:
                parent_content = parent_content[:length_limit].strip() + '...'

            data += f" parent='{parent_content}'"

        return data + ">"

    # From here we start the selecting functions
    def relocate(
            self, element: Union[Dict, html.HtmlElement, 'Adaptor'], percentage: int = 0, adaptor_type: bool = False
    ) -> Union[List[Union[html.HtmlElement, None]], 'Adaptors']:
        """This function will search again for the element in the page tree, used automatically on page structure change

        :param element: The element we want to relocate in the tree
        :param percentage: The minimum percentage to accept and not going lower than that. Be aware that the percentage
         calculation depends solely on the page structure so don't play with this number unless you must know
         what you are doing!
        :param adaptor_type: If True, the return result will be converted to `Adaptors` object
        :return: List of pure HTML elements that got the highest matching score or 'Adaptors' object
        """
        score_table = {}
        # Note: `element` will be most likely always be a dictionary at this point.
        if isinstance(element, self.__class__):
            element = element._root

        if issubclass(type(element), html.HtmlElement):
            element = _StorageTools.element_to_dict(element)

        for node in self._root.xpath('.//*'):
            # Collect all elements in the page then for each element get the matching score of it against the node.
            # Hence: the code doesn't stop even if the score was 100%
            # because there might be another element(s) left in page with the same score
            score = self.__calculate_similarity_score(element, node)
            score_table.setdefault(score, []).append(node)

        if score_table:
            highest_probability = max(score_table.keys())
            if score_table[highest_probability] and highest_probability >= percentage:
                if log.getEffectiveLevel() < 20:
                    # No need to execute this part if logging level is not debugging
                    log.debug(f'Highest probability was {highest_probability}%')
                    log.debug('Top 5 best matching elements are: ')
                    for percent in tuple(sorted(score_table.keys(), reverse=True))[:5]:
                        log.debug(f'{percent} -> {self.__handle_elements(score_table[percent])}')

                if not adaptor_type:
                    return score_table[highest_probability]
                return self.__handle_elements(score_table[highest_probability])
        return []

    def css_first(self, selector: str, identifier: str = '',
                  auto_match: bool = False, auto_save: bool = False, percentage: int = 0
                  ) -> Union['Adaptor', 'TextHandler', None]:
        """Search current tree with CSS3 selectors and return the first result if possible, otherwise return `None`

        **Important:
        It's recommended to use the identifier argument if you plan to use different selector later
        and want to relocate the same element(s)**

        :param selector: The CSS3 selector to be used.
        :param auto_match: Enabled will make function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in auto-matching
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `auto_match` later
        :param percentage: The minimum percentage to accept while auto-matching and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure so don't play with this
         number unless you must know what you are doing!
        """
        for element in self.css(selector, identifier, auto_match, auto_save, percentage):
            return element
        return None

    def xpath_first(self, selector: str, identifier: str = '',
                    auto_match: bool = False, auto_save: bool = False, percentage: int = 0, **kwargs: Any
                    ) -> Union['Adaptor', 'TextHandler', None]:
        """Search current tree with XPath selectors and return the first result if possible, otherwise return `None`

        **Important:
        It's recommended to use the identifier argument if you plan to use different selector later
        and want to relocate the same element(s)**

         Note: **Additional keyword arguments will be passed as XPath variables in the XPath expression!**

        :param selector: The XPath selector to be used.
        :param auto_match: Enabled will make function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in auto-matching
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `auto_match` later
        :param percentage: The minimum percentage to accept while auto-matching and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure so don't play with this
         number unless you must know what you are doing!
        """
        for element in self.xpath(selector, identifier, auto_match, auto_save, percentage, **kwargs):
            return element
        return None

    def css(self, selector: str, identifier: str = '',
            auto_match: bool = False, auto_save: bool = False, percentage: int = 0
            ) -> Union['Adaptors[Adaptor]', List, 'TextHandlers[TextHandler]']:
        """Search current tree with CSS3 selectors

        **Important:
        It's recommended to use the identifier argument if you plan to use different selector later
        and want to relocate the same element(s)**

        :param selector: The CSS3 selector to be used.
        :param auto_match: Enabled will make function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in auto-matching
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `auto_match` later
        :param percentage: The minimum percentage to accept while auto-matching and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure so don't play with this
         number unless you must know what you are doing!

        :return: List as :class:`Adaptors`
        """
        try:
            if not self.__auto_match_enabled or ',' not in selector:
                # No need to split selectors in this case, let's save some CPU cycles :)
                xpath_selector = HTMLTranslator().css_to_xpath(selector)
                return self.xpath(xpath_selector, identifier or selector, auto_match, auto_save, percentage)

            results = []
            if ',' in selector:
                for single_selector in split_selectors(selector):
                    # I'm doing this only so the `save` function save data correctly for combined selectors
                    # Like using the ',' to combine two different selectors that point to different elements.
                    xpath_selector = HTMLTranslator().css_to_xpath(single_selector.canonical())
                    results += self.xpath(
                        xpath_selector, identifier or single_selector.canonical(), auto_match, auto_save, percentage
                    )

            return results
        except (SelectorError, SelectorSyntaxError,):
            raise SelectorSyntaxError(f"Invalid CSS selector: {selector}")

    def xpath(self, selector: str, identifier: str = '',
              auto_match: bool = False, auto_save: bool = False, percentage: int = 0, **kwargs: Any
              ) -> Union['Adaptors[Adaptor]', List, 'TextHandlers[TextHandler]']:
        """Search current tree with XPath selectors

        **Important:
        It's recommended to use the identifier argument if you plan to use different selector later
        and want to relocate the same element(s)**

         Note: **Additional keyword arguments will be passed as XPath variables in the XPath expression!**

        :param selector: The XPath selector to be used.
        :param auto_match: Enabled will make function try to relocate the element if it was 'saved' before
        :param identifier: A string that will be used to save/retrieve element's data in auto-matching
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `auto_match` later
        :param percentage: The minimum percentage to accept while auto-matching and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure so don't play with this
         number unless you must know what you are doing!

        :return: List as :class:`Adaptors`
        """
        try:
            elements = self._root.xpath(selector, **kwargs)

            if elements:
                if auto_save:
                    if not self.__auto_match_enabled:
                        log.warning("Argument `auto_save` will be ignored because `auto_match` wasn't enabled on initialization. Check docs for more info.")
                    else:
                        self.save(elements[0], identifier or selector)

                return self.__handle_elements(elements)
            elif self.__auto_match_enabled:
                if auto_match:
                    element_data = self.retrieve(identifier or selector)
                    if element_data:
                        elements = self.relocate(element_data, percentage)
                        if elements is not None and auto_save:
                            self.save(elements[0], identifier or selector)

                return self.__handle_elements(elements)
            else:
                if auto_match:
                    log.warning("Argument `auto_match` will be ignored because `auto_match` wasn't enabled on initialization. Check docs for more info.")
                elif auto_save:
                    log.warning("Argument `auto_save` will be ignored because `auto_match` wasn't enabled on initialization. Check docs for more info.")

                return self.__handle_elements(elements)

        except (SelectorError, SelectorSyntaxError, etree.XPathError, etree.XPathEvalError):
            raise SelectorSyntaxError(f"Invalid XPath selector: {selector}")

    def find_all(self, *args: Union[str, Iterable[str], Pattern, Callable, Dict[str, str]], **kwargs: str) -> 'Adaptors':
        """Find elements by filters of your creations for ease..

        :param args: Tag name(s), an iterable of tag names, regex patterns, function, or a dictionary of elements' attributes. Leave empty for selecting all.
        :param kwargs: The attributes you want to filter elements based on it.
        :return: The `Adaptors` object of the elements or empty list
        """
        # Attributes that are Python reserved words and can't be used directly
        # Ex: find_all('a', class="blah") -> find_all('a', class_="blah")
        # https://www.w3schools.com/python/python_ref_keywords.asp
        whitelisted = {
            'class_': 'class',
            'for_': 'for',
        }

        if not args and not kwargs:
            raise TypeError('You have to pass something to search with, like tag name(s), tag attributes, or both.')

        attributes = dict()
        tags, patterns = set(), set()
        results, functions, selectors = Adaptors([]), [], []

        # Brace yourself for a wonderful journey!
        for arg in args:
            if type(arg) is str:
                tags.add(arg)

            elif type(arg) in [list, tuple, set]:
                if not all(map(lambda x: type(x) is str, arg)):
                    raise TypeError('Nested Iterables are not accepted, only iterables of tag names are accepted')
                tags.update(set(arg))

            elif isinstance(arg, dict):
                if not all([(type(k) is str and type(v) is str) for k, v in arg.items()]):
                    raise TypeError('Nested dictionaries are not accepted, only string keys and string values are accepted')
                attributes.update(arg)

            elif isinstance(arg, re.Pattern):
                patterns.add(arg)

            elif callable(arg):
                if len(inspect.signature(arg).parameters) > 0:
                    functions.append(arg)
                else:
                    raise TypeError("Callable filter function must have at least one argument to take `Adaptor` objects.")

            else:
                raise TypeError(f'Argument with type "{type(arg)}" is not accepted, please read the docs.')

        if not all([(type(k) is str and type(v) is str) for k, v in kwargs.items()]):
            raise TypeError('Only string values are accepted for arguments')

        for attribute_name, value in kwargs.items():
            # Only replace names for kwargs, replacing them in dictionaries doesn't make sense
            attribute_name = whitelisted.get(attribute_name, attribute_name)
            attributes[attribute_name] = value

        # It's easier and faster to build a selector than traversing the tree
        tags = tags or ['*']
        for tag in tags:
            selector = tag
            for key, value in attributes.items():
                value = value.replace('"', r'\"')  # Escape double quotes in user input
                # Not escaping anything with the key so the user can pass patterns like {'href*': '/p/'} or get errors :)
                selector += '[{}="{}"]'.format(key, value)
            if selector != '*':
                selectors.append(selector)

        if selectors:
            results = self.css(', '.join(selectors))
            if results:
                # From the results, get the ones that fulfill passed regex patterns
                for pattern in patterns:
                    results = results.filter(lambda e: e.text.re(pattern, check_match=True))

                # From the results, get the ones that fulfill passed functions
                for function in functions:
                    results = results.filter(function)
        else:
            results = results or self.below_elements
            for pattern in patterns:
                results = results.filter(lambda e: e.text.re(pattern, check_match=True))

            # Collect element if it fulfills passed function otherwise
            for function in functions:
                results = results.filter(function)

        return results

    def find(self, *args: Union[str, Iterable[str], Pattern, Callable, Dict[str, str]], **kwargs: str) -> Union['Adaptor', None]:
        """Find elements by filters of your creations for ease then return the first result. Otherwise return `None`.

        :param args: Tag name(s), an iterable of tag names, regex patterns, function, or a dictionary of elements' attributes. Leave empty for selecting all.
        :param kwargs: The attributes you want to filter elements based on it.
        :return: The `Adaptor` object of the element or `None` if the result didn't match
        """
        for element in self.find_all(*args, **kwargs):
            return element
        return None

    def __calculate_similarity_score(self, original: Dict, candidate: html.HtmlElement) -> float:
        """Used internally to calculate a score that shows how candidate element similar to the original one

        :param original: The original element in the form of the dictionary generated from `element_to_dict` function
        :param candidate: The element to compare with the original element.
        :return: A percentage score of how similar is the candidate to the original element
        """
        score, checks = 0, 0
        candidate = _StorageTools.element_to_dict(candidate)

        # Possible TODO:
        # Study the idea of giving weight to each test below so some are more important than others
        # Current results: With weights some websites had better score while it was worse for others
        score += 1 if original['tag'] == candidate['tag'] else 0  # * 0.3  # 30%
        checks += 1

        if original['text']:
            score += SequenceMatcher(None, original['text'], candidate.get('text') or '').ratio()  # * 0.3  # 30%
            checks += 1

        # if both doesn't have attributes, it still count for something!
        score += self.__calculate_dict_diff(original['attributes'], candidate['attributes'])  # * 0.3  # 30%
        checks += 1

        # Separate similarity test for class, id, href,... this will help in full structural changes
        for attrib in ('class', 'id', 'href', 'src',):
            if original['attributes'].get(attrib):
                score += SequenceMatcher(
                    None, original['attributes'][attrib], candidate['attributes'].get(attrib) or ''
                ).ratio()  # * 0.3  # 30%
                checks += 1

        score += SequenceMatcher(None, original['path'], candidate['path']).ratio()  # * 0.1  # 10%
        checks += 1

        if original.get('parent_name'):
            # Then we start comparing parents' data
            if candidate.get('parent_name'):
                score += SequenceMatcher(
                    None, original['parent_name'], candidate.get('parent_name') or ''
                ).ratio()  # * 0.2  # 20%
                checks += 1

                score += self.__calculate_dict_diff(
                    original['parent_attribs'], candidate.get('parent_attribs') or {}
                )  # * 0.2  # 20%
                checks += 1

                if original['parent_text']:
                    score += SequenceMatcher(
                        None, original['parent_text'], candidate.get('parent_text') or ''
                    ).ratio()  # * 0.1  # 10%
                    checks += 1
            # else:
            #     # The original element have a parent and this one not, this is not a good sign
            #     score -= 0.1

        if original.get('siblings'):
            score += SequenceMatcher(
                None, original['siblings'], candidate.get('siblings') or []
            ).ratio()  # * 0.1  # 10%
            checks += 1

        # How % sure? let's see
        return round((score / checks) * 100, 2)

    @staticmethod
    def __calculate_dict_diff(dict1: dict, dict2: dict) -> float:
        """Used internally calculate similarity between two dictionaries as SequenceMatcher doesn't accept dictionaries
        """
        score = SequenceMatcher(None, tuple(dict1.keys()), tuple(dict2.keys())).ratio() * 0.5
        score += SequenceMatcher(None, tuple(dict1.values()), tuple(dict2.values())).ratio() * 0.5
        return score

    def save(self, element: Union['Adaptor', html.HtmlElement], identifier: str) -> None:
        """Saves the element's unique properties to the storage for retrieval and relocation later

        :param element: The element itself that we want to save to storage, it can be a `Adaptor` or pure `HtmlElement`
        :param identifier: This is the identifier that will be used to retrieve the element later from the storage. See
            the docs for more info.
        """
        if self.__auto_match_enabled:
            if isinstance(element, self.__class__):
                element = element._root

            if self._is_text_node(element):
                element = element.getparent()

            self._storage.save(element, identifier)
        else:
            log.critical(
                "Can't use Auto-match features while disabled globally, you have to start a new class instance."
            )

    def retrieve(self, identifier: str) -> Optional[Dict]:
        """Using the identifier, we search the storage and return the unique properties of the element

        :param identifier: This is the identifier that will be used to retrieve the element from the storage. See
            the docs for more info.
        :return: A dictionary of the unique properties
        """
        if self.__auto_match_enabled:
            return self._storage.retrieve(identifier)

        log.critical(
            "Can't use Auto-match features while disabled globally, you have to start a new class instance."
        )

    # Operations on text functions
    def json(self) -> Dict:
        """Return json response if the response is jsonable otherwise throws error"""
        if self.text:
            return self.text.json()
        else:
            return self.get_all_text(strip=True).json()

    def re(self, regex: Union[str, Pattern[str]], replace_entities: bool = True,
           clean_match: bool = False, case_sensitive: bool = False) -> TextHandlers:
        """Apply the given regex to the current text and return a list of strings with the matches.

        :param regex: Can be either a compiled regular expression or a string.
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it
        """
        return self.text.re(regex, replace_entities, clean_match, case_sensitive)

    def re_first(self, regex: Union[str, Pattern[str]], default=None, replace_entities: bool = True,
                 clean_match: bool = False, case_sensitive: bool = False) -> TextHandler:
        """Apply the given regex to text and return the first match if found, otherwise return the default value.

        :param regex: Can be either a compiled regular expression or a string.
        :param default: The default value to be returned if there is no match
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it
        """
        return self.text.re_first(regex, default, replace_entities, clean_match, case_sensitive)

    def find_similar(
            self,
            similarity_threshold: float = 0.2,
            ignore_attributes: Union[List, Tuple] = ('href', 'src',),
            match_text: bool = False
    ) -> Union['Adaptors[Adaptor]', List]:
        """Find elements that are in the same tree depth in the page with the same tag name and same parent tag etc...
        then return the ones that match the current element attributes with percentage higher than the input threshold.

        This function is inspired by AutoScraper and made for cases where you, for example, found a product div inside
        a products-list container and want to find other products using that that element as a starting point EXCEPT
        this function works in any case without depending on the element type.

        :param similarity_threshold: The percentage to use while comparing elements attributes.
            Note: Elements found before attributes matching/comparison will be sharing the same depth, same tag name,
            same parent tag name, and same grand parent tag name. So they are 99% likely to be correct unless your are
            extremely unlucky then attributes matching comes into play so basically don't play with this number unless
            you are getting the results you don't want.
            Also, if current element doesn't have attributes and the similar element as well, then it's a 100% match.
        :param ignore_attributes: Attribute names passed will be ignored while matching the attributes in last step.
            The default value is to ignore `href` and `src` as URLs can change a lot between elements so it's unreliable
        :param match_text: If True, elements text content will be taken into calculation while matching.
            Not recommended to use in normal cases but it depends.

        :return: A ``Adaptors`` container of ``Adaptor`` objects or empty list
        """
        def get_attributes(element: html.HtmlElement) -> Dict:
            """Return attributes dictionary without the ignored list"""
            return {k: v for k, v in element.attrib.items() if k not in ignore_attributes}

        def are_alike(original: html.HtmlElement, original_attributes: Dict, candidate: html.HtmlElement) -> bool:
            """Calculate a score of how much these elements are alike and return True
                if score is higher or equal the threshold"""
            candidate_attributes = get_attributes(candidate) if ignore_attributes else candidate.attrib
            score, checks = 0, 0

            if original_attributes:
                score += sum(
                    SequenceMatcher(None, v, candidate_attributes.get(k, '')).ratio()
                    for k, v in original_attributes.items()
                )
                checks += len(candidate_attributes)
            else:
                if not candidate_attributes:
                    # Both doesn't have attributes, this must mean something
                    score += 1
                    checks += 1

            if match_text:
                score += SequenceMatcher(
                    None, clean_spaces(original.text or ''), clean_spaces(candidate.text or '')
                ).ratio()
                checks += 1

            if checks:
                return round(score / checks, 2) >= similarity_threshold
            return False

        # We will use the elements root from now on to get the speed boost of using Lxml directly
        root = self._root
        current_depth = len(list(root.iterancestors()))
        target_attrs = get_attributes(root) if ignore_attributes else root.attrib
        similar_elements = list()
        # + root.xpath(f"//{self.tag}[count(ancestor::*) = {current_depth-1}]")
        parent = root.getparent()
        if parent is not None:
            grandparent = parent.getparent()  # lol
            if grandparent is not None:
                potential_matches = root.xpath(
                    f"//{grandparent.tag}/{parent.tag}/{self.tag}[count(ancestor::*) = {current_depth}]"
                )
            else:
                potential_matches = root.xpath(f"//{parent.tag}/{self.tag}[count(ancestor::*) = {current_depth}]")
        else:
            potential_matches = root.xpath(f"//{self.tag}[count(ancestor::*) = {current_depth}]")

        for potential_match in potential_matches:
            if potential_match != root and are_alike(root, target_attrs, potential_match):
                similar_elements.append(potential_match)

        return self.__handle_elements(similar_elements)

    def find_by_text(
            self, text: str, first_match: bool = True, partial: bool = False,
            case_sensitive: bool = False, clean_match: bool = True
    ) -> Union['Adaptors[Adaptor]', 'Adaptor']:
        """Find elements that its text content fully/partially matches input.
        :param text: Text query to match
        :param first_match: Return first element that matches conditions, enabled by default
        :param partial: If enabled, function return elements that contains the input text
        :param case_sensitive: if enabled, letters case will be taken into consideration
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        """

        results = Adaptors([])
        if not case_sensitive:
            text = text.lower()

        # This selector gets all elements with text content
        for node in self.__handle_elements(self._root.xpath('.//*[normalize-space(text())]')):
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
            self, query: Union[str, Pattern[str]], first_match: bool = True, case_sensitive: bool = False, clean_match: bool = True
    ) -> Union['Adaptors[Adaptor]', 'Adaptor']:
        """Find elements that its text content matches the input regex pattern.
        :param query: Regex query/pattern to match
        :param first_match: Return first element that matches conditions, enabled by default
        :param case_sensitive: if enabled, letters case will be taken into consideration in the regex
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        """
        results = Adaptors([])

        # This selector gets all elements with text content
        for node in self.__handle_elements(self._root.xpath('.//*[normalize-space(text())]')):
            """Check if element matches given regex otherwise, traverse the children tree and iterate"""
            node_text = node.text
            if node_text.re(query, check_match=True, clean_match=clean_match, case_sensitive=case_sensitive):
                results.append(node)

            if first_match and results:
                # we got an element so we should stop
                break

        if results and first_match:
            return results[0]
        return results


class Adaptors(List[Adaptor]):
    """
    The :class:`Adaptors` class is a subclass of the builtin ``List`` class, which provides a few additional methods.
    """
    __slots__ = ()

    @typing.overload
    def __getitem__(self, pos: SupportsIndex) -> Adaptor:
        pass

    @typing.overload
    def __getitem__(self, pos: slice) -> "Adaptors":
        pass

    def __getitem__(self, pos: Union[SupportsIndex, slice]) -> Union[Adaptor, "Adaptors"]:
        lst = super().__getitem__(pos)
        if isinstance(pos, slice):
            return self.__class__(lst)
        else:
            return lst

    def xpath(
            self, selector: str, identifier: str = '', auto_save: bool = False, percentage: int = 0, **kwargs: Any
    ) -> "Adaptors[Adaptor]":
        """
        Call the ``.xpath()`` method for each element in this list and return
        their results as another :class:`Adaptors`.

        **Important:
        It's recommended to use the identifier argument if you plan to use different selector later
        and want to relocate the same element(s)**

         Note: **Additional keyword arguments will be passed as XPath variables in the XPath expression!**

        :param selector: The XPath selector to be used.
        :param identifier: A string that will be used to retrieve element's data in auto-matching
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `auto_match` later
        :param percentage: The minimum percentage to accept while auto-matching and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure so don't play with this
         number unless you must know what you are doing!

        :return: List as :class:`Adaptors`
        """
        results = [
            n.xpath(selector, identifier or selector, False, auto_save, percentage, **kwargs) for n in self
        ]
        return self.__class__(flatten(results))

    def css(self, selector: str, identifier: str = '', auto_save: bool = False, percentage: int = 0) -> "Adaptors[Adaptor]":
        """
        Call the ``.css()`` method for each element in this list and return
        their results flattened as another :class:`Adaptors`.

        **Important:
        It's recommended to use the identifier argument if you plan to use different selector later
        and want to relocate the same element(s)**

        :param selector: The CSS3 selector to be used.
        :param identifier: A string that will be used to retrieve element's data in auto-matching
         otherwise the selector will be used.
        :param auto_save: Automatically save new elements for `auto_match` later
        :param percentage: The minimum percentage to accept while auto-matching and not going lower than that.
         Be aware that the percentage calculation depends solely on the page structure so don't play with this
         number unless you must know what you are doing!

        :return: List as :class:`Adaptors`
        """
        results = [
            n.css(selector, identifier or selector, False, auto_save, percentage) for n in self
        ]
        return self.__class__(flatten(results))

    def re(self, regex: Union[str, Pattern[str]], replace_entities: bool = True,
           clean_match: bool = False, case_sensitive: bool = False) -> TextHandlers[TextHandler]:
        """Call the ``.re()`` method for each element in this list and return
        their results flattened as List of TextHandler.

        :param regex: Can be either a compiled regular expression or a string.
        :param replace_entities: if enabled character entity references are replaced by their corresponding character
        :param clean_match: if enabled, this will ignore all whitespaces and consecutive spaces while matching
        :param case_sensitive: if enabled, function will set the regex to ignore letters case while compiling it
        """
        results = [
            n.text.re(regex, replace_entities, clean_match, case_sensitive) for n in self
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

    def search(self, func: Callable[['Adaptor'], bool]) -> Union['Adaptor', None]:
        """Loop over all current elements and return the first element that matches the passed function
        :param func: A function that takes each element as an argument and returns True/False
        :return: The first element that match the function or ``None`` otherwise.
        """
        for element in self:
            if func(element):
                return element
        return None

    def filter(self, func: Callable[['Adaptor'], bool]) -> 'Adaptors[Adaptor]':
        """Filter current elements based on the passed function
        :param func: A function that takes each element as an argument and returns True/False
        :return: The new `Adaptors` object or empty list otherwise.
        """
        return self.__class__([
            element for element in self if func(element)
        ])

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

    def __getstate__(self) -> Any:
        # lxml don't like it :)
        raise TypeError("Can't pickle Adaptors object")
