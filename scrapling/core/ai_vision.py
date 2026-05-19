"""Vision-assisted selector recovery + anti-detection toolkit for Scrapling MCP.

This module implements `VisionMCPTools`, a collection of `@staticmethod async`
helpers that complement the standard MCP fetcher tools when:

* CSS selectors break and a page needs to be located via DOM + visual cues.
* A page is gated by Cloudflare / Akamai / hCaptcha / etc. and we want to
  diagnose it before paying for a full stealth fetch.
* A long-lived browser session needs a stable, locale-aligned fingerprint that
  matches the egress proxy.

All methods return a `VisionResponse` so callers (LLM agents) get a uniform
shape regardless of which capability they invoked.
"""

from __future__ import annotations

import base64
import hashlib
import io
import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Soft imports - we never want this module to break the import graph just
# because an optional capability (PIL / pytesseract / a sibling MCP module
# that is still being authored in parallel) is missing.
# ---------------------------------------------------------------------------

try:  # Pillow is used for screenshot diffing + OCR pre-processing.
    from PIL import Image, ImageChops  # type: ignore
except Exception:  # pragma: no cover - pillow is an optional runtime dep.
    Image = None  # type: ignore
    ImageChops = None  # type: ignore

try:
    # ai_interact.py is being authored by another agent in parallel. We import
    # defensively so that this module is still importable on its own.
    from scrapling.core.ai_interact import (  # type: ignore
        _SESSION_REGISTRY,
        _PAGE_REGISTRY,
        get_or_create_page,
    )
except Exception:  # pragma: no cover - sibling module not yet ready.
    _SESSION_REGISTRY: Dict[str, Any] = {}
    _PAGE_REGISTRY: Dict[str, Any] = {}

    async def get_or_create_page(session_id: str):  # type: ignore
        """Fallback when ai_interact is not yet available.

        The real implementation lives in `ai_interact.py`. Until it is wired
        up we raise a clear error rather than silently doing nothing.
        """
        raise RuntimeError(
            "ai_interact._SESSION_REGISTRY is not initialised; cannot resolve "
            f"session_id={session_id!r}."
        )


# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------


class VisionResponse(BaseModel):
    """Uniform return type for every VisionMCPTools method."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    method: Optional[str] = None


# ---------------------------------------------------------------------------
# Country -> timezone / locale mapping for `align_with_proxy`.
# Roughly the 30 most common egress geos for residential / DC proxies.
# ---------------------------------------------------------------------------

_COUNTRY_PROFILES: Dict[str, Dict[str, str]] = {
    "US": {"timezone": "America/New_York", "locale": "en-US", "accept_language": "en-US,en;q=0.9"},
    "CA": {"timezone": "America/Toronto", "locale": "en-CA", "accept_language": "en-CA,en;q=0.9,fr-CA;q=0.5"},
    "MX": {"timezone": "America/Mexico_City", "locale": "es-MX", "accept_language": "es-MX,es;q=0.9,en;q=0.5"},
    "BR": {"timezone": "America/Sao_Paulo", "locale": "pt-BR", "accept_language": "pt-BR,pt;q=0.9,en;q=0.5"},
    "AR": {"timezone": "America/Argentina/Buenos_Aires", "locale": "es-AR", "accept_language": "es-AR,es;q=0.9"},
    "GB": {"timezone": "Europe/London", "locale": "en-GB", "accept_language": "en-GB,en;q=0.9"},
    "IE": {"timezone": "Europe/Dublin", "locale": "en-IE", "accept_language": "en-IE,en;q=0.9"},
    "DE": {"timezone": "Europe/Berlin", "locale": "de-DE", "accept_language": "de-DE,de;q=0.9,en;q=0.5"},
    "FR": {"timezone": "Europe/Paris", "locale": "fr-FR", "accept_language": "fr-FR,fr;q=0.9,en;q=0.5"},
    "ES": {"timezone": "Europe/Madrid", "locale": "es-ES", "accept_language": "es-ES,es;q=0.9,en;q=0.5"},
    "IT": {"timezone": "Europe/Rome", "locale": "it-IT", "accept_language": "it-IT,it;q=0.9,en;q=0.5"},
    "NL": {"timezone": "Europe/Amsterdam", "locale": "nl-NL", "accept_language": "nl-NL,nl;q=0.9,en;q=0.5"},
    "BE": {"timezone": "Europe/Brussels", "locale": "nl-BE", "accept_language": "nl-BE,nl;q=0.9,fr-BE;q=0.5"},
    "CH": {"timezone": "Europe/Zurich", "locale": "de-CH", "accept_language": "de-CH,de;q=0.9,en;q=0.5"},
    "AT": {"timezone": "Europe/Vienna", "locale": "de-AT", "accept_language": "de-AT,de;q=0.9"},
    "PL": {"timezone": "Europe/Warsaw", "locale": "pl-PL", "accept_language": "pl-PL,pl;q=0.9,en;q=0.5"},
    "SE": {"timezone": "Europe/Stockholm", "locale": "sv-SE", "accept_language": "sv-SE,sv;q=0.9,en;q=0.5"},
    "NO": {"timezone": "Europe/Oslo", "locale": "nb-NO", "accept_language": "nb-NO,nb;q=0.9,en;q=0.5"},
    "FI": {"timezone": "Europe/Helsinki", "locale": "fi-FI", "accept_language": "fi-FI,fi;q=0.9,en;q=0.5"},
    "DK": {"timezone": "Europe/Copenhagen", "locale": "da-DK", "accept_language": "da-DK,da;q=0.9,en;q=0.5"},
    "RU": {"timezone": "Europe/Moscow", "locale": "ru-RU", "accept_language": "ru-RU,ru;q=0.9,en;q=0.5"},
    "UA": {"timezone": "Europe/Kyiv", "locale": "uk-UA", "accept_language": "uk-UA,uk;q=0.9,en;q=0.5"},
    "TR": {"timezone": "Europe/Istanbul", "locale": "tr-TR", "accept_language": "tr-TR,tr;q=0.9,en;q=0.5"},
    "JP": {"timezone": "Asia/Tokyo", "locale": "ja-JP", "accept_language": "ja-JP,ja;q=0.9,en;q=0.5"},
    "KR": {"timezone": "Asia/Seoul", "locale": "ko-KR", "accept_language": "ko-KR,ko;q=0.9,en;q=0.5"},
    "CN": {"timezone": "Asia/Shanghai", "locale": "zh-CN", "accept_language": "zh-CN,zh;q=0.9,en;q=0.5"},
    "HK": {"timezone": "Asia/Hong_Kong", "locale": "zh-HK", "accept_language": "zh-HK,zh;q=0.9,en;q=0.5"},
    "TW": {"timezone": "Asia/Taipei", "locale": "zh-TW", "accept_language": "zh-TW,zh;q=0.9,en;q=0.5"},
    "SG": {"timezone": "Asia/Singapore", "locale": "en-SG", "accept_language": "en-SG,en;q=0.9,zh;q=0.5"},
    "IN": {"timezone": "Asia/Kolkata", "locale": "en-IN", "accept_language": "en-IN,en;q=0.9,hi;q=0.5"},
    "AU": {"timezone": "Australia/Sydney", "locale": "en-AU", "accept_language": "en-AU,en;q=0.9"},
    "NZ": {"timezone": "Pacific/Auckland", "locale": "en-NZ", "accept_language": "en-NZ,en;q=0.9"},
    "ZA": {"timezone": "Africa/Johannesburg", "locale": "en-ZA", "accept_language": "en-ZA,en;q=0.9"},
    "AE": {"timezone": "Asia/Dubai", "locale": "ar-AE", "accept_language": "ar-AE,ar;q=0.9,en;q=0.5"},
    "IL": {"timezone": "Asia/Jerusalem", "locale": "he-IL", "accept_language": "he-IL,he;q=0.9,en;q=0.5"},
}


# ---------------------------------------------------------------------------
# Init-script template for humanize_fingerprint.
# Placeholders are replaced via simple .replace() so we don't pull in jinja.
# ---------------------------------------------------------------------------

_FINGERPRINT_TEMPLATE = r"""
(() => {
  try {
    const seed = SEED_PLACEHOLDER;
    const rand = (n) => {
      const s = seed + n;
      const v = Math.sin(s) * 10000;
      return ((v - Math.floor(v)) + 1) % 1;
    };

    // -------- Canvas: deterministic micro-noise --------
    if (CANVAS_LOCK_PLACEHOLDER) {
      const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
      HTMLCanvasElement.prototype.toDataURL = function (...args) {
        try {
          const ctx = this.getContext('2d');
          if (ctx) {
            const noise = rand(this.width * this.height + 1);
            ctx.fillStyle = `rgba(${Math.floor(noise * 256)}, 0, 0, 0.0001)`;
            ctx.fillRect(0, 0, 1, 1);
          }
        } catch (e) {}
        return origToDataURL.apply(this, args);
      };

      const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
      CanvasRenderingContext2D.prototype.getImageData = function (...args) {
        const data = origGetImageData.apply(this, args);
        try {
          for (let i = 0; i < data.data.length; i += 4) {
            const n = rand(i) * 2 - 1;
            data.data[i] = Math.max(0, Math.min(255, data.data[i] + (n < 0 ? 0 : 1)));
          }
        } catch (e) {}
        return data;
      };
    }

    // -------- WebGL vendor / renderer pinning --------
    const patchGL = (proto) => {
      if (!proto) return;
      const orig = proto.getParameter;
      proto.getParameter = function (p) {
        if (p === 37445) return 'Intel Inc.';
        if (p === 37446) return 'Intel Iris OpenGL Engine';
        return orig.call(this, p);
      };
    };
    if (typeof WebGLRenderingContext !== 'undefined') patchGL(WebGLRenderingContext.prototype);
    if (typeof WebGL2RenderingContext !== 'undefined') patchGL(WebGL2RenderingContext.prototype);

    // -------- AudioContext: tiny per-sample noise --------
    if (typeof AudioBuffer !== 'undefined') {
      const origGetChannelData = AudioBuffer.prototype.getChannelData;
      AudioBuffer.prototype.getChannelData = function (channel) {
        const data = origGetChannelData.call(this, channel);
        try {
          for (let i = 0; i < data.length; i += 100) {
            data[i] = data[i] + (rand(i) * 1e-7);
          }
        } catch (e) {}
        return data;
      };
    }

    // -------- navigator.languages aligned with locale --------
    Object.defineProperty(navigator, 'languages', {
      get: () => LANGS_PLACEHOLDER,
      configurable: true,
    });
    Object.defineProperty(navigator, 'language', {
      get: () => (LANGS_PLACEHOLDER)[0],
      configurable: true,
    });

    // -------- Timezone offset override (minutes, west = +) --------
    if (TZ_OFFSET_PLACEHOLDER !== null) {
      const off = TZ_OFFSET_PLACEHOLDER;
      Date.prototype.getTimezoneOffset = function () { return off; };
    }

    // -------- screen.width / height override --------
    if (SCREEN_W_PLACEHOLDER !== null) {
      Object.defineProperty(screen, 'width', { get: () => SCREEN_W_PLACEHOLDER, configurable: true });
      Object.defineProperty(screen, 'availWidth', { get: () => SCREEN_W_PLACEHOLDER, configurable: true });
    }
    if (SCREEN_H_PLACEHOLDER !== null) {
      Object.defineProperty(screen, 'height', { get: () => SCREEN_H_PLACEHOLDER, configurable: true });
      Object.defineProperty(screen, 'availHeight', { get: () => SCREEN_H_PLACEHOLDER, configurable: true });
    }
  } catch (err) {
    // Never let fingerprint patches break the page.
  }
})();
"""


# ---------------------------------------------------------------------------
# Protection signatures used by detect_protection.
# (regex, label, severity-weight)
# ---------------------------------------------------------------------------

_PROTECTION_SIGNATURES: List[Tuple[re.Pattern, str, int]] = [
    (re.compile(r"cf-(ray|chl|mitigated)|cloudflare|__cf_bm|cdn-cgi/challenge", re.I), "Cloudflare", 3),
    (re.compile(r"akamai|ak_bmsc|_abck|bm_sz", re.I), "Akamai", 3),
    (re.compile(r"datadome|dd_cookie|x-datadome", re.I), "DataDome", 3),
    (re.compile(r"perimeterx|_px[a-z0-9]*|x-px-", re.I), "PerimeterX", 3),
    (re.compile(r"incapsula|imperva|visid_incap", re.I), "Imperva/Incapsula", 3),
    (re.compile(r"hcaptcha\.com|h-captcha", re.I), "hCaptcha", 2),
    (re.compile(r"recaptcha|google\.com/recaptcha|grecaptcha", re.I), "reCAPTCHA", 2),
    (re.compile(r"challenges\.cloudflare\.com/turnstile|cf-turnstile", re.I), "Cloudflare Turnstile", 2),
    (re.compile(r"kasada|x-kpsdk", re.I), "Kasada", 3),
    (re.compile(r"shape\s*security|f5-shape", re.I), "Shape/F5", 3),
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _seed_from_session(session_id: str) -> int:
    """Stable integer seed derived from a session id - same id, same noise."""
    digest = hashlib.sha256(session_id.encode("utf-8")).digest()
    # Use first 4 bytes as unsigned int, scale down so JS Math.sin stays sane.
    return int.from_bytes(digest[:4], "big") % 1_000_000


async def _resolve_page(session_id: str):
    """Look up an already-attached page or create one via ai_interact."""
    page = _PAGE_REGISTRY.get(session_id)
    if page is not None:
        return page
    return await get_or_create_page(session_id)


def _b64_to_image(image_base64: str):
    """Decode a base64 (with optional data: prefix) string into a PIL Image."""
    if Image is None:
        raise RuntimeError("Pillow (PIL) is required but not installed.")
    if "," in image_base64 and image_base64.strip().startswith("data:"):
        image_base64 = image_base64.split(",", 1)[1]
    raw = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(raw))


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _score_element(node: Dict[str, Any], query: str) -> Tuple[float, Dict[str, Any]]:
    """Heuristic confidence score for a single accessibility / DOM node."""
    q = query.strip().lower()
    if not q:
        return 0.0, {}

    text = _safe_text(node.get("text") or node.get("name") or node.get("innerText")).lower()
    aria = _safe_text(node.get("aria_label") or node.get("ariaLabel")).lower()
    title = _safe_text(node.get("title")).lower()
    placeholder = _safe_text(node.get("placeholder")).lower()
    role = _safe_text(node.get("role") or node.get("tag")).lower()

    score = 0.0
    matched_via = []

    if text and text == q:
        score += 1.0
        matched_via.append("text_exact")
    elif text and q in text:
        score += 0.6
        matched_via.append("text_contains")

    for label, value in (("aria", aria), ("title", title), ("placeholder", placeholder)):
        if value and q in value:
            score += 0.5
            matched_via.append(f"{label}_contains")

    if role and q in role:
        score += 0.2
        matched_via.append("role_contains")

    # Boost for "obvious" interactive elements - exactly the kind of selectors
    # an LLM is most often trying to recover.
    if role in {"button", "link", "textbox", "combobox", "checkbox", "radio", "menuitem", "tab"}:
        score *= 1.25
    if node.get("tag") in {"a", "button", "input", "select", "textarea"}:
        score *= 1.1

    # Visibility / interactability tie-breakers.
    if node.get("visible") is False:
        score *= 0.4
    if node.get("disabled"):
        score *= 0.5

    return score, {"matched_via": matched_via}


# JS snippet that walks the DOM and produces a flat list of candidate nodes.
# We keep it inline to avoid an extra file roundtrip on Playwright init.
_DOM_SNAPSHOT_JS = r"""
() => {
  const out = [];
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const s = window.getComputedStyle(el);
    if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) === 0) return false;
    return true;
  };
  const cssPath = (el) => {
    if (!(el instanceof Element)) return '';
    const path = [];
    while (el && el.nodeType === 1 && path.length < 6) {
      let sel = el.nodeName.toLowerCase();
      if (el.id) { sel += '#' + CSS.escape(el.id); path.unshift(sel); break; }
      const parent = el.parentNode;
      if (parent) {
        const siblings = Array.from(parent.children).filter(c => c.nodeName === el.nodeName);
        if (siblings.length > 1) sel += `:nth-of-type(${siblings.indexOf(el) + 1})`;
      }
      path.unshift(sel);
      el = el.parentElement;
    }
    return path.join(' > ');
  };
  const xPath = (el) => {
    if (!(el instanceof Element)) return '';
    const segs = [];
    while (el && el.nodeType === 1) {
      let i = 1, sib = el.previousSibling;
      while (sib) { if (sib.nodeType === 1 && sib.nodeName === el.nodeName) i++; sib = sib.previousSibling; }
      segs.unshift(`${el.nodeName.toLowerCase()}[${i}]`);
      el = el.parentElement;
    }
    return '/' + segs.join('/');
  };
  const all = document.querySelectorAll('a,button,input,select,textarea,[role],[onclick],[tabindex]');
  let idx = 0;
  for (const el of all) {
    if (idx > 1500) break;
    const r = el.getBoundingClientRect();
    out.push({
      index: idx++,
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role') || '',
      text: (el.innerText || el.value || '').trim().slice(0, 200),
      aria_label: el.getAttribute('aria-label') || '',
      title: el.getAttribute('title') || '',
      placeholder: el.getAttribute('placeholder') || '',
      type: el.getAttribute('type') || '',
      name: el.getAttribute('name') || '',
      id: el.id || '',
      href: el.getAttribute('href') || '',
      disabled: el.disabled === true,
      visible: visible(el),
      bbox: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
      css_selector: cssPath(el),
      xpath: xPath(el),
    });
  }
  return out;
}
"""


# ---------------------------------------------------------------------------
# Public toolset
# ---------------------------------------------------------------------------


class VisionMCPTools:
    """Vision + anti-detection MCP helpers. Static methods are awaited by callers."""

    # ------------------------------------------------------------------
    # 1. vision_select - heuristic visual + DOM selector recovery
    # ------------------------------------------------------------------
    @staticmethod
    async def vision_select(
        session_id: str,
        query: str,
        return_top: int = 5,
        screenshot_save_path: Optional[str] = None,
    ) -> VisionResponse:
        """Locate elements by combining DOM/AXTree snapshot with text heuristics.

        No external LLM is used - scoring is local and deterministic.
        """
        try:
            page = await _resolve_page(session_id)
        except Exception as e:
            return VisionResponse(success=False, error=f"session_not_found: {e}", method="vision_select")

        try:
            nodes: List[Dict[str, Any]] = await page.evaluate(_DOM_SNAPSHOT_JS)
        except Exception as e:
            return VisionResponse(success=False, error=f"dom_snapshot_failed: {e}", method="vision_select")

        # Optional screenshot - useful for the caller's own debugging, not used
        # internally for scoring (we don't run pixel-level OCR here).
        screenshot_b64: Optional[str] = None
        try:
            shot = await page.screenshot(full_page=True, type="png")
            if screenshot_save_path:
                with open(screenshot_save_path, "wb") as fh:
                    fh.write(shot)
            screenshot_b64 = base64.b64encode(shot).decode("ascii")
        except Exception:
            pass  # screenshots are best-effort.

        scored: List[Tuple[float, Dict[str, Any], Dict[str, Any]]] = []
        for node in nodes:
            score, meta = _score_element(node, query)
            if score > 0:
                scored.append((score, node, meta))
        scored.sort(key=lambda t: t[0], reverse=True)

        results = []
        for score, node, meta in scored[: max(1, return_top)]:
            bbox = node.get("bbox") or [0, 0, 0, 0]
            results.append(
                {
                    "element_index": node.get("index"),
                    "css_selector": node.get("css_selector"),
                    "xpath": node.get("xpath"),
                    "role": node.get("role") or node.get("tag"),
                    "tag": node.get("tag"),
                    "text": node.get("text"),
                    "bbox": bbox,
                    "confidence": round(min(score, 1.5) / 1.5, 3),
                    "matched_via": meta.get("matched_via", []),
                }
            )

        return VisionResponse(
            success=bool(results),
            data={
                "query": query,
                "candidates": results,
                "total_scanned": len(nodes),
                "screenshot_base64": screenshot_b64 if not screenshot_save_path else None,
                "screenshot_path": screenshot_save_path,
                "hint": (
                    "no element matched the query; consider rephrasing, calling "
                    "find_clickable_elements first, or running get_page_state to "
                    "see what's actually on the page"
                ) if not results else None,
            },
            error=None if results else f"no element matched query: {query!r}",
            method="vision_select",
        )

    # ------------------------------------------------------------------
    # 2. find_clickable_elements - "map" of every clickable on the page
    # ------------------------------------------------------------------
    @staticmethod
    async def find_clickable_elements(
        session_id: str,
        viewport_only: bool = True,
    ) -> VisionResponse:
        try:
            page = await _resolve_page(session_id)
        except Exception as e:
            return VisionResponse(success=False, error=f"session_not_found: {e}", method="find_clickable_elements")

        try:
            nodes: List[Dict[str, Any]] = await page.evaluate(_DOM_SNAPSHOT_JS)
        except Exception as e:
            return VisionResponse(success=False, error=f"dom_snapshot_failed: {e}", method="find_clickable_elements")

        viewport: Dict[str, int] = {}
        try:
            viewport = await page.evaluate(
                "() => ({w: window.innerWidth, h: window.innerHeight, sx: window.scrollX, sy: window.scrollY})"
            )
        except Exception:
            viewport = {"w": 0, "h": 0, "sx": 0, "sy": 0}

        cleaned = []
        for n in nodes:
            if not n.get("visible"):
                continue
            x, y, w, h = n.get("bbox") or [0, 0, 0, 0]
            if viewport_only and viewport.get("w"):
                if x + w < 0 or y + h < 0 or x > viewport["w"] or y > viewport["h"]:
                    continue
            cleaned.append(
                {
                    "index": n.get("index"),
                    "tag": n.get("tag"),
                    "role": n.get("role"),
                    "text": n.get("text"),
                    "css_selector": n.get("css_selector"),
                    "xpath": n.get("xpath"),
                    "href": n.get("href"),
                    "bbox": [x, y, w, h],
                }
            )

        return VisionResponse(
            success=True,
            data={"viewport": viewport, "elements": cleaned, "count": len(cleaned)},
            method="find_clickable_elements",
        )

    # ------------------------------------------------------------------
    # 3. compare_screenshots - PIL diff
    # ------------------------------------------------------------------
    @staticmethod
    async def compare_screenshots(
        image_a_base64: str,
        image_b_base64: str,
        threshold: float = 0.05,
    ) -> VisionResponse:
        if Image is None or ImageChops is None:
            return VisionResponse(
                success=False,
                error="Pillow is required for compare_screenshots. Install with `pip install pillow`.",
                method="compare_screenshots",
            )
        try:
            img_a = _b64_to_image(image_a_base64).convert("RGB")
            img_b = _b64_to_image(image_b_base64).convert("RGB")
        except Exception as e:
            return VisionResponse(success=False, error=f"decode_failed: {e}", method="compare_screenshots")

        # Normalize sizes - resize the larger one down to the smaller's bounds.
        if img_a.size != img_b.size:
            target = (min(img_a.size[0], img_b.size[0]), min(img_a.size[1], img_b.size[1]))
            img_a = img_a.resize(target)
            img_b = img_b.resize(target)

        diff = ImageChops.difference(img_a, img_b)
        bbox = diff.getbbox()
        # Per-pixel difference percentage: any channel > 16/255 counts as changed.
        gray = diff.convert("L")
        pixels = list(gray.getdata())
        total = len(pixels) or 1
        changed = sum(1 for p in pixels if p > 16)
        diff_pct = changed / total

        regions: List[Dict[str, int]] = []
        if bbox:
            x0, y0, x1, y1 = bbox
            regions.append({"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0})

        return VisionResponse(
            success=True,
            data={
                "similar": diff_pct <= threshold,
                "diff_percentage": round(diff_pct, 6),
                "threshold": threshold,
                "diff_regions": regions,
                "size": list(img_a.size),
            },
            method="compare_screenshots",
        )

    # ------------------------------------------------------------------
    # 4. extract_text_from_image - OCR via pytesseract (lazy)
    # ------------------------------------------------------------------
    @staticmethod
    async def extract_text_from_image(image_base64: str) -> VisionResponse:
        try:
            import pytesseract  # type: ignore  # lazy on purpose
        except Exception:
            return VisionResponse(
                success=False,
                error=(
                    "pytesseract is not available. Install the Python package "
                    "(`pip install pytesseract`) AND the tesseract binary "
                    "(`brew install tesseract` on macOS, `apt install tesseract-ocr` on Debian)."
                ),
                method="extract_text_from_image",
            )
        if Image is None:
            return VisionResponse(
                success=False, error="Pillow is required.", method="extract_text_from_image"
            )

        try:
            img = _b64_to_image(image_base64)
        except Exception as e:
            return VisionResponse(success=False, error=f"decode_failed: {e}", method="extract_text_from_image")

        try:
            full_text = pytesseract.image_to_string(img)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        except Exception as e:
            return VisionResponse(success=False, error=f"ocr_failed: {e}", method="extract_text_from_image")

        blocks: List[Dict[str, Any]] = []
        n = len(data.get("text", []))
        for i in range(n):
            text = (data["text"][i] or "").strip()
            if not text:
                continue
            try:
                conf = float(data["conf"][i])
            except Exception:
                conf = -1.0
            blocks.append(
                {
                    "text": text,
                    "x": int(data["left"][i]),
                    "y": int(data["top"][i]),
                    "w": int(data["width"][i]),
                    "h": int(data["height"][i]),
                    "confidence": conf,
                }
            )

        return VisionResponse(
            success=True,
            data={"full_text": full_text.strip(), "blocks": blocks, "block_count": len(blocks)},
            method="extract_text_from_image",
        )

    # ------------------------------------------------------------------
    # 5. humanize_fingerprint - inject a deterministic anti-fp init script
    # ------------------------------------------------------------------
    @staticmethod
    async def humanize_fingerprint(
        session_id: str,
        locale: Optional[str] = None,
        timezone: Optional[str] = None,
        screen_width: Optional[int] = None,
        screen_height: Optional[int] = None,
        lock_canvas: bool = True,
    ) -> VisionResponse:
        applied: List[str] = []
        skipped: List[str] = []

        try:
            page = await _resolve_page(session_id)
        except Exception as e:
            return VisionResponse(success=False, error=f"session_not_found: {e}", method="humanize_fingerprint")

        # Build the languages list the script will install.
        if locale:
            primary = locale
            base = locale.split("-")[0]
            langs = [primary] if primary == base else [primary, base]
        else:
            langs = ["en-US", "en"]

        # Compute timezone offset in minutes (JS getTimezoneOffset convention:
        # positive = west of UTC). We keep this rough - exact DST handling
        # would need zoneinfo; close enough for fingerprint blending.
        tz_offset: Optional[int] = None
        if timezone:
            try:
                from datetime import datetime
                from zoneinfo import ZoneInfo  # py>=3.9

                now = datetime.now(ZoneInfo(timezone))
                offset = now.utcoffset()
                if offset is not None:
                    tz_offset = -int(offset.total_seconds() // 60)
                applied.append(f"timezone={timezone}")
            except Exception:
                skipped.append(f"timezone={timezone} (zoneinfo unavailable)")

        seed = _seed_from_session(session_id)
        script = (
            _FINGERPRINT_TEMPLATE
            .replace("SEED_PLACEHOLDER", str(seed))
            .replace("CANVAS_LOCK_PLACEHOLDER", "true" if lock_canvas else "false")
            .replace("LANGS_PLACEHOLDER", repr(langs).replace("'", '"'))
            .replace("TZ_OFFSET_PLACEHOLDER", "null" if tz_offset is None else str(tz_offset))
            .replace("SCREEN_W_PLACEHOLDER", "null" if screen_width is None else str(int(screen_width)))
            .replace("SCREEN_H_PLACEHOLDER", "null" if screen_height is None else str(int(screen_height)))
        )

        injected = False
        # Try the page-level API first, fall back to the browser context.
        for target in (page, getattr(page, "context", None)):
            if target is None:
                continue
            adder = getattr(target, "add_init_script", None)
            if adder is None:
                continue
            try:
                result = adder(script=script)
                if hasattr(result, "__await__"):
                    await result
                injected = True
                break
            except TypeError:
                # Some bindings expect a positional arg.
                try:
                    result = adder(script)
                    if hasattr(result, "__await__"):
                        await result
                    injected = True
                    break
                except Exception as e:
                    skipped.append(f"add_init_script: {e}")
            except Exception as e:
                skipped.append(f"add_init_script: {e}")

        if injected:
            applied.append("canvas" if lock_canvas else "canvas_skipped")
            applied.extend(["webgl", "audio", "languages"])
            if screen_width is not None:
                applied.append(f"screen_width={screen_width}")
            if screen_height is not None:
                applied.append(f"screen_height={screen_height}")
        else:
            skipped.append("init_script_not_supported_by_page")

        # Also try to set the locale + Accept-Language header on the context
        # itself - this is what most anti-bot vendors actually look at.
        ctx = getattr(page, "context", None)
        if ctx is not None and locale is not None:
            try:
                set_extra = getattr(ctx, "set_extra_http_headers", None)
                if set_extra is not None:
                    res = set_extra({"Accept-Language": f"{locale},{locale.split('-')[0]};q=0.9"})
                    if hasattr(res, "__await__"):
                        await res
                    applied.append(f"accept_language={locale}")
            except Exception as e:
                skipped.append(f"accept_language: {e}")

        return VisionResponse(
            success=injected,
            data={"applied": applied, "skipped": skipped, "seed": seed},
            method="humanize_fingerprint",
        )

    # ------------------------------------------------------------------
    # 6. align_with_proxy - country -> tz/locale -> humanize_fingerprint
    # ------------------------------------------------------------------
    @staticmethod
    async def align_with_proxy(
        session_id: str,
        proxy_country: Optional[str] = None,
    ) -> VisionResponse:
        if not proxy_country:
            return VisionResponse(
                success=False,
                error="proxy_country (ISO-2) is required.",
                method="align_with_proxy",
            )
        cc = proxy_country.upper()
        profile = _COUNTRY_PROFILES.get(cc)
        if profile is None:
            return VisionResponse(
                success=False,
                error=f"unknown_country={cc}; supported: {sorted(_COUNTRY_PROFILES.keys())}",
                method="align_with_proxy",
            )

        humanize_result = await VisionMCPTools.humanize_fingerprint(
            session_id=session_id,
            locale=profile["locale"],
            timezone=profile["timezone"],
            lock_canvas=True,
        )

        return VisionResponse(
            success=humanize_result.success,
            data={
                "country": cc,
                "profile": profile,
                "humanize": humanize_result.data,
            },
            error=humanize_result.error,
            method="align_with_proxy",
        )

    # ------------------------------------------------------------------
    # 7. detect_protection - keyword fingerprint of HTML / headers
    # ------------------------------------------------------------------
    @staticmethod
    async def detect_protection(session_id_or_url: str) -> VisionResponse:
        html: str = ""
        headers: Dict[str, str] = {}
        source: str = ""

        looks_like_url = re.match(r"^https?://", session_id_or_url, re.I) is not None

        if looks_like_url:
            try:
                # stealthy_fetch is the safest default for a probe - it survives
                # a Cloudflare splash without solving anything.
                from scrapling.fetchers import StealthyFetcher  # local import

                page = await StealthyFetcher.async_fetch(session_id_or_url, headless=True, network_idle=False)
                html = getattr(page, "html_content", "") or getattr(page, "body", "") or ""
                raw_headers = getattr(page, "headers", {}) or {}
                headers = {str(k).lower(): str(v) for k, v in dict(raw_headers).items()}
                source = "stealthy_fetch"
            except Exception as e:
                return VisionResponse(success=False, error=f"fetch_failed: {e}", method="detect_protection")
        else:
            try:
                page = await _resolve_page(session_id_or_url)
                html = await page.content()
                source = "live_session"
            except Exception as e:
                return VisionResponse(success=False, error=f"session_not_found: {e}", method="detect_protection")

        haystack = html + "\n" + "\n".join(f"{k}: {v}" for k, v in headers.items())

        hits: List[Dict[str, Any]] = []
        weight_total = 0
        for pattern, label, weight in _PROTECTION_SIGNATURES:
            if pattern.search(haystack):
                hits.append({"name": label, "weight": weight})
                weight_total += weight

        if weight_total == 0:
            severity = "low"
        elif weight_total <= 2:
            severity = "medium"
        else:
            severity = "high"

        if severity == "high":
            recommended = "stealthy_fetch"
        elif severity == "medium":
            recommended = "fetch"
        else:
            recommended = "get"

        return VisionResponse(
            success=True,
            data={
                "source": source,
                "protections": hits,
                "severity": severity,
                "recommended_tier": recommended,
                "header_count": len(headers),
            },
            method="detect_protection",
        )

    # ------------------------------------------------------------------
    # 8. auto_solve_captcha - detect + report (real solving deferred)
    # ------------------------------------------------------------------
    @staticmethod
    async def auto_solve_captcha(
        session_id: str,
        captcha_type: str = "auto",
    ) -> VisionResponse:
        try:
            page = await _resolve_page(session_id)
        except Exception as e:
            return VisionResponse(success=False, error=f"session_not_found: {e}", method="auto_solve_captcha")

        # Probe for the most common captcha containers.
        detection_js = r"""
        () => {
          const hits = [];
          const probe = (sel, kind) => {
            for (const el of document.querySelectorAll(sel)) {
              const r = el.getBoundingClientRect();
              hits.push({kind, selector: sel, x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)});
            }
          };
          probe('iframe[src*="recaptcha"]', 'recaptcha_v2');
          probe('div.g-recaptcha, div[data-sitekey][class*="recaptcha"]', 'recaptcha_v2');
          probe('iframe[src*="hcaptcha"]', 'hcaptcha');
          probe('div.h-captcha, div[data-hcaptcha-widget-id]', 'hcaptcha');
          probe('iframe[src*="challenges.cloudflare.com/turnstile"]', 'turnstile');
          probe('div.cf-turnstile, div[data-sitekey][class*="turnstile"]', 'turnstile');
          probe('img[src*="captcha"], img[alt*="captcha" i]', 'image');
          return hits;
        }
        """
        try:
            hits: List[Dict[str, Any]] = await page.evaluate(detection_js)
        except Exception as e:
            return VisionResponse(success=False, error=f"detection_failed: {e}", method="auto_solve_captcha")

        if not hits:
            return VisionResponse(
                success=True,
                data={"detected": [], "action": "none", "message": "No captcha widgets detected on page."},
                method="auto_solve_captcha",
            )

        kinds_present = {h["kind"] for h in hits}
        target = captcha_type.lower()
        if target == "auto":
            # Pick the highest-priority kind found.
            for candidate in ("turnstile", "recaptcha_v2", "hcaptcha", "image"):
                if candidate in kinds_present:
                    target = candidate
                    break

        # Turnstile: in stealthy sessions we delegate to the engine's own
        # solver, so here we just verify whether the challenge token has
        # already been issued.
        if target == "turnstile":
            try:
                token = await page.evaluate(
                    "() => { const t = document.querySelector('input[name=\"cf-turnstile-response\"]'); return t ? t.value : ''; }"
                )
            except Exception:
                token = ""
            if token:
                return VisionResponse(
                    success=True,
                    data={"detected": hits, "action": "already_solved", "kind": "turnstile"},
                    method="auto_solve_captcha",
                )
            return VisionResponse(
                success=False,
                data={
                    "detected": hits,
                    "kind": "turnstile",
                    "action": "needs_stealthy_session",
                    "hint": (
                        "Use a StealthyFetcher session - its built-in solve_cloudflare "
                        "path handles Turnstile. This tool only detects."
                    ),
                },
                method="auto_solve_captcha",
            )

        # All other kinds: report and point the user at a solver service.
        return VisionResponse(
            success=False,
            data={
                "detected": hits,
                "kind": target,
                "action": "not_implemented",
                "hint": (
                    "Plug a solver such as 2captcha or capsolver via their API key. "
                    "This tool currently reports captchas; a future hook will dispatch "
                    "to the configured solver."
                ),
            },
            method="auto_solve_captcha",
        )


__all__ = ["VisionMCPTools", "VisionResponse"]
