# Scrapling Web UI

A small Express + React front end for Scrapling's `extract` CLI, meant to run
as a lightweight always-on service on a Raspberry Pi.

## Architecture

```
webui/
├── server/   Express 5 API — spawns the `scrapling` CLI per job, tracks
│             job history in SQLite, and manages the `scrapling mcp` process
└── client/   React 19 + Vite 8 SPA — job form, history table, job detail
              view, and an MCP server control panel
```

The server never calls Scrapling's Python API directly; it shells out to the
`scrapling` CLI (`execFile`, arguments passed as an array — never through a
shell) so the Node process has no Python dependency beyond `scrapling` being
on `PATH`. Every job runs as a background task and the client polls for
status, because `fetch`/`stealthy-fetch` launch a real Chromium via
Playwright/Patchright, which can take a while on a Pi's ARM CPU.

Job history lives in `server/data/jobs.db` (SQLite) and job output files in
`server/data/outputs/`. The MCP server (`scrapling mcp`) is managed as a
single long-lived child process; its auth token, when set, is passed via the
`SCRAPLING_MCP_AUTH_TOKEN` environment variable rather than `--auth-token`,
so it never shows up in `ps` — the same thing the CLI's own `--help` text
recommends.

## Prerequisites

On the Pi:

```bash
pip install "scrapling[shell]"
scrapling install         # downloads Chromium + browser deps
node -v                   # needs Node >= 18 (Express 5 requirement)
```

## Development

```bash
cd webui/server && npm install && npm run dev   # http://localhost:3000
cd webui/client && npm install && npm run dev   # http://localhost:5173, proxies /api to :3000
```

## Production (single process on the Pi)

```bash
cd webui/client && npm install && npm run build   # writes webui/client/dist
cd webui/server && npm install && npm start        # serves the API + the built SPA on one port
```

### Running as a systemd service

```ini
# /etc/systemd/system/scrapling-webui.service
[Unit]
Description=Scrapling Web UI
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/scrapling/webui/server
ExecStart=/usr/bin/node src/index.js
Restart=on-failure
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now scrapling-webui
```

## Notes / known gaps in this scaffold

- No authentication on the web UI itself — fine on a trusted LAN, not fine
  exposed to the internet. Put it behind a reverse proxy with basic auth
  (nginx/Caddy) before doing that.
- The job runner has no queue/concurrency limit — two `stealthy-fetch` jobs
  launching Chromium at once on a Pi will contend hard for CPU/RAM. A
  simple in-process queue (e.g. cap concurrent browser jobs at 1) would be
  the next thing to add if you hit that.
- Output files in `server/data/outputs/` are never cleaned up automatically.
