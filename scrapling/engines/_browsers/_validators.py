from pathlib import Path
from typing import Annotated
from dataclasses import dataclass
from urllib.parse import urlparse

from msgspec import Struct, Meta, convert, ValidationError

from scrapling.core._types import (
    Dict,
    List,
    Tuple,
    Optional,
    Callable,
    Iterable,
    SelectorWaitStates,
    cast,
    overload,
)
from scrapling.engines.toolbelt.navigation import construct_proxy_dict


# Custom validators for msgspec
def _validate_file_path(value: str):
    """Fast file path validation"""
    path = Path(value)
    if not path.exists():
        raise ValueError(f"Init script path not found: {value}")
    if not path.is_file():
        raise ValueError(f"Init script is not a file: {value}")
    if not path.is_absolute():
        raise ValueError(f"Init script is not a absolute path: {value}")


def _validate_addon_path(value: str):
    """Fast addon path validation"""
    path = Path(value)
    if not path.exists():
        raise FileNotFoundError(f"Addon path not found: {value}")
    if not path.is_dir():
        raise ValueError(f"Addon path must be a directory of the extracted addon: {value}")


def _validate_cdp_url(cdp_url: str):
    """Fast CDP URL validation"""
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


# Type aliases for cleaner annotations
PagesCount = Annotated[int, Meta(ge=1, le=50)]
Seconds = Annotated[int, float, Meta(ge=0)]


class PlaywrightConfig(Struct, kw_only=True, frozen=False):
    """Configuration struct for validation"""

    max_pages: PagesCount = 1
    cdp_url: Optional[str] = None
    headless: bool = True
    google_search: bool = True
    hide_canvas: bool = False
    disable_webgl: bool = False
    real_chrome: bool = False
    stealth: bool = False
    wait: Seconds = 0
    page_action: Optional[Callable] = None
    proxy: Optional[str | Dict[str, str] | Tuple] = None  # The default value for proxy in Playwright's source is `None`
    locale: str = "en-US"
    extra_headers: Optional[Dict[str, str]] = None
    useragent: Optional[str] = None
    timeout: Seconds = 30000
    init_script: Optional[str] = None
    disable_resources: bool = False
    wait_selector: Optional[str] = None
    cookies: Optional[Iterable[Dict]] = None
    network_idle: bool = False
    load_dom: bool = True
    wait_selector_state: SelectorWaitStates = "attached"
    selector_config: Optional[Dict] = {}

    def __post_init__(self):
        """Custom validation after msgspec validation"""
        if self.page_action and not callable(self.page_action):
            raise TypeError(f"page_action must be callable, got {type(self.page_action).__name__}")
        if self.proxy:
            self.proxy = construct_proxy_dict(self.proxy, as_tuple=True)
        if self.cdp_url:
            _validate_cdp_url(self.cdp_url)

        if not self.cookies:
            self.cookies = []
        if not self.selector_config:
            self.selector_config = {}

        if self.init_script is not None:
            _validate_file_path(self.init_script)


class CamoufoxConfig(Struct, kw_only=True, frozen=False):
    """Configuration struct for validation"""

    max_pages: PagesCount = 1
    headless: bool = True  # noqa: F821
    block_images: bool = False
    disable_resources: bool = False
    block_webrtc: bool = False
    allow_webgl: bool = True
    network_idle: bool = False
    load_dom: bool = True
    humanize: bool | float = True
    solve_cloudflare: bool = False
    wait: Seconds = 0
    timeout: Seconds = 30000
    init_script: Optional[str] = None
    page_action: Optional[Callable] = None
    wait_selector: Optional[str] = None
    addons: Optional[List[str]] = None
    wait_selector_state: SelectorWaitStates = "attached"
    cookies: Optional[Iterable[Dict]] = None
    google_search: bool = True
    extra_headers: Optional[Dict[str, str]] = None
    proxy: Optional[str | Dict[str, str] | Tuple] = None  # The default value for proxy in Playwright's source is `None`
    os_randomize: bool = False
    disable_ads: bool = False
    geoip: bool = False
    selector_config: Optional[Dict] = {}
    additional_args: Optional[Dict] = {}

    def __post_init__(self):
        """Custom validation after msgspec validation"""
        if self.page_action and not callable(self.page_action):
            raise TypeError(f"page_action must be callable, got {type(self.page_action).__name__}")
        if self.proxy:
            self.proxy = construct_proxy_dict(self.proxy, as_tuple=True)

        if self.addons and isinstance(self.addons, list):
            for addon in self.addons:
                _validate_addon_path(addon)
        else:
            self.addons = []

        if self.init_script is not None:
            _validate_file_path(self.init_script)

        if not self.cookies:
            self.cookies = []
        # Cloudflare timeout adjustment
        if self.solve_cloudflare and self.timeout < 60_000:
            self.timeout = 60_000
        if not self.selector_config:
            self.selector_config = {}
        if not self.additional_args:
            self.additional_args = {}


# Code parts to validate `fetch` in the least possible numbers of lines overall
class FetchConfig(Struct, kw_only=True):
    """Configuration struct for `fetch` calls validation"""

    google_search: bool = True
    timeout: Seconds = 30000
    wait: Seconds = 0
    page_action: Optional[Callable] = None
    extra_headers: Optional[Dict[str, str]] = None
    disable_resources: bool = False
    wait_selector: Optional[str] = None
    wait_selector_state: SelectorWaitStates = "attached"
    network_idle: bool = False
    load_dom: bool = True
    solve_cloudflare: bool = False
    selector_config: Dict = {}

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}


@dataclass
class _fetch_params:
    """A dataclass of all parameters used by `fetch` calls"""

    google_search: bool
    timeout: Seconds
    wait: Seconds
    page_action: Optional[Callable]
    extra_headers: Optional[Dict[str, str]]
    disable_resources: bool
    wait_selector: Optional[str]
    wait_selector_state: SelectorWaitStates
    network_idle: bool
    load_dom: bool
    solve_cloudflare: bool
    selector_config: Dict


def validate_fetch(params: List[Tuple], sentinel=None) -> _fetch_params:
    result = {}
    overrides = {}

    for arg, request_value, session_value in params:
        if request_value is not sentinel:
            overrides[arg] = request_value
        else:
            result[arg] = session_value

    if overrides:
        overrides = cast(FetchConfig, validate(overrides, FetchConfig)).to_dict()
        overrides.update(result)
        return _fetch_params(**overrides)

    if not result.get("solve_cloudflare"):
        result["solve_cloudflare"] = False

    return _fetch_params(**result)


@overload
def validate(params: Dict, model: type[PlaywrightConfig]) -> PlaywrightConfig: ...


@overload
def validate(params: Dict, model: type[CamoufoxConfig]) -> CamoufoxConfig: ...


@overload
def validate(params: Dict, model: type[FetchConfig]) -> FetchConfig: ...


def validate(
    params: Dict, model: type[PlaywrightConfig] | type[CamoufoxConfig] | type[FetchConfig]
) -> PlaywrightConfig | CamoufoxConfig | FetchConfig:
    try:
        return convert(params, model)
    except ValidationError as e:
        raise TypeError(f"Invalid argument type: {e}") from e
