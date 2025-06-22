from msgspec import Struct, convert, ValidationError
from urllib.parse import urlparse

from scrapling.core._types import (
    Optional,
    Union,
    Dict,
    Callable,
    Iterable,
    SelectorWaitStates,
)
from scrapling.engines.toolbelt import construct_proxy_dict


class PlaywrightConfig(Struct, kw_only=True, frozen=False):
    """Configuration struct for validation"""

    max_pages: int = 1
    cdp_url: Optional[str] = None
    headless: bool = True
    google_search: bool = True
    hide_canvas: bool = False
    disable_webgl: bool = False
    real_chrome: bool = False
    stealth: bool = False
    wait: Union[int, float] = 0
    page_action: Optional[Callable] = None
    proxy: Optional[Union[str, Dict[str, str]]] = (
        None  # The default value for proxy in Playwright's source is `None`
    )
    locale: str = "en-US"
    extra_headers: Optional[Dict[str, str]] = None
    useragent: Optional[str] = None
    timeout: Union[int, float] = 30000
    disable_resources: bool = False
    wait_selector: Optional[str] = None
    cookies: Optional[Iterable[Dict]] = None
    network_idle: bool = False
    wait_selector_state: SelectorWaitStates = "attached"
    adaptor_arguments: Optional[Dict] = None

    def __post_init__(self):
        """Custom validation after msgspec validation"""
        if self.max_pages < 1 or self.max_pages > 50:
            raise ValueError("max_pages must be between 1 and 50")
        if self.wait_selector_state not in (
            "attached",
            "detached",
            "hidden",
            "visible",
        ):
            raise ValueError(f"Invalid wait_selector_state: {self.wait_selector_state}")
        if self.timeout < 0:
            raise ValueError("timeout must be >= 0")
        if self.page_action is not None and not callable(self.page_action):
            raise TypeError(
                f"page_action must be callable, got {type(self.page_action).__name__}"
            )
        if self.proxy:
            self.proxy = construct_proxy_dict(self.proxy, as_tuple=True)
        if self.cdp_url:
            self.__validate_cdp(self.cdp_url)

    @staticmethod
    def __validate_cdp(cdp_url):
        try:
            # Check the scheme
            if not cdp_url.startswith(("ws://", "wss://")):
                raise ValueError("CDP URL must use 'ws://' or 'wss://' scheme")

            # Validate hostname and port
            if not urlparse(cdp_url).netloc:
                raise ValueError("Invalid hostname for the CDP URL")

        except AttributeError as e:
            raise ValueError(f"Malformed CDP URL: {cdp_url}: {str(e)}")

        except Exception as e:
            raise ValueError(f"Invalid CDP URL '{cdp_url}': {str(e)}")


def validate(params, model):
    try:
        config = convert(params, model)
    except ValidationError as e:
        raise TypeError(f"Invalid argument type: {e}")

    return config
