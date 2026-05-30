"""
Field extractor for the Scrapling wrapper.

Takes a parsed Scrapling Selector (or Response, which extends Selector)
and a config object, and returns plain Python dicts — no Scrapling types
leak out of this module.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Union

from wrapper.config import FieldConfig, ItemsConfig, TopLevelConfig

if TYPE_CHECKING:
    from scrapling.parser import Selector


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_css(selector: str, attr: str | None) -> str:
    """Append the appropriate CSS pseudo-element for text or attribute extraction."""
    if attr:
        return f"{selector}::attr({attr})"
    return f"{selector}::text"


def _apply_regex(text: str, pattern: str) -> str | None:
    """
    Apply a regex to text and return the first captured group, or the whole
    match if there are no groups, or None if the pattern doesn't match.
    """
    match = re.search(pattern, text)
    if not match:
        return None
    return match.group(1) if match.lastindex else match.group(0)


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def _coerce(value, type_name: str | None):
    """Apply optional type coercion to a single extracted string value."""
    if type_name is None or value is None:
        return value
    if type_name == "int":
        # Strip anything that isn't a digit or minus sign before converting
        cleaned = re.sub(r"[^\d-]", "", str(value))
        return int(cleaned) if cleaned else None
    if type_name == "float":
        # Strip anything that isn't a digit, dot, comma, or minus; normalise comma→dot
        cleaned = re.sub(r"[^\d.,-]", "", str(value)).replace(",", ".")
        # If multiple dots remain (e.g. "1.400.000"), keep only the last as decimal
        parts = cleaned.split(".")
        if len(parts) > 2:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        return float(cleaned) if cleaned else None
    return str(value)


def extract_field(
    element: "Selector",
    field_cfg: FieldConfig,
) -> Union[str, list, None]:
    """
    Extract a single named field from a Selector element.

    Returns:
        - A plain str (or int/float if type is set) when all=False, or None if nothing matched.
        - A list when all=True (may be empty).
    """
    css = _build_css(field_cfg.selector, field_cfg.attr)
    results = element.css(css)

    if field_cfg.all:
        raw_values = [str(v) for v in results.getall()]
        if field_cfg.regex:
            applied = [_apply_regex(v, field_cfg.regex) for v in raw_values]
            raw_values = [v for v in applied if v is not None]
        return [_coerce(v, field_cfg.type) for v in raw_values]

    # single-value path
    raw = results.get()
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if field_cfg.regex:
        text = _apply_regex(text, field_cfg.regex)
    return _coerce(text, field_cfg.type)


def extract_items(page: "Selector", cfg: ItemsConfig) -> list[dict]:
    """
    Find every element matching cfg.container and extract cfg.fields from each.

    Returns a list of dicts, one per container element.  Fields that yield
    no content are stored as None (or [] when all=True).
    """
    records: list[dict] = []
    containers = page.css(cfg.container)

    for element in containers:
        record: dict = {}
        for field_name, field_cfg in cfg.fields.items():
            record[field_name] = extract_field(element, field_cfg)
        records.append(record)

    return records


def extract_top_level(page: "Selector", cfg: TopLevelConfig) -> dict:
    """
    Extract cfg.fields from the page root (non-repeating, single-record pages).

    Returns a single dict.
    """
    record: dict = {}
    for field_name, field_cfg in cfg.fields.items():
        record[field_name] = extract_field(page, field_cfg)
    return record
