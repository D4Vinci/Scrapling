import pytest
from mcp.client import Client

from scrapling.core.ai import ScraplingMCPServer


@pytest.mark.asyncio
async def test_tool_discovery_keeps_parameter_help_in_input_fields() -> None:
    async with Client(ScraplingMCPServer()._build_server("127.0.0.1", 8000)) as client:
        tools = (await client.list_tools()).tools
    assert tools
    for tool in tools:
        assert tool.description and ":param" not in tool.description, tool.name
        for name, parameter in tool.input_schema["properties"].items():
            description = parameter.get("description")
            assert isinstance(description, str) and description.strip(), f"{tool.name}.{name}"
