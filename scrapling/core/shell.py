# -*- coding: utf-8 -*-
from sys import stderr
from copy import deepcopy
from functools import wraps
from re import sub as re_sub
from collections import namedtuple
from shlex import split as shlex_split
from inspect import signature, Parameter
from tempfile import mkstemp as make_temp_file
from argparse import ArgumentParser, SUPPRESS
from webbrowser import open as open_in_browser
from urllib.parse import urlparse, urlunparse, parse_qsl
from logging import (
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
    FATAL,
    getLogger,
    getLevelName,
)

from orjson import loads as json_loads, JSONDecodeError

from ._shell_signatures import Signatures_map
from scrapling import __version__
from scrapling.core.utils import log
from scrapling.parser import Selector, Selectors
from scrapling.core.custom_types import TextHandler
from scrapling.engines.toolbelt.custom import Response
from scrapling.core.utils._shell import _ParseHeaders, _CookieParser
from scrapling.core._types import (
    Callable,
    Dict,
    Any,
    cast,
    Optional,
    Generator,
    extraction_types,
)


_known_logging_levels = {
    "debug": DEBUG,
    "info": INFO,
    "warning": WARNING,
    "error": ERROR,
    "critical": CRITICAL,
    "fatal": FATAL,
}


# Define the structure for parsed context - Simplified for Fetcher args
Request = namedtuple(
    "Request",
    [
        "method",
        "url",
        "params",
        "data",  # Can be str, bytes, or dict (for urlencoded)
        "json_data",  # Python object (dict/list) for JSON payload
        "headers",
        "cookies",
        "proxy",
        "follow_redirects",  # Added for -L flag
    ],
)


# Suppress exit on error to handle parsing errors gracefully
class NoExitArgumentParser(ArgumentParser):  # pragma: no cover
    def error(self, message):
        log.error(f"Curl arguments parsing error: {message}")
        raise ValueError(f"Curl arguments parsing error: {message}")

    def exit(self, status=0, message=None):
        if message:
            log.error(f"Scrapling shell exited with status {status}: {message}")
            self._print_message(message, stderr)
        raise ValueError(f"Scrapling shell exited with status {status}: {message or 'Unknown reason'}")


class CurlParser:
    """Builds the argument parser for relevant curl flags from DevTools."""

    def __init__(self) -> None:
        from scrapling.fetchers import Fetcher as __Fetcher

        self.__fetcher = __Fetcher
        # We will use argparse parser to parse the curl command directly instead of regex
        # We will focus more on flags that will show up on curl commands copied from DevTools's network tab
        _parser = NoExitArgumentParser(add_help=False)  # Disable default help
        # Basic curl arguments
        _parser.add_argument("curl_command_placeholder", nargs="?", help=SUPPRESS)
        _parser.add_argument("url")
        _parser.add_argument("-X", "--request", dest="method", default=None)
        _parser.add_argument("-H", "--header", action="append", default=[])
        _parser.add_argument(
            "-A", "--user-agent", help="Will be parsed from -H if present"
        )  # Note: DevTools usually includes this in -H

        # Data arguments (prioritizing types common from DevTools)
        _parser.add_argument("-d", "--data", default=None)
        _parser.add_argument("--data-raw", default=None)  # Often used by browsers for JSON body
        _parser.add_argument("--data-binary", default=None)
        # Keep urlencode for completeness, though less common from browser copy/paste
        _parser.add_argument("--data-urlencode", action="append", default=[])
        _parser.add_argument("-G", "--get", action="store_true")  # Use GET and put data in URL

        _parser.add_argument(
            "-b",
            "--cookie",
            default=None,
            help="Send cookies from string/file (string format used by DevTools)",
        )

        # Proxy
        _parser.add_argument("-x", "--proxy", default=None)
        _parser.add_argument("-U", "--proxy-user", default=None)  # Basic proxy auth

        # Connection/Security
        _parser.add_argument("-k", "--insecure", action="store_true")
        _parser.add_argument("--compressed", action="store_true")  # Very common from browsers

        # Other flags often included but may not map directly to request args
        _parser.add_argument("-i", "--include", action="store_true")
        _parser.add_argument("-s", "--silent", action="store_true")
        _parser.add_argument("-v", "--verbose", action="store_true")

        self.parser: NoExitArgumentParser = _parser
        self._supported_methods = ("get", "post", "put", "delete")

    # --- Main Parsing Logic ---
    def parse(self, curl_command: str) -> Optional[Request]:
        """Parses the curl command string into a structured context for Fetcher."""

        clean_command = curl_command.strip().lstrip("curl").strip().replace("\\\n", " ")

        try:
            tokens = shlex_split(clean_command)  # Split the string using shell-like syntax
        except ValueError as e:  # pragma: no cover
            log.error(f"Could not split command line: {e}")
            return None

        try:
            parsed_args, unknown = self.parser.parse_known_args(tokens)
            if unknown:
                raise AttributeError(f"Unknown/Unsupported curl arguments: {unknown}")

        except ValueError:  # pragma: no cover
            return None

        except AttributeError:
            raise

        except Exception as e:  # pragma: no cover
            log.error(f"An unexpected error occurred during curl arguments parsing: {e}")
            return None

        # --- Determine Method ---
        method = "get"  # Default
        if parsed_args.get:  # `-G` forces GET
            method = "get"

        elif parsed_args.method:
            method = parsed_args.method.strip().lower()

        # Infer POST if data is present (unless overridden by -X or -G)
        elif any(
            [
                parsed_args.data,
                parsed_args.data_raw,
                parsed_args.data_binary,
                parsed_args.data_urlencode,
            ]
        ):
            method = "post"

        headers, cookies = _ParseHeaders(parsed_args.header)

        if parsed_args.cookie:
            # We are focusing on the string format from DevTools.
            try:
                for key, value in _CookieParser(parsed_args.cookie):
                    # Update the cookie dict, potentially overwriting cookies with the same name from -H 'cookie:'
                    cookies[key] = value
                log.debug(f"Parsed cookies from -b argument: {list(cookies.keys())}")
            except Exception as e:  # pragma: no cover
                log.error(f"Could not parse cookie string from -b '{parsed_args.cookie}': {e}")

        # --- Process Data Payload ---
        params = dict()
        data_payload: Optional[str | bytes | Dict] = None
        json_payload: Optional[Any] = None

        # DevTools often uses --data-raw for JSON bodies
        # Precedence: --data-binary > --data-raw / -d > --data-urlencode
        if parsed_args.data_binary is not None:  # pragma: no cover
            try:
                data_payload = parsed_args.data_binary.encode("utf-8")
                log.debug("Using data from --data-binary as bytes.")
            except Exception as e:
                log.warning(
                    f"Could not encode binary data '{parsed_args.data_binary}' as bytes: {e}. Using raw string."
                )
                data_payload = parsed_args.data_binary  # Fallback to string

        elif parsed_args.data_raw is not None:
            data_payload = parsed_args.data_raw.lstrip("$")

        elif parsed_args.data is not None:
            data_payload = parsed_args.data

        elif parsed_args.data_urlencode:  # pragma: no cover
            # Combine and parse urlencoded data
            combined_data = "&".join(parsed_args.data_urlencode)
            try:
                data_payload = dict(parse_qsl(combined_data, keep_blank_values=True))
            except Exception as e:
                log.warning(f"Could not parse urlencoded data '{combined_data}': {e}. Treating as raw string.")
                data_payload = combined_data

        # Check if raw data looks like JSON, prefer 'json' param if so
        if isinstance(data_payload, str):
            try:
                maybe_json = json_loads(data_payload)
                if isinstance(maybe_json, (dict, list)):
                    json_payload = maybe_json
                    data_payload = None
            except JSONDecodeError:
                pass  # Not JSON, keep it in data_payload

        # Handle `-G`: Move data to params if the method is GET
        if method == "get" and data_payload:  # pragma: no cover
            if isinstance(data_payload, dict):  # From --data-urlencode likely
                params.update(data_payload)
            elif isinstance(data_payload, str):
                try:
                    params.update(dict(parse_qsl(data_payload, keep_blank_values=True)))
                except ValueError:
                    log.warning(f"Could not parse data '{data_payload}' into GET parameters for -G.")

            if params:
                data_payload = None  # Clear data as it's moved to params
                json_payload = None  # Should not have JSON body with -G

        # --- Process Proxy ---
        proxies: Optional[Dict[str, str]] = None
        if parsed_args.proxy:
            proxy_url = f"http://{parsed_args.proxy}" if "://" not in parsed_args.proxy else parsed_args.proxy

            if parsed_args.proxy_user:
                user_pass = parsed_args.proxy_user
                parts = urlparse(proxy_url)
                netloc_parts = parts.netloc.split("@")
                netloc = f"{user_pass}@{netloc_parts[-1]}" if len(netloc_parts) > 1 else f"{user_pass}@{parts.netloc}"
                proxy_url = urlunparse(
                    (
                        parts.scheme,
                        netloc,
                        parts.path,
                        parts.params,
                        parts.query,
                        parts.fragment,
                    )
                )

            # Standard proxy dict format
            proxies = {"http": proxy_url, "https": proxy_url}
            log.debug(f"Using proxy configuration: {proxies}")

        # --- Final Context ---
        return Request(
            method=method,
            url=parsed_args.url,
            params=params,
            data=data_payload,
            json_data=json_payload,
            headers=headers,
            cookies=cookies,
            proxy=proxies,
            follow_redirects=True,  # Scrapling default is True
        )

    def convert2fetcher(self, curl_command: Request | str) -> Optional[Response]:
        if isinstance(curl_command, (Request, str)):
            request = self.parse(curl_command) if isinstance(curl_command, str) else curl_command

            # Ensure request parsing was successful before proceeding
            if request is None:  # pragma: no cover
                log.error("Failed to parse curl command, cannot convert to fetcher.")
                return None

            request_args = request._asdict()
            method = request_args.pop("method").strip().lower()
            if method in self._supported_methods:
                request_args["json"] = request_args.pop("json_data")

                # Ensure data/json are removed for non-POST/PUT methods
                if method not in ("post", "put"):
                    _ = request_args.pop("data", None)
                    _ = request_args.pop("json", None)

                try:
                    return getattr(self.__fetcher, method)(**request_args)
                except Exception as e:  # pragma: no cover
                    log.error(f"Error calling Fetcher.{method}: {e}")
                    return None
            else:  # pragma: no cover
                log.error(f'Request method "{method}" isn\'t supported by Scrapling yet')
                return None

        else:  # pragma: no cover
            log.error("Input must be a valid curl command string or a Request object.")
            return None


def _unpack_signature(func, signature_name=None):
    """
    Unpack TypedDict from Unpack[TypedDict] annotations in **kwargs and reconstruct the signature.

    This allows the interactive shell to show individual parameters instead of just **kwargs, similar to how IDEs display them.
    """
    try:
        sig = signature(func)
        func_name = signature_name or getattr(func, "__name__", None)

        # Check if this function has known parameters
        if func_name not in Signatures_map:
            return sig

        new_params = []
        for param in sig.parameters.values():
            if param.kind == Parameter.VAR_KEYWORD:
                # Replace **kwargs with individual keyword-only parameters
                for field_name, field_type in Signatures_map[func_name].items():
                    new_params.append(
                        Parameter(field_name, Parameter.KEYWORD_ONLY, default=Parameter.empty, annotation=field_type)
                    )
            else:
                new_params.append(param)

        # Reconstruct signature with unpacked parameters
        if len(new_params) != len(sig.parameters):
            return sig.replace(parameters=new_params)
        return sig

    except Exception:  # pragma: no cover
        return signature(func)


def show_page_in_browser(page: Selector):  # pragma: no cover
    if not page or not isinstance(page, Selector):
        log.error("Input must be of type `Selector`")
        return

    try:
        fd, fname = make_temp_file(prefix="scrapling_view_", suffix=".html")
        with open(fd, "w", encoding=page.encoding) as f:
            f.write(page.html_content)

        open_in_browser(f"file://{fname}")
    except IOError as e:
        log.error(f"Failed to write temporary file for viewing: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred while viewing the page: {e}")


class CustomShell:
    """A custom IPython shell with minimal dependencies"""

    def __init__(self, code, log_level="debug"):
        from IPython.terminal.embed import InteractiveShellEmbed as __InteractiveShellEmbed
        from scrapling.fetchers import (
            Fetcher as __Fetcher,
            AsyncFetcher as __AsyncFetcher,
            FetcherSession as __FetcherSession,
            DynamicFetcher as __DynamicFetcher,
            DynamicSession as __DynamicSession,
            AsyncDynamicSession as __AsyncDynamicSession,
            StealthyFetcher as __StealthyFetcher,
            StealthySession as __StealthySession,
            AsyncStealthySession as __AsyncStealthySession,
        )

        self.__InteractiveShellEmbed = __InteractiveShellEmbed
        self.__Fetcher = __Fetcher
        self.__AsyncFetcher = __AsyncFetcher
        self.__FetcherSession = __FetcherSession
        self.__DynamicFetcher = __DynamicFetcher
        self.__DynamicSession = __DynamicSession
        self.__AsyncDynamicSession = __AsyncDynamicSession
        self.__StealthyFetcher = __StealthyFetcher
        self.__StealthySession = __StealthySession
        self.__AsyncStealthySession = __AsyncStealthySession
        self.code = code
        self.page = None
        self.pages = Selectors([])
        self._curl_parser = CurlParser()
        log_level = log_level.strip().lower()

        if _known_logging_levels.get(log_level):
            self.log_level = _known_logging_levels[log_level]
        else:  # pragma: no cover
            log.warning(f'Unknown log level "{log_level}", defaulting to "DEBUG"')
            self.log_level = DEBUG

        self.shell = None

        # Initialize your application components
        self.init_components()

    def init_components(self):
        """Initialize application components"""
        # This is where you'd set up your application-specific objects
        if self.log_level:
            getLogger("scrapling").setLevel(self.log_level)

        settings = self.__Fetcher.display_config()
        settings.pop("storage", None)
        settings.pop("storage_args", None)
        log.info(f"Scrapling {__version__} shell started")
        log.info(f"Logging level is set to '{getLevelName(self.log_level)}'")
        log.info(f"Fetchers' parsing settings: {settings}")

    @staticmethod
    def banner():
        """Create a custom banner for the shell"""
        return f"""
-> Available Scrapling objects:
   - Fetcher/AsyncFetcher/FetcherSession
   - DynamicFetcher/DynamicSession/AsyncDynamicSession
   - StealthyFetcher/StealthySession/AsyncStealthySession
   - Selector

-> Useful shortcuts:
   - {"get":<30} Shortcut for `Fetcher.get`
   - {"post":<30} Shortcut for `Fetcher.post`
   - {"put":<30} Shortcut for `Fetcher.put`
   - {"delete":<30} Shortcut for `Fetcher.delete`
   - {"fetch":<30} Shortcut for `DynamicFetcher.fetch`
   - {"stealthy_fetch":<30} Shortcut for `StealthyFetcher.fetch`

-> Useful commands
   - {"page / response":<30} The response object of the last page you fetched
   - {"pages":<30} Selectors object of the last 5 response objects you fetched
   - {"uncurl('curl_command')":<30} Convert curl command to a Request object. (Optimized to handle curl commands copied from DevTools network tab.)
   - {"curl2fetcher('curl_command')":<30} Convert curl command and make the request with Fetcher. (Optimized to handle curl commands copied from DevTools network tab.)
   - {"view(page)":<30} View page in a browser
   - {"help()":<30} Show this help message (Shell help)

Type 'exit' or press Ctrl+D to exit.
        """

    def update_page(self, result):  # pragma: no cover
        """Update the current page and add to pages history"""
        self.page = result
        if isinstance(result, (Response, Selector)):
            self.pages.append(result)
            if len(self.pages) > 5:
                self.pages.pop(0)  # Remove the oldest item

            # Update in IPython namespace too
            if self.shell:
                self.shell.user_ns["page"] = self.page
                self.shell.user_ns["response"] = self.page
                self.shell.user_ns["pages"] = self.pages

        return result

    def create_wrapper(
        self, func: Callable, get_signature: bool = True, signature_name: Optional[str] = None
    ) -> Callable:
        """Create a wrapper that preserves function signature but updates page"""

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            return self.update_page(result)

        if get_signature:
            # Explicitly preserve and unpack signature for IPython introspection and autocompletion
            setattr(wrapper, "__signature__", _unpack_signature(func, signature_name))
        else:
            setattr(wrapper, "__signature__", signature(func))

        return wrapper

    def get_namespace(self):
        """Create a namespace with application-specific objects"""

        # Create wrapped versions of fetch functions
        get = self.create_wrapper(self.__Fetcher.get)
        post = self.create_wrapper(self.__Fetcher.post)
        put = self.create_wrapper(self.__Fetcher.put)
        delete = self.create_wrapper(self.__Fetcher.delete)
        dynamic_fetch = self.create_wrapper(self.__DynamicFetcher.fetch)
        stealthy_fetch = self.create_wrapper(self.__StealthyFetcher.fetch, signature_name="stealthy_fetch")
        curl2fetcher = self.create_wrapper(self._curl_parser.convert2fetcher, get_signature=False)

        # Create the namespace dictionary
        return {
            "get": get,
            "post": post,
            "put": put,
            "delete": delete,
            "Fetcher": self.__Fetcher,
            "AsyncFetcher": self.__AsyncFetcher,
            "FetcherSession": self.__FetcherSession,
            "DynamicSession": self.__DynamicSession,
            "AsyncDynamicSession": self.__AsyncDynamicSession,
            "StealthySession": self.__StealthySession,
            "AsyncStealthySession": self.__AsyncStealthySession,
            "fetch": dynamic_fetch,
            "DynamicFetcher": self.__DynamicFetcher,
            "stealthy_fetch": stealthy_fetch,
            "StealthyFetcher": self.__StealthyFetcher,
            "Selector": Selector,
            "page": self.page,
            "response": self.page,
            "pages": self.pages,
            "view": show_page_in_browser,
            "uncurl": self._curl_parser.parse,
            "curl2fetcher": curl2fetcher,
            "help": self.show_help,
        }

    def show_help(self):  # pragma: no cover
        """Show help information"""
        print(self.banner())

    def start(self):  # pragma: no cover
        """Start the interactive shell"""

        # Get our namespace with application objects
        namespace = self.get_namespace()
        ipython_shell = self.__InteractiveShellEmbed(
            banner1=self.banner(),
            banner2="",
            enable_tip=False,
            exit_msg="Bye Bye",
            user_ns=namespace,
        )
        self.shell = ipython_shell

        # If a command was provided, execute it and exit
        if self.code:
            log.info(f"Executing provided code: {self.code}")
            try:
                ipython_shell.run_cell(self.code, store_history=False)
            except Exception as e:
                log.error(f"Error executing initial code: {e}")
            return

        ipython_shell()


class Convertor:
    """Utils for the extract shell command"""

    _extension_map: Dict[str, extraction_types] = {
        "md": "markdown",
        "html": "html",
        "txt": "text",
    }

    @classmethod
    def _convert_to_markdown(cls, body: TextHandler) -> str:
        """Convert HTML content to Markdown"""
        from markdownify import markdownify

        return markdownify(body)

    @classmethod
    def _strip_noise_tags(cls, page: Selector) -> Selector:
        """Return a copy of the Selector with noise tags removed."""
        clean_root = deepcopy(page._root)
        for element in clean_root.iter(*{"script", "style", "noscript", "svg"}):
            element.drop_tree()
        return Selector(root=clean_root, url=page.url)

    @classmethod
    def _extract_content(
        cls,
        page: Selector,
        extraction_type: extraction_types = "markdown",
        css_selector: Optional[str] = None,
        main_content_only: bool = False,
    ) -> Generator[str, None, None]:
        """Extract the content of a Selector"""
        if not page or not isinstance(page, Selector):  # pragma: no cover
            raise TypeError("Input must be of type `Selector`")
        elif not extraction_type or extraction_type not in cls._extension_map.values():
            raise ValueError(f"Unknown extraction type: {extraction_type}")
        else:
            if main_content_only:
                page = cast(Selector, page.css("body").first) or page
                page = cls._strip_noise_tags(page)

            pages = [page] if not css_selector else cast(Selectors, page.css(css_selector))
            for page in pages:
                match extraction_type:
                    case "markdown":
                        yield cls._convert_to_markdown(page.html_content)
                    case "html":
                        yield page.html_content
                    case "text":
                        txt_content = page.get_all_text(
                            strip=True, ignore_tags=("script", "style", "noscript", "svg", "iframe")
                        )
                        for s in (
                            "\n",
                            "\r",
                            "\t",
                            " ",
                        ):
                            # Remove consecutive white-spaces
                            txt_content = TextHandler(re_sub(f"[{s}]+", s, txt_content))
                        yield txt_content
            yield ""

    @classmethod
    def write_content_to_file(cls, page: Selector, filename: str, css_selector: Optional[str] = None) -> None:
        """Write a Selector's content to a file"""
        if not page or not isinstance(page, Selector):  # pragma: no cover
            raise TypeError("Input must be of type `Selector`")
        elif not filename or not isinstance(filename, str) or not filename.strip():
            raise ValueError("Filename must be provided")
        elif not filename.endswith((".md", ".html", ".txt")):
            raise ValueError("Unknown file type: filename must end with '.md', '.html', or '.txt'")
        else:
            with open(filename, "w", encoding=page.encoding) as f:
                extension = filename.split(".")[-1]
                f.write(
                    "".join(
                        cls._extract_content(
                            page,
                            cls._extension_map[extension],
                            css_selector=css_selector,
                        )
                    )
                )
