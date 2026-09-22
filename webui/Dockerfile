# Build context is the repo root (needed for the `scrapling` package itself):
#   docker build -f webui/Dockerfile -t scrapling-webui .
# For a Raspberry Pi (arm64) from another machine:
#   docker buildx build --platform linux/arm64 -f webui/Dockerfile -t scrapling-webui --load .

# ---- client build -----------------------------------------------------
FROM node:20-bookworm-slim AS client-build
WORKDIR /client
COPY webui/client/package*.json ./
RUN npm ci
COPY webui/client/ ./
RUN npm run build

# ---- node runtime, borrowed for the final image ------------------------
FROM node:20-bookworm-slim AS node-runtime

# ---- final image: python (scrapling) + node (webui server) ------------
FROM python:3.12-slim-bookworm AS final

LABEL org.opencontainers.image.title="scrapling-webui"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Grafted from node:20-bookworm-slim — same Debian release as the base image
# here, so glibc/libstdc++ line up. Copied path-by-path (rather than the
# whole /usr/local) to avoid clobbering anything CPython put there.
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/bin/npm /usr/local/bin/npm
COPY --from=node-runtime /usr/local/bin/npx /usr/local/bin/npx
COPY --from=node-runtime /usr/local/bin/corepack /usr/local/bin/corepack
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node-runtime /usr/local/include/node /usr/local/include/node

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:${PATH}" \
    PORT=3000

WORKDIR /app

# Install Python deps first for layer caching.
COPY pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --all-extras --compile-bytecode

# Now bring in the rest of the source (scrapling/ package + webui/).
COPY . .

# Chromium + the scrapling package itself, in one layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    uv run playwright install-deps chromium && \
    uv run playwright install chromium && \
    uv sync --all-extras --compile-bytecode && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# webui/server shells out to the `scrapling` binary on PATH (see
# webui/server/src/services/scraplingRunner.js) — the .venv/bin PATH entry
# above is what makes that resolve inside the container.
WORKDIR /app/webui/server
RUN npm ci --omit=dev

COPY --from=client-build /client/dist /app/webui/client/dist

EXPOSE 3000
VOLUME ["/app/webui/server/data"]

CMD ["node", "src/index.js"]
