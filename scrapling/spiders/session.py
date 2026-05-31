from asyncio import Lock

from scrapling.spiders.request import Request
from scrapling.engines.static import _ASyncSessionLogic
from scrapling.engines.toolbelt.convertor import Response
from scrapling.core._types import Set, Dict, Any, cast, SUPPORTED_HTTP_METHODS
from scrapling.fetchers import AsyncDynamicSession, AsyncStealthySession, FetcherSession

Session = FetcherSession | AsyncDynamicSession | AsyncStealthySession


class SessionManager:
    """Manages pre-configured session instances."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._default_session_id: str | None = None
        self._started: bool = False
        self._lazy_sessions: Set[str] = set()
        self._lazy_lock = Lock()

    def add(self, session_id: str, session: Session, *, default: bool = False, lazy: bool = False) -> "SessionManager":
        """Register a session instance.

        :param session_id: Name to reference this session in requests
        :param session: Your pre-configured session instance
        :param default: If True, this becomes the default session
        :param lazy: If True, the session will be started only when a request uses its ID.
        """
        if session_id in self._sessions:
            raise ValueError(f"Session '{session_id}' already registered")

        self._sessions[session_id] = session

        if default or self._default_session_id is None:
            self._default_session_id = session_id

        if lazy:
            self._lazy_sessions.add(session_id)

        return self

    def remove(self, session_id: str) -> None:
        """Removes a session.

        :param session_id: ID of session to remove
        """
        _ = self.pop(session_id)

    def pop(self, session_id: str) -> Session:
        """Remove and returns a session.

        :param session_id: ID of session to remove
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found")

        session = self._sessions.pop(session_id)
        if session_id in self._lazy_sessions:
            self._lazy_sessions.remove(session_id)

        if session and self._default_session_id == session_id:
            self._default_session_id = next(iter(self._sessions), None)

        return session

    @property
    def default_session_id(self) -> str:
        if self._default_session_id is None:
            raise RuntimeError("No sessions registered")
        return self._default_session_id

    @property
    def session_ids(self) -> list[str]:
        return list(self._sessions.keys())

    def get(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            available = ", ".join(self._sessions.keys())
            raise KeyError(f"Session '{session_id}' not found. Available: {available}")
        return self._sessions[session_id]

    def cache_context(self, session_id: str) -> Dict[str, Any]:
        """Return stable session fields that affect development-cache response identity."""
        session = self.get(session_id)
        context: Dict[str, Any] = {"session_type": f"{session.__class__.__module__}.{session.__class__.__qualname__}"}

        default_headers = getattr(session, "_default_headers", None)
        if default_headers:
            context["headers"] = default_headers

        client = getattr(session, "_client", None)
        for attr in ("_curl_session", "_async_curl_session"):
            curl_session = getattr(client, attr, None)
            cookies = getattr(curl_session, "cookies", None)
            if cookies:
                context["cookies"] = repr(cookies)
                break

        config = getattr(session, "_config", None)
        if config is not None:
            for key in ("extra_headers", "cookies", "user_data_dir"):
                value = getattr(config, key, None)
                if value:
                    context[key] = value

        return context

    async def start(self) -> None:
        """Start all sessions that aren't already alive."""
        if self._started:
            return

        for sid, session in self._sessions.items():
            if sid not in self._lazy_sessions and not session._is_alive:
                await session.__aenter__()

        self._started = True

    async def close(self) -> None:
        """Close all registered sessions."""
        for sid, session in self._sessions.items():
            if sid in self._lazy_sessions and not session._is_alive:
                continue
            _ = await session.__aexit__(None, None, None)

        self._started = False

    async def fetch(self, request: Request) -> Response:
        sid = request.sid if request.sid else self.default_session_id
        session = self.get(sid)

        if session:
            if sid in self._lazy_sessions and not session._is_alive:
                async with self._lazy_lock:
                    if not session._is_alive:
                        await session.__aenter__()

            if isinstance(session, FetcherSession):
                client = session._client

                if isinstance(client, _ASyncSessionLogic):
                    kwargs = request._session_kwargs.copy()
                    method = cast(SUPPORTED_HTTP_METHODS, kwargs.pop("method", "GET"))
                    response = await client._make_request(
                        method=method,
                        url=request.url,
                        **kwargs,
                    )
                else:
                    # Sync session or other types - shouldn't happen in async context
                    raise TypeError(f"Session type {type(client)} not supported for async fetch")
            else:
                response = await session.fetch(url=request.url, **request._session_kwargs)

            response.request = request
            # Merge request meta into response meta (response meta takes priority)
            response.meta = {**request.meta, **response.meta}
            return response
        raise RuntimeError("No session found with the request session id")

    async def __aenter__(self) -> "SessionManager":
        await self.start()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    def __contains__(self, session_id: str) -> bool:
        """Check if a session ID is registered."""
        return session_id in self._sessions

    def __len__(self) -> int:
        """Number of registered sessions."""
        return len(self._sessions)
