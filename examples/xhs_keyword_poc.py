#!/usr/bin/env python3
"""Minimal runnable PoC for Xiaohongshu keyword extraction with Scrapling.

Usage examples:
  # 1) Render mode (recommended for dynamic pages)
  PYTHONPATH=. python examples/xhs_keyword_poc.py \
    --mode render --keyword 穿搭 --max-notes 10 --output xhs_notes.json

  # 2) API mode (requires you to provide valid signed headers)
  PYTHONPATH=. python examples/xhs_keyword_poc.py \
    --mode api --keyword 穿搭 --max-notes 10 \
    --api-headers '{"x-s":"...","x-t":"..."}' \
    --cookie 'a1=...; web_session=...'

Notes:
- Render mode uses `StealthySession` and listens to XHS API responses via Playwright page events.
- API mode uses `FetcherSession` and calls XHS web API endpoints directly.
- XHS signatures/cookies/headers change frequently. You must provide a valid login state
  and valid signed headers for API mode.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

SEARCH_API_HINT = "/api/sns/web/v1/search/notes"
NOTE_API_HINTS = (
    "/api/sns/web/v1/feed",
    "/api/sns/web/v1/note",
    "/api/sns/web/v1/comment/page",
)

DEFAULT_SEARCH_API = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
DEFAULT_DETAIL_API = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"


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


def lazy_import_fetchers(mode: str):
    """Delay imports so `--help` still works without optional deps."""
    if mode == "render":
        from scrapling.fetchers import StealthySession

        return StealthySession

    from scrapling.fetchers import FetcherSession

    return FetcherSession


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


def parse_cookie_to_dict(cookie_header: str) -> Dict[str, str]:
    cookie_dict: Dict[str, str] = {}
    for pair in cookie_header.split(";"):
        if "=" not in pair:
            continue
        name, val = pair.split("=", 1)
        name, val = name.strip(), val.strip()
        if name:
            cookie_dict[name] = val
    return cookie_dict


def load_json_input(raw_or_path: str) -> Dict[str, Any]:
    if not raw_or_path.strip():
        return {}
    candidate = raw_or_path.strip()
    if candidate.startswith("{"):
        return json.loads(candidate)
    with open(candidate, "r", encoding="utf-8") as f:
        return json.load(f)


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


def extract_note_ids_from_payload(payload: Dict[str, Any]) -> set[str]:
    data = payload.get("data") or payload
    items = data.get("items") or data.get("note_list") or []
    ids: set[str] = set()
    for item in items:
        note = item.get("note_card") or item.get("note") or item
        note_id = str(pick(note, "note_id", "id") or "").strip()
        if note_id:
            ids.add(note_id)
    return ids


def parse_note_detail_payload(payload: Dict[str, Any], model: XHSNote) -> None:
    data = payload.get("data") or payload
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
            model.first_image = str(pick(first, "url_default", "url", "image_url", "master_url") or "")


# ---------------------------- render mode ----------------------------

def search_note_ids_render(
    session: Any,
    keyword: str,
    max_notes: int = 20,
    scroll_rounds: int = 4,
    idle_rounds_stop: int = 3,
) -> Dict[str, XHSNote]:
    url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&source=web_explore_feed"
    captured_payloads: List[Dict[str, Any]] = []
    seen_note_ids: set[str] = set()

    def page_action(page):
        nonlocal seen_note_ids

        def on_response(resp):
            try:
                if SEARCH_API_HINT in resp.url:
                    payload = resp.json()
                    captured_payloads.append(payload)
                    seen_note_ids.update(extract_note_ids_from_payload(payload))
            except Exception:
                return

        page.on("response", on_response)
        page.wait_for_timeout(2500)
        idle_rounds = 0
        for _ in range(scroll_rounds):
            before_count = len(seen_note_ids)
            page.mouse.wheel(0, 2800)
            page.wait_for_timeout(1500)
            after_count = len(seen_note_ids)
            if after_count > before_count:
                idle_rounds = 0
            else:
                idle_rounds += 1
            if idle_rounds >= idle_rounds_stop:
                break

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


def enrich_note_detail_render(session: Any, model: XHSNote) -> None:
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

    # Fallback from DOM when API response is unavailable.
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
            model.first_image = str(img[0].attrib.get("src") or img[0].attrib.get("data-src") or "")


def run_render_mode(
    keyword: str,
    max_notes: int,
    cookie_header: str = "",
    scroll_rounds: int = 4,
    render_idle_rounds: int = 3,
) -> List[XHSNote]:
    StealthySession = lazy_import_fetchers("render")
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
        notes_map = search_note_ids_render(
            session,
            keyword=keyword,
            max_notes=max_notes,
            scroll_rounds=scroll_rounds,
            idle_rounds_stop=render_idle_rounds,
        )
        for note in notes_map.values():
            try:
                enrich_note_detail_render(session, note)
            except Exception:
                continue
        return list(notes_map.values())


# ---------------------------- api mode ----------------------------

def api_search_notes(
    session: Any,
    keyword: str,
    max_notes: int,
    search_api_url: str,
    api_headers: Dict[str, Any],
    page_size: int,
) -> Dict[str, XHSNote]:
    captured_payloads: List[Dict[str, Any]] = []
    page = 1

    while True:
        params = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": "",
            "sort": "general",
            "note_type": 0,
        }

        resp = session.get(search_api_url, params=params, headers=api_headers)
        try:
            payload = resp.json()
        except Exception:
            break

        captured_payloads.append(payload)
        notes = flatten_search_notes(captured_payloads)
        if len(notes) >= max_notes:
            return dict(list(notes.items())[:max_notes])

        has_more = (payload.get("data") or {}).get("has_more")
        if not has_more:
            return notes
        page += 1


def api_enrich_note_detail(
    session: Any,
    note: XHSNote,
    detail_api_url: str,
    api_headers: Dict[str, Any],
) -> None:
    # Commonly used feed endpoint style; you can override URL/params if your API shape differs.
    params = {
        "source_note_id": note.note_id,
        "image_scenes": "CRD_PRV_WEBP,CRD_WM_WEBP",
    }
    resp = session.get(detail_api_url, params=params, headers=api_headers)
    try:
        payload = resp.json()
    except Exception:
        return
    parse_note_detail_payload(payload, note)


def run_api_mode(
    keyword: str,
    max_notes: int,
    cookie_header: str,
    api_headers_raw: str,
    search_api_url: str,
    detail_api_url: str,
    page_size: int,
) -> List[XHSNote]:
    FetcherSession = lazy_import_fetchers("api")
    api_headers = load_json_input(api_headers_raw)
    cookie_dict = parse_cookie_to_dict(cookie_header)

    with FetcherSession(
        stealthy_headers=False,
        impersonate="chrome",
        timeout=30,
        retries=2,
        retry_delay=1,
        cookies=cookie_dict or None,
    ) as session:
        notes_map = api_search_notes(
            session=session,
            keyword=keyword,
            max_notes=max_notes,
            search_api_url=search_api_url,
            api_headers=api_headers,
            page_size=page_size,
        )

        for note in notes_map.values():
            try:
                api_enrich_note_detail(
                    session=session,
                    note=note,
                    detail_api_url=detail_api_url,
                    api_headers=api_headers,
                )
            except Exception:
                continue

        return list(notes_map.values())


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Xiaohongshu keyword scraping PoC based on Scrapling")
    parser.add_argument("--mode", choices=["render", "api"], default="render", help="render=browser mode, api=HTTP mode")
    parser.add_argument("--keyword", required=True, help="Search keyword")
    parser.add_argument("--max-notes", type=int, default=10, help="Maximum notes to extract")
    parser.add_argument("--cookie", default="", help="Raw cookie header string from logged-in browser")
    parser.add_argument("--output", default="xhs_notes.json", help="Output JSON file path")

    # render-mode tuning
    parser.add_argument("--scroll-rounds", type=int, default=4, help="How many scroll rounds in render mode")
    parser.add_argument(
        "--render-idle-rounds",
        type=int,
        default=3,
        help="Stop render scrolling after this many consecutive rounds with no new note_id",
    )

    # api-mode tuning
    parser.add_argument(
        "--api-headers",
        default="{}",
        help="JSON string or JSON file path containing required API headers (e.g. x-s, x-t, x-s-common)",
    )
    parser.add_argument("--search-api-url", default=DEFAULT_SEARCH_API, help="Search API URL for --mode api")
    parser.add_argument("--detail-api-url", default=DEFAULT_DETAIL_API, help="Detail API URL for --mode api")
    parser.add_argument("--page-size", type=int, default=20, help="API mode page size")

    return parser


def main() -> None:
    args = build_cli().parse_args()
    start = time.time()

    if args.mode == "render":
        items = run_render_mode(
            keyword=args.keyword,
            max_notes=args.max_notes,
            cookie_header=args.cookie,
            scroll_rounds=args.scroll_rounds,
            render_idle_rounds=args.render_idle_rounds,
        )
    else:
        items = run_api_mode(
            keyword=args.keyword,
            max_notes=args.max_notes,
            cookie_header=args.cookie,
            api_headers_raw=args.api_headers,
            search_api_url=args.search_api_url,
            detail_api_url=args.detail_api_url,
            page_size=args.page_size,
        )

    payload = {
        "mode": args.mode,
        "keyword": args.keyword,
        "count": len(items),
        "elapsed_sec": round(time.time() - start, 2),
        "items": [asdict(item) for item in items],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(items)} notes to {args.output} (mode={args.mode})")


if __name__ == "__main__":
    main()
