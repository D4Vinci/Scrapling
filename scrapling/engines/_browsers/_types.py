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
    Iterable,
    TypedDict,
    TypeAlias,
    SelectorWaitStates,
    TYPE_CHECKING,
)

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
        data: Optional[Dict | str]
        json: Optional[Dict | List]

    # Types for browser session
    class BrowserSession(TypedDict, total=False):
        max_pages: int
        headless: bool
        disable_resources: bool
        network_idle: bool
        load_dom: bool
        wait_selector: Optional[str]
        wait_selector_state: SelectorWaitStates
        cookies: Optional[Iterable[Dict]]
        google_search: bool
        wait: int | float
        page_action: Optional[Callable]
        proxy: Optional[str | Dict[str, str] | Tuple]
        extra_headers: Optional[Dict[str, str]]
        timeout: int | float
        init_script: Optional[str]
        user_data_dir: str
        selector_config: Optional[Dict]
        additional_args: Optional[Dict]

    class PlaywrightSession(BrowserSession, total=False):
        cdp_url: Optional[str]
        hide_canvas: bool
        disable_webgl: bool
        real_chrome: bool
        stealth: bool
        locale: str
        useragent: Optional[str]
        extra_flags: Optional[List[str]]

    class PlaywrightFetchParams(TypedDict, total=False):
        google_search: bool
        timeout: int | float
        wait: int | float
        page_action: Optional[Callable]
        extra_headers: Optional[Dict[str, str]]
        disable_resources: bool
        wait_selector: Optional[str]
        wait_selector_state: SelectorWaitStates
        network_idle: bool
        load_dom: bool
        selector_config: Optional[Dict]

    class CamoufoxSession(BrowserSession, total=False):
        block_images: bool
        block_webrtc: bool
        allow_webgl: bool
        humanize: bool | float
        solve_cloudflare: bool
        addons: Optional[List[str]]
        os_randomize: bool
        disable_ads: bool
        geoip: bool

    class CamoufoxFetchParams(PlaywrightFetchParams, total=False):
        solve_cloudflare: bool

else:  # pragma: no cover
    RequestsSession = TypedDict
    GetRequestParams = TypedDict
    DataRequestParams = TypedDict
    PlaywrightSession = TypedDict
    PlaywrightFetchParams = TypedDict
    CamoufoxSession = TypedDict
    CamoufoxFetchParams = TypedDict
