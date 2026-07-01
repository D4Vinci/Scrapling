import os
import subprocess
import time

IMAGE = "scrapling-mcp"
MCP_HOST_PORT = 18000

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _docker(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", *args], **kwargs)  # nosec B603 B607


def _ensure_image(image: str = IMAGE) -> None:
    if _docker("image", "inspect", image, capture_output=True).returncode != 0:
        subprocess.run(["docker", "build", "-t", image, _PROJECT_ROOT], check=True)  # nosec B603 B607


def _wait_until_ready(container: str, timeout: int = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = _docker("inspect", "-f", "{{.State.Running}}", container, capture_output=True, text=True)
        if state.stdout.strip() != "true":
            logs = _docker("logs", container, capture_output=True, text=True)
            raise RuntimeError(f"container exited early:\n{logs.stdout}\n{logs.stderr}")
        blob = _docker("logs", container, capture_output=True, text=True)
        if "Uvicorn running" in blob.stderr:
            return
        time.sleep(1)
    raise RuntimeError("timed out waiting for MCP server")


def start_mcp_container(container: str, image: str = IMAGE, host_port: int = MCP_HOST_PORT) -> str:
    _docker("rm", "-f", container, capture_output=True)
    _ensure_image(image)
    result = _docker(
        "run",
        "-d",
        "--name",
        container,
        "-p",
        f"{host_port}:8000",
        "--add-host=host.docker.internal:host-gateway",
        image,
        "mcp",
        "--http",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"docker run failed:\n{result.stderr}")
    _wait_until_ready(container)
    return f"http://127.0.0.1:{host_port}/mcp"


def stop_mcp_container(container: str) -> None:
    _docker("rm", "-f", container, capture_output=True)
