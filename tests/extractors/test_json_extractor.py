# -*- coding: utf-8 -*-
import pytest
from scrapling import Selector, JsonExtractor

HTML = """
<html><body>
  <div class="primary">
    <span class="label">Name</span>
    <strong class="value">42.5</strong>
  </div>
  <div class="info" data-flag="true">
    <span class="field-a">alpha</span>
    <span class="field-b">beta</span>
  </div>
  <div class="list">
    <div class="item"><a href="/x/one">one</a></div>
    <div class="item"><a href="/x/two">two</a></div>
    <div class="item"><a href="/x/three">three</a></div>
  </div>
  <ul class="records">
    <li class="record"><span class="k">first</span><span class="v">10</span></li>
    <li class="record"><span class="k">second</span><span class="v">20.5</span></li>
  </ul>
</body></html>
"""


@pytest.fixture
def page():
    return Selector(HTML)


class TestScalarFields:
    """Core scalar extraction and casting scenarios (string, int, float, bool)."""

    def test_float_cast(self, page):
        schema = {"value": {"path": ".primary strong.value::text", "type": "float"}}
        assert JsonExtractor.resolve(page, schema) == {"value": 42.5}

    def test_int_cast(self, page):
        schema = {"first": {"path": "ul.records li.record span.v::text", "type": "int"}}
        assert JsonExtractor.resolve(page, schema) == {"first": 10}

    def test_string_default_type_is_str(self, page):
        schema = {"label": {"path": ".primary span.label::text"}}
        assert JsonExtractor.resolve(page, schema) == {"label": "Name"}

    def test_attr_selector(self, page):
        schema = {"href": {"path": "div.item a::attr(href)"}}
        assert JsonExtractor.resolve(page, schema) == {"href": "/x/one"}

    def test_bool_cast_truthy_falsy(self, page):
        # HTML tag data attribute with "true"
        schema = {"flag_attr": {"path": "div.info::attr(data-flag)", "type": "bool"}}
        assert JsonExtractor.resolve(page, schema) == {"flag_attr": True}

        # Text strings casting to boolean
        assert JsonExtractor._CASTERS["bool"]("true") is True
        assert JsonExtractor._CASTERS["bool"]("1") is True
        assert JsonExtractor._CASTERS["bool"]("yes") is True
        assert JsonExtractor._CASTERS["bool"]("on") is True
        assert JsonExtractor._CASTERS["bool"]("false") is False
        assert JsonExtractor._CASTERS["bool"]("0") is False
        assert JsonExtractor._CASTERS["bool"]("no") is False
        assert JsonExtractor._CASTERS["bool"]("off") is False
        assert JsonExtractor._CASTERS["bool"]("random_text") is False
        assert JsonExtractor._CASTERS["bool"](True) is True
        assert JsonExtractor._CASTERS["bool"](False) is False

    def test_missing_node_returns_default(self, page):
        schema = {"value": {"path": ".nope strong::text", "type": "float", "default": 0.0}}
        assert JsonExtractor.resolve(page, schema) == {"value": 0.0}

    def test_malformed_selector_returns_default(self, page):
        schema = {"value": {"path": ">>>broken<<<", "type": "float", "default": 1.5}}
        assert JsonExtractor.resolve(page, schema) == {"value": 1.5}

    def test_cast_failure_returns_default(self, page):
        # The label text is not numeric, so the float cast fails -> default
        schema = {"value": {"path": ".primary span.label::text", "type": "float", "default": 0.0}}
        assert JsonExtractor.resolve(page, schema) == {"value": 0.0}

    def test_unknown_type_returns_string(self, page):
        schema = {"value": {"path": ".primary strong.value::text", "type": "weird"}}
        assert JsonExtractor.resolve(page, schema) == {"value": "42.5"}


class TestStructureResolution:
    """Complex structure extraction (objects, arrays, deep nesting, default structure shapes)."""

    def test_nested_object(self, page):
        schema = {
            "details": {
                "path": "div.info",
                "type": "object",
                "properties": {
                    "field_a": {"path": "span.field-a::text", "type": "string", "default": ""},
                    "field_b": {"path": "span.field-b::text", "type": "string", "default": ""},
                },
            }
        }
        assert JsonExtractor.resolve(page, schema) == {"details": {"field_a": "alpha", "field_b": "beta"}}

    def test_missing_container_emits_shaped_child_defaults(self, page):
        schema = {
            "details": {
                "path": "div.absent",
                "type": "object",
                "properties": {
                    "field_a": {"path": "span.field-a::text", "type": "string", "default": "x"},
                    "field_b": {"path": "span.field-b::text", "type": "string", "default": "y"},
                },
            }
        }
        assert JsonExtractor.resolve(page, schema) == {"details": {"field_a": "x", "field_b": "y"}}

    def test_array_of_scalars(self, page):
        schema = {
            "items": {
                "path": ".item",
                "type": "array",
                "items": {"type": "string", "path": "a::text"},
            }
        }
        assert JsonExtractor.resolve(page, schema) == {"items": ["one", "two", "three"]}

    def test_array_of_objects(self, page):
        schema = {
            "records": {
                "path": "ul.records li.record",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"path": "span.k::text", "type": "string", "default": ""},
                        "value": {"path": "span.v::text", "type": "float", "default": 0.0},
                    },
                },
            }
        }
        assert JsonExtractor.resolve(page, schema) == {
            "records": [{"key": "first", "value": 10.0}, {"key": "second", "value": 20.5}]
        }

    def test_missing_array_returns_empty_list(self, page):
        schema = {"rows": {"path": ".no-such-item", "type": "array", "items": {"type": "string", "path": "a::text"}}}
        assert JsonExtractor.resolve(page, schema) == {"rows": []}

    def test_object_with_array_of_objects_deep_recursion(self, page):
        schema = {
            "root": {
                "path": "body",
                "type": "object",
                "properties": {
                    "value": {"path": ".primary strong.value::text", "type": "float", "default": 0.0},
                    "records": {
                        "path": "ul.records li.record",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"path": "span.k::text", "type": "string", "default": ""},
                                "value": {"path": "span.v::text", "type": "float", "default": 0.0},
                            },
                        },
                    },
                    "missing_branch": {
                        "path": ".ghost",
                        "type": "object",
                        "properties": {
                            "deep": {
                               "path": ".deeper",
                                "type": "object",
                                "properties": {"leaf": {"path": "span::text", "type": "int", "default": -1}},
                            }
                        },
                    },
                },
            }
        }
        assert JsonExtractor.resolve(page, schema) == {
            "root": {
                "value": 42.5,
                "records": [{"key": "first", "value": 10.0}, {"key": "second", "value": 20.5}],
                "missing_branch": {"deep": {"leaf": -1}},
            }
        }


class TestEntryPointsAndEdgeCases:
    """Core public API agreement and invalid input handling."""

    def test_entry_points_agree(self, page):
        schema = {"value": {"path": ".primary strong.value::text", "type": "float", "default": 0.0}}
        expected = {"value": 42.5}
        assert JsonExtractor.resolve(page, schema) == expected
        assert JsonExtractor.resolve(page, schema) == expected

    def test_empty_schema_returns_empty_dict(self, page):
        assert JsonExtractor.resolve(page, {}) == {}
        assert JsonExtractor.resolve(page, None) == {}

    def test_non_dict_spec_is_none(self, page):
        assert JsonExtractor.resolve(page, {"weird": "not-a-spec"}) == {"weird": None}
