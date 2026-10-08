import pytest

from scrapling.engines.antibot.solvers import CapMonsterSolver, CapSolverSolver, TwoCaptchaSolver

from .mock_providers import MockProviders

CLASSES = {"capmonster": CapMonsterSolver, "capsolver": CapSolverSolver, "2captcha": TwoCaptchaSolver}


@pytest.fixture
def mock():
    server = MockProviders().start()
    try:
        yield server
    finally:
        server.stop()


def fast(solver):
    """Shrink polling delays so tests run in milliseconds."""
    solver.token_first_poll = 0.01
    solver.poll_interval = 0.01
    solver.recognition_first_poll = 0.01
    solver.recognition_poll_interval = 0.01
    return solver


@pytest.fixture
def make(mock):
    def _make(provider, key=None, **kwargs):
        return fast(CLASSES[provider](key or mock.key, api_base=mock.base(provider), **kwargs))

    return _make
