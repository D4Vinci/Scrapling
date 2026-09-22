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

const IMAGE_EXTENSIONS = new Set(["jpg", "jpeg", "png", "gif", "webp", "avif", "bmp", "svg", "ico"]);

// True for a string that looks like a path/URL ending in a known image
// extension — used to fish image URLs out of places that aren't `src`/
// `srcset` at all, like `onclick="openModal('...')"` lightbox handlers,
// which plenty of gallery sites use instead of a real <img src>.
function looksLikeImageUrl(str) {
  if (!str || str.length > 2000) return false;
  const withoutQuery = str.split(/[?#]/)[0];
  const ext = withoutQuery.split(".").pop()?.toLowerCase();
  return Boolean(ext) && IMAGE_EXTENSIONS.has(ext) && !/\s/.test(withoutQuery);
}

// Pulls out every single- or double-quoted substring in an attribute value
// (e.g. the two arguments to `openModal('a.jpg', 'caption')`), plus the raw
// value itself, as candidates to test with looksLikeImageUrl.
function candidateStringsFromAttrValue(value) {
  const quoted = [...value.matchAll(/'([^']+)'|"([^"]+)"/g)].map((m) => m[1] ?? m[2]);
  return [value, ...quoted];
}

// Scans the given HTML for images (scoped to `selector` if provided, else the
// whole document) and returns their absolute URLs in document order, deduped.
// Two passes: first the well-known <img> attributes (src, lazy-load
// data-* variants, srcset), then a generic sweep of every element's
// attributes — onclick handlers and data-* attributes included — for any
// value that looks like an image URL, since a lot of gallery/lightbox
// markup never puts the image in an <img> tag's src at all.
export function extractImageUrls(html, pageUrl, selector) {
  const $ = cheerio.load(html);
  let scope = $("body").length ? $("body") : $.root();
  if (selector && selector.trim()) {
    const matched = $(selector);
    if (matched.length) scope = matched;
  }

  const seen = new Set();
  const urls = [];
  function addCandidate(candidate) {
    if (!candidate) return;
    let absolute;
    try {
      absolute = candidate.startsWith("data:") ? candidate : new URL(candidate, pageUrl).toString();
    } catch {
      return;
    }
    if (seen.has(absolute)) return;
    seen.add(absolute);
    urls.push(absolute);
  }

  const imgElements = [];
  scope.each((_, el) => {
    const $el = $(el);
    if ($el.is("img")) imgElements.push(el);
    $el.find("img").each((__, img) => imgElements.push(img));
  });
  for (const el of imgElements) {
    const $el = $(el);
    addCandidate(
      $el.attr("src") ||
        $el.attr("data-src") ||
        $el.attr("data-lazy-src") ||
        $el.attr("data-original") ||
        (($el.attr("srcset") || $el.attr("data-srcset")) && widestFromSrcset($el.attr("srcset") || $el.attr("data-srcset"))),
    );
  }

  const allElements = [];
  scope.each((_, el) => {
    allElements.push(el);
    $(el)
      .find("*")
      .each((__, child) => allElements.push(child));
  });
  for (const el of allElements) {
    for (const [name, value] of Object.entries(el.attribs || {})) {
      if (name === "src" || name === "srcset") continue; // already handled above for <img>
      for (const candidate of candidateStringsFromAttrValue(value)) {
        if (looksLikeImageUrl(candidate)) addCandidate(candidate);
      }
    }
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
