import re
from typing import TYPE_CHECKING
from orjson import loads as orjson_loads, JSONDecodeError

from scrapling.core._types import Any, Dict, List, Optional
from scrapling.core.utils import log

if TYPE_CHECKING:
    from lxml.html import HtmlElement

_WRAPPER_PREFIX = re.compile(
    r"^\s*(?:<!--(?:\s*//<!\[CDATA\[|\s*<!\[CDATA\[|\s*/\*<!\[CDATA\[\*/)?|//<!\[CDATA\[|<!\[CDATA\[|/\*<!\[CDATA\[\*/)\s*"
)
_WRAPPER_SUFFIX = re.compile(r"\s*(?:(?://\]\]>\s*|\]\]>\s*|/\*\]\]>\*/\s*)?-->|//\]\]>|\]\]>|/\*\]\]>\*/)\s*$")

# XPath to locate all script tags with an application/ld+json type, case-insensitively
_JSON_LD_XPATH = (
    ".//script[contains(translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
    "'application/ld+json')]"
)


def clean_json_ld_string(raw_text: str) -> str:
    """Strip leading/trailing HTML comments (<!-- -->) and CDATA blocks from extracted script content."""
    text = raw_text.strip()
    if not text:
        return ""

    # Continuously peel off wrapper layers in case they are nested (e.g. <!-- //<![CDATA[ ... //]]> -->)
    while True:
        orig = text
        text = _WRAPPER_PREFIX.sub("", text)
        text = _WRAPPER_SUFFIX.sub("", text)
        text = text.strip()
        if text == orig:
            break

    return text


def normalize_schema_entries(parsed: Any) -> List[Dict[str, Any]]:
    """Normalize parsed JSON-LD structures into a flat list of top-level schema dictionaries.

    Preserves individual object structures without recursively altering nested properties.
    When a top-level `@graph` container is encountered, unpacks each entry while propagating
    the parent `@context` down to entries that do not define their own.
    """
    if isinstance(parsed, dict):
        if "@graph" in parsed and isinstance(parsed["@graph"], list):
            parent_context = parsed.get("@context")
            results: List[Dict[str, Any]] = []
            for node in parsed["@graph"]:
                if isinstance(node, dict):
                    if parent_context and "@context" not in node:
                        node = {"@context": parent_context, **node}
                    results.append(node)
            return results
        return [parsed]

    elif isinstance(parsed, list):
        results = []
        for item in parsed:
            if isinstance(item, dict):
                if "@graph" in item and isinstance(item["@graph"], list):
                    results.extend(normalize_schema_entries(item))
                else:
                    results.append(item)
        return results

    return []


def extract_json_ld(root: "HtmlElement", url: str = "") -> List[Dict[str, Any]]:
    """Extract and parse all JSON-LD scripts from an HTML element root into a normalized list of schema dictionaries."""
    if root is None:
        return []

    # Check if the root element itself is an ld+json script tag
    if getattr(root, "tag", None) == "script":
        script_type = (root.attrib.get("type") or "").lower()
        scripts = [root] if "application/ld+json" in script_type else []
    else:
        scripts = root.xpath(_JSON_LD_XPATH)

    schemas: List[Dict[str, Any]] = []
    for script in scripts:
        raw_text = script.text or "".join(script.itertext())
        cleaned = clean_json_ld_string(raw_text)
        if not cleaned:
            continue

        try:
            parsed = orjson_loads(cleaned)
        except JSONDecodeError as err:
            target_desc = f"'{url}'" if url else "document"
            log.debug(f"Skipping malformed JSON-LD script in {target_desc}: {err}")
            continue

        schemas.extend(normalize_schema_entries(parsed))

    return schemas


def normalize_schema_type(t: str) -> str:
    """Normalize a schema type by stripping schema.org URI prefixes and lowercasing."""
    cleaned = t.strip()
    for prefix in ("https://schema.org/", "http://schema.org/", "schema.org/"):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    return cleaned.strip("/").lower()


def matches_schema_type(schema: Dict[str, Any], target_type: str) -> bool:
    """Check if a schema dictionary's @type matches target_type.

    Supports:
    - String @type: "@type": "Product"
    - List of types: "@type": ["Product", "Thing"]
    - Full schema.org URI: "@type": "https://schema.org/Product"
    - Case-insensitive comparison
    """
    schema_type = schema.get("@type")
    if not schema_type:
        return False

    norm_target = normalize_schema_type(target_type)
    if isinstance(schema_type, str):
        return normalize_schema_type(schema_type) == norm_target
    elif isinstance(schema_type, (list, tuple, set)):
        return any(isinstance(item, str) and normalize_schema_type(item) == norm_target for item in schema_type)

    return False


def find_schema(schemas: List[Dict[str, Any]], schema_type: str = "") -> Optional[Dict[str, Any]]:
    """Return the first schema matching the given schema_type, or the first schema if schema_type is empty."""
    if not schema_type:
        return schemas[0] if schemas else None

    for schema in schemas:
        if matches_schema_type(schema, schema_type):
            return schema

    return None


def find_all_schemas(schemas: List[Dict[str, Any]], schema_type: str = "") -> List[Dict[str, Any]]:
    """Return all schemas matching the given schema_type, or all schemas if schema_type is empty."""
    if not schema_type:
        return list(schemas)

    return [s for s in schemas if matches_schema_type(s, schema_type)]
