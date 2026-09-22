import { useEffect, useState } from "react";
import { getMcpStatus, startMcp, stopMcp } from "../api.js";

const INITIAL_FORM = {
  http: false,
  host: "127.0.0.1",
  port: 8000,
  executablePath: "",
  authToken: "",
  allowedHosts: "",
  noAuth: false,
};

export default function McpManager() {
  const [status, setStatus] = useState(null);
  const [form, setForm] = useState(INITIAL_FORM);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      setStatus(await getMcpStatus());
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 3000);
    return () => clearInterval(timer);
  }, []);

  function set(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleStart(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await startMcp({
        ...form,
        port: Number(form.port),
        allowedHosts: form.allowedHosts
          .split(",")
          .map((h) => h.trim())
          .filter(Boolean),
      });
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleStop() {
    setBusy(true);
    setError(null);
    try {
      await stopMcp();
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mcp-manager">
      <h1>MCP server</h1>

      {status && (
        <div className="mcp-status">
          <p>
            Status: <strong>{status.running ? "running" : "stopped"}</strong>
            {status.running && ` (pid ${status.pid}, since ${new Date(status.startedAt).toLocaleTimeString()})`}
          </p>
          {status.running && (
            <button onClick={handleStop} disabled={busy}>
              Stop
            </button>
          )}
        </div>
      )}

      {!status?.running && (
        <form onSubmit={handleStart} className="mcp-form">
          <label className="field">
            <span>Transport</span>
            <select value={form.http ? "http" : "stdio"} onChange={(e) => set("http", e.target.value === "http")}>
              <option value="stdio">stdio</option>
              <option value="http">streamable-http</option>
            </select>
          </label>

          {form.http && (
            <>
              <label className="field">
                <span>Host</span>
                <input value={form.host} onChange={(e) => set("host", e.target.value)} />
              </label>
              <label className="field">
                <span>Port</span>
                <input type="number" value={form.port} onChange={(e) => set("port", e.target.value)} />
              </label>
              <label className="field">
                <span>Auth token</span>
                <input
                  type="password"
                  value={form.authToken}
                  onChange={(e) => set("authToken", e.target.value)}
                  placeholder="sent via env var, never as a CLI flag"
                />
              </label>
              <label className="field">
                <span>Allowed hosts (comma-separated)</span>
                <input value={form.allowedHosts} onChange={(e) => set("allowedHosts", e.target.value)} />
              </label>
              <label className="field checkbox-field">
                <input type="checkbox" checked={form.noAuth} onChange={(e) => set("noAuth", e.target.checked)} />
                <span>Allow unauthenticated (not recommended)</span>
              </label>
              {form.noAuth && !form.authToken && <p className="warning">This will serve the MCP server with no authentication at all.</p>}
            </>
          )}

          <label className="field">
            <span>Custom browser executable path</span>
            <input value={form.executablePath} onChange={(e) => set("executablePath", e.target.value)} />
          </label>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={busy}>
            Start
          </button>
        </form>
      )}

      {status?.logs?.length > 0 && (
        <>
          <h2>Logs</h2>
          <pre className="logs">{status.logs.join("")}</pre>
        </>
      )}
    </div>
  );
}
