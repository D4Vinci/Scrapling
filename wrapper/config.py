"""
Config loader and validator for the Scrapling wrapper.

Each YAML config file describes one scraping job: the URL to fetch, which
fetcher to use, and how to extract fields from the response.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

import yaml


FETCHER_TYPES = ("http", "stealth", "dynamic")
OUTPUT_TYPES = ("json", "csv", "stdout")


class ConfigError(ValueError):
    """Raised when a config file is invalid, with a descriptive message."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FieldConfig:
    """Extraction rule for a single named field."""
    selector: str
    attr: Optional[str] = None      # HTML attribute to read; None → text content
    regex: Optional[str] = None     # Optional regex applied after extraction (first group)
    all: bool = False               # True → getall(); False → get() (first match only)
    type: Optional[Literal["str", "int", "float"]] = None  # Coerce extracted value


@dataclass
class ItemsConfig:
    """Config for list/table pages: one container selector + per-field rules."""
    container: str                  # CSS selector for the repeating wrapper element
    fields: dict[str, FieldConfig]


@dataclass
class TopLevelConfig:
    """Config for single-record pages (articles, product detail, etc.)."""
    fields: dict[str, FieldConfig]


@dataclass
class PaginationConfig:
    next_selector: str              # CSS selector that resolves to the "next page" link
    max_pages: Optional[int] = None # Hard cap; None means follow until exhausted


@dataclass
class FetcherOptions:
    impersonate: str = "chrome"
    http3: bool = False
    proxy: Optional[str] = None
    extra_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class RequestOptions:
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    timeout: Optional[int] = None   # seconds


@dataclass
class ScrapeConfig:
    name: str
    url: str
    fetcher: Literal["http", "stealth", "dynamic"]
    output: Literal["json", "csv", "stdout"]
    fetcher_options: FetcherOptions
    request_options: RequestOptions
    items: Optional[ItemsConfig]
    top_level: Optional[TopLevelConfig]
    pagination: Optional[PaginationConfig]


# ---------------------------------------------------------------------------
# Internal parsers (raw dict → dataclass), each raises ConfigError on bad input
# ---------------------------------------------------------------------------

def _parse_field(name: str, raw: Any, context: str) -> FieldConfig:
    location = f"{context}.fields.{name}"

    if not isinstance(raw, dict):
        raise ConfigError(f"{location}: expected a mapping, got {type(raw).__name__}")

    if "selector" not in raw:
        raise ConfigError(f"{location}: missing required key 'selector'")

    selector = raw["selector"]
    if not isinstance(selector, str) or not selector.strip():
        raise ConfigError(f"{location}.selector: must be a non-empty string")

    attr = raw.get("attr")
    if attr is not None and not isinstance(attr, str):
        raise ConfigError(f"{location}.attr: must be a string, got {type(attr).__name__}")

    regex = raw.get("regex")
    if regex is not None:
        if not isinstance(regex, str):
            raise ConfigError(f"{location}.regex: must be a string")
        try:
            re.compile(regex)
        except re.error as exc:
            raise ConfigError(f"{location}.regex: invalid regular expression — {exc}") from exc

    all_matches = raw.get("all", False)
    if not isinstance(all_matches, bool):
        raise ConfigError(f"{location}.all: must be true or false")

    type_coerce = raw.get("type")
    if type_coerce is not None:
        if type_coerce not in ("str", "int", "float"):
            raise ConfigError(f"{location}.type: must be 'str', 'int', or 'float'")

    unknown = set(raw) - {"selector", "attr", "regex", "all", "type"}
    if unknown:
        raise ConfigError(f"{location}: unknown key(s): {', '.join(sorted(unknown))}")

    return FieldConfig(selector=selector, attr=attr, regex=regex, all=all_matches, type=type_coerce)


def _parse_fields(raw_fields: Any, context: str) -> dict[str, FieldConfig]:
    if not isinstance(raw_fields, dict):
        raise ConfigError(f"{context}.fields: expected a mapping, got {type(raw_fields).__name__}")
    if not raw_fields:
        raise ConfigError(f"{context}.fields: must define at least one field")
    return {name: _parse_field(name, value, context) for name, value in raw_fields.items()}


def _parse_items(raw: Any) -> ItemsConfig:
    if not isinstance(raw, dict):
        raise ConfigError("items: expected a mapping, got {type(raw).__name__}")

    if "container" not in raw:
        raise ConfigError("items: missing required key 'container'")
    container = raw["container"]
    if not isinstance(container, str) or not container.strip():
        raise ConfigError("items.container: must be a non-empty string")

    if "fields" not in raw:
        raise ConfigError("items: missing required key 'fields'")

    unknown = set(raw) - {"container", "fields"}
    if unknown:
        raise ConfigError(f"items: unknown key(s): {', '.join(sorted(unknown))}")

    return ItemsConfig(container=container, fields=_parse_fields(raw["fields"], "items"))


def _parse_top_level(raw: Any) -> TopLevelConfig:
    if not isinstance(raw, dict):
        raise ConfigError(f"top_level: expected a mapping, got {type(raw).__name__}")

    if "fields" not in raw:
        raise ConfigError("top_level: missing required key 'fields'")

    unknown = set(raw) - {"fields"}
    if unknown:
        raise ConfigError(f"top_level: unknown key(s): {', '.join(sorted(unknown))}")

    return TopLevelConfig(fields=_parse_fields(raw["fields"], "top_level"))


def _parse_pagination(raw: Any) -> PaginationConfig:
    if not isinstance(raw, dict):
        raise ConfigError(f"pagination: expected a mapping, got {type(raw).__name__}")

    if "next_selector" not in raw:
        raise ConfigError("pagination: missing required key 'next_selector'")
    next_selector = raw["next_selector"]
    if not isinstance(next_selector, str) or not next_selector.strip():
        raise ConfigError("pagination.next_selector: must be a non-empty string")

    max_pages = raw.get("max_pages")
    if max_pages is not None:
        if not isinstance(max_pages, int) or max_pages < 1:
            raise ConfigError("pagination.max_pages: must be a positive integer")

    unknown = set(raw) - {"next_selector", "max_pages"}
    if unknown:
        raise ConfigError(f"pagination: unknown key(s): {', '.join(sorted(unknown))}")

    return PaginationConfig(next_selector=next_selector, max_pages=max_pages)


def _parse_fetcher_options(raw: Any) -> FetcherOptions:
    if raw is None:
        return FetcherOptions()
    if not isinstance(raw, dict):
        raise ConfigError(f"fetcher_options: expected a mapping, got {type(raw).__name__}")

    opts = FetcherOptions()

    if "impersonate" in raw:
        if not isinstance(raw["impersonate"], str):
            raise ConfigError("fetcher_options.impersonate: must be a string")
        opts.impersonate = raw["impersonate"]

    if "http3" in raw:
        if not isinstance(raw["http3"], bool):
            raise ConfigError("fetcher_options.http3: must be true or false")
        opts.http3 = raw["http3"]

    if "proxy" in raw:
        proxy = raw["proxy"]
        if proxy is not None and not isinstance(proxy, str):
            raise ConfigError("fetcher_options.proxy: must be a string or null")
        opts.proxy = proxy

    if "extra_headers" in raw:
        eh = raw["extra_headers"]
        if not isinstance(eh, dict):
            raise ConfigError("fetcher_options.extra_headers: must be a mapping")
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in eh.items()):
            raise ConfigError("fetcher_options.extra_headers: all keys and values must be strings")
        opts.extra_headers = eh

    unknown = set(raw) - {"impersonate", "http3", "proxy", "extra_headers"}
    if unknown:
        raise ConfigError(f"fetcher_options: unknown key(s): {', '.join(sorted(unknown))}")

    return opts


def _parse_request_options(raw: Any) -> RequestOptions:
    if raw is None:
        return RequestOptions()
    if not isinstance(raw, dict):
        raise ConfigError(f"request_options: expected a mapping, got {type(raw).__name__}")

    opts = RequestOptions()

    if "headers" in raw:
        h = raw["headers"]
        if not isinstance(h, dict):
            raise ConfigError("request_options.headers: must be a mapping")
        opts.headers = {str(k): str(v) for k, v in h.items()}

    if "cookies" in raw:
        c = raw["cookies"]
        if not isinstance(c, dict):
            raise ConfigError("request_options.cookies: must be a mapping")
        opts.cookies = {str(k): str(v) for k, v in c.items()}

    if "timeout" in raw:
        t = raw["timeout"]
        if not isinstance(t, int) or t < 1:
            raise ConfigError("request_options.timeout: must be a positive integer (seconds)")
        opts.timeout = t

    unknown = set(raw) - {"headers", "cookies", "timeout"}
    if unknown:
        raise ConfigError(f"request_options: unknown key(s): {', '.join(sorted(unknown))}")

    return opts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_config(path: str | Path) -> ScrapeConfig:
    """
    Parse and validate a YAML scrape config file.

    Raises:
        FileNotFoundError: if the file does not exist.
        ConfigError: if the YAML is structurally invalid or missing required keys.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        try:
            raw = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Could not parse YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: top-level structure must be a YAML mapping")

    # --- required top-level keys ---
    for key in ("name", "url"):
        if key not in raw:
            raise ConfigError(f"Missing required top-level key '{key}'")
        if not isinstance(raw[key], str) or not raw[key].strip():
            raise ConfigError(f"'{key}' must be a non-empty string")

    fetcher = raw.get("fetcher", "http")
    if fetcher not in FETCHER_TYPES:
        raise ConfigError(
            f"'fetcher' must be one of: {', '.join(FETCHER_TYPES)} — got '{fetcher}'"
        )

    output = raw.get("output", "stdout")
    if output not in OUTPUT_TYPES:
        raise ConfigError(
            f"'output' must be one of: {', '.join(OUTPUT_TYPES)} — got '{output}'"
        )

    fetcher_options = _parse_fetcher_options(raw.get("fetcher_options"))
    request_options = _parse_request_options(raw.get("request_options"))

    items = _parse_items(raw["items"]) if "items" in raw else None
    top_level = _parse_top_level(raw["top_level"]) if "top_level" in raw else None

    if items is None and top_level is None:
        raise ConfigError("At least one of 'items' or 'top_level' must be defined")

    pagination = _parse_pagination(raw["pagination"]) if "pagination" in raw else None

    # pagination only makes sense alongside items
    if pagination is not None and items is None:
        raise ConfigError("'pagination' requires 'items' to be defined")

    known_keys = {
        "name", "url", "fetcher", "output",
        "fetcher_options", "request_options",
        "items", "top_level", "pagination",
    }
    unknown = set(raw) - known_keys
    if unknown:
        raise ConfigError(f"Unknown top-level key(s): {', '.join(sorted(unknown))}")

    return ScrapeConfig(
        name=raw["name"].strip(),
        url=raw["url"].strip(),
        fetcher=fetcher,
        output=output,
        fetcher_options=fetcher_options,
        request_options=request_options,
        items=items,
        top_level=top_level,
        pagination=pagination,
    )
