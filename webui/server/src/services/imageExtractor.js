import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import * as cheerio from "cheerio";

const CONCURRENCY = 4;

const EXT_BY_MIME = {
  "image/jpeg": "jpg",
  "image/png": "png",
  "image/gif": "gif",
  "image/webp": "webp",
  "image/svg+xml": "svg",
  "image/avif": "avif",
  "image/bmp": "bmp",
  "image/x-icon": "ico",
};

// Picks the widest candidate out of a `srcset` (e.g. "a.jpg 480w, b.jpg 1024w"),
// since that's the highest-resolution version the page offers.
function widestFromSrcset(srcset) {
  const candidates = srcset
    .split(",")
    .map((part) => part.trim().split(/\s+/))
    .filter((parts) => parts[0]);
  if (!candidates.length) return null;
  candidates.sort((a, b) => (parseInt(b[1]) || 0) - (parseInt(a[1]) || 0));
  return candidates[0][0];
}

// Scans the given HTML for images (scoped to `selector` if provided, else the
// whole document) and returns their absolute URLs in document order, deduped.
// Looks past plain `src` at the common lazy-load attributes too, since a lot
// of sites don't put the real image URL in `src` until JS runs.
export function extractImageUrls(html, pageUrl, selector) {
  const $ = cheerio.load(html);
  let scope = $("body").length ? $("body") : $.root();
  if (selector && selector.trim()) {
    const matched = $(selector);
    if (matched.length) scope = matched;
  }

  const elements = [];
  scope.each((_, el) => {
    const $el = $(el);
    if ($el.is("img")) elements.push(el);
    $el.find("img").each((__, img) => elements.push(img));
  });

  const seen = new Set();
  const urls = [];
  for (const el of elements) {
    const $el = $(el);
    const candidate =
      $el.attr("src") ||
      $el.attr("data-src") ||
      $el.attr("data-lazy-src") ||
      $el.attr("data-original") ||
      (($el.attr("srcset") || $el.attr("data-srcset")) && widestFromSrcset($el.attr("srcset") || $el.attr("data-srcset")));
    if (!candidate) continue;

    let absolute;
    try {
      absolute = candidate.startsWith("data:") ? candidate : new URL(candidate, pageUrl).toString();
    } catch {
      continue;
    }
    if (seen.has(absolute)) continue;
    seen.add(absolute);
    urls.push(absolute);
  }
  return urls;
}

function extensionFor(url, contentType) {
  if (url.startsWith("data:")) {
    const mime = url.slice(5, url.indexOf(";"));
    return EXT_BY_MIME[mime] || "bin";
  }
  const fromPath = path.extname(new URL(url).pathname).replace(".", "").toLowerCase();
  if (fromPath && fromPath.length <= 5) return fromPath;
  return EXT_BY_MIME[contentType?.split(";")[0]?.trim()] || "bin";
}

function sanitizeBaseName(url, index) {
  if (url.startsWith("data:")) return `image-${index + 1}`;
  const base = path.basename(new URL(url).pathname).split(".")[0];
  const cleaned = (base || "").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 60);
  return cleaned || `image-${index + 1}`;
}

async function downloadOne(url, index, destDir, usedNames) {
  try {
    let bytes;
    let contentType;
    if (url.startsWith("data:")) {
      const comma = url.indexOf(",");
      const meta = url.slice(5, comma);
      contentType = meta.split(";")[0];
      const isBase64 = meta.includes("base64");
      const data = url.slice(comma + 1);
      bytes = isBase64 ? Buffer.from(data, "base64") : Buffer.from(decodeURIComponent(data), "utf8");
    } else {
      const res = await fetch(url, { signal: AbortSignal.timeout(20_000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      contentType = res.headers.get("content-type");
      bytes = Buffer.from(await res.arrayBuffer());
    }

    const ext = extensionFor(url, contentType);
    let name = `${sanitizeBaseName(url, index)}.${ext}`;
    let n = 1;
    while (usedNames.has(name)) {
      name = `${sanitizeBaseName(url, index)}-${n}.${ext}`;
      n += 1;
    }
    usedNames.add(name);

    await writeFile(path.join(destDir, name), bytes);
    return { url, filename: name, status: "ok", bytes: bytes.length };
  } catch (err) {
    return { url, status: "error", error: String(err.message || err) };
  }
}

// Downloads every URL into destDir with bounded concurrency (a Pi's network/CPU
// can't handle downloading dozens of images at once) and returns a manifest
// describing what happened to each one.
export async function downloadImages(urls, destDir) {
  await mkdir(destDir, { recursive: true });
  const usedNames = new Set();
  const results = new Array(urls.length);
  let next = 0;

  async function worker() {
    while (next < urls.length) {
      const i = next++;
      results[i] = await downloadOne(urls[i], i, destDir, usedNames);
    }
  }

  await Promise.all(Array.from({ length: Math.min(CONCURRENCY, urls.length) }, worker));
  return results;
}
