from http import cookies as Cookie


from scrapling.core._types import (
    List,
    Dict,
    Tuple,
)


def _CookieParser(cookie_string):
    # Errors will be handled on call so the log can be specified
    cookie_parser = Cookie.SimpleCookie()
    cookie_parser.load(cookie_string)
    for key, morsel in cookie_parser.items():
        yield key, morsel.value


def _ParseHeaders(header_lines: List[str], parse_cookies: bool = True) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Parses headers into separate header and cookie dictionaries."""
    header_dict = dict()
    cookie_dict = dict()

    for header_line in header_lines:
        if ":" not in header_line:
            if header_line.endswith(";"):
                header_key = header_line[:-1].strip()
                header_value = ""
                header_dict[header_key] = header_value
            else:
                raise ValueError(f"Could not parse header without colon: '{header_line}'.")
        else:
            header_key, header_value = header_line.split(":", 1)
            header_key = header_key.strip()
            header_value = header_value.strip()

            if parse_cookies:
                if header_key.lower() == "cookie":
                    try:
                        cookie_dict = {key: value for key, value in _CookieParser(header_value)}
                    except Exception as e:  # pragma: no cover
                        raise ValueError(f"Could not parse cookie string from header '{header_value}': {e}")
                else:
                    header_dict[header_key] = header_value
            else:
                header_dict[header_key] = header_value

    return header_dict, cookie_dict
