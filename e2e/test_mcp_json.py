# Run: pytest e2e/
import json
import os

import pytest

from e2e._server_helpers import _serve_mock

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

MOCK_HTML = (
    b"<!doctype html><html><body>"
    b'<div class="primary"><span class="label">Name</span><strong class="value">42.5</strong></div>'
    b'<div class="info"><span class="field-a">alpha</span><span class="field-b">beta</span></div>'
    b'<div class="item"><a href="/x/one">one</a></div>'
    b'<div class="item"><a href="/x/two">two</a></div>'
    b"</body></html>"
)

SCHEMA = {
    "value": {"path": ".primary strong.value::text", "type": "float", "default": 0.0},
    "details": {
        "path": "div.info",
        "type": "object",
        "properties": {
            "field_a": {"path": "span.field-a::text", "type": "string", "default": ""},
            "field_b": {"path": "span.field-b::text", "type": "string", "default": ""},
        },
    },
    "items": {"path": ".item", "type": "array", "items": {"type": "string", "path": "a::text"}},
}

EXPECTED = {
    "value": 42.5,
    "details": {"field_a": "alpha", "field_b": "beta"},
    "items": ["one", "two"],
}


class TestMCPJsonE2E:
    @pytest.mark.asyncio
    async def test_stealthy_fetch_resolves_schema(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        with _serve_mock(MOCK_HTML) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    opened = await session.call_tool("open_session", {"session_type": "stealthy", "headless": True})
                    assert opened.structuredContent is not None
                    session_id = opened.structuredContent["session_id"]
                    fetched = await session.call_tool(
                        "stealthy_fetch",
                        {
                            "url": container_url,
                            "extraction_type": "json",
                            "session_id": session_id,
                            "network_idle": True,
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["content"][0])
                    with open(os.path.join(ARTIFACTS_DIR, "structured_output.json"), "w") as fh:
                        json.dump(output, fh, indent=2)
                    await session.call_tool("close_session", {"session_id": session_id})
        assert output == EXPECTED

    @pytest.mark.asyncio
    async def test_bulk_stealthy_fetch_resolves_schema(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        with _serve_mock(MOCK_HTML) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    opened = await session.call_tool("open_session", {"session_type": "stealthy", "headless": True})
                    assert opened.structuredContent is not None
                    session_id = opened.structuredContent["session_id"]
                    fetched = await session.call_tool(
                        "bulk_stealthy_fetch",
                        {
                            "urls": [container_url],
                            "extraction_type": "json",
                            "session_id": session_id,
                            "network_idle": True,
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["result"][0]["content"][0])
                    await session.call_tool("close_session", {"session_id": session_id})
        assert output == EXPECTED

    @pytest.mark.asyncio
    async def test_get_resolves_schema(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        with _serve_mock(MOCK_HTML) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    fetched = await session.call_tool(
                        "get",
                        {
                            "url": container_url,
                            "extraction_type": "json",
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["content"][0])
        assert output == EXPECTED

    @pytest.mark.asyncio
    async def test_bulk_get_resolves_schema(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        with _serve_mock(MOCK_HTML) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    fetched = await session.call_tool(
                        "bulk_get",
                        {
                            "urls": [container_url],
                            "extraction_type": "json",
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["result"][0]["content"][0])
        assert output == EXPECTED

    @pytest.mark.asyncio
    async def test_fetch_resolves_schema(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        with _serve_mock(MOCK_HTML) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    fetched = await session.call_tool(
                        "fetch",
                        {
                            "url": container_url,
                            "extraction_type": "json",
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["content"][0])
        assert output == EXPECTED

    @pytest.mark.asyncio
    async def test_bulk_fetch_resolves_schema(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        with _serve_mock(MOCK_HTML) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    fetched = await session.call_tool(
                        "bulk_fetch",
                        {
                            "urls": [container_url],
                            "extraction_type": "json",
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["result"][0]["content"][0])
        assert output == EXPECTED

    @pytest.mark.asyncio
    async def test_missing_nodes_return_schema_defaults(self, docker_mcp_server: str) -> None:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        empty_html = b"<html><body><p>nothing here</p></body></html>"
        with _serve_mock(empty_html) as (_, container_url):
            async with streamable_http_client(docker_mcp_server) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    fetched = await session.call_tool(
                        "get",
                        {
                            "url": container_url,
                            "extraction_type": "json",
                            "schema": SCHEMA,
                        },
                    )
                    assert fetched.structuredContent is not None
                    output = json.loads(fetched.structuredContent["content"][0])
        assert output == {"value": 0.0, "details": {"field_a": "", "field_b": ""}, "items": []}
