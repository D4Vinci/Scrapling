import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { ALL_OPTIONS, CLI_COMMAND_NAME, FETCHER_TYPES } from "../optionsSchema.js";
import { updateJob } from "../db.js";

const execFileAsync = promisify(execFile);

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

export async function runJob({ id, fetcherType, url, outputPath, options }) {
  const args = buildArgs(fetcherType, url, outputPath, options);
  const isBrowserJob = FETCHER_TYPES[fetcherType]?.kind === "browser";

  updateJob(id, { status: "running", started_at: new Date().toISOString() });
  const startedAt = Date.now();

  try {
    // Browser fetchers launch Chromium via Playwright/Patchright, which is
    // slow on a Pi's ARM CPU — give those a much longer ceiling than plain HTTP.
    await execFileAsync("scrapling", args, { timeout: isBrowserJob ? 120_000 : 45_000 });
    updateJob(id, {
      status: "success",
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - startedAt,
      output_path: outputPath,
    });
  } catch (err) {
    updateJob(id, {
      status: "error",
      finished_at: new Date().toISOString(),
      duration_ms: Date.now() - startedAt,
      error: String(err.stderr || err.message || "Unknown error").slice(0, 4000),
    });
  }
}
