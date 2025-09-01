from .custom import (
    BaseFetcher,
    Response,
    StatusText,
    get_variable_name,
)
from .fingerprints import (
    generate_convincing_referer,
    generate_headers,
    get_os_name,
    __default_useragent__,
)
from .navigation import (
    async_intercept_route,
    construct_cdp_url,
    construct_proxy_dict,
    intercept_route,
    js_bypass_path,
)
from .convertor import ResponseFactory
