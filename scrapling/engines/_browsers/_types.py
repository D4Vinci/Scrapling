from io import BytesIO

from curl_cffi.requests import (
    ProxySpec,
    CookieTypes,
    BrowserTypeLiteral,
)

from scrapling.core._types import (
    Dict,
    List,
    Tuple,
    Mapping,
    Optional,
    Callable,
    Sequence,
    TypedDict,
    TypeAlias,
    SetCookieParam,
    SelectorWaitStates,
    TYPE_CHECKING,
)
from scrapling.engines.toolbelt.proxy_rotation import ProxyRotator

# Type alias for `impersonate` parameter - accepts a single browser or list of browsers
ImpersonateType: TypeAlias = BrowserTypeLiteral | List[BrowserTypeLiteral] | None


if TYPE_CHECKING:  # pragma: no cover
    # Types for session initialization
    class RequestsSession(TypedDict, total=False):
        impersonate: ImpersonateType
        http3: Optional[bool]
        stealthy_headers: Optional[bool]
        proxies: Optional[ProxySpec]
        proxy: Optional[str]
        proxy_auth: Optional[Tuple[str, str]]
        proxy_rotator: Optional[ProxyRotator]
        timeout: Optional[int | float]
        headers: Optional[Mapping[str, Optional[str]]]
        retries: Optional[int]
        retry_delay: Optional[int]
        follow_redirects: Optional[bool]
        max_redirects: Optional[int]
        verify: Optional[bool]
        cert: Optional[str | Tuple[str, str]]
        selector_config: Optional[Dict]

    # Types for GET request method parameters
    class GetRequestParams(RequestsSession, total=False):
        params: Optional[Dict | List | Tuple]
        cookies: Optional[CookieTypes]
        auth: Optional[Tuple[str, str]]

    # Types for POST/PUT/DELETE request method parameters
    class DataRequestParams(GetRequestParams, total=False):
        data: Optional[Dict[str, str] | List[Tuple] | str | BytesIO | bytes]
        json: Optional[Dict | List]

    # Types for browser session
    class PlaywrightSession(TypedDict, total=False):
        max_pages: int
        headless: bool
        disable_resources: bool
        network_idle: bool
        load_dom: bool
        wait_selector: Optional[str]
        wait_selector_state: SelectorWaitStates
        cookies: Sequence[SetCookieParam] | None
        google_search: bool
        wait: int | float
        timezone_id: str | None
        page_action: Optional[Callable]
        proxy: Optional[str | Dict[str, str] | Tuple]
        proxy_rotator: Optional[ProxyRotator]
        extra_headers: Optional[Dict[str, str]]
        timeout: int | float
        init_script: Optional[str]
        user_data_dir: str
        selector_config: Optional[Dict]
        additional_args: Optional[Dict]
        locale: Optional[str]
        real_chrome: bool
        cdp_url: Optional[str]
        useragent: Optional[str]
        extra_flags: Optional[List[str]]
        retries: int
        retry_delay: int | float

    class PlaywrightFetchParams(TypedDict, total=False):
        load_dom: bool
        wait: int | float
        network_idle: bool
        google_search: bool
        timeout: int | float
        disable_resources: bool
        wait_selector: Optional[str]
        page_action: Optional[Callable]
        selector_config: Optional[Dict]
        extra_headers: Optional[Dict[str, str]]
        wait_selector_state: SelectorWaitStates

    class StealthSession(PlaywrightSession, total=False):
        allow_webgl: bool
        hide_canvas: bool
        block_webrtc: bool
        solve_cloudflare: bool

    class StealthFetchParams(PlaywrightFetchParams, total=False):
        solve_cloudflare: bool

else:  # pragma: no cover
    RequestsSession = TypedDict
    GetRequestParams = TypedDict
    DataRequestParams = TypedDict
    PlaywrightSession = TypedDict
    PlaywrightFetchParams = TypedDict
    StealthSession = TypedDict
    StealthFetchParams = TypedDict
