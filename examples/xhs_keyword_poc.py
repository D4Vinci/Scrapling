#!/usr/bin/env python3
"""Minimal runnable PoC for Xiaohongshu keyword extraction with Scrapling.

Usage:
  python examples/xhs_keyword_poc.py --keyword 穿搭 --max-notes 10 --output xhs_notes.json

Notes:
- This PoC uses browser rendering (StealthySession) which is the recommended approach
  for dynamic/anti-bot pages in Scrapling docs.
- You should provide valid cookies if anonymous traffic is blocked.
- Selectors/endpoints may change at any time.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

from scrapling.fetchers import StealthySession

SEARCH_API_HINT = "/api/sns/web/v1/search/notes"
NOTE_API_HINTS = (
    "/api/sns/web/v1/feed",
    "/api/sns/web/v1/note",
    "/api/sns/web/v1/comment/page",
)


@dataclass
class XHSNote:
    note_id: str
    url: str
    title: str = ""
    author_name: str = ""
    author_id: str = ""
    author_avatar: str = ""
    content: str = ""
    first_image: str = ""
    likes: int = 0
    collects: int = 0
    comments: int = 0
    shares: int = 0


def to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().replace(",", "")
    m = re.search(r"\d+", text)
    return int(m.group()) if m else default


def parse_cookie_header(cookie_header: str) -> List[Dict[str, str]]:
    cookies: List[Dict[str, str]] = []
    for pair in cookie_header.split(";"):
        if "=" not in pair:
            continue
        name, val = pair.split("=", 1)
        name, val = name.strip(), val.strip()
        if name:
            cookies.append({"name": name, "value": val, "domain": ".xiaohongshu.com", "path": "/"})
    return cookies


def pick(d: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in d and d[key] not in (None, ""):
            return d[key]
    return None


def flatten_search_notes(payloads: Iterable[Dict[str, Any]]) -> Dict[str, XHSNote]:
    notes: Dict[str, XHSNote] = {}
    for payload in payloads:
        data = payload.get("data") or payload
        items = data.get("items") or data.get("note_list") or []
        for item in items:
            note = item.get("note_card") or item.get("note") or item
            note_id = str(pick(note, "note_id", "id") or "").strip()
            if not note_id:
                continue

            user = note.get("user") or note.get("author") or {}
            interact = note.get("interact_info") or note.get("interaction") or {}

            title = str(pick(note, "display_title", "title", "name") or "").strip()
            author_name = str(pick(user, "nickname", "name", "user_name") or "").strip()
            author_id = str(pick(user, "user_id", "id") or "").strip()
            author_avatar = str(pick(user, "avatar", "image", "avatar_url") or "").strip()

            model = notes.get(note_id) or XHSNote(note_id=note_id, url=f"https://www.xiaohongshu.com/explore/{note_id}")
            if title:
                model.title = title
            if author_name:
                model.author_name = author_name
            if author_id:
                model.author_id = author_id
            if author_avatar:
                model.author_avatar = author_avatar
            model.likes = max(model.likes, to_int(pick(interact, "liked_count", "likes", "like_count")))
            model.collects = max(model.collects, to_int(pick(interact, "collected_count", "collects", "collect_count")))
            model.comments = max(model.comments, to_int(pick(interact, "comment_count", "comments")))
            model.shares = max(model.shares, to_int(pick(interact, "share_count", "shares", "forward_count")))
            notes[note_id] = model
    return notes


def search_note_ids(session: StealthySession, keyword: str, max_notes: int = 20, scroll_rounds: int = 4) -> Dict[str, XHSNote]:
    url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&source=web_explore_feed"
    captured_payloads: List[Dict[str, Any]] = []

    def page_action(page):
        def on_response(resp):
            try:
                if SEARCH_API_HINT in resp.url:
                    captured_payloads.append(resp.json())
            except Exception:
                return

        page.on("response", on_response)
        page.wait_for_timeout(2500)
        for _ in range(scroll_rounds):
            page.mouse.wheel(0, 2800)
            page.wait_for_timeout(1500)

    session.fetch(
        url,
        headless=True,
        network_idle=True,
        timeout=90_000,
        wait_selector="section, .note-item, #global",
        wait_selector_state="attached",
        page_action=page_action,
    )

    notes = flatten_search_notes(captured_payloads)
    if len(notes) > max_notes:
        notes = dict(list(notes.items())[:max_notes])
    return notes


def parse_note_detail_payload(payload: Dict[str, Any], model: XHSNote) -> None:
    data = payload.get("data") or payload
    # Try common container fields from different versions.
    candidates = [
        data,
        data.get("item") if isinstance(data, dict) else None,
        data.get("note") if isinstance(data, dict) else None,
        data.get("note_card") if isinstance(data, dict) else None,
    ]
    note = next((x for x in candidates if isinstance(x, dict) and x), None)
    if not note:
        return

    user = note.get("user") or note.get("author") or {}
    interact = note.get("interact_info") or note.get("interaction") or {}

    model.title = str(pick(note, "title", "display_title") or model.title)
    model.content = str(pick(note, "desc", "content", "description") or model.content)
    model.author_name = str(pick(user, "nickname", "name") or model.author_name)
    model.author_id = str(pick(user, "user_id", "id") or model.author_id)
    model.author_avatar = str(pick(user, "avatar", "image", "avatar_url") or model.author_avatar)

    model.likes = max(model.likes, to_int(pick(interact, "liked_count", "likes", "like_count")))
    model.collects = max(model.collects, to_int(pick(interact, "collected_count", "collects", "collect_count")))
    model.comments = max(model.comments, to_int(pick(interact, "comment_count", "comments")))
    model.shares = max(model.shares, to_int(pick(interact, "share_count", "shares", "forward_count")))

    image_list = note.get("image_list") or note.get("images") or []
    if image_list and not model.first_image:
        first = image_list[0]
        if isinstance(first, dict):
            model.first_image = str(
                pick(
                    first,
                    "url_default",
                    "url",
                    "image_url",
                    "master_url",
                )
                or ""
            )


def enrich_note_detail(session: StealthySession, model: XHSNote) -> None:
    captured: List[Dict[str, Any]] = []

    def page_action(page):
        def on_response(resp):
            try:
                if any(hint in resp.url for hint in NOTE_API_HINTS):
                    content_type = (resp.headers or {}).get("content-type", "")
                    if "application/json" in content_type.lower() or "api/" in resp.url:
                        captured.append(resp.json())
            except Exception:
                return

        page.on("response", on_response)
        page.wait_for_timeout(3500)

    response = session.fetch(
        model.url,
        headless=True,
        network_idle=True,
        timeout=90_000,
        wait_selector="body",
        wait_selector_state="attached",
        page_action=page_action,
    )

    for payload in captured:
        parse_note_detail_payload(payload, model)

    # Fallback from DOM when API response not captured.
    if not model.content:
        content_nodes = response.css(".note-content, .desc, .content, article")
        if content_nodes:
            model.content = str(content_nodes[0].get_all_text(strip=True))
    if not model.title:
        title = response.css("h1::text, .title::text").get()
        if title:
            model.title = str(title).strip()
    if not model.first_image:
        img = response.css("article img, .note-content img, img")
        if img:
            first = img[0].attrib.get("src") or img[0].attrib.get("data-src") or ""
            model.first_image = str(first)


def run(keyword: str, max_notes: int, cookie_header: str = "") -> List[XHSNote]:
    session_kwargs: Dict[str, Any] = {
        "headless": True,
        "disable_resources": False,
        "solve_cloudflare": False,
        "google_search": False,
        "timeout": 90_000,
    }

    if cookie_header.strip():
        session_kwargs["cookies"] = parse_cookie_header(cookie_header)

    with StealthySession(**session_kwargs) as session:
        notes_map = search_note_ids(session, keyword=keyword, max_notes=max_notes)
        for note in notes_map.values():
            try:
                enrich_note_detail(session, note)
            except Exception:
                continue
        return list(notes_map.values())


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Xiaohongshu keyword scraping PoC based on Scrapling")
    parser.add_argument("--keyword", required=True, help="Search keyword")
    parser.add_argument("--max-notes", type=int, default=10, help="Maximum notes to extract")
    parser.add_argument("--cookie", default="", help="Raw cookie header string from logged-in browser")
    parser.add_argument("--output", default="xhs_notes.json", help="Output JSON file path")
    return parser


def main() -> None:
    args = build_cli().parse_args()
    start = time.time()
    results = run(keyword=args.keyword, max_notes=args.max_notes, cookie_header=args.cookie)

    payload = {
        "keyword": args.keyword,
        "count": len(results),
        "elapsed_sec": round(time.time() - start, 2),
        "items": [asdict(item) for item in results],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} notes to {args.output}")


if __name__ == "__main__":
    main()
