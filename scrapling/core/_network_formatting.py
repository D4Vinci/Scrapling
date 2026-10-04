from pydantic import BaseModel

from scrapling.core._types import Dict, Literal, Optional
from scrapling.engines._browsers._network import NetworkRequest
from scrapling.engines.toolbelt.convertor import ResponseFactory

NetworkPart = Literal["summary", "request_headers", "request_body", "response_headers", "response_body"]


class NetworkRequestInfo(BaseModel):
    """Summary of a recorded browser request."""

    id: int
    url: str
    method: str
    resource_type: str
    status: int


class NetworkRequestModel(BaseModel):
    """One complete saved request part, with an optional note."""

    request_id: int
    part: NetworkPart
    data: Dict[str, str] | NetworkRequestInfo | str | None = None
    note: Optional[str] = None


def _decode(body: bytes, encoding: str) -> str:
    try:
        return body.decode(encoding, errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


def _request_details(record: NetworkRequest, part: NetworkPart) -> NetworkRequestModel:
    """Read one saved request part without browser access."""
    result = NetworkRequestModel(request_id=record.id, part=part)
    if part == "summary":
        result.data = NetworkRequestInfo.model_validate(record, from_attributes=True)
        return result
    headers = record.request_headers if part.startswith("request_") else record.response_headers
    if part.endswith("headers"):
        result.data = headers.copy()
        if record.response.meta.get("request_headers_partial" if part == "request_headers" else "headers_partial"):
            result.note = "Headers are partial; full headers unavailable."
        return result
    body = record.request_body if part == "request_body" else record.response.body
    if part == "response_body" and record.response.meta.get("body_note"):
        result.note = record.response.meta["body_note"]
    elif body is None:
        result.note = "Body is absent."
    elif body and not ResponseFactory._text_content(headers):
        result.note = "Only text bodies can be displayed."
    else:
        encoding = (
            ResponseFactory._extract_encoding(headers.get("content-type"))
            if part == "request_body"
            else record.response.encoding
        )
        result.data = _decode(body, encoding)
    return result
