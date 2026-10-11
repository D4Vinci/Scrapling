import pytest

from scrapling.core._types import Any
from scrapling.engines._browsers._validators import PlaywrightConfig, StealthConfig, validate
from scrapling.fetchers import StealthySession, AsyncStealthySession


@pytest.mark.parametrize("model", [PlaywrightConfig, StealthConfig])
def test_network_config_defaults(model: type[PlaywrightConfig]) -> None:
    config = validate({}, model)
    assert config.record_requests is False
    assert config.max_recorded_requests == 1000


@pytest.mark.parametrize("model", [PlaywrightConfig, StealthConfig])
@pytest.mark.parametrize(
    "values", [{"record_requests": "yes"}, {"max_recorded_requests": 0}, {"max_recorded_requests": -1}]
)
def test_network_config_invalid(model: type[PlaywrightConfig], values: dict[str, Any]) -> None:
    with pytest.raises(TypeError):
        validate(values, model)


@pytest.mark.parametrize("session_type", [StealthySession, AsyncStealthySession])
@pytest.mark.parametrize("enabled", [False, True])
def test_sessions_configure_one_network_history(session_type: Any, enabled: bool) -> None:
    session = session_type(record_requests=enabled, max_recorded_requests=7)
    assert session.network.enabled is enabled
    assert session._config.max_recorded_requests == 7
    assert session.network.search() == []
    assert session.network.get(1) is None
    assert session.network.last_id == 0
