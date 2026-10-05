from pydantic import AliasPath, BaseModel, Field

from scrapling.core._types import Dict, Literal, Optional
from scrapling.engines.toolbelt.custom import Response
from scrapling.engines.toolbelt.convertor import ResponseFactory

NetworkPart = Literal["summary", "request_headers", "request_body", "response_headers", "response_body"]


class NetworkRequestInfo(BaseModel):
    """Summary of a recorded browser request."""

    model_config = {"populate_by_name": True}

    id: int = Field(validation_alias=AliasPath("meta", "network_id"))
    url: str
    method: str
    resource_type: str = Field(validation_alias=AliasPath("meta", "resource_type"))
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


def _request_details(record: Response, part: NetworkPart) -> NetworkRequestModel:
    """Read one saved request part without browser access."""
    result = NetworkRequestModel(request_id=record.meta["network_id"], part=part)
    if part == "summary":
        result.data = NetworkRequestInfo.model_validate(record, from_attributes=True)
        return result
    headers = record.request_headers if part.startswith("request_") else record.headers
    if part.endswith("headers"):
        result.data = headers.copy()
        if record.meta.get("request_headers_partial" if part == "request_headers" else "headers_partial"):
            result.note = "Headers are partial; full headers unavailable."
        return result
    body = record.meta["request_body"] if part == "request_body" else record.body
    if part == "response_body" and record.meta.get("body_note"):
        result.note = record.meta["body_note"]
    elif body is None:
        result.note = "Body is absent."
    elif body and not ResponseFactory._text_content(headers):
        result.note = "Only text bodies can be displayed."
    else:
        encoding = (
            ResponseFactory._extract_encoding(headers.get("content-type"))
            if part == "request_body"
            else record.encoding
        )
        result.data = _decode(body, encoding)
    return result
