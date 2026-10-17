from types import SimpleNamespace

import pytest

from scrapling.engines._browsers._validators import PlaywrightConfig, StealthConfig, validate, validate_fetch


@pytest.mark.parametrize("model", [PlaywrightConfig, StealthConfig])
def test_shadow_default(model: type[PlaywrightConfig]) -> None:
    config = validate({}, model)
    assert config.pierce_shadow is False
    assert validate_fetch({}, SimpleNamespace(_config=config), model).pierce_shadow is False


@pytest.mark.parametrize("model", [PlaywrightConfig, StealthConfig])
@pytest.mark.parametrize("enabled", [False, True])
def test_shadow_inherits_session(model: type[PlaywrightConfig], enabled: bool) -> None:
    session = SimpleNamespace(_config=validate({"pierce_shadow": enabled}, model))
    assert validate_fetch({}, session, model).pierce_shadow is enabled


@pytest.mark.parametrize("model", [PlaywrightConfig, StealthConfig])
@pytest.mark.parametrize("session_value", [False, True])
@pytest.mark.parametrize("request_value", [False, True])
def test_shadow_request_override(model: type[PlaywrightConfig], session_value: bool, request_value: bool) -> None:
    session = SimpleNamespace(_config=validate({"pierce_shadow": session_value}, model))
    assert validate_fetch({"pierce_shadow": request_value}, session, model).pierce_shadow is request_value
    assert session._config.pierce_shadow is session_value


@pytest.mark.parametrize("model", [PlaywrightConfig, StealthConfig])
def test_shadow_rejects_invalid_value(model: type[PlaywrightConfig]) -> None:
    with pytest.raises(TypeError, match="pierce_shadow"):
        validate({"pierce_shadow": "yes"}, model)
    with pytest.raises(TypeError, match="pierce_shadow"):
        validate_fetch({"pierce_shadow": "yes"}, SimpleNamespace(_config=model()), model)
