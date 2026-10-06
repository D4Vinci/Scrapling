from re import compile as compile_regex, error as RegexError
from collections import OrderedDict
from contextlib import suppress

from scrapling.core._types import Any, Callable, Dict, List, Optional
from scrapling.engines.toolbelt.custom import Response
from scrapling.engines.toolbelt.convertor import ResponseFactory

MAX_BODY_BYTES = 1024 * 1024
MAX_TOTAL_BODY_BYTES = 20 * 1024 * 1024


class NetworkRecorder:
    """Keep bounded request history and saved responses for browser sessions."""

    def __init__(self, enabled: bool = False, max_requests: int = 1000, asynchronous: bool = False):
        if max_requests < 1:
            raise ValueError("max_requests must be greater than zero.")
        self.enabled = enabled
        self.max_requests = max_requests
        self.dropped_count = 0
        self.last_id = 0
        self._records: OrderedDict[int, Response] = OrderedDict()
        self._contexts: Dict[Any, Dict[str, Callable[..., Any]]] = {}
        self._body_bytes = 0
        self._asynchronous = asynchronous
        self._generation = 0

    def _attach(self, context: Any) -> None:
        """Save completed responses until the context is detached or closed."""
        if not self.enabled or context in self._contexts:
            return
        capture = self._capture_async if self._asynchronous else self._capture
        listeners: Dict[str, Callable[..., Any]] = {
            "requestfinished": lambda request: capture(request, self._generation, context, listeners),
            "close": lambda *args: self._detach(context),
        }
        self._contexts[context] = listeners
        try:
            for event, listener in listeners.items():
                context.on(event, listener)
        except Exception:
            self._detach(context)

    def _capture(self, request: Any, generation: int, context: Any, listeners: Dict) -> None:
        with suppress(Exception):
            response = ResponseFactory.from_playwright_response(
                None,
                request.existing_response,
                None,
                {"method": request.method, "_log": False},
                collect_history=False,
                max_body_bytes=MAX_BODY_BYTES,
            )
            self._store(request, response, generation, context, listeners)

    async def _capture_async(self, request: Any, generation: int, context: Any, listeners: Dict) -> None:
        with suppress(Exception):
            response = await ResponseFactory.from_async_playwright_response(
                None,
                request.existing_response,
                None,
                {"method": request.method, "_log": False},
                collect_history=False,
                max_body_bytes=MAX_BODY_BYTES,
            )
            self._store(request, response, generation, context, listeners)

    def _store(self, request: Any, response: Response, generation: int, context: Any, listeners: Dict) -> None:
        if generation != self._generation or self._contexts.get(context) is not listeners:
            return
        self.last_id += 1
        response.meta.update(
            network_id=self.last_id, resource_type=request.resource_type, request_body=request.post_data_buffer
        )
        self._records[self.last_id] = response
        self._body_bytes += len(response.body)
        while len(self._records) > self.max_requests or self._body_bytes > MAX_TOTAL_BODY_BYTES:
            self._body_bytes -= len(self._records.popitem(last=False)[1].body)
            self.dropped_count += 1

    def get(self, request_id: int) -> Optional[Response]:
        """Return one saved response, or None if its recording ID is unavailable."""
        return self._records.get(request_id)

    def search(
        self,
        url_pattern: Optional[str] = None,
        method: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[int] = None,
        after_id: int = 0,
        limit: Optional[int] = 100,
        include_static: bool = True,
    ) -> List[Response]:
        """Return responses in recording ID order; filter by URL regex and use limit=None for all matches."""
        if (limit is not None and limit < 1) or after_id < 0:
            raise ValueError("limit must be positive or None and after_id must be nonnegative.")
        try:
            pattern = compile_regex(url_pattern) if url_pattern is not None else None
        except RegexError as error:
            raise ValueError(f"Invalid URL pattern: {error}") from error
        found = []
        for request_id, record in self._records.items():
            if (
                request_id <= after_id
                or (pattern is not None and not pattern.search(record.url))
                or (method is not None and record.method != method.upper())
                or (resource_type is not None and record.meta["resource_type"] != resource_type)
                or (status is not None and record.status != status)
                or (not include_static and record.meta["resource_type"] not in {"xhr", "fetch"} and record.status < 400)
            ):
                continue
            found.append(record)
            if len(found) == limit:
                break
        return found

    def clear(self) -> None:
        """Clear history without reusing request IDs."""
        self._records.clear()
        self._body_bytes = 0
        self.dropped_count = 0
        self._generation += 1

    def _detach(self, context: Any = None) -> None:
        """Stop recording one context, or all contexts, and keep the history."""
        for context in (context,) if context is not None else tuple(self._contexts):
            for event, listener in self._contexts.pop(context, {}).items():
                with suppress(Exception):
                    context.remove_listener(event, listener)
