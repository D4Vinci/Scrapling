"""Session management and advanced output tooling for the Scrapling MCP server.

This module exposes :class:`SessionMCPTools`, a collection of ``@staticmethod``
async helpers that:

* boot/teardown long-lived browser sessions backed by
  :class:`scrapling.fetchers.AsyncDynamicSession` /
  :class:`scrapling.fetchers.AsyncStealthySession`,
* persist sessions across MCP tool calls via shared registries,
* export/import session storage state (cookies + localStorage + viewport + UA),
* produce screenshots, PDFs, HAR, DOM diffs and live network controls.

The session and page registries are intentionally shared with
``scrapling.core.ai_interact``; both modules import the *same* dict objects so
that any agent (interact, session, vision, ...) can look up an active session
by id.  When ``ai_interact`` has not been authored yet, this module degrades
gracefully and instantiates the registries locally so import-time never blows
up.
"""

from __future__ import annotations

import base64
import json
import secrets
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession


# ---------------------------------------------------------------------------
# Shared registries
# ---------------------------------------------------------------------------
#
# We try to bind onto whatever objects ``ai_interact`` already exposes so the
# two modules end up referencing the *same* underlying dict instances.  If the
# sibling module is empty or fails to import we create local dicts and expose
# the registration helper so ``ai_interact`` can re-use them when it boots.

try:  # pragma: no cover - cooperating module may be empty during bootstrap
    from scrapling.core.ai_interact import (  # type: ignore[attr-defined]
        _SESSION_REGISTRY,
        _PAGE_REGISTRY,
        register_session,
    )
except Exception:  # noqa: BLE001 - degrade if ai_interact is incomplete
    _SESSION_REGISTRY: Dict[str, Dict[str, Any]] = {}
    _PAGE_REGISTRY: Dict[str, Any] = {}

    def register_session(session_id: str, session: Any, session_type: str = "dynamic") -> None:
        """Register a live session into the shared registry.

        ``ai_interact`` is expected to provide its own implementation; this
        fallback keeps imports working when the sibling module is still being
        authored by another agent.
        """

        _SESSION_REGISTRY[session_id] = {
            "session": session,
            "type": session_type,
            "created_at": time.time(),
        }


# Per-session network capture buffers and route registries.  Kept module-local
# because they are implementation details of this module's tooling.
_API_CAPTURES: Dict[str, Dict[str, Any]] = {}
_ROUTE_REGISTRY: Dict[str, List[Dict[str, Any]]] = {}
_HAR_REGISTRY: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Pydantic output schema
# ---------------------------------------------------------------------------


class SessionResponse(BaseModel):
    """Uniform response envelope for session-oriented MCP tools."""

    success: bool
    session_id: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _new_session_id() -> str:
    """Generate a 12-char hex session identifier."""

    return secrets.token_hex(6)


def _get_session_record(session_id: str) -> Dict[str, Any]:
    record = _SESSION_REGISTRY.get(session_id)
    if record is None:
        raise KeyError(f"Unknown session_id: {session_id}")
    return record


async def _get_or_create_page(session_id: str) -> Any:
    """Resolve the cached page for ``session_id`` or open a fresh tab."""

    page = _PAGE_REGISTRY.get(session_id)
    if page is not None and not getattr(page, "is_closed", lambda: False)():
        return page

    record = _get_session_record(session_id)
    session = record["session"]
    context = getattr(session, "context", None)
    if context is None:
        raise RuntimeError(f"Session {session_id!r} has no active browser context")

    page = await context.new_page()
    _PAGE_REGISTRY[session_id] = page
    return page


def _merge_additional_args(
    base: Optional[Dict[str, Any]],
    record_har_path: Optional[str],
    record_video_dir: Optional[str],
) -> Dict[str, Any]:
    """Inject HAR / video recording options into ``additional_args``."""

    merged: Dict[str, Any] = dict(base or {})
    if record_har_path:
        merged["record_har_path"] = record_har_path
        merged.setdefault("record_har_omit_content", False)
    if record_video_dir:
        merged["record_video_dir"] = record_video_dir
    return merged


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class SessionMCPTools:
    """Static MCP tool handlers for session management and advanced outputs."""

    # ------------------------------------------------------------------ #
    # 1. open_session                                                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def open_session(
        session_type: str = "dynamic",
        session_id: Optional[str] = None,
        headless: bool = True,
        cookies: Optional[Any] = None,
        proxy: Optional[Any] = None,
        locale: Optional[str] = None,
        timezone_id: Optional[str] = None,
        useragent: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        cdp_url: Optional[str] = None,
        real_chrome: bool = False,
        timeout: int = 30000,
        disable_resources: bool = False,
        max_pages: int = 5,
        solve_cloudflare: bool = False,
        allow_webgl: bool = True,
        hide_canvas: bool = False,
        block_webrtc: bool = False,
        additional_args: Optional[Dict[str, Any]] = None,
        record_har_path: Optional[str] = None,
        record_video_dir: Optional[str] = None,
    ) -> SessionResponse:
        """Boot a long-lived browser session (dynamic or stealthy)."""

        try:
            if session_type not in ("dynamic", "stealthy"):
                raise ValueError(
                    f"session_type must be 'dynamic' or 'stealthy', got {session_type!r}"
                )

            sid = session_id or _new_session_id()
            if sid in _SESSION_REGISTRY:
                raise ValueError(f"session_id {sid!r} already exists")

            merged_extra = _merge_additional_args(
                additional_args, record_har_path, record_video_dir
            )

            common_kwargs: Dict[str, Any] = dict(
                headless=headless,
                locale=locale,
                timezone_id=timezone_id,
                useragent=useragent,
                extra_headers=extra_headers,
                cdp_url=cdp_url,
                real_chrome=real_chrome,
                timeout=timeout,
                disable_resources=disable_resources,
                max_pages=max_pages,
                additional_args=merged_extra,
            )
            if cookies is not None:
                common_kwargs["cookies"] = cookies
            if proxy is not None:
                common_kwargs["proxy"] = proxy

            if session_type == "stealthy":
                common_kwargs.update(
                    solve_cloudflare=solve_cloudflare,
                    allow_webgl=allow_webgl,
                    hide_canvas=hide_canvas,
                    block_webrtc=block_webrtc,
                )
                session = AsyncStealthySession(**common_kwargs)
            else:
                session = AsyncDynamicSession(**common_kwargs)

            try:
                await session.__aenter__()
            except Exception:
                # __aenter__ may have launched playwright/browser before raising;
                # always attempt teardown so we never leak chromium processes.
                try:
                    await session.__aexit__(None, None, None)
                except Exception:  # noqa: BLE001 - best-effort cleanup
                    pass
                raise

            register_session(sid, session, session_type)
            # Make sure the registry record carries the type even if a
            # third-party ``register_session`` ignored the kwarg.
            record = _SESSION_REGISTRY.get(sid)
            if record is not None:
                record.setdefault("type", session_type)
                record.setdefault("created_at", time.time())
                if record_har_path:
                    _HAR_REGISTRY[sid] = {"path": record_har_path, "active": True}

            return SessionResponse(
                success=True,
                session_id=sid,
                data={"session_id": sid, "type": session_type, "ready": True},
            )
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(success=False, error=f"open_session failed: {exc}")

    # ------------------------------------------------------------------ #
    # 2. close_session                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def close_session(session_id: str) -> SessionResponse:
        """Tear down a registered session and release its resources."""

        try:
            record = _SESSION_REGISTRY.pop(session_id, None)
            if record is None:
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    error=f"Unknown session_id: {session_id}",
                )
            session = record["session"]

            page = _PAGE_REGISTRY.pop(session_id, None)
            if page is not None:
                try:
                    if not page.is_closed():
                        await page.close()
                except Exception:  # noqa: BLE001 - best effort cleanup
                    pass

            try:
                await session.__aexit__(None, None, None)
            finally:
                _API_CAPTURES.pop(session_id, None)
                _ROUTE_REGISTRY.pop(session_id, None)
                har_meta = _HAR_REGISTRY.pop(session_id, None)
                # Bug #14: ai_interact._MOUSE_POS leaked one entry per session.
                try:
                    from scrapling.core.ai_interact import _MOUSE_POS as _mp
                    _mp.pop(session_id, None)
                except Exception:  # noqa: BLE001
                    pass

            return SessionResponse(
                success=True,
                session_id=session_id,
                data={"closed": True, "har_path": (har_meta or {}).get("path")},
            )
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False, session_id=session_id, error=f"close_session failed: {exc}"
            )

    # ------------------------------------------------------------------ #
    # 3. list_sessions                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def list_sessions() -> SessionResponse:
        """Snapshot of all registered sessions."""

        try:
            now = time.time()
            sessions: List[Dict[str, Any]] = []
            for sid, record in _SESSION_REGISTRY.items():
                session = record.get("session")
                created_at = record.get("created_at", now)

                page = _PAGE_REGISTRY.get(sid)
                current_url: Optional[str] = None
                if page is not None:
                    try:
                        if not page.is_closed():
                            current_url = page.url
                    except Exception:  # noqa: BLE001
                        current_url = None

                page_count = 0
                context = getattr(session, "context", None)
                if context is not None:
                    try:
                        page_count = len(context.pages)
                    except Exception:  # noqa: BLE001
                        page_count = 0

                sessions.append(
                    {
                        "session_id": sid,
                        "type": record.get("type", "dynamic"),
                        "age_seconds": round(now - created_at, 3),
                        "current_url": current_url,
                        "page_count": page_count,
                    }
                )

            return SessionResponse(success=True, data=sessions)
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(success=False, error=f"list_sessions failed: {exc}")

    # ------------------------------------------------------------------ #
    # 4a. export_session                                                 #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def export_session(session_id: str) -> SessionResponse:
        """Serialize cookies + storage + UA + viewport into a base64 blob."""

        try:
            record = _get_session_record(session_id)
            session = record["session"]
            context = getattr(session, "context", None)
            if context is None:
                raise RuntimeError("Session has no active context")

            storage_state = await context.storage_state()

            user_agent: Optional[str] = None
            viewport: Optional[Dict[str, int]] = None
            page = _PAGE_REGISTRY.get(session_id)
            if page is None and getattr(context, "pages", None):
                try:
                    page = context.pages[0]
                except Exception:  # noqa: BLE001
                    page = None
            if page is not None:
                try:
                    user_agent = await page.evaluate("() => navigator.userAgent")
                except Exception:  # noqa: BLE001
                    user_agent = None
                try:
                    viewport = page.viewport_size
                except Exception:  # noqa: BLE001
                    viewport = None

            payload = {
                "version": 1,
                "type": record.get("type", "dynamic"),
                "storage_state": storage_state,
                "user_agent": user_agent,
                "viewport": viewport,
            }
            blob = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
            return SessionResponse(
                success=True,
                session_id=session_id,
                data={"blob": blob, "size_bytes": len(blob)},
            )
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False, session_id=session_id, error=f"export_session failed: {exc}"
            )

    # ------------------------------------------------------------------ #
    # 4b. import_session                                                 #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def import_session(blob: str, headless: bool = True) -> SessionResponse:
        """Recreate a stealthy session from a blob produced by export_session."""

        try:
            try:
                payload = json.loads(base64.b64decode(blob).decode("utf-8"))
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid blob: {exc}") from exc

            storage_state = payload.get("storage_state") or {}
            user_agent = payload.get("user_agent")
            viewport = payload.get("viewport")

            cookies = storage_state.get("cookies") or []
            additional_args: Dict[str, Any] = {"storage_state": storage_state}
            if viewport:
                additional_args["viewport"] = viewport

            sid = _new_session_id()
            session = AsyncStealthySession(
                headless=headless,
                useragent=user_agent,
                cookies=cookies,
                additional_args=additional_args,
            )
            await session.__aenter__()
            register_session(sid, session, "stealthy")
            record = _SESSION_REGISTRY.get(sid)
            if record is not None:
                record.setdefault("type", "stealthy")
                record.setdefault("created_at", time.time())

            return SessionResponse(
                success=True,
                session_id=sid,
                data={"session_id": sid, "type": "stealthy", "ready": True},
            )
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(success=False, error=f"import_session failed: {exc}")

    # ------------------------------------------------------------------ #
    # 5. screenshot                                                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def screenshot(
        session_id: str,
        full_page: bool = False,
        image_type: str = "png",
        quality: Optional[int] = None,
        wait: int = 0,
        wait_selector: Optional[str] = None,
        network_idle: bool = False,
        timeout: int = 30000,
        return_base64: bool = True,
        save_path: Optional[str] = None,
        max_base64_bytes: int = 524288,
    ) -> SessionResponse:
        """Capture a screenshot of the session's active page.

        ``return_base64`` defaults to True for ergonomics, but full-page shots on
        modern resolutions can easily exceed several megabytes. When the raw
        image is larger than ``max_base64_bytes`` and no ``save_path`` is given,
        we transparently write to a temp file and return the path instead of an
        oversized base64 blob.
        """

        try:
            page = await _get_or_create_page(session_id)

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=timeout)
            if network_idle:
                try:
                    await page.wait_for_load_state("networkidle", timeout=timeout)
                except Exception:  # noqa: BLE001
                    pass
            if wait:
                await page.wait_for_timeout(wait)

            shot_kwargs: Dict[str, Any] = {
                "full_page": full_page,
                "type": image_type,
                "timeout": timeout,
            }
            if quality is not None and image_type.lower() in ("jpeg", "jpg"):
                shot_kwargs["quality"] = quality
            if save_path:
                shot_kwargs["path"] = save_path

            raw = await page.screenshot(**shot_kwargs)

            viewport = None
            try:
                viewport = page.viewport_size
            except Exception:  # noqa: BLE001
                viewport = None
            width = (viewport or {}).get("width") if isinstance(viewport, dict) else None
            height = (viewport or {}).get("height") if isinstance(viewport, dict) else None

            size = len(raw) if raw else 0
            data: Dict[str, Any] = {
                "width": width,
                "height": height,
                "save_path": save_path,
                "image_type": image_type,
                "size_bytes": size,
            }
            if raw:
                # Auto-spill large screenshots to disk to keep MCP payloads sane.
                if return_base64 and not save_path and size > max_base64_bytes:
                    import tempfile

                    fd, tmp_path = tempfile.mkstemp(prefix="scrapling-shot-", suffix=f".{image_type}")
                    with __import__("os").fdopen(fd, "wb") as fp:
                        fp.write(raw)
                    data["save_path"] = tmp_path
                    data["spilled_to_disk"] = True
                    data["reason"] = (
                        f"image is {size} bytes; exceeded max_base64_bytes={max_base64_bytes}. "
                        "Pass save_path to choose your own location, or raise max_base64_bytes."
                    )
                elif return_base64:
                    data["image_base64"] = base64.b64encode(raw).decode("ascii")
            return SessionResponse(success=True, session_id=session_id, data=data)
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False, session_id=session_id, error=f"screenshot failed: {exc}"
            )

    # ------------------------------------------------------------------ #
    # 6. pdf_export                                                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def pdf_export(
        session_id: str,
        save_path: str,
        format: str = "A4",
        landscape: bool = False,
        print_background: bool = True,
        scale: float = 1.0,
        header_template: Optional[str] = None,
        footer_template: Optional[str] = None,
    ) -> SessionResponse:
        """Render the active page to PDF.  Chromium / headless required."""

        try:
            page = await _get_or_create_page(session_id)

            pdf_kwargs: Dict[str, Any] = {
                "path": save_path,
                "format": format,
                "landscape": landscape,
                "print_background": print_background,
                "scale": scale,
            }
            if header_template is not None or footer_template is not None:
                pdf_kwargs["display_header_footer"] = True
                if header_template is not None:
                    pdf_kwargs["header_template"] = header_template
                if footer_template is not None:
                    pdf_kwargs["footer_template"] = footer_template

            data = await page.pdf(**pdf_kwargs)

            size_bytes = len(data) if data else 0
            if not size_bytes and save_path:
                try:
                    import os

                    size_bytes = os.path.getsize(save_path)
                except OSError:
                    size_bytes = 0

            return SessionResponse(
                success=True,
                session_id=session_id,
                data={"success": True, "path": save_path, "size_bytes": size_bytes},
            )
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False, session_id=session_id, error=f"pdf_export failed: {exc}"
            )

    # ------------------------------------------------------------------ #
    # 7. record_har                                                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def record_har(
        session_id: str,
        action: str,
        path: Optional[str] = None,  # noqa: ARG004 - reserved for future symmetry
    ) -> SessionResponse:
        """Inspect / stop HAR recording previously enabled at open_session."""

        try:
            record = _get_session_record(session_id)
            har_meta = _HAR_REGISTRY.get(session_id)

            if action == "status":
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    data={
                        "active": bool(har_meta and har_meta.get("active")),
                        "path": (har_meta or {}).get("path"),
                    },
                )

            if action == "stop":
                if not har_meta:
                    raise RuntimeError(
                        "HAR was not enabled for this session. Pass record_har_path "
                        "to open_session() to enable it."
                    )

                # Bug #12: closing only the context leaves the session half-dead
                # in the registry; subsequent close_session would re-close an
                # already-closed context. Tear the whole session down so the
                # caller gets a clean state and a flushed HAR.
                har_path = har_meta.get("path")
                close_resp = await SessionMCPTools.close_session(session_id)
                har_meta["active"] = False
                return SessionResponse(
                    success=close_resp.success,
                    session_id=session_id,
                    data={"stopped": True, "path": har_path, "session_closed": True},
                    error=close_resp.error,
                )

            if action == "start":
                raise RuntimeError(
                    "HAR recording must be enabled at open_session via record_har_path; "
                    "it cannot be started on a live session."
                )

            raise ValueError(f"Unknown action: {action!r}")
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False, session_id=session_id, error=f"record_har failed: {exc}"
            )

    # ------------------------------------------------------------------ #
    # 8. dom_diff                                                        #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def dom_diff(html_a: str, html_b: str) -> SessionResponse:
        """Compute a coarse DOM diff between two HTML documents."""

        try:
            from lxml import html as lxml_html  # local import keeps cold-start light

            def _index(doc: Any) -> Dict[Any, Any]:
                index: Dict[Any, Any] = {}
                if doc is None:
                    return index
                for el in doc.iter():
                    tag = getattr(el, "tag", None)
                    if not isinstance(tag, str):
                        continue
                    attrs = tuple(sorted((el.attrib or {}).items()))
                    key = (tag, attrs)
                    text = (el.text or "").strip()
                    # Track only the first occurrence per identity key for a
                    # deterministic comparison.
                    index.setdefault(key, text)
                return index

            def _selector(key: Any) -> str:
                tag, attrs = key
                bits = [tag]
                attr_dict = dict(attrs)
                if "id" in attr_dict:
                    bits.append(f"#{attr_dict['id']}")
                if "class" in attr_dict:
                    classes = ".".join(attr_dict["class"].split())
                    if classes:
                        bits.append(f".{classes}")
                return "".join(bits) if len(bits) > 1 else tag

            doc_a = lxml_html.fromstring(html_a) if html_a else None
            doc_b = lxml_html.fromstring(html_b) if html_b else None
            idx_a = _index(doc_a)
            idx_b = _index(doc_b)

            added: List[Dict[str, str]] = []
            removed: List[Dict[str, str]] = []
            changed: List[Dict[str, str]] = []

            for key, text in idx_b.items():
                if key not in idx_a:
                    added.append({"selector": _selector(key), "text": text})

            for key, text in idx_a.items():
                if key not in idx_b:
                    removed.append({"selector": _selector(key), "text": text})
                elif idx_b[key] != text:
                    changed.append(
                        {
                            "selector": _selector(key),
                            "before": text,
                            "after": idx_b[key],
                        }
                    )

            return SessionResponse(
                success=True,
                data={"added": added, "removed": removed, "changed": changed},
            )
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(success=False, error=f"dom_diff failed: {exc}")

    # ------------------------------------------------------------------ #
    # 9. network_intercept                                               #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def network_intercept(
        session_id: str,
        action: str,
        pattern: Optional[str] = None,
        response_body: Optional[str] = None,
        block: bool = False,
    ) -> SessionResponse:
        """Install or clear request interception rules on the active page."""

        try:
            page = await _get_or_create_page(session_id)
            routes = _ROUTE_REGISTRY.setdefault(session_id, [])

            if action == "clear":
                cleared = 0
                for entry in list(routes):
                    try:
                        await page.unroute(entry["pattern"], entry["handler"])
                        cleared += 1
                    except Exception:  # noqa: BLE001
                        pass
                _ROUTE_REGISTRY[session_id] = []
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    data={"cleared": cleared},
                )

            if pattern is None:
                raise ValueError("'pattern' is required for action 'block' or 'modify'")

            if action == "block" or block:

                async def _block_handler(route, request):  # noqa: ARG001
                    try:
                        await route.abort()
                    except Exception:  # noqa: BLE001
                        await route.continue_()

                await page.route(pattern, _block_handler)
                routes.append({"pattern": pattern, "handler": _block_handler, "kind": "block"})
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    data={"installed": "block", "pattern": pattern},
                )

            if action == "modify":
                if response_body is None:
                    raise ValueError("'response_body' is required for action 'modify'")
                body_value = response_body

                async def _modify_handler(route, request):  # noqa: ARG001
                    try:
                        await route.fulfill(status=200, body=body_value)
                    except Exception:  # noqa: BLE001
                        await route.continue_()

                await page.route(pattern, _modify_handler)
                routes.append({"pattern": pattern, "handler": _modify_handler, "kind": "modify"})
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    data={"installed": "modify", "pattern": pattern},
                )

            raise ValueError(f"Unknown action: {action!r}")
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False,
                session_id=session_id,
                error=f"network_intercept failed: {exc}",
            )

    # ------------------------------------------------------------------ #
    # 10. extract_api_calls                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    async def extract_api_calls(
        session_id: str,
        action: str = "start",
        filter_pattern: Optional[str] = None,
    ) -> SessionResponse:
        """Capture XHR / fetch traffic on a session's browser context."""

        try:
            record = _get_session_record(session_id)
            session = record["session"]
            context = getattr(session, "context", None)
            if context is None:
                raise RuntimeError("Session has no active context")

            capture = _API_CAPTURES.get(session_id)

            if action == "start":
                if capture and capture.get("active"):
                    return SessionResponse(
                        success=True,
                        session_id=session_id,
                        data={"started": False, "reason": "already active"},
                    )

                events: List[Dict[str, Any]] = []
                pending: Dict[Any, Dict[str, Any]] = {}

                def _on_request(request: Any) -> None:
                    rtype = getattr(request, "resource_type", None)
                    if rtype not in ("xhr", "fetch"):
                        return
                    body = None
                    try:
                        body = request.post_data
                    except Exception:  # noqa: BLE001
                        body = None
                    pending[request] = {
                        "url": request.url,
                        "method": request.method,
                        "headers": dict(request.headers or {}),
                        "request_body": body,
                        "resource_type": rtype,
                        "ts": time.time(),
                    }

                async def _on_response(response: Any) -> None:
                    request = response.request
                    entry = pending.pop(request, None)
                    if entry is None:
                        rtype = getattr(request, "resource_type", None)
                        if rtype not in ("xhr", "fetch"):
                            return
                        entry = {
                            "url": request.url,
                            "method": request.method,
                            "headers": dict(request.headers or {}),
                            "request_body": None,
                            "resource_type": rtype,
                            "ts": time.time(),
                        }
                    entry["status"] = response.status
                    preview: Optional[str] = None
                    try:
                        text = await response.text()
                        preview = text[:2048] if text else None
                    except Exception:  # noqa: BLE001
                        preview = None
                    entry["response_body_preview"] = preview
                    events.append(entry)

                context.on("request", _on_request)
                context.on("response", _on_response)
                _API_CAPTURES[session_id] = {
                    "events": events,
                    "active": True,
                    "request_listener": _on_request,
                    "response_listener": _on_response,
                    "context": context,
                }
                return SessionResponse(
                    success=True, session_id=session_id, data={"started": True}
                )

            if action == "stop":
                if not capture or not capture.get("active"):
                    return SessionResponse(
                        success=True,
                        session_id=session_id,
                        data={"stopped": False, "reason": "not active"},
                    )
                ctx = capture.get("context") or context
                try:
                    ctx.remove_listener("request", capture["request_listener"])
                    ctx.remove_listener("response", capture["response_listener"])
                except Exception:  # noqa: BLE001
                    pass
                capture["active"] = False
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    data={"stopped": True, "events_collected": len(capture.get("events", []))},
                )

            if action == "get":
                events = list((capture or {}).get("events", []))
                if filter_pattern:
                    import re

                    rx = re.compile(filter_pattern)
                    events = [e for e in events if rx.search(e.get("url", ""))]
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    data={"count": len(events), "events": events},
                )

            raise ValueError(f"Unknown action: {action!r}")
        except Exception as exc:  # noqa: BLE001
            return SessionResponse(
                success=False,
                session_id=session_id,
                error=f"extract_api_calls failed: {exc}",
            )


__all__ = [
    "SessionMCPTools",
    "SessionResponse",
    "_SESSION_REGISTRY",
    "_PAGE_REGISTRY",
    "_API_CAPTURES",
    "_ROUTE_REGISTRY",
    "_HAR_REGISTRY",
    "register_session",
]
