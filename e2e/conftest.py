# Run E2E tests: pytest e2e/
import pytest

from e2e._docker_helpers import IMAGE, MCP_HOST_PORT, start_mcp_container, stop_mcp_container

_CONTAINER = "scrapling_e2e_mcp"


@pytest.fixture(scope="session")
def docker_mcp_server() -> str:  # type: ignore[return]
    endpoint = start_mcp_container(_CONTAINER, IMAGE, MCP_HOST_PORT)
    try:
        yield endpoint
    finally:
        stop_mcp_container(_CONTAINER)
