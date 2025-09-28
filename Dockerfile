FROM python:3.12-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ADD . /app

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --all-extras --compile-bytecode

# Install all browsers and their deps
RUN uv run playwright install-deps chromium firefox
RUN uv run playwright install chromium
RUN uv run camoufox fetch --browserforge

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-extras --compile-bytecode

# Clean up to save space
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Expose port for MCP server HTTP transport
EXPOSE 8000

# Set entrypoint to run scrapling
ENTRYPOINT ["uv", "run", "scrapling"]

# Default command (can be overridden)
CMD ["--help"]