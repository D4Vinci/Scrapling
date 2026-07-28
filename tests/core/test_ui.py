import json
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from scrapling.core.ui import ScraplingWebUI, UIJobStore, UIRequestError
from scrapling.engines.toolbelt.custom import Response


@pytest.fixture
def sample_response():
    return Response(
        url="https://example.com/products",
        content="""
        <html><head><title>Products</title></head><body>
          <article class="product">Keyboard</article>
          <article class="product">Mouse</article>
        </body></html>
        """,
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )


@pytest.fixture
def web_ui(tmp_path):
    ui = ScraplingWebUI(database=str(tmp_path / "ui.db"))
    ui._validate_url = lambda url: None
    return ui


class TestUIJobStore:
    def test_save_list_and_get_job(self, tmp_path):
        store = UIJobStore(tmp_path / "jobs.db")
        job = {
            "id": "job123",
            "created_at": "2026-07-28T12:00:00+00:00",
            "url": "https://example.com",
            "final_url": "https://example.com/",
            "mode": "http",
            "selector": "h1",
            "selector_type": "css",
            "output_format": "text",
            "status": 200,
            "duration_ms": 12,
            "item_count": 1,
            "title": "Example",
            "result_json": json.dumps([{"index": 1, "value": "Example Domain"}]),
            "error": "",
        }

        store.save(job)

        assert store.list()[0]["id"] == "job123"
        assert store.get("job123")["items"] == [{"index": 1, "value": "Example Domain"}]
        assert store.get("missing") is None


class TestScraplingWebUI:
    def test_defaults_are_safe(self, tmp_path):
        ui = ScraplingWebUI(database=str(tmp_path / "ui.db"))

        with pytest.raises(UIRequestError, match="Private"):
            with patch("scrapling.core.ui.socket.getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 80))]):
                ui._validate_url("http://localhost")

        with pytest.raises(UIRequestError, match="complete"):
            ui._validate_url("file:///etc/passwd")

    @pytest.mark.asyncio
    async def test_extract_and_index_through_api(self, web_ui, sample_response):
        async with AsyncClient(transport=ASGITransport(app=web_ui.app), base_url="http://test") as client:
            with patch("scrapling.fetchers.Fetcher.get", return_value=sample_response):
                response = await client.post(
                    "/api/extract",
                    json={
                        "url": "https://example.com/products",
                        "mode": "http",
                        "selector": ".product",
                        "selector_type": "css",
                        "output_format": "text",
                    },
                )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == 200
            assert data["title"] == "Products"
            assert [item["value"] for item in data["items"]] == ["Keyboard", "Mouse"]

            history = (await client.get("/api/jobs")).json()["jobs"]
            assert history[0]["id"] == data["id"]
            assert history[0]["item_count"] == 2

            exported = await client.get(f"/api/jobs/{data['id']}/export?format=csv")
            assert exported.status_code == 200
            assert "Keyboard" in exported.text

    @pytest.mark.asyncio
    async def test_health_and_assets(self, web_ui):
        async with AsyncClient(transport=ASGITransport(app=web_ui.app), base_url="http://test") as client:
            health = await client.get("/api/health")
            index = await client.get("/")
            stylesheet = await client.get("/assets/style.css")

        assert health.json()["status"] == "ok"
        assert "Scrapling Studio" in index.text
        assert stylesheet.status_code == 200

    @pytest.mark.asyncio
    async def test_rejects_invalid_request(self, web_ui):
        async with AsyncClient(transport=ASGITransport(app=web_ui.app), base_url="http://test") as client:
            response = await client.post("/api/extract", json={"url": "https://example.com", "mode": "unknown"})

        assert response.status_code == 400
        assert "Unknown fetching mode" in response.json()["error"]
