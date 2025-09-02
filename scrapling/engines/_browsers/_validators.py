from msgspec import Struct, convert, ValidationError
from urllib.parse import urlparse
from pathlib import Path

from scrapling.core._types import (
    Optional,
    Dict,
    Callable,
    List,
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
    wait: int | float = 0
    page_action: Optional[Callable] = None
    proxy: Optional[str | Dict[str, str]] = (
        None  # The default value for proxy in Playwright's source is `None`
    )
    locale: str = "en-US"
    extra_headers: Optional[Dict[str, str]] = None
    useragent: Optional[str] = None
    timeout: int | float = 30000
    init_script: Optional[str] = None
    disable_resources: bool = False
    wait_selector: Optional[str] = None
    cookies: Optional[List[Dict]] = None
    network_idle: bool = False
    wait_selector_state: SelectorWaitStates = "attached"
    selector_config: Optional[Dict] = None

    def __post_init__(self):
        """Custom validation after msgspec validation"""
        if self.max_pages < 1 or self.max_pages > 50:
            raise ValueError("max_pages must be between 1 and 50")
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
        if not self.cookies:
            self.cookies = []
        if not self.selector_config:
            self.selector_config = {}

        if self.init_script is not None:
            script_path = Path(self.init_script)
            if not script_path.exists():
                raise ValueError("Init script path not found")
            elif not script_path.is_file():
                raise ValueError("Init script is not a file")
            elif not script_path.is_absolute():
                raise ValueError("Init script is not a absolute path")

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


class CamoufoxConfig(Struct, kw_only=True, frozen=False):
    """Configuration struct for validation"""

    max_pages: int = 1
    headless: bool = True  # noqa: F821
    block_images: bool = False
    disable_resources: bool = False
    block_webrtc: bool = False
    allow_webgl: bool = True
    network_idle: bool = False
    humanize: bool | float = True
    solve_cloudflare: bool = False
    wait: int | float = 0
    timeout: int | float = 30000
    init_script: Optional[str] = None
    page_action: Optional[Callable] = None
    wait_selector: Optional[str] = None
    addons: Optional[List[str]] = None
    wait_selector_state: SelectorWaitStates = "attached"
    cookies: Optional[List[Dict]] = None
    google_search: bool = True
    extra_headers: Optional[Dict[str, str]] = None
    proxy: Optional[str | Dict[str, str]] = (
        None  # The default value for proxy in Playwright's source is `None`
    )
    os_randomize: bool = False
    disable_ads: bool = False
    geoip: bool = False
    selector_config: Optional[Dict] = None
    additional_args: Optional[Dict] = None

    def __post_init__(self):
        """Custom validation after msgspec validation"""
        if self.max_pages < 1 or self.max_pages > 50:
            raise ValueError("max_pages must be between 1 and 50")
        if self.timeout < 0:
            raise ValueError("timeout must be >= 0")
        if self.page_action is not None and not callable(self.page_action):
            raise TypeError(
                f"page_action must be callable, got {type(self.page_action).__name__}"
            )
        if self.proxy:
            self.proxy = construct_proxy_dict(self.proxy, as_tuple=True)

        if not self.addons:
            self.addons = []
        else:
            for addon in self.addons:
                addon_path = Path(addon)
                if not addon_path.exists():
                    raise FileNotFoundError(f"Addon's path not found: {addon}")
                elif not addon_path.is_dir():
                    raise ValueError(
                        f"Addon's path is not a folder, you need to pass a folder of the extracted addon: {addon}"
                    )

        if self.init_script is not None:
            script_path = Path(self.init_script)
            if not script_path.exists():
                raise ValueError("Init script path not found")
            elif not script_path.is_file():
                raise ValueError("Init script is not a file")
            elif not script_path.is_absolute():
                raise ValueError("Init script is not a absolute path")

        if not self.cookies:
            self.cookies = []
        if self.solve_cloudflare and self.timeout < 60_000:
            self.timeout = 60_000
        if not self.selector_config:
            self.selector_config = {}
        if not self.additional_args:
            self.additional_args = {}


def validate(params, model):
    try:
        config = convert(params, model)
    except ValidationError as e:
        raise TypeError(f"Invalid argument type: {e}")

    return config
