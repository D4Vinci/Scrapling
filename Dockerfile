FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy dependency file first for better layer caching
COPY pyproject.toml ./

# Install dependencies only
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --all-extras --compile-bytecode

# Copy source code
COPY . .

# Install browsers and project in one optimized layer
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    uv run playwright install-deps chromium firefox && \
    uv run playwright install chromium && \
    uv run camoufox fetch --browserforge && \
    uv sync --all-extras --compile-bytecode && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Expose port for MCP server HTTP transport
EXPOSE 8000

# Set entrypoint to run scrapling
ENTRYPOINT ["uv", "run", "scrapling"]

# Default command (can be overridden)
CMD ["--help"]