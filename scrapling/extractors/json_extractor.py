# -*- coding: utf-8 -*-
"""Resolve a declarative dict schema against a Scrapling `Selector` into structured data."""

from cssselect import SelectorError, SelectorSyntaxError

from scrapling.core._types import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from scrapling.parser import Selector

_FIELD_ERRORS = (SelectorError, SelectorSyntaxError, ValueError, TypeError, KeyError, AttributeError)


class JsonExtractor:
    """Resolve a dict schema against a `Selector` tree into a structured dict."""

    _CASTERS: Dict[str, Callable[[Any], Any]] = {
        "string": str,
        "int": int,
        "float": float,
        "bool": lambda v: v.strip().lower() in {"true", "1", "yes", "on"} if isinstance(v, str) else bool(v),
    }

    @classmethod
    def resolve(cls, page: "Selector", schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve every top-level field of `schema` against `page`."""
        if not schema:
            return {}
        return {name: cls._resolve_field(page, spec) for name, spec in schema.items()}

    @classmethod
    def _resolve_field(cls, node: Optional["Selector"], spec: Any) -> Any:
        """Dispatch a field spec, falling back to its default on any failure."""
        if not isinstance(spec, dict):
            return None
        try:
            kind = spec.get("type")
            if kind == "object":
                return cls._resolve_object(node, spec)
            if kind == "array":
                return cls._resolve_array(node, spec)
            return cls._resolve_scalar(node, spec)
        except _FIELD_ERRORS:
            return cls._default_for(spec)

    @classmethod
    def _resolve_scalar(cls, node: Optional["Selector"], spec: Dict[str, Any]) -> Any:
        """Resolve and cast a leaf value, or return its default when absent."""
        path = spec.get("path")
        if node is None or not path:
            return spec.get("default")
        raw = node.css(path).get()
        if raw is None:
            return spec.get("default")
        kind = spec.get("type")
        caster = cls._CASTERS.get(kind) if isinstance(kind, str) else None
        return caster(raw) if caster else str(raw)

    @classmethod
    def _resolve_object(cls, node: Optional["Selector"], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve nested `properties` against the object's container, or `node` itself when no path is set."""
        path = spec.get("path")
        properties = spec.get("properties") or {}
        container = node.css(path).first if (node is not None and path) else node
        return {name: cls._resolve_field(container, child) for name, child in properties.items()}

    @classmethod
    def _resolve_array(cls, node: Optional["Selector"], spec: Dict[str, Any]) -> list:
        """Resolve the `items` spec against every element matched by the array's path."""
        path = spec.get("path")
        items = spec.get("items") or {}
        if node is None or not path:
            return []
        return [cls._resolve_field(element, items) for element in node.css(path)]

    @classmethod
    def _default_for(cls, spec: Dict[str, Any]) -> Any:
        """Return a spec's shaped fallback: nested defaults for objects, `[]` for arrays."""
        if not isinstance(spec, dict):
            return None
        kind = spec.get("type")
        if kind == "object":
            properties = spec.get("properties") or {}
            return {name: cls._default_for(child) for name, child in properties.items()}
        if kind == "array":
            return spec.get("default", [])
        return spec.get("default")
