"""Tests for the SessionManager class."""

from scrapling.core._types import Any
import pytest

from scrapling.spiders.session import SessionManager


class MockSession:  # type: ignore[type-arg]
    """Mock session for testing without actual network calls."""

    def __init__(self, name: str = "mock"):
        self.name = name
        self._is_alive = False
        self._started = False
        self._closed = False

    async def __aenter__(self):
        self._is_alive = True
        self._started = True
        return self

    async def __aexit__(self, *args):
        self._is_alive = False
        self._closed = True

    async def fetch(self, url: str, **kwargs):
        pass


class TestSessionManagerInit:
    """Test SessionManager initialization."""

    def test_manager_starts_empty(self):
        """Test that manager starts with no sessions."""
        manager = SessionManager()

        assert len(manager) == 0

    def test_manager_no_default_session_when_empty(self):
        """Test that accessing default_session_id raises when empty."""
        manager = SessionManager()

        with pytest.raises(RuntimeError, match="No sessions registered"):
            _ = manager.default_session_id


class TestSessionManagerAdd:
    """Test SessionManager add functionality."""

    def test_add_single_session(self):
        """Test adding a single session."""
        manager = SessionManager()
        session = MockSession()

        manager.add("test", session)

        assert len(manager) == 1
        assert "test" in manager
        assert manager.session_ids == ["test"]

    def test_first_session_becomes_default(self):
        """Test that first added session becomes default."""
        manager = SessionManager()
        session = MockSession()

        manager.add("first", session)

        assert manager.default_session_id == "first"

    def test_add_multiple_sessions(self):
        """Test adding multiple sessions."""
        manager = SessionManager()

        manager.add("session1", MockSession("s1"))
        manager.add("session2", MockSession("s2"))
        manager.add("session3", MockSession("s3"))

        assert len(manager) == 3
        assert "session1" in manager
        assert "session2" in manager
        assert "session3" in manager

    def test_explicit_default_session(self):
        """Test setting explicit default session."""
        manager = SessionManager()

        manager.add("first", MockSession())
        manager.add("second", MockSession(), default=True)

        assert manager.default_session_id == "second"

    def test_add_duplicate_id_raises(self):
        """Test that adding duplicate session ID raises."""
        manager = SessionManager()
        manager.add("test", MockSession())

        with pytest.raises(ValueError, match="already registered"):
            manager.add("test", MockSession())

    def test_add_returns_self_for_chaining(self):
        """Test that add returns self for method chaining."""
        manager = SessionManager()

        result = manager.add("test", MockSession())

        assert result is manager

    def test_method_chaining(self):
        """Test fluent interface for adding sessions."""
        manager = SessionManager()

        manager.add("s1", MockSession()).add("s2", MockSession()).add("s3", MockSession())

        assert len(manager) == 3

    def test_add_lazy_session(self):
        """Test adding lazy session."""
        manager = SessionManager()

        manager.add("lazy", MockSession(), lazy=True)

        assert "lazy" in manager
        assert "lazy" in manager._lazy_sessions


class TestSessionManagerRemove:
    """Test SessionManager remove/pop functionality."""

    def test_remove_session(self):
        """Test removing a session."""
        manager = SessionManager()
        manager.add("test", MockSession())

        manager.remove("test")

        assert "test" not in manager
        assert len(manager) == 0

    def test_remove_nonexistent_raises(self):
        """Test removing nonexistent session raises."""
        manager = SessionManager()

        with pytest.raises(KeyError, match="not found"):
            manager.remove("nonexistent")

    def test_pop_returns_session(self):
        """Test pop returns the removed session."""
        manager = SessionManager()
        session = MockSession("original")
        manager.add("test", session)

        popped = manager.pop("test")

        assert popped is session
        assert "test" not in manager

    def test_remove_default_updates_default(self):
        """Test that removing default session updates default."""
        manager = SessionManager()
        manager.add("first", MockSession())
        manager.add("second", MockSession())

        assert manager.default_session_id == "first"

        manager.remove("first")

        assert manager.default_session_id == "second"

    def test_remove_lazy_session_cleans_up(self):
        """Test that removing lazy session cleans up lazy set."""
        manager = SessionManager()
        manager.add("lazy", MockSession(), lazy=True)

        manager.remove("lazy")

        assert "lazy" not in manager._lazy_sessions


class TestSessionManagerGet:
    """Test SessionManager get functionality."""

    def test_get_existing_session(self):
        """Test getting an existing session."""
        manager = SessionManager()
        session = MockSession("test")
        manager.add("test", session)

        retrieved = manager.get("test")

        assert retrieved is session

    def test_get_nonexistent_raises_with_available(self):
        """Test getting nonexistent session shows available sessions."""
        manager = SessionManager()
        manager.add("session1", MockSession())
        manager.add("session2", MockSession())

        with pytest.raises(KeyError, match="Available:"):
            manager.get("nonexistent")


class TestSessionManagerContains:
    """Test SessionManager contains functionality."""

    def test_contains_existing(self):
        """Test contains for existing session."""
        manager = SessionManager()
        manager.add("test", MockSession())

        assert "test" in manager

    def test_not_contains_missing(self):
        """Test contains for missing session."""
        manager = SessionManager()
        manager.add("test", MockSession())

        assert "other" not in manager


class TestSessionManagerAsyncContext:
    """Test SessionManager async context manager."""

    @pytest.mark.asyncio
    async def test_start_activates_sessions(self):
        """Test that start activates non-lazy sessions."""
        manager = SessionManager()
        session = MockSession()
        manager.add("test", session)

        await manager.start()

        assert session._is_alive is True
        assert manager._started is True

    @pytest.mark.asyncio
    async def test_start_skips_lazy_sessions(self):
        """Test that start skips lazy sessions."""
        manager = SessionManager()
        eager_session = MockSession("eager")
        lazy_session = MockSession("lazy")

        manager.add("eager", eager_session)
        manager.add("lazy", lazy_session, lazy=True)

        await manager.start()

        assert eager_session._is_alive is True
        assert lazy_session._is_alive is False

    @pytest.mark.asyncio
    async def test_close_deactivates_sessions(self):
        """Test that close deactivates all sessions."""
        manager = SessionManager()
        session = MockSession()
        manager.add("test", session)

        await manager.start()
        assert session._is_alive is True

        await manager.close()
        assert session._is_alive is False
        assert manager._started is False

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using SessionManager as async context manager."""
        manager = SessionManager()
        session = MockSession()
        manager.add("test", session)

        async with manager:
            assert session._is_alive is True

        assert session._is_alive is False

    @pytest.mark.asyncio
    async def test_start_idempotent(self):
        """Test that calling start multiple times is safe."""
        manager = SessionManager()
        session = MockSession()
        manager.add("test", session)

        await manager.start()
        await manager.start()  # Should not raise or double-start

        assert session._started is True


class TestSessionManagerProperties:
    """Test SessionManager properties."""

    def test_session_ids_returns_list(self):
        """Test session_ids returns list of IDs."""
        manager = SessionManager()
        manager.add("a", MockSession())
        manager.add("b", MockSession())
        manager.add("c", MockSession())

        ids = manager.session_ids

        assert isinstance(ids, list)
        assert set(ids) == {"a", "b", "c"}

    def test_len_returns_session_count(self):
        """Test len returns number of sessions."""
        manager = SessionManager()

        assert len(manager) == 0

        manager.add("s1", MockSession())
        assert len(manager) == 1

        manager.add("s2", MockSession())
        assert len(manager) == 2


class TestSessionManagerIntegration:
    """Integration tests for SessionManager."""

    def test_realistic_setup(self):
        """Test realistic session manager setup."""
        manager = SessionManager()

        # Add different types of sessions
        manager.add("default", MockSession("default"))
        manager.add("backup", MockSession("backup"))
        manager.add("lazy_special", MockSession("special"), lazy=True)

        assert len(manager) == 3
        assert manager.default_session_id == "default"
        assert "lazy_special" in manager._lazy_sessions

    @pytest.mark.asyncio
    async def test_lifecycle_management(self):
        """Test complete lifecycle of session manager."""
        manager = SessionManager()
        sessions = [MockSession(f"s{i}") for i in range(3)]

        for i, session in enumerate(sessions):
            manager.add(f"session{i}", session)

        # Before start - no sessions active
        assert all(not s._is_alive for s in sessions)

        # After start - all active
        await manager.start()
        assert all(s._is_alive for s in sessions)

        # After close - all inactive
        await manager.close()
        assert all(not s._is_alive for s in sessions)
