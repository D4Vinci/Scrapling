"""
Functions related to custom types or type checking
"""
import inspect
import logging
from dataclasses import dataclass, field

from scrapling.parser import Adaptor, SQLiteStorageSystem
from scrapling.core._types import Any, List, Type, Union, Optional, Dict


@dataclass(frozen=True)
class Response:
    url: str
    text: str
    content: bytes
    status: int
    reason: str
    encoding: str = 'utf-8'  # default encoding
    cookies: Dict = field(default_factory=dict)
    headers: Dict = field(default_factory=dict)
    request_headers: Dict = field(default_factory=dict)
    adaptor_arguments: Dict = field(default_factory=dict)

    @property
    def adaptor(self):
        if self.content:
            return Adaptor(body=self.content, url=self.url, encoding=self.encoding, **self.adaptor_arguments)
        elif self.text:
            return Adaptor(text=self.text, url=self.url, encoding=self.encoding, **self.adaptor_arguments)
        return None

    def __repr__(self):
        return f'<{self.__class__.__name__} [{self.status} {self.reason}]>'


class BaseFetcher:
    def __init__(
            self,
            # Adaptor class parameters
            huge_tree: bool = True,
            keep_comments: Optional[bool] = False,
            auto_match: Optional[bool] = False,
            storage: Any = SQLiteStorageSystem,
            storage_args: Optional[Dict] = None,
            debug: Optional[bool] = True,
    ):
        # I won't validate Adaptor's class parameters here again, I will leave it to be validated later
        self.adaptor_arguments = dict(
            huge_tree=huge_tree,
            keep_comments=keep_comments,
            auto_match=auto_match,
            storage=storage,
            storage_args=storage_args,
            debug=debug,
        )


def check_if_engine_usable(engine):
    # if isinstance(engine, type):
    #     raise TypeError("Expected an engine instance, not a class definition of the engine")

    if hasattr(engine, 'fetch'):
        fetch_function = getattr(engine, "fetch")
        if callable(fetch_function):
            if len(inspect.signature(fetch_function).parameters) > 0:
                return engine
            else:
                # raise TypeError("Engine class instance must have a callable method 'fetch' with the first argument used for the url.")
                raise TypeError("Engine class must have a callable method 'fetch' with the first argument used for the url.")
        else:
            # raise TypeError("Invalid engine instance! Engine class must have a callable method 'fetch'")
            raise TypeError("Invalid engine class! Engine class must have a callable method 'fetch'")
    else:
        # raise TypeError("Invalid engine instance! Engine class must have the method 'fetch'")
        raise TypeError("Invalid engine class! Engine class must have the method 'fetch'")


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


def check_type_validity(variable: Any, valid_types: Union[List[Type], None], default_value: Any = None, critical: bool = False, param_name: Optional[str] = None) -> Any:
    """Check if a variable matches the specified type constraints.
    :param variable: The variable to check
    :param valid_types: List of valid types for the variable
    :param default_value: Value to return if type check fails
    :param critical: If True, raises TypeError instead of logging error
    :param param_name: Optional parameter name for error messages
    :return: The original variable if valid, default_value if invalid
    :raise TypeError: If critical=True and type check fails
    """
    # Use provided param_name or try to get it automatically
    var_name = param_name or get_variable_name(variable) or "Unknown"

    # Convert valid_types to a list if None
    valid_types = valid_types or []

    # Handle None value
    if variable is None:
        if type(None) in valid_types:
            return variable
        error_msg = f'Argument "{var_name}" cannot be None'
        if critical:
            raise TypeError(error_msg)
        logging.error(f'[Ignored] {error_msg}')
        return default_value

    # If no valid_types specified and variable has a value, return it
    if not valid_types:
        return variable

    # Check if variable type matches any of the valid types
    if not any(isinstance(variable, t) for t in valid_types):
        type_names = [t.__name__ for t in valid_types]
        error_msg = f'Argument "{var_name}" must be of type {" or ".join(type_names)}'
        if critical:
            raise TypeError(error_msg)
        logging.error(f'[Ignored] {error_msg}')
        return default_value

    return variable


# Pew Pew
def do_nothing(page):
    # Just works as a filler for `page_action` argument in browser engines
    return page
