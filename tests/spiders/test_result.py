"""Tests for the result module (ItemList, CrawlStats, CrawlResult)."""

import csv
import json
import tempfile
from pathlib import Path
from xml.etree import ElementTree  # nosec B405 - only used to read back files these tests just wrote

import pytest

from scrapling.spiders.result import ItemList, CrawlStats, CrawlResult


def _read_xml(path):
    """Parse a file the test itself just wrote."""
    return ElementTree.parse(path).getroot()  # nosec B314 - trusted local file, not untrusted input


class TestItemList:
    """Test ItemList functionality."""

    def test_itemlist_is_list(self):
        """Test that ItemList is a list subclass."""
        items = ItemList()

        assert isinstance(items, list)

    def test_itemlist_basic_operations(self):
        """Test basic list operations work."""
        items = ItemList()

        items.append({"id": 1})
        items.append({"id": 2})

        assert len(items) == 2
        assert items[0] == {"id": 1}

    def test_to_json_creates_file(self):
        """Test to_json creates JSON file."""
        items = ItemList()
        items.append({"name": "test", "value": 123})
        items.append({"name": "test2", "value": 456})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.json"
            items.to_json(path)

            assert path.exists()

            content = json.loads(path.read_text())
            assert len(content) == 2
            assert content[0]["name"] == "test"

    def test_to_json_creates_parent_directory(self):
        """Test to_json creates parent directories."""
        items = ItemList()
        items.append({"data": "test"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dirs" / "output.json"
            items.to_json(path)

            assert path.exists()

    def test_to_json_with_indent(self):
        """Test to_json with indentation."""
        items = ItemList()
        items.append({"key": "value"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.json"
            items.to_json(path, indent=True)

            content = path.read_text()
            # Indented JSON should have newlines
            assert "\n" in content

    def test_to_csv_creates_file(self):
        """Test to_csv writes a header and one row per item."""
        items = ItemList()
        items.append({"name": "first", "price": 10})
        items.append({"name": "second", "price": 20})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.csv"
            items.to_csv(path)

            assert path.exists()

            rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
            assert len(rows) == 2
            assert rows[0] == {"name": "first", "price": "10"}
            assert rows[1]["name"] == "second"

    def test_to_csv_unions_the_keys_of_every_item(self):
        """Items with different keys must all be written, with the missing cells left empty."""
        items = ItemList()
        items.append({"name": "first"})
        items.append({"price": 20, "name": "second"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.csv"
            items.to_csv(path)

            reader = csv.DictReader(path.open(newline="", encoding="utf-8"))
            assert reader.fieldnames == ["name", "price"]
            rows = list(reader)
            assert rows[0] == {"name": "first", "price": ""}
            assert rows[1] == {"name": "second", "price": "20"}

    def test_to_csv_serializes_nested_values(self):
        items = ItemList()
        items.append({"name": "first", "tags": ["a", "b"], "meta": {"x": 1}, "empty": None})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.csv"
            items.to_csv(path)

            row = next(csv.DictReader(path.open(newline="", encoding="utf-8")))
            assert json.loads(row["tags"]) == ["a", "b"]
            assert json.loads(row["meta"]) == {"x": 1}
            assert row["empty"] == ""

    def test_to_csv_accepts_explicit_fields_and_delimiter(self):
        items = ItemList()
        items.append({"name": "first", "price": 10, "skipped": "yes"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.tsv"
            items.to_csv(path, fields=["price", "name"], delimiter="\t")

            lines = path.read_text(encoding="utf-8").splitlines()
            assert lines[0] == "price\tname"
            assert lines[1] == "10\tfirst"

    def test_to_csv_handles_no_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.csv"
            ItemList().to_csv(path)

            assert path.exists()
            assert path.read_text(encoding="utf-8").strip() == ""

    def test_to_csv_creates_parent_directory(self):
        items = ItemList()
        items.append({"data": "test"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "output.csv"
            items.to_csv(path)

            assert path.exists()

    def test_to_xml_creates_file(self):
        """Test to_xml writes one element per item with the keys as children."""
        items = ItemList()
        items.append({"name": "first", "price": 10})
        items.append({"name": "second", "price": 20})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.xml"
            items.to_xml(path)

            assert path.exists()

            root = _read_xml(path)
            assert root.tag == "items"
            assert len(root) == 2
            assert [child.tag for child in root] == ["item", "item"]
            assert root[0].find("name").text == "first"
            assert root[0].find("price").text == "10"

    def test_to_xml_custom_tags(self):
        items = ItemList()
        items.append({"name": "first"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.xml"
            items.to_xml(path, root_tag="products", item_tag="product")

            root = _read_xml(path)
            assert root.tag == "products"
            assert root[0].tag == "product"

    def test_to_xml_sanitizes_keys_that_are_not_valid_tags(self):
        """Scraped keys can be anything, but XML names can't"""
        items = ItemList()
        items.append({"product name": "first", "2nd": "x", "ok_key": "y"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.xml"
            items.to_xml(path)

            item = _read_xml(path)[0]
            tags = {child.tag: child for child in item}
            assert tags["product_name"].text == "first"
            assert tags["product_name"].get("name") == "product name"
            assert tags["_2nd"].get("name") == "2nd"
            assert tags["ok_key"].get("name") is None

    def test_to_xml_strips_characters_that_xml_forbids(self):
        """Control characters in scraped text would produce a file no parser can read"""
        items = ItemList()
        items.append({"text": "bad\x08char\x0bhere", "kept": "tab\tnewline\n"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.xml"
            items.to_xml(path)

            item = _read_xml(path)[0]
            assert item.find("text").text == "badcharhere"
            assert item.find("kept").text == "tab\tnewline\n"

    def test_to_xml_serializes_nested_values(self):
        items = ItemList()
        items.append({"tags": ["a", "b"], "meta": {"x": 1}, "empty": None})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.xml"
            items.to_xml(path)

            item = _read_xml(path)[0]
            assert json.loads(item.find("tags").text) == ["a", "b"]
            assert json.loads(item.find("meta").text) == {"x": 1}
            assert item.find("empty").text in (None, "")

    def test_to_xml_handles_no_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.xml"
            ItemList().to_xml(path)

            root = _read_xml(path)
            assert root.tag == "items"
            assert len(root) == 0

    def test_to_xml_creates_parent_directory(self):
        items = ItemList()
        items.append({"data": "test"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "output.xml"
            items.to_xml(path)

            assert path.exists()

    def test_to_jsonl_creates_file(self):
        """Test to_jsonl creates JSON Lines file."""
        items = ItemList()
        items.append({"id": 1, "name": "first"})
        items.append({"id": 2, "name": "second"})
        items.append({"id": 3, "name": "third"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            items.to_jsonl(path)

            assert path.exists()

            lines = path.read_text().strip().split("\n")
            assert len(lines) == 3

            # Each line should be valid JSON
            for line in lines:
                parsed = json.loads(line)
                assert "id" in parsed
                assert "name" in parsed

    def test_to_jsonl_one_object_per_line(self):
        """Test that JSONL has one JSON object per line."""
        items = ItemList()
        items.append({"line": 1})
        items.append({"line": 2})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            items.to_jsonl(path)

            lines = path.read_text().strip().split("\n")

            assert json.loads(lines[0])["line"] == 1
            assert json.loads(lines[1])["line"] == 2


class TestCrawlStats:
    """Test CrawlStats dataclass."""

    def test_default_values(self):
        """Test CrawlStats default values."""
        stats = CrawlStats()

        assert stats.requests_count == 0
        assert stats.concurrent_requests == 0
        assert stats.failed_requests_count == 0
        assert stats.response_bytes == 0
        assert stats.items_scraped == 0
        assert stats.items_dropped == 0
        assert stats.start_time == 0.0
        assert stats.end_time == 0.0
        assert stats.custom_stats == {}
        assert stats.response_status_count == {}
        assert stats.proxies == []

    def test_elapsed_seconds(self):
        """Test elapsed_seconds property."""
        stats = CrawlStats(start_time=100.0, end_time=150.0)

        assert stats.elapsed_seconds == 50.0

    def test_requests_per_second(self):
        """Test requests_per_second calculation."""
        stats = CrawlStats(
            requests_count=100,
            start_time=0.0,
            end_time=10.0,
        )

        assert stats.requests_per_second == 10.0

    def test_requests_per_second_zero_elapsed(self):
        """Test requests_per_second when elapsed is zero."""
        stats = CrawlStats(
            requests_count=100,
            start_time=0.0,
            end_time=0.0,
        )

        assert stats.requests_per_second == 0.0

    def test_increment_status(self):
        """Test increment_status method."""
        stats = CrawlStats()

        stats.increment_status(200)
        stats.increment_status(200)
        stats.increment_status(404)

        assert stats.response_status_count == {"status_200": 2, "status_404": 1}

    def test_increment_response_bytes(self):
        """Test increment_response_bytes method."""
        stats = CrawlStats()

        stats.increment_response_bytes("example.com", 1000)
        stats.increment_response_bytes("example.com", 500)
        stats.increment_response_bytes("other.com", 2000)

        assert stats.response_bytes == 3500
        assert stats.domains_response_bytes == {
            "example.com": 1500,
            "other.com": 2000,
        }

    def test_increment_requests_count(self):
        """Test increment_requests_count method."""
        stats = CrawlStats()

        stats.increment_requests_count("session1")
        stats.increment_requests_count("session1")
        stats.increment_requests_count("session2")

        assert stats.requests_count == 3
        assert stats.sessions_requests_count == {"session1": 2, "session2": 1}

    def test_to_dict(self):
        """Test to_dict method returns all stats."""
        stats = CrawlStats(
            items_scraped=10,
            items_dropped=2,
            requests_count=15,
            start_time=0.0,
            end_time=5.0,
        )
        stats.increment_status(200)

        result = stats.to_dict()

        assert result["items_scraped"] == 10
        assert result["items_dropped"] == 2
        assert result["requests_count"] == 15
        assert result["elapsed_seconds"] == 5.0
        assert result["requests_per_second"] == 3.0
        assert result["response_status_count"] == {"status_200": 1}

    def test_custom_stats(self):
        """Test custom_stats can be used."""
        stats = CrawlStats()
        stats.custom_stats["my_metric"] = 42
        stats.custom_stats["another"] = "value"

        assert stats.custom_stats["my_metric"] == 42
        assert stats.to_dict()["custom_stats"]["my_metric"] == 42


class TestCrawlResult:
    """Test CrawlResult dataclass."""

    def test_basic_creation(self):
        """Test basic CrawlResult creation."""
        stats = CrawlStats(items_scraped=5)
        items = ItemList()
        items.extend([{"id": i} for i in range(5)])

        result = CrawlResult(stats=stats, items=items)

        assert result.stats.items_scraped == 5
        assert len(result.items) == 5
        assert result.paused is False

    def test_completed_property_true_when_not_paused(self):
        """Test completed is True when not paused."""
        result = CrawlResult(
            stats=CrawlStats(),
            items=ItemList(),
            paused=False,
        )

        assert result.completed is True

    def test_completed_property_false_when_paused(self):
        """Test completed is False when paused."""
        result = CrawlResult(
            stats=CrawlStats(),
            items=ItemList(),
            paused=True,
        )

        assert result.completed is False

    def test_len_returns_item_count(self):
        """Test len returns number of items."""
        items = ItemList()
        items.extend([{"id": i} for i in range(10)])

        result = CrawlResult(stats=CrawlStats(), items=items)

        assert len(result) == 10

    def test_iter_yields_items(self):
        """Test iteration yields items."""
        items = ItemList()
        items.extend([{"id": 1}, {"id": 2}, {"id": 3}])

        result = CrawlResult(stats=CrawlStats(), items=items)

        collected = list(result)

        assert collected == [{"id": 1}, {"id": 2}, {"id": 3}]

    def test_result_with_stats(self):
        """Test CrawlResult with populated stats."""
        stats = CrawlStats(
            requests_count=100,
            items_scraped=50,
            failed_requests_count=5,
            start_time=0.0,
            end_time=10.0,
        )
        items = ItemList()

        result = CrawlResult(stats=stats, items=items)

        assert result.stats.requests_count == 100
        assert result.stats.items_scraped == 50
        assert result.stats.requests_per_second == 10.0


class TestCrawlResultIntegration:
    """Integration tests for result classes."""

    def test_full_workflow(self):
        """Test realistic workflow with all result classes."""
        # Simulate a crawl
        stats = CrawlStats(start_time=1000.0)

        # Simulate requests
        for _ in range(10):
            stats.increment_requests_count("default")
            stats.increment_status(200)
            stats.increment_response_bytes("example.com", 5000)

        # Simulate some failures
        stats.failed_requests_count = 2
        stats.blocked_requests_count = 1

        # Collect items
        items = ItemList()
        for i in range(8):
            items.append({"product_id": i, "name": f"Product {i}"})
            stats.items_scraped += 1

        # Finish crawl
        stats.end_time = 1005.0

        # Create result
        result = CrawlResult(stats=stats, items=items, paused=False)

        # Verify
        assert result.completed is True
        assert len(result) == 8
        assert result.stats.requests_count == 10
        assert result.stats.requests_per_second == 2.0
        assert result.stats.response_bytes == 50000
