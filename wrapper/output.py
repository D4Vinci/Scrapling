"""
Output writer for the Scrapling wrapper.

Handles three output modes declared in the config:
  json   → writes a JSON file (uses orjson for speed + pretty printing)
  csv    → writes a CSV file (list values are joined with "; ")
  stdout → pretty-prints JSON to the terminal

Public API:
    write_output(records, cfg, output_path=None)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Union

import orjson

from wrapper.config import ScrapeConfig


# Type that callers hand us: a list of row dicts, or a single dict for top_level pages.
Records = Union[list[dict], dict]


def write_output(
    records: Records,
    cfg: ScrapeConfig,
    output_path: str | Path | None = None,
) -> Path | None:
    """
    Write *records* according to cfg.output.

    Args:
        records:     list[dict] from extract_items(), or a single dict from
                     extract_top_level(). A bare dict is wrapped in a list
                     before writing so callers don't need to care.
        cfg:         The parsed ScrapeConfig (used for output format and default path).
        output_path: Override the destination file path.  When None, the file is
                     placed in ./output/<cfg.name>.<ext>.  Ignored for stdout.

    Returns:
        The Path that was written to, or None for stdout.
    """
    rows = [records] if isinstance(records, dict) else records

    if cfg.output == "stdout":
        _write_stdout(rows)
        return None

    dest = _resolve_path(cfg, output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if cfg.output == "json":
        _write_json(rows, dest)
    elif cfg.output == "csv":
        _write_csv(rows, dest)
    else:
        raise ValueError(f"Unknown output format: {cfg.output!r}")

    return dest


# ---------------------------------------------------------------------------
# Format writers
# ---------------------------------------------------------------------------

def _write_stdout(rows: list[dict]) -> None:
    payload = rows[0] if len(rows) == 1 else rows
    print(orjson.dumps(payload, option=orjson.OPT_INDENT_2).decode())


def _write_json(rows: list[dict], dest: Path) -> None:
    dest.write_bytes(orjson.dumps(rows, option=orjson.OPT_INDENT_2))


def _write_csv(rows: list[dict], dest: Path) -> None:
    if not rows:
        dest.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_flatten_row(row))


def _flatten_row(row: dict) -> dict:
    """Coerce list values to "; "-joined strings so CSV stays one-row-per-item."""
    out = {}
    for k, v in row.items():
        if isinstance(v, list):
            out[k] = "; ".join(str(x) for x in v)
        elif v is None:
            out[k] = ""
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _resolve_path(cfg: ScrapeConfig, override: str | Path | None) -> Path:
    if override is not None:
        return Path(override)
    ext = "json" if cfg.output == "json" else "csv"
    return Path("output") / f"{cfg.name}.{ext}"
