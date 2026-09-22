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

// Stage 1 of the URL preview: a single plain GET, quick enough to run
// synchronously from a button click. This intentionally doesn't try the
// browser/stealthy fetchers yet — the `signals` this returns (looksBlocked,
// looksEmpty) are there so a later auto-retry pass has something to key off.
export async function runPreview(url) {
  const tmpFile = path.join(tmpdir(), `scrapling-preview-${randomUUID()}.html`);

  try {
    await execFileAsync("scrapling", ["extract", "get", url, tmpFile, "--timeout", "15"], { timeout: 20_000 });
    const raw = await readFile(tmpFile, "utf8");
    const truncated = raw.length > MAX_HTML_LENGTH;
    const html = truncated ? raw.slice(0, MAX_HTML_LENGTH) : raw;

    return { success: true, html, truncated, signals: computeSignals(html) };
  } catch (err) {
    return {
      success: false,
      error: String(err.stderr || err.message || "Preview fetch failed").slice(0, 2000),
      signals: {},
    };
  } finally {
    await rm(tmpFile, { force: true });
  }
}
