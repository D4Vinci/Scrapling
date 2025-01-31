"""
Type definitions for type checking purposes.
"""

from typing import (TYPE_CHECKING, Any, Callable, Dict, Generator, Iterable,
                    List, Literal, Optional, Pattern, Tuple, Type, TypeVar,
                    Union)

SelectorWaitStates = Literal["attached", "detached", "hidden", "visible"]

try:
    from typing import Protocol
except ImportError:
    # Added in Python 3.8
    Protocol = object

try:
    from typing import SupportsIndex
except ImportError:
    # 'SupportsIndex' got added in Python 3.8
    SupportsIndex = None

if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self
else:
    Self = object
