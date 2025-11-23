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
    Iterable,
    List,
    Set,
    Literal,
    Optional,
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
