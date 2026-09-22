import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { randomUUID } from "node:crypto";
import { readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const execFileAsync = promisify(execFile);

const MAX_HTML_LENGTH = 2_000_000; // cap payload size for pathologically large pages
const BLOCKED_MARKERS = [
  /just a moment/i,
  /attention required/i,
  /cf-browser-verification/i,
  /captcha/i,
  /access denied/i,
  /403 forbidden/i,
  /enable javascript to continue/i,
];

function computeSignals(html) {
  const title = /<title[^>]*>([\s\S]*?)<\/title>/i.exec(html)?.[1]?.trim() || null;
  const textOnly = html
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  return {
    title,
    // A real page, even a sparse one, still has some visible text; a JS-app
    // shell that needs a browser to render (e.g. `<div id="root"></div>`)
    // has next to none. 40 was chosen to sit below realistic minimal content.
    looksEmpty: textOnly.length < 40,
    looksBlocked: BLOCKED_MARKERS.some((re) => re.test(html)),
  };
}

// Positional args (`extract <cmd> <url> <output_file>`) must come before any
// flags — the CLI parses output_file positionally, so a flag placed earlier
// gets mistaken for it.
async function fetchViaCli(cmd, url, flags, { timeoutMs }) {
  const tmpFile = path.join(tmpdir(), `scrapling-preview-${randomUUID()}.html`);
  try {
    await execFileAsync("scrapling", ["extract", cmd, url, tmpFile, ...flags], { timeout: timeoutMs });
    const raw = await readFile(tmpFile, "utf8");
    const truncated = raw.length > MAX_HTML_LENGTH;
    const html = truncated ? raw.slice(0, MAX_HTML_LENGTH) : raw;
    return { success: true, html, truncated, signals: computeSignals(html) };
  } catch (err) {
    return {
      success: false,
      error: String(err.stderr || err.message || "Fetch failed").slice(0, 2000),
      signals: {},
    };
  } finally {
    await rm(tmpFile, { force: true });
  }
}

// A quick plain GET — no browser, no JS rendering. Used both as its own fast
// preview and, in runRenderedPreview, as a baseline to compare a full
// browser render against (so we can tell whether JS rendering was the thing
// that actually mattered for this page).
export async function runPreview(url) {
  return fetchViaCli("get", url, ["--timeout", "15"], { timeoutMs: 20_000 });
}

// Decides which fetcher to recommend for the real job, by comparing the
// cheap plain-GET result against what a full browser render actually got.
function suggestFetcher(plain, rendered) {
  if (rendered.signals?.looksBlocked) {
    return { fetcher: "stealthy_fetch", reason: "Even a full browser render looks blocked (captcha/challenge page) — try Stealthy fetch." };
  }
  if (!plain.success || plain.signals?.looksBlocked) {
    return { fetcher: "stealthy_fetch", reason: "A plain GET looks blocked (captcha/challenge page) — Stealthy fetch is built to get past that." };
  }
  if (plain.signals?.looksEmpty && !rendered.signals?.looksEmpty) {
    return { fetcher: "fetch", reason: "A plain GET comes back almost empty, but the JS-rendered page has real content — this page needs a browser." };
  }
  return { fetcher: "get", reason: "A plain GET already returns the full content — no browser needed, and it's much faster." };
}

// Stage 2 of the URL preview: a full browser render (JS included), plus a
// parallel plain GET purely so we can compare the two and suggest which
// fetcher the real job should use. Much slower than runPreview, especially
// on a Pi — this only runs when the user explicitly asks to analyze a page,
// not on every keystroke.
export async function runRenderedPreview(url) {
  const [rendered, plain] = await Promise.all([
    fetchViaCli("fetch", url, ["--timeout", "45000"], { timeoutMs: 90_000 }),
    runPreview(url),
  ]);
  if (!rendered.success) return rendered;
  return { ...rendered, suggestion: suggestFetcher(plain, rendered) };
}
