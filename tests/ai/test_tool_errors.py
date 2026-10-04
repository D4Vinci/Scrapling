from asyncio import CancelledError
from inspect import signature

import pytest
from curl_cffi.curl import CurlError
from mcp import MCPError
from mcp.client import Client
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import TextContent
from patchright.async_api import Error as PatchrightError

from scrapling.core.ai import ScraplingMCPServer, _mcp_tool
from scrapling.core._types import Any


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        ValueError("bad input"),
        RuntimeError("page busy"),
        PatchrightError("page closed"),
        CurlError("connection failed"),
    ],
)
async def test_expected_tool_errors_keep_their_message(error: Exception) -> None:
    async def tool() -> None:
        raise error

    with pytest.raises(ToolError) as result:
        await _mcp_tool(tool)()
    assert str(result.value) == str(error)
    assert result.value.__cause__ is error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "arguments, message",
    [
        ({"executable_path": "/missing/scrapling-browser-binary"}, "Browser executable path not found"),
        ({"cdp_url": "invalid://localhost:9222"}, "CDP URL must use"),
        ({"proxy": {"username": "test"}}, "server"),
    ],
)
async def test_browser_configuration_errors_reach_client(arguments: dict[str, Any], message: str) -> None:
    server = ScraplingMCPServer()
    async with Client(server._build_server("127.0.0.1", 8000)) as client:
        result = await client.call_tool("browser_open", arguments)
    assert result.is_error
    assert result.content and isinstance(result.content[0], TextContent)
    assert message in result.content[0].text
    assert await server.list_sessions() == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [KeyError("internal"), TypeError("internal"), CancelledError(), MCPError(code=-32603, message="protocol failure")],
)
async def test_other_tool_errors_pass_through(error: BaseException) -> None:
    async def tool() -> None:
        raise error

    with pytest.raises(type(error)) as result:
        await _mcp_tool(tool)()
    assert result.value is error


@pytest.mark.asyncio
async def test_tool_wrapper_preserves_signature_and_result() -> None:
    async def tool(value: int = 3) -> dict[str, int]:
        return {"value": value}

    wrapped = _mcp_tool(tool)
    assert wrapped.__name__ == tool.__name__
    assert signature(wrapped) == signature(tool)
    assert await wrapped(value=5) == {"value": 5}
