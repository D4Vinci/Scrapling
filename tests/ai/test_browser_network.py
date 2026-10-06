from json import loads
from os import getenv
from asyncio import Event, create_task, sleep, wait_for
from types import SimpleNamespace
from urllib.parse import urlsplit
from unittest.mock import AsyncMock, Mock

import pytest
from mcp.client import Client
from mcp.types import CallToolResult, TextContent

from scrapling.core._types import Any
from scrapling.core.ai._network_formatting import _request_details
from scrapling.core.ai import NetworkRequestModel, NetworkRequestsModel, ScraplingMCPServer
from scrapling.core.ai.server import _SessionEntry
from scrapling.engines._browsers._network import NetworkRecorder
from scrapling.engines.toolbelt.custom import Response


def _server() -> tuple[ScraplingMCPServer, Mock]:
    server = ScraplingMCPServer()
    record = Response(
        url="https://network.test/api/items",
        content='{"name":"مرحبا"}'.encode(),
        status=201,
        reason="Created",
        cookies={},
        headers={"content-type": "application/json; charset=utf-8", "set-cookie": "test=2"},
        request_headers={"content-type": "application/json", "cookie": "test=1"},
        method="POST",
        meta={"network_id": 4, "resource_type": "fetch", "request_body": b'{"sent":true}'},
    )
    network = Mock(spec=["last_id", "dropped_count", "search", "get"], last_id=4, dropped_count=0)
    network.search.return_value = [record]
    network.get.side_effect = lambda request_id: record if request_id == 4 else None
    session = SimpleNamespace(_is_alive=True, network=network)
    server._sessions["browser"] = _SessionEntry(session, "stealthy")
    return server, network


def _recording_server(max_requests: int = 3) -> tuple[ScraplingMCPServer, NetworkRecorder, Mock]:
    server, network, context = ScraplingMCPServer(), NetworkRecorder(True, max_requests, asynchronous=True), Mock()
    network._attach(context)
    session = SimpleNamespace(_is_alive=True, network=network)
    server._sessions["browser"] = _SessionEntry(session, "stealthy")
    return server, network, context


def _native_request(path: str, resource_type: str = "fetch", status: int = 200) -> Mock:
    request = Mock(
        url=f"https://network.test{path}",
        method="GET",
        resource_type=resource_type,
        headers={},
        post_data_buffer=None,
    )
    request.all_headers = AsyncMock(return_value={})
    response = Mock(
        url=request.url,
        status=status,
        status_text="OK",
        request=request,
        headers={"content-type": "text/plain"},
    )
    response.all_headers = AsyncMock(return_value=response.headers.copy())
    response.body = AsyncMock(return_value=b"saved")
    request.existing_response = response
    return request


def _listing(result: CallToolResult) -> dict[str, Any]:
    assert not result.is_error and isinstance(result.structured_content, dict)
    assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
    assert loads(result.content[0].text) == result.structured_content
    assert set(result.structured_content) == {"requests", "next_cursor", "has_more", "dropped_count"}
    return result.structured_content


def _detail(result: CallToolResult) -> dict[str, Any]:
    assert not result.is_error and isinstance(result.structured_content, dict)
    assert len(result.content) == 1 and isinstance(result.content[0], TextContent)
    assert loads(result.content[0].text) == result.structured_content
    assert set(result.structured_content) == {"request_id", "part", "data", "note"}
    return result.structured_content


def _detail_info(
    request_id: int,
    part: str,
    data: Any = None,
    note: str | None = None,
) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "part": part,
        "data": data,
        "note": note,
    }


def _request_info(
    request_id: int, path: str, method: str = "GET", resource_type: str = "fetch", status: int = 200
) -> dict[str, Any]:
    return {
        "id": request_id,
        "url": f"https://network.test{path}",
        "method": method,
        "resource_type": resource_type,
        "status": status,
    }


@pytest.mark.asyncio
async def test_network_tools_schema_and_content() -> None:
    server, network = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        for name in ("browser_network_requests", "browser_network_request"):
            tool = tools[name]
            assert tool.annotations is not None and tool.annotations.read_only_hint is True
            assert tool.annotations.open_world_hint is False
        listing = tools["browser_network_requests"]
        assert listing.title == "List network requests"
        assert listing.input_schema["required"] == ["session_id"]
        properties = listing.input_schema["properties"]
        assert properties["include_static"]["default"] is False
        assert properties["limit"]["default"] == 50 and properties["limit"]["maximum"] == 200
        assert properties["after_id"]["minimum"] == 0
        schema = listing.output_schema
        assert schema is not None and schema["type"] == "object"
        output_properties = schema["properties"]
        assert {name: value["type"] for name, value in output_properties.items()} == {
            "requests": "array",
            "next_cursor": "integer",
            "has_more": "boolean",
            "dropped_count": "integer",
        }
        item_schema = schema["$defs"][output_properties["requests"]["items"]["$ref"].rsplit("/", 1)[-1]]
        assert item_schema["type"] == "object"
        assert {name: value["type"] for name, value in item_schema["properties"].items()} == {
            "id": "integer",
            "url": "string",
            "method": "string",
            "resource_type": "string",
            "status": "integer",
        }
        detail = tools["browser_network_request"]
        detail_schema = detail.output_schema
        assert detail_schema is not None and detail_schema["type"] == "object"
        output_properties = detail_schema["properties"]
        assert set(output_properties) == {"request_id", "part", "data", "note"}
        assert output_properties["request_id"]["type"] == "integer"
        assert output_properties["part"]["type"] == "string"
        assert set(output_properties["part"]["enum"]) == {
            "summary",
            "request_headers",
            "request_body",
            "response_headers",
            "response_body",
        }
        assert {option["type"] for option in output_properties["note"]["anyOf"]} == {"string", "null"}
        data_options = output_properties["data"]["anyOf"]
        assert len(data_options) == 4
        assert {option["type"] for option in data_options if "type" in option} == {"object", "string", "null"}
        header_schema = next(option for option in data_options if option.get("type") == "object")
        assert header_schema["additionalProperties"] == {"type": "string"}
        summary_ref = next(option["$ref"] for option in data_options if "$ref" in option)
        assert detail_schema["$defs"][summary_ref.rsplit("/", 1)[-1]] == item_schema
        assert detail.title == "Read network request"
        assert detail.input_schema["required"] == ["session_id", "request_id"]
        properties = detail.input_schema["properties"]
        assert properties["part"]["default"] == "summary"
        assert set(properties["part"]["enum"]) == {
            "summary",
            "request_headers",
            "request_body",
            "response_headers",
            "response_body",
        }
        assert set(properties) == {"session_id", "request_id", "part"}
        assert properties["request_id"]["minimum"] == 1
        result = await client.call_tool("browser_network_requests", {"session_id": "browser"})
        assert _listing(result) == {
            "requests": [_request_info(4, "/api/items", "POST", status=201)],
            "next_cursor": 4,
            "has_more": False,
            "dropped_count": 0,
        }
    network.search.assert_called_once_with(url_pattern=None, include_static=False, after_id=0, limit=51)


@pytest.mark.asyncio
async def test_network_list_forwards_filters_and_reports_paging_eviction() -> None:
    server, network = _server()
    network.search.return_value.append(
        Response(
            url="https://network.test/next",
            content=b"next",
            status=200,
            reason="OK",
            cookies={},
            headers={"content-type": "text/plain"},
            request_headers={},
            method="GET",
            meta={"network_id": 8, "resource_type": "document", "request_body": None},
        )
    )
    network.last_id = 8
    network.dropped_count = 3
    result = await server.browser_network_requests(
        "browser", url_pattern="/api/", include_static=True, after_id=2, limit=1
    )
    network.search.assert_called_once_with(url_pattern="/api/", include_static=True, after_id=2, limit=2)
    assert isinstance(result, NetworkRequestsModel)
    assert result.model_dump() == {
        "requests": [_request_info(4, "/api/items", "POST", status=201)],
        "next_cursor": 4,
        "has_more": True,
        "dropped_count": 3,
    }
    network.search.return_value = []
    result = await server.browser_network_requests("browser", after_id=10)
    assert result.model_dump() == {"requests": [], "next_cursor": 10, "has_more": False, "dropped_count": 3}


@pytest.mark.asyncio
async def test_network_cursor_follows_save_order_and_survives_clear() -> None:
    server, network, context = _recording_server()
    callback = network._contexts[context]["requestfinished"]
    started, release = Event(), Event()
    slow, fast = _native_request("/api/slow"), _native_request("/api/fast")

    async def slow_body() -> bytes:
        started.set()
        await release.wait()
        return b"slow"

    slow.existing_response.body.side_effect = slow_body
    capture = create_task(callback(slow))
    try:
        await wait_for(started.wait(), timeout=2)
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            empty = await client.call_tool("browser_network_requests", {"session_id": "browser"})
            assert _listing(empty) == {"requests": [], "next_cursor": 0, "has_more": False, "dropped_count": 0}
            await callback(fast)
            first = await client.call_tool("browser_network_requests", {"session_id": "browser", "limit": 1})
            assert _listing(first) == {
                "requests": [_request_info(1, "/api/fast")],
                "next_cursor": 1,
                "has_more": False,
                "dropped_count": 0,
            }
            release.set()
            await wait_for(capture, timeout=2)
            second = await client.call_tool(
                "browser_network_requests", {"session_id": "browser", "after_id": 1, "limit": 1}
            )
            assert _listing(second) == {
                "requests": [_request_info(2, "/api/slow")],
                "next_cursor": 2,
                "has_more": False,
                "dropped_count": 0,
            }
            network.clear()
            await callback(_native_request("/api/new"))
            after_clear = await client.call_tool("browser_network_requests", {"session_id": "browser", "after_id": 2})
            assert _listing(after_clear) == {
                "requests": [_request_info(3, "/api/new")],
                "next_cursor": 3,
                "has_more": False,
                "dropped_count": 0,
            }
            assert network.get(2) is None
    finally:
        release.set()
        await wait_for(capture, timeout=2)
        network._detach()


@pytest.mark.asyncio
async def test_network_real_filtering_eviction_and_cursor_paging() -> None:
    server, network, context = _recording_server()
    callback = network._contexts[context]["requestfinished"]
    try:
        for native in (
            _native_request("/page", "document"),
            _native_request("/api/first"),
            _native_request("/missing.png", "image", 404),
        ):
            await callback(native)
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            first = await client.call_tool("browser_network_requests", {"session_id": "browser", "limit": 1})
            assert _listing(first) == {
                "requests": [_request_info(2, "/api/first")],
                "next_cursor": 2,
                "has_more": True,
                "dropped_count": 0,
            }
            await callback(_native_request("/site.css", "stylesheet"))
            await callback(_native_request("/api/last", status=503))
            next_page = await client.call_tool("browser_network_requests", {"session_id": "browser", "after_id": 2})
            assert _listing(next_page) == {
                "requests": [
                    _request_info(3, "/missing.png", resource_type="image", status=404),
                    _request_info(5, "/api/last", status=503),
                ],
                "next_cursor": 5,
                "has_more": False,
                "dropped_count": 2,
            }
            all_types = await client.call_tool(
                "browser_network_requests", {"session_id": "browser", "include_static": True, "after_id": 2}
            )
            assert _listing(all_types) == {
                "requests": [
                    _request_info(3, "/missing.png", resource_type="image", status=404),
                    _request_info(4, "/site.css", resource_type="stylesheet"),
                    _request_info(5, "/api/last", status=503),
                ],
                "next_cursor": 5,
                "has_more": False,
                "dropped_count": 2,
            }
            filtered = await client.call_tool(
                "browser_network_requests", {"session_id": "browser", "url_pattern": r"/api/"}
            )
            assert _listing(filtered) == {
                "requests": [_request_info(5, "/api/last", status=503)],
                "next_cursor": 5,
                "has_more": False,
                "dropped_count": 2,
            }
            evicted = await client.call_tool("browser_network_request", {"session_id": "browser", "request_id": 2})
            assert isinstance(evicted.content[0], TextContent)
            assert evicted.is_error and "no longer retained" in evicted.content[0].text
            invalid = await client.call_tool("browser_network_requests", {"session_id": "browser", "url_pattern": "["})
            assert isinstance(invalid.content[0], TextContent)
            assert invalid.is_error and "Invalid URL pattern" in invalid.content[0].text
    finally:
        network._detach()


@pytest.mark.asyncio
@pytest.mark.parametrize("count,after_id,next_cursor", [(0, 0, 0), (2, 0, 2), (2, 1, 2), (2, 2, 2), (2, 9, 9)])
async def test_network_empty_matches_keep_cursor_at_or_after_saved_history(
    count: int, after_id: int, next_cursor: int
) -> None:
    server, network, context = _recording_server()
    try:
        for index in range(count):
            await network._contexts[context]["requestfinished"](_native_request(f"/api/{index}"))
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool(
                "browser_network_requests",
                {"session_id": "browser", "url_pattern": "/missing/", "after_id": after_id},
            )
            assert _listing(result) == {
                "requests": [],
                "next_cursor": next_cursor,
                "has_more": False,
                "dropped_count": 0,
            }
        assert network.last_id == count
    finally:
        network._detach()


@pytest.mark.asyncio
@pytest.mark.parametrize("count,has_more", [(2, False), (3, True)])
async def test_network_listing_limit_checks_for_an_extra_match(count: int, has_more: bool) -> None:
    server, network, context = _recording_server()
    try:
        for index in range(1, count + 1):
            await network._contexts[context]["requestfinished"](_native_request(f"/api/{index}"))
        async with Client(server._build_server("127.0.0.1", 8000)) as client:
            result = await client.call_tool("browser_network_requests", {"session_id": "browser", "limit": 2})
            assert _listing(result) == {
                "requests": [_request_info(1, "/api/1"), _request_info(2, "/api/2")],
                "next_cursor": 2,
                "has_more": has_more,
                "dropped_count": 0,
            }
    finally:
        network._detach()


@pytest.mark.asyncio
async def test_network_listing_preserves_url_characters_and_only_returns_summary_fields() -> None:
    server, network, context = _recording_server()
    path = '/api/مرحبا?q="quoted"&path=one\\two#one\ntwo'
    native = _native_request(path)
    native.method = "POST"
    native.post_data_buffer = b'{"secret":"request"}'
    native.headers = {"content-type": "application/json", "cookie": "secret=request"}
    native.all_headers.return_value = native.headers.copy()
    native.existing_response.headers = {"content-type": "application/json", "set-cookie": "secret=response"}
    native.existing_response.all_headers.return_value = native.existing_response.headers.copy()
    native.existing_response.body.return_value = b'{"secret":"response"}'
    await network._contexts[context]["requestfinished"](native)
    network._detach()
    record = network.get(1)
    assert record is not None and record.url == native.url
    assert record.meta["request_body"] == b'{"secret":"request"}' and record.body == b'{"secret":"response"}'
    readers = (native.all_headers, native.existing_response.all_headers, native.existing_response.body)
    for reader in readers:
        reader.assert_awaited_once()
        reader.side_effect = AssertionError("Listing saved history must not read the browser")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_network_requests", {"session_id": "browser"})
        assert _listing(result) == {
            "requests": [_request_info(1, path, "POST")],
            "next_cursor": 1,
            "has_more": False,
            "dropped_count": 0,
        }
    for reader in readers:
        reader.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("part", ["summary", "request_headers", "request_body", "response_headers", "response_body"])
async def test_network_detail_returns_only_selected_part(part: Any) -> None:
    server, network = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_network_request", {"session_id": "browser", "request_id": 4, "part": part}
        )
        record = network.get(4)
        if part == "summary":
            assert _detail(result) == _detail_info(4, part, _request_info(4, "/api/items", "POST", status=201))
        elif part.endswith("headers"):
            expected = record.request_headers if part == "request_headers" else record.headers
            assert _detail(result) == _detail_info(4, part, expected)
        else:
            expected = '{"sent":true}' if part == "request_body" else '{"name":"مرحبا"}'
            assert _detail(result) == _detail_info(4, part, expected)
        assert isinstance(record, Response) and record.request is None
        assert not hasattr(record, "response")
    network.search.assert_not_called()


@pytest.mark.parametrize("part", ["request_headers", "response_headers", "response_body"])
def test_saved_response_details_are_local(part: Any) -> None:
    _, network = _server()
    record = network.get(4)
    result = _request_details(record, part)
    assert isinstance(result, NetworkRequestModel)
    if part.endswith("headers"):
        expected = record.request_headers if part == "request_headers" else record.headers
        assert result.model_dump() == _detail_info(4, part, expected)
    else:
        assert result.model_dump() == _detail_info(4, part, '{"name":"مرحبا"}')


@pytest.mark.asyncio
@pytest.mark.parametrize("part", ["summary", "request_headers", "response_headers"])
async def test_network_objects_keep_all_summary_fields_and_header_values(part: str) -> None:
    server, network = _server()
    record = network.get(4)
    headers = {
        "id": "007",
        "url": "https://headers.test/",
        "method": "PATCH",
        "resource_type": "xhr",
        "status": "0200",
        "x-extra": "kept",
    }
    if part == "request_headers":
        record.request_headers = headers
    elif part == "response_headers":
        record.headers = headers
    expected = _request_info(4, "/api/items", "POST", status=201) if part == "summary" else headers
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_network_request",
            {"session_id": "browser", "request_id": 4, "part": part},
        )
        assert _detail(result) == _detail_info(4, part, expected)


@pytest.mark.asyncio
@pytest.mark.parametrize("part", ["request_body", "response_body"])
async def test_network_unicode_body_returns_the_full_original_text(part: str) -> None:
    server, network = _server()
    record = network.get(4)
    text = 'Aمرحبا🙂e\u0301\n"z"'
    if part == "request_body":
        record.meta["request_body"] = text.encode()
    else:
        record._raw_body = text.encode()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_network_request", {"session_id": "browser", "request_id": 4, "part": part}
        )
        assert _detail(result) == _detail_info(4, part, text)


@pytest.mark.asyncio
@pytest.mark.parametrize("part", ["request_body", "response_body"])
@pytest.mark.parametrize("size", [0, 10001, 50001, 100003])
async def test_network_detail_returns_complete_empty_and_large_saved_bodies(part: str, size: int) -> None:
    server, network, context = _recording_server()
    native = _native_request("/api/full-body")
    text = 'start\n"' + "x" * (size - 11) + '"end' if size else ""
    assert len(text) == size
    if part == "request_body":
        native.post_data_buffer = text.encode()
        native.headers = {"content-type": "text/plain"}
        native.all_headers.return_value = native.headers.copy()
    else:
        native.existing_response.body.return_value = text.encode()
    await network._contexts[context]["requestfinished"](native)
    network._detach()
    record = network.get(1)
    assert record is not None
    assert (record.meta["request_body"] if part == "request_body" else record.body) == text.encode()
    readers = (native.all_headers, native.existing_response.all_headers, native.existing_response.body)
    for reader in readers:
        reader.assert_awaited_once()
        reader.side_effect = AssertionError("Reading full saved bodies must not read the browser")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_network_request", {"session_id": "browser", "request_id": 1, "part": part}
        )
        assert _detail(result) == _detail_info(1, part, text)
    for reader in readers:
        reader.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["empty", "binary", "unavailable", "too_large"])
async def test_network_detail_body_availability(case: str) -> None:
    server, network = _server()
    record = network.get(4)
    if case == "empty":
        record.status = 204
        record._raw_body = b""
    elif case == "binary":
        record.headers["content-type"] = "image/png"
    elif case == "too_large":
        record.meta["body_note"] = "too large; not saved."
    else:
        record.meta["body_note"] = "Context closed"
    result = await server.browser_network_request("browser", 4, "response_body")
    expected = {
        "empty": _detail_info(4, "response_body", ""),
        "binary": _detail_info(4, "response_body", note="Only text bodies can be displayed."),
        "unavailable": _detail_info(4, "response_body", note="Context closed"),
        "too_large": _detail_info(4, "response_body", note="too large; not saved."),
    }
    assert result.model_dump() == expected[case]


@pytest.mark.asyncio
@pytest.mark.parametrize("part", ["request_headers", "response_headers"])
@pytest.mark.parametrize("partial", [False, True])
async def test_network_detail_saved_headers_report_completeness(part: Any, partial: bool) -> None:
    server, network = _server()
    record = network.get(4)
    headers = record.request_headers if part == "request_headers" else record.headers
    key = "request_headers_partial" if part == "request_headers" else "headers_partial"
    record.meta[key] = partial
    result = await server.browser_network_request("browser", 4, part)
    assert result.model_dump() == _detail_info(
        4, part, headers, note="Headers are partial; full headers unavailable." if partial else None
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type, body, encoding, expected",
    [
        ("text/plain; charset = iso-8859-1", b"caf\xe9", "iso-8859-1", "café"),
        ("text/plain; charset=invalid-codec", b"hi", "invalid-codec", "hi"),
        ('text/plain; CHARSET = "ISO-8859-1"', b"caf\xe9", "iso-8859-1", "café"),
        ("text/plain; charset = 'ISO-8859-1'", b"caf\xe9", "iso-8859-1", "café"),
        ("text/plain; charset=iso-8859-1", "café".encode(), "utf-8", "café"),
        ("application/problem+json", b'{"error":true}', "utf-8", '{"error":true}'),
        ("application/xml", b"<ok/>", "utf-8", "<ok/>"),
    ],
)
async def test_network_detail_decodes_text_for_any_resource(
    content_type: str, body: bytes, encoding: str, expected: str
) -> None:
    server, network = _server()
    record = network.get(4)
    record.meta["resource_type"] = "document"
    record.headers["content-type"] = content_type
    record._raw_body = body
    record.encoding = encoding
    result = await server.browser_network_request("browser", 4, "response_body")
    assert result.model_dump() == _detail_info(4, "response_body", expected)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_type,native_body,response_encoding,response_text,request_type,request_body,request_text",
    [
        (
            "text/plain; charset=iso-8859-15",
            "café ¤".encode(),
            "utf-8",
            "café ¤",
            "text/plain; charset=iso-8859-15",
            b"caf\xe9 \xa4",
            "café €",
        ),
        (
            "text/plain; charset=iso-8859-1",
            b"caf\xe9",
            "iso-8859-1",
            "café",
            "text/plain; charset=iso-8859-1",
            b"caf\xe9",
            "café",
        ),
        (
            "text/plain; charset=invalid-codec",
            "café".encode(),
            "utf-8",
            "café",
            "text/plain; charset=invalid-codec",
            "café".encode(),
            "café",
        ),
        (
            "text/plain; charset=invalid-codec",
            b"caf\xe9",
            "utf-8",
            "caf\ufffd",
            "text/plain; charset=invalid-codec",
            b"caf\xe9",
            "caf\ufffd",
        ),
    ],
)
async def test_network_response_uses_saved_encoding_and_request_uses_its_header(
    response_type: str,
    native_body: bytes,
    response_encoding: str,
    response_text: str,
    request_type: str,
    request_body: bytes,
    request_text: str,
) -> None:
    server, network, context = _recording_server()
    native = _native_request("/api/encoded")
    native.method = "POST"
    native.headers = {"content-type": request_type}
    native.all_headers.return_value = native.headers.copy()
    native.post_data_buffer = request_body
    native.existing_response.headers = {"content-type": response_type}
    native.existing_response.all_headers.return_value = native.existing_response.headers.copy()
    native.existing_response.body.return_value = native_body
    await network._contexts[context]["requestfinished"](native)
    network._detach()
    record = network.get(1)
    assert record is not None
    assert record.encoding == response_encoding
    assert record.body == native_body and record.meta["request_body"] == request_body
    assert record.headers == {"content-type": response_type}
    assert record.request_headers == {"content-type": request_type}
    readers = (native.all_headers, native.existing_response.all_headers, native.existing_response.body)
    for reader in readers:
        reader.assert_awaited_once()
        reader.side_effect = AssertionError("Saved history must not read the browser")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        for part, expected in (("response_body", response_text), ("request_body", request_text)):
            result = await client.call_tool(
                "browser_network_request", {"session_id": "browser", "request_id": 1, "part": part}
            )
            assert _detail(result) == _detail_info(1, part, expected)
        for part, expected in (("response_headers", response_type), ("request_headers", request_type)):
            result = await client.call_tool(
                "browser_network_request", {"session_id": "browser", "request_id": 1, "part": part}
            )
            assert _detail(result) == _detail_info(1, part, {"content-type": expected})
    for reader in readers:
        reader.assert_awaited_once()
    assert record.body == native_body and record.meta["request_body"] == request_body


@pytest.mark.asyncio
async def test_network_request_body_absent_and_binary() -> None:
    server, network = _server()
    record = network.get(4)
    record.meta["request_body"] = None
    result = await server.browser_network_request("browser", 4, "request_body")
    assert result.model_dump() == _detail_info(4, "request_body", note="Body is absent.")
    record.meta["request_body"] = b"binary"
    record.request_headers["content-type"] = "application/octet-stream"
    result = await server.browser_network_request("browser", 4, "request_body")
    assert result.model_dump() == _detail_info(4, "request_body", note="Only text bodies can be displayed.")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "part,body,content_type,status,expected,note",
    [
        ("request_body", None, "text/plain", 200, None, "Body is absent."),
        ("request_body", b"", "text/plain", 200, "", None),
        ("request_body", b"", None, 200, "", None),
        ("request_body", b"binary", "application/octet-stream", 200, None, "Only text bodies can be displayed."),
        ("response_body", b"", "text/plain", 200, "", None),
        ("response_body", b"", "application/json", 204, "", None),
        ("response_body", b"", None, 200, None, "Non-text body; not saved."),
        ("response_body", b"", None, 204, "", None),
        ("response_body", b"binary", "image/png", 200, None, "Non-text body; not saved."),
        ("response_body", b"file", "application/pdf", 200, None, "Non-text body; not saved."),
        ("response_body", b"file", "application/octet-stream", 200, None, "Non-text body; not saved."),
        ("response_body", b"saved", "application/unknown", 200, None, "Non-text body; not saved."),
        ("response_body", b"saved", None, 200, None, "Non-text body; not saved."),
        ("response_body", b'{"ok":true}', "application/problem+json", 200, '{"ok":true}', None),
    ],
)
async def test_network_reads_saved_parts_without_native_access(
    part: str, body: bytes | None, content_type: str | None, status: int, expected: str | None, note: str | None
) -> None:
    server, network, context = _recording_server()
    native = _native_request("/api/saved", status=status)
    headers = {"content-type": content_type} if content_type is not None else {}
    if part == "request_body":
        native.post_data_buffer = body
        native.headers = headers
        native.all_headers.return_value = headers.copy()
    else:
        native.existing_response.body.return_value = body
        native.existing_response.headers = headers
        native.existing_response.all_headers.return_value = headers.copy()
    await network._contexts[context]["requestfinished"](native)
    network._detach()
    record = network.get(1)
    assert record is not None
    skipped = part == "response_body" and note == "Non-text body; not saved."
    assert record.meta == {
        "network_id": 1,
        "resource_type": "fetch",
        "request_body": body if part == "request_body" else None,
        **({"body_note": note} if skipped else {}),
    }
    if part == "response_body":
        assert record.body == (b"" if skipped else body)
        assert native.existing_response.body.await_count == (not skipped and status != 204)
    readers = (native.all_headers, native.existing_response.all_headers, native.existing_response.body)
    counts = [reader.await_count for reader in readers]
    for reader in readers:
        reader.side_effect = AssertionError("Saved history must not read the browser")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(
            "browser_network_request", {"session_id": "browser", "request_id": 1, "part": part}
        )
        assert _detail(result) == _detail_info(1, part, expected, note=note)
        for saved_part in ("summary", "request_headers", "response_headers"):
            result = await client.call_tool(
                "browser_network_request", {"session_id": "browser", "request_id": 1, "part": saved_part}
            )
            expected_data = (
                _request_info(1, "/api/saved", status=status)
                if saved_part == "summary"
                else record.request_headers
                if saved_part == "request_headers"
                else record.headers
            )
            assert _detail(result) == _detail_info(1, saved_part, expected_data)
    assert [reader.await_count for reader in readers] == counts


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error,expected",
    [
        (None, "too large; not saved."),
        (RuntimeError("Context closed"), "Context closed"),
        (RuntimeError(), "could not be saved."),
    ],
)
async def test_network_body_note_does_not_replace_other_saved_parts(error: Exception | None, expected: str) -> None:
    server, network, context = _recording_server()
    native = _native_request("/api/body-note")
    native.method = "POST"
    native.post_data_buffer = b'{"sent":true}'
    native.headers = {"content-type": "application/json"}
    native.all_headers.return_value = native.headers.copy()
    response_headers = {"content-type": "application/json", "x-recorded": "yes"}
    if error is None:
        response_headers["content-length"] = str(1024 * 1024 + 1)
    else:
        native.existing_response.body.side_effect = error
    native.existing_response.headers = response_headers
    native.existing_response.all_headers.return_value = response_headers.copy()
    await network._contexts[context]["requestfinished"](native)
    network._detach()
    record = network.get(1)
    assert record is not None and record.meta == {
        "network_id": 1,
        "resource_type": "fetch",
        "request_body": b'{"sent":true}',
        "body_note": expected,
    }
    assert record.body == b"" and record.meta["request_body"] == b'{"sent":true}'
    assert native.existing_response.body.await_count == (error is not None)
    readers = (native.all_headers, native.existing_response.all_headers, native.existing_response.body)
    counts = [reader.await_count for reader in readers]
    for reader in readers:
        reader.side_effect = AssertionError("Saved history must not read the browser")
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        for part in ("response_body", "summary", "request_headers", "response_headers", "request_body"):
            result = await client.call_tool(
                "browser_network_request", {"session_id": "browser", "request_id": 1, "part": part}
            )
            if part == "response_body":
                assert _detail(result) == _detail_info(1, part, note=expected)
            elif part == "summary":
                assert _detail(result) == _detail_info(1, part, _request_info(1, "/api/body-note", "POST"))
            elif part.endswith("headers"):
                assert _detail(result) == _detail_info(
                    1, part, native.headers if part == "request_headers" else response_headers
                )
            else:
                assert _detail(result) == _detail_info(1, part, '{"sent":true}')
    assert [reader.await_count for reader in readers] == counts


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, options",
    [
        ("browser_network_requests", {"after_id": -1}),
        ("browser_network_requests", {"limit": 0}),
        ("browser_network_requests", {"limit": 201}),
        ("browser_network_request", {"request_id": 0}),
        ("browser_network_request", {}),
        ("browser_network_request", {"request_id": 4, "part": "all"}),
    ],
)
async def test_network_invalid_input_does_not_read_history(name: str, options: dict[str, Any]) -> None:
    server, network = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool(name, {"session_id": "browser", **options})
        assert result.is_error
    network.get.assert_not_called()
    network.search.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["missing", "static", "dead"])
@pytest.mark.parametrize("name", ["browser_network_requests", "browser_network_request"])
async def test_network_session_guards(case: str, name: str) -> None:
    server, network = _server()
    if case == "missing":
        server._sessions.clear()
    elif case == "static":
        server._sessions["browser"].session_type = "static"
    else:
        server._sessions["browser"].session._is_alive = False
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        options = {"request_id": 4} if name == "browser_network_request" else {}
        assert (await client.call_tool(name, {"session_id": "browser", **options})).is_error
    network.get.assert_not_called()
    network.search.assert_not_called()


@pytest.mark.asyncio
async def test_network_missing_id_and_search_error_reach_client() -> None:
    server, network = _server()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_network_request", {"session_id": "browser", "request_id": 99})
        assert isinstance(result.content[0], TextContent)
        assert result.is_error and "no longer retained" in result.content[0].text
        network.search.side_effect = ValueError("Invalid URL regular expression")
        result = await client.call_tool("browser_network_requests", {"session_id": "browser", "url_pattern": "["})
        assert isinstance(result.content[0], TextContent)
        assert result.is_error and "regular expression" in result.content[0].text


@pytest.mark.asyncio
async def test_network_live_capture_actions_navigation_and_reads() -> None:
    server = ScraplingMCPServer(executable_path=getenv("SCRAPLING_EXECUTABLE_PATH"))
    seen: list[str] = []
    html = """<html><head><link rel="icon" href="data:,"></head><body><button id="load" onclick="fetch('/api/items', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sent: true})}).then(r => r.json()).then(() => document.body.dataset.done='yes')">Load</button></body></html>"""
    responses = {
        "/api/items": (200, "application/json", b'{"items":[1,2]}'),
        "/api/empty": (200, "text/plain", b""),
        "/api/absent": (204, "application/json", b""),
        "/api/binary": (200, "application/octet-stream", b"\x00\xff\x80binary"),
        "/api/error": (503, "application/json", b'{"error":"unavailable"}'),
    }

    async def serve(route: Any) -> None:
        seen.append(route.request.url)
        path = urlsplit(route.request.url).path
        if path == "/api/failed":
            await route.abort("failed")
            return
        status, content_type, body = responses.get(path, (200, "text/html", html.encode()))
        await route.fulfill(status=status, content_type=content_type, body=body, headers={"x-recorded": "yes"})

    async def captured(session: Any, pattern: str) -> Response:
        while not (records := session.network.search(url_pattern=pattern)):
            await sleep(0.01)
        return records[0]

    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        opened = await client.call_tool("browser_open", {"session_id": "browser"})
        assert not opened.is_error
        session = server._sessions["browser"].session
        try:
            assert session.network.enabled and opened.structured_content["settings"]["record_requests"] is True
            empty = await client.call_tool("browser_network_requests", {"session_id": "browser"})
            assert _listing(empty) == {"requests": [], "next_cursor": 0, "has_more": False, "dropped_count": 0}
            await session.context.route("**/*", serve)
            assert not (
                await client.call_tool("browser_fetch", {"session_id": "browser", "url": "https://network.test/"})
            ).is_error
            acted = await client.call_tool(
                "browser_actions",
                {
                    "session_id": "browser",
                    "actions": [
                        {"type": "click", "selector": "#load"},
                        {"type": "wait_element", "selector": "body[data-done=yes]", "timeout": 2000},
                    ],
                },
            )
            assert not acted.is_error
            request = await wait_for(captured(session, "/api/items$"), timeout=5)
            extra = await client.call_tool(
                "browser_evaluate",
                {
                    "session_id": "browser",
                    "expression": "async () => { await Promise.allSettled(['/api/empty', '/api/absent', '/api/binary', '/api/error', '/api/failed'].map(path => fetch(path).then(response => response.arrayBuffer()))); return true; }",
                },
            )
            assert not extra.is_error
            records = {
                name: await wait_for(captured(session, f"/api/{name}$"), timeout=5)
                for name in ("empty", "absent", "binary", "error")
            }
            assert session.network.search(url_pattern="/api/failed$") == []
            for name, record in records.items():
                assert record.body == (b"" if name == "binary" else responses[f"/api/{name}"][2])
                assert record.meta == {
                    "network_id": record.meta["network_id"],
                    "resource_type": "fetch",
                    "request_body": None,
                    **({"body_note": "Non-text body; not saved."} if name == "binary" else {}),
                }
            before = list(seen)
            page = session.page_pool.get_ready_page()
            assert page is not None
            try:
                listed = await client.call_tool("browser_network_requests", {"session_id": "browser"})
                detail = await client.call_tool(
                    "browser_network_request",
                    {"session_id": "browser", "request_id": request.meta["network_id"], "part": "response_body"},
                )
                assert not listed.is_error and not detail.is_error
                assert request is not None and request.body == b'{"items":[1,2]}'
                expected_requests = sorted(
                    [_request_info(request.meta["network_id"], "/api/items", "POST")]
                    + [
                        _request_info(record.meta["network_id"], f"/api/{name}", status=responses[f"/api/{name}"][0])
                        for name, record in records.items()
                    ],
                    key=lambda item: item["id"],
                )
                expected_listing = {
                    "requests": expected_requests,
                    "next_cursor": expected_requests[-1]["id"],
                    "has_more": False,
                    "dropped_count": 0,
                }
                assert _listing(listed) == expected_listing
                assert _detail(detail) == _detail_info(request.meta["network_id"], "response_body", '{"items":[1,2]}')
                request_body = await client.call_tool(
                    "browser_network_request",
                    {"session_id": "browser", "request_id": request.meta["network_id"], "part": "request_body"},
                )
                assert _detail(request_body) == _detail_info(
                    request.meta["network_id"], "request_body", '{"sent":true}'
                )
                for name, expected, note in (
                    ("empty", "", None),
                    ("absent", "", None),
                    ("binary", None, "Non-text body; not saved."),
                    ("error", '{"error":"unavailable"}', None),
                ):
                    result = await client.call_tool(
                        "browser_network_request",
                        {
                            "session_id": "browser",
                            "request_id": records[name].meta["network_id"],
                            "part": "response_body",
                        },
                    )
                    assert _detail(result) == _detail_info(
                        records[name].meta["network_id"], "response_body", expected, note=note
                    )
                    headers = await client.call_tool(
                        "browser_network_request",
                        {
                            "session_id": "browser",
                            "request_id": records[name].meta["network_id"],
                            "part": "response_headers",
                        },
                    )
                    assert _detail(headers) == _detail_info(
                        records[name].meta["network_id"], "response_headers", records[name].headers
                    )
                    assert _detail(headers)["data"]["x-recorded"] == "yes"
                assert page.state == "busy" and seen == before
            finally:
                page.mark_ready()
            assert not (
                await client.call_tool("browser_fetch", {"session_id": "browser", "url": "https://network.test/next"})
            ).is_error
            await wait_for(captured(session, "/next$"), timeout=5)
            listed = await client.call_tool("browser_network_requests", {"session_id": "browser"})
            assert _listing(listed) == expected_listing
            await session.close_pages()
            before = list(seen)
            detail = await client.call_tool(
                "browser_network_request",
                {"session_id": "browser", "request_id": request.meta["network_id"], "part": "response_body"},
            )
            assert _detail(detail) == _detail_info(request.meta["network_id"], "response_body", '{"items":[1,2]}')
            for record in records.values():
                saved = await client.call_tool(
                    "browser_network_request",
                    {"session_id": "browser", "request_id": record.meta["network_id"], "part": "response_headers"},
                )
                assert _detail(saved) == _detail_info(record.meta["network_id"], "response_headers", record.headers)
                assert _detail(saved)["data"]["x-recorded"] == "yes"
            assert seen == before
        finally:
            try:
                assert not (await client.call_tool("close_session", {"session_id": "browser"})).is_error
            finally:
                await session.close()
        assert not session.network._contexts
        assert request.body == b'{"items":[1,2]}'
        closed = await client.call_tool("browser_network_requests", {"session_id": "browser"})
        assert closed.is_error
        closed_detail = await client.call_tool(
            "browser_network_request",
            {"session_id": "browser", "request_id": request.meta["network_id"], "part": "response_body"},
        )
        assert closed_detail.is_error
