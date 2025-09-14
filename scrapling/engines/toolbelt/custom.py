"""
Functions related to custom types or type checking
"""

from functools import lru_cache
from email.message import Message

from scrapling.core.utils import log
from scrapling.core._types import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)
from scrapling.core.custom_types import MappingProxyType
from scrapling.parser import Selector, SQLiteStorageSystem


class Response(Selector):
    """This class is returned by all engines as a way to unify response type between different libraries."""

    def __init__(
        self,
        url: str,
        content: str | bytes,
        status: int,
        reason: str,
        cookies: Tuple[Dict[str, str], ...] | Dict[str, str],
        headers: Dict,
        request_headers: Dict,
        encoding: str = "utf-8",
        method: str = "GET",
        history: List = None,
        **selector_config: Dict,
    ):
        adaptive_domain = selector_config.pop("adaptive_domain", None)
        self.status = status
        self.reason = reason
        self.cookies = cookies
        self.headers = headers
        self.request_headers = request_headers
        self.history = history or []
        super().__init__(
            content=content,
            url=adaptive_domain or url,
            encoding=encoding,
            **selector_config,
        )
        # For easier debugging while working from a Python shell
        log.info(f"Fetched ({status}) <{method} {url}> (referer: {request_headers.get('referer')})")


class BaseFetcher:
    __slots__ = ()
    huge_tree: bool = True
    adaptive: Optional[bool] = False
    storage: Any = SQLiteStorageSystem
    keep_cdata: Optional[bool] = False
    storage_args: Optional[Dict] = None
    keep_comments: Optional[bool] = False
    adaptive_domain: Optional[str] = None
    parser_keywords: Tuple = (
        "huge_tree",
        "adaptive",
        "storage",
        "keep_cdata",
        "storage_args",
        "keep_comments",
        "adaptive_domain",
    )  # Left open for the user

    def __init__(self, *args, **kwargs):
        # For backward-compatibility before 0.2.99
        args_str = ", ".join(args) or ""
        kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items()) or ""
        if args_str:
            args_str += ", "

        log.warning(
            f"This logic is deprecated now, and have no effect; It will be removed with v0.3. Use `{self.__class__.__name__}.configure({args_str}{kwargs_str})` instead before fetching"
        )
        pass

    @classmethod
    def display_config(cls):
        return dict(
            huge_tree=cls.huge_tree,
            keep_comments=cls.keep_comments,
            keep_cdata=cls.keep_cdata,
            adaptive=cls.adaptive,
            storage=cls.storage,
            storage_args=cls.storage_args,
            adaptive_domain=cls.adaptive_domain,
        )

    @classmethod
    def configure(cls, **kwargs):
        """Set multiple arguments for the parser at once globally

        :param kwargs: The keywords can be any arguments of the following: huge_tree, keep_comments, keep_cdata, adaptive, storage, storage_args, adaptive_domain
        """
        for key, value in kwargs.items():
            key = key.strip().lower()
            if hasattr(cls, key):
                if key in cls.parser_keywords:
                    setattr(cls, key, value)
                else:
                    # Yup, no fun allowed LOL
                    raise AttributeError(f'Unknown parser argument: "{key}"; maybe you meant {cls.parser_keywords}?')
            else:
                raise ValueError(f'Unknown parser argument: "{key}"; maybe you meant {cls.parser_keywords}?')

        if not kwargs:
            raise AttributeError(f"You must pass a keyword to configure, current keywords: {cls.parser_keywords}?")

    @classmethod
    def _generate_parser_arguments(cls) -> Dict:
        # Selector class parameters
        # I won't validate Selector's class parameters here again, I will leave it to be validated later
        parser_arguments = dict(
            huge_tree=cls.huge_tree,
            keep_comments=cls.keep_comments,
            keep_cdata=cls.keep_cdata,
            adaptive=cls.adaptive,
            storage=cls.storage,
            storage_args=cls.storage_args,
        )
        if cls.adaptive_domain:
            if not isinstance(cls.adaptive_domain, str):
                log.warning('[Ignored] The argument "adaptive_domain" must be of string type')
            else:
                parser_arguments.update({"adaptive_domain": cls.adaptive_domain})

        return parser_arguments


class StatusText:
    """A class that gets the status text of response status code.

    Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    """

    _phrases = MappingProxyType(
        {
            100: "Continue",
            101: "Switching Protocols",
            102: "Processing",
            103: "Early Hints",
            200: "OK",
            201: "Created",
            202: "Accepted",
            203: "Non-Authoritative Information",
            204: "No Content",
            205: "Reset Content",
            206: "Partial Content",
            207: "Multi-Status",
            208: "Already Reported",
            226: "IM Used",
            300: "Multiple Choices",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            305: "Use Proxy",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            402: "Payment Required",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            407: "Proxy Authentication Required",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            412: "Precondition Failed",
            413: "Payload Too Large",
            414: "URI Too Long",
            415: "Unsupported Media Type",
            416: "Range Not Satisfiable",
            417: "Expectation Failed",
            418: "I'm a teapot",
            421: "Misdirected Request",
            422: "Unprocessable Entity",
            423: "Locked",
            424: "Failed Dependency",
            425: "Too Early",
            426: "Upgrade Required",
            428: "Precondition Required",
            429: "Too Many Requests",
            431: "Request Header Fields Too Large",
            451: "Unavailable For Legal Reasons",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            505: "HTTP Version Not Supported",
            506: "Variant Also Negotiates",
            507: "Insufficient Storage",
            508: "Loop Detected",
            510: "Not Extended",
            511: "Network Authentication Required",
        }
    )

    @classmethod
    @lru_cache(maxsize=128)
    def get(cls, status_code: int) -> str:
        """Get the phrase for a given HTTP status code."""
        return cls._phrases.get(status_code, "Unknown Status Code")


def get_variable_name(var: Any) -> Optional[str]:
    """Get the name of a variable using global and local scopes.
    :param var: The variable to find the name for
    :return: The name of the variable if found, None otherwise
    """
    for scope in [globals(), locals()]:
        for name, value in scope.items():
            if value is var:
                return name
    return None
