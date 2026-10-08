"""Detection over the JSON response fixtures in ``tests/antibot/fixtures``.

Each fixture is one response (status, headers, cookie names, body) with the vendor detection it must produce, or
``null`` for a page that is content (including pages that only carry a vendor's sensor, cookies or headers, and
pages that quote a vendor's block-page wording).
"""

import json
from pathlib import Path

import pytest

from scrapling.engines.antibot import KINDS, VENDORS, Signal, detect, detect_all

FIXTURES = sorted((Path(__file__).parent / "fixtures").glob("*.json"))


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("path", FIXTURES, ids=[p.stem for p in FIXTURES])
def test_fixture_detection(path):
    fixture = _load(path)
    found = detect(Signal(**fixture["signal"]))
    got = None if found is None else {"vendor": found.vendor, "kind": found.kind, "rule": found.rule}
    assert got == fixture["expect"], fixture["source"]


@pytest.mark.parametrize("path", FIXTURES, ids=[p.stem for p in FIXTURES])
def test_fixture_detections_are_well_formed(path):
    """Every detection any handler makes names a known vendor and kind, and its details are a dict."""
    for found in detect_all(Signal(**_load(path)["signal"])):
        assert found.vendor in VENDORS
        assert found.kind in KINDS
        assert found.rule and isinstance(found.details, dict)


def test_fixture_set_covers_every_vendor():
    vendors = {(_load(p)["expect"] or {}).get("vendor") for p in FIXTURES}
    assert set(VENDORS) <= vendors


def test_fixture_set_has_content_pages():
    """At least a dozen fixtures must stay undetected, so over-eager rules show up as failures."""
    assert sum(1 for p in FIXTURES if _load(p)["expect"] is None) >= 12
