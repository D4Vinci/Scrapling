const form = document.querySelector("#extract-form");
const runButton = document.querySelector("#run-button");
const errorBox = document.querySelector("#form-error");
const emptyState = document.querySelector("#empty-state");
const loadingState = document.querySelector("#loading-state");
const resultState = document.querySelector("#result-state");
const resultBody = document.querySelector("#result-body");
const resultSubtitle = document.querySelector("#result-subtitle");
const exportActions = document.querySelector("#export-actions");
let selectorType = "css";

document.querySelectorAll("[data-selector-type]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-selector-type]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    selectorType = button.dataset.selectorType;
    document.querySelector("#selector").placeholder = selectorType === "css" ? ".product-card" : "//article";
  });
});

function setLoading(active) {
  runButton.disabled = active;
  runButton.querySelector("span").textContent = active ? "Extracting…" : "Run extraction";
  emptyState.hidden = true;
  loadingState.hidden = !active;
  resultState.hidden = true;
  if (active) exportActions.hidden = true;
}

function escapeHTML(value) {
  const element = document.createElement("div");
  element.textContent = value;
  return element.innerHTML;
}

function renderResult(job) {
  loadingState.hidden = true;
  resultState.hidden = false;
  document.querySelector("#metric-status").textContent = job.status;
  document.querySelector("#metric-count").textContent = job.item_count;
  document.querySelector("#metric-time").textContent = `${job.duration_ms}ms`;
  resultSubtitle.textContent = job.title || job.final_url;
  resultBody.innerHTML = job.items.length
    ? job.items.map((item) => `<tr><td>${item.index}</td><td>${escapeHTML(item.value)}</td></tr>`).join("")
    : '<tr><td>—</td><td>No elements matched this selector.</td></tr>';

  document.querySelector("#export-json").href = `/api/jobs/${job.id}/export?format=json`;
  document.querySelector("#export-csv").href = `/api/jobs/${job.id}/export?format=csv`;
  exportActions.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";
  setLoading(true);
  const payload = {
    url: document.querySelector("#url").value,
    mode: document.querySelector("#mode").value,
    selector: document.querySelector("#selector").value,
    selector_type: selectorType,
    output_format: document.querySelector("#output-format").value,
    headless: document.querySelector("#headless").checked,
    network_idle: document.querySelector("#network-idle").checked,
    timeout: Number(document.querySelector("#timeout").value),
  };

  try {
    const response = await fetch("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Extraction failed");
    renderResult(data);
    await loadHistory();
  } catch (error) {
    loadingState.hidden = true;
    emptyState.hidden = false;
    errorBox.textContent = error.message;
  } finally {
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "Run extraction";
  }
});

function compactURL(value) {
  try {
    const parsed = new URL(value);
    return `${parsed.hostname}${parsed.pathname === "/" ? "" : parsed.pathname}`;
  } catch {
    return value;
  }
}

async function loadHistory() {
  const container = document.querySelector("#history-list");
  try {
    const response = await fetch("/api/jobs?limit=25");
    const data = await response.json();
    if (!data.jobs.length) {
      container.innerHTML = '<p class="history-empty">No indexed jobs yet.</p>';
      return;
    }
    container.innerHTML = data.jobs.map((job) => {
      const date = new Date(job.created_at);
      return `<article class="history-item">
        <time datetime="${job.created_at}">${date.toLocaleDateString()}<br>${date.toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"})}</time>
        <a href="${job.url}" target="_blank" rel="noreferrer" title="${escapeHTML(job.url)}">${escapeHTML(compactURL(job.url))}</a>
        <span class="mode">${escapeHTML(job.mode)}</span>
        <span class="meta duration">${job.duration_ms}ms</span>
        <strong>${job.item_count}</strong>
      </article>`;
    }).join("");
  } catch {
    container.innerHTML = '<p class="history-empty">History is temporarily unavailable.</p>';
  }
}

document.querySelector("#refresh-history").addEventListener("click", loadHistory);
loadHistory();
