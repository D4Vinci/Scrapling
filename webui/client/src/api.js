const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

export const getOptionsSchema = () => request("/options-schema");

export const createJob = (payload) => request("/jobs", { method: "POST", body: JSON.stringify(payload) });

export const getJob = (id) => request(`/jobs/${id}`);

export const getJobImages = (id) => request(`/jobs/${id}/images`);

export const listJobs = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/jobs${qs ? `?${qs}` : ""}`);
};

export const previewUrl = (url) => request("/preview", { method: "POST", body: JSON.stringify({ url }) });

export const listOutputFolders = () => request("/output-folders");

export const getMcpStatus = () => request("/mcp/status");

export const startMcp = (payload) => request("/mcp/start", { method: "POST", body: JSON.stringify(payload) });

export const stopMcp = () => request("/mcp/stop", { method: "POST" });
