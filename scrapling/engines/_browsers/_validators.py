from pathlib import Path
from typing import Annotated
from functools import lru_cache
from urllib.parse import urlparse
from dataclasses import dataclass, fields

from msgspec import Struct, Meta, convert, ValidationError

from scrapling.core._types import (
    Any,
    Dict,
    List,
    Tuple,
    Optional,
    Callable,
    Iterable,
    SelectorWaitStates,
    overload,
)
from scrapling.engines.toolbelt.navigation import construct_proxy_dict
from scrapling.engines._browsers._types import PlaywrightFetchParams, CamoufoxFetchParams


# Custom validators for msgspec
@lru_cache(8)
def _is_invalid_file_path(value: str) -> bool | str:  # pragma: no cover
    """Fast file path validation"""
    path = Path(value)
    if not path.exists():
        return f"Init script path not found: {value}"
    if not path.is_file():
        return f"Init script is not a file: {value}"
    if not path.is_absolute():
        return f"Init script is not a absolute path: {value}"
    return False


def _validate_addon_path(value: str) -> None:  # pragma: no cover
    """Fast addon path validation"""
    path = Path(value)
    if not path.exists():
        raise FileNotFoundError(f"Addon path not found: {value}")
    if not path.is_dir():
        raise ValueError(f"Addon path must be a directory of the extracted addon: {value}")


@lru_cache(2)
def _is_invalid_cdp_url(cdp_url: str) -> bool | str:
    """Fast CDP URL validation"""
    if not cdp_url.startswith(("ws://", "wss://")):
        return "CDP URL must use 'ws://' or 'wss://' scheme"

    netloc = urlparse(cdp_url).netloc
    if not netloc:  # pragma: no cover
        return "Invalid hostname for the CDP URL"
    return False


# Type aliases for cleaner annotations
PagesCount = Annotated[int, Meta(ge=1, le=50)]
Seconds = Annotated[int, float, Meta(ge=0)]


class PlaywrightConfig(Struct, kw_only=True, frozen=False, weakref=True):
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
    user_data_dir: str = ""
    timezone_id: str = ""
    extra_flags: Optional[List[str]] = None
    selector_config: Optional[Dict] = {}
    additional_args: Optional[Dict] = {}

    def __post_init__(self):  # pragma: no cover
        """Custom validation after msgspec validation"""
        if self.page_action and not callable(self.page_action):
            raise TypeError(f"page_action must be callable, got {type(self.page_action).__name__}")
        if self.proxy:
            self.proxy = construct_proxy_dict(self.proxy, as_tuple=True)
        if self.cdp_url:
            cdp_msg = _is_invalid_cdp_url(self.cdp_url)
            if cdp_msg:
                raise ValueError(cdp_msg)

        if not self.cookies:
            self.cookies = []
        if not self.extra_flags:
            self.extra_flags = []
        if not self.selector_config:
            self.selector_config = {}
        if not self.additional_args:
            self.additional_args = {}

        if self.init_script is not None:
            validation_msg = _is_invalid_file_path(self.init_script)
            if validation_msg:
                raise ValueError(validation_msg)


class CamoufoxConfig(Struct, kw_only=True, frozen=False, weakref=True):
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
    user_data_dir: str = ""
    selector_config: Optional[Dict] = {}
    additional_args: Optional[Dict] = {}

    def __post_init__(self):
        """Custom validation after msgspec validation"""
        if self.page_action and not callable(self.page_action):
            raise TypeError(f"page_action must be callable, got {type(self.page_action).__name__}")
        if self.proxy:
            self.proxy = construct_proxy_dict(self.proxy, as_tuple=True)

        if self.addons:
            for addon in self.addons:
                _validate_addon_path(addon)
        else:
            self.addons = []

        if self.init_script is not None:
            validation_msg = _is_invalid_file_path(self.init_script)
            if validation_msg:
                raise ValueError(validation_msg)

        if not self.cookies:
            self.cookies = []
        # Cloudflare timeout adjustment
        if self.solve_cloudflare and self.timeout < 60_000:
            self.timeout = 60_000
        if not self.selector_config:
            self.selector_config = {}
        if not self.additional_args:
            self.additional_args = {}


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


def validate_fetch(
    method_kwargs: Dict | PlaywrightFetchParams | CamoufoxFetchParams,
    session: Any,
    model: type[PlaywrightConfig] | type[CamoufoxConfig],
) -> _fetch_params:  # pragma: no cover
    result = {}
    overrides = {}

    # Get all field names that _fetch_params needs
    fetch_param_fields = {f.name for f in fields(_fetch_params)}

    for key in fetch_param_fields:
        if key in method_kwargs:
            overrides[key] = method_kwargs[key]
        else:
            # Check for underscore-prefixed attribute (private)
            attr_name = f"_{key}"
            if hasattr(session, attr_name):
                result[key] = getattr(session, attr_name)

    if overrides:
        validated_config = validate(overrides, model)
        # Extract only the fields that _fetch_params needs from validated_config
        validated_dict = {
            f.name: getattr(validated_config, f.name)
            for f in fields(_fetch_params)
            if hasattr(validated_config, f.name)
        }
        validated_dict.setdefault("solve_cloudflare", False)

        # Start with session defaults, then overwrite with validated overrides
        result.update(validated_dict)

    # solve_cloudflare defaults to False for models that don't have it (PlaywrightConfig)
    result.setdefault("solve_cloudflare", False)

    return _fetch_params(**result)


# Cache default values for each model to reduce validation overhead
models_default_values = {}

for _model in (CamoufoxConfig, PlaywrightConfig):
    _defaults = {}
    if hasattr(_model, "__struct_defaults__") and hasattr(_model, "__struct_fields__"):
        for field_name, default_value in zip(_model.__struct_fields__, _model.__struct_defaults__):  # type: ignore
            # Skip factory defaults - these are msgspec._core.Factory instances
            if type(default_value).__name__ != "Factory":
                _defaults[field_name] = default_value

    models_default_values[_model.__name__] = _defaults.copy()


def _filter_defaults(params: Dict, model: str) -> Dict:
    """Filter out parameters that match their default values to reduce validation overhead."""
    defaults = models_default_values[model]
    return {k: v for k, v in params.items() if k not in defaults or v != defaults[k]}


@overload
def validate(params: Dict, model: type[PlaywrightConfig]) -> PlaywrightConfig: ...


@overload
def validate(params: Dict, model: type[CamoufoxConfig]) -> CamoufoxConfig: ...


def validate(params: Dict, model: type[PlaywrightConfig] | type[CamoufoxConfig]) -> PlaywrightConfig | CamoufoxConfig:
    try:
        # Filter out params with the default values (no need to validate them) to speed up validation
        filtered = _filter_defaults(params, model.__name__)
        return convert(filtered, model)
    except ValidationError as e:
        raise TypeError(f"Invalid argument type: {e}") from e
