import base64

import pytest
import pytest_httpbin

from scrapling.core.ai import (
    ScraplingMCPServer,
    ResponseModel,
    ScreenshotModel,
    SessionInfo,
    SessionCreatedModel,
    SessionClosedModel,
    _normalize_credentials,
)


@pytest_httpbin.use_class_based_httpbin
class TestMCPServer:
    """Test MCP server functionality"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_get_tool(self, server, test_url):
        """Test the get tool method"""
        result = await server.get(url=test_url, extraction_type="markdown")
        assert isinstance(result, ResponseModel)
        assert result.status == 200
        assert result.url == test_url

    @pytest.mark.asyncio
    async def test_bulk_get_tool(self, server, test_url):
        """Test the bulk_get tool method"""
        results = await server.bulk_get(urls=(test_url, test_url), extraction_type="html")

        assert len(results) == 2
        assert all(isinstance(r, ResponseModel) for r in results)

    @pytest.mark.asyncio
    async def test_fetch_tool(self, server, test_url):
        """Test the fetch tool method"""
        result = await server.fetch(url=test_url, headless=True)
        assert isinstance(result, ResponseModel)
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_bulk_fetch_tool(self, server, test_url):
        """Test the bulk_fetch tool method"""
        result = await server.bulk_fetch(urls=(test_url, test_url), headless=True)
        assert all(isinstance(r, ResponseModel) for r in result)

    @pytest.mark.asyncio
    async def test_stealthy_fetch_tool(self, server, test_url):
        """Test the stealthy_fetch tool method"""
        result = await server.stealthy_fetch(url=test_url, headless=True)
        assert isinstance(result, ResponseModel)
        assert result.status == 200

    @pytest.mark.asyncio
    async def test_bulk_stealthy_fetch_tool(self, server, test_url):
        """Test the bulk_stealthy_fetch tool method"""
        result = await server.bulk_stealthy_fetch(urls=(test_url, test_url), headless=True)
        assert all(isinstance(r, ResponseModel) for r in result)


@pytest_httpbin.use_class_based_httpbin
class TestSessionManagement:
    """Test persistent browser session management"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_open_and_close_session(self, server):
        """Test opening and closing a dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True)
        assert isinstance(result, SessionCreatedModel)
        assert result.session_type == "dynamic"
        assert result.is_alive is True
        session_id = result.session_id

        # Close the session
        closed = await server.close_session(session_id)
        assert isinstance(closed, SessionClosedModel)
        assert closed.session_id == session_id

    @pytest.mark.asyncio
    async def test_list_sessions(self, server):
        """Test listing sessions"""
        # Initially empty
        sessions = await server.list_sessions()
        assert sessions == []

        # Open a session
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        # List should show it
        sessions = await server.list_sessions()
        assert len(sessions) == 1
        assert isinstance(sessions[0], SessionInfo)
        assert sessions[0].session_id == session_id
        assert sessions[0].session_type == "dynamic"
        assert sessions[0].is_alive is True

        # Cleanup
        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_fetch_with_session(self, server, test_url):
        """Test fetching with a persistent dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        # Fetch using the session
        response = await server.fetch(url=test_url, session_id=session_id)
        assert isinstance(response, ResponseModel)
        assert response.status == 200

        # Fetch again with the same session (reuse)
        response2 = await server.fetch(url=test_url, session_id=session_id)
        assert isinstance(response2, ResponseModel)
        assert response2.status == 200

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_bulk_fetch_with_session(self, server, test_url):
        """Test bulk fetching with a persistent dynamic session"""
        result = await server.open_session(session_type="dynamic", headless=True, max_pages=5)
        session_id = result.session_id

        responses = await server.bulk_fetch(urls=[test_url, test_url], session_id=session_id)
        assert len(responses) == 2
        assert all(isinstance(r, ResponseModel) for r in responses)

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_session_type_mismatch(self, server, test_url):
        """Test that using a dynamic session with stealthy_fetch raises an error"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id

        with pytest.raises(ValueError, match="'dynamic' session"):
            await server.stealthy_fetch(url=test_url, session_id=session_id)

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, server):
        """Test closing a session that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.close_session("nonexistent")

    @pytest.mark.asyncio
    async def test_fetch_with_nonexistent_session(self, server, test_url):
        """Test fetching with a session ID that doesn't exist"""
        with pytest.raises(ValueError, match="not found"):
            await server.fetch(url=test_url, session_id="nonexistent")

    @pytest.mark.asyncio
    async def test_fetch_with_closed_session(self, server, test_url):
        """Test fetching with a session that has been closed"""
        result = await server.open_session(session_type="dynamic", headless=True)
        session_id = result.session_id
        await server.close_session(session_id)

        with pytest.raises(ValueError, match="not found"):
            await server.fetch(url=test_url, session_id=session_id)


class TestNormalizeCredentials:
    """Test the _normalize_credentials helper"""

    def test_none_returns_none(self):
        assert _normalize_credentials(None) is None

    def test_empty_dict_returns_none(self):
        assert _normalize_credentials({}) is None

    def test_valid_credentials_returns_tuple(self):
        result = _normalize_credentials({"username": "user", "password": "pass"})
        assert result == ("user", "pass")

    def test_missing_password_raises(self):
        with pytest.raises(ValueError, match="password"):
            _normalize_credentials({"username": "user"})

    def test_missing_username_raises(self):
        with pytest.raises(ValueError, match="username"):
            _normalize_credentials({"password": "pass"})


@pytest_httpbin.use_class_based_httpbin
class TestScreenshot:
    """Test MCP screenshot functionality"""

    @pytest.fixture(scope="class")
    def test_url(self, httpbin):
        return f"{httpbin.url}/html"

    @pytest.fixture
    def server(self):
        return ScraplingMCPServer()

    @pytest.mark.asyncio
    async def test_screenshot_ad_hoc_png(self, server, test_url):
        """Test taking a PNG screenshot without a session (ad-hoc browser)"""
        result = await server.screenshot(url=test_url, image_type="png", headless=True)
        assert isinstance(result, ScreenshotModel)
        assert result.image_type == "png"
        assert result.full_page is False
        # Verify valid base64 that decodes to a PNG
        raw = base64.b64decode(result.image_data)
        assert raw[:4] == b"\x89PNG"

    @pytest.mark.asyncio
    async def test_screenshot_ad_hoc_jpeg(self, server, test_url):
        """Test taking a JPEG screenshot"""
        result = await server.screenshot(url=test_url, image_type="jpeg", quality=80, headless=True)
        assert isinstance(result, ScreenshotModel)
        assert result.image_type == "jpeg"
        raw = base64.b64decode(result.image_data)
        assert raw[:2] == b"\xff\xd8"  # JPEG magic bytes

    @pytest.mark.asyncio
    async def test_screenshot_full_page(self, server, test_url):
        """Test full-page screenshot"""
        result = await server.screenshot(url=test_url, full_page=True, headless=True)
        assert isinstance(result, ScreenshotModel)
        assert result.full_page is True
        assert len(result.image_data) > 0

    @pytest.mark.asyncio
    async def test_screenshot_with_session(self, server, test_url):
        """Test screenshot using a persistent session"""
        session = await server.open_session(session_type="dynamic", headless=True)
        session_id = session.session_id

        result = await server.screenshot(url=test_url, session_id=session_id)
        assert isinstance(result, ScreenshotModel)
        raw = base64.b64decode(result.image_data)
        assert raw[:4] == b"\x89PNG"

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_screenshot_with_stealthy_session(self, server, test_url):
        """Test screenshot using a stealthy session"""
        session = await server.open_session(session_type="stealthy", headless=True)
        session_id = session.session_id

        result = await server.screenshot(url=test_url, session_id=session_id)
        assert isinstance(result, ScreenshotModel)
        assert len(result.image_data) > 0

        await server.close_session(session_id)

    @pytest.mark.asyncio
    async def test_screenshot_nonexistent_session(self, server, test_url):
        """Test screenshot with invalid session ID raises error"""
        with pytest.raises(ValueError, match="not found"):
            await server.screenshot(url=test_url, session_id="nonexistent")
