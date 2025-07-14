"""
Type definitions for type checking purposes.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Pattern,
    Tuple,
    Type,
    TypeVar,
    Union,
    Match,
    Mapping,
    Awaitable,
    Protocol,
    SupportsIndex,
)

SUPPORTED_HTTP_METHODS = Literal["GET", "POST", "PUT", "DELETE"]
SelectorWaitStates = Literal["attached", "detached", "hidden", "visible"]
PageLoadStates = Literal["commit", "domcontentloaded", "load", "networkidle"]
extraction_types = Literal["text", "html", "markdown"]
StrOrBytes = Union[str, bytes]


if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self
else:
    Self = object
