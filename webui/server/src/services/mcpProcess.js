import { spawn } from "node:child_process";

let child = null;
let meta = null;
const logBuffer = [];
const MAX_LOG_LINES = 200;

function pushLog(line) {
  logBuffer.push(line);
  if (logBuffer.length > MAX_LOG_LINES) logBuffer.shift();
}

export function status() {
  return {
    running: Boolean(child),
    pid: child?.pid ?? null,
    startedAt: meta?.startedAt ?? null,
    args: meta?.args ?? null,
    logs: logBuffer.slice(-100),
  };
}

export function start({ http, host, port, executablePath, authToken, allowedHosts, noAuth } = {}) {
  if (child) throw new Error("MCP server is already running");

  const args = ["mcp"];
  if (http) args.push("--http");
  if (host) args.push("--host", host);
  if (port) args.push("--port", String(port));
  if (executablePath) args.push("--executable-path", executablePath);
  if (Array.isArray(allowedHosts)) {
    for (const h of allowedHosts) if (h) args.push("--allowed-host", h);
  }
  if (noAuth) args.push("--no-auth");

  // Pass the token via env instead of --auth-token so it never shows up in
  // `ps`/process listings — matching the CLI's own --help recommendation.
  const env = { ...process.env };
  if (authToken) env.SCRAPLING_MCP_AUTH_TOKEN = authToken;

  child = spawn("scrapling", args, { env });
  meta = { startedAt: new Date().toISOString(), args };
  logBuffer.length = 0;

  child.stdout.on("data", (chunk) => pushLog(chunk.toString()));
  child.stderr.on("data", (chunk) => pushLog(chunk.toString()));
  child.on("exit", (code, signal) => {
    pushLog(`[process exited: code=${code} signal=${signal}]`);
    child = null;
    meta = null;
  });
  child.on("error", (err) => {
    pushLog(`[failed to start: ${err.message}]`);
    child = null;
    meta = null;
  });

  return status();
}

export function stop() {
  if (!child) throw new Error("MCP server is not running");
  child.kill("SIGTERM");
  return { stopping: true };
}
