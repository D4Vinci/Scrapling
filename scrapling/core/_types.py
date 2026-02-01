"""
Type definitions for type checking purposes.
"""

from typing import (
    TYPE_CHECKING,
    TypedDict,
    TypeAlias,
    cast,
    overload,
    Any,
    Callable,
    Dict,
    Generator,
    AsyncGenerator,
    Generic,
    Iterable,
    List,
    Set,
    Literal,
    Optional,
    Iterator,
    Pattern,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    Match,
    Mapping,
    Awaitable,
    Protocol,
    Coroutine,
    SupportsIndex,
)

# Proxy can be a string URL or a dict (Playwright format: {"server": "...", "username": "...", "password": "..."})
ProxyType = Union[str, Dict[str, str]]
SUPPORTED_HTTP_METHODS = Literal["GET", "POST", "PUT", "DELETE"]
SelectorWaitStates = Literal["attached", "detached", "hidden", "visible"]
PageLoadStates = Literal["commit", "domcontentloaded", "load", "networkidle"]
extraction_types = Literal["text", "html", "markdown"]
StrOrBytes = Union[str, bytes]

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Unpack
else:  # pragma: no cover

    class _Unpack:
        @staticmethod
        def __getitem__(*args, **kwargs):
            pass

    Unpack = _Unpack()


try:
    # Python 3.11+
    from typing import Self  # novermin
except ImportError:  # pragma: no cover
    try:
        from typing_extensions import Self  # Backport
    except ImportError:
        Self = object


# Copied from `playwright._impl._api_structures.SetCookieParam`
class SetCookieParam(TypedDict, total=False):
    name: str
    value: str
    url: Optional[str]
    domain: Optional[str]
    path: Optional[str]
    expires: Optional[float]
    httpOnly: Optional[bool]
    secure: Optional[bool]
    sameSite: Optional[Literal["Lax", "None", "Strict"]]
    partitionKey: Optional[str]
