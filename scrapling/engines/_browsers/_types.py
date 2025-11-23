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
    TypedDict,
    TypeAlias,
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

else:  # pragma: no cover
    RequestsSession = TypedDict
    GetRequestParams = TypedDict
    DataRequestParams = TypedDict
