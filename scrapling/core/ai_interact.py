"""Interaction tools and Action Plan for Scrapling MCP.
Allows LLMs to drive a persistent browser session with click/type/scroll/wait
primitives, plus a run_action_plan tool that batches them.
"""
import asyncio
import base64
import random
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Shared registry shape (also used by ai_session.py):
#   _SESSION_REGISTRY[session_id] = {"session": <AsyncSession>, "type": "dynamic"|"stealthy", "created_at": float}
_SESSION_REGISTRY: Dict[str, Dict[str, Any]] = {}
_PAGE_REGISTRY: Dict[str, Any] = {}  # session_id -> playwright Page
_MOUSE_POS: Dict[str, Dict[str, float]] = {}  # session_id -> {x, y}


def register_session(session_id: str, session: Any, session_type: str = "dynamic") -> None:
    """Register an open AsyncDynamicSession / AsyncStealthySession under an id."""
    _SESSION_REGISTRY[session_id] = {
        "session": session,
        "type": session_type,
        "created_at": time.time(),
    }


def get_session(session_id: str):
    """Return the registered session object or raise."""
    record = _SESSION_REGISTRY.get(session_id)
    if record is None:
        raise ValueError(f"Session {session_id} not found. Open one with open_session first.")
    return record["session"] if isinstance(record, dict) and "session" in record else record


async def get_or_create_page(session_id: str):
    """Return the Playwright Page bound to this session, lazily creating it on first use."""
    page = _PAGE_REGISTRY.get(session_id)
    if page is not None and not getattr(page, "is_closed", lambda: False)():
        return page
    session = get_session(session_id)
    context = getattr(session, "context", None)
    if context is None:
        raise RuntimeError(f"Session {session_id!r} has no active browser context")
    page = await context.new_page()
    _PAGE_REGISTRY[session_id] = page
    _MOUSE_POS[session_id] = {"x": 0.0, "y": 0.0}
    return page


def drop_page(session_id: str) -> None:
    """Forget the cached page (e.g. when the session is closed)."""
    _PAGE_REGISTRY.pop(session_id, None)
    _MOUSE_POS.pop(session_id, None)
    _SESSION_REGISTRY.pop(session_id, None)


class InteractResponse(BaseModel):
    """Generic structured response for interaction tools."""

    success: bool = Field(description="Whether the action completed without error.")
    error: Optional[str] = Field(default=None, description="Error message if the action failed.")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Action-specific output payload.")
    url: Optional[str] = Field(default=None, description="Page URL after the action ran.")


# ---------------------------------------------------------------------------
# Human-like helpers
# ---------------------------------------------------------------------------

def _bezier_points(x0: float, y0: float, x1: float, y1: float, steps: int) -> List[tuple]:
    """Quadratic bezier curve from (x0,y0) to (x1,y1) with a slightly off-axis control point."""
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    dx, dy = x1 - x0, y1 - y0
    dist = max((dx * dx + dy * dy) ** 0.5, 1.0)
    nx, ny = -dy / dist, dx / dist
    bow = random.uniform(-0.25, 0.25) * dist
    cx, cy = mx + nx * bow, my + ny * bow

    pts: List[tuple] = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1.0 - t
        x = u * u * x0 + 2 * u * t * cx + t * t * x1
        y = u * u * y0 + 2 * u * t * cy + t * t * y1
        pts.append((x, y))
    return pts


async def _human_move(page: Any, session_id: str, x: float, y: float, steps: int = 20) -> None:
    """Move the mouse along a bezier curve with small random delays between steps."""
    pos = _MOUSE_POS.setdefault(session_id, {"x": 0.0, "y": 0.0})
    x0, y0 = pos["x"], pos["y"]
    steps = max(5, int(steps))
    for px, py in _bezier_points(x0, y0, float(x), float(y), steps):
        await page.mouse.move(px, py)
        await asyncio.sleep(random.uniform(0.005, 0.015))
    pos["x"], pos["y"] = float(x), float(y)


async def _human_type(page: Any, text: str, delay_min: int = 50, delay_max: int = 180) -> None:
    """Type a string char-by-char with randomized delays and occasional typo+correct."""
    for ch in text:
        # 5% chance of a typo: type a wrong key, backspace, then correct
        if random.random() < 0.05 and ch.isalpha():
            wrong = random.choice("abcdefghijklmnopqrstuvwxyz")
            await page.keyboard.type(wrong)
            await asyncio.sleep(random.uniform(delay_min, delay_max) / 1000.0)
            await page.keyboard.press("Backspace")
            await asyncio.sleep(random.uniform(delay_min, delay_max) / 1000.0)
        await page.keyboard.type(ch)
        await asyncio.sleep(random.uniform(delay_min, delay_max) / 1000.0)


async def _resolve_locator(page: Any, selector: Optional[str], text: Optional[str], index: Optional[int]):
    """Return a Playwright Locator from selector / text / index, in that order."""
    if selector:
        return page.locator(selector).first
    if text:
        return page.get_by_text(text, exact=False).first
    if index is not None:
        return page.locator(
            "a, button, input, select, textarea, [role=button], [role=link], [role=menuitem], [role=tab]"
        ).nth(int(index))
    raise ValueError("One of selector / text / index must be provided.")


async def _element_center(locator) -> tuple:
    """Get the center coordinates of an element via its bounding box, with small jitter."""
    box = await locator.bounding_box()
    if not box:
        raise ValueError("Element is not visible or has no bounding box.")
    cx = box["x"] + box["width"] / 2.0 + random.uniform(-2.0, 2.0)
    cy = box["y"] + box["height"] / 2.0 + random.uniform(-2.0, 2.0)
    return cx, cy


# ---------------------------------------------------------------------------
# DOM summary helper
# ---------------------------------------------------------------------------

_DOM_SUMMARY_JS = r"""
() => {
  const out = [];
  const sels = 'a, button, input, select, textarea, [role=button], [role=link], [role=tab], [role=menuitem]';
  const nodes = Array.from(document.querySelectorAll(sels));
  let idx = 0;
  for (const el of nodes) {
    if (idx >= 80) break;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const tag = el.tagName.toLowerCase();
    const id = el.id ? '#' + el.id : '';
    const cls = (typeof el.className === 'string' && el.className)
        ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.')
        : '';
    const name = el.getAttribute('name');
    const type = el.getAttribute('type');
    const role = el.getAttribute('role');
    const aria = el.getAttribute('aria-label');
    const txt = (el.innerText || el.value || '').trim().slice(0, 80);
    let suggested = id || (tag + cls);
    if (name) suggested = `${tag}[name="${name}"]`;
    out.push({
      index: idx++,
      tag,
      role,
      type,
      name,
      aria_label: aria,
      text: txt,
      selector_suggestion: suggested,
    });
  }
  return out;
}
"""


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class InteractMCPTools:
    """Interaction primitives + action-plan runner backed by a registered browser session."""

    @staticmethod
    async def click(
        session_id: str,
        selector: Optional[str] = None,
        index: Optional[int] = None,
        text: Optional[str] = None,
        button: str = "left",
        click_count: int = 1,
        force: bool = False,
        timeout: int = 10000,
    ) -> InteractResponse:
        """Click an element located by CSS selector, visible text, or interactable index.

        :param session_id: Identifier of an open browser session (see open_session).
        :param selector: CSS selector to locate the target element.
        :param index: 0-based index into the page's interactable elements (links, buttons, inputs).
        :param text: Visible text to match (substring, case-insensitive).
        :param button: Mouse button: "left", "right", or "middle".
        :param click_count: Number of clicks (2 = double click).
        :param force: Bypass actionability checks.
        :param timeout: Milliseconds to wait for the element.
        """
        try:
            page = await get_or_create_page(session_id)
            locator = await _resolve_locator(page, selector, text, index)
            await locator.wait_for(state="visible", timeout=timeout)
            try:
                cx, cy = await _element_center(locator)
                await _human_move(page, session_id, cx, cy, steps=random.randint(15, 28))
            except Exception:
                pass  # Fall back to Playwright's own click positioning
            await locator.click(button=button, click_count=click_count, force=force, timeout=timeout)
            return InteractResponse(success=True, url=page.url)
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def type_text(
        session_id: str,
        selector: str,
        text: str,
        delay_min: int = 50,
        delay_max: int = 180,
        clear_first: bool = True,
    ) -> InteractResponse:
        """Type text into an input with human-like rhythm and occasional typo correction.

        :param session_id: Identifier of an open browser session.
        :param selector: CSS selector for the target input/textarea.
        :param text: The text to enter.
        :param delay_min: Minimum per-character delay in milliseconds.
        :param delay_max: Maximum per-character delay in milliseconds.
        :param clear_first: Whether to clear the field before typing.
        """
        try:
            page = await get_or_create_page(session_id)
            locator = page.locator(selector).first
            await locator.wait_for(state="visible", timeout=10000)
            try:
                cx, cy = await _element_center(locator)
                await _human_move(page, session_id, cx, cy, steps=random.randint(12, 22))
            except Exception:
                pass
            await locator.click()
            if clear_first:
                await page.keyboard.press("Control+A")
                await asyncio.sleep(random.uniform(0.04, 0.10))
                await page.keyboard.press("Delete")
                await asyncio.sleep(random.uniform(0.04, 0.10))
            await _human_type(page, text, delay_min=delay_min, delay_max=delay_max)
            return InteractResponse(success=True, url=page.url, data={"typed": text})
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def press_key(
        session_id: str,
        key: str,
        modifiers: Optional[List[str]] = None,
    ) -> InteractResponse:
        """Press a single key, optionally with modifiers like Control / Shift / Alt / Meta.

        :param session_id: Identifier of an open browser session.
        :param key: Playwright key name (e.g. "Enter", "ArrowDown", "a").
        :param modifiers: Modifier keys to hold (e.g. ["Control", "Shift"]).
        """
        try:
            page = await get_or_create_page(session_id)
            combo = "+".join((modifiers or []) + [key]) if modifiers else key
            await page.keyboard.press(combo)
            return InteractResponse(success=True, url=page.url, data={"key": combo})
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def scroll(
        session_id: str,
        direction: str = "down",
        amount: int = 500,
        selector: Optional[str] = None,
        until_text: Optional[str] = None,
        max_steps: int = 20,
    ) -> InteractResponse:
        """Scroll the page (or a container) in human-sized chunks. Optionally stop when text appears.

        :param session_id: Identifier of an open browser session.
        :param direction: "up", "down", "left", or "right".
        :param amount: Total pixels to scroll if no until_text is given.
        :param selector: Optional element to scroll into view first.
        :param until_text: Stop scrolling once this text becomes visible.
        :param max_steps: Safety cap on scroll iterations when using until_text.
        """
        try:
            page = await get_or_create_page(session_id)
            sign_x, sign_y = 0, 0
            if direction == "down":
                sign_y = 1
            elif direction == "up":
                sign_y = -1
            elif direction == "right":
                sign_x = 1
            elif direction == "left":
                sign_x = -1
            else:
                raise ValueError(f"Unknown direction: {direction}")

            if selector:
                await page.locator(selector).first.scroll_into_view_if_needed(timeout=5000)

            steps_taken = 0
            scrolled = 0
            chunk = max(60, min(220, abs(amount) // max(1, max_steps // 2 or 1) or 120))

            while steps_taken < max_steps:
                if until_text:
                    try:
                        visible = await page.locator(f"text={until_text}").first.is_visible()
                    except Exception:
                        visible = False
                    if visible:
                        break
                else:
                    if scrolled >= abs(amount):
                        break

                step = chunk + random.randint(-30, 30)
                await page.mouse.wheel(sign_x * step, sign_y * step)
                scrolled += step
                steps_taken += 1
                await asyncio.sleep(random.uniform(0.08, 0.22))

            return InteractResponse(
                success=True,
                url=page.url,
                data={"steps": steps_taken, "scrolled_px": scrolled},
            )
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def hover(
        session_id: str,
        selector: Optional[str] = None,
        index: Optional[int] = None,
    ) -> InteractResponse:
        """Hover the mouse over an element, moving along a curved path.

        :param session_id: Identifier of an open browser session.
        :param selector: CSS selector to locate the target.
        :param index: Fallback positional index in the interactables list.
        """
        try:
            page = await get_or_create_page(session_id)
            locator = await _resolve_locator(page, selector, None, index)
            await locator.wait_for(state="visible", timeout=10000)
            try:
                cx, cy = await _element_center(locator)
                await _human_move(page, session_id, cx, cy, steps=random.randint(15, 25))
            except Exception:
                await locator.hover()
            return InteractResponse(success=True, url=page.url)
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def wait_for(
        session_id: str,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        network_idle: bool = False,
        timeout: int = 10000,
    ) -> InteractResponse:
        """Wait for a selector, visible text, or network-idle state. Exactly one trigger.

        :param session_id: Identifier of an open browser session.
        :param selector: CSS selector to wait for (state=visible).
        :param text: Text to wait for in the page.
        :param network_idle: If True, wait until network is idle.
        :param timeout: Milliseconds before giving up.
        """
        try:
            page = await get_or_create_page(session_id)
            if selector:
                await page.locator(selector).first.wait_for(state="visible", timeout=timeout)
            elif text:
                await page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=timeout)
            elif network_idle:
                await page.wait_for_load_state("networkidle", timeout=timeout)
            else:
                raise ValueError("Provide selector, text, or network_idle=True.")
            return InteractResponse(success=True, url=page.url)
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def navigate(
        session_id: str,
        url: str,
        wait_until: str = "load",
    ) -> InteractResponse:
        """Navigate the active page to a URL.

        :param session_id: Identifier of an open browser session.
        :param url: Destination URL.
        :param wait_until: "load", "domcontentloaded", or "networkidle".
        """
        try:
            page = await get_or_create_page(session_id)
            if wait_until not in ("load", "domcontentloaded", "networkidle"):
                raise ValueError(f"wait_until must be load/domcontentloaded/networkidle, got {wait_until}")
            await page.goto(url, wait_until=wait_until)
            return InteractResponse(success=True, url=page.url)
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def get_page_state(
        session_id: str,
        include_screenshot: bool = False,
        include_dom_summary: bool = True,
    ) -> InteractResponse:
        """Return the current page URL, title, optional DOM summary, and optional screenshot.

        :param session_id: Identifier of an open browser session.
        :param include_screenshot: Embed a base64 PNG screenshot in data.screenshot.
        :param include_dom_summary: Include a list of likely-interactable elements with selector hints.
        """
        try:
            page = await get_or_create_page(session_id)
            data: Dict[str, Any] = {"url": page.url, "title": await page.title()}
            if include_dom_summary:
                try:
                    data["dom_summary"] = await page.evaluate(_DOM_SUMMARY_JS)
                except Exception as exc:  # noqa: BLE001
                    data["dom_summary"] = []
                    data["dom_summary_error"] = f"{type(exc).__name__}: {exc}"
            if include_screenshot:
                shot = await page.screenshot(full_page=False)
                data["screenshot"] = base64.b64encode(shot).decode("ascii")
            return InteractResponse(success=True, url=page.url, data=data)
        except Exception as exc:  # noqa: BLE001
            return InteractResponse(success=False, error=f"{type(exc).__name__}: {exc}")

    @staticmethod
    async def run_action_plan(
        session_id: str,
        steps: List[Dict[str, Any]],
        stop_on_error: bool = True,
    ) -> List[Dict[str, Any]]:
        """Execute a list of interaction steps in order.

        Each step is a dict like {"action": "click", "selector": "..."}.
        Supported actions: click, type, scroll, wait_for, navigate, press_key, hover.
        Returns a list of {step_index, action, success, error?, output?}.

        :param session_id: Identifier of an open browser session.
        :param steps: Ordered list of step dicts.
        :param stop_on_error: Halt the plan on the first failed step.
        """
        results: List[Dict[str, Any]] = []
        dispatch = {
            "click": InteractMCPTools.click,
            "type": InteractMCPTools.type_text,
            "type_text": InteractMCPTools.type_text,
            "scroll": InteractMCPTools.scroll,
            "wait_for": InteractMCPTools.wait_for,
            "navigate": InteractMCPTools.navigate,
            "press_key": InteractMCPTools.press_key,
            "hover": InteractMCPTools.hover,
        }
        for i, raw in enumerate(steps):
            step = dict(raw or {})
            action = step.pop("action", None)
            entry: Dict[str, Any] = {"step_index": i, "action": action, "success": False}
            handler = dispatch.get(action) if action else None
            if handler is None:
                entry["error"] = f"Unknown action: {action!r}"
                results.append(entry)
                if stop_on_error:
                    break
                continue
            try:
                resp: InteractResponse = await handler(session_id=session_id, **step)
                entry["success"] = resp.success
                if resp.error:
                    entry["error"] = resp.error
                if resp.data is not None:
                    entry["output"] = resp.data
            except Exception as exc:  # noqa: BLE001
                entry["error"] = f"{type(exc).__name__}: {exc}"
            # X2 finding: when a step fails the LLM has no idea what's
            # actually on the page. Attach a trimmed dom_summary so the
            # caller can choose a different selector without re-prompting.
            if not entry["success"]:
                try:
                    state = await InteractMCPTools.get_page_state(
                        session_id=session_id,
                        include_screenshot=False,
                        include_dom_summary=True,
                    )
                    if state.success and state.data:
                        summary = state.data.get("dom_summary") or []
                        entry["page_state"] = {
                            "url": state.data.get("url"),
                            "title": state.data.get("title"),
                            "dom_summary": summary[:30],
                        }
                except Exception:  # noqa: BLE001 - best effort
                    pass
            results.append(entry)
            if stop_on_error and not entry["success"]:
                break
        return results
