from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from scrapling.engines._browsers._stealth import AsyncStealthySession
from scrapling.engines.toolbelt.convertor import ResponseFactory


@pytest.mark.asyncio
async def test_solver_clicks_localized_cloudflare_challenge(monkeypatch):
    solved = False

    async def content(_page):
        if solved:
            return "<html><title>La Redoute</title></html>"
        return (
            "<html><title>Un instant…</title>"
            '<input name="cf-turnstile-response">'
            "<script>cType: 'interactive'</script></html>"
        )

    async def click(*args, **kwargs):
        nonlocal solved
        solved = True

    monkeypatch.setattr(ResponseFactory, "_get_async_page_content", AsyncMock(side_effect=content))
    monkeypatch.setattr(AsyncStealthySession, "_wait_for_networkidle", AsyncMock())
    monkeypatch.setattr(AsyncStealthySession, "_wait_for_page_stability", AsyncMock())

    box = MagicMock()
    box.bounding_box = AsyncMock(return_value={"x": 100, "y": 200})
    response_input = MagicMock()
    response_input.locator.return_value = MagicMock(last=box)
    page = MagicMock()
    page.frame.return_value = None
    page.locator.return_value = response_input
    page.mouse = SimpleNamespace(click=AsyncMock(side_effect=click))

    await object.__new__(AsyncStealthySession)._cloudflare_solver(page)

    page.locator.assert_any_call('input[name="cf-turnstile-response"]')
    response_input.locator.assert_called_once_with("xpath=..")
    x, y = page.mouse.click.await_args.args
    assert 126 <= x <= 128
    assert 225 <= y <= 227
