"""Run the async anti-bot handlers on a page of Scrapling's sync session.

Playwright's sync API is its async implementation driven from greenlets: a sync call schedules the implementation's
coroutine on Playwright's private event loop and switches to the greenlet that runs that loop until the call is
done. The handlers are written once, against the async API, so :func:`run_sync` runs a handler coroutine as a task
on that same loop, and :class:`AsyncView` gives the sync objects (page, frames, mouse, CDP sessions, responses) the
async API's shape:

* an attribute that is a coroutine method in the async API runs the sync method in a child greenlet and returns an
  awaitable for its result, so the loop keeps running while the call waits for the browser;
* properties and plain methods (``page.url``, ``page.frame(...)``, ``page.locator(...)``) are passed through;
* ``on``/``once``/``remove_listener`` take async or sync listeners, as the async API does; an async listener is run
  as a task on the loop.

Results are wrapped again, and one view is kept per sync object, so identity checks such as
``frame is page.main_frame`` hold. Arguments are unwrapped before they reach the sync API.
"""

from __future__ import annotations

import asyncio
import inspect
from importlib import import_module

from greenlet import GreenletExit, greenlet

from scrapling.core._types import Any, Callable, Coroutine, Dict, Tuple
from scrapling.core.utils import log

__all__ = ["AsyncView", "run_sync", "wrap", "unwrap"]

_VIEW_ATTR = "_scrapling_async_view_"
_LISTENER_METHODS = ("on", "once", "add_listener")


def _load_sync_bases() -> Tuple[type, ...]:
    bases = []
    for name in ("patchright._impl._sync_base", "playwright._impl._sync_base"):
        try:
            bases.append(import_module(name).SyncBase)
        except (ImportError, AttributeError):  # pragma: no cover - a driver that is not installed
            continue
    return tuple(bases)


_SYNC_BASES: Tuple[type, ...] = _load_sync_bases()


_KINDS: Dict[Tuple[str, str, str], str] = {}


def _async_kind(cls: type, name: str) -> str:
    """How the async API exposes ``name`` on the twin of sync class ``cls``: coroutine, property or plain."""
    key = (cls.__module__, cls.__name__, name)
    kind = _KINDS.get(key)
    if kind is None:
        kind = "plain"
        try:
            twin = getattr(import_module(cls.__module__.replace(".sync_api", ".async_api")), cls.__name__)
        except (ImportError, AttributeError):
            twin = None
        if twin is not None:
            attr = inspect.getattr_static(twin, name, None)
            if isinstance(attr, property):
                kind = "property"
            elif inspect.iscoroutinefunction(attr):
                kind = "coroutine"
        _KINDS[key] = kind
    return kind


def wrap(value: Any) -> Any:
    """``value`` with every sync Playwright object in it replaced by its :class:`AsyncView`."""
    if isinstance(value, AsyncView):
        return value
    if _SYNC_BASES and isinstance(value, _SYNC_BASES):
        view = value.__dict__.get(_VIEW_ATTR)
        if view is None:
            view = AsyncView(value)
            value.__dict__[_VIEW_ATTR] = view
        return view
    if isinstance(value, list):
        return [wrap(item) for item in value]
    if isinstance(value, tuple):
        return tuple(wrap(item) for item in value)
    if isinstance(value, dict):
        return {key: wrap(item) for key, item in value.items()}
    return value


def unwrap(value: Any) -> Any:
    """``value`` with every :class:`AsyncView` in it replaced by the sync object it shows."""
    if isinstance(value, AsyncView):
        return object.__getattribute__(value, "_target")
    if isinstance(value, list):
        return [unwrap(item) for item in value]
    if isinstance(value, tuple):
        return tuple(unwrap(item) for item in value)
    if isinstance(value, dict):
        return {key: unwrap(item) for key, item in value.items()}
    return value


async def _in_greenlet(method: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Any:
    """Call a blocking sync API method without blocking the loop it runs on.

    The child greenlet's ``_sync`` call schedules the implementation coroutine and switches back to the loop's
    greenlet (this one), which then awaits the future; when the call completes, Playwright switches to the child,
    which resolves the future and ends, returning control to the loop.
    """
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    def run() -> None:
        try:
            result = method(*args, **kwargs)
        except GreenletExit:  # pragma: no cover - the driver is shutting down
            raise
        except BaseException as error:
            if not future.done():
                future.set_exception(error)
        else:
            if not future.done():
                future.set_result(wrap(result))

    greenlet(run).switch()
    return await future


class AsyncView:
    """A sync Playwright object seen through the async API (see the module docstring)."""

    __slots__ = ("_target", "_listeners", "__weakref__")

    def __init__(self, target: Any) -> None:
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_listeners", {})

    def __getattr__(self, name: str) -> Any:
        target = object.__getattribute__(self, "_target")
        if name in _LISTENER_METHODS:
            return lambda event, listener: self._listen(name, event, listener)
        if name == "remove_listener":
            return self._unlisten
        kind = _async_kind(type(target), name)
        value = getattr(target, name)
        if kind == "coroutine":

            async def call(*args: Any, **kwargs: Any) -> Any:
                return await _in_greenlet(value, unwrap(args), unwrap(kwargs))

            return call
        if callable(value) and kind == "plain" and not isinstance(value, type):
            return lambda *args, **kwargs: wrap(value(*unwrap(args), **unwrap(kwargs)))
        return wrap(value)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(object.__getattribute__(self, "_target"), name, unwrap(value))

    def __repr__(self) -> str:
        return f"<AsyncView of {object.__getattribute__(self, '_target')!r}>"

    def _listen(self, method: str, event: str, listener: Callable[..., Any]) -> None:
        target = object.__getattribute__(self, "_target")
        listeners = object.__getattribute__(self, "_listeners")
        loop = target._loop

        def relay(*args: Any) -> None:
            result = listener(*wrap(args))
            if inspect.isawaitable(result):
                task = asyncio.ensure_future(result, loop=loop)
                task.add_done_callback(_log_listener_error)

        listeners[(event, listener)] = relay
        getattr(target, "on" if method == "add_listener" else method)(event, relay)

    def _unlisten(self, event: str, listener: Callable[..., Any]) -> None:
        relay = object.__getattribute__(self, "_listeners").pop((event, listener), None)
        if relay is not None:
            object.__getattribute__(self, "_target").remove_listener(event, relay)


def _log_listener_error(task: "asyncio.Future[Any]") -> None:
    if not task.cancelled() and task.exception() is not None:
        log.debug(f"Anti-bot listener failed: {task.exception()!r}")


def run_sync(page: Any, factory: Callable[[Any], Coroutine[Any, Any, Any]]) -> Any:
    """Run ``factory(view)`` on the loop behind the sync ``page`` and return its result (blocking).

    :param page: A sync Patchright/Playwright ``Page``.
    :param factory: Takes the page's :class:`AsyncView` and returns the coroutine to run.
    """
    return page._sync(factory(wrap(page)))
