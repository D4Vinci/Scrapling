from scrapling.core._types import (
    List,
    Dict,
    Tuple,
    Generator,
)

# `Set-Cookie` attributes, skipped so a pasted `Set-Cookie` value still gives only the cookie itself
_COOKIE_ATTRIBUTES = frozenset(
    {"expires", "path", "comment", "domain", "max-age", "secure", "httponly", "version", "samesite", "partitioned"}
)


def _CookieParser(cookie_string: str) -> Generator[Tuple[str, str], None, None]:
    """Split a cookie string like `a=1; b=2` into (name, value) pairs, keeping each value as it was sent.

    `http.cookies.SimpleCookie` isn't used here because it stops at the first value it considers invalid (a space,
    a double quote, etc.) and silently drops that cookie and every one after it, while browsers send such values.
    """
    for pair in cookie_string.split(";"):
        name, separator, value = pair.partition("=")
        name = name.strip()
        if not separator or not name or name.lower() in _COOKIE_ATTRIBUTES:
            continue
        yield name, value.strip()


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
