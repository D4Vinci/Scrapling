"""
Functions related to custom types or type checking
"""
import inspect
import logging

from scrapling.core.utils import setup_basic_logging
from scrapling.parser import Adaptor, SQLiteStorageSystem
from scrapling.core._types import Any, List, Type, Union, Optional, Dict, Callable


class Response(Adaptor):
    """This class is returned by all engines as a way to unify response type between different libraries."""

    def __init__(self, url: str, text: str, content: bytes, status: int, reason: str, cookies: Dict, headers: Dict, request_headers: Dict, adaptor_arguments: Dict, encoding: str = 'utf-8'):
        automatch_domain = adaptor_arguments.pop('automatch_domain', None)
        super().__init__(text=text, body=content, url=automatch_domain or url, encoding=encoding, **adaptor_arguments)

        self.status = status
        self.reason = reason
        self.cookies = cookies
        self.headers = headers
        self.request_headers = request_headers
        # For back-ward compatibility
        self.adaptor = self

    # def __repr__(self):
    #     return f'<{self.__class__.__name__} [{self.status} {self.reason}]>'


class BaseFetcher:
    def __init__(
            self, huge_tree: bool = True, keep_comments: Optional[bool] = False, auto_match: Optional[bool] = True,
            storage: Any = SQLiteStorageSystem, storage_args: Optional[Dict] = None, debug: Optional[bool] = True,
            automatch_domain: Optional[str] = None,
    ):
        """Arguments below are the same from the Adaptor class so you can pass them directly, the rest of Adaptor's arguments
        are detected and passed automatically from the Fetcher based on the response for accessibility.

        :param huge_tree: Enabled by default, should always be enabled when parsing large HTML documents. This controls
            libxml2 feature that forbids parsing certain large documents to protect from possible memory exhaustion.
        :param keep_comments: While parsing the HTML body, drop comments or not. Disabled by default for obvious reasons
        :param auto_match: Globally turn-off the auto-match feature in all functions, this argument takes higher
            priority over all auto-match related arguments/functions in the class.
        :param storage: The storage class to be passed for auto-matching functionalities, see ``Docs`` for more info.
        :param storage_args: A dictionary of ``argument->value`` pairs to be passed for the storage class.
            If empty, default values will be used.
        :param automatch_domain: For cases where you want to automatch selectors across different websites as if they were on the same website, use this argument to unify them.
            Otherwise, the domain of the request is used by default.
        :param debug: Enable debug mode
        """
        # Adaptor class parameters
        # I won't validate Adaptor's class parameters here again, I will leave it to be validated later
        self.adaptor_arguments = dict(
            huge_tree=huge_tree,
            keep_comments=keep_comments,
            auto_match=auto_match,
            storage=storage,
            storage_args=storage_args,
            debug=debug,
        )
        # If the user used fetchers first, then configure the logger from here instead of the `Adaptor` class
        setup_basic_logging(level='debug' if debug else 'info')
        if automatch_domain:
            if type(automatch_domain) is not str:
                logging.warning('[Ignored] The argument "automatch_domain" must be of string type')
            else:
                self.adaptor_arguments.update({'automatch_domain': automatch_domain})


def check_if_engine_usable(engine: Callable) -> Union[Callable, None]:
    """This function check if the passed engine can be used by a Fetcher-type class or not.

    :param engine: The engine class itself
    :return: The engine class again if all checks out, otherwise raises error
    :raise TypeError: If engine class don't have fetch method, If engine class have fetch attribute not method, or If engine class have fetch function but it doesn't take arguments
    """
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
