"""Tests for the persistent seen-set (`SeenStore`) and its use by the scheduler and engine."""

import sqlite3
from pathlib import Path

import pytest

from scrapling.spiders.engine import CrawlerEngine
from scrapling.spiders.request import Request
from scrapling.spiders.scheduler import Scheduler
from scrapling.spiders.seen_store import SeenStore
from scrapling.spiders.session import SessionManager
from scrapling.spiders.spider import Spider
from scrapling.engines.toolbelt.custom import Response
from scrapling.core._types import Any, Dict, List, AsyncGenerator


FEED_URL = "https://example.com/feed"


class FakeSession:
    """Serves every URL with an empty page and records which URLs were fetched."""

    def __init__(self, fetched: List[str]):
        self.fetched = fetched
        self._is_alive = False

    async def __aenter__(self):
        self._is_alive = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False

    async def fetch(self, url: str, **kwargs: Any) -> Response:
        self.fetched.append(url)
        return Response(
            url=url, content=b"<html></html>", status=200, reason="OK", cookies={}, headers={}, request_headers={}
        )


class MonitorSpider(Spider):
    """A feed that links to articles: the feed yields requests, each article yields an item."""

    name = "monitor"
    start_urls = [FEED_URL]
    persistent_seen = True

    def __init__(self, articles: List[str], seen_file: Path, **kwargs: Any):
        self.articles = articles
        self.persistent_seen_file = str(seen_file)
        self.fetched: List[str] = []
        super().__init__(**kwargs)

    def configure_sessions(self, manager: SessionManager) -> None:
        manager.add("default", FakeSession(self.fetched))

    async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        for path in self.articles:
            yield response.follow(path, callback=self.parse_article)

    async def parse_article(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
        yield {"url": response.url}


class TestSeenStore:
    def test_fingerprints_survive_reopening(self, tmp_path: Path):
        path = tmp_path / "seen.db"
        store = SeenStore(path)
        store.add(b"\x01" * 20)
        store.add(b"\x01" * 20)
        store.add(b"\x02" * 20)
        store.close()

        reopened = SeenStore(path)
        assert b"\x01" * 20 in reopened
        assert b"\x02" * 20 in reopened
        assert b"\x03" * 20 not in reopened
        assert len(reopened) == 2
        reopened.close()

    def test_open_creates_parent_dirs(self, tmp_path: Path):
        path = tmp_path / "nested" / "dir" / "seen.db"
        store = SeenStore(path)
        store.open()
        assert path.exists()
        store.close()

    def test_clear(self, tmp_path: Path):
        store = SeenStore(tmp_path / "seen.db")
        store.add(b"\x01" * 20)
        store.clear()
        assert len(store) == 0
        store.close()

    def test_close_is_idempotent(self, tmp_path: Path):
        store = SeenStore(tmp_path / "seen.db")
        store.close()
        store.open()
        store.close()
        store.close()

    def test_database_errors_dont_stop_the_crawl(self, tmp_path: Path):
        class BrokenConnection:
            def execute(self, *args: Any) -> Any:
                raise sqlite3.OperationalError("database is locked")

        store = SeenStore(tmp_path / "seen.db")
        store._connection = BrokenConnection()  # type: ignore[assignment]
        store.add(b"\x01" * 20)
        # An unreadable store means a page is fetched again, never that it's skipped
        assert b"\x01" * 20 not in store


class TestSchedulerWithSeenStore:
    @pytest.mark.asyncio
    async def test_requests_from_previous_runs_are_dropped(self, tmp_path: Path):
        store = SeenStore(tmp_path / "seen.db")
        old = Request("https://example.com/old", sid="default")
        store.add(old.update_fingerprint())

        scheduler = Scheduler(seen_store=store)
        assert await scheduler.enqueue(Request("https://example.com/old", sid="default")) is False
        assert await scheduler.enqueue(Request("https://example.com/new", sid="default")) is True
        assert scheduler.previously_seen_count == 1
        assert len(scheduler) == 1
        store.close()

    @pytest.mark.asyncio
    async def test_dont_filter_bypasses_the_store(self, tmp_path: Path):
        store = SeenStore(tmp_path / "seen.db")
        store.add(Request("https://example.com/feed", sid="default").update_fingerprint())

        scheduler = Scheduler(seen_store=store)
        assert await scheduler.enqueue(Request("https://example.com/feed", sid="default", dont_filter=True)) is True
        assert scheduler.previously_seen_count == 0
        store.close()

    @pytest.mark.asyncio
    async def test_repeats_in_the_same_run_count_as_duplicates(self, tmp_path: Path):
        store = SeenStore(tmp_path / "seen.db")
        store.add(Request("https://example.com/old", sid="default").update_fingerprint())

        scheduler = Scheduler(seen_store=store)
        await scheduler.enqueue(Request("https://example.com/old", sid="default"))
        await scheduler.enqueue(Request("https://example.com/old", sid="default"))
        assert scheduler.previously_seen_count == 1
        store.close()

    @pytest.mark.asyncio
    async def test_store_fingerprints_follow_the_scheduler_settings(self, tmp_path: Path):
        store = SeenStore(tmp_path / "seen.db")
        store.add(Request("https://example.com/page#top", sid="default").update_fingerprint(keep_fragments=True))

        assert not await Scheduler(seen_store=store, keep_fragments=True).enqueue(
            Request("https://example.com/page#top", sid="default")
        )
        assert await Scheduler(seen_store=store, keep_fragments=True).enqueue(
            Request("https://example.com/page#bottom", sid="default")
        )
        store.close()


class TestPersistentSeenCrawl:
    def test_second_run_only_fetches_new_articles(self, tmp_path: Path):
        seen_file = tmp_path / "seen.db"

        first = MonitorSpider(["/a1", "/a2"], seen_file)
        result = first.start()
        assert sorted(first.fetched) == ["https://example.com/a1", "https://example.com/a2", FEED_URL]
        assert len(result.items) == 2
        assert result.stats.previously_seen_count == 0

        second = MonitorSpider(["/a1", "/a2", "/a3"], seen_file)
        result = second.start()
        # The feed yielded no items, so it's fetched again; only the new article follows it
        assert second.fetched == [FEED_URL, "https://example.com/a3"]
        assert [item["url"] for item in result.items] == ["https://example.com/a3"]
        assert result.stats.previously_seen_count == 2
        assert result.stats.to_dict()["previously_seen_count"] == 2

    def test_page_that_yields_items_itself_needs_dont_filter_to_be_rechecked(self, tmp_path: Path):
        class FeedItemsSpider(MonitorSpider):
            async def parse(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield {"feed": response.url}

        seen_file = tmp_path / "seen.db"
        FeedItemsSpider([], seen_file).start()

        skipped = FeedItemsSpider([], seen_file)
        result = skipped.start()
        assert skipped.fetched == []
        assert result.stats.previously_seen_count == 1

        class RecheckedFeedSpider(FeedItemsSpider):
            async def start_requests(self) -> AsyncGenerator[Request, None]:
                yield Request(FEED_URL, sid="default", dont_filter=True)

        rechecked = RecheckedFeedSpider([], seen_file)
        rechecked.start()
        assert rechecked.fetched == [FEED_URL]

    def test_failed_callback_is_fetched_again(self, tmp_path: Path):
        class FlakyArticleSpider(MonitorSpider):
            async def parse_article(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield {"url": response.url}
                raise RuntimeError("parser broke halfway")

        seen_file = tmp_path / "seen.db"
        FlakyArticleSpider(["/a1"], seen_file).start()

        retry = MonitorSpider(["/a1"], seen_file)
        retry.start()
        assert retry.fetched == [FEED_URL, "https://example.com/a1"]

    def test_page_without_items_is_fetched_again(self, tmp_path: Path):
        class EmptyArticleSpider(MonitorSpider):
            async def parse_article(self, response: Response) -> AsyncGenerator[Dict[str, Any] | Request | None, None]:
                yield None

        seen_file = tmp_path / "seen.db"
        EmptyArticleSpider(["/a1"], seen_file).start()

        retry = MonitorSpider(["/a1"], seen_file)
        retry.start()
        assert retry.fetched == [FEED_URL, "https://example.com/a1"]

    def test_items_dropped_by_on_scraped_item_still_mark_the_page(self, tmp_path: Path):
        class DroppingSpider(MonitorSpider):
            async def on_scraped_item(self, item: Dict[str, Any]) -> Dict[str, Any] | None:
                return None

        seen_file = tmp_path / "seen.db"
        DroppingSpider(["/a1"], seen_file).start()

        second = MonitorSpider(["/a1"], seen_file)
        second.start()
        assert second.fetched == [FEED_URL]

    def test_store_is_closed_after_the_crawl(self, tmp_path: Path):
        spider = MonitorSpider(["/a1"], tmp_path / "seen.db")
        engine = CrawlerEngine(spider, spider._session_manager)
        assert engine._seen_store is not None

        import anyio

        anyio.run(engine.crawl)
        assert engine._seen_store._connection is None
        assert len(engine._seen_store) == 1
        engine._seen_store.close()

    def test_disabled_by_default(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)

        class PlainSpider(MonitorSpider):
            persistent_seen = False

        PlainSpider(["/a1"], tmp_path / "seen.db").start()
        second = PlainSpider(["/a1"], tmp_path / "seen.db")
        second.start()
        assert second.fetched == [FEED_URL, "https://example.com/a1"]
        assert not (tmp_path / "seen.db").exists()
        assert not (tmp_path / ".scrapling_seen").exists()

    def test_default_location(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.chdir(tmp_path)

        class DefaultLocationSpider(MonitorSpider):
            def __init__(self, *args: Any, **kwargs: Any):
                super().__init__(*args, **kwargs)
                self.persistent_seen_file = None

        DefaultLocationSpider(["/a1"], tmp_path / "unused.db").start()
        assert (tmp_path / ".scrapling_seen" / "monitor.db").exists()

    def test_disabled_in_development_mode(self, tmp_path: Path):
        class DevSpider(MonitorSpider):
            development_mode = True

            def __init__(self, *args: Any, **kwargs: Any):
                self.development_cache_dir = str(tmp_path / "cache")
                super().__init__(*args, **kwargs)

        spider = DevSpider(["/a1"], tmp_path / "seen.db")
        assert CrawlerEngine(spider, spider._session_manager)._seen_store is None

        DevSpider(["/a1"], tmp_path / "seen.db").start()
        replay = DevSpider(["/a1"], tmp_path / "seen.db")
        result = replay.start()
        # Replayed from the response cache, and nothing was skipped as already seen
        assert replay.fetched == []
        assert result.stats.cache_hits == 2
        assert len(result.items) == 1
        assert not (tmp_path / "seen.db").exists()
