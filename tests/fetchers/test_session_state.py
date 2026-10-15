from json import JSONDecodeError, loads
from os import getenv
from pathlib import Path

import pytest

from scrapling.core._types import Any
from scrapling.engines.toolbelt.proxy_rotation import ProxyRotator
from scrapling.fetchers import AsyncStealthySession, StealthySession


URL = "http://state.test/"
HTML = '<!DOCTYPE html><html><head><link rel="icon" href="data:,"></head><body>ready</body></html>'
STATE_ERROR = "Session state requires a started browser session without proxy rotation"
WRITE_STATE = """async value => {
    document.cookie = `login=${value}; Path=/; SameSite=Lax`;
    localStorage.setItem('login', value);
    sessionStorage.setItem('temporary', value);
    await new Promise((resolve, reject) => {
        const request = indexedDB.open('auth', 1);
        request.onupgradeneeded = () => request.result.createObjectStore('tokens', {keyPath: 'id'});
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const database = request.result;
            const transaction = database.transaction('tokens', 'readwrite');
            transaction.objectStore('tokens').put({id: 1, value});
            transaction.oncomplete = () => { database.close(); resolve(); };
            transaction.onerror = () => reject(transaction.error);
        };
    });
    if (value !== 'saved') {
        document.cookie = 'stale=true; Path=/; SameSite=Lax';
        localStorage.setItem('stale', 'true');
        await new Promise((resolve, reject) => {
            const request = indexedDB.open('stale', 1);
            request.onerror = () => reject(request.error);
            request.onsuccess = () => { request.result.close(); resolve(); };
        });
    }
}"""
READ_STATE = """async () => {
    const value = await new Promise((resolve, reject) => {
        const request = indexedDB.open('auth', 1);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const database = request.result;
            const transaction = database.transaction('tokens');
            const record = transaction.objectStore('tokens').get(1);
            record.onsuccess = () => resolve(record.result);
            record.onerror = () => reject(record.error);
            transaction.oncomplete = () => database.close();
        };
    });
    return {
        cookies: document.cookie,
        localStorage: {...localStorage},
        indexedDB: value,
        databases: (await indexedDB.databases()).map(database => database.name).sort()
    };
}"""
SAVED_STATE = {
    "cookies": "login=saved",
    "localStorage": {"login": "saved"},
    "indexedDB": {"id": 1, "value": "saved"},
    "databases": ["auth"],
}


def _options(**kwargs: Any) -> dict[str, Any]:
    return {"executable_path": getenv("SCRAPLING_EXECUTABLE_PATH"), "google_search": False, "retries": 1, **kwargs}


def _check_json(path: Path, native_state: dict[str, Any]) -> None:
    state = loads(path.read_text())
    assert state == native_state
    assert [(cookie["name"], cookie["value"]) for cookie in state["cookies"]] == [("login", "saved")]
    assert len(state["origins"]) == 1
    origin = state["origins"][0]
    assert origin["origin"] == URL.rstrip("/")
    assert origin["localStorage"] == [{"name": "login", "value": "saved"}]
    assert origin["indexedDB"][0]["name"] == "auth"
    assert "sessionStorage" not in origin


@pytest.mark.browser
@pytest.mark.parametrize("session_type", [StealthySession])
def test_sync_state_round_trip(session_type: Any, tmp_path: Path) -> None:
    path, native_path = tmp_path / "state.json", tmp_path / "native.json"
    with session_type(**_options()) as source:
        source.context.route("http://state.test/**", lambda route: route.fulfill(body=HTML, content_type="text/html"))
        source.fetch(URL)
        source.page_pool.pages[0].page.evaluate(WRITE_STATE, "saved")
        assert source.save_state(path) is None
        _check_json(path, source.context.storage_state(path=native_path, indexed_db=True))
    for method in (source.save_state, source.load_state):
        with pytest.raises(RuntimeError, match=STATE_ERROR):
            method(path)
    with session_type(**_options()) as restored:
        restored.context.route("http://state.test/**", lambda route: route.fulfill(body=HTML, content_type="text/html"))
        assert restored.load_state(str(path)) is None
        restored.fetch(URL)
        page = restored.page_pool.pages[0].page
        assert page.evaluate(READ_STATE) == SAVED_STATE
        assert page.evaluate("sessionStorage.length") == 0
        page.evaluate(WRITE_STATE, "changed")
        changed = page.evaluate(READ_STATE)
        assert changed["indexedDB"]["value"] == "changed" and changed["databases"] == ["auth", "stale"]
        assert "stale" in changed["cookies"] and "stale" in changed["localStorage"]
        restored.load_state(native_path)
        assert page.url == URL and not page.is_closed()
        assert page.evaluate("sessionStorage.getItem('temporary')") == "changed"
        restored.fetch(URL)
        assert page.evaluate(READ_STATE) == SAVED_STATE
        assert restored.save_state(str(path)) is None
        _check_json(path, loads(native_path.read_text()))


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncStealthySession])
async def test_async_state_round_trip(session_type: Any, tmp_path: Path) -> None:
    async def route_page(route: Any) -> None:
        await route.fulfill(body=HTML, content_type="text/html")

    path, native_path = tmp_path / "state.json", tmp_path / "native.json"
    async with session_type(**_options()) as source:
        await source.context.route("http://state.test/**", route_page)
        await source.fetch(URL)
        await source.page_pool.pages[0].page.evaluate(WRITE_STATE, "saved")
        assert await source.save_state(path) is None
        _check_json(path, await source.context.storage_state(path=native_path, indexed_db=True))
    for method in (source.save_state, source.load_state):
        with pytest.raises(RuntimeError, match=STATE_ERROR):
            await method(path)
    async with session_type(**_options()) as restored:
        await restored.context.route("http://state.test/**", route_page)
        assert await restored.load_state(str(path)) is None
        await restored.fetch(URL)
        page = restored.page_pool.pages[0].page
        assert await page.evaluate(READ_STATE) == SAVED_STATE
        assert await page.evaluate("sessionStorage.length") == 0
        await page.evaluate(WRITE_STATE, "changed")
        changed = await page.evaluate(READ_STATE)
        assert changed["indexedDB"]["value"] == "changed" and changed["databases"] == ["auth", "stale"]
        assert "stale" in changed["cookies"] and "stale" in changed["localStorage"]
        await restored.load_state(native_path)
        assert page.url == URL and not page.is_closed()
        assert await page.evaluate("sessionStorage.getItem('temporary')") == "changed"
        await restored.fetch(URL)
        assert await page.evaluate(READ_STATE) == SAVED_STATE
        assert await restored.save_state(str(path)) is None
        _check_json(path, loads(native_path.read_text()))


@pytest.mark.browser
@pytest.mark.parametrize("session_type", [StealthySession])
def test_sync_state_file_errors(session_type: Any, tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{")
    with session_type(**_options()) as session:
        session.context.add_cookies([{"name": "kept", "value": "true", "url": URL}])
        for path, error in ((tmp_path / "missing.json", FileNotFoundError), (invalid, JSONDecodeError)):
            with pytest.raises(error):
                session.load_state(path)
        assert [(cookie["name"], cookie["value"]) for cookie in session.context.cookies()] == [("kept", "true")]
        with pytest.raises(FileNotFoundError):
            session.save_state(tmp_path / "missing" / "state.json")
        with pytest.raises(IsADirectoryError):
            session.save_state("")


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncStealthySession])
async def test_async_state_file_errors(session_type: Any, tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{")
    async with session_type(**_options()) as session:
        await session.context.add_cookies([{"name": "kept", "value": "true", "url": URL}])
        for path, error in ((tmp_path / "missing.json", FileNotFoundError), (invalid, JSONDecodeError)):
            with pytest.raises(error):
                await session.load_state(path)
        assert [(cookie["name"], cookie["value"]) for cookie in await session.context.cookies()] == [("kept", "true")]
        with pytest.raises(FileNotFoundError):
            await session.save_state(tmp_path / "missing" / "state.json")
        with pytest.raises(IsADirectoryError):
            await session.save_state("")


@pytest.mark.parametrize("session_type", [StealthySession])
def test_sync_state_before_start(session_type: Any, tmp_path: Path) -> None:
    session = session_type(**_options())
    for method in (session.save_state, session.load_state):
        with pytest.raises(RuntimeError, match=STATE_ERROR):
            method(tmp_path / "state.json")


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncStealthySession])
async def test_async_state_before_start(session_type: Any, tmp_path: Path) -> None:
    session = session_type(**_options())
    for method in (session.save_state, session.load_state):
        with pytest.raises(RuntimeError, match=STATE_ERROR):
            await method(tmp_path / "state.json")


@pytest.mark.browser
@pytest.mark.parametrize("session_type", [StealthySession])
def test_sync_state_with_proxy_rotation(session_type: Any, tmp_path: Path) -> None:
    with session_type(**_options(proxy_rotator=ProxyRotator(["http://127.0.0.1:1"]))) as session:
        for method in (session.save_state, session.load_state):
            with pytest.raises(RuntimeError, match=STATE_ERROR):
                method(tmp_path / "state.json")


@pytest.mark.browser
@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [AsyncStealthySession])
async def test_async_state_with_proxy_rotation(session_type: Any, tmp_path: Path) -> None:
    async with session_type(**_options(proxy_rotator=ProxyRotator(["http://127.0.0.1:1"]))) as session:
        for method in (session.save_state, session.load_state):
            with pytest.raises(RuntimeError, match=STATE_ERROR):
                await method(tmp_path / "state.json")
