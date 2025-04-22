import os
import logging
import tempfile
import webbrowser
from functools import wraps

from IPython.terminal.embed import InteractiveShellEmbed

from scrapling import __version__
from scrapling.core.utils import log
from scrapling.parser import Adaptor, Adaptors
from scrapling.fetchers import Fetcher, AsyncFetcher, PlayWrightFetcher, StealthyFetcher


_known_logging_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "fatal": logging.FATAL,
}


def show_page_in_browser(page):
    if not page:
        log.error("Input must be of type `Adaptor`")
        return

    fd, fname = tempfile.mkstemp(".html")
    os.write(fd, page.body.encode("utf-8"))
    os.close(fd)
    webbrowser.open(f"file://{fname}")


class CustomShell:
    """A custom IPython shell with minimal dependencies"""

    def __init__(self, code, log_level="debug"):
        self.code = code
        self.page = None
        self.pages = Adaptors([])
        log_level = log_level.strip().lower()

        if _known_logging_levels.get(log_level):
            self.log_level = _known_logging_levels[log_level]
        else:
            log.error(f'Unknown log level "{log_level}", defaulting to "DEBUG"')
            self.log_level = logging.DEBUG

        self.shell = None

        # Initialize your application components
        self.init_components()

    def init_components(self):
        """Initialize application components"""
        # This is where you'd set up your application-specific objects
        if self.log_level:
            logging.getLogger("scrapling").setLevel(self.log_level)

        settings = Fetcher.display_config()
        _ = settings.pop("storage")
        _ = settings.pop("storage_args")
        log.info(f"Scrapling {__version__} shell started")
        log.info(f"Logging level is set to '{logging.getLevelName(self.log_level)}'")
        log.info(f"Fetchers' parsing settings: {settings}")

    @staticmethod
    def banner():
        """Create a custom banner for the shell"""
        return f"""
-> Available Scrapling objects:
   - Fetcher/AsyncFetcher
   - PlayWrightFetcher
   - StealthyFetcher
   - Adaptor

-> Useful shortcuts:
   - {"get":<30} Shortcut for `Fetcher.get`
   - {"post":<30} Shortcut for `Fetcher.post`
   - {"put":<30} Shortcut for `Fetcher.put`
   - {"delete":<30} Shortcut for `Fetcher.delete`
   - {"fetch":<30} Shortcut for `PlayWrightFetcher.fetch`
   - {"stealthy_fetch":<30} Shortcut for `StealthyFetcher.fetch`

-> Useful commands
   - {"page / response":<30} The response object of the last page you fetched
   - {"pages":<30} Adaptors object of the last 5 response objects you fetched
   - {"view(page)":<30} View page in a browser
   - {"help()":<30} Show this help message (Shell help)

Type 'exit' or press Ctrl+D to exit.
        """

    def update_page(self, result):
        """Update current page and add to pages history"""
        self.page = result
        self.pages.append(result)
        if len(self.pages) > 5:
            self.pages.pop(0)  # Remove oldest item

        # Update in IPython namespace too
        if self.shell:
            self.shell.user_ns["page"] = self.page
            self.shell.user_ns["response"] = self.page
            self.shell.user_ns["pages"] = self.pages

        return result

    def create_wrapper(self, func):
        """Create a wrapper that preserves function signature but updates page"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return self.update_page(result)

        return wrapper

    def get_namespace(self):
        """Create a namespace with application-specific objects"""

        # Create wrapped versions of fetch functions
        get = self.create_wrapper(Fetcher.get)
        post = self.create_wrapper(Fetcher.post)
        put = self.create_wrapper(Fetcher.put)
        delete = self.create_wrapper(Fetcher.delete)
        dynamic_fetch = self.create_wrapper(PlayWrightFetcher.fetch)
        stealthy_fetch = self.create_wrapper(StealthyFetcher.fetch)

        # Create the namespace dictionary
        return {
            "get": get,
            "post": post,
            "put": put,
            "delete": delete,
            "Fetcher": Fetcher,
            "AsyncFetcher": AsyncFetcher,
            "fetch": dynamic_fetch,
            "PlayWrightFetcher": PlayWrightFetcher,
            "stealthy_fetch": stealthy_fetch,
            "StealthyFetcher": StealthyFetcher,
            "Adaptor": Adaptor,
            "page": self.page,
            "response": self.page,
            "pages": self.pages,
            "view": show_page_in_browser,
            "help": self.show_help,
        }

    def show_help(self):
        """Show help information"""
        print(self.banner())

    def start(self):
        """Start the interactive shell"""
        # Create the shell
        ipython_shell = InteractiveShellEmbed(banner1=self.banner(), exit_msg="Bye Bye")

        # Store reference to the shell
        self.shell = ipython_shell

        # Get our namespace with application objects
        namespace = self.get_namespace()

        ipython_shell.user_ns.update(namespace)
        # If a command was provided, execute it and exit
        if self.code:
            # Execute the command in the namespace
            ipython_shell.run_cell(self.code, store_history=False)
            return

        # Start the shell with our namespace
        ipython_shell(local_ns=namespace)
