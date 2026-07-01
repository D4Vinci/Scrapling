# Run: pytest e2e/test_mcp_json_playground.py
import base64
import json
import os
import httpx
import pytest

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

# Global variables for testing custom payloads/URLs
URL = "https://toscrape.com/"
SCHEMA = {
    "books": {
        "path": "div.row:nth-child(2) > div:nth-child(2) > div:nth-child(4) > table tr:not(:first-child)",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "detail": {"path": "td:nth-child(1)::text", "type": "string", "default": ""},
                "value": {"path": "td:nth-child(2)::text", "type": "string", "default": ""},
            },
        },
    },
    "quotes": {
        "path": "div.row:nth-child(3) > div:nth-child(2) > div:nth-child(4) > table tr:not(:first-child)",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "endpoint": {"path": "td:nth-child(1) > a::text", "type": "string", "default": ""},
                "url": {"path": "td:nth-child(1) > a::attr(href)", "type": "string", "default": ""},
                "description": {"path": "td:nth-child(2)::text", "type": "string", "default": ""},
            },
        },
    },
}


def _post_mcp(url, data, mcp_session_id=None):
    headers = {
        "accept": "application/json, text/event-stream",
        "content-type": "application/json",
    }
    if mcp_session_id:
        headers["mcp-session-id"] = mcp_session_id

    r = httpx.post(url, json=data, headers=headers)
    r.raise_for_status()
    for line in r.text.split("\n"):
        if line.startswith("data: "):
            return r.headers, json.loads(line[6:].strip())
    raise ValueError(f"No SSE data event found: {r.text}")


class TestMCPJsonPlayground:
    @pytest.mark.asyncio
    async def test_playground_payload(self, docker_mcp_server: str) -> None:
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)

        # 1. Initialize session
        res_headers, _ = _post_mcp(
            docker_mcp_server,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"},
                },
            },
        )
        mcp_session_id = res_headers.get("mcp-session-id")

        # 2. Open browser session
        _, open_data = _post_mcp(
            docker_mcp_server,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "open_session", "arguments": {"session_type": "stealthy", "headless": True}},
            },
            mcp_session_id,
        )
        session_id = open_data["result"]["structuredContent"]["session_id"]

        # Save the input payload that will be executed
        tool_args = {
            "url": URL,
            "extraction_type": "json",
            "schema": SCHEMA,
            "session_id": session_id,
            "network_idle": True,
        }
        with open(os.path.join(ARTIFACTS_DIR, "input_payload.json"), "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "stealthy_fetch", "arguments": tool_args},
                },
                fh,
                indent=2,
            )

        # 3. Call stealthy_fetch tool
        _, fetched_data = _post_mcp(
            docker_mcp_server,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "stealthy_fetch", "arguments": tool_args},
            },
            mcp_session_id,
        )
        output = json.loads(fetched_data["result"]["structuredContent"]["content"][0])

        with open(os.path.join(ARTIFACTS_DIR, "structured_output.json"), "w", encoding="utf-8") as fh:
            json.dump(output, fh, indent=2)

        # 4. Screenshot
        _, shot_data = _post_mcp(
            docker_mcp_server,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "screenshot",
                    "arguments": {
                        "url": URL,
                        "session_id": session_id,
                        "full_page": True,
                        "image_type": "png",
                        "network_idle": True,
                    },
                },
            },
            mcp_session_id,
        )

        for block in shot_data["result"]["content"]:
            if block.get("type") == "image":
                with open(os.path.join(ARTIFACTS_DIR, "screenshot.png"), "wb") as fh:
                    fh.write(base64.b64decode(block["data"]))
                break

        # 5. Close session
        _post_mcp(
            docker_mcp_server,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "close_session", "arguments": {"session_id": session_id}},
            },
            mcp_session_id,
        )
