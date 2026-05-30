#!/usr/bin/env python3
"""
Scrapling config-driven wrapper — CLI entry point.

Usage:
    python scrape.py <config.yaml> [options]

Options:
    -o / --output PATH      Override the output file path.
    -p / --pages N          Override pagination.max_pages (requires 'pagination'
                            to be defined in the config).
    -f / --fetcher TYPE     Override the fetcher (http | stealth | dynamic).
    -v / --verbose          Enable debug logging.

Examples:
    python scrape.py configs/books_to_scrape.yaml
    python scrape.py configs/books_to_scrape.yaml --output results/books.json
    python scrape.py configs/books_to_scrape.yaml --pages 5
    python scrape.py configs/books_to_scrape.yaml --fetcher stealth -v
"""

import argparse
import dataclasses
import logging
import sys
from pathlib import Path

from wrapper.config import ConfigError, PaginationConfig, ScrapeConfig, load_config
from wrapper.fetcher import build_fetcher
from wrapper.output import write_output
from wrapper.runner import ScrapeResult, scrape


def main() -> None:
    args = _parse_args()
    _configure_logging(args.verbose)

    # ── Load & validate config ───────────────────────────────────────────────
    try:
        cfg = load_config(args.config)
    except FileNotFoundError as exc:
        _die(str(exc))
    except ConfigError as exc:
        _die(f"Config error: {exc}")

    # ── Apply CLI overrides ──────────────────────────────────────────────────
    try:
        cfg = _apply_overrides(cfg, args)
    except ValueError as exc:
        _die(str(exc))

    # ── Run ─────────────────────────────────────────────────────────────────
    try:
        with build_fetcher(cfg) as fetcher:
            result = scrape(cfg, fetcher)
    except Exception as exc:
        _die(f"Scrape failed: {exc}")

    # ── Write output ─────────────────────────────────────────────────────────
    records = _build_records(result, cfg)
    output_path = write_output(records, cfg, args.output)

    if output_path:
        item_count = len(result.items) if cfg.items else (1 if result.top_level else 0)
        print(
            f"Scraped {item_count} record(s) across {result.pages_scraped} page(s)"
            f" → {output_path}",
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and extract structured data from a website using a YAML config.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:")[1].strip() if "Examples:" in __doc__ else "",
    )
    parser.add_argument(
        "config",
        metavar="CONFIG",
        help="Path to the YAML scrape config file.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="PATH",
        default=None,
        help="Output file path (overrides config default of output/<name>.json|csv).",
    )
    parser.add_argument(
        "-p", "--pages",
        metavar="N",
        type=int,
        default=None,
        help="Max pages to scrape (overrides pagination.max_pages in the config).",
    )
    parser.add_argument(
        "-f", "--fetcher",
        metavar="TYPE",
        choices=("http", "stealth", "dynamic"),
        default=None,
        help="Fetcher type to use: http, stealth, or dynamic.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Enable debug logging.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Config overrides
# ---------------------------------------------------------------------------

def _apply_overrides(cfg: ScrapeConfig, args: argparse.Namespace) -> ScrapeConfig:
    changes: dict = {}

    if args.fetcher is not None:
        changes["fetcher"] = args.fetcher

    if args.pages is not None:
        if cfg.pagination is None:
            raise ValueError(
                "--pages requires 'pagination' to be defined in the config "
                "(needs a next_selector to know where to go)."
            )
        if args.pages < 1:
            raise ValueError("--pages must be a positive integer.")
        changes["pagination"] = dataclasses.replace(cfg.pagination, max_pages=args.pages)

    return dataclasses.replace(cfg, **changes) if changes else cfg


# ---------------------------------------------------------------------------
# Result → writable records
# ---------------------------------------------------------------------------

def _build_records(result: ScrapeResult, cfg: ScrapeConfig):
    """
    Decide what to hand to write_output:

    - items only          → list[dict]
    - top_level only      → dict
    - both                → {"items": [...], "top_level": {...}}
    """
    has_items = cfg.items is not None
    has_top = cfg.top_level is not None

    if has_items and has_top:
        return {"items": result.items, "top_level": result.top_level}
    if has_items:
        return result.items
    return result.top_level or {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname)s %(name)s: %(message)s",
        level=level,
        stream=sys.stderr,
    )
    # Keep third-party loggers quiet unless verbose
    if not verbose:
        for noisy in ("scrapling", "curl_cffi", "playwright", "asyncio"):
            logging.getLogger(noisy).setLevel(logging.WARNING)


def _die(message: str) -> None:
    print(f"scrape.py: {message}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
