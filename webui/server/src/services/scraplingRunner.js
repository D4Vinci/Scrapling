import { spawn } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { ALL_OPTIONS, CLI_COMMAND_NAME, FETCHER_TYPES } from "../optionsSchema.js";
import { appendJobLog, updateJob } from "../db.js";
import { emitDone, emitLog } from "./jobEvents.js";
import { downloadImages, extractImageUrls } from "./imageExtractor.js";

export function buildArgs(fetcherType, url, outputFile, options) {
  const args = ["extract", CLI_COMMAND_NAME[fetcherType], url, outputFile];
  const schema = ALL_OPTIONS[fetcherType] ?? [];

  for (const opt of schema) {
    const value = options[opt.name];
    if (value === undefined || value === null || value === "") continue;

    if (opt.type === "boolean") {
      if (value === true && opt.flag) args.push(opt.flag);
      if (value === false && opt.negFlag) args.push(opt.negFlag);
      continue;
    }

    if (opt.type === "list") {
      const items = Array.isArray(value) ? value : String(value).split("\n");
      for (const item of items) {
        const trimmed = item.trim();
        if (trimmed) args.push(opt.flag, trimmed);
      }
      continue;
    }

    if (opt.type === "multiselect") {
      // The CLI takes one --impersonate value; comma-joining several tells
      // Scrapling to pick a random one per request (see cli.py's __BuildRequest).
      const items = Array.isArray(value) ? value : [value];
      if (items.length) args.push(opt.flag, items.join(","));
      continue;
    }

    args.push(opt.flag, String(value));
  }

  return args;
}

function logLine(id, line) {
  const chunk = line.endsWith("\n") ? line : `${line}\n`;
  appendJobLog(id, chunk);
  emitLog(id, chunk);
}

// Runs the CLI with output streamed line-by-line to the job's log (persisted
// to the DB and pushed live over SSE) instead of buffered until exit, so the
// Current Job page can show what's actually happening in real time.
function runCliStreaming(id, args, { timeoutMs }) {
  return new Promise((resolve, reject) => {
    logLine(id, `$ scrapling ${args.join(" ")}`);
    const child = spawn("scrapling", args, { timeout: timeoutMs, killSignal: "SIGTERM" });
    let stderrTail = "";
    let buffer = "";

    function onChunk(text) {
      buffer += text;
      const lines = buffer.split("\n");
      buffer = lines.pop(); // keep the trailing partial line for the next chunk
      for (const line of lines) logLine(id, line);
    }

    child.stdout.on("data", (chunk) => onChunk(chunk.toString()));
    child.stderr.on("data", (chunk) => {
      const text = chunk.toString();
      stderrTail = (stderrTail + text).slice(-4000);
      onChunk(text);
    });
    child.on("error", (err) => {
      if (buffer) logLine(id, buffer);
      reject(err);
    });
    child.on("close", (code, signal) => {
      if (buffer) logLine(id, buffer);
      if (code === 0) {
        resolve();
      } else if (signal) {
        reject(new Error(`Killed (${signal}) — likely hit the ${Math.round(timeoutMs / 1000)}s timeout`));
      } else {
        reject(new Error(`scrapling exited with code ${code}${stderrTail ? `: ${stderrTail.trim()}` : ""}`));
      }
    });
  });
}

export async function runJob({ id, fetcherType, url, outputPath, options }) {
  const isBrowserJob = FETCHER_TYPES[fetcherType]?.kind === "browser";
  updateJob(id, { status: "running", started_at: new Date().toISOString() });
  const startedAt = Date.now();

  try {
    const args = buildArgs(fetcherType, url, outputPath, options);
    // Browser fetchers launch Chromium via Playwright/Patchright, which is
    // slow on a Pi's ARM CPU — give those a much longer ceiling than plain HTTP.
    await runCliStreaming(id, args, { timeoutMs: isBrowserJob ? 120_000 : 45_000 });
    logLine(id, "Done.");
    updateJob(id, {
      status: "success",
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - startedAt,
      output_path: outputPath,
    });
    emitDone(id, "success");
  } catch (err) {
    const message = String(err.message || "Unknown error").slice(0, 4000);
    logLine(id, `Error: ${message}`);
    updateJob(id, {
      status: "error",
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - startedAt,
      error: message,
    });
    emitDone(id, "error");
  }
}

// The "images" output format has no equivalent in `scrapling extract` (which
// only ever writes one html/md/txt file), so this fetches the raw page HTML
// via the CLI same as any other job, then does the image discovery/download
// itself: parses out every <img> (scoped to the CSS selector, if set),
// resolves lazy-load attributes and srcset, and downloads each one into its
// own folder with bounded concurrency.
export async function runImageJob({ id, fetcherType, url, outputDir, options }) {
  const isBrowserJob = FETCHER_TYPES[fetcherType]?.kind === "browser";
  updateJob(id, { status: "running", started_at: new Date().toISOString() });
  const startedAt = Date.now();

  try {
    await mkdir(outputDir, { recursive: true });
    const pagePath = path.join(outputDir, "page.html");
    const args = buildArgs(fetcherType, url, pagePath, options);
    await runCliStreaming(id, args, { timeoutMs: isBrowserJob ? 120_000 : 45_000 });

    logLine(id, "Scanning fetched page for images…");
    const html = await readFile(pagePath, "utf8");
    const imageUrls = extractImageUrls(html, url, options.css_selector);
    logLine(id, `Found ${imageUrls.length} candidate image URL(s). Downloading…`);
    const manifest = await downloadImages(imageUrls, outputDir);
    await writeFile(path.join(outputDir, "manifest.json"), JSON.stringify(manifest, null, 2));

    const okCount = manifest.filter((m) => m.status === "ok").length;
    logLine(id, `Downloaded ${okCount}/${manifest.length} image(s). Done.`);
    updateJob(id, {
      status: "success",
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - startedAt,
      output_path: outputDir,
      error: manifest.length && !okCount ? "Found images but none could be downloaded." : null,
    });
    emitDone(id, "success");
  } catch (err) {
    const message = String(err.message || "Unknown error").slice(0, 4000);
    logLine(id, `Error: ${message}`);
    updateJob(id, {
      status: "error",
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - startedAt,
      error: message,
    });
    emitDone(id, "error");
  }
}
