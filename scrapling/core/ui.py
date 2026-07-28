"""Local Web UI for interactive scraping and indexed extraction history."""

from __future__ import annotations

import csv
import io
import ipaddress
import json
import socket
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from uuid import uuid4

from markdownify import markdownify
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

from scrapling import __version__


class UIRequestError(ValueError):
    """An invalid or unsafe Web UI request."""


class UIJobStore:
    """Persist extraction jobs in a small local SQLite database."""

    def __init__(self, database: str | Path):
        self.database = Path(database).expanduser().resolve()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Create a configured database connection."""
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        """Create the job table and indexes when they do not exist."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ui_jobs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    url TEXT NOT NULL,
                    final_url TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    selector TEXT NOT NULL,
                    selector_type TEXT NOT NULL,
                    output_format TEXT NOT NULL,
                    status INTEGER NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    item_count INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    error TEXT NOT NULL DEFAULT ''
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS ui_jobs_created_at ON ui_jobs(created_at DESC)")
            connection.execute("CREATE INDEX IF NOT EXISTS ui_jobs_url ON ui_jobs(url)")

    def save(self, job: Dict[str, Any]) -> None:
        """Insert an extraction job."""
        fields = (
            "id",
            "created_at",
            "url",
            "final_url",
            "mode",
            "selector",
            "selector_type",
            "output_format",
            "status",
            "duration_ms",
            "item_count",
            "title",
            "result_json",
            "error",
        )
        with self._connect() as connection:
            connection.execute(
                f"INSERT INTO ui_jobs ({', '.join(fields)}) VALUES ({', '.join('?' for _ in fields)})",
                tuple(job[field] for field in fields),
            )

    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent jobs without their potentially large results."""
        safe_limit = max(1, min(limit, 200))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, url, final_url, mode, selector, selector_type,
                       output_format, status, duration_ms, item_count, title, error
                FROM ui_jobs ORDER BY created_at DESC LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Return one stored job, including extracted results."""
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM ui_jobs WHERE id = ?", (job_id,)).fetchone()
        if not row:
            return None
        job = dict(row)
        job["items"] = json.loads(job.pop("result_json"))
        return job


class ScraplingWebUI:
    """Serve a local UI backed by Scrapling's existing fetchers and parser."""

    modes = frozenset(("http", "dynamic", "stealth"))
    selector_types = frozenset(("css", "xpath"))
    output_formats = frozenset(("text", "html", "markdown"))

    def __init__(self, database: str | None = None, allow_private_targets: bool = False):
        default_database = Path.home() / ".scrapling" / "ui.db"
        self.store = UIJobStore(database or default_database)
        self.allow_private_targets = allow_private_targets
        self.assets = Path(__file__).parent.parent / "webui"
        self.app = Starlette(
            debug=False,
            routes=[
                Route("/", self.index),
                Route("/assets/app.js", self.javascript),
                Route("/assets/style.css", self.stylesheet),
                Route("/api/health", self.health),
                Route("/api/jobs", self.jobs, methods=["GET"]),
                Route("/api/jobs/{job_id:str}", self.job, methods=["GET"]),
                Route("/api/jobs/{job_id:str}/export", self.export, methods=["GET"]),
                Route("/api/extract", self.extract, methods=["POST"]),
            ],
        )

    async def index(self, request: Request) -> HTMLResponse:
        """Return the Web UI shell."""
        return HTMLResponse((self.assets / "index.html").read_text(encoding="utf-8"))

    async def javascript(self, request: Request) -> Response:
        """Return the UI JavaScript."""
        return Response((self.assets / "app.js").read_text(encoding="utf-8"), media_type="application/javascript")

    async def stylesheet(self, request: Request) -> Response:
        """Return the UI stylesheet."""
        return Response((self.assets / "style.css").read_text(encoding="utf-8"), media_type="text/css")

    async def health(self, request: Request) -> JSONResponse:
        """Return service health and version information."""
        return JSONResponse({"status": "ok", "service": "Scrapling Web UI", "version": __version__})

    async def jobs(self, request: Request) -> JSONResponse:
        """Return recent indexed extraction jobs."""
        try:
            limit = int(request.query_params.get("limit", "50"))
        except ValueError:
            limit = 50
        return JSONResponse({"jobs": self.store.list(limit)})

    async def job(self, request: Request) -> JSONResponse:
        """Return a single indexed extraction job."""
        stored_job = self.store.get(request.path_params["job_id"])
        if stored_job is None:
            return JSONResponse({"error": "Job not found"}, status_code=404)
        return JSONResponse(stored_job)

    async def extract(self, request: Request) -> JSONResponse:
        """Fetch a URL, extract selected values, and index the result."""
        try:
            payload = await request.json()
            normalized = self._normalize_payload(payload)
            result = self._run_extraction(normalized)
            self.store.save(result["stored_job"])
            return JSONResponse(result["response"])
        except (UIRequestError, json.JSONDecodeError) as error:
            return JSONResponse({"error": str(error)}, status_code=400)
        except Exception as error:
            return JSONResponse({"error": f"{type(error).__name__}: {error}"}, status_code=502)

    async def export(self, request: Request) -> Response:
        """Export a stored job as JSON or CSV."""
        stored_job = self.store.get(request.path_params["job_id"])
        if stored_job is None:
            return JSONResponse({"error": "Job not found"}, status_code=404)

        export_format = request.query_params.get("format", "json").lower()
        if export_format == "json":
            content = json.dumps(stored_job, indent=2, ensure_ascii=False)
            media_type, suffix = "application/json", "json"
        elif export_format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=("index", "value"))
            writer.writeheader()
            writer.writerows({"index": item["index"], "value": item["value"]} for item in stored_job["items"])
            content, media_type, suffix = output.getvalue(), "text/csv", "csv"
        else:
            return JSONResponse({"error": "Supported export formats are json and csv"}, status_code=400)

        return Response(
            content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="scrapling-{stored_job["id"]}.{suffix}"'},
        )

    def _normalize_payload(self, payload: Any) -> Dict[str, Any]:
        """Validate and normalize an extraction request body."""
        if not isinstance(payload, dict):
            raise UIRequestError("Request body must be a JSON object")

        url = str(payload.get("url", "")).strip()
        mode = str(payload.get("mode", "http")).lower()
        selector = str(payload.get("selector", "")).strip()
        selector_type = str(payload.get("selector_type", "css")).lower()
        output_format = str(payload.get("output_format", "text")).lower()

        if mode not in self.modes:
            raise UIRequestError(f"Unknown fetching mode: {mode}")
        if selector_type not in self.selector_types:
            raise UIRequestError(f"Unknown selector type: {selector_type}")
        if output_format not in self.output_formats:
            raise UIRequestError(f"Unknown output format: {output_format}")
        self._validate_url(url)

        return {
            "url": url,
            "mode": mode,
            "selector": selector,
            "selector_type": selector_type,
            "output_format": output_format,
            "headless": bool(payload.get("headless", True)),
            "network_idle": bool(payload.get("network_idle", False)),
            "timeout": max(1, min(int(payload.get("timeout", 30)), 120)),
        }

    def _validate_url(self, url: str) -> None:
        """Reject unsupported URLs and private-network targets by default."""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise UIRequestError("Enter a complete http:// or https:// URL")
        if self.allow_private_targets:
            return

        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port or 80)}
        except socket.gaierror as error:
            raise UIRequestError(f"Could not resolve URL host: {error}") from error

        for address in addresses:
            ip = ipaddress.ip_address(address)
            if not ip.is_global:
                raise UIRequestError("Private, loopback, and local-network targets are blocked by default")

    def _run_extraction(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform one synchronous extraction with the selected fetcher."""
        from time import monotonic

        started = monotonic()
        if options["mode"] == "http":
            from scrapling.fetchers import Fetcher

            response = Fetcher.get(options["url"], timeout=options["timeout"])
        elif options["mode"] == "dynamic":
            from scrapling.fetchers import DynamicFetcher

            response = DynamicFetcher.fetch(
                options["url"],
                headless=options["headless"],
                network_idle=options["network_idle"],
                timeout=options["timeout"] * 1000,
            )
        else:
            from scrapling.fetchers import StealthyFetcher

            response = StealthyFetcher.fetch(
                options["url"],
                headless=options["headless"],
                network_idle=options["network_idle"],
                timeout=options["timeout"] * 1000,
            )

        selected: List[Any] = [response]
        if options["selector"]:
            selector_method = response.css if options["selector_type"] == "css" else response.xpath
            selected = list(selector_method(options["selector"]))

        items = [
            {
                "index": index,
                "value": self._serialize_node(node, options["output_format"]),
            }
            for index, node in enumerate(selected, 1)
        ]
        title = str(response.css("title::text").get(default=""))
        duration_ms = round((monotonic() - started) * 1000)
        job_id = uuid4().hex[:12]
        final_url = str(response.url)
        status = int(response.status)
        created_at = datetime.now(timezone.utc).isoformat()

        stored_job = {
            "id": job_id,
            "created_at": created_at,
            "url": options["url"],
            "final_url": final_url,
            "mode": options["mode"],
            "selector": options["selector"],
            "selector_type": options["selector_type"],
            "output_format": options["output_format"],
            "status": status,
            "duration_ms": duration_ms,
            "item_count": len(items),
            "title": title,
            "result_json": json.dumps(items, ensure_ascii=False),
            "error": "",
        }
        return {
            "stored_job": stored_job,
            "response": {
                **{key: value for key, value in stored_job.items() if key != "result_json"},
                "items": items,
            },
        }

    @staticmethod
    def _serialize_node(node: Any, output_format: str) -> str:
        """Convert a selected node to the requested display format."""
        if output_format == "html":
            return str(node.get(default=""))
        if output_format == "markdown":
            return markdownify(str(node.get(default=""))).strip()
        return str(node.get_all_text(separator=" ", strip=True))

    def serve(self, host: str = "127.0.0.1", port: int = 8001) -> None:
        """Start the Uvicorn server."""
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)
