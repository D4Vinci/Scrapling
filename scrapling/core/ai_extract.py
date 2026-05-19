"""Schema-driven heuristic extraction and self-healing selectors for Scrapling MCP.

This module provides pure-heuristic (no LLM) tools to:
  * Extract data shaped to a JSON-Schema-like dict from arbitrary HTML
  * Recover from broken CSS selectors by ranking candidate replacements
  * Categorize links by destination type
  * Pull structured metadata (JSON-LD, microdata, Open Graph, Twitter Card)

Example::

    from scrapling.core.ai_extract import ExtractMCPTools

    html = "<html>...</html>"
    schema = {"posts": [{"title": "string", "url": "string", "date": "string"}]}
    out = ExtractMCPTools.smart_extract(html, schema)
    # out.success, out.data, out.method_used

    healed = ExtractMCPTools.self_healing_selector(
        html, broken_selector="div.product-title", last_known_text="Wireless Mouse"
    )
    # healed.data -> [{"selector": "...", "confidence": 0.93, "sample_text": "..."}, ...]
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from html import unescape
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from lxml import etree, html as lxml_html
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pydantic response model
# ---------------------------------------------------------------------------
class ExtractResponse(BaseModel):
    """Uniform response envelope for every tool in this module."""

    success: bool = Field(description="Whether extraction produced usable output.")
    data: Optional[Any] = Field(default=None, description="Extracted payload, shape depends on tool.")
    selector_hints: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Candidate selectors / fragments to feed back to an LLM when heuristics fail.",
    )
    error: Optional[str] = Field(default=None, description="Human readable failure reason.")
    method_used: Optional[str] = Field(
        default=None,
        description='One of "json-ld" / "heuristic" / "repeating-pattern" / "fallback-text" / etc.',
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_BLOCK_TAGS = {
    "article",
    "section",
    "li",
    "tr",
    "div",
    "main",
    "aside",
    "header",
    "footer",
    "nav",
    "p",
}
_FIELD_HINTS = {
    "title": (("h1", "h2", "h3", "h4"), ("title", "headline", "name", "heading")),
    "name": (("h1", "h2", "h3"), ("name", "title", "headline")),
    "headline": (("h1", "h2", "h3"), ("headline", "title")),
    "author": (("a", "span", "p", "div"), ("author", "byline", "writer", "creator")),
    "date": (("time", "span", "p", "div"), ("date", "time", "published", "posted")),
    "time": (("time",), ("time", "date", "published")),
    "published": (("time", "span"), ("date", "published", "posted")),
    "url": (("a",), ("link", "url", "permalink")),
    "link": (("a",), ("link", "url")),
    "image": (("img",), ("image", "thumb", "photo", "picture", "cover")),
    "thumbnail": (("img",), ("thumb", "image", "preview")),
    "price": (("span", "p", "div"), ("price", "amount", "cost")),
    "description": (("p", "div", "span"), ("description", "summary", "excerpt", "desc")),
    "summary": (("p", "div", "span"), ("summary", "excerpt", "abstract")),
    "rating": (("span", "div"), ("rating", "stars", "score")),
    "category": (("a", "span"), ("category", "tag", "topic", "section")),
    "tag": (("a", "span"), ("tag", "label", "category")),
    "content": (("div", "article", "section", "p"), ("content", "body", "article")),
    "text": (("p", "div", "span", "article"), ("text", "body", "content", "message")),
    "body": (("p", "div", "article"), ("body", "content", "text", "message")),
    "excerpt": (("p", "div", "span"), ("excerpt", "summary", "description", "abstract")),
    "message": (("p", "div", "span"), ("message", "text", "body", "comment")),
    "comment": (("p", "div", "span"), ("comment", "message", "body", "text")),
    "id": ((), ("id",)),
}
_DOC_EXTS = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "zip", "rar", "7z", "tar", "gz", "csv", "txt"}
_IMG_EXTS = {"jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico", "avif", "tiff"}
_VID_EXTS = {"mp4", "webm", "mov", "avi", "mkv", "m4v", "flv", "wmv"}
_SOCIAL_HOSTS = {
    "twitter.com",
    "x.com",
    "facebook.com",
    "fb.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "reddit.com",
    "pinterest.com",
    "github.com",
    "discord.gg",
    "discord.com",
    "t.me",
    "telegram.org",
    "weibo.com",
    "mastodon.social",
}


def _parse_html(html: str) -> Optional[lxml_html.HtmlElement]:
    if not html or not isinstance(html, str):
        return None
    try:
        # lxml is robust against malformed HTML; wrap in fragments_fromstring fallback
        return lxml_html.fromstring(html)
    except (etree.XMLSyntaxError, etree.ParserError, ValueError):
        try:
            doc = lxml_html.fragment_fromstring(html, create_parent="div")
            return doc
        except Exception:
            return None


def _text_of(el) -> str:
    if el is None:
        return ""
    try:
        return re.sub(r"\s+", " ", el.text_content()).strip()
    except Exception:
        return ""


def _classes(el) -> List[str]:
    if el is None or not hasattr(el, "get"):
        return []
    raw = el.get("class") or ""
    return [c for c in raw.split() if c]


def _signature(el) -> Tuple[str, Tuple[str, ...]]:
    """A stable tag+sorted-class signature for grouping siblings."""
    return (el.tag if isinstance(el.tag, str) else "?", tuple(sorted(_classes(el))))


def _tree_path(el) -> str:
    """Build a CSS selector path that uniquely targets `el`."""
    parts: List[str] = []
    cur = el
    while cur is not None and getattr(cur, "tag", None) and isinstance(cur.tag, str):
        seg = cur.tag
        eid = cur.get("id") if hasattr(cur, "get") else None
        if eid:
            seg += f"#{eid}"
            parts.append(seg)
            break
        cls = _classes(cur)
        if cls:
            seg += "." + ".".join(cls[:2])
        parent = cur.getparent()
        if parent is not None:
            same = [c for c in parent if getattr(c, "tag", None) == cur.tag]
            if len(same) > 1:
                seg += f":nth-of-type({same.index(cur) + 1})"
        parts.append(seg)
        cur = parent
    return " > ".join(reversed(parts)) or "*"


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]


def _class_similarity(a: List[str], b: List[str]) -> float:
    if not a and not b:
        return 1.0
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    jacc = inter / union if union else 0.0
    # token-level fuzzy boost
    fuzzy = 0.0
    for ta in sa:
        best = max((1 - _levenshtein(ta, tb) / max(len(ta), len(tb), 1) for tb in sb), default=0.0)
        fuzzy += best
    fuzzy = fuzzy / max(len(sa), 1)
    return 0.6 * jacc + 0.4 * fuzzy


# ---------------------------------------------------------------------------
# SchemaExtractor: heart of smart_extract
# ---------------------------------------------------------------------------
class SchemaExtractor:
    """Heuristic schema-driven HTML to dict extractor.

    Strategy order per top-level field:
      1. JSON-LD with matching @type / property name
      2. Repeating sibling pattern (lists / cards / table rows)
      3. Microdata / Open Graph / direct semantic tag match
      4. Readability-style main content fallback
    """

    def __init__(self, root: lxml_html.HtmlElement, base_url: str = "", max_items: int = 50):
        self.root = root
        self.base_url = base_url or ""
        self.max_items = max(1, int(max_items))
        self._jsonld: Optional[List[dict]] = None

    # -- public entry --------------------------------------------------------
    def extract(self, schema: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Return (data, methods_used) for top-level schema."""
        out: Dict[str, Any] = {}
        methods: List[str] = []
        for key, sub in (schema or {}).items():
            value, method = self._extract_field(self.root, key, sub)
            out[key] = value
            if method and method not in methods:
                methods.append(method)
        return out, methods

    def _extract_field(self, scope, key: str, sub: Any) -> Tuple[Any, str]:
        if isinstance(sub, list) and sub:
            item_schema = sub[0]
            items = self._extract_repeating_pattern(scope, item_schema, hint=key)
            return items, "repeating-pattern"
        if isinstance(sub, dict):
            inner: Dict[str, Any] = {}
            method = "heuristic"
            for k, v in sub.items():
                val, m = self._extract_field(scope, k, v)
                inner[k] = val
                method = m
            return inner, method
        # leaf scalar field
        val = self._extract_scalar(scope, key, sub)
        return val, "heuristic"

    # -- repeating pattern ---------------------------------------------------
    def _extract_repeating_pattern(self, scope, item_schema: Any, hint: str = "") -> List[Dict[str, Any]]:
        """Find sibling groups with the same (tag, classes) signature and project schema."""
        if scope is None:
            return []

        groups = self._find_repeating_groups(scope, hint=hint)
        for parent, children, _score in groups:
            items: List[Dict[str, Any]] = []
            for child in children[: self.max_items]:
                if isinstance(item_schema, dict):
                    obj: Dict[str, Any] = {}
                    for fk, fv in item_schema.items():
                        if isinstance(fv, list) and fv:
                            obj[fk] = self._extract_repeating_pattern(child, fv[0], hint=fk)
                        elif isinstance(fv, dict):
                            obj[fk] = {k: self._extract_scalar(child, k, v) for k, v in fv.items()}
                        else:
                            obj[fk] = self._extract_scalar(child, fk, fv)
                    if any(v not in (None, "", [], {}) for v in obj.values()):
                        items.append(obj)
                else:
                    txt = _text_of(child)
                    if txt:
                        items.append(txt)
            if items:
                return items
        return []

    def _find_repeating_groups(self, scope, hint: str = "") -> List[Tuple[Any, List[Any], float]]:
        """Scan descendants, group siblings by signature, rank by size and tag preference."""
        ranked: List[Tuple[Any, List[Any], float]] = []
        for parent in scope.iter():
            if not isinstance(parent.tag, str):
                continue
            buckets: Dict[Tuple[str, Tuple[str, ...]], List[Any]] = defaultdict(list)
            for child in parent:
                if not isinstance(getattr(child, "tag", None), str):
                    continue
                buckets[_signature(child)].append(child)
            for sig, kids in buckets.items():
                if len(kids) < 2:
                    continue
                tag = sig[0]
                cls = sig[1]
                score = float(len(kids))
                if tag in ("article", "li", "tr"):
                    score *= 1.6
                elif tag in ("div", "section"):
                    score *= 1.1
                if hint:
                    h = hint.lower().rstrip("s")
                    if any(h in c.lower() for c in cls):
                        score *= 1.5
                # prefer groups with substantive text and links
                tot_text = sum(len(_text_of(k)) for k in kids)
                if tot_text < 20 * len(kids):
                    score *= 0.4
                ranked.append((parent, kids, score))
        ranked.sort(key=lambda t: t[2], reverse=True)
        return ranked[:8]

    # -- scalar field --------------------------------------------------------
    def _extract_scalar(self, scope, key: str, type_hint: Any) -> Optional[str]:
        if scope is None:
            return None
        k = key.lower()

        # 1. itemprop
        try:
            m = scope.xpath(f'.//*[@itemprop="{key}"]')
            if m:
                return self._element_value(m[0], k)
        except Exception:
            pass

        # 2. Open Graph / meta (only for root scope, since meta tags live in <head>)
        og = self._meta_lookup(scope, k)
        if og:
            return og

        # 3. tag + class hints
        tags, words = _FIELD_HINTS.get(k, ((), (k,)))
        candidates: List[Tuple[float, Any]] = []
        for el in scope.iter():
            if not isinstance(getattr(el, "tag", None), str):
                continue
            score = 0.0
            tag = el.tag
            if tags and tag in tags:
                score += 2.0
            cls = _classes(el)
            attr_blob = " ".join([el.get("id") or "", " ".join(cls), el.get("name") or "", el.get("rel") or ""]).lower()
            for w in words:
                if w and w in attr_blob:
                    score += 1.5
            if k in ("url", "link") and tag == "a" and el.get("href"):
                score += 2.0
            if k in ("image", "thumbnail") and tag == "img" and el.get("src"):
                score += 2.0
            if k in ("date", "time", "published") and tag == "time":
                score += 2.0
            if score > 0:
                candidates.append((score, el))
        if candidates:
            candidates.sort(key=lambda t: t[0], reverse=True)
            return self._element_value(candidates[0][1], k)

        # Bug #5: when a field has no _FIELD_HINTS entry and no class/id signal,
        # fall back to the longest <p> / textNode inside the scope so generic
        # keys like "text", "body", "comment" don't silently return None.
        if scope is not self.root and k not in _FIELD_HINTS:
            best_text = ""
            for el in scope.iter():
                if not isinstance(getattr(el, "tag", None), str):
                    continue
                if el.tag in ("p", "div", "span"):
                    txt = _text_of(el)
                    if len(txt) > len(best_text):
                        best_text = txt
            if best_text:
                return best_text

        # 4. last resort: root-level direct text for trivial roots
        if scope is self.root and k in ("title",):
            t = scope.find(".//title")
            if t is not None:
                return _text_of(t)
        return None

    def _element_value(self, el, key: str) -> Optional[str]:
        if el is None:
            return None
        tag = el.tag if isinstance(el.tag, str) else ""
        if key in ("url", "link") or tag == "a":
            href = el.get("href")
            if href:
                return urljoin(self.base_url, href) if self.base_url else href
        if key in ("image", "thumbnail") or tag == "img":
            src = el.get("src") or el.get("data-src")
            if src:
                return urljoin(self.base_url, src) if self.base_url else src
        if tag == "time":
            return el.get("datetime") or _text_of(el)
        if tag == "meta":
            return el.get("content")
        return _text_of(el) or None

    def _meta_lookup(self, scope, key: str) -> Optional[str]:
        if scope is not self.root:
            return None
        keys = {key, f"og:{key}", f"twitter:{key}", f"article:{key}"}
        for meta in self.root.iter("meta"):
            prop = (meta.get("property") or meta.get("name") or "").lower()
            if prop in keys and meta.get("content"):
                return meta.get("content")
        return None

    # -- main content (readability lite) ------------------------------------
    def main_content_text(self) -> str:
        best = None
        best_score = 0.0
        for el in self.root.iter():
            if not isinstance(getattr(el, "tag", None), str):
                continue
            if el.tag not in _BLOCK_TAGS and el.tag not in ("main", "article"):
                continue
            text = _text_of(el)
            if not text:
                continue
            score = len(text) ** 0.5
            cls_id = " ".join(_classes(el)) + " " + (el.get("id") or "")
            cls_id = cls_id.lower()
            if any(w in cls_id for w in ("article", "content", "main", "post", "story", "entry")):
                score *= 1.6
            if any(w in cls_id for w in ("comment", "sidebar", "footer", "nav", "advert", "promo")):
                score *= 0.3
            if el.tag in ("article", "main"):
                score *= 1.5
            p_count = len(el.findall(".//p"))
            score += p_count * 5
            if score > best_score:
                best_score = score
                best = el
        return _text_of(best) if best is not None else _text_of(self.root)


# ---------------------------------------------------------------------------
# Structured data extractor (shared)
# ---------------------------------------------------------------------------
def _extract_jsonld(root) -> List[Any]:
    """Pull JSON-LD blobs out of a document.

    Bug #4: previously stored `{"@context": ..., "@graph": [...]}` as a single
    opaque entry, so consumers searching for `@type=Article` would miss it.
    Now we expand `@graph` into top-level entries and propagate `@context`
    onto each child (matching Google's structured-data convention).
    """

    def _push(out: List[Any], data: Any) -> None:
        if isinstance(data, list):
            for item in data:
                _push(out, item)
            return
        if isinstance(data, dict):
            if isinstance(data.get("@graph"), list):
                ctx = data.get("@context")
                for child in data["@graph"]:
                    if isinstance(child, dict) and ctx is not None and "@context" not in child:
                        child = dict(child)
                        child["@context"] = ctx
                    _push(out, child)
                return
        out.append(data)

    out: List[Any] = []
    for s in root.iter("script"):
        if (s.get("type") or "").lower() != "application/ld+json":
            continue
        raw = (s.text or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            try:
                data = json.loads(re.sub(r",\s*([\]}])", r"\1", raw))
            except Exception:
                continue
        _push(out, data)
    return out


def _extract_open_graph(root) -> Dict[str, str]:
    og: Dict[str, str] = {}
    for m in root.iter("meta"):
        prop = (m.get("property") or "").lower()
        if prop.startswith("og:") or prop.startswith("article:") or prop.startswith("product:"):
            content = m.get("content")
            if content:
                og[prop] = content
    return og


def _extract_twitter(root) -> Dict[str, str]:
    tw: Dict[str, str] = {}
    for m in root.iter("meta"):
        name = (m.get("name") or "").lower()
        if name.startswith("twitter:"):
            content = m.get("content")
            if content:
                tw[name] = content
    return tw


def _extract_microdata(root) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for el in root.xpath('//*[@itemscope]'):
        itype = el.get("itemtype")
        record: Dict[str, Any] = {"@type": itype} if itype else {}
        for prop in el.xpath('.//*[@itemprop]'):
            # skip nested itemscopes' children to avoid leakage
            ancestor = prop.getparent()
            skip = False
            while ancestor is not None and ancestor is not el:
                if ancestor.get("itemscope") is not None:
                    skip = True
                    break
                ancestor = ancestor.getparent()
            if skip:
                continue
            name = prop.get("itemprop")
            tag = prop.tag if isinstance(prop.tag, str) else ""
            if tag == "meta":
                val = prop.get("content")
            elif tag in ("a", "link", "area"):
                val = prop.get("href")
            elif tag in ("img", "audio", "video", "source", "iframe", "embed"):
                val = prop.get("src")
            elif tag == "time":
                val = prop.get("datetime") or _text_of(prop)
            else:
                val = _text_of(prop)
            if not val:
                continue
            if name in record:
                cur = record[name]
                if isinstance(cur, list):
                    cur.append(val)
                else:
                    record[name] = [cur, val]
            else:
                record[name] = val
        if record:
            items.append(record)
    return items


# ---------------------------------------------------------------------------
# Self-healing selector helpers
# ---------------------------------------------------------------------------
_SEL_TAG_RE = re.compile(r"^([a-zA-Z][\w-]*)")
_SEL_ID_RE = re.compile(r"#([\w-]+)")
_SEL_CLS_RE = re.compile(r"\.([\w-]+)")
_SEL_ATTR_RE = re.compile(r"\[([^\]=]+)(?:[~|^$*]?=\s*['\"]?([^'\"\]]*)['\"]?)?\]")


def _parse_selector(sel: str) -> Dict[str, Any]:
    """Crude CSS selector parse - extracts tag, id, classes, attrs from the last simple sel."""
    if not sel:
        return {}
    last = re.split(r"\s*[>+~ ]\s*", sel.strip())[-1] or sel
    info: Dict[str, Any] = {}
    m = _SEL_TAG_RE.match(last)
    if m:
        info["tag"] = m.group(1).lower()
    info["id"] = (_SEL_ID_RE.search(last) or [None, None])[1] if _SEL_ID_RE.search(last) else None
    info["classes"] = _SEL_CLS_RE.findall(last)
    info["attrs"] = {k.strip(): v for k, v in _SEL_ATTR_RE.findall(last)}
    return info


_ROLE_TAGS = {
    "button": {"button", "a", "input"},
    "link": {"a"},
    "input": {"input", "textarea", "select"},
    "image": {"img", "picture"},
    "heading": {"h1", "h2", "h3", "h4", "h5", "h6"},
    "list": {"ul", "ol"},
    "listitem": {"li"},
    "navigation": {"nav"},
    "form": {"form"},
}


# ---------------------------------------------------------------------------
# Link classification
# ---------------------------------------------------------------------------
def _ext_of(href: str) -> str:
    try:
        path = urlparse(href).path
        if "." in path:
            return path.rsplit(".", 1)[-1].lower()
    except Exception:
        pass
    return ""


def _is_social(host: str) -> bool:
    host = (host or "").lower()
    if not host:
        return False
    if host.startswith("www."):
        host = host[4:]
    return any(host == s or host.endswith("." + s) for s in _SOCIAL_HOSTS)


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------
class ExtractMCPTools:
    """Pure-heuristic schema extraction, link grouping, and selector self-healing.

    Example::

        from scrapling.core.ai_extract import ExtractMCPTools

        # 1. schema-driven extraction
        result = ExtractMCPTools.smart_extract(
            html,
            schema={"posts": [{"title": "string", "author": "string", "url": "string"}]},
            url="https://example.com/blog",
        )
        if result.success:
            print(result.data)             # {"posts": [...]}
            print(result.method_used)      # "repeating-pattern"
        else:
            print(result.selector_hints)   # candidate selectors for LLM follow-up

        # 2. self-healing selector
        healed = ExtractMCPTools.self_healing_selector(
            html,
            broken_selector="div.product-title.old",
            last_known_text="Wireless Mouse",
            element_role="link",
        )
        for c in healed.data:
            print(c["selector"], c["confidence"], c["sample_text"])
    """

    # ------------------------------------------------------------------ 1
    @staticmethod
    def smart_extract(
        html: str,
        schema: Dict[str, Any],
        instructions: str = "",
        url: str = "",
        max_items: int = 50,
    ) -> ExtractResponse:
        """Heuristically extract data from `html` shaped to `schema`.

        ``schema`` follows a lightweight JSON-Schema-style:
            * ``"string"`` / ``"number"`` / ``"url"`` etc. mark scalar leaves
            * a list ``[ {...} ]`` requests a repeating pattern
            * a dict requests a nested object

        Returns :class:`ExtractResponse`. On failure, ``selector_hints`` carries
        candidate selectors plus the page's main-content text so the caller can
        forward it to an LLM.
        """
        root = _parse_html(html)
        if root is None:
            return ExtractResponse(
                success=False,
                error="Failed to parse HTML (empty or invalid).",
                method_used="fallback-text",
            )
        if not isinstance(schema, dict) or not schema:
            return ExtractResponse(
                success=False,
                error="`schema` must be a non-empty dict (JSON-Schema-style).",
                method_used="fallback-text",
            )

        # 1. JSON-LD shortcut: when schema top key matches a JSON-LD @type or property.
        # Bug #1: previously returned the raw entry/payload regardless of schema shape,
        # which violated `{"key": [...]}` contracts. Now we coerce shape and expand
        # `itemListElement` / `@graph` so list schemas always receive a list.
        try:
            jsonld = _extract_jsonld(root)
        except Exception:
            jsonld = []

        def _coerce_jsonld_payload(entry: Dict[str, Any], top_key: str, want_list: bool) -> Any:
            payload = entry.get(top_key, entry) if top_key in entry else entry
            # Expand ItemList → its members.
            if isinstance(payload, dict) and isinstance(payload.get("itemListElement"), list):
                payload = payload["itemListElement"]
            # Expand @graph → its members (Google/SEO convention).
            if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
                payload = payload["@graph"]
            if want_list and not isinstance(payload, list):
                payload = [payload]
            if not want_list and isinstance(payload, list):
                payload = payload[0] if payload else {}
            return payload

        for top_key, top_val in schema.items():
            tk = top_key.lower().rstrip("s")
            want_list = isinstance(top_val, list)
            for entry in jsonld:
                if not isinstance(entry, dict):
                    continue
                etype = entry.get("@type")
                if isinstance(etype, list):
                    etypes = [str(t).lower() for t in etype]
                else:
                    etypes = [str(etype).lower()] if etype else []
                if any(tk in t for t in etypes) or top_key in entry:
                    payload = _coerce_jsonld_payload(entry, top_key, want_list)
                    return ExtractResponse(
                        success=True,
                        data={top_key: payload},
                        method_used="json-ld",
                    )

        # 2. Heuristic + repeating pattern walk
        extractor = SchemaExtractor(root, base_url=url, max_items=max_items)
        try:
            data, methods = extractor.extract(schema)
        except Exception as exc:
            data, methods = {}, []
            err = f"Heuristic extraction crashed: {exc}"
        else:
            err = None

        def _has_value(v: Any) -> bool:
            if v is None or v == "" or v == [] or v == {}:
                return False
            if isinstance(v, dict):
                return any(_has_value(x) for x in v.values())
            if isinstance(v, list):
                return any(_has_value(x) for x in v)
            return True

        if data and any(_has_value(v) for v in data.values()):
            method = "json-ld" if "json-ld" in methods else (
                "repeating-pattern" if "repeating-pattern" in methods else "heuristic"
            )
            return ExtractResponse(success=True, data=data, method_used=method)

        # 3. Fallback: emit main content + selector hints for downstream LLM
        hints: List[Dict[str, Any]] = []
        try:
            for parent, kids, score in extractor._find_repeating_groups(root)[:5]:
                sample = kids[0]
                hints.append(
                    {
                        "selector": _tree_path(sample),
                        "count": len(kids),
                        "score": round(float(score), 2),
                        "sample_text": _text_of(sample)[:200],
                    }
                )
        except Exception:
            pass
        text = ""
        try:
            text = extractor.main_content_text()
        except Exception:
            text = _text_of(root)
        return ExtractResponse(
            success=False,
            data={"main_text": text[:8000]},
            selector_hints=hints,
            error=err
            or "Heuristics could not satisfy the schema. Use `data.main_text` and `selector_hints` with an LLM.",
            method_used="fallback-text",
        )

    # ------------------------------------------------------------------ 2
    @staticmethod
    def self_healing_selector(
        html: str,
        broken_selector: str,
        last_known_text: str = "",
        element_role: str = "",
    ) -> ExtractResponse:
        """Suggest replacement selectors when ``broken_selector`` no longer matches.

        Ranking priority: exact text match > partial text match > role+attr fuzzy
        > class-set similarity. Returns up to 5 candidates with confidence in [0, 1].
        """
        root = _parse_html(html)
        if root is None:
            return ExtractResponse(success=False, error="Failed to parse HTML.")

        parsed = _parse_selector(broken_selector or "")
        target_tag = parsed.get("tag")
        target_classes = parsed.get("classes") or []
        target_id = parsed.get("id")
        target_attrs = parsed.get("attrs") or {}
        role = (element_role or "").strip().lower()
        role_tags = _ROLE_TAGS.get(role, set())
        lkt = (last_known_text or "").strip()
        lkt_low = lkt.lower()

        # Quick win: id direct match
        candidates: List[Tuple[float, Any, str]] = []  # (confidence, element, reason)

        # First pass: broken selector still resolves. Bug #2: previously
        # we awarded a flat 0.5 here without comparing against last_known_text,
        # so completely-wrong elements scored as high-confidence matches.
        # Now we use a weak baseline (0.15) and require lkt corroboration
        # before promoting; mismatched text is penalised, not rewarded.
        try:
            existing = root.cssselect(broken_selector) if broken_selector else []
        except Exception:
            existing = []
        for e in existing[:5]:
            base = 0.15
            reason_parts = ["broken-selector-resolves"]
            if lkt:
                cand_text_low = _text_of(e).lower()
                if cand_text_low == lkt_low:
                    base = 0.85
                    reason_parts.append("text-exact")
                elif lkt_low and lkt_low in cand_text_low:
                    base = 0.55
                    reason_parts.append("text-contains")
                else:
                    base = 0.05  # penalise: structurally there but text doesn't match
                    reason_parts.append("text-mismatch")
            candidates.append((base, e, ",".join(reason_parts)))

        # Iterate candidates
        for el in root.iter():
            if not isinstance(getattr(el, "tag", None), str):
                continue
            tag = el.tag
            text = _text_of(el)
            text_low = text.lower()
            score = 0.0
            reasons: List[str] = []

            # text exact / contains
            if lkt:
                if text_low == lkt_low:
                    score += 0.7
                    reasons.append("text-exact")
                elif lkt_low in text_low and len(text) <= max(60, len(lkt) * 6):
                    score += 0.45
                    reasons.append("text-contains")
                elif text_low and text_low in lkt_low:
                    score += 0.25
                    reasons.append("text-substring")

            # tag match
            if target_tag and tag == target_tag:
                score += 0.12
                reasons.append("tag-match")

            # role match
            if role_tags and tag in role_tags:
                score += 0.1
                reasons.append("role-match")

            # id match
            eid = el.get("id") or ""
            if target_id and eid == target_id:
                score += 0.25
                reasons.append("id-match")

            # class similarity
            cls_sim = _class_similarity(target_classes, _classes(el)) if target_classes else 0.0
            if cls_sim > 0:
                score += 0.25 * cls_sim
                if cls_sim > 0.5:
                    reasons.append(f"class-sim={cls_sim:.2f}")

            # attribute hints
            for ak, av in target_attrs.items():
                eav = el.get(ak)
                if eav is None:
                    continue
                if not av or av == eav:
                    score += 0.08
                    reasons.append(f"attr:{ak}")
                elif av in eav:
                    score += 0.04

            # role-tag hints from element's own attributes
            if role:
                rattr = (el.get("role") or "").lower()
                if rattr == role:
                    score += 0.12
                    reasons.append("role-attr")

            if score >= 0.2:
                candidates.append((score, el, ",".join(reasons) or "weak"))

        # de-dup by element identity, keep highest score
        seen: Dict[int, Tuple[float, Any, str]] = {}
        for c in candidates:
            key = id(c[1])
            if key not in seen or c[0] > seen[key][0]:
                seen[key] = c
        ranked = sorted(seen.values(), key=lambda t: t[0], reverse=True)[:5]

        if not ranked:
            return ExtractResponse(
                success=False,
                error="No candidate elements scored high enough to replace the broken selector.",
                data=[],
            )

        results = []
        max_score = max(r[0] for r in ranked) or 1.0
        for score, el, reason in ranked:
            conf = max(0.0, min(1.0, score / max(max_score, 1.0))) if max_score else 0.0
            # ensure confidence reflects absolute strength too
            conf = min(1.0, 0.5 * conf + 0.5 * min(1.0, score))
            results.append(
                {
                    "selector": _tree_path(el),
                    "confidence": round(conf, 3),
                    "sample_text": _text_of(el)[:200],
                    "tag": el.tag if isinstance(el.tag, str) else None,
                    "reason": reason,
                }
            )
        return ExtractResponse(success=True, data=results, method_used="heuristic")

    # ------------------------------------------------------------------ 3
    @staticmethod
    def extract_links(
        html: str,
        url: str = "",
        same_domain_only: bool = False,
        types: Optional[List[str]] = None,
    ) -> ExtractResponse:
        """Group links found in HTML into images / videos / docs / external_pages /
        internal_pages / social. ``url`` resolves relative hrefs and decides the
        internal/external split."""
        root = _parse_html(html)
        if root is None:
            return ExtractResponse(success=False, error="Failed to parse HTML.")

        # Bug #3: respect document-level <base href>; the HTML spec says relative
        # URLs resolve against <base> first, falling back to the request URL.
        base_el = root.find(".//base[@href]")
        doc_base = (base_el.get("href") if base_el is not None else "") or ""
        if doc_base and url:
            base = urljoin(url, doc_base)
        else:
            base = doc_base or url or ""
        base_host = urlparse(base).netloc.lower() if base else ""
        wanted = set(types) if types else None

        buckets: Dict[str, List[Dict[str, str]]] = {
            "images": [],
            "videos": [],
            "docs": [],
            "external_pages": [],
            "internal_pages": [],
            "social": [],
        }
        seen: Dict[str, str] = {}

        def _push(kind: str, href: str, text: str = "", el_tag: str = ""):
            if wanted is not None and kind not in wanted:
                return
            if not href or href.startswith(("javascript:", "#", "mailto:", "tel:", "data:")):
                return
            absolute = urljoin(base, href) if base else href
            host = urlparse(absolute).netloc.lower()
            if same_domain_only and base_host and host and host != base_host:
                return
            key = f"{kind}:{absolute}"
            if key in seen:
                return
            seen[key] = absolute
            buckets[kind].append({"url": absolute, "text": text[:200], "host": host, "tag": el_tag})

        # <a href>
        for a in root.iter("a"):
            href = unescape(a.get("href") or "")
            if not href:
                continue
            text = _text_of(a)
            ext = _ext_of(href)
            host = urlparse(urljoin(base, href)).netloc.lower() if base else urlparse(href).netloc.lower()
            if ext in _IMG_EXTS:
                _push("images", href, text, "a")
            elif ext in _VID_EXTS:
                _push("videos", href, text, "a")
            elif ext in _DOC_EXTS:
                _push("docs", href, text, "a")
            elif _is_social(host):
                _push("social", href, text, "a")
            elif base_host and host and host != base_host:
                _push("external_pages", href, text, "a")
            elif host == base_host or not base_host:
                _push("internal_pages", href, text, "a")
            else:
                _push("external_pages", href, text, "a")

        # <img>
        for img in root.iter("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                _push("images", src, img.get("alt") or "", "img")
        # <source srcset>
        for src_el in root.iter("source"):
            srcset = src_el.get("srcset") or src_el.get("src")
            if not srcset:
                continue
            for piece in srcset.split(","):
                u = piece.strip().split(" ")[0]
                if u:
                    _push("images", u, "", "source")
        # <video>, <iframe> (youtube etc.)
        for v in root.iter("video"):
            src = v.get("src")
            if src:
                _push("videos", src, "", "video")
        for ifr in root.iter("iframe"):
            src = ifr.get("src") or ""
            if not src:
                continue
            host = urlparse(urljoin(base, src)).netloc.lower() if base else urlparse(src).netloc.lower()
            if any(s in host for s in ("youtube", "vimeo", "youtu.be", "dailymotion", "bilibili")):
                _push("videos", src, ifr.get("title") or "", "iframe")
            elif _is_social(host):
                _push("social", src, ifr.get("title") or "", "iframe")

        return ExtractResponse(
            success=True,
            data=buckets,
            method_used="heuristic",
        )

    # ------------------------------------------------------------------ 4
    @staticmethod
    def extract_structured_data(html: str) -> ExtractResponse:
        """Extract and merge JSON-LD, microdata, Open Graph and Twitter Card metadata."""
        root = _parse_html(html)
        if root is None:
            return ExtractResponse(success=False, error="Failed to parse HTML.")

        try:
            jsonld = _extract_jsonld(root)
        except Exception:
            jsonld = []
        try:
            og = _extract_open_graph(root)
        except Exception:
            og = {}
        try:
            tw = _extract_twitter(root)
        except Exception:
            tw = {}
        try:
            micro = _extract_microdata(root)
        except Exception:
            micro = []

        # canonical fields (merged for convenience)
        merged: Dict[str, Any] = {}
        title = root.find(".//title")
        if title is not None:
            merged["title"] = _text_of(title)
        if og.get("og:title"):
            merged["title"] = og["og:title"]
        if tw.get("twitter:title"):
            merged.setdefault("title", tw["twitter:title"])
        if og.get("og:description"):
            merged["description"] = og["og:description"]
        if tw.get("twitter:description"):
            merged.setdefault("description", tw["twitter:description"])
        if og.get("og:image"):
            merged["image"] = og["og:image"]
        if tw.get("twitter:image"):
            merged.setdefault("image", tw["twitter:image"])
        if og.get("og:url"):
            merged["url"] = og["og:url"]
        if og.get("og:type"):
            merged["type"] = og["og:type"]
        if og.get("og:site_name"):
            merged["site_name"] = og["og:site_name"]

        # opportunistic enrichment from JSON-LD
        for entry in jsonld:
            if isinstance(entry, dict):
                for k in ("name", "headline", "description", "datePublished", "author", "image"):
                    if k in entry and k not in merged:
                        merged[k] = entry[k]

        any_found = bool(jsonld or og or tw or micro or merged)
        return ExtractResponse(
            success=any_found,
            data={
                "merged": merged,
                "json_ld": jsonld,
                "microdata": micro,
                "open_graph": og,
                "twitter": tw,
            },
            method_used="json-ld" if jsonld else "heuristic",
            error=None if any_found else "No structured data detected.",
        )


__all__ = ["ExtractMCPTools", "ExtractResponse", "SchemaExtractor"]
